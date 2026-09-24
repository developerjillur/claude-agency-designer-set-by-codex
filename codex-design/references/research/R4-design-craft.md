# R4 — Professional Graphic-Design Craft: numeric rules, pairings, composition, colour, anti-AI tells, trends, logos, brand kits, critique rubric

Research date: 2026-09-23. Scope: the craft knowledge behind a Claude Code skill that designs social posts, stories, carousels, YouTube thumbnails, banners and covers, posters, flyers, brochures, infographics, quote cards, special-day posts, logos, brand guidelines and ads. The skill lays out real type in HTML/CSS over AI-generated visuals and renders PNG or PDF with headless Chrome.

## How to read these notes

- `[n]` is a numbered source. The full list, with URLs and dates, is at the end.
- **[Opinion]** marks practitioner judgement: mine or a cited author's. It is not an empirical finding.
- **[Derived]** marks arithmetic I worked out from cited facts, such as the display-scale maths.
- **[Measured]** marks numbers I measured myself this session with HarfBuzz (`hb-shape --show-extents`) on the Google Fonts TTFs of 2026-09-23 [88]. The method and its limits are in Appendix A.
- **[Verify]** marks facts from secondary sources, or platform specs that change often. Check these again before hard-coding them.
- Everything is paraphrased; nothing is quoted verbatim.

---

## 0. TL;DR (the 25 rules that matter most)

