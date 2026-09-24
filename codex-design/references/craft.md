# Design craft: the rules a senior designer works by

Numbers first; taste second. Sources are in the research notes `references/research/R1-skills-higgsfield-local.md`
(skills survey), `R3-gpt-image-design-prompting.md` (GPT Image) and `R4-design-craft.md` (craft). The template tells,
the ten composition devices and the judges' lessons (§4, §7, §8) come from 70 art-director judge runs on 23 and 24
September 2026. "[Op]" marks practitioner opinion rather than measurement.

## 1. Design for the size people see

A 1080-px-wide post is shown about 360–440 px wide on a phone (scale 0.33–0.41). Size everything for that.

| Role (1080-wide canvas: posts, stories, carousels) | Floor | Typical |
|---|---|---|
| Legal / fine print (non-critical only) | 30 px | 30–34 px |
| Caption, label, date line | 34 px | 36–44 px |
| Body / supporting line | 36 px | 40–52 px |
| Subhead | 52 px | 56–80 px |
| Headline | 72 px | 90–180 px |

- **YouTube thumbnail** (1280×720 layout; render 3840×2160 when you can): it must read at the 168-px sidebar
  (≈13 % scale). Headline cap height 12–18 % of the frame (86–130 px at 720 high, i.e. font-size ≈ 120–180 px for a
  heavy condensed face); 2–4 words, never more than 5; subject 40–60 % of the frame.
- **Covers and banners**: judge at the smallest place they show (mobile profile header, link preview).
- **Print**: A5/A4 flyer body 9–11 pt, captions ≥ 7 pt, headlines 24–72 pt; posters by viewing distance (a headline
  read at 5 m needs ≈ 70 mm cap height) [Op]. Minimum stroke 0.25 pt.
- Always look at the design at phone size (`judge` makes a 390-px copy; `render --scale 0.36` is a quick check).

## 2. Type system

- **Per piece: 1–2 families (3 at most), 2–3 weights, 3–4 sizes.** Adjacent steps ≥ 1.25 (1.25 / 1.333 / 1.5
  ratios); headline ÷ body ≥ 2 on social. Two sizes that differ by less than 12 % read as a mistake.
- **Leading, set explicitly** (never `line-height: normal`, fonts range 1.0–2.4):
  display 0.9–1.1 (all-caps stacks 0.85–1.0), titles ~1.2, body 1.3–1.5 (1.4–1.6 for 3+ lines), light-on-dark +0.05.
- **Tracking:** display −0.01 to −0.03 em (never below −0.04 em); all-caps labels +0.05 to +0.12 em; body 0.
- **Breaks:** `text-wrap: balance` on headlines (≤ 6 lines), `pretty` on paragraphs; no one-word last line (runt);
  no hyphenation in display type; never split a name, number or date across lines.
- **Measure:** 45–75 characters for prose; 20–45 on social cards.
- **Punctuation:** real quotes and apostrophes (’ “ ”), the ellipsis (…), × for dimensions, − for minus, and the en
  dash only closed up inside a number range (10–12); a non-breaking space between a number and its unit (20 kg).
- **No em dash, ever.** No em dash or spaced en dash goes on any design, even when the brief or the client's own copy
  has one. Propose the dash-free version to the client and ship that once they approve it. Never ship a dash
  silently (`copy.md` §1).
- **Currency,** as in `copy.md` §4: $20 and £20 with no space (en-US, en-GB); 20 € with a no-break space (de, fr, es,
  it); ₹500 (India); ৳৫০০, or ৫০০ টাকা, which reads more natural in Bangladeshi ads.
- **Case:** caps only for short labels, set with `text-transform` (the DOM keeps the approved case).
- **Numerals:** lining for stats, tabular (`.nums`) in tables and prices; one digit script per piece.
- **Emphasis:** one weight step or one colour, not a size jump. A single accented word is fine on thumbnails and ads
  when it carries the hook, otherwise avoid it.
