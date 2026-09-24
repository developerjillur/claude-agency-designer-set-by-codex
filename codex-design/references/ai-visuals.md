# AI visuals for designs: routes, plates, text budgets, edits

Two routes put AI pixels into a design. **Compose**, the primary route, has the model make text-free plates and sets
the type in HTML. **Direct**, the secondary route, has the model make the finished design, text included, then proves
the text by OCR and repairs it (`direct.md`). This file covers choosing between them, briefing plates for Compose, and
editing and fixing AI pixels. Plates are generated with
`python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py batch --jobs jobs.json …` (see that skill's SKILL.md
for jobs, style locks, transparent output and the natural-photo look).

## 1. Engine facts (Codex route, ChatGPT plan)

- Codex's built-in `image_gen` requests `gpt-image-2`; quality and size are always `auto`; ≤ 5 reference images; no
  mask. Report the model as "Codex image_gen (requests gpt-image-2)".
- Native sizes (measured): 3:2 → 1536×1024, 2:3 → 1024×1536, 4:5 → 1122×1402, 1:1 → 1254×1254, 16:9 → 1672×941
  (9:16, 21:9 and 3:1: read the decoded size). The aspect comes from the words at the top of the prompt, so every
  job gets an `aspect`.
- Plan budget: image turns use plan limits 3–5× faster than text; hybrid variants (sizes, languages, A/B copy) are
  free re-renders, full-AI retries are not.
- The optional API engine (`--engine api`, key in the Keychain) adds `high`/`xhigh` quality, exact sizes up to
  3840 px, masks and real transparency. Use it for text-art tier B and print-size plates when a key exists.
- Codex's `AGENTS.md` here asks for Banglish replies. The fast pipeline passes the compiled prompt straight to the
  tool, so quoted copy survives; do not use `--mode agent` for jobs whose pixels carry exact text.

## 2. Choose the route (first match wins)

| # | Signal | Route |
|---|---|---|
| 1 | Dense data (tables, charts, many numbers), QR or barcodes, legal, medical or nutrition lines, a promo code | **Compose** for that element (Hybrid if the rest suits Direct) |
| 2 | Bengali, Indic or Hebrew text beyond one ≤ 3-word art headline (OCR cannot verify it) | **Compose** or Hybrid |
| 3 | Print with small text, a ratio beyond 3:1, or more than ~1.6 MP needed without an API key | **Compose** (AI plate, vector type) |
| 4 | A series or template whose layout must repeat, a multi-size set that must match exactly, editable source | **Compose** |
| 5 | Copy beyond tier B (below) | **Compose**, or Hybrid with the long copy typeset |
| 6 | A client photo must stay the hero (image to banner or social) | **Edit**: keep the photo's pixels; crop, cut out, extend, typeset |
| 7 | A type-as-image concept (the type is the picture), fast concept exploration, or a hero piece worth a challenger, with text that fits tier B | **Direct** (`direct.md`) as well: make the composed version too and choose with `design.py pairwise` in both orders |
| 8 | Everything else | **Compose**, the default |

Why Compose is the default: in blind pairwise votes on 24 September 2026 (Northloaf; Codex and Claude judges; both
orders), Compose won 17 of 24 votes and 3 of 4 deliverables. Direct won the story, where a giant type-as-image headline
was the idea (`direct.md` §1).

Logos: AI makes concept sketches only; the final mark is SVG (`brand.md`), composited after generation on Direct.
Charts and numbers that must be exact: always code.

### Text budget tiers (for pixels, not for HTML)

The tiers say how much text Direct can carry when row 7 picks it; they never make Direct the default.

- **Tier A:** ≤ 3 strings (headline ≤ 6 words / 35 chars; subline ≤ 10 words; CTA ≤ 3 words), Latin script, at most
  one simple number. Direct can carry it on either engine, usually right first time.
- **Tier B:** 4–8 strings, ≤ 150 characters, a few numbers (times, one price), strings ≤ 12 words; or one ≤ 3-word
  non-Latin art headline with a native reader's sign-off. Direct can carry it with OCR verification and repairs.
  Measured [L, 2026-09-23]: a 5-string, 140-character Instagram post with two times came out exact on the Codex engine
  in 1 of 2 candidates on the first attempt, twice.
- **Tier C (Compose or Hybrid):** anything longer, sentence-length body text, the data in row 1, fine print, exact
  brand fonts, print, multi-size or multi-language sets.
- Why budgets matter: one-line headlines are right ~94% of the time and two-line subheads ~87%, and errors compound
  (8 strings at 94% ≈ 61% all correct). That is why Direct verifies every string and makes 2 candidates. The bigger
  risk is invented copy (made-up claims, extra taglines), which the verifier catches as extra text.

## 3. Plates for composed designs (text-free visuals)