1. **Design for display size, not canvas size.** Phones show a 1080-wide post about 360–440 px wide, a scale of 0.33–0.41. Body text on a 1080 canvas therefore needs **≥ 36 px (absolute floor 32 px)**, which renders at about 12 pt. Headlines need **≥ 72 px** [Derived from 11].
2. **Use no more than 3 type sizes, 2 families and 2–3 weights per piece** [5][12]. Make the steps between levels large on social: headline ÷ body ≥ 2 [Opinion; 39].
3. **Leading depends on size.** Latin body 1.3–1.5 [4]; display 0.95–1.1; all-caps display 0.85–1.0 [Opinion]. Bengali and Devanagari display text needs **≥ 1.25–1.45** and body 1.5–1.8. Arabic display ≥ 1.3–1.6, body 1.6–2.0 [Measured]. Never leave `line-height: normal` [Measured: fonts' built-in "normal" ranges from 1.0 to 2.4].
4. **Tracking depends on size.** Tighten display type by −1% to −3% [8]. Open all-caps by +5% to +12% [2][3]. **Never letter-space Arabic, Bengali or Devanagari** [25].
5. **Balance the lines of every headline** (`text-wrap: balance`, Chrome 114+, ≤ 6 lines) and use `pretty` for paragraphs (Chrome 117+) [17][18]. Don't hyphenate display type, and leave no one-word last lines [Opinion].
6. **Text on photos must pass contrast against the worst pixels behind it**: ≥ 4.5:1 for small text, ≥ 3:1 for large [13][65]. Fix it with a scrim (dark 20–40%, light 40–60%, eased gradient), with copy space, with blur, or with a colour block [15][16].
7. **Pick fonts deliberately.** Inter, Roboto, Arial, Poppins and Montserrat, used by default, are an "AI or template" tell [39][40] [Opinion]. Use optical-size (`opsz`) fonts for display where they exist [26].
8. **Size a second script against the Latin, not in isolation.** In co-designed families the Bengali or Devanagari headstroke sits at about **1.26× the Latin x-height** (≈ 0.93× cap height). The Arabic alef sits at about **1.05× the Latin cap height** [Measured, n = 35 and n = 24]. Scale fonts to those targets with `@font-face { size-adjust }`.
9. **Build every layout on one grid**, with margins of **6–9% of canvas width** on social and 12–20 mm on A4. Make every spacing a multiple of **8 px** (4 px for fine steps) [Opinion].
10. **Respect safe zones.** Stories: keep the top ~250 px and bottom ~340 px of 1920 clear [80, Verify]. Reels and TikTok: also keep the right ~120 px clear [81, Verify]. On a 4:5 post, the profile grid trims ~34 px per side (3:4 crop) [78]. On YouTube thumbnails, keep the bottom-right timestamp area clear [Opinion].
11. **Make YouTube thumbnail text survive about 13% scale** (the 168-px sidebar): cap height **≥ 100 px on 1280×720**, **≤ 5 words**. Render at 3840×2160, which YouTube now recommends [82][Derived].
12. **Place one focal point** on a thirds or golden intersection. Asymmetric beats centred-everything [75][77][Opinion].
13. **Group by proximity.** Space between groups should be ≥ 2× the space within a group [76][Opinion for the ratio].
14. **Colour: 60/30/10** (dominant, secondary, accent) as a starting heuristic [68]. Use one saturated accent. Tint neutrals toward the brand hue, and never use pure #000 for large areas [67].
15. **Interpolate gradients in OKLCH/OKLab** (`linear-gradient(in oklch, …)`). Use two or three adjacent hues and add 1–3% grain against banding [69]. The default purple→blue gradient is the loudest AI tell [40].
16. **Never encode meaning with red vs green alone.** Test renders with Chrome's emulated deuteranopia, achromatopsia and blurred vision (Puppeteer `page.emulateVisionDeficiency`) [72].
17. **One effect per element at most.** Shadows should be soft, low-opacity and consistent with the scene's light. No glows, bevels, strokes, sparkles or emoji clutter [Opinion; 41].
18. **Typeset every word in HTML.** Visible AI-generated text in the imagery is an automatic fail [42].
19. **Check AI imagery** for anatomical, stylistic, functional, physics and sociocultural implausibilities (Kellogg's five categories) [42].
20. **Logos must work in one colour, at 16 px, and inside a defined clear space.** Minimum sizes go in both px and mm (e.g. Spotify: 70 px / 20 mm for the logo, 21 px / 6 mm for the icon, clear space ½ icon height) [59]. A logo generated purely by AI is not copyrightable in the US [60].
21. **Brand kits are structured, not a PDF.** Keep them as tokens (DTCG 2025.10 JSON) for colour, type, spacing, radii and logo rules, plus do/don't examples and imagery rules [61][62].
22. **Critique against the objective, not taste** [63][64]. Score 10 criteria from 0 to 5, and let hard gates force a FAIL (§9).
23. **Durable trends for 2026:** human and imperfect signals, type as hero, editorial or zine storytelling, local cultural specificity, and clean "opt-out" minimalism [45][47][53][54]. **Fads:** gummy/jelly 3D, glass everywhere, surreal AI absurdism, and trend colours used as brand colours [Opinion].
24. **Check before export:** real punctuation (’ “ ” – —), non-breaking spaces in number+unit pairs, no widows, a consistent radius family, clean optical alignment, fonts actually loaded, and the correct pixel size and colour profile [Opinion; §5.3].
25. **Every element must earn its place.** Remove anything whose removal doesn't hurt the message [Opinion].

---

## 1. Typography (with numbers)

### 1.1 Type-scale ratios

A modular scale multiplies a base size by a fixed ratio. The common ratios are borrowed from musical intervals [9][10]:

| Name | Ratio | Character | Where it fits (our use) |
|---|---|---|---|
| Minor second | 1.067 | very low contrast | dense UI, never for social |
| Major second | 1.125 | low | long documents, data-heavy brochures |
| Minor third | 1.200 | medium | print body hierarchies (A4/A5 text) |
| Major third | 1.250 | medium | brochures, infographics with a lot of text |
| Perfect fourth | 1.333 | medium-high | carousels with teaching content, posters' secondary levels |
| Augmented fourth | 1.414 | high | social posts |
| Perfect fifth | 1.500 | high | social posts, flyers |
| Golden ratio | 1.618 | very high | posters, thumbnails, covers |
| Octave | 2.000 | extreme | thumbnails, event posters, single-message ads |

- **Tim Brown's method** (A List Apart, 2011-05-03) [9]: start from the body size that renders well in the chosen face (he used 18 px), pick a ratio that means something for the content (he used the golden ratio), and multiply or divide. Scale values are a guide; he also improvised off-scale sizes where needed.
- **Anthropic's own frontend guidance** (2025-11-12) [39] warns against timid hierarchies. It recommends extreme weight contrasts (e.g. 100 vs 900) and size jumps of 3× or more for display impact. **[Opinion]** On social graphics a headline of 2–4× body size reads as designed; 1.2–1.3× reads as a document.
- **[Derived] Worked scales for a 1080-wide canvas, base 40 px:**
  - r = 1.333 → 30 / 40 / 53 / 71 / 95 / 126 / 168
  - r = 1.5 → 27 / 40 / 60 / 90 / 135 / 202 / 304
  - r = 1.618 → 25 / 40 / 65 / 105 / 169 / 274 / 444
  - Print, base 10 pt, r = 1.25 → 8 / 10 / 12.5 / 15.6 / 19.5 / 24.4 / 30.5 pt.
- **[Opinion] Rule for the skill.** Choose the ratio by format:
  - dense print: 1.2–1.25
  - carousels and infographics: 1.333
  - single-message posts and ads: 1.5–1.618
  - thumbnails and posters: 1.618–2.0, or a free "hero" size

  Snap final sizes to whole px (screen) or 0.5 pt (print).

### 1.2 Practical sizes per canvas

**Display-scale maths [Derived].** Instagram and Facebook feeds show images at full phone width. Phone viewports are about 360–440 CSS px wide (iPhone 15/16 = 393 pt, Pro Max = 440 pt, many Androids = 360–412 dp). A 1080-px canvas is therefore shown at **0.333–0.407×**.

Apple's HIG sets iOS default text at 17 pt and the minimum at 11 pt, and advises avoiding Ultralight, Thin and Light weights at small sizes [11]. Working back from those numbers:

| Rendered size you want | Canvas px needed on 1080 (worst case: 360-wide phone) | On a 393-wide phone |
|---|---|---|
| 11 pt (legal floor) | 33 px | 30 px |
| 12 pt (fine print) | 36 px | 33 px |
| 14 pt (supporting text) | 42 px | 38 px |
| 16 pt (comfortable body) | 48 px | 44 px |
| 20 pt | 60 px | 55 px |
| 24 pt (clear subhead) | 72 px | 66 px |
| 32 pt | 96 px | 88 px |
| 48 pt | 144 px | 132 px |

#### A. Social post, 1080×1080 / 1080×1350 (4:5) / 1080×1440 (3:4)

- Headline: **72–160 px**. A 1–4-word "hero" line can go to 180–300 px.
- Subhead: 44–64 px.
- Body/supporting: **36–48 px** (never < 32 px).
- Fine print / legal / source line: 28–32 px, non-essential text only.
- Eyebrow/kicker labels in caps: 26–32 px, tracked +8–12%.
- [Derived from the table above + 11]

#### B. Story / Reel cover / TikTok, 1080×1920

- Same px sizes as posts, because the width is the same.
- Fewer words: a story frame is seen for a few seconds. **[Opinion]** Keep it to ≤ 25–30 words per frame and ≤ 3 text blocks.
- Headline: 80–150 px. Body: ≥ 40–48 px.
- Keep text inside the safe band (see §3.1).

#### C. YouTube thumbnail, 1280×720 (YouTube now recommends 3840×2160; minimum width 640; 16:9) [82]

Thumbnails are shown from about 168 px wide (the desktop "up next" sidebar) up to about 430 px (mobile feed). The scale is **0.13–0.34** [Derived]:

| Canvas cap height | Rendered at 168 px wide | At 360 px wide |
|---|---|---|
| 100 px | ≈ 13 px | ≈ 28 px |
| 120 px | ≈ 16 px | ≈ 34 px |
| 160 px | ≈ 21 px | ≈ 45 px |

Rules:
- Cap height **≥ 100 px, better 120–180 px**.
- **≤ 5 words, ideally 2–4** [Opinion/practitioner consensus].
- Weights 700–900.
- No thin or high-contrast Didones.
- Build the page at 1280×720 CSS px and render at `deviceScaleFactor: 3` to get 3840×2160.

#### D. Print, A4/A5 at 300 dpi (1 pt = 4.167 px; 1 mm = 11.81 px) [Derived]

**Pixel sizes:**
- A4 = 2480×3508 px (with 3 mm bleed on every side, 2551×3579 px)
- A5 = 1748×2480 px (with bleed, 1819×2551 px)

**Type sizes:**
- Body: **9–11 pt** (Butterick: 10–12 pt print body [1]); A5 body 8.5–10 pt.
- Captions: 7–8 pt.
- Legal minimum: 6–7 pt. Reversed-out text ≥ 8 pt semibold [Opinion/print-shop norm, Verify with printer].
- A4 flyer headline: 28–72 pt. A5 flyer headline: 24–48 pt.

**Rendering in Chrome:**
- For a vector PDF, write the page in pt/mm with `@page { size: A4; margin: 0 }`.
- For a 300-dpi PNG, lay out at 793.7×1122.5 CSS px and render at `deviceScaleFactor: 3.125` [Derived].

#### E. Posters

Rule of thumb, from sign-industry guidance derived from the US Sign Council: **1 inch of cap height per 10 ft of viewing distance** (≈ 25 mm per 3 m) for impact. The maximum readable distance is about 3–4× that [83].

Academic and event poster guides give these ranges [84]:

| Format | Body | Headline |
|---|---|---|
| A3 | 12–14 pt | 24–36 pt |
| A2 | 14–16 pt | 36–48 pt |
| A1 | 18–24 pt | 48–90 pt |

Test by printing a section at 100% and reading it at 1–2 m.

#### F. Brochures

- Tri-fold A4 panels are about 99 mm wide.
- Body 9–10 pt; 40–55 characters per line.
- Panel margins ≥ 8–10 mm.
- Keep text ≥ 4–5 mm from folds [Opinion, Verify with printer].

### 1.3 Line-height (leading) by size, case and script

| Context | line-height (unitless) | Basis |
|---|---|---|
| Latin body, print or screen | 1.30–1.50 (Butterick: 1.20–1.45; WCAG AAA suggests ≥ 1.5 for web text blocks) | [4][1] |
| Latin supporting text on social (36–48 px) | 1.25–1.40 | [Opinion] |
| Latin subheads (48–80 px) | 1.10–1.25 | [Opinion] |
| Latin display (≥ 80 px, mixed case) | 0.95–1.10; check that descenders and accents don't collide | [Opinion] |
| Latin all-caps display | 0.85–1.00 (no descenders) | [Opinion] |
| Bengali / Devanagari display | **≥ 1.25**; per font ≥ its measured ink span + 0.05 (1.10–1.48, median 1.28) | [Measured] |
| Bengali / Devanagari body | 1.5–1.8 | [Measured + 29] |
| Arabic display | **≥ 1.3** (Amiri / Scheherazade New ≥ 1.6) | [Measured] |
| Arabic body | 1.6–2.0 | [Measured + 32] |
| CJK body | 1.7–1.9 (AQ: +10–15% vs Latin) | [34] |
| CJK display | 1.2–1.4 | [Opinion] |

- **Never ship `line-height: normal`.** "Normal" comes from each font's hhea or OS/2 metrics. Among the Google Fonts I measured it ranges from **1.0 (Newsreader) to 2.1 (Noto Sans Arabic)**, and Google Sans' Windows metrics imply 2.4 [Measured]. Mixed-script lines then jump around.
- Leading scales inversely with size: the bigger the type, the tighter the ratio. Long lines need slightly more leading than short ones [4].

### 1.4 Tracking (letter-spacing) by size and case

**Inter's dynamic-metrics formula** is a good generic curve for grotesks [8]. Tracking in em = −0.0223 + 0.185 × e^(−0.1745 × size_px). It gives:

| Size | Tracking |
|---|---|
| 10 px | +1.0% |
| 12 px | 0 |
| 14 px | −0.6% |
| 16 px | −1.1% |
| 20 px | −1.7% |
| 24 px | −2.0% |
| ≥ 32 px | −2.2% (asymptote) |

[Derived from 8]

Rules:
- **All caps and small caps:** add **5–12%** (0.05–0.12 em) [2][3]. Small labels (eyebrows, buttons, ≤ 14 pt rendered) sit at the high end.
- **Display lowercase / title case ≥ 80 px:** −1% to −3% **[Opinion]**. Stop before counters touch or "rn" starts reading as "m". Heavy grotesks at 150 px+ can go to −4% **[Opinion]**.
- **Body:** 0 or whatever the font's own spacing gives. Don't loosen lowercase body text [3].
- **Arabic, Bengali, Devanagari, Gurmukhi and other connected or headline scripts: letter-spacing = 0.** Browsers still insert gaps that break joins and the headstroke (matra/shirorekha) [25][29][32]. Apply tracking only to Latin runs, via `:lang(en)` or spans.
- **CJK:** 0 to +0.05 em is common in Japanese web practice **[Opinion]**. Use `text-spacing-trim` for punctuation (Chrome 123+) [35].
- **Fonts with an `opsz` axis already adjust spacing for size.** Keep `font-optical-sizing: auto` and reduce manual tracking.

### 1.5 Measure (line length)

- **Print and long-form:** 45–75 characters, 66 ideal (Bringhurst [7]); Butterick allows 45–90 [1].
- **Social graphics:** text blocks are short. **[Opinion]** Keep supporting paragraphs at **25–45 characters per line** and headlines at **8–20 characters per line**. Longer lines at 40 px on a 1080 canvas mean the text is too small or there is too much copy.
- **Japanese:** 15–35 characters per line [34].
- **Arabic:** similar to Latin by word count. Measure by rendered width, not by character count [Opinion].

### 1.6 Hierarchy, and how many fonts and weights

- **Sizes:** use 3 distinct sizes; NN/g advises no more than 3 sizes and 2–3 type sizes for hierarchy [12]. **[Opinion]** On social: headline, support, and meta/brand. Use a fourth size only for a large number or statistic.
- **Families:** 1–2. A second font is usually fine, a third rarely, a fourth almost never [5]. You don't need to pair serif with sans: two related faces with low contrast can work better, and fonts by the same designer or from one superfamily pair safely [5].
- **Weights:** 2–3 per family (e.g. 400 / 600 / 800). Avoid Thin, Light and Ultralight at small sizes [11].
- **Emphasis:** change one variable at a time (size, *or* weight, *or* colour) [Opinion].
- **Reading order:** the eye should get the message in the first ~1–2 seconds (squint test). Hierarchy is proved when a grayscale, blurred version still shows the order [Opinion; §9].

### 1.7 All-caps rules

- Use caps for less than one line: headings, labels, buttons, captions and eyebrows. Never for paragraphs [2].
- Always add 5–12% tracking, and keep kerning on [2][3].
- Don't set caps in scripts or blackletter, or in fonts whose capitals are ornate **[Opinion]**.
- Scripts without case (Bengali, Devanagari, Arabic, CJK) can't be "capitalised". Get emphasis from weight, size, colour, a width axis (Anek) or a stylised headstroke [29][32].

### 1.8 Numerals

`font-variant-numeric` [21]:
- `lining-nums` for headlines, prices and statistics.
- `tabular-nums` (fixed width) for tables, schedules, scoreboards, countdowns and any stacked or aligned numbers.
- `proportional-nums` for numbers inside running text.
- `oldstyle-nums` for editorial body text in serif faces.
- `diagonal-fractions` for ½-style fractions; `slashed-zero` for codes.

Other numeral rules:
- **[Opinion]** Big statistics get lining numerals, set 1–2 weights heavier than the label.
- Use a real minus sign (−), en dashes for ranges (10–12), and "×" for dimensions.
- **Native digits.** Bengali ০–৯, Arabic-Indic ٠–٩ and Persian ۰–۹ are distinct sets. Pick one set per piece, consistent with the audience, and never mix sets in a list [Opinion; 33]. Fustat and several Boutros families include proportional and tabular digit features [27].

### 1.9 Widows, orphans, rags and line breaks

- **Headlines and short blocks:** `text-wrap: balance`. It evens out line lengths, works for ≤ 6 lines in Chrome (since 114), and doesn't change the box width [17].
- **Paragraphs:** `text-wrap: pretty` (Chrome 117+) avoids a lone last word and adjusts the final lines [18].
- **Manual breaks for display type [Opinion]:**
  - Break on sense units.
  - Never split a name, a number from its unit, or a date.
  - Don't end a line on an article or preposition ("a", "the", "of", "to").
  - Avoid a one-word last line (a runt).
  - Avoid staircase rags (lines steadily lengthening or shortening). Aim for a gently uneven rag, with the longest line in the middle or first.
- **No hyphenation in display text.** Hyphenation is only for justified long text [1].
- **Justification:** avoid on social (rivers at short measures); allowed in print columns only with hyphenation [1]. Japanese is conventionally justified [34].
- **Centred text:** only for short phrases and titles; left-aligned for anything longer than ~3 lines [6].

### 1.10 Optical alignment, overshoot and hanging punctuation

- **Hanging punctuation:** CSS `hanging-punctuation` works only in Safari. In Chrome, hang an opening quote or bullet with a negative `text-indent` of about −0.4 to −0.5 em (measure per font) [19].
- **Vertical optical centring:** Chrome 133+ supports `text-box: trim-both cap alphabetic` (from `text-box-trim` / `text-box-edge`). It trims half-leading so type sits truly centred in pills, badges and buttons with equal padding [20]. Use it for every text-in-a-shape element.
- **Optical left edge:** large display letters (T, V, W, A, O, quotes) look indented because of their side-bearings. Shift the headline left by about 0.02–0.06 em so its visible edge aligns with the body text below [Opinion].
- **Overshoot:** round and pointed shapes (O, A, circles, triangles, icons) must be slightly larger than squares to look equal. Circular icons need about 2–4% more diameter than square ones in the same row [Opinion].
- **Centre by visual mass.** Play triangles, arrows and asymmetric logos need nudging toward their heavy side [Opinion].

### 1.11 Kerning and optical sizes for display type

- Kerning is always on (`font-kerning: normal`) [1].
- **Check display pairs by eye** at the final size: AV, AW, AT, LT, LY, To, Tr, Ty, Wa, Yo, "r.", "f." and quote marks. Fix outliers with per-glyph spans (`letter-spacing` on the first letter of the pair) [Opinion].
- **Use `opsz` fonts at the right optical size.** Fonts on Google Fonts with an `opsz` axis include [26]:
  - Inter (14–32), DM Sans (9–40), Bricolage Grotesque (12–96)
  - Fraunces (9–144), Newsreader (6–72), Source Serif 4 (8–60), Literata (7–72)
  - Bodoni Moda (6–96), Playfair (2023 version, 5–1200), Merriweather (18–144)
  - Roboto Flex (8–144), Roboto Serif (8–144), Nunito Sans (6–12), Google Sans Flex (6–144), Big Shoulders (10–72)

  With `font-optical-sizing: auto` the browser picks display cuts at large sizes. Display cuts are tighter and have finer contrast, which is a large part of the "designed" look.
- **Weight trap:** if a family lacks the weight you ask for, Chrome synthesises a fake bold or oblique, which looks cheap. Examples: Tiro Bangla (400 only), Galada, Instrument Serif, Gloock, Young Serif, DM Serif Display. Set `font-synthesis: none` globally, and request only weights that exist [24][26].

### 1.12 Text on images: scrims, gradients, blur, colour blocks

Techniques, from gentlest to strongest [13][14][15]:

1. **Copy space.** Place text over a calm, even region of the image (sky, wall, blurred background). Generate images with a planned empty zone, e.g. "subject in right third, clean negative space left" [14][Opinion].
2. **Gradient scrim** covering only the text zone (floor fade, side fade).
   - Material's text-protection guidance: dark scrims **20–40%** opacity, light scrims **40–60%** [15].
   - The gradient's midpoint sits about **3/10 of the way toward the dark end**, the far end reaches 0%, and the gradient is long enough to avoid banding (Material: ~3× the app-bar height; for us, **≥ 40–60% of the canvas height**) [15][Opinion for our proportion].
   - Use **eased stops, not linear ones.** Larsen's black-to-transparent scrim has 13 stops, with alpha 1 / .738 / .541 / .382 / .278 / .194 / .126 / .075 / .042 / .021 / .008 / .002 / 0 at 0 / 19 / 34 / 47 / 56.5 / 65 / 73 / 80.2 / 86.1 / 91 / 95.2 / 98.2 / 100%. It blends invisibly, and a scrim only about 30% longer reaches the same mid-contrast as a linear one [16].
   - Tint the scrim with the darkest brand or image colour rather than pure black, for a designed look [Opinion].
3. **Full overlay** at uniform opacity, e.g. about 50% black (NN/g's REI example). Simple, but it dims the whole photo [13].
4. **Blur** of the region behind the text (or the whole background): higher blur is better on busy images [13][43]. A glass panel needs a heavy blur (≥ 20–40 px at 1080) *and* a contrast check [43][Opinion for values].
5. **Colour block, strip or highlight** behind the text: solid or semi-opaque bars, e.g. a highlighter-style strip per line with `box-decoration-break: clone` [14].
6. **Text shadow or outline:** a last resort. If used, keep it soft and wide (blur ≥ 0.3 em, 20–35% opacity, no hard offset) so it reads as a local darkening, not an outline [13][Opinion].

**Measure it:** WCAG requires ≥ 4.5:1 for text, and ≥ 3:1 for large text (≥ 18 pt, or 14 pt bold ≈ 24 px or 18.66 px). Logotypes are exempt [65].
- On social graphics, apply the "large" threshold to the rendered size: a 72-px canvas headline is about 24 px on a phone, so it counts as "large" [Derived].
- Test the **worst-case background region, not the average**, and design for the lightest and darkest images you might receive [13].
- **[Opinion] Algorithm for the pipeline:**
  1. Render once with the text hidden.
  2. Sample background pixels inside each text box.
  3. Take the 95th-percentile luminance (for light text) or the 5th percentile (for dark text).
  4. Compute the WCAG ratio against the text colour.
  5. If it fails, raise the scrim alpha (binary search, compositing in sRGB space the way the browser does) until it passes.
- APCA targets are optional and stricter for body text [66]. **Lc 75** is the body minimum and **Lc 90** is preferred; **Lc 60** covers non-body text (24 px regular / 16 px bold); **Lc 45** covers headlines (36 px regular / 24 px bold); **Lc 30** is the floor for any text; **Lc 15** covers discernible non-text.

---

## 2. Font-pairing shortlist (Google Fonts, OFL or Apache)

All families, weights and axes below were checked against the live Google Fonts metadata on 2026-09-23: 1,946 families [26]. The designer descriptions come from google/fonts `DESCRIPTION.en_us.html` files [27].

### 2.1 Pairing principles

- **Fewer is better.** One family with weight and width contrast often beats two families [5]. Superfamilies and same-designer pairs are the safest route to harmony [5][38].
- **When you do pair, contrast one dimension clearly** (serif vs sans, wide vs condensed, geometric vs humanist) and **match the rest**: similar x-height, similar stroke weight at the used sizes, a compatible era or mood [38].
- **Give each face one fixed job**, e.g. display = A, text = B, data = C mono [5].
- **Use optical sizes** where available (`opsz` list in §1.11).
- **The same font size does not mean the same visual size.** Measured Latin x-heights on Google Fonts run from 0.386 em (Cormorant Garamond) and 0.405 (EB Garamond) to 0.546 (Inter), 0.578 (Oswald) and 0.733 (Anton) [Measured]. Scale small-x-height serifs up by about 25–35% when they sit next to Inter-class sans text [Derived].

### 2.2 Latin pairings by mood or industry

"Display / text (+ accent)". Weights are the ones that look best. **[Opinion]**, informed by the sources noted.

| Mood / industry | Pairing (display / text) | Good weights | Why it works | Known issues |
|---|---|---|---|---|
| **Corporate / finance / consulting** | Hanken Grotesk / Source Serif 4 | 700 / 400 (opsz auto) | Crisp grotesk plus a serious text serif reads as an annual report | Keep serif body ≥ 36 px on social |
| | IBM Plex Sans / Plex Serif (+ Plex Mono for data) | 600 / 400 | Superfamily; Plex Sans has a width axis 75–100 [26] | Recognisably IBM; can feel cold |
| | Schibsted Grotesk / Schibsted Grotesk | 800 / 400 | Media-group confidence, 400–900 + italics | – |
| | Public Sans / Public Sans | 700 / 400 | US government design system (USWDS) heritage; neutral, institutional, NGO | Plain unless the layout carries it |
| **Tech / SaaS / AI** | Bricolage Grotesque / Figtree (+ JetBrains Mono) | 700–800 / 400 | Bricolage has opsz 12–96 + width 75–100: characterful display, quiet text [26] | Bricolage at small sizes is quirky; text in Figtree |
| | Mona Sans / Mona Sans (+ Hubot Sans) | 800 expanded / 400 | GitHub superfamily, width 75–125 | – |
| | Host Grotesk or Funnel Display / Funnel Sans | 600–700 / 400 | 2024 additions, not yet overused | – |
| | Geist / Geist Mono | 600 / 400 | Clean, developer-native | Everywhere in dev-tool marketing 2024–26 (sameness) |
| | *Avoid by default:* Space Grotesk + Inter; Inter-only | | Reads as the AI/SaaS default [39][40] | |
| **Luxury / fashion / beauty / premium hospitality** | Bodoni Moda / Jost | 500–600 at opsz 96 / 400; caps labels +10–12% | Didone opsz 6–96 keeps hairlines appropriate to size [26] | Hairlines vanish at phone and thumbnail scale → only ≥ 72 px on a 1080 canvas and on calm backgrounds |
| | Playfair (2023, opsz 5–1200 + width) / Albert Sans | display opsz max / 400 | The newer Playfair has true display cuts | "Playfair Display + Montserrat" is a template cliché |
| | Cormorant Garamond / Hanken Grotesk | 500–600 / 400 | Elegant calligraphic serif | x-height 0.386 → never body text; needs +30% size |
| | Gloock / Instrument Sans | 400 / 400–500 | Single-weight high-contrast serif with character | No bold exists → never fake-bold |
| **Editorial / media / reports** | Newsreader (opsz 72) / Newsreader (opsz 12) + Libre Franklin labels | 600 / 400 | Production Type newspaper family with optical sizes | Newsreader's built-in line height is 1.0 → always set explicitly |
| | Fraunces (opsz 144, SOFT 0–50, WONK 0) / Source Serif 4 or Libre Franklin | 600 / 400 | Expressive soft old-style; SOFT and WONK axes for personality | WONK 1 at small sizes looks like an error |
| | Instrument Serif (+ italic) / Instrument Sans | 400 / 400–600 | Contemporary magazine look | Serif is 400-only |
| | Libre Caslon Display/Text / Libre Franklin | 400 / 400–600 | Classic American editorial (Impallari) | Libre Caslon Display is 400 only |
| | DM Serif Display / DM Sans | 400 / 400–500 | Colophon superfamily, safe | Very common |
| **Playful / kids / education / consumer apps** | Fredoka / Nunito | 600 / 400–600 | Rounded and warm; Fredoka has a width axis 75–125 | Overused for kids; add a custom colour or illustration |
| | Baloo 2 / Nunito Sans | 700–800 / 400 | Has Bengali (Baloo Da 2), Arabic (Baloo Bhaijaan 2) and other Indic siblings → good for **multilingual playful** campaigns [27] | Heavy for long text |
| | DynaPuff / Figtree | 600 / 400 | Cartoon energy for games and kids | Display only |
| | Accent: Caveat or Kalam | 500–700 | Handwritten notes | ≤ 10% of text; never body |
| **Bold / sporty / fitness / esports / events** | Big Shoulders (opsz 10–72) / Barlow or Barlow Condensed | 800 caps / 500 | Condensed Chicago-poster energy; 100–900 | Caps need +2–4% tracking at small sizes |
| | Archivo expanded / Archivo condensed + regular | 800 / 400 | One superfamily, width 62–125 × weight 100–900 [26] | – |
| | Unbounded / Manrope | 800 / 500 | Wide, modern, techy sport | Unbounded is wide: short words only |
| | Anton / Inter Tight | 400 / 500 | Classic condensed impact | Anton and Bebas Neue are template staples; restyle (colour, crop, scale) |
| **Organic / wellness / eco / craft** | Fraunces (SOFT 100, WONK 1) / Karla | 500 / 400 | Soft, quirky, human | – |
| | Young Serif / Work Sans | 400 / 400 | Warm single-weight serif | 400 only |
| | Lora / Nunito Sans | 500–600 / 400 | Gentle calligraphic serif | – |
| **Medical / clinical / pharma / public health** | Atkinson Hyperlegible Next / same | 700 / 400 | Braille Institute legibility design, 200–800 + italics (added 2025-01) [26] | Plain; add hierarchy by colour and space |
| | Lexend / Lexend | 600 / 400 | Built for reading fluency; 100–900 | – |
| | Source Sans 3 / Source Serif 4 | 600 / 400 | Neutral, trustworthy, excellent coverage | – |
| | Noto Sans (+ Noto script families) | 600 / 400 | Multilingual health communications | Generic unless the layout carries the brand |
| **Food / restaurant / FMCG / café** | Shrikhand / Work Sans | 400 / 400–500 | Joyful fat italic display (Jonny Pinhorn; also Gujarati) | Display only, short words |
| | DM Serif Display or Gloock / DM Sans | 400 / 400 | Bistro and menu elegance | – |
| | Bagel Fat One / Figtree | 400 / 400–600 | Snack and fast-food punch (also Korean) | Display only |
| | Alfa Slab One / Rokkitt | 400 / 400–600 | Diner, BBQ, burger | Retro cliché if overdone |

**[Opinion] Default fonts to use only with intent** (they read as template or AI output when used by reflex):
- Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Arial/Helvetica, Space Grotesk.
- Playfair Display + Montserrat as "luxury".
- Bebas Neue, Oswald or Anton as "sport".
- Lobster, Pacifico, Dancing Script, Great Vibes, Amatic SC or Comfortaa as "fun", "elegant" or "handmade".

The fonts themselves are fine (Inter is excellent [40]); it is the default use that gives the piece away [39][40].

**Google Sans** has been on Google Fonts under the OFL since December 2025 [36][26]. It is polished, covers Latin + Bengali + Devanagari (+ many more scripts), and has a `GRAD` axis. **[Opinion]** It is strongly associated with Google's own brand, so avoid it for client brands unless you need its script coverage.

### 2.3 Latin + Bengali

The Google Fonts Bengali families, ranked by popularity on 2026-09-23 [26]:
- Google Sans
- Hind Siliguri
- Noto Sans Bengali
- Noto Serif Bengali
- Anek Bangla
- Baloo Da 2
- Tiro Bangla
- Atma
- Alkatra
- Galada
- Mina

**Measured target [Measured, n = 35 co-designed Bengali/Devanagari + Latin families]:**
- The Bengali headstroke top sits at **1.26 × the Latin x-height** (IQR 1.20–1.30), or **0.93 × the Latin cap height** (IQR 0.87–0.99).
- Hind's own designers aligned the Bengali headline to roughly the Latin cap height, rising with weight [27].

To pair a Bengali font with a *different* Latin font, set the Bengali `@font-face { size-adjust: X% }` from the "Scale" column, so its headline lands at 1.26 × the partner's x-height.

| Bengali family | GF weights / axes | Latin partner(s) → scale | Ink span (em) → min display line-height | Character | Known issues |
|---|---|---|---|---|---|
| **Hind Siliguri** (ITF, 2015) | 300–700, static ×5 | own Latin (Hind) 100%; DM Sans 99%; Work Sans / Figtree 98%; Inter 107% | 1.18 → **≥ 1.23** | UI humanist, very legible for supporting text | **Bengali digit ১ is malformed in 400/500/600** (google/fonts #6037; a community fork fixes it) [28]. Check numerals, or render digits in another font. No variable version. Built-in line height 1.62 |
| **Noto Sans Bengali** | 100–900 + width 62.5–100 | Inter / Noto Sans 109–111%; Plus Jakarta 109% | 1.19 → ≥ 1.24 | Safest coverage; condensed widths fit long headlines | Generic look. Its bundled Latin glyphs are Noto Sans, so put your Latin font first in the stack |
| **Noto Serif Bengali** | 100–900 + width | Noto Serif 109%; Source Serif 4 100%; Lora 102%; Newsreader 89% | 1.18 → ≥ 1.23 | Editorial and literary | – |
| **Anek Bangla** (Ek Type; Bangla by Sulekha Rajkumar) | 100–800 + width 75–125 | Anek Latin 98%; Archivo 106%; Inter 110% | 1.28 → **≥ 1.33** | Headlines and wordmarks; the bold weights and condensed widths shine [27] | Anek Latin has a small cap height (0.639 em), so mixed-case Latin looks small next to the Bangla; deep descenders |
| **Baloo Da 2** (Ek Type) | 400–800 | Baloo 2 ≈ 96%; Nunito 100%; Fredoka 98% | 1.29 → **≥ 1.34** | Friendly, playful, FMCG, kids | A display personality; below-base descent −0.37 em |
| **Tiro Bangla** (Tiro Typeworks: John Hudson, Fiona Ross) | **400 + italic only** | Source Serif 4 100%; Libre Caslon Text 108% | 1.18 → ≥ 1.23 | Literary and traditional; rooted in Kolkata metal-type texture [27] | **One weight**: set `font-synthesis: none`, emphasise by size or colour. Its Latin is a transliteration subset |
| **Galada** (Black Foundry) | 400 only | a *different* Latin display: DM Serif Display 90%, Fraunces 88% | **1.39 → ≥ 1.44** | Festive Bengali display script | **Its Latin is derived from Lobster** [27], a dated cliché, so don't use its Latin. Single weight; tall marks (top 1.02 em) |
| **Mina** (Suman Bhandary et al.) | 400 / 700 | Sora 106%; Manrope 107% | 1.24 → ≥ 1.29 | Geometric, tech-ish display (extends Exo) [27] | Two weights |
| **Atma** (Black Foundry) | 300–700 | Figtree 101% | 1.27 → ≥ 1.32 | Informal, fun | Informal Latin; tall top marks |
| **Alkatra** (Suman Bhandary; Latin by Lewis McGuffie) | 400–700 (variable) | Archivo 109% | 1.30 → ≥ 1.35 | Street-graffiti "stick and tar" display; also Devanagari and Odia [27] | Display only |
| **Google Sans** | 400–700 + GRAD + opsz 17–18 | own Latin 97% | 1.29 → ≥ 1.34 | Polished product-UI tone | Google brand association |

Rules:
- **Line-height after scaling [Derived]:** the minimum display line-height in the *Latin* font's em = ink span × size-adjust + 0.05. For example, Noto Sans Bengali at 110% gives 1.19 × 1.10 + 0.05 ≈ 1.36. For body text use 1.5–1.8.
- **No caps, no italics** (except Tiro's italic), **no letter-spacing** [25][29].
- **Emphasis** comes from weight, colour, size, or width (Anek).
- **Punctuation:** use the dari "।" for full stops in Bengali prose. Native digits ০–৯ vs Western digits is a brand decision; keep one set per piece [Opinion].
- **Rendering:** set `lang="bn"` on Bengali runs. The Latin font goes first in `font-family`; the Bengali face is declared with a `unicode-range` of U+0980–09FF, U+0964–0965, U+200C–200D and U+25CC.

### 2.4 Latin + Arabic

- **Nadine Chahine's advice** [31]: choose fonts that contain both scripts, designed together. Arabic is usually drawn smaller for a given point size (her example: Latin at 10 pt pairs with Arabic at about 13 pt). In bilingual lockups, put the Arabic above the Latin for stability.
- **Common mistakes** [32]: Latin spacing or tracking applied to Arabic, automated "Arabic versions" of Latin fonts, forced caps or italics, and skipping native review.
- **Measured target [Measured, n = 24]:** the Arabic alef top sits at **1.05 × the Latin cap height** (IQR 1.00–1.09). The ink span is 1.02–1.62 em (median 1.27).

| Arabic family | GF weights | Partner → scale | Min display line-height | Character | Known issues |
|---|---|---|---|---|---|
| **IBM Plex Sans Arabic** | 100–700 | IBM Plex Sans 99% | 1.35 | Corporate, tech | Teeth are short relative to the alef (seen/alef 0.40), so text can look small: consider 105% |
| **Noto Naskh Arabic** | 400–700 | Noto Serif 112%; Source Serif 4 105% | 1.30 | Text Naskh; pairs with serifs [27] | Small on the body (alef 0.94 × its Latin cap) |
| **Noto Sans Arabic** | 100–900 + width | Noto Sans 105%; Inter ≈ 107% | 1.32 | Neutral UI | Built-in line height 2.1 → always set explicitly |
| **Noto Kufi Arabic** | 100–900 | Inter 101% | 1.42 | Geometric Kufi, mainly for larger sizes [27] | Not for small text |
| **Cairo** (Mohamed Gaber; Latin from Titillium Web) | 200–1000 + slant | Inter 107% | 1.35 | Contemporary Kufi-based, techy; short ascenders and descenders [27] | Very widely used in the region (sameness) |
| **Tajawal** (Boutros) | 200–900 | DM Sans 114% | 1.20 | Low-contrast geometric that respects calligraphic rules [27] | Small on the body |
| **Almarai** (Boutros) | 300–800 | Inter 107% | 1.32 | Clarity, screen UI [27] | Four weights |
| **Readex Pro** | 160–700 + HEXP | Lexend 99% | 1.46 | Reading-fluency design (Lexend lineage); accessible | Tall ink |
| **Alexandria** (Gaber; companion to Montserrat) | 100–900 | Montserrat 90% | 1.47 | Poster and sign heritage [27] | Big on the body; the Montserrat pairing is template-y |
| **Vazirmatn** | 100–900 | Inter 114% | 1.39 | Persian-first, very legible | Its Latin is Roboto [27] |
| **Markazi Text** (Reading/Google; Borna Izadpanah, Fiona Ross) | 400–700 | Source Serif 4 **137%** | 1.07 × 1.37 + 0.05 ≈ 1.52 | Moderate-contrast editorial text [27] | **Very small on the body** (Latin x-height only 0.364 em) |
| **El Messiri** (Gaber; Latin from Philosopher) | 400–700 | Playfair Display 113% | 1.26 | Brush-Naskh curves, display and culture | – |
| **Reem Kufi** (Khaled Hosny) | 400–700 | Montserrat 92% | 1.43 | Early Kufic, historic or Islamic feel [27] | Display only; strong connotations |
| **Amiri** (Khaled Hosny) | 400/700 + italic | Lora 102%; EB Garamond 95% | **1.58** | Classical Bulaq-press Naskh for books [27] | Tall ink span (1.53) → body line-height ≥ 1.8 |
| **Fustat** (Gaber / Hosny) | 200–800 | Inter 101% | 1.29 | Manuscript-Kufi flavour; tabular digits, fractions [27] | – |
| **Beiruti** (Boutros) | 200–900 | DM Sans 116% | 1.15 | Modern geometric with a built-in Latin [27] | Small on the body |
| **Rubik** (includes Arabic) | 300–900 + italic | Inter 102% | 1.22 | Soft, friendly consumer | – |
| **Zain** (Boutros, for Zain Group) | 200–900 | Inter 110% | 1.39 | Corporate | Associated with a telecom brand [27] |
| **Lalezar** | 400 | Latin display | 1.25 | 1960s–70s Iranian film-poster lettering [27] | Display only; small on the body |
| **Baloo Bhaijaan 2** | 400–800 | Baloo 2 96% | 1.28 | Playful | – |

Rules:
- Direction is RTL (`dir="rtl"`), and **mirror the layout**. The hierarchy that worked in LTR may need rethinking [32].
- **No letter-spacing.** Use kashida elongation only sparingly for emphasis or justification [32][33].
- **No caps, no italics, no fake bold.**
- **Numerals:** Western (0–9) vs Arabic-Indic (٠–٩) vs Persian (۰–۹) per market; stay consistent [33][Opinion].
- **Native-speaker check is mandatory**, because disconnected or reversed letters are a common failure [31][32].

### 2.5 Latin + Devanagari

- **Typesetting rules** [29]:
  - Align the shirorekha optically with the Latin (treat lower matras like descenders).
  - Give Devanagari extra line spacing.
  - Never use italics or caps.
  - Any tracking must not break the shirorekha.
  - Match stroke weight, terminal shapes and contrast type.
  - Same point size works with sentence-case Latin; increase the size when the Latin is all caps.
- **Measured:** headline = 1.26 × x-height target, as for Bengali.

| Devanagari family | GF weights | Partner → scale | Min display line-height | Character | Issues |
|---|---|---|---|---|---|
| **Poppins** (ITF) | 100–900 + italics | own Latin 93% | 1.40 | Geometric; the first Devanagari family with a full weight range [27] | Latin is overused; the Devanagari sits tall (headline 1.06 × cap) |
| **Hind** (ITF) | 300–700 | own Latin 100% | 1.23 | UI humanist [27] | – |
| **Mukta** (Ek Type) | 200–800 | own Latin 94%; Inter 109% | 1.23 | Humanist, part of a multi-script system [27] | Latin x-height small (0.47) |
| **Anek Devanagari** | 100–800 + width | Anek Latin 97% | 1.28 | Headlines and wordmarks | – |
| **Noto Sans / Serif Devanagari** | 100–900 + width | Inter 111% / Noto Serif 108% | 1.22 / 1.23 | Coverage | Generic |
| **Tiro Devanagari Hindi / Marathi / Sanskrit** | 400 + italic | Source Serif 4 100% | 1.30 | Literary; Nirnaya Sagar metal-type heritage [27] | Single weight |
| **Martel** (Dan Reynolds; Latin from Merriweather) | 200–900 | Lora 98% | **1.48** | Long-form text [27] | Tall ink |
| **Eczar** (Vaibhav Singh / Rosetta) | 400–800 | Fraunces 97% | 1.39 | Lively; display intensifies with weight [27] | – |
| **Yatra One** | 400 | DM Serif Display 98% | 1.32 | Mumbai railway sign-painting brush display [27] | Display only |
| **Rozha One** (ITF) | 400 | Playfair Display 116% | 1.11 | High-contrast Didone display (weddings, fashion, film) [27] | Hairlines vanish when small |
| **Teko / Rajdhani / Khand** (ITF) | 300–700 | Barlow Condensed 102% / Archivo 106% | 1.10–1.20 | Condensed, techy, sport and esports [27] | Template-y in sports graphics [Opinion] |
| **Baloo 2** | 400–800 | own Latin 97% | 1.25 | Playful | – |
| **Kalam** | 300–700 | Figtree 98% | 1.40 | Handwriting accent | Accent only |
| **Yantramanav** (Erin McLaughlin) | 100–900 | Inter or Roboto 110% | 1.19 | Designed as Roboto's Devanagari companion [27] | – |

### 2.6 Latin + CJK

**Japanese** [34][26]:
- **Gothic ↔ sans:**
  - Noto Sans JP (100–900); M PLUS 1 / M PLUS 2 (variable 100–900)
  - Zen Kaku Gothic New (300–900); Zen Maru Gothic (rounded)
  - BIZ UDPGothic (Morisawa UD design); IBM Plex Sans JP
  - **LINE Seed JP** (100–800, added 2026-01-21)
  - Display: Dela Gothic One
- **Mincho ↔ serif:**
  - Noto Serif JP (200–900), Shippori Mincho (400–800), Zen Old Mincho, Kaisei Decol / Opti / Tokumin
  - Pair with Cormorant, EB Garamond or Libre Caslon Text.
- **Rules** [34]:
  - Pair Gothic with sans and Mincho with serif.
  - No italics.
  - 15–35 characters per line.
  - Reduce Japanese size by 10–15%, or enlarge the Latin, because kanji and kana fill the em.
  - Add 10–15% line height.
  - Put the Latin font first in the stack so Latin glyphs don't come from the CJK font.
  - Use `word-break: auto-phrase` for natural phrase breaks (Chrome 119+), `text-spacing-trim` for punctuation kerning (Chrome 123+), and `text-autospace` for CJK–Latin spacing (recent Chrome; Verify) [35].

**Korean:**
- Families: Noto Sans KR / Noto Serif KR (variable); Gothic A1 (100–900); IBM Plex Sans KR; Nanum Gothic / Nanum Myeongjo (3 weights); Gowun Batang / Gowun Dodum; Hahmlet (variable serif); Asta Sans (2025).
- Display: Black Han Sans, Do Hyeon, Jua (Woowahan fonts), Bagel Fat One.
- Use `word-break: keep-all` so Korean words don't split mid-word [Opinion/common practice].

**Chinese:**
- Noto Sans SC / TC (100–900), Noto Serif SC / TC (200–900).
- Display: ZCOOL KuaiLe, ZCOOL XiaoWei, ZCOOL QingKe HuangYou, Ma Shan Zheng (brush), LXGW WenKai TC, Chiron GoRound TC / Chiron Hei HK (2025) [26].
- **Tag the language correctly** (`lang="zh-Hans"`, `zh-Hant`, `ja` or `ko`). Pan-CJK fonts pick region-specific glyph forms and punctuation positions from the language tag [Opinion; widely documented].

**All CJK:**
- Files are large; Google serves unicode-range slices.
- Wait for `document.fonts.ready` before capture.
- `font-synthesis: none` (MDN warns that synthesised bold or italic hurts CJK legibility) [24].

### 2.7 Implementation notes for headless Chrome

```css
/* Latin first, then the script face; scale the script face to the Latin partner */
@font-face { font-family: "Brand Bengali"; src: url(/fonts/NotoSansBengali.woff2) format("woff2");
  unicode-range: U+0980-09FF, U+0964-0965, U+200C-200D, U+25CC; size-adjust: 110%; font-weight: 100 900; }
:root { font-synthesis: none; font-optical-sizing: auto; font-kerning: normal; }
body  { font-family: "Inter Tight", "Brand Bengali", sans-serif; }
:lang(bn), :lang(ar), :lang(hi) { letter-spacing: 0 !important; text-transform: none; }
h1, h2, .headline { text-wrap: balance; }  p { text-wrap: pretty; }
.pill { text-box: trim-both cap alphabetic; }   /* Chrome 133+ optical centring */
```

- `size-adjust` scales every metric of that face [23]. `font-size-adjust` (Baseline 2024) can normalise by `ex-height`, `cap-height` or `ic-height` [22].
- Mixed fonts on one line can make line boxes uneven, because each font brings its own ascent and descent. Normalise with `ascent-override` / `descent-override` on the fallback face, or give the element an explicit `line-height` and check it visually [23][Opinion].
- Before the screenshot:
  - `await document.fonts.ready`
  - `document.fonts.check('700 96px "Inter Tight"')` for every face/weight you used; fail the render if any returns false.
  - **[Opinion/Verify]** CDP `CSS.getPlatformFontsForNode` shows which font actually drew each node. Use it to catch silent fallbacks and tofu.

---

## 3. Layout and composition

### 3.1 Grids per format (margins as % of width, gutters, safe zones)

**Grid basics.** A grid has columns, modules, gutters, margins, flowlines and spatial zones. Müller-Brockmann's *Grid Systems in Graphic Design* (1981) is the canonical text; Tschichold and the Van de Graaf canon cover classical page proportions [77].

**[Opinion]** Everything below comes from practice and is sized for our canvases. The safe-zone numbers are cited.

| Format (px) | Columns / gutter | Outer margins | Safe zones and keep-clear areas |
|---|---|---|---|
| **Square 1080×1080** | 6 or 12 columns, 24–32 px gutters (2.2–3%) | **64–88 px (6–8%)**; generous = 96–120 px (9–11%) for luxury or editorial | Keep logo and handle ≥ 48 px from the edges |
| **Portrait 1080×1350 (4:5)** | 6/12 columns, 24–32 px gutters | 64–96 px sides; 80–110 px top and bottom | Profile grid shows a 3:4 centre crop, trimming ≈ 34 px per side (1350 × 3/4 = 1012 px wide) [78]. Keep nothing important in the outer 40 px |
| **Portrait 1080×1440 (3:4)** | 6/12 columns | 72–96 px | Displays uncropped in feed and grid since the 2025-05 3:4 upload support [78] |
| **Story / Reel 1080×1920** | 4 or 6 columns, 24–32 px gutters | 64–90 px sides | Meta Stories: keep ~14% (≈ 250 px) at the top and ≈ 340 px at the bottom free of text and logos [80, Verify]. Reels / TikTok: also keep the right ~120–160 px (buttons) and the bottom ~20–25% (caption + CTA) clear [81, Verify]. **Safe text band ≈ x 64–900, y 250–1500** [Derived] |
| **Carousel slide** | Same as the base format | Same | The first slide is also the grid thumbnail (3:4 crop) [78] |
| **YouTube thumbnail 1280×720** | 12 columns, 16–24 px gutters | 48–64 px (4–5%) | Keep the bottom-right ≈ 200×70 px clear (duration badge) and avoid tiny text anywhere [Opinion]. Test at 168 px wide |
| **Landscape banner / OG 1200×630, 1920×1080** | 12 columns | 5–6% | Platform crops differ; centre the essentials [Verify per platform] |
| **A4 portrait print** | 12 columns, 4–5 mm gutters; baseline 12–14 pt for 9.5–10 pt body | 15–20 mm outer, 12–15 mm top, 15–20 mm bottom | 3 mm bleed beyond trim, text ≥ 3–5 mm inside trim [85]. Larger bleeds (up to 6 mm) for big posters |
| **A5 flyer** | 6 columns, 4 mm gutters | 10–15 mm | 3 mm bleed, 3–5 mm safe |
| **A2/A1 poster** | Modular 6×8 or 8×12 | 20–40 mm | 3–6 mm bleed |

**Baseline and spacing rhythm [Opinion]:**
- Use an **8-px spacing scale**: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128. This follows the 8-dp grid tradition of Material and similar design systems (widely documented; not re-fetched).
- In print, align body text to a **baseline grid equal to the body leading**, e.g. 10/13 pt → 13-pt baseline.
- Headings take whole multiples of the baseline, including their space above and below.
- On social, a 4-px or 8-px baseline is enough.
- Snap every margin, gap and box height to the scale.

**Gutters and grouping [Opinion; 76]:**
- Gutter ≥ ~0.5–1× the body line height.
- **Space between groups ≥ 2× the space inside a group.** Proximity overrides colour and shape similarity as a grouping cue [76].

### 3.2 CRAP and Gestalt, as working rules

Robin Williams' four principles from *The Non-Designer's Design Book* are Contrast, Repetition, Alignment and Proximity (book; not fetched). Gestalt principles per NN/g [12][76]:

- **Contrast:** make different things *very* different (size ≥ 2×, weight ≥ 300 units apart, or complementary value). Weak contrast looks like a mistake [Opinion].
- **Repetition:** reuse type styles, colours, corner radii, icon style and spacing. Across a series, repetition is what makes a set feel designed [Opinion].
- **Alignment:** every element sits on a grid line or a clear axis. Mix no more than two alignment axes per canvas, e.g. a left edge plus centred CTA only when intentional [Opinion]. Left-aligned text is the default for anything over ~3 lines [6].
- **Proximity:** related items close together, unrelated ones apart [76].
- **Similarity, common region, closure, continuation:** use cards or tints (common region) to group, lines and arrows (continuation) to lead, and cropped shapes (closure) for dynamism [12].
- **Figure–ground:** text needs a clear ground. A busy image behind text is a figure–ground failure → scrim or copy space (§1.12).

### 3.3 Focal point, reading patterns, thirds, whitespace, visual weight

- **One dominant focal point per canvas, then a clear second and third** (the hierarchy). If everything is emphasised, nothing is [12].
- **Reading patterns:** NN/g's F-pattern comes from unformatted text, speed-seeking readers and low commitment [74]. Other patterns include layer-cake (heading scanning), spotted, marking, bypassing and commitment.
  - For graphics: front-load the key words in headlines, keep headings strong, and don't rely on body copy being read [74].
  - Z-pattern (top-left → top-right → diagonal → bottom-right) and the Gutenberg diagram are practitioner heuristics for sparse layouts **[Opinion]**. Put the logo and hook along the first stroke, and the CTA at the terminal area (bottom-right), unless culture flips it: in RTL layouts, mirror the order [32].
- **Rule of thirds:** place the subject, eyes or horizon on the third lines or intersections. It dates from John Thomas Smith (1797). It is a guideline, not a law; critics since 1845 warn that rigid use makes work monotonous [77].
- **Visual weight** increases with [75]:
  - size, warm hue (red heaviest, yellow lightest), dark value, saturation
  - texture, density, isolation (local white space)
  - regular shape, vertical or diagonal orientation, sharp focus against blur
  - intrinsic interest, including faces
  - position (higher = heavier)
- **Direction** comes from gaze, arrows or pointing, shape axes, implied motion and the proximity of elements [75]. Make a photographed person look toward the headline or CTA, not off-canvas [75][Opinion].
- **Balance:** symmetric reads calm and formal; asymmetric reads dynamic; radial suits badges and centred marks [12]. Asymmetric balance is the default for "designed" social graphics **[Opinion]**. Offset a large mass with a smaller, denser, more saturated element placed further from the centre (lever principle).
- **Whitespace [Opinion]:**
  - Premium and editorial pieces keep **≥ 40–50% of the canvas visually empty**.
  - Information pieces (infographics, carousels) about 25–35%.
  - Crowding is the most common amateur tell (Venngage lists clutter and competing elements [41]).

### 3.4 Integrating photos, cut-outs and type (depth, overlap, framing) — [Opinion: practitioner technique]

1. **Plan the copy space first.** When generating the image, ask for the subject on one third and calm negative space where the type will go, lit to suit the palette.
2. **Text behind the subject.** This is the magazine-cover depth effect, which Apple also popularised on iOS lock screens [44]. Stack: background photo → headline → subject cut-out (transparent PNG) on top.
   - The subject may cover **≤ 20–30% of the headline's letter area**.
   - Never cover the first letter or a whole word; the word must stay readable.
3. **Overlap boundaries.** Let the headline or a colour block cross the edge of a photo panel by 10–25% of its height to tie layers together. Consistent overlap across a series becomes a recognisable device.
4. **Frame with the scene.** Align type to architectural edges, the horizon or table lines. Place text inside natural frames (doorways, windows, negative sky).
5. **Scale contrast.** A huge type crop bleeding off the canvas plus a small human figure, or a huge face with small type, reads as confident.
6. **Colour sampling.** Pick accent and type colours from the image (a secondary object, not the dominant hue). Or grade the image toward the brand (duotone or split-tone, §4.5).
7. **Believable depth.** Cut-outs need contact shadows that match the light direction, consistent colour temperature, and clean edges at 200% zoom (no halos or fringes). No generic outer glows.
8. **Image-in-type** (`background-clip: text`) only for one or two short words at ≥ 200 px, where the image stays recognisable.
9. **Cropping people.** Don't crop at joints (ankles, knees, wrists, elbows); crop mid-limb. Leave lead room in the gaze direction.
10. **Trend hook:** It's Nice That (2026-01-12) flags "visual index" layouts of flattened, numbered cut-outs arranged like specimens [54]. Cut-out collages pair well with the imperfect / scrapbook trend (§6).

### 3.5 Designing series (carousels, campaign sets)

**Build a system before slide 1 [Opinion]:**
- one grid and margin set
- 2–3 type styles
- colour roles
- one recurring graphic device (a crop shape, a strip, a corner mark)
- a fixed logo or handle position
- a page indicator ("02/08")
- a fixed headline position, so the eye knows where to look on each swipe

**Cover slide:**
- Hook headline ≤ 8 words.
- The strongest image.
- A subtle swipe cue: an arrow, or an element that runs off the right edge into slide 2.
- Hootsuite: the first image is the hook; keep copy minimal, one idea per slide, a consistent palette and style, and end with a CTA [79].

**Limits:**
- Instagram carousels allow **up to 20** items [79].
- Carousel engagement (≈ 10%) vs single images (≈ 7%) and Reels (≈ 6%), per figures Hootsuite cites [79, Verify: vendor data].

**Seamless panorama:**
- Design one wide canvas (N × 1080) and slice it.
- Keep text and faces off the seams.
- Every slice must also work alone.
- The first slice doubles as the 3:4 grid thumbnail.

**Rhythm:**
- Vary the layouts (e.g. A-B-A-C) inside the same grid, so the series isn't monotonous.
- Allow 20–40 words per slide at most **[Opinion]**.

**Campaign sets:**
- One key visual + master layout, re-flowed to 1:1, 4:5, 3:4, 9:16 and 16:9. The logo, CTA and colour roles keep the same *relative* positions.
- Re-compose for each ratio rather than scaling. Keep the type size in *rendered* terms (§1.2), not in canvas percent.
- Keep the photo treatment (grade, grain, crop style) identical across the set.

---

## 4. Colour

### 4.1 Palette construction

- **60-30-10:** 60% dominant, 30% secondary, 10% accent. The origin is interior design, and the provenance is unclear [68]. **[Opinion]** On graphics, "60" is usually the background or photo field, "30" the text and support shapes, "10" the CTA or highlight.
- **Refactoring UI** [67]:
  - Real designs need more colours than you think: **8–10 greys**, and **5–10 shades per primary and accent** (nine is a clean number).
  - Pick the base (the "button" shade), then the darkest (for text) and the lightest (for tinted backgrounds), then fill the middle.
  - Don't rely on `lighten()` / `darken()` or random generators.
  - Pure black looks unnatural; start from a very dark grey.
  - Increase saturation toward the lightest and darkest shades so they don't wash out.
  - Rotate hue toward brighter hues (yellow, green) to lighten and toward blue to darken, because perceived brightness differs by hue.
- **[Opinion] Our palette recipe (OKLCH):**
  1. Brand hue H.
  2. Build a 10-step ramp: L = 0.97 / 0.93 / 0.87 / 0.78 / 0.68 / 0.58 / 0.48 / 0.39 / 0.30 / 0.22. Chroma peaks at the middle steps and is reduced at the extremes; nudge hue ±5–10° at the ends.
  3. Neutrals: the same H at chroma 0.005–0.02 (warm or cool tinted greys).
  4. Accent: complementary or split-complementary to H, used at ≤ 10% of the area.
  5. Near-black: L 0.16–0.22 with a little of the brand chroma.
- **Palette size for one piece:**
  - 1 dominant hue + 1 accent + neutrals is professional.
  - Three saturated hues is the practical maximum for a single graphic, except in deliberately maximalist styles [Opinion].

### 4.2 Contrast for text and graphics

- **WCAG 1.4.3:**
  - text ≥ **4.5:1**
  - large text (≥ 18 pt ≈ 24 px, or ≥ 14 pt bold ≈ 18.66 px) ≥ **3:1**
  - logotypes and pure decoration are exempt [65]
- **Non-text graphics** (icons, chart marks, input borders) ≥ **3:1** under WCAG 1.4.11 (known criterion; not re-fetched).
- On social, judge "large" by the *rendered* size (§1.2): a 72-px canvas line ≈ 24 px on a 360-px phone [Derived].
- **APCA** (optional, perceptual) [66]:
  - body Lc 75 minimum, 90 preferred
  - non-body text Lc 60
  - headlines Lc 45
  - any text Lc 30
  - non-text Lc 15
  - Light-on-dark gives negative Lc values; judge by magnitude.
- **Text on photos:** use the worst-case-pixel method (§1.12) and design for the worst image [13].
- Don't reduce text contrast to look "elegant". NN/g explicitly warns against it [12].

### 4.3 Tints, shades, black and white

- Build tints by increasing L and lowering chroma in OKLCH. Adding white in sRGB greys the colour out.
- Build shades by lowering L while keeping or slightly raising chroma and shifting hue a little [67][Opinion].
- **Avoid:**
  - pure #000 fills (use near-black)
  - pure #FFF behind long text on screens (use off-white L 0.97–0.99 tinted toward the brand)
  - grey text on coloured backgrounds; use a darker or lighter shade of the background hue instead (Refactoring UI principle [67])

### 4.4 Gradients: designed vs cheap

**Designed:**
- **Interpolate in OKLab or OKLCH** (`linear-gradient(in oklch, …)`). Default sRGB interpolation passes through a grey "dead zone"; OKLab keeps the middle vivid [69].
- **2–3 stops of adjacent hues** (≤ 60° apart), or tints of one hue [Opinion].
- **Eased stops** for scrims and fades [16].
- **A light-source logic:** the gradient behaves like light falling on a surface [Opinion; 53 calls 2026 gradients "light and atmosphere"].
- **1–3% monochrome noise or grain** to break 8-bit banding on large areas. Banding and muddy midtones are two different problems: banding needs noise, muddy midtones need colour-space interpolation [69 + secondary].

**Cheap / AI:**
- The **indigo→purple** or blue→purple default [40]
- Rainbow multi-stop gradients
- Neon glow gradients on dark backgrounds [40]
- Unmotivated "mesh-blob" wallpapers
- Gradient text on everything
- Banding on large smooth areas

### 4.5 Duotone and colour grading

- **Duotone** maps an image's tones to two inks: traditionally a dark ink plus a second colour, with highlights and midtones carried by the second colour [73].
- **[Opinion] Digital recipe:**
  - Shadows → darkest brand shade (L ≤ 0.25).
  - Highlights → light brand tint (L ≥ 0.85).
  - Increase image contrast before mapping.
  - Re-check text contrast afterwards.
- **In Chrome:** apply an SVG `feColorMatrix` (grayscale) + `feComponentTransfer` (table per channel) filter, or grayscale + `mix-blend-mode: multiply/screen` layers.
- **Series use:** one duotone pair per campaign makes mixed stock or AI photos look like a single shoot [Opinion].

### 4.6 Colour by industry — use with caution

- **Evidence is weak and contextual.** No colour appeals to all audiences. Meanings vary by culture: red is anger in some Western contexts but not in Japan; purple is jealousy mainly for Polish respondents; expected flavours of brown drinks differ between the UK and Taiwan. Studies such as Labrecque & Milne link red to excitement and blue to competence, but those are correlational findings, not laws [70].
- **Typical associations [Opinion, conventional]:**
  - **Finance / insurance:** navy or deep blue, green, restrained accents.
  - **Healthcare:** blue, teal, green and white. Avoid alarming reds except for warnings.
  - **Tech:** blue or violet (now an AI cliché, see §5), or black and white + one electric accent.
  - **Luxury:** black, ivory, deep jewel tones; metallic "gold" as flat ochre or tan in digital (real foil in print).
  - **Food:** warm reds, oranges and yellows for appetite and fast food; greens and earth tones for fresh or organic.
  - **Eco:** greens, ochres, clay.
  - **Kids and education:** saturated primaries (Pinterest's "Primary Play" 2025 [89]).
  - **Beauty and wellness:** blush, nude, soft neutrals (Pantone 2025 Mocha Mousse and 2026 Cloud Dancer [50]).
  - **Sport:** black or white + one saturated accent.
  - **Government / NGO:** accessible blues and neutrals.
- **Cultural checks [Opinion; verify locally]:**
  - White is a mourning colour in parts of East and South Asia.
  - Red is luck and celebration in China and bridal in much of South Asia.
  - Green carries religious associations in parts of the Muslim world.
- **For Bangladeshi clients [Opinion; verify with the client]:**
  - Red + green are the national colours (Victory and Independence days).
  - Red + white is customary for Pohela Boishakh.
  - Black + white is worn for 21 February (Language Martyrs' Day).
  - Memorial days need muted palettes and no sales messaging.
- **Global by default:** take place and culture cues from the *client's* market, not the requester's locale (see the user's memory rule).

### 4.7 Colour-blind safety

- **Prevalence:** about 8% of men and 0.5% of women of Northern European ancestry have red–green colour-vision deficiency (NEI figure, via [71]).
- **Rules [Opinion]:**
  - Never distinguish meaning by hue alone, especially red vs green.
  - Keep an OKLCH lightness difference of ΔL ≥ 0.15–0.20 between categories that must be told apart.
  - Add labels, icons or patterns.
  - Blue / orange is the safest contrasting pair.
  - Use the Okabe–Ito palette for charts (8 colours built for all common CVD types; secondary source).
- **Automate:** render once each with Chrome/Puppeteer `emulateVisionDeficiency('deuteranopia' | 'protanopia' | 'tritanopia' | 'achromatopsia' | 'blurredVision')` [72]:
  - **achromatopsia** doubles as a grayscale value-hierarchy check
  - **blurredVision** doubles as the squint test (§9)

---

## 5. "Looks AI or cheap" vs "looks professional"

Sources for the tells:
- Anthropic's own guidance (2025-11-12): overused fonts (Inter, Roboto, Arial, system fonts), purple gradients on white, predictable layouts, flat characterless backgrounds, scattered micro-motion [39].
- 925 Studios (2026): Inter, the indigo→purple gradient, three rounded cards with thin-line icons, weightless headline copy, generic thin-line icons [40].
- Venngage (2026-08-12): inconsistent kerning and baselines, oversized headings, cramped text, clutter, repetitive brush-stroke banners and circle icons, polish without a message [41].
- Kellogg (2024-09-09): photo tells in five categories [42].
- NN/g on glassmorphism legibility (2024-06-07) [43].

### 5.1 Tell → why it reads cheap → how senior designers avoid it

| # | Tell | Why it reads as AI or template | Senior fix (numeric where possible) |
|---|---|---|---|
| 1 | Generic gradients (indigo→purple, blue→pink, neon on dark) | The statistical default of AI tools [40] | Palette from the brand, the product or the photo; 1 accent ≤ 10% of the area; OKLCH gradients of adjacent hues with grain (§4.4) |
| 2 | Glossy blobs, orbs, floating spheres, liquid chrome | Decoration with no referent | Replace with real photography, real materials, texture or type. If abstract, tie it to a brand shape |
| 3 | Glassmorphism everywhere (frosted cards on busy photos) | Trendy since Apple's Liquid Glass (2025-06-09) [44], but illegible without heavy blur [43] | ≤ 1 glass surface per piece; blur ≥ 24 px at 1080; text contrast checked; opaque fallback |
| 4 | Fake 3D icons and clay emoji-style icons; mixed icon styles | Stock-kit look; inconsistent geometry | One icon family, one stroke width (e.g. 2 px at 24 px → scale proportionally), one corner radius, and optical size corrections |
| 5 | Centre-aligned everything (logo, headline, sub, button stacked on the axis) | The default composition of templates and generators | An asymmetric grid, left-aligned text, a focal point on the thirds; centre only single short lines |
| 6 | Too many effects (shadow + glow + stroke + gradient on one element) | Every effect is a decision; stacking signals no decisions | ≤ 1 effect per element, ≤ 2 effect types per piece |
| 7 | Heavy or default drop shadows (black, 50%, offset 5/5) | Screams template | Soft, large blur (≥ 2× the offset), 8–20% opacity, tinted by the background colour, offset direction consistent with the scene light; or no shadow |
| 8 | Random sparkles ✨, lens flares, bokeh dots, "magic dust" | Filler meaning "AI / new" | Delete them. Use motion or light only where the scene justifies it |
| 9 | Emoji clutter in graphics | Social-caption habit leaking into design | 0 emoji on the canvas (one only if it is the concept) |
| 10 | Inconsistent spacing and edge-hugging elements | No system | 8-px scale, equal margins, gaps between groups ≥ 2× gaps within, consistent radii |
| 11 | Stock clichés (handshakes, lightbulb brains, robots for "AI", globe networks, people pointing at laptops, laughing-at-salad) | Seen a million times; carries no information | Specific, local, candid imagery for the client's market; show the real product or context; natural light |
| 12 | Illegible or pseudo-text inside AI images (signs, labels, fake logos) | The most recognisable AI artifact [42] | Prompt for no text; inspect the background at 200%; mask or blur gibberish; set every word in HTML |
| 13 | Over-saturated, HDR, teal-orange grade; plastic or waxy skin; too-perfect symmetry; cinematic haze | Stylistic artifacts [42] | Natural grade, restrained saturation, real skin texture, slight imperfection, a coherent light source (see the user's "natural photo look" rule) |
| 14 | Meaningless decorative elements (dot grids, squiggles, random circles, brush-stroke banners) | Decoration without function [41] | Removal test: if deleting it changes nothing, delete it |
| 15 | Template-y hierarchy: everything bold, ALL-CAPS paragraphs, 5+ sizes | No hierarchy | 3 sizes, 2–3 weights, caps only for short labels (§1.6–1.7) |
| 16 | Default fonts (Inter, Roboto, Poppins, Montserrat, Space Grotesk) and default weights (400/700 only) | Distributional default [39] | Choose for meaning (§2.2); use optical sizes; purposeful extreme weight contrast |
| 17 | Three rounded cards in a row; bento grids for no reason | SaaS-template skeleton [40] | Content-driven layout; vary scale; break the grid once, deliberately |
| 18 | Weightless copy ("Elevate your brand", "Unlock your potential") | Says nothing specific [40] | Concrete claim, number or benefit; the client's own voice |
| 19 | Rainbow palettes, 4+ saturated hues, pure #000 / #FFF | No palette discipline | §4.1 recipe |
| 20 | "Same face" AI people (generic 30-somethings, identical smiles, uncanny eyes) | Anatomical and stylistic tells [42] | Diverse, market-appropriate, candid people; check eyes, teeth, hands and ears at 200% |
| 21 | Stretched or distorted logos, low-res logos, logo with added effects | Brand violation | Use vector (SVG) logo files only, at the defined clear space and minimum size [59] |
| 22 | Low-res upscaled images, JPEG blocks, banding | Visible at 100% | Generate at ≥ 1× final pixel size (2× for crops); export PNG for flat graphics; add grain to gradients |

### 5.2 AI-image artifact checklist (use on every generated visual)

Based on Kellogg's five categories [42]. Check at 100% and 200%:

1. **Anatomical:**
   - extra or missing fingers or limbs
   - merged bodies
   - odd teeth; non-round pupils; hollow eyes
   - elongated necks
   - nail-less hands
2. **Stylistic:**
   - waxy skin, over-saturation, "too perfect" beauty
   - face lighting that doesn't match the background
   - smudges; patchwork backgrounds; over-cinematic depth
3. **Functional:**
   - misspelled or fake text and logos
   - objects used wrongly
   - straps, buttons or buckles that don't work
   - food that defies physics
4. **Physics:**
   - shadows at impossible angles
   - reflections that don't match
   - warped perspective or stairs
   - floating feet
5. **Sociocultural:**
   - scenes implausible for the market
   - anachronisms
   - culturally insensitive details

**Any hit → regenerate or retouch. Never ship.**

### 5.3 Professional finishing checklist (pre-export) — [Opinion; compiled from §1–4]

**Typography**
- [ ] Real punctuation: ’ “ ” … – (ranges) — (breaks) × (dimensions) − (minus); no straight quotes; no double spaces.
- [ ] Non-breaking spaces between number and unit, currency and amount, and within dates and names.
- [ ] Headline lines balanced; no runts (one-word last lines); no split names or numbers; no hyphenation in display text.
- [ ] Tracking: caps +5–12%; display tightened; nothing tracked in Bengali, Arabic or Devanagari.
- [ ] Line heights set explicitly per style and script; no collisions of accents, matras or descenders.
- [ ] Kerning checked on display pairs; optical left edge aligned; quotes hung.
- [ ] Numbers: lining for statistics, tabular in tables; one digit script per piece.
- [ ] Every font actually loaded (`document.fonts.check`); no synthetic bold or italic; no tofu (□).

**Layout**
- [ ] Every element on the grid; margins equal (or intentionally unequal); spacing values from the 8-px scale.
- [ ] Safe zones respected (story top/bottom, Reels right rail, 3:4 grid crop, YouTube timestamp).
- [ ] One focal point, clear reading order (squint and blur test), balance intended.
- [ ] Consistent corner radii (one or two values), stroke widths and icon family.
- [ ] Nothing accidentally touching or tangent to an edge; no near-misses (elements 2–6 px apart that look like errors).

**Colour and image**
- [ ] Text contrast ≥ 4.5:1 (small) / 3:1 (large) against the worst pixels; charts and icons ≥ 3:1.
- [ ] ≤ 1 dominant + 1 accent hue (unless the style is deliberately maximal); neutrals tinted; no pure black fills.
- [ ] Gradients in OKLCH, with grain on large areas; no banding.
- [ ] AI-image checklist §5.2 passed; light direction consistent across the composite; clean cut-out edges.
- [ ] Colour-blind and grayscale renders still readable.

**Output**
- [ ] Exact pixel size and aspect ratio for the platform; sRGB with profile embedded; PNG for flat or text-heavy work, high-quality JPEG/WebP for photographic work; file size under the platform's limits (YouTube: 2 MB phone / 50 MB desktop [82]).
- [ ] Print: PDF with 3 mm bleed, text ≥ 3–5 mm inside trim, images ≥ 300 ppi at final size, CMYK conversion and rich black per the printer's spec (Chrome outputs RGB PDFs; convert downstream) [85][Verify with printer].
- [ ] Copy proofread against the brief (names, dates, prices, phone numbers, URLs); legal lines present.

---

## 6. Trends 2025–2026 (what the reports say, and what lasts)

### 6.1 Report-by-report (paraphrased)

**Canva Design Trends 2025** (report of Nov 2024) [46] — 7 trends:
- Analog Meets AI (collage and craft + AI)
- Future in Motion (motion search +109%, animation +78%)
- Serious Fun (playful, nostalgic; "silly" +92%)
- Refined Grit (stripped-back, handwriting and scribbles)
- Mechanical Botanical (organic + futuristic)
- Shape Theory (modular bold shapes, back-lit photos, warm colours)
- Opulence Era (minimal + luxurious details)

**Canva Design Trends 2026, "Imperfect by Design"** (Dec 2025) [45] — 10 trends:
- Reality Warp (liminal/uncanny searches +220%)
- Prompt Playground (lo-fi, early-internet; lo-fi searches +527%)
- Explorecore (zine and Substack layouts +85%)
- Texture Check (hyper-real glassy, waxy, tactile surfaces, +30%)
- Notes App Chic (scrapbook and DIY, +90%)
- Opt-Out Era ("clean layout", "serif", "simple branding" +54%)
- Drama Club (cinematic storytelling, +27%)
- GrannyWave (India: handloom, Bollywood glamour, Hindi typography)
- Zinegeist (Mexico: DIY zine, brutalist type posters +77%)
- Block Party (Spain: vintage folklore)

**Adobe 2026:**
- Four macro trends [47]: All the Feels (multisensory, tactile), Surreal Silliness (playful AI-driven absurdity), Emotional Authenticity (local creators, real communities) and human-centred analog design.
- Adobe Express top-10 graphic trends (2025-12-12) [47]: sensory materials; exaggerated playful letterforms (oversized sans, bubbly, handwritten); saturated immersive palettes with real textures; surreal collage; organic and imperfect; freeform storytelling layouts (overlap, asymmetry); warm personal style; local and cultural flavour; layered collage; maximalist "controlled chaos".

**Pinterest Predicts:**
- **2025** [49][89]: Cherry Coded, Aura (mood colours), Primary Play (bold primaries in UI and branding), Rococo (ornamental, classical type). 2025 Palette (2025-01-16): cherry red, butter yellow, aura indigo, dill green, alpine oat.
- **2026** (2025-12-09; Pinterest claims 88% accuracy over six years) [48]. Visually relevant items: Gimme Gummy (jelly and rubber textures), FunHaus (circus stripes), Neo Deco (modern Art Deco, chevrons, metallics), Glitchy Glam (intentional imperfection), Laced Up (doily and lace), Vamp Romantic (dark romantic), Cool Blue (sub-zero palette), Extra Celestial (holographic and opalescent), Opera Aesthetic (theatrical drapery), Wilderkind (animal motifs), Poetcore, Afrohemian.

**Pantone Colour of the Year:**
- 2025: PANTONE 17-1230 **Mocha Mousse**.
- 2026: PANTONE 11-4201 **Cloud Dancer**, a white, announced 2025-12-04; the first white since the programme began in 1999 [50].

**Figma, "Top web design trends for 2026"** [51]:
- 3D and immersive; experimental navigation; vibrant palettes and neon gradients; bold typography; dark mode
- motion; gamification; neumorphism; retrofuturism; maximalism; collage; neo-brutalism / anti-design; sustainable web

**Type foundry and editorial views:**
- **Fontfabric** (2025-12-09, upd. 2026-08-13) [53]: perfectly imperfect / naive; decentralised brands; **typographic maximalism (type as hero image)**; creative-coding systems; grid-native brands; heritage re-imagined; hyper-real 3D; atmospheric gradients (light, not wallpaper); retro analog / screen-print; counterculture zines.
- **It's Nice That** (2026-01-12) [54]: xerox / photocopy print texture ("make me a copy"; it says AI still struggles to fake layered, scanned, mixed-media work); visual index of numbered cut-outs; micrographics (tiny technical type as ornament); "blotch" organic logos; pick-and-mix mismatched lettering.
- **Kittl** (2026-06-30) [52]: naive design, type collage, blueprint (technical drawing), trinket grids, punk grunge, future-medieval, distorted portraits, surveillance / CCTV UI, grainy blur, 90s "signal" TV graphics.

**Shutterstock:** in 2025–26 it published a data-led *Creative Impact Report*, not a visual trend list. Headline finding: marketing spend +33% vs purchase-intent impact +17% (2023→24). Creative quality, emotional relevance and cultural fit drive ROI; AI is positioned as a tool for emotional relevance [55]. Secondary summaries mention AI-enhanced visuals, eco-optimism, surreal storytelling and motion (low confidence).

**Apple Liquid Glass** (2025-06-09): a translucent, refracting UI material across all Apple OSes [44]. It revived glass looks in marketing.

**Behance / Dribbble:** no platform-level 2026 trend report was located this session. The "Design Trends 2026" galleries there are individual designers' views (e.g. behance.net/gallery/239027109, dribbble.com/tags/design-trends-2026). Treat them as signals, not sources.

### 6.2 Durable vs fad — [Opinion, grounded in cross-report recurrence]

| Theme | Evidence of durability | Verdict | Best-fit industries | Use with care in |
|---|---|---|---|---|
| **Human, imperfect, handmade signals** (scribbles, scans, xerox, grain, naive drawing) | In Canva 2025 *and* 2026, Adobe 2026, Fontfabric, Kittl and INT; a structural reaction to AI sameness [45][46][47][52][53][54] | **Durable (2026–27+)** | Food, cafés, lifestyle, education, creators, NGOs, local retail, music | Banking, medical (use only a light grain or texture) |
| **Type as hero / expressive typography** | Adobe #2, Fontfabric #3, Figma, Kittl type collage | **Durable**: cheap to produce, brand-ownable | Events, media, fashion, tech launches, campaigns | Dense information pieces |
| **Editorial / zine storytelling layouts** | Canva Explorecore + Zinegeist; Adobe freeform layouts | **Durable** for content marketing and carousels | Education, B2B thought leadership, publishing, NGOs | – |
| **Local / cultural specificity** | Adobe local flavour; Canva GrannyWave, Zinegeist, Block Party | **Durable**, and strongly relevant to South Asian clients (Bengali/Devanagari lettering, handloom motifs) | Consumer brands, festivals, food, fashion | Avoid pastiche and stereotypes; check with locals |
| **Clean "opt-out" minimalism** | Canva Opt-Out Era (+54%) | **Durable** (counter-cycle to maximalism) | Finance, health, B2B, premium | Youth brands may find it cold |
| **Maximalism / collage / controlled chaos** | Adobe #9–10, Figma, Kittl | **Cyclical**: strong now, will swing back | Youth, music, entertainment, fashion drops | Corporate, healthcare |
| **Tactile / hyper-real 3D materials** (jelly, gummy, glassy, waxy) | Canva Texture Check, Pinterest Gimme Gummy, Fontfabric 3D | The principle (tactility) lasts; **"gummy/jelly" is a fad** | FMCG, beauty, toys, games | Anything needing trust or legibility |
| **Surreal / absurd AI imagery** | Canva Reality Warp; Adobe Surreal Silliness | **Fad-ish**, and raises the "AI look" risk | Entertainment, youth campaigns | Trust sectors; product truth |
| **Retro / lo-fi / 90s TV / Y2K** | Canva Prompt Playground, Fontfabric Retro Frequencies, Kittl Signal Graphics | **Cyclical nostalgia** | Music, gaming, streetwear | – |
| **Glass / Liquid Glass / glassmorphism** | Apple 2025; NN/g legibility caveats [43][44] | **Fad** in marketing graphics | Tech launches (sparingly) | Text-heavy pieces |
| **Neo-Deco / Rococo / opulence** | Pinterest 2025 Rococo, 2026 Neo Deco; Canva Opulence Era | **Seasonal niche** | Hospitality, jewellery, weddings, galas | – |
| **Trend colours** (Mocha Mousse, Cloud Dancer, cherry red, butter yellow, Cool Blue) | Annual by definition | **Seasonal accents only**; never the base of a brand | Campaign accents, seasonal posts | Brand identities |

---

## 7. Logo design

### 7.1 Principles

- **Paul Rand** ("Logos, Flags, and Escutcheons", AIGA 1991) [56]:
  - A logo's job is to identify and point, as simply as possible.
  - Its meaning comes from the quality of what it represents, not the other way round.
  - Complex, fussy or arcane marks tend to defeat themselves.
  - Simplicity is hard to reach but worth the effort.
- **Chermayeff & Geismar & Haviv** (*Identify*, 2011) [57]:
  - A good mark is **appropriate, distinctive and simple, in that order**.
  - It must be unusual enough to hook memory while staying simple in form.
  - A simple, distinctive mark can take fashionable treatments (3D, shadows) when needed and stay recognisable.
- **David Airey**, *Logo Design Love*, chapter "Elements of iconic design" [58]:
  - keep it simple
  - make it relevant
  - incorporate tradition
  - aim for distinction
  - commit to memory
  - think small
  - focus on one thing

### 7.2 Specs a professional logo system includes

| Spec | Rule | Source / basis |
|---|---|---|
| **Versions** | Primary lockup, horizontal and stacked lockups, symbol only, wordmark only; full-colour, 1-colour, black, white (reversed) | [61]; [Opinion] |
| **Mono test** | Must work in one flat colour, and as a stamp, cut vinyl, engraving or embroidery; gradients can't be the only version | [86] |
| **Minimum size** | Defined in px *and* mm. Example: Spotify logo ≥ 70 px / 20 mm, icon ≥ 21 px / 6 mm [59]. **[Opinion]** Symbols should read at 16×16 (favicon) and wordmarks at 24 px cap height |
| **Clear space** | A unit taken from the mark itself, applied on all sides (Spotify: ½ the icon height [59]). Common practice: 1–1.5× the cap height or a symbol part (secondary summary) |
| **Stroke / detail survival** | **[Derived/Opinion]** At the minimum display size, the thinnest stroke must stay ≥ 1 device px (screen) or ≥ 0.25 pt (print). E.g. a 24-px-tall mark needs strokes ≥ ~8% of its height at 3× density, or ≥ 2 px at 1× | [86] ("thin strokes break at small sizes") |
| **Misuse list** | No rotating, stretching, recolouring outside the palette, adding effects, outlining, or placing on busy or low-contrast backgrounds; no rebuilding from parts | [59] |
| **Colour specs** | HEX + RGB for screen; CMYK + Pantone for print | [61] |
| **Files** | Master SVG; PDF/EPS vector; transparent PNG @1×/2×/3×; favicon set (16/32/180/192/512); versions per colour mode | [Opinion; standard practice] |

### 7.3 Process — [Opinion; aligned with Airey [58]]

1. **Brief and research:** audience, positioning, competitors' marks (mapped on a grid to find white space), constraints (languages and scripts, applications, sizes).
2. **Concepting:** word lists and mind maps → **many** thumbnail sketches (dozens) → pick 3 routes.
3. **Construction in vector:**
   - geometric scaffolding with optical corrections (overshoots, stroke tapering at joins, ink traps if tiny sizes matter)
   - hand-kerned wordmark
   - custom letter tweaks instead of stock type
4. **Stress tests:** 16 px, 1 colour, reversed, on photos, dark mode, at a distance, animated, and side by side with competitors.
5. **Present in context** (mockups on real applications), with the rationale tied to the brief.
6. **Refine → finalise → deliver** the files and the logo section of the guidelines.

**For our HTML pipeline:**
- Build logos as SVG with text converted to paths.
- Use image generators only for mood exploration, never for final marks (see 7.4).

### 7.4 Common amateur mistakes and AI-logo mistakes

**Amateur** [86]:
- too many elements, colours or details
- poor or unkerned typography
- trend-chasing
- raster-only files
- thin strokes that vanish at small sizes
- gradient-dependence
- clip-art or stock symbols
- too literal ("dentist = tooth")
- illegible scripts
- several fonts in one mark
- not tested small or in mono

**AI-generated logos (additional) [Opinion + 42 + 60]:**
- garbled or inconsistent letters
- over-rendered illustrations (3D, glossy, photoreal textures, glows) that can't be vectorised cleanly
- inconsistent stroke weights and corner radii
- accidental asymmetry
- generic swooshes, globes, leaves, lightbulbs and "people" figures
- similarity to existing marks (trademark risk)
- no mono version

**Legal:** the US Copyright Office's Part 2 report (2025-01-29) says prompts alone are not enough human authorship. Purely AI-generated output is not copyrightable; human-authored contributions that are perceptible in the output can be [60]. **Human redrawing and authorship are therefore needed for a protectable mark** [Opinion: consult counsel; trademark is a separate question].

---

## 8. Brand guidelines (brand book) and brand-kit tokens

### 8.1 Structure of a professional brand book

Frontify (updated 2026-09-04) [61]:
1. **Brand core:** mission, vision, values, positioning, audience, personality, promise.
2. **Logo:** approved variations, clear space, minimum sizes, colour versions, lockups, misuse examples.
3. **Colour:** primary, secondary, neutral and accent palettes; **HEX + RGB for digital, CMYK + Pantone for print**; usage rules and proportions.
4. **Typography:** primary and secondary faces, approved weights, sizes and hierarchy levels, line height, letter-spacing, fallbacks per content type.
5. **Imagery and iconography:** photo style (lighting, composition, subjects, treatment), illustration style, icon rules, concrete examples of what to avoid.
6. **Voice and tone:** voice vs contextual tone, traits, writing principles, vocabulary, channel guidance, on-brand vs off-brand copy.
7. **Social standards:** profile specs, caption style, platform sizes, templates, hashtags, approvals.
8. **Templates and applications:** decks, reports, email, social, events.
9. **Governance:** owners, approvals, exceptions, review cycle (at least yearly).
10. **AI and retrieval rules:** approved sources and tools, what AI may do, human review, examples of acceptable output.

**Usability:** side-by-side do/don't examples beat paragraphs of rules; digital guidelines beat static PDFs; link the rules to the actual assets [61]. The classic canon of standards manuals (e.g. NASA 1975) follows the same logic: specification plus application examples [Opinion].

### 8.2 Brand-kit tokens our skill should store (DTCG 2025.10)

- **Format:** the W3C Design Tokens Community Group spec reached its first stable version, **2025.10**, on 2025-10-28 [62]. It supports:
  - theming and multi-brand
  - modern colour spaces (Display P3, OKLCH, all CSS Color 4 spaces)
  - aliases
- **Syntax:**
  - colour `$value` = `{colorSpace, components[], alpha, hex}`
  - dimension = `{value, unit: "px" | "rem"}`
  - aliases use `{group.token}`
  - `$type` values: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number, strokeStyle, border, transition, shadow, gradient, typography [62]

**Minimum token set for a graphic-design brand kit [Opinion]:**
- `brand.meta`: name, tagline, markets / locales / scripts (e.g. `en`, `bn`), industry, personality adjectives (3–5), voice do/don't phrases.
- `logo.*`: file paths per version (primary, horizontal, stacked, symbol, wordmark × colour modes), clear-space unit (e.g. `0.5 × symbolHeight`), min sizes (px and mm), allowed backgrounds, misuse list.
- `color.*`:
  - ramps (50–900) for primary, secondary, accent and neutral, with HEX, RGB, OKLCH, CMYK and Pantone for the key swatches
  - roles (bg, surface, text, text-muted, accent, cta)
  - approved text/background pairs with measured contrast ratios
  - 60/30/10 guidance
- `font.*`: families per role (display / text / mono / script-specific: `bn`, `ar`, `hi`, `ja`), weights, `size-adjust` per script face, fallbacks, and Google Fonts availability.
- `type.scale.*` per canvas (post, story, thumbnail, A4, A5, poster): size, line-height, tracking, case, `text-wrap`.
- `space.*` (8-px scale), `grid.*` per format (columns, gutter, margins, safe zones), `radius.*` (1–2 values), `stroke.*`, `shadow.*` (or explicitly none), `effects.allowed` (list; default none).
- `image.*`:
  - style prompt fragments (subject, lighting, grade, lens, texture)
  - negative prompt list (no text, no plastic skin, no purple gradient …)
  - treatment (duotone pair, grain %)
  - crop rules
- `icon.*`: library, stroke width at 24 px, corner style, fill vs line.
- `motif.*`: recurring graphic devices and their rules.
- `special_days.*`: tone rules, colour overrides, "no sales" flags.
- `templates.*`: per-format layout specs (JSON), each tied to the grid.

**Minimal example (illustrative values):**

```json
{
  "color": {
    "brand": { "600": { "$type": "color", "$value": { "colorSpace": "oklch", "components": [0.48, 0.14, 250], "hex": "#1F5FAF" },
                        "$extensions": { "cmyk": [88, 55, 0, 5], "pantone": "2935 C" } } },
    "text":  { "onLight": { "$type": "color", "$value": "{color.neutral.900}" } }
  },
  "type": {
    "post.headline": { "$type": "typography", "$value": { "fontFamily": ["Bricolage Grotesque", "Anek Bangla"],
      "fontSize": { "value": 120, "unit": "px" }, "fontWeight": 800, "lineHeight": 1.02, "letterSpacing": { "value": -0.02, "unit": "rem" } } }
  },
  "space": { "4": { "$type": "dimension", "$value": { "value": 32, "unit": "px" } } }
}
```

(`letterSpacing` sits inside typography per the spec's composite. Non-spec data such as CMYK or Pantone goes in `$extensions` [Opinion/Verify].)

---

## 9. Critique: how senior designers critique, converted into a scored rubric

### 9.1 Frameworks

- **NN/g** (Sarah Gibbons, 2016-10-23) [63]:
  - Critique asks whether the design **meets its objectives**.
  - Roles: presenter, critiquers, facilitator.
  - Agree the objectives and scope first.
  - Feedback goes to the work, not the person, framed around goals (instead of "this is terrible", ask "does this help the user do X?").
  - It is a conversation, not a command.
- **Connor & Irizarry, *Discussing Design*** (talk 2012-07-13; book O'Reilly 2015) [64]:
  - Critique is analysis against goals and principles, distinct from gut **reaction** and from **direction** (jumping to solutions).
  - Ask: what is the objective, which elements serve it, are they effective, and why or why not.
  - A review is about sign-off; critique is ongoing and designer-driven.
- **[Opinion] Senior visual-design critique habits:**
  - **Squint test:** blur the piece until only masses remain. Does the hierarchy survive?
  - **Grayscale test:** does value alone carry the hierarchy?
  - **Thumbnail test:** view at the real display size (360 px wide; 168 px for YouTube).
  - **5-second test:** what do you remember?
  - **Removal test:** delete each element in turn; if nothing is lost, it stays deleted.
  - **Swap-the-logo test:** if a competitor's logo fits equally well, the design is generic.
  - **Mirror / flip test:** reveals balance problems.
  - **Distance test** for posters.
  - **Edge audit:** margins, tangencies, near-alignments.
  - **Type audit:** rag, breaks, spacing, punctuation.
  - **Fix order:** concept → hierarchy → layout → type → colour → polish.

### 9.2 Rubric for a vision model (0–5 per criterion + hard gates)

**How to run it:**
1. The pipeline supplies the final PNG at 100%, a phone-scale render (360 px wide; 168 px for thumbnails), a grayscale render and a blurred render (Puppeteer `emulateVisionDeficiency('achromatopsia' | 'blurredVision')` [72]).
2. It also supplies the brief and the brand kit.
3. It supplies **programmatic measurements**: contrast per text box (worst-pixel method), rendered font sizes, safe-zone and overflow checks, fonts-loaded status, detected fallback fonts.
4. The model checks the gates first, then scores.

**Hard gates. Any "yes" = FAIL, whatever the scores.**

| Gate | FAIL if … | Check type |
|---|---|---|
| G1 Text accuracy | Any misspelling, wrong name, date, price, number or URL vs the brief; placeholder text ("Lorem ipsum", "Your text here"); an unintended language | Vision + string diff vs brief |
| G2 Script rendering | Tofu boxes; broken or detached Bengali/Devanagari conjuncts or matras; disconnected or LTR-reversed Arabic; mixed digit scripts; fake-bold or fake-italic on scripts | Vision + font-fallback detection |
| G3 Legibility | Any *required* text below 4.5:1 (small) or 3:1 (large, judged at rendered size); rendered size below the floor (≈ 11 pt at display scale; thumbnail caps < 13 px at 168 px wide) | Programmatic |
| G4 Clipping, overflow, collision | Text cut off, overlapping unintentionally, colliding lines; key content outside safe zones (story top/bottom, Reels right rail, 3:4 grid crop, YouTube timestamp) | Programmatic + vision |
| G5 Format | Wrong pixel dimensions or aspect ratio; print without bleed or with text inside the trim margin; wrong colour mode where specified | Programmatic |
| G6 Brand violation | Logo stretched, rotated, recoloured, effected, too small, or crowding its clear space; off-palette key colours or off-brand fonts when a kit exists | Vision + kit diff |
| G7 AI-image artifacts | Any Kellogg-category artifact (§5.2): hands, teeth, eyes, melted objects, impossible physics, fake text or watermarks/signatures in the imagery | Vision (zoom 200%) |
| G8 Rights and ethics | Unlicensed third-party logos or trademarks, real identifiable people not supplied or cleared, stock watermarks, misleading claims, culturally offensive content | Vision + brief |
| G9 Missing essentials | The brief's required elements absent (CTA, logo, date / time / venue, disclaimer, handle) | Checklist vs brief |
| G10 Technical quality | Visible pixelation, JPEG blocking, banding, blur on the key subject, halo edges on cut-outs at 100% | Vision |

**Scored criteria (0–5).** Anchors:
- **0** = absent or broken
- **1** = amateur
- **2** = below professional
- **3** = competent professional (acceptable)
- **4** = strong senior work
- **5** = exceptional, portfolio or award level

| # | Criterion (weight) | What a 5 looks like | What a 2 looks like | Evidence to check |
|---|---|---|---|---|
| C1 | **Message and brief fit** (15%) | Single clear message understood in ≤ 2 s; right audience tone; a CTA where needed | Message diluted; tone off; CTA buried | 5-second test; brief |
| C2 | **Hierarchy and focal point** (15%) | Unmistakable entry point; 2–3 levels; blurred and grayscale renders keep the order | Competing elements; 4+ sizes; flat emphasis | Blur and grayscale renders |
| C3 | **Typography craft** (15%) | Purposeful faces; correct leading and tracking per size and script; balanced breaks; real punctuation; optical alignment | Default fonts by reflex; cramped or loose leading; runts; tracked Bengali | §1, §5.3 checklist |
| C4 | **Layout and composition** (10%) | Clear grid, consistent margins and 8-px spacing, intentional asymmetric balance, strong use of white space | Centred-everything; uneven gaps; edge-hugging; clutter | Overlay the grid; measure gaps |
| C5 | **Colour and contrast** (10%) | Disciplined palette (dominant + accent), harmonious with the imagery; contrast comfortably above the thresholds; designed gradients | Rainbow or default gradients; muddy mixes; marginal contrast | Palette extraction; contrast data |
| C6 | **Imagery and integration** (10%) | Credible, specific imagery; consistent light and grade; type and image interlock (copy space, depth, framing) | Stock-cliché or plastic AI look; type floating on a busy photo | §3.4, §5.2 |
| C7 | **Brand consistency** (10%) | Every kit rule honoured; recognisable without the logo | Brand elements present but misapplied | Kit diff |
| C8 | **Originality / non-template feel** (5%) | A specific idea; passes the swap-the-logo test; zero AI tells | Several tells from §5.1 | §5.1 table |
| C9 | **Finish and polish** (5%) | Pixel-level care: radii, strokes, alignment, kerning, no near-misses | Visible sloppiness | Zoomed inspection |
| C10 | **Format and platform fitness** (5%) | Legible at display scale; crop-safe; series-consistent; export spec met | Readable only at 100%; UI overlaps | Phone and thumbnail renders |

**Verdict logic [Opinion]:**
- **FAIL:** any gate hit, OR any criterion ≤ 1.
- **REVISE:** weighted score < 3.5, OR any criterion = 2, OR C1/C2/C3 < 3.
- **PASS (client-ready):** weighted ≥ 3.5, and every criterion ≥ 3.
- **PASS-SENIOR (target):** weighted ≥ 4.2, and C1–C3 ≥ 4.

**Output format for the model:**
- gate results (Y/N with evidence)
- the 10 scores with one-line evidence each
- a **prioritised fix list, max 5 items, in fix order**: concept → hierarchy → layout → type → colour → polish
- each fix phrased as a concrete edit, e.g. "reduce the subhead from 64 to 48 px", "move the CTA to the bottom-left column 1–4", "raise the scrim to 45% at the bottom 40%"

---

## 10. Recommendations for our skill

### 10.1 Numeric rules (drop-in defaults; see the sections above for sources and tags)

This block is compact pseudo-YAML: `;` separates keys on one line. Expand it into real YAML or JSON before parsing.

```yaml
display_scale:            # rendered = canvas_px * scale
  social_1080_phone: [0.333, 0.407]      # 360–440 px wide feeds
  youtube_1280:      [0.131, 0.336]      # 168 px sidebar … 430 px mobile feed
min_rendered_text_pt: {legal: 11, body: 12, comfortable: 16}   # Apple HIG min 11 / default 17
canvas_type_px:           # 1080-wide canvases (post 1:1, 4:5, 3:4; story 9:16)
  hero: [180, 300]; headline: [72, 160]; subhead: [44, 64]; body: [36, 48]; fine_print_min: 32; eyebrow_caps: [26, 32]
thumbnail_1280x720:
  cap_height_px_min: 100; cap_height_px_ideal: [120, 180]; max_words: 5; weights: [700, 900]; render_scale: 3   # → 3840×2160
print_300dpi:
  pt_to_px: 4.1667; mm_to_px: 11.811; bleed_mm: 3; safe_inside_trim_mm: [3, 5]
  a4_body_pt: [9, 11]; a5_body_pt: [8.5, 10]; caption_pt: [7, 8]; legal_min_pt: 6.5
  a4_headline_pt: [28, 72]; a4_margins_mm: {outer: [15, 20], top: [12, 15]}
poster: {cap_height_per_distance: "25 mm per 3 m (1 in per 10 ft) for impact", A3_body_pt: [12, 14], A2_body_pt: [14, 16], A1_body_pt: [18, 24]}
scale_ratio_by_format: {print_dense: [1.2, 1.25], carousel_infographic: 1.333, post_ad: [1.5, 1.618], thumbnail_poster: [1.618, 2.0]}
hierarchy: {max_sizes: 3, max_families: 2, weights_per_family: [2, 3], headline_to_body_min_ratio_social: 2.0}
line_height:
  latin: {body: [1.3, 1.5], support_social: [1.25, 1.4], subhead: [1.1, 1.25], display: [0.95, 1.1], caps_display: [0.85, 1.0]}
  bengali_devanagari: {body: [1.5, 1.8], display_min: "ink_span*size_adjust+0.05 (≈1.25–1.5)"}
  arabic: {body: [1.6, 2.0], display_min: "ink_span*size_adjust+0.05 (≈1.3–1.7)"}
  cjk: {body: [1.7, 1.9], display: [1.2, 1.4]}
  never: "line-height: normal"
tracking_em:
  body: 0; latin_display_ge_80px: [-0.03, -0.01]; latin_caps: [0.05, 0.12]; tiny_text_lt_12pt_rendered: [0.01, 0.02]
  inter_formula: "-0.0223 + 0.185*exp(-0.1745*px)"
  bengali_arabic_devanagari: 0      # hard rule
  cjk: [0, 0.05]
measure_chars: {print_body: [45, 75], social_paragraph: [25, 45], headline_line: [8, 20], japanese: [15, 35]}
wrapping: {headline: "text-wrap: balance", paragraph: "text-wrap: pretty", hyphenate_display: false, no_runts: true}
script_size_targets:
  indic_headline_over_latin_xheight: 1.26   # IQR 1.20–1.30 (n=35)
  arabic_alef_over_latin_cap: 1.05          # IQR 1.00–1.09 (n=24)
grid:
  spacing_scale_px: [4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
  social_margin_pct_of_width: [6, 9]; social_gutter_px: [24, 32]
  group_gap_over_inner_gap_min: 2.0
  whitespace_share: {premium_editorial: ">=0.40", information: [0.25, 0.35]}
safe_zones:
  story_1080x1920: {top_px: 250, bottom_px: 340, text_band_y: [250, 1500]}      # Verify with Meta
  reels_tiktok: {right_px: [120, 160], bottom_pct: [20, 25]}                     # Verify
  ig_4x5_grid_crop_side_px: 34
  youtube: {keep_clear_bottom_right_px: [200, 70]}
contrast:
  wcag: {text: 4.5, large_text: 3.0, non_text: 3.0, measure_on: "p95 luminance under text (light text) / p5 (dark text)"}
  apca_optional: {body: 75, body_preferred: 90, non_body: 60, headline: 45, any_text: 30}
scrim:
  dark_alpha: [0.20, 0.40]; light_alpha: [0.40, 0.60]; midpoint_toward_dark: 0.3; length_pct_of_canvas: [40, 60]; easing: "Larsen 13-stop"
colour:
  rule_60_30_10: true; max_saturated_hues: 3; accent_area_max_pct: 10
  ramp_oklch_L: [0.97, 0.93, 0.87, 0.78, 0.68, 0.58, 0.48, 0.39, 0.30, 0.22]
  neutral_chroma: [0.005, 0.02]; near_black_L: [0.16, 0.22]
  gradient: {interpolation: "oklch", max_stops: 3, max_hue_span_deg: 60, grain_pct: [1, 3]}
  cvd_min_deltaL_between_categories: [0.15, 0.20]
effects: {max_per_element: 1, max_types_per_piece: 2, shadow: {opacity: [0.08, 0.20], blur_over_offset_min: 2}}
logo: {favicon_px: 16, wordmark_min_cap_px: 24, clear_space: "derived unit (e.g. 0.5×symbol height)", mono_version_required: true}
qa_renders: ["100%", "phone 360w", "thumb 168w (YT)", "achromatopsia", "blurredVision", "deuteranopia"]
```

### 10.2 Pairing table the skill should ship (compact)

Bengali `size-adjust` values are [Measured] against the **primary text face** named in that row. The target is headline = 1.26 × that face's x-height.

| Mood | Primary pick (display / text) | Alternate | Bengali companion → size-adjust vs the primary text face |
|---|---|---|---|
| Corporate | Hanken Grotesk 700 / Source Serif 4 400 | IBM Plex Sans 600/400 (+ Plex Serif) | Noto Sans Bengali 100% · Hind Siliguri 97% |
| Tech | Bricolage Grotesque 800 / Figtree 400 (+ JetBrains Mono) | Mona Sans 800 / 400 | Anek Bangla 101% · Noto Sans Bengali 101% |
| Luxury | Bodoni Moda 500 (opsz) / Jost 400 | Playfair (2023) / Albert Sans | Tiro Bangla 93% (400 only) · Noto Serif Bengali 93% |
| Editorial | Newsreader 600 / Newsreader 400 (+ Libre Franklin labels) | Fraunces 600 / Source Serif 4 | Noto Serif Bengali 89% · Tiro Bangla 90% |
| Playful | Fredoka 600 / Nunito 400 | Baloo 2 800 / Nunito Sans | **Baloo Da 2** 100% · Atma 100% |
| Bold / sport | Big Shoulders 800 / Barlow 500 | Archivo (wdth) 800 / 400 | Anek Bangla (condensed widths, 700–800) 102% |
| Organic | Fraunces (SOFT 100) 500 / Karla 400 | Young Serif / Work Sans | Noto Serif Bengali 97% · Tiro Bangla 97% |
| Medical | Atkinson Hyperlegible Next 700 / 400 | Lexend 600/400 | Noto Sans Bengali 100% · Hind Siliguri 97% (check the ১ digit) |
| Food | Shrikhand / Work Sans | DM Serif Display / DM Sans | Galada 94% (display only) + Hind Siliguri 98% or Baloo Da 2 102% for text |
| (Reference) Inter-class text face | – | – | Noto Sans Bengali 111% vs Inter / Inter Tight: Inter-class faces have a large x-height (0.546 em) |
| Arabic markets | IBM Plex Sans + Plex Sans Arabic (99%) | Readex Pro + Lexend (99%); Noto Naskh + Source Serif 4 (105%) | – |
| Hindi markets | Hind / Mukta (co-designed) | Tiro Devanagari Hindi + Source Serif 4 (100%) | – |
| Japanese | Zen Kaku Gothic New + Inter Tight (Latin first) | Shippori Mincho + EB Garamond | – |

**Global rules for the table:**
- `font-synthesis: none` everywhere.
- No tracking on Bengali, Arabic or Devanagari runs.
- Tag `lang` on every run.
- Treat Inter, Roboto, Montserrat and Poppins as last-resort text faces, never as the display voice [Opinion].

### 10.3 Rubric

Use §9.2 verbatim:
- 10 hard gates → FAIL.
- 10 weighted criteria at 0–5.
- PASS ≥ 3.5 with every criterion ≥ 3; senior target ≥ 4.2 with C1–C3 ≥ 4.
- Always emit ≤ 5 concrete fixes in the order concept → hierarchy → layout → type → colour → polish.
- Automate G1 (string diff), G3 (contrast and size), G4 (overflow and safe zones), G5 (dimensions) and the G2 fallback-font detection in the renderer. The vision model then judges only what needs eyes.

### 10.4 Anti-AI / anti-template checklist (run before every export)

1. **Palette:** no indigo→purple / blue→pink default gradient; ≤ 1 accent; gradients in OKLCH with grain; no neon-glow-on-black unless the brand is literally that.
2. **Type:** not Inter, Roboto, Poppins, Montserrat or Space Grotesk as the display voice; optical sizes on; purposeful weight contrast; 3 sizes max.
3. **Composition:** not centre-stacked (logo / headline / sub / button); a focal point on a third; asymmetric balance; a real grid; white space ≥ the targets.
4. **Decoration:** zero sparkles, lens flares, random blobs, orbs or squiggles; ≤ 1 effect per element; no default drop shadows; ≤ 1 glass panel with heavy blur.
5. **Icons:** one family, one stroke, one radius; no 3D or clay emoji icons unless that is the brand's own style.
6. **Emoji:** none on the canvas.
7. **Imagery:** specific and local to the client's market; natural light and grade; no stock clichés; §5.2 artifact checklist passed at 200%; **no generated text anywhere in the image**.
8. **Copy:** a concrete claim or number; no "elevate / unlock / seamless / next-level" filler; proofread against the brief.
9. **Series:** a consistent system (grid, type styles, colour roles, motif, logo position, page numbers).
10. **Human signal (optional, trend-durable):** one deliberate imperfection or crafted element that isn't template-able, such as hand-drawn annotation, scanned texture, custom lettering, a real photograph of a real place or product, or a local cultural reference done respectfully.
11. **The swap test:** if the client's logo could be swapped for a competitor's without the design feeling wrong, it isn't done.

---

## Appendix A — Measured font metrics (method and data) [Measured]

**Method:**
1. Downloaded each family's Regular (400) TTF through the Google Fonts CSS API (curl user-agent → TTF), 2026-09-23.
2. Measured with HarfBuzz `hb-shape --show-extents` (glyph bounding boxes after shaping) and `hb-info --get-metric` (hhea / OS/2).
3. Latin: x-height = top of "x"; cap = top of "H"; ascender and descender maxima from "dhlkÁÉ" / "gjpqy".
4. Indic:
   - headline = top of ক / क
   - mark top = max over কি কী র্ক কৈ কৌ (Devanagari: कि की र्क कैं के)
   - mark bottom = min over কু কূ কৃ ক্র ঙ্গ ক্ত (Devanagari: कु कू कृ क्र ट्र ङ्ग)
5. Arabic: alef top; "seen" tooth top; extremes over آ لأ ك ط / ج ع ي إ ق ں.
6. **Ink span** = (highest mark − lowest mark) / em. Recommended display line-height ≥ ink span + 0.05, multiplied by any `size-adjust`.

**Limits:**
- Only a sample of glyph combinations was measured; rarer stacks (e.g. reph + candrabindu + long vowel) can go further.
- Weight 400 only; bold weights usually extend slightly.
- The results are design heuristics, not a validation of rendering.

**Bengali** (headline ÷ own Latin x-height; ink span; built-in "normal" line-height):
- Hind Siliguri 1.26 / 1.18 / 1.62
- Noto Sans Bengali 1.16 / 1.19 / 1.32
- Noto Serif Bengali 1.16 / 1.18 / 1.59
- Anek Bangla 1.28 / 1.28 / 1.87
- Baloo Da 2 1.32 / 1.29 / 1.68
- Tiro Bangla 1.30 / 1.18 / 1.33
- Galada 1.20 / 1.39 / 1.63
- Mina 1.20 / 1.24 / 1.59
- Atma 1.13 / 1.27 / 1.62
- Alkatra 1.23 / 1.30 / 1.68
- Google Sans 1.29 / 1.29 / 1.25 (Windows metrics 2.40)

**Devanagari** (same columns):
- Poppins 1.35 / 1.35 / 1.50
- Hind 1.26 / 1.18 / 1.60
- Mukta 1.34 / 1.18 / 1.66
- Noto Sans Devanagari 1.16 / 1.17 / 1.30
- Tiro Devanagari Hindi 1.30 / 1.25 / 1.33
- Anek Devanagari 1.30 / 1.23 / 1.71
- Baloo 2 1.30 / 1.20 / 1.60
- Martel 1.18 / 1.43 / 1.69
- Eczar 1.30 / 1.34 / 1.78
- Yatra One 1.29 / 1.27 / 1.48
- Rozha One 1.22 / 1.06 / 1.42
- Teko 1.28 / 1.05 / 1.43
- Rajdhani 1.22 / 1.15 / 1.28
- Kalam 1.26 / 1.34 / 1.59
- Khand 1.14 / 1.11 / 1.53
- Yantramanav 1.31 / 1.14 / 1.30
- Palanquin 1.40 / 1.33 / 1.81
- Biryani 1.17 / 1.30 / 1.76
- Laila 1.26 / 1.21 / 1.55
- Sarala 1.28 / 1.22 / 1.63
- Karma 1.24 / 1.18 / 1.45
- Halant 1.34 / 1.31 / 1.57
- Akshar 1.26 / 1.25 / 1.38

**Pooled Indic results:** headline/x median 1.26 (IQR 1.20–1.30, range 1.13–1.40); headline/cap median 0.93 (IQR 0.87–0.99); ink span median 1.23 (range 1.05–1.43).

**Arabic** (alef ÷ own Latin cap; ink span; built-in line-height):
- Cairo 1.04 / 1.30 / 1.87
- Tajawal 1.02 / 1.15 / 1.20
- Almarai 1.00 / 1.27 / 1.12
- IBM Plex Sans Arabic 1.06 / 1.30 / 1.50
- Readex Pro 1.06 / 1.41 / 1.25
- Noto Naskh Arabic 0.94 / 1.25 / 1.70
- Noto Sans Arabic 1.00 / 1.27 / 2.11
- Noto Kufi Arabic 1.06 / 1.37 / 1.90
- Amiri 1.11 / 1.53 / 1.76
- Alexandria 1.17 / 1.42 / 1.22
- Vazirmatn 0.95 / 1.34 / 1.56
- Markazi Text 1.06 / 1.02 / 1.20 (whole font small on the body: Latin x = 0.364 em)
- El Messiri 1.00 / 1.21 / 1.56
- Reem Kufi 1.10 / 1.38 / 1.50
- Rubik 1.07 / 1.17 / 1.19
- Changa 1.01 / 1.36 / 1.84
- Fustat 1.08 / 1.24 / 1.42
- Zain 1.00 / 1.34 / 1.66
- Beiruti 1.04 / 1.10 / 1.20
- Lalezar 0.99 / 1.20 / 1.57
- Baloo Bhaijaan 2 1.10 / 1.23 / 1.71
- Lateef 1.16 / 1.04 / 1.45
- Scheherazade New 1.17 / 1.62 / 2.04
- Mada 0.95 / 1.06 / 1.30

**Pooled Arabic results:** alef/cap median 1.05 (IQR 1.00–1.09); ink span median 1.27 (range 1.02–1.62).

**Latin x-height / cap height (em):**
- Anton .733/.859
- Bebas Neue .700/.700
- Oswald .578/.810
- Unbounded .566/.750
- Poppins .548/.697
- Inter .546/.728
- Manrope .540/.720
- Plus Jakarta Sans .536/.745
- Noto Sans .536/.714
- Geist .530/.710
- Roboto .528/.711
- Montserrat .525/.700
- Bricolage Grotesque .517/.660
- IBM Plex Sans .516/.698
- Playfair Display .515/.708
- Instrument Serif .510/.720
- DM Sans .504/.700
- Work Sans .500/.660
- Figtree .500/.700
- Lora .500/.700
- Source Serif 4 .492/.670
- Space Grotesk .489/.700
- Anek Latin .488/.639
- DM Serif Display .481/.660
- Outfit .475/.694
- Mukta .470/.630
- Fraunces .469/.700
- Baloo 2 .469/.613
- Spectral .450/.660
- Newsreader .441/.676
- EB Garamond .405/.653
- Cormorant Garamond .386/.625

Built-in "normal" line-heights range from 1.00 (Newsreader) to 1.66 (Mukta) across these Latin families.

---

## Appendix B — Sources (URL · date · note)

1. Butterick, *Practical Typography*, "Summary of key rules" — https://practicaltypography.com/summary-of-key-rules.html (web book, undated; accessed 2026-09-23)
2. Butterick, "All caps" — https://practicaltypography.com/all-caps.html (accessed 2026-09-23)
3. Butterick, "Letterspacing" — https://practicaltypography.com/letterspacing.html (via search summary, 2026-09-23)
4. Butterick, "Line spacing" — https://practicaltypography.com/line-spacing.html (accessed 2026-09-23)
5. Butterick, "Mixing fonts" — https://practicaltypography.com/mixing-fonts.html (accessed 2026-09-23)
6. Butterick, "Centered text" — https://practicaltypography.com/centered-text.html (accessed 2026-09-23)
7. Bringhurst, *The Elements of Typographic Style* §2.1.2, via webtypography.net — http://webtypography.net/2.1.2 (book 1992/2004)
8. Rasmus Andersson, Inter "Dynamic Metrics" — https://d.rsms.me/inter-website/v3/dynmetrics/ (Inter v3 docs, undated)
9. Tim Brown, "More Meaningful Typography", *A List Apart* — https://alistapart.com/article/more-meaningful-typography/ (2011-05-03)
10. Cieden, "Different type scale types" — https://cieden.com/book/sub-atomic/typography/different-type-scale-types (undated; ratio names)
11. Apple Human Interface Guidelines, Typography — https://developer.apple.com/design/human-interface-guidelines/typography (accessed 2026-09-23; iOS default 17 pt, minimum 11 pt; avoid light weights)
12. NN/g, Kelley Gordon, "5 Principles of Visual Design in UX" — https://www.nngroup.com/articles/principles-visual-design/ (2020-03-01)
13. NN/g, Aurora Harley, "Ensure High Contrast for Text Over Images" — https://www.nngroup.com/articles/text-over-images/ (2015-10-18; reviewed 2026-01-13)
14. Smashing Magazine, Hannah Milan, "Designing Accessible Text Over Images (Part 1)" — https://www.smashingmagazine.com/2023/08/designing-accessible-text-over-images-part1/ (2023-08-04)
15. Material Design 1, "Imagery" (text protection / scrims) — https://m1.material.io/style/imagery.html ; mirror https://www.mdui.org/en/design/1/style/imagery.html (c. 2014–2016)
16. Andreas Larsen, "Easing Linear Gradients", CSS-Tricks — https://css-tricks.com/easing-linear-gradients/ (2017-05-08)
17. Chrome for Developers, "CSS text-wrap: balance" — https://developer.chrome.com/docs/css-ui/css-text-wrap-balance (updated 2023-12-19)
18. Chrome for Developers, "CSS text-wrap: pretty" — https://developer.chrome.com/blog/css-text-wrap-pretty (2023-10-23)
19. Hanging punctuation support — https://caniuse.com/css-hanging-punctuation ; Chris Coyier — https://chriscoyier.net/2023/11/27/the-hanging-punctuation-property-in-css/ (2023-11-27)
20. Chrome for Developers, "CSS text-box-trim" — https://developer.chrome.com/blog/css-text-box-trim (2025-01-14; Chrome 133)
21. MDN, font-variant-numeric — https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric (accessed 2026-09-23)
22. MDN, font-size-adjust — https://developer.mozilla.org/en-US/docs/Web/CSS/font-size-adjust (Baseline 2024)
23. MDN, @font-face size-adjust — https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/size-adjust (Baseline since 2023-09)
24. MDN, font-synthesis — https://developer.mozilla.org/en-US/docs/Web/CSS/font-synthesis (accessed 2026-09-23)
25. W3C i18n on letter-spacing and Indic/Arabic scripts — https://github.com/w3c/iip/issues/119 ; https://www.w3.org/TR/deva-gap/ ; https://www.w3.org/International/track/issues/354 (via search summaries, 2026-09-23)
26. Google Fonts metadata API — https://fonts.google.com/metadata/fonts (pulled 2026-09-23; 1,946 families)
27. google/fonts DESCRIPTION files — https://github.com/google/fonts/tree/main/ofl (e.g. ofl/hindsiliguri/DESCRIPTION.en_us.html; accessed 2026-09-23)
28. google/fonts issue #6037, "malformed glyph in Hind Siliguri" — https://github.com/google/fonts/issues/6037 ; fork https://github.com/bdeshi/Hind-Siliguri
29. Alphabettes, Aasawari Kulkarni, "Devanagari Typography 101: a guide for typesetting with Latin" — https://www.alphabettes.org/devanagari-typography-101-a-guide-for-typesetting-with-latin/ (page date shown 2026-03-31)
30. Google Design, "Design for Many — Anek" — https://design.google/library/anek-multiscript (undated)
31. CreativePro / InDesign Magazine #92, "InPerson Interview: Nadine Chahine" — https://creativepro.com/inperson-interview-nadine-chahine/ (c. 2016-12)
32. Gaëlle Lamirault (GLDS), "Arabic Typography Best Practices" — https://gaellelamirault.com/blog/arabic-typography-best-practices (2026-05)
33. W3C, Arabic & Persian Layout Requirements — https://www.w3.org/TR/alreq/
34. AQ, Eiko Nagase, "Seven rules for perfect Japanese typography" — https://www.aqworks.com/blog/perfect-japanese-typography (undated)
35. Chrome for Developers, "Introducing four new international features in CSS" — https://developer.chrome.com/blog/css-i18n-features (2023-12-04); text-spacing-trim shipped Chrome 123 (2024-03) — https://chromestatus.com/feature/5170044014690304
36. Google Sans / Google Sans Flex open-sourced (OFL) — https://www.omgubuntu.co.uk/2025/11/google-sans-flex-font-ubuntu (2025-11); Google Fonts dateAdded 2025-12-09 [26]
37. Typewolf, "The 40 Best Google Fonts" — https://www.typewolf.com/google-fonts (updated 2026-01-12)
38. Google Fonts Knowledge, "Pairing typefaces" and "…within a family & superfamily" — https://fonts.google.com/knowledge/choosing_type/pairing_typefaces (via search summary; page is JS-rendered)
39. Anthropic, "Improving frontend design through Skills" — https://claude.com/blog/improving-frontend-design-through-skills (2025-11-12)
40. 925 Studios, "AI Slop Fonts and Gradients: The Tells That Give Away AI Design" — https://www.925studios.co/blog/ai-slop-design-tells (page dated 2026-09-23)
41. Venngage, Manish Nepal, "Why your AI-generated graphic designs look like slop" — https://venngage.com/blog/ai-slop-in-design/ (updated 2026-08-12)
42. Kellogg Insight, "5 Telltale Signs That a Photo Is AI-generated" — https://insight.kellogg.northwestern.edu/article/ai-photos-identification (2024-09-09); paper: Kamali, Nakamura, Chatzimparmpas, Hullman, Groh, arXiv 2406.08651
43. NN/g, Megan Brown, "Glassmorphism: Definition and Best Practices" — https://www.nngroup.com/articles/glassmorphism/ (2024-06-07)
44. Apple Newsroom, new software design (Liquid Glass) — https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ (2025-06-09)
45. Canva Design Trends 2026 — Campaign Brief Asia https://campaignbriefasia.com/2025/12/15/canvas-2026-design-trends-report-highlights-shift-toward-imperfect-by-design/ (2025-12-15); Business Wire release (2025-12-10) https://www.businesswire.com/news/home/20251210696597/en
46. Canva Design Trends 2025 — https://www.canva.com/newsroom/news/design-trends-2025/ (Nov 2024; names via search summaries, the page returned 403); Fast Company https://www.fastcompany.com/91232583/canva-trend-report-2025
47. Adobe Express, "Top 10 graphic design trends for 2026" — https://www.adobe.com/express/learn/blog/design-trends-2026 (2025-12-12); Adobe Blog, "Four creative trends that will define marketing in 2026" — https://blog.adobe.com/en/publish/2025/12/09/four-creative-trends-define-marketing-2026 (2025-12-09)
48. Pinterest Newsroom, "Pinterest Predicts 2026" — https://newsroom.pinterest.com/news/pinterest-predicts-nonconformity-self-preservation-and-escapism-drive-21-trends-for-2026/ (2025-12-09)
49. Pinterest Newsroom, "2025 Pinterest Palette" — https://newsroom.pinterest.com/news/from-butter-yellow-to-cherry-red-meet-the-2025-pinterest-palette/ (2025-01-16)
50. Pantone, COTY 2026 Cloud Dancer 11-4201 — https://www.pantone.com/articles/press-releases/pantone-announces-color-of-the-year-2026-cloud-dancer (2025-12-04); COTY 2025 Mocha Mousse 17-1230 — https://www.pantone.com/color-of-the-year/2025
51. Figma Resource Library, "Top Web Design Trends for 2026" — https://www.figma.com/resource-library/web-design-trends/ (undated)
52. Kittl, "10 graphic design trends 2026" — https://www.kittl.com/blogs/graphic-design-trends-2026/ (2026-06-30)
53. Fontfabric, "10 Design & Typography Trends for 2026" — https://www.fontfabric.com/blog/10-design-trends-shaping-the-visual-typographic-landscape-in-2026/ (2025-12-09; updated 2026-08-13)
54. It's Nice That, Ellis Tree, "The graphic trends you'll want to bookmark for 2026" — https://www.itsnicethat.com/features/forward-thinking-graphic-trends-2026-graphic-design-120126 (2026-01-12)
55. Shutterstock, Creative Impact Report news release — https://investor.shutterstock.com/news-releases/news-release-details/creative-impact-crisis-new-data-shows-why-consumer-connection (2025)
56. Paul Rand, "Logos, Flags, and Escutcheons" — https://www.paulrand.design/writing/articles/1991-logos-flags-and-escutcheons.html (AIGA 1991)
57. Chermayeff & Geismar & Haviv, *Identify* (2011); PRINT interview — https://www.printmag.com/branding-identity-design/marks-men-an-interview-with-ivan-chermayeff-tom-geismar-and-sagi-haviv-of-chermayeff-geisma/ (via search summaries)
58. David Airey, *Logo Design Love* (2nd ed. 2014; 3rd ed.) — https://www.logodesignlove.com/book (chapter list via search summary)
59. Spotify for Developers, Design & Branding Guidelines — https://developer.spotify.com/documentation/design (accessed 2026-09-23)
60. US Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* — https://copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf (2025-01-29)
61. Frontify, "Brand Guidelines: What They Are & How to Create Them" — https://www.frontify.com/en/guide/brand-guidelines (updated 2026-09-04)
62. W3C Design Tokens CG, "Design Tokens specification reaches first stable version" — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ (2025-10-28); Format Module 2025.10 — https://www.designtokens.org/tr/drafts/format/
63. NN/g, Sarah Gibbons, "Design Critiques: Encourage a Positive Culture to Improve Products" — https://www.nngroup.com/articles/design-critiques/ (2016-10-23)
64. UIE Brainsparks, Adam Connor & Aaron Irizarry, "Discussing Design: The Art of Critique" — https://archive.uie.com/brainsparks/2012/07/13/adam-connor-aaron-irizarry-discussing-design-the-art-of-critique/ (2012-07-13); book *Discussing Design* (O'Reilly, 2015)
65. W3C, Understanding SC 1.4.3 Contrast (Minimum) — https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html
66. APCA, "Easy Intro" — https://git.apcacontrast.com/documentation/APCAeasyIntro.html (2022)
67. Refactoring UI (Wathan & Schoger), "Building Your Color Palette" — https://refactoringui.com/previews/building-your-color-palette (undated)
68. 60-30-10 rule (interior-design origin), e.g. Behr — https://www.behr.com/colorfullybehr/tried-and-true-color-combinations/ (via search summary)
69. Chrome for Developers, Adam Argyle, "High definition CSS color guide" — https://developer.chrome.com/docs/css-ui/high-definition-css-color-guide (via search summary; banding/noise note from secondary guides such as https://www.toolbox365.net/tutorials/gradient-banding-and-oklch/)
70. Wikipedia, "Color psychology" — https://en.wikipedia.org/wiki/Color_psychology (accessed 2026-09-23)
71. Colour-vision-deficiency prevalence (NEI figure), via SUNY College of Optometry — https://www.sunyopt.edu/what-it-means-to-be-color-blind-and-what-you-can-do-about-it/ (via search summary)
72. Chrome, "Simulating color vision deficiencies in the Blink Renderer" — https://developer.chrome.com/docs/chromium/cvd ; Puppeteer `page.emulateVisionDeficiency` (via search summary)
73. Wikipedia, "Duotone" — https://en.wikipedia.org/wiki/Duotone (accessed 2026-09-23)
74. NN/g, Kara Pernice, "F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant" — https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/ (2017-11-12)
75. Smashing Magazine, Steven Bradley, "Design Principles: Visual Weight and Direction" — https://www.smashingmagazine.com/2014/12/design-principles-visual-weight-direction/ (2014-12-12)
76. NN/g, Aurora Harley, "The Principle of Proximity in Visual Design" — https://www.nngroup.com/articles/gestalt-proximity/ (2020-08-02)
77. Wikipedia, "Rule of thirds" — https://en.wikipedia.org/wiki/Rule_of_thirds ; "Grid (graphic design)" — https://en.wikipedia.org/wiki/Grid_(graphic_design) (accessed 2026-09-23)
78. Instagram 3:4 grid (2025-01) and 3:4 uploads (2025-05-28) — Neal Schaffer https://nealschaffer.com/instagram-post-size/ (2026); Exchange4media https://www.exchange4media.com/digital-news/instagram-introduces-34-aspect-ratio-for-photo-uploads-143973.html ; Slashdot https://tech.slashdot.org/story/25/05/30/2146239/instagram-isnt-just-for-square-photos-anymore (2025-05-30)
79. Hootsuite, Instagram carousel guide — https://blog.hootsuite.com/instagram-carousel/ (2025-12-03)
80. Meta Stories safe zones (secondary) — https://www.outfy.com/blog/instagram-safe-zone/ (2026); https://www.thebrief.ai/blog/meta-ad-specs/ (2026). **Verify against the Meta Ads Guide**
81. TikTok safe zones (secondary) — https://kreatli.com/guides/tiktok-safe-zone ; https://rightblogger.com/blog/tiktok-safe-zone-template (2026). **Verify**
82. YouTube Help, "Add video thumbnails" — https://support.google.com/youtube/answer/72431 (accessed 2026-09-23)
83. Signs.com, "Signage 101 — Letter Height Visibility" — https://www.signs.com/blog/signage-101-letter-height-visibility/ (USSC-derived rule; via search summary)
84. University of York, "Posters: Text" — https://subjectguides.york.ac.uk/posters/text ; Printed.com poster sizes — https://www.printed.com/blog/poster-sizes/ (via search summaries)
85. Wikipedia, "Bleed (printing)" — https://en.wikipedia.org/wiki/Bleed_(printing) (accessed 2026-09-23)
86. Logo mistakes — Looka https://looka.com/blog/logo-mistakes/ ; Column Five https://www.columnfivemedia.com/7-huge-logo-design-mistakes-to-avoid-at-all-costs/ ; Kittl https://www.kittl.com/blogs/what-are-common-mistakes-in-logo-design-dsi/ (via search summaries)
87. NN/g, UX design critiques cheat sheet (PDF) — https://media.nngroup.com/media/articles/attachments/NNg_UXCritiqueCheatsheet.pdf
88. This research: HarfBuzz measurements on Google Fonts TTFs, 2026-09-23 (Appendix A). Raw data kept at `scratchpad/tmp-r4/metrics.json`
89. Pinterest Predicts 2025 — https://www.webdesignerdepot.com/pinterest-predicts-design-trends-for-2025/ ; https://business.pinterest.com/en-ca/pinterest-predicts/2025/cherry-coded/ (via search summaries)

*End of notes.*