- **Thin weights** (100–300) only from ~78 px on a 1080 canvas; below ~50 px use ≥ 400.
- **Outlined type** (thumbnails, posters): stroke 8–14 % of cap height on heavy condensed faces, 3–6 % or none on
  serifs; `paint-order: stroke fill`; static (not variable) font files.
- **Optical sizes:** use `opsz` fonts at display sizes (Fraunces, Bricolage Grotesque, Newsreader, Bodoni Moda).
- **Vertical centring in pills/buttons:** `text-box: trim-both cap alphabetic` (`.cap-trim`, Chrome 133+).

## 3. Scripts other than Latin

- Put `lang` on every run (`lang="bn"`, `"ar"`, `"hi"`, `"ja"`). Set Bengali runs in `var(--font-bengali)`, which
  lists the Bengali face first and then a generic family, as `design.py brand` writes it; another script uses its own
  font role the same way. The renderer's script check reads the first family, so a Latin face placed first is
  reported as a fallback. A Latin word inside a Bengali line takes the Bengali family's own Latin; when that does not
  suit, give the word a `<span lang="en">` set in `var(--font-text)` (`fonts.md` §7).
- **Never letter-space, caps or italicise** Bengali, Devanagari or Arabic (breaks conjuncts, headline stroke and
  joins). The kit enforces `letter-spacing: 0` on those `:lang()`s; the checks flag it.
- **Size a second script against the Latin**, not alone: the Bengali/Devanagari headline stroke sits at ~1.26× the
  Latin x-height, the Arabic alef at ~1.05× the Latin cap height. Use `fonts --family "Noto Sans Bengali:400,700@110"`
  (size-adjust %) from the table in `fonts.md`.
- **Size at viewing size:** Bengali, Devanagari and Arabic text needs at least 12 px as people see it. The check's
  floor is 34 px on a 1080-wide post or story and 77 px on a YouTube thumbnail, but the judges passed Bengali only at
  about 42 px on a 1080-wide story and 96 px for a thumbnail subtitle, so aim there (`fonts.md` §3).
- **Leading:** Bengali/Devanagari display ≥ 1.25–1.45 (per font, see `fonts.md`), body 1.5–1.8; Arabic display
  ≥ 1.3–1.6, body 1.6–2.0; CJK +10–15 %.
- Arabic/Urdu/Persian: `dir="rtl"`, mirror the layout; kashida only sparingly.
- Bengali full stop is the dari “।”; digits ০–৯ and ৳ follow the copy.
- **Text in these scripts is always typeset, never generated in pixels** (except ≤ 3-word lettering art with a native
  reader's sign-off). Never generate religious text (verses, du'a, mantras) or names in pixels.
- A native reader checks every client-facing non-Latin string (automated readers miss conjunct errors).

## 4. Layout and composition

- **One grid per piece.** Margins 6–9 % of the width on social (≥ 5 % of the short side; 60–96 px at 1080), 12–20 mm
  on A4, 8–12 mm on A5. Every gap from an 8-px scale (4 for fine steps).
- **Proximity:** the gap between groups ≥ 2× the gap inside a group; at most 4 items per group.
- **One focal point, one dominant move;** everything else holds still. Put it on a third; asymmetric beats
  centred-everything (centre only a single short line, a quote or a manifesto).
- **Reading order:** entry point → headline → support → CTA/brand. The squint test must keep that order.
- **Copy budgets:** headline ≤ 8 words (thumbnails 2–4); support ≤ 20–25 words; CTA ≤ 3 words in Latin script and
  ≤ 6 in Bengali, never wrapping; one CTA per piece; 4–6 bullets per slide or card at most; ≤ 6 cards in a grid. Too
  much copy: split it (carousel, second panel), never shrink below the floors.
- **The key fact gets its own line.** The time, deadline, price or qualifying purchase sits on a line of its own, one
  weight step heavier than the support text, beside the CTA. Mark it `"role": "key_fact"` in `copy.json`, never a
  role with "action" or "cta" in its name (the lint would read it as a second CTA). The judges asked for this in 16
  of the 70 runs.