Generate each plate **at the canvas aspect family** (4:5 for feed and carousels, 9:16 for stories, 16:9 for
thumbnails and heroes, 3:1 for covers extended in CSS, 2:3 for posters and flyers), with the text zone reserved.

```text
Intent: text-free background plate for a <deliverable>; typography is added later in a separate layer.
Scene / Subject: <subject>, placed in <zone>, <facing or leading the eye toward the reserved zone>.
Reserved zone: <e.g. "the top 35 %" / "the left 45 %"> stays calm and low-detail: <dark|light> <texture: soft paper
grain / out-of-focus wall / smooth sky / plain floor>, with no objects, faces, edges or bright highlights in it.
Light / Camera or Style: <real light, capture or medium words>; palette <2–4 colours in words> (guidance only).
Crop safety: everything important inside the central 80 % so the plate survives a <other aspect> crop.
Constraints: no text, letters, numbers, logos, signage, labels, packaging text, screens, books with titles, price
tags or watermarks anywhere.
```

- Photos inside designs still follow codex-imagegen's natural look (real light, candid action, no stock polish).
- **Named-place street scenes** (a Dhaka market, a London high street): a real street has people and signs, so
  "no people, no signs" fights the place and the model adds them anyway. Ask for them "distant, defocused,
  unreadable" instead: people small and soft in the background, every sign too far or too blurred to read.
- **Generate plates that reserve a text zone with codex-imagegen `--strict`** (on `generate` and `batch`). Without
  it, a missed zone passes as PASS_WITH_NOTES and no fix round is spent. In the 23 to 24 September review (70 design
  judge runs, 28 plate candidates), all 10 PASS_WITH_NOTES plates had failed instruction_following, and 2 design
  failures traced back to them.
- **Then measure the zone from the pixels:** `design.py analyze --src plate.png --zone x,y,w,h` (percent of the image;
  repeat `--zone` for each zone; `--strict` exits 2 unless every zone is calm). Each zone gets a verdict by its detail
  score:
  - calm (detail ≤ 8): the text goes straight on it;
  - scrim (8 to 15): set the text over a gradient scrim;
  - busy (above 15): one solid panel over it, or regenerate the plate;
  - `subject_covered`: how much of the subject the zone would cover.

  The zone's brightness decides light or dark type. A plate with any glyph is rejected.
- **Use only the file the image batch kept,** never a rejected candidate (`-c2`, `-raw`). `design.py render` warns
  when a design uses a rejected candidate or a plate the image judge failed.
- **Cut-out layer:** `"transparent": true` job: "Isolated <object/person> on a fully transparent background, centred
  with generous padding, crisp silhouette, no halos, no floor, no checkerboard, no cast shadow (added later).
  <Existing product: keep its geometry and label exactly.>" Add the contact shadow in CSS.
- **Lettering layer (1–3 Latin words):** "The word "<WORD>" as <chrome 3D / hand-painted sign / neon tube lettering>,
  spelled exactly <W-O-R-D>, alone on a fully transparent background, letterforms fully visible with padding; no other
  text or objects." Spell-check it like full-AI; information stays in HTML.
- **Icon sets:** "A set of <6> matching flat icons for <topic>, each isolated on transparency, same stroke weight and
  palette, no text, no numbers". Better still, an SVG icon library (Lucide, Tabler, Phosphor).
- **Mock-up plates:** "Photorealistic <tote bag on a café chair>; the bag face is blank and evenly lit; no logos, text
  or prints anywhere". Then place the real SVG logo in CSS (perspective transform) rather than asking the model.

Per-deliverable plate notes:

| Deliverable | Plate |
|---|---|
| Feed post 4:5 | reserve the top ~30 % (headline) and bottom ~18 % (CTA/logo), subject in the middle band |
| Story 9:16 | keep the top 14 % and bottom 20–35 % free of detail; a calm band at 30–60 % height for the headline |
| Carousel | one **anchor** plate for slide 1, approved first; every other plate generated *from the anchor* as a style reference ("copy its palette, light, grain and treatment; not its subject, layout or marks"), never chained slide to slide |
| Thumbnail 16:9 | subject large in the right 55 % (face sharp, readable emotion, rim light), left 40 % a simple high-contrast field, bottom-right corner clear |
| Banner / cover | subject in the right third; the rest a continuous low-detail surface that extends sideways without seams. For a banner wider than 3:1, generate the plate at 3:1 or narrower and put no crop-band demands in the prompt ("keep the subject inside the middle band for a 4:1 crop"): the image model misses them (0 of 7 plates met one). Extend the plate in CSS instead (edge gradient, blurred mirror) |
| Poster | art-led: the title may be lettering art (tier A); keep the bottom 18 % flat for the HTML info strip |
| Flyer / brochure | one plate per panel from a shared style lock and a cover anchor; body copy never in pixels |
| Infographic | hero illustration + icon set as transparent layers; charts in SVG from data |
| Day post | festive/solemn illustration with a calm centre for the typeset greeting; "no text in any script, no calligraphy, no numbers" |
| Product / sale | cut-out of the real product + a scene plate with an empty surface at the right camera height and light direction |

