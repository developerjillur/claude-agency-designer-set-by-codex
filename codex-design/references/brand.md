# Brand kits, logos and guidelines

## 1. The brand folder (one per client, in the project)

| File | Holds | Made by |
|---|---|---|
| `brand/brand.json` | design tokens: colours, fonts (with size-adjust), radius, logo files, voice, motifs | Claude (from the client's assets or the identity work) |
| `brand/brand.css` + `brand/fonts/` | CSS variables and the font files with licences | `design.py brand --json brand/brand.json` |
| `brand/style.json` | the imagery style lock (palette in words, light, mood, people, materials, avoid, locale) | Claude, for codex-imagegen |
| `brand/logo-*.svg` | primary, horizontal, stacked, mark, wordmark; colour, one-colour, black, white | Claude (SVG), `design.py outline` for wordmarks |
| `brand/BRAND.md` | the short rules everyone follows | Claude |
| `brand/guidelines.pdf` | the brand book | `templates/brand/guidelines.html` → `render --pages N` |
| `public/favicon*`, `site.webmanifest` | favicon set from the mark | codex-imagegen `favicon` |

`brand.json` (what `design.py brand` and the brand book read; extra keys are free-form notes for Claude). The sample
brand in `templates/sample-brand/brand.json` is a complete example:

```json
{
  "name": "Tidewater Coffee Roasters",
  "positioning": "A small roastery that roasts in the shop and sells by weight: fresh, exact and unfussy.",
  "colors": {"ink": "#16191B", "paper": "#F3F1EC", "primary": "#164E57", "accent": "#E0A33A", "muted": "#5C6368",
             "line": "#D9D4CA", "sand": "#E6DED0"},
  "proportions": {"paper": 55, "primary": 25, "sand": 10, "ink": 7, "accent": 3},
  "fonts": {"display": "Bricolage Grotesque:700,800", "text": "Figtree:400,500,700", "bengali": "Anek Bangla:500,700@106"},
  "type_scale": {"display": "800, -0.025em, line-height 0.9-0.95", "text": "500, line-height 1.3-1.45", "ratio": 1.333},
  "radius": 14,
  "logo": {"mark": "logo-mark.svg", "mark_reversed": "logo-mark-reversed.svg", "wordmark": "wordmark.svg"},
  "clear_space": "0.5 x mark height", "min_size": {"mark": "24 px / 6 mm", "wordmark": "96 px wide / 25 mm"},
  "voice": {"is": ["plain", "warm", "exact"], "is_not": ["hype", "slang", "exclamation marks"]},
  "motif": "a single tide line (a gentle wave, 3 px at 1080) under or beside headlines",
  "special_days": {"solemn": "mono mark only, no accent colour, no offers"},
  "applications": [{"src": "applications/post.jpg", "caption": "Feed post, type-led"}]
}
```

**Brand lock:** tokens from the client's real assets are *locked* (sampled hex from their logo files, their fonts);
tokens we propose are *proposed* until the client approves. A fix never changes locked tokens, the logo geometry or
approved copy. When a token is revised, re-render every asset that uses it. A vision model is never proof of exact
hex, font or spacing; the renderer's measurements are.

## 2. Logos

**Principles:** appropriate, distinctive, simple, in that order; one idea; it must work in one colour, at 16 px and
as a stamp, engraving or embroidery; no gradient-only versions. Avoid generic swooshes, globes, leaves, lightbulbs,
people figures, letter-in-circle, fused metaphors, and anything too literal ("dentist = tooth").

**Process**
1. Brief: audience, positioning, competitors' marks (find the white space), scripts and languages, applications,
   smallest size.
2. Three mechanisms, each explored: **letter-derived** (a monogram or custom letterform), **meaning-derived** (from the
   product, place or story), **abstract** (a constructed shape with a rationale). Optionally 4–8 AI concept sketches
   as independent transparent jobs ("Original, non-infringing logo concept for "<Brand>", a <what> for <audience>;
   mark only, no lettering; flat vector-like shapes, strong silhouette, balanced negative space; reads at 16 px; 1–2
   colours; centred with padding on a fully transparent background; no mockups, 3D, gradients, text or watermark").
   Sketches are mood only: never delivered.
3. **Construction in SVG by Claude:** geometric scaffolding with optical corrections (overshoot on curves, tapered joins),
   consistent stroke and corner radii; the wordmark from a licensed font converted to outlines
   (`design.py outline --text "Name" --family "…" --weight 700 --tracking -0.01 --out brand/wordmark.svg`, HarfBuzz
   shaping, so kerning and Bengali/Arabic are right), then hand-kerned by adjusting the path offsets.
4. Stress tests (render them): 16/32/48 px, one colour, reversed on the primary, on a photo, next to competitors'
   marks, at a distance (squint).
5. Present 2–3 routes in context (mock-up plates, social avatar, favicon) with the rationale.
6. Deliver the system (below). A purely AI-generated logo is not copyrightable in the US: the final mark is drawn by us;
   advise a trademark search before launch.

**The system:** versions (primary lockup, horizontal, stacked, symbol, wordmark) × (full colour, one colour, black,
white/reversed; a mark that sits in a brand-coloured shape needs its own reversed file, because the full-colour
version on a ground of that colour loses its shape; the checks cannot see this, so look at every dark-ground use); clear
space defined from the mark itself (e.g. 0.5 × symbol height, which the renderer checks for every element marked
`.logo`); minimum sizes in px and mm (the
symbol readable at 16 px, the wordmark at ~24 px cap height); the thinnest stroke ≥ 1 device px at the minimum size
(≥ 0.25 pt in print); a misuse list (no stretching, rotating, recolouring, effects, outlines, busy or low-contrast
backgrounds, rebuilding from parts). Files: master SVG, PDF, transparent PNG @1×/2×/3×, favicon set (codex-imagegen
`favicon`).

**Colour specs:** HEX + RGB for screens; CMYK and Pantone for print are **approximations until the printer proofs
them** (Chrome can't write CMYK; say so).

## 3. Mock-ups

Generate a blank-surface plate ("photorealistic <tote bag / storefront / business card on a desk>, the surface is
blank and evenly lit, no logos, text or prints anywhere"), then place the real SVG logo in CSS (`transform:
perspective(…) rotateX(…)`, `mix-blend-mode: multiply` for printed surfaces, a subtle texture). One locked base scene
per mock-up family; record the placement (surface, position, scale, clear space). The model never redraws the logo.

## 4. The brand book

`templates/brand/guidelines.html` builds the book from `brand.json` (copy it next to `brand/`, set
`<body data-brand="brand/brand.json">` and the brand.css link, then
`render --preset deck-16x9 --pages 10 --out brand/guidelines.pdf --preview`). Its ten pages are generated, not typed:

1. **Cover:** the wordmark, "Brand guidelines", name, version and month.
2. **Who we are:** `positioning`, voice `is` / `is_not`, the special-day rules.
3. **Logo:** primary lockup, mark and reversed lockup on their grounds, with file names.
4. **Clear space and size:** the lockup with its clear-space box and `x` markers; the minimum sizes drawn at size.
5. **Never do this:** stretched, recoloured, effects, rotated, busy ground, crowded (drawn from the real files).
6. **Colour:** swatches with HEX and RGB, and the `proportions` bar (CMYK and Pantone are for the printer to
   proof; Chrome cannot write them).
7. **Contrast:** every text colour on every ground, with the WCAG ratio computed and graded AAA / AA / large only /
   do not use.
8. **Typography:** a specimen per font role, including the second script (Bengali shows a conjunct, ক্ষ, to prove the
   shaping), the weights and the scale.
9. **Graphic elements:** the motif and the illustration style (replace the sample art with the client's).
10. **In use:** the `applications` renders.

Add pages by hand when the client has them: photography style (with the codex-imagegen style lock), iconography,
voice examples on-brand vs off-brand, social templates with their safe zones, governance (owners, approvals, how AI
imagery is used and labelled). Do/don't pairs beat paragraphs. Keep the rules linked to the real files.

## 5. Social templates for a brand

For every recurring post type (announcement, tip card, quote, event, hiring, day post, carousel cover/body/CTA,
thumbnail), keep one HTML skeleton in `brand/templates/` built on the brand tokens, with the copy in a `copy.json`
next to each job. A new post is a copy change and a plate, not a new design; consistency is free and the grid never
drifts between posts.