- **Subject scale:** 40–60 % of the frame on thumbnails; about two-thirds in cover scenes; in 9:16, faces in the upper
  two-thirds.
- **Radii:** one radius language per piece (0, one value, or pill); nested radius = outer − padding.
- **Photos on flat colour:** a hairline ring at ~10 % black (light grounds) or white (dark grounds), 2–3 px at 1080.
- **Icons:** one family (Lucide, Tabler, Phosphor), one stroke width matched to the text weight, optically centred.
- **Safe zones** come from the preset (`presets`); the checks flag text outside them.
- **Carousels:** cover hook → one idea per slide → a quiet slide after a dense one → an oversized statement → CTA
  slide; one grid and rhythm for all slides, but vary the composition anchor (≥ 3 anchors per carousel, never the
  same anchor on two slides in a row).
- **Chain (seamless) carousels:** one canvas N × slide width, render with `--slides N`; shapes and photos may cross
  the cuts on purpose; text never within 40 px of a cut (checked); let the next slide's element peek 44–88 px as the
  swipe cue.

### Ten composition devices

A device makes the type and the picture depend on each other, which is what the judges missed in the layouts they
called "template" (§7). Give every design one. Record it as the `device` axis of the design's recipe (in the
dossier's `recipe` for Direct; with `design.py ledger` for Compose, flags in `cli.md`), and never give one client the
same device within three pieces.

1. **Horizon lock:** the headline's baseline sits on a real edge in the photo (a counter, a shelf, the horizon).
2. **Depth sandwich:** a cut-out crosses the headline, covering at most a fifth of the letter height.
3. **Data spine:** a real data line is the divider and the ground.
4. **Aperture:** the photo shows only inside the motif's shape.
5. **Unit grid:** a number drawn as counted units.
6. **Borrowed format:** a forecast, a receipt or a ticket, drawn in the brand's own language (Tokjhal's
   "১০০% ফুচকার সম্ভাবনা" weather forecast).
7. **Macro plus inset:** a close-up texture fills the frame, with a small photo for context.
8. **Time diptych:** one place at two moments.
9. **Continuity thread:** one line links the copy blocks and runs across the slides.
10. **Type as material:** HTML type masked with a stencil, a weave or chalk.

## 5. Colour

- **Choose the strategy first:** Restrained (neutrals + one accent), Committed (one saturated colour on 30–60 % of the
  surface), Full palette (3–4 named roles), Drenched (the surface is the colour). Social posts and posters usually
  want Committed or Drenched; corporate and editorial want Restrained.
- **Roles:** bg, surface, ink, muted ink, primary, accent, accent-ink, line; 3–6 colours per palette. 60/30/10 as a
  start; the accent stays under ~10 % of the area.
- **Contrast on real pixels:** ≥ 4.5:1 small text, ≥ 3:1 large (bold ≥ ~52 px, regular ≥ ~66 px on a 1080 canvas),
  measured against the worst pixels behind the text (the renderer does this). Fix by lightness, not hue.
- **OKLCH construction:** ink ≥ 7:1 against the background; muted ink ≥ 3.5:1 (4.5:1 if it carries small text);
  primary chroma ≤ 0.23 (≤ 0.18 when L > 0.78); accent differs from primary in hue and lightness.
- **Neutrals:** tint them toward the brand hue; no pure #000 / #FFF for large fields (hairlines excepted).
- **Gradients:** interpolate in OKLCH (`linear-gradient(in oklch, …)`), two or three adjacent hues, 1–3 % grain against
  banding. Never the default purple→blue / indigo→violet (the loudest AI tell).
- **Scrims for text on photos:** dark 20–40 % (up to ~45 % at the text), light 40–60 %, eased gradient (not linear),
  midpoint 3/10 toward the dark end; or copy space, a colour block, or a blurred panel. `.scrim-bottom` / `.scrim-top`
  are starting points.