## 4. Full-AI designs: the Direct route

When §2 picks Direct, `direct.md` replaces the hand-written full-AI job. The dossier is compiled into the prompt
structure that works for finished designs (manifest, artifact, purpose and idea, layout zones, focus, picture,
type-image device, typography, exact text, colour by role, logo space, style, safe zones, constraints). Candidates are
verified and repaired, and the real logo is composited. `judge --route full-ai --copy` fails a full-AI design on any missing,
extra, duplicated or misspelled Latin string.

**Comp-first** is now Direct's fallback. When a Direct design stays wrong after repairs and retries, `direct` exits 4
and writes `<id>-plate.png`: the best attempt with every word removed and the background rebuilt. Rebuild the type
in HTML where the attempt had it, with real fonts, then compare side by side. The rebuild must keep the hierarchy,
sizes within ~20% and the line counts.

## 5. Edits

- **Wrong text in a composed design:** edit `copy.json` / the HTML and re-render. No generation.
- **Wrong or invented text in a full-AI design:** `design.py patch` (Direct runs it automatically).
  - Boxes come from OCR (`--extra`, `--find`) or by hand (`--box`), and approved words are protected.
  - `--mode crop` edits a close-up window, so a small string gets several times more pixels.
  - The pointer copy uses a colour the design lacks, and a leak rejects the edit.
  - The edit is registered to the original on the unchanged area, feathered and composited: outside the boxes the
    result is the original, pixel for pixel.
  - Only short fixes that do not reflow. After two failed edits, rebuild that text in HTML over a text-free patch.
    Never chain more than two edits.
- **Another aspect ratio:** best is to generate natively at each aspect with the approved image as a style reference
  ("same scene as a <16:9> frame, extend the <wall/sky/floor> naturally; keep the subject identical"); next a crop from
  a wider master (`design.py reframe`, which warns when faces or the subject would be cut); for flat or abstract
  grounds extend in CSS. Generative outpainting is best-effort: composite the original area back.
- **Product into a designed layout:** cut out the real product (`design.py cutout` for photos, codex-imagegen
  `cutout` for flat studio backgrounds) → a scene plate with an empty surface → composite in HTML with a contact shadow
  (blurred ellipse 8–20 %) and a slight colour match. The label stays pixel-exact; never let the model redraw it.
- **Image to banner / social (client photo):** `analyze` (faces, subject, calm zones) → `reframe` to every preset
  or cut out and place → type in HTML → `pack`. The client's subject, product, label and people are never regenerated.
- **Series consistency:** a style lock (codex-imagegen `brand/style.json`), one anchor image passed as a style-only
  reference with its role stated, every asset generated from the anchor, the brand layer (logo SVG, fonts, colours,
  spacing) in HTML so it cannot drift, and a contact sheet (`design.py sheet`) to reject outliers.

## 6. Failures and fixes

| Failure | Prevention | Repair |
|---|---|---|
| Misspelled or garbled text | tier A budget, quotes, letter-by-letter spelling, larger type | one edit or regenerate (≤ 2), then Compose |
| Invented text (taglines, claims, specs, sponsor strips) | "render only these strings; no other text"; no promo props | regenerate; Compose |
| Duplicated text | mention each string once; "exactly once" | regenerate |
| Casing drift | write the final casing; "preserve capitalisation" | edit or regenerate |
| Hex codes printed as labels | colour words; hex guard line | regenerate |
| Small text wavy | tier C → Compose | Compose |
| Wrong numbers, chart shapes that disagree with the data | Compose; SVG charts from data | rebuild in HTML/SVG |
| Fake logos or maker marks on products and clothes | "no logos or trademarks"; plain items; the real logo composited | local edit, then composite; or regenerate |
| Mockup or moodboard instead of a flat design | the one-artifact line | regenerate |
| Text off-zone or over the subject | zones; reserved empty areas | Compose |
| "AI poster look" (pastel florals, bunting, bokeh orbs, glossy 3D, generic gradients) | a named style anchor, restrained palette, avoid-list, real typography | restyle |
| Edit drift (other things change, blur, contrast creep) | edit the original, one change per pass | composite the region back |
| Painted checkerboard instead of alpha | describe an isolated subject only | regenerate; check the alpha |
| Series drift | style lock + anchor + template | regenerate from the anchor |
| Reference leaks its content | state the role: "palette and texture only; not its subject, layout or text" | regenerate |
| Text-bearing props in a no-text plate (menus, screens, books, signs) | leave them out or turn them away | regenerate |
| Too low resolution for print | vector type; the API engine for larger plates; honest upscale warning | rebuild the plate |