- **Attractor palettes to avoid unless the brand asks:** warm cream + italic serif + terracotta; near-black + one neon
  with glow; AI violet on white; navy + cream + orange; graphite + orange; beige + brass + espresso.
- **Photos:** the brand colour appears as a small accent, never a colour-matched set; one grade per set.
- **Data:** one highlight colour + greys; categorical ≤ 6–8 hues, colour-vision safe (blue/orange, not red/green);
  never colour alone. Check with `render --simulate deuteranopia,achromatopsia`.
- **Culture:** red, white, green, gold and black mean different things by market (see `occasions.md`).

## 6. Images inside designs

- Generate the visual **at the canvas aspect** with the text zone reserved (plate prompts in `ai-visuals.md`); do
  not crop a 16:9 photo into a story.
- Text sits on calm areas: `analyze --src` lists calm zones and their brightness; add a scrim where needed.
- Cut-outs: clean edges (check on light and dark), a soft contact shadow (blurred ellipse, 8–20 % opacity) under
  products; light direction consistent with the background.
- Treatments are deliberate looks, never disguise: duotone, two-ink, halftone, grain 0.08–0.16 only when the style
  calls for it; product shots get no grain or vignette; portraits vignette ≤ 0.05.
- AI-image artifact check at 100 % and 200 % on every generated visual: anatomy (fingers, teeth, eyes, necks),
  style (waxy skin, over-saturation, mismatched light), function (fake text, broken straps and buckles), physics
  (shadows, reflections, perspective, floating feet), culture (implausible scenes, anachronisms). Any hit:
  regenerate or retouch; never ship.

## 7. What reads as AI or template (and the fix)

| Area | Tell | Fix |
|---|---|---|
| Type | Inter/Roboto/Arial/Poppins/Montserrat/Space Grotesk as the display voice by reflex; Playfair + Montserrat as "luxury"; Bebas/Oswald/Anton as "sport"; Lobster/Pacifico as "fun" | choose for meaning (`fonts.md`); a reflex font needs a stated reason (genre conventions such as Anton on thumbnails are fine, restyled) |
| Type | tracked all-caps eyebrow over every heading; "No. 01" micro-meta; 01/02/03 without a real sequence; gradient text; 5+ sizes | functional labels only (date, series, step); 3–4 sizes |
| Colour | purple→blue gradients; neon glow on black; rainbow accents; one-note palette | brand/product/photo palette; one accent ≤ 10 % |
| Layout | everything centred; three identical rounded cards; bento for no reason; icon tile above every heading; decorative grids, crosshairs, dot fields, squiggles, brush-stroke banners; the template tells below | asymmetric grid; content-driven layout; one composition device (§4); the removal test |
| Effects | shadow + glow + stroke + gradient on one element; default black 50 % drop shadows; glass everywhere; sparkles, lens flares, bokeh orbs; emoji scattered on the canvas | ≤ 1 effect per element, ≤ 2 effect types per piece; soft tinted shadows (blur ≥ 2× offset, 8–20 %); one glass panel at most, only over a busy photo; emoji: at most one, inside the text (`copy.md` §1) |
| Imagery | glossy blobs and orbs; plastic 3D icons; stock clichés (handshakes, lightbulb brains, robots for AI, globes); same-face smiling people; orange grade; golden-hour default; pseudo-text; floating products; marble-pedestal luxury | specific, local, candid imagery (codex-imagegen natural look); real materials; show the real product |
| Logo | swooshes, globes, leaves, lightbulbs, people figures, letter-in-circle, fused metaphors | a mark from the brand's own idea (`brand.md`) |
| Copy | the em dash; "not just X, it's Y"; AI vocabulary (elevate, unleash, game-changing); urgency with no fact; invented numbers; translated, bookish or sadhu Bengali; a greeting as the first line | `copy.md` holds the rules and the fixes (§1 house rules, §2 English, §3 Bengali, §4 other languages); `copylint` checks them and `copyjudge` rates the copy |

### Template tells to avoid

In 70 judge runs these are the moves the judges called "template" or "AI":

- a striped awning, a stack of rounded offer cards, a tilted ticket;
- a pill CTA button by default (use one only when the brand's own buttons are pills);
- hand-drawn circles or arrows that point at nothing;
- decorative badges with no job, and containers drawn around numerals;
- clip-art motifs;
- a photo with a serif headline in one corner and the footer in the opposite corner;
- a text half set beside a photo half;
- the same layout on every carousel slide.

Panels: at most one opaque panel per design, covering no more than 35 % of the photo and never the subject.

Precedence: the brief's explicit words and the client's brand beat these bans, except the dash rule: an em dash or a
spaced en dash never ships, whoever wrote it (§2). A format convention (thumbnails, ads, posters) may override a ban
with a stated reason.

## 8. Critique the way seniors do

Run these before the judge, on the rendered PNG (Read it at full size and at phone size):

1. **Two-second read:** what do you take away, where does the eye land first?
2. **Squint / grey test:** blur and desaturate (the judge gets this image): does the hierarchy survive?
3. **Thumbnail test:** at 390 px (posts) or 168 px (thumbnails) is the headline still readable?
4. **Removal test:** delete each element in turn; if nothing is lost, it stays deleted. Name one thing you removed.
5. **Swap-the-logo test:** if a competitor's logo fits equally well, the idea is generic; find the specific idea.
6. **Edge audit:** margins, tangents, near-alignments (2–6 px misses read as errors).
7. **Type audit:** rag, breaks, runts, punctuation, spacing, scripts.

Fix in this order: concept → hierarchy → layout → type → colour → polish. A fix never changes approved copy, the logo
or brand tokens, and never deletes required content to pass a check.

### Lessons the judges enforced

From the same 70 runs, the fixes that turned a FAIL or a REVISE into a pass:

- **The key fact stands out:** its own line and one weight step more (§4).
- **A logo over a photo sits on an ink bar or a plate,** never straight on busy detail. Logo handling caused 15 of
  the 39 gate failures.
- **Draw the brand motif in exactly the colour the brief states.** A motif in the wrong colour failed the brand gate.
- **Keep text and logos 24 px clear of the platform's UI bands,** and away from the avatar on covers.
- **Bengali, Devanagari and Arabic text at 12 px or more at viewing size** (§3): about 42 px on a 1080-wide story and
  96 px for a thumbnail subtitle.
- **Vary the anchor from slide to slide** in a carousel (§4).
- **Use only the plate candidate the image batch kept,** never a rejected one (`-c2`, `-raw`). A rejected candidate
  keeps its defects, and the design judge may not see them; `design.py render` warns when a design uses one
  (`ai-visuals.md` §3).

## 9. Before export

- [ ] Real punctuation, no straight quotes or double spaces; no widows or runts; nothing hyphenated in display type.
- [ ] Fonts loaded (no "font missing" in the checks), no faux bold/italic, no tofu boxes.
- [ ] Every element on the grid; equal (or deliberately unequal) margins; one radius family; consistent strokes.
- [ ] Safe zones respected; one focal point; squint test passed.
- [ ] Contrast checks green on real pixels; colour-blind and grey renders still read.
- [ ] AI-image artifact check passed; light direction consistent across the composite; clean cut-outs.
- [ ] Exact pixel size; sRGB profile (embedded by the renderer); PNG for flat/text-heavy work, JPG/WebP 85–92 for
  photographic work; under the platform's byte limit.
- [ ] Print: PDF with bleed, text ≥ 3–5 mm inside the trim, images ≥ 300 ppi at final size, fonts embedded (the
  report's `fonts.not_embedded` is empty); RGB PDF: the printer converts to CMYK (ask for a proof on colour-critical
  jobs).
- [ ] Copy proofread against the approved copy (`--copy`): names, dates, prices, phone numbers, URLs, legal lines; no
  em dash or spaced en dash anywhere on the design.
- [ ] Delivered through `design.py deliver`, the final gate, which copies the files to the final folder with a
  `DELIVERY.md` (flags in `cli.md`).
