# Deliverable playbooks

Each entry: preset ids (`design.py presets`), anatomy in order of prominence, copy budget, proven patterns, rules.
"(H)" marks practitioner heuristics; hard evidence is mostly about formats, not layouts. Starting HTML for most of
these is in `templates/patterns/` (see `templates/README.md`).

**Cross-cutting.** Body text on a 1080 canvas ≥ 36–40 px, headlines 72–160 px; ≤ ~25 words on a feed image (the
detail goes in the caption); one message and one CTA; the logo in the same corner, ≥ 64 px from the edges and inside
the safe zone; alt text for every export. Formats that perform: Instagram carousels 0.55 % engagement vs Reels
0.52 % vs single images 0.37 % (2025, 35 M posts); LinkedIn native documents 7.0 % (the top format). Faces with
complex, readable emotion beat neutral ones; more than three people hurts (Netflix artwork research).

## 1. Social posts by intent (ig-portrait / ig-3x4 / ig-square / fb-feed / li-square / li-landscape / x-post)

Patterns: `post-photo.html`, `post-type.html` (announce, event, hiring), `post-product.html`, `card.html` (quote, tip, stat).

| Intent | Anatomy | Budget | Patterns (H) | Rules |
|---|---|---|---|---|
| Announcement | news headline → visual anchor → kicker ("New") → one support line → brand | headline ≤ 8 words, support ≤ 15 | big-type poster (headline 110–140 px, flush left); photo + eased bottom scrim; split (image 55 % / panel 45 %); date stamp (220–300 px numeral) | date on time-bound news; the news in the first 125 caption characters |
| Promo / sale | offer → product → conditions (dates, "selected items", code) → CTA → brand → legal line | offer ≤ 4 words, conditions ≤ 12, code ≤ 10 chars | offer built from type overlapping the product; was/now (old price at 60 % size, struck); deadline ribbon; one-product-per-slide carousel | real end dates only; "up to" when discounts vary; was/now needs a real reference price + dates (EU: lowest price of the previous 30 days); never on marketplace images |
| Product launch | product hero (largest) → name → one-line benefit → ≤ 3 features → availability → CTA | name ≤ 4 words, benefit ≤ 10, feature ≤ 5 | hero on a seamless ground (product 55–70 % of the frame); launch carousel (teaser → hero → features → proof → CTA); exploded callouts | real product pixels (cut-out), no "best/#1/clinically proven" without a source |
| Event | name → date + time (+ timezone) → place → headliners → price/"Free" → CTA/short URL or QR | title ≤ 6 words, info block 4 lines | info-block poster (oversized date); speaker grid (≤ 3 faces per slide); countdown series (same template, the number changes) | unambiguous dates ("Sat 11 Oct 2026"); year on cross-year events; no text over faces |
| Hiring | "We're hiring" → role title (dominant) → chips (place/remote, contract, **pay range**) → 2–3 perks → how to apply | title ≤ 6 words, ≤ 5 chips, ≤ 3 bullets × 8 words | role card (title 96–120 px + chips); team photo + overlay; carousel role → work → offer → apply; LinkedIn document | pay range where pay-transparency rules apply (EU); gender-neutral titles; real team photos only |
| Quote | quote (dominant) → attribution (name, role) → headshot (optional) → brand | quote ≤ 25–30 words, attribution ≤ 8 | a large quote glyph at 20 % behind a 56–72 px serif quote; headshot circle ≥ 240 px; photo + 60 % scrim; typographic | verify wording and source; permission for headshots; never invent people |
| Tip / educational | topic title → numbered tips → icons → save/share cue → series number | title ≤ 8 words, ≤ 5 tips × 12 words (one per slide in carousels) | numbered list (numbers 120 px in the accent); checklist; do/don't split (icons as well as colour); mini infographic | series frame fixed across posts |
| Testimonial (real only) | verbatim excerpt → name + role/company (consent) → photo or logo → rating only from a real source → source line ("Google review · May 2026") | excerpt ≤ 25 words | quote card + stars + source; result card with a real metric and timeframe; customer photo | never generate names, faces, quotes or ratings; mark paid/employee relationships |
| Behind the scenes | candid real photos → short label → light branding | ≤ 8 words | photo-dump carousel; process sequence; team spotlight; detail close-ups | real unretouched photos; never AI people as staff |
| Special day | greeting (typeset, audience's script) → one motif → one warm line → small logo | ≤ 10–20 words | typographic greeting on the brand colour; motif frame; photo + greeting | `occasions.md`; `render --occasion`; offers as a separate creative |
| Card series (info/quote/tip/stat) | fixed 12-col grid, 64–80 px margins, a type scale (36/48/72/110), series tag + number, logo corner, one accent per series | per card type | header band + body; centred statement; icon + statement; stat card (200 px number, label, source) | source + date on every stat; never change the grid between cards; export 4:5 and 1:1 when cross-posting |

## 2. Carousels (ig-carousel, ig-carousel-3x4, li-doc)

- Anatomy: **hook slide** (a promise or tension, ≤ 8 words, works inside the 3:4 grid crop) → one idea per body slide
  (≤ 30 words) → swipe cues (arrow or "1/7", an element that carries into slide 2) → final CTA slide (save, share,
  follow, comment; link in bio) → brand and series tag in the same place on every slide.
- 5–10 slides for education (H), up to 20 for photo dumps; the strongest idea on slide 1; every slide must also stand
  alone (carousels resurface in the feed on later slides).
- Patterns: listicle (hook → N tips → recap → CTA); story arc (problem → stakes → solution → proof → CTA); panorama
  chain; before/after pairs (not for health results); product range (organic only).
- **Chain (seamless):** one canvas N × 1080 by 1350 (or 1440); render `--slides N` (each slide is a crop of the one
  layout, so the seams match to the pixel). Rules (after ParthJadhav/app-store-screenshots, MIT):
  - how many things cross a cut: one by default for 5+ slides, at most two for 8–10, none is fine for formal decks.
    The slides belong together; they are not one poster chopped up;
  - a non-critical visual may overlap a cut by 10–30 % of its width; only backgrounds, paths and abstract lines (a
    horizon, a route, the brand's tide line) run further; the cut passes through negative space or a simple shape;
  - never across a cut: headlines, names, prices, legal text, ratings, CTAs, faces (no text within 40 px: checked);
    never centre a big object on a cut;
  - every slide passes a one-second test on its own; look at the strip zoomed out, then each slide, then at 160 px;
  - the headline in the top 30–40 %; no two neighbouring slides with the same layout; invert one or two for rhythm.
  Pattern: `carousel.html` (the tide line is the one element that crosses every cut).
- **LinkedIn document:** the same slides as a PDF (`--out deck.pdf --slides N`), one page size, page numbers, body
  ≥ 32 px; ≤ 100 MB / 300 pages.
- Plates: one anchor plate approved first, the others generated from the anchor (`ai-visuals.md`).

## 3. YouTube thumbnails (yt-thumbnail; export 3840×2160 with `--scale 3` when uploading from a computer)

Pattern: `thumbnail.html` (five text overlays).

- Anatomy: the subject (a face with a specific, readable emotion, or the object/result) at 35–60 % of the frame
  height → optional 2–4 words that complement (never repeat) the title → a background that separates the subject
  (contrast, rim light, outline) → a small series element.
- Keep clear: the bottom-right ~270×155 (duration badge) and, on rails, the top-left ~210×125 ("New" badge).
- Legibility: cap height ≥ 100 px on 1280×720; it must read at 200×113, 248×139 and 375×210 (and the 168×94 stress
  test): judge with `--kind thumbnail`; `design.py sheet` of downscaled copies.
- Patterns: face + reaction + object (face on the left 45 %, eyes on the upper third, object right, 2–3 words top
  right); before/after split (divider at x 640, an arrow across); big result number (200–260 px numerals + cut-out
  subject); single hero object (60 % of the frame on a saturated ground that contrasts with YouTube's white and dark
  UIs); a fixed series template.
- ≤ 3 people; honest promise (YouTube judges tests on watch time, and clickbait lowers recommendation); the text
  overlay is HTML (Beast / Fire / Neon Lime / Clean Glass / Marker in `styles.md`), the face and scene a plate or the
  creator's real photo cut out (`cutout`). Never use a real person's likeness without their consent.
- ≤ 2 MB for phone uploads (the preset's byte limit); up to 50 MB from a computer.

## 4. Stories and vertical (ig-story, vertical-safe, wa-status, tiktok, meta-ad-story)

Pattern: `story.html` (sticker slot, CTA above the bottom band).

- Frames: 1 hook → content (one point each) → an interactive frame with room for a poll/quiz/slider sticker → CTA
  frame with room for the link sticker. 3–7 frames; ≤ 20 words per frame; type ≥ 56 px.
- Safe box: `vertical-safe` (x 65–916, y 269–1248) for anything cross-platform or paid; `ig-story` for organic
  Instagram/Facebook. Leave a ~700×300 block clear for stickers (e.g. y 780–1080) and keep the CTA above y 1248.
- Patterns: full-bleed photo + headline in the upper safe band; text frame on the brand colour with a sticker slot;
  countdown; "tap for more" sequence; product frame with a link-sticker slot.

## 5. Banners and covers

Patterns: `cover.html` (YouTube, Facebook, LinkedIn, X from one file), `ad-banner.html` (the IAB and Google set).

| Surface (preset) | Geometry | Message |
|---|---|---|
| YouTube channel (yt-banner) | everything important inside the centred 1546×423 | value line ≤ 8 words + cadence ("New videos every Tuesday"); the outer area is pleasant, non-critical imagery (TV shows all of it) |
| Facebook Page (fb-cover) | bottom-left 660×160 clear (avatar); a 2.4:1 crop may cut the right 190 px; content within x 40–1512 | PNG when it carries text or a logo |
| LinkedIn personal (li-profile-cover) | avatar over the lower-left: message in the right 60 % | no extra rule |
| LinkedIn company (li-company-cover) | a thin strip 1512×256 | one line of text or a pattern |
| X header (x-header) | avatar over the lower-left; central band y 60–440, message right | no extra rule |
| Web hero (web-hero + web-hero-mobile) | one static hero; the H1 and CTA are live HTML on the site | art-direct a mobile crop; no auto-rotating sliders |
| Email header/hero (email-header, email-hero) | 600 CSS px at 2×; the headline and CTA in live HTML below | first GIF frame carries the message; transparent-PNG logos with a subtle outline for dark mode |

Don't repeat the avatar/logo large (the platform already shows it); never put CTAs or contact details in crop-prone
edges.

## 6. Posters and flyers (a3-poster, a2-poster, tabloid-poster, poster-18x24, a4-flyer, a5-flyer, dl-flyer, letter-flyer)

Patterns: `poster.html` (image-led, the date inside the visual), `flyer.html` (A5, two sides).

- AIDA as a layout checklist: attention (one image or headline, the largest element) → interest (a benefit subhead)
  → desire (proof, price, offer) → action (**info block**: what · when · where · price · how, with a short URL or QR)
  → brand.
- Budget: headline ≤ 7 words; info block ≤ 5 lines; ≤ 40 words on an A3/A2 poster; flyers may carry more on the back.
- Distance: ~25 mm letter height per ~3 m of reading distance; headline in the top third; info block at eye level.
- QR: ≥ 18.5 mm at arm's length (bigger for distance: roughly distance ÷ 10), a 4-module quiet zone, labelled with the
  action and the URL (`design.py qr`).
- Patterns: image-led (full-bleed image in the top 60 %, info band below); one huge word; Swiss grid; Z-pattern
  (logo → headline → image → CTA bottom-right); tear-off/coupon strip.
- Print: render `.pdf` (vector text, bleed, exact TrimBox/BleedBox), body in 100 % black (no rich black for small
  type), text ≥ 3–5 mm inside the trim, placed photos ≥ 300 ppi at final size (150 for A1+ and roll-ups); proof
  vivid oranges and greens in CMYK with the printer.

## 7. Brochures (trifold-a4, trifold-letter, bifold-a4)

Pattern: `brochure-trifold.html` (folds checked from the preset).

- Tri-fold order: front cover (outside right: hook + brand) → the flap (outside left, seen when the cover lifts: the
  problem/teaser) → the inside spread (three panels: solution, services, proof; the right inside panel is the
  narrower fold-in) → back (outside middle: contact, map, QR, legal).
- Panel widths (A4): outside 97 / 100 / 100 mm, inside 100 / 100 / 97; (Letter) 3.625 / 3.6875 / 3.6875 in and
  reverse. Keep text 4 mm from every fold; bridging images may cross the inside folds, text never does; no QR across a
  fold.
- Bi-fold: cover → inside left (story) → inside right (offer/pricing) → back (contact). Gatefold: the front spans both
  flaps; the inside centre is the reveal.
- ≤ 60–80 words per panel, one heading per panel. Build as two `.page`s (outside, inside) and render `--pages 2`.

## 8. Infographics (ig-portrait, vertical-safe, pin-standard, deck-16x9)

Pattern: `infographic.html` (a line chart drawn from a JSON data block; labels scale per preset).

- Match the relationship to the chart (FT Visual Vocabulary): deviation, correlation, ranking, distribution, change over
  time, magnitude, part-to-whole, spatial, flow; types: statistical, timeline, process, comparison, hierarchical,
  list, geographic (rates, not totals).
- Integrity lint: bars start at 0; no 3D, shadows or decorative textures; no dual axes; pies ≤ 5 categories of a real
  whole; direct labels over legends; source + link + data date; lie factor ≈ 1; pictograms scale by area; no
  exaggerating truncated axes; units, n and time frame shown; percentages add up (or a rounding note); one scale
  across small multiples; light grey gridlines; horizontal text; colour-blind-safe palettes.
- Patterns: one big number with context and source; one chart with a headline stating the finding and a statistical
  subtitle; vertical timeline; horizontal numbered process; versus table.
- Charts are SVG drawn from the data by Claude (or a chart library's SVG output), never generated pixels.

## 9. Business cards (bc-eu, bc-us, bc-jp)

Pattern: `business-card.html`.

Name → role → logo → phone, email, web → address, handle or QR (≥ 18.5 mm). ≤ 7 lines per side; name 10–14 pt,
details 7.5–9 pt (never below 7 pt), 100 % black small type, no hairlines under 0.25 pt. Patterns: logo-only front on
the brand colour + details back; left-aligned details with a vertical rule; centred name with a monogram; QR back.
Render front and back as two `.page`s: `--pages 2 --out card.pdf`. Spot UV or foil is separate artwork.

## 10. E-commerce and marketplace

- Store/site banners: product or lifestyle visual + offer headline (≤ 6 words) + one support line (≤ 12) + a **live
  HTML** CTA; art-directed mobile crop; no auto-rotating sliders; alt text; compressed for LCP.
- Marketplace main image (shop-square, 2000×2000 or larger): the product on a plain ground, generous margins, no text,
  logos, badges, prices, borders or watermarks (Google Merchant Center and eBay penalise them).
- Secondary images (H): feature-callout infographic (3–5 callouts ≤ 5 words, leader lines), in-use shot, scale shot,
  dimensions diagram with units, what's in the box, texture close-up, comparison with own products only.

## 11. Menus (menu-a4, a3-poster)

Sections with clear headers; item name, a short description (≤ 15 words), the price as a bare number without a
currency sign (monetary cues reduce spend); dietary/allergen icons with a legend; ≥ 10–11 pt item text for dim rooms;
aligned prices; no leader dots; there is no evidence for menu "sweet spots".

## 12. Stickers

Die-cut silhouette or roundel, a bold mark or word, optional keyline; ≤ 5 words; text ≥ 6–7 pt and 3 mm inside the cut;
supply the cut path as a separate spot-colour vector ("CutContour") with 2–3 mm artwork beyond it; no hair-thin parts.

## 13. Image to banner / image to social (a client's photo)

1. `design.py analyze --src photo.jpg`: faces, subject, calm zones and their brightness.
2. Either `reframe --presets ig-portrait,ig-story,fb-cover …` (smart crop; it warns when the subject would be cut or the
   photo is too small) or `cutout` the subject and place it on a designed ground or an AI scene plate.
3. Type in HTML in the calm zone (scrim if the contrast check asks), then `pack` to every size.
4. The client's subject, product, label and people are never regenerated; extensions are single-scope and composited
   back; a generative change to a real photo is `compositeWithTrainedAlgorithmicMedia` and, for photoreal people or
   products shown to EU audiences, needs a visible label (`occasions.md`).

## 14. Pinterest pins (pin-standard, pin-square, pin-long, pin-9x16)

Pattern: `pin.html`. A pin is a search result that people save: it has to promise a result at about 183 px wide (two
columns on a phone), so nothing under 60 px on the 1000 px canvas.

- Anatomy: the image of the result; a 3 to 8 word title overlay (a "how to", a list count, a before and after); a small
  logo or URL at the bottom; the Pin title field (the first 40 characters show) repeats the promise.
- 2:3 is the safe ratio; taller pins get cut in the feed (keep the hook inside the top 1000x1500 of a `pin-long`); a
  square pin is never cut but gets a third less height. Organic 9:16: nothing important in the bottom 790 px or the
  right 195 px (action rail).
- Pinterest lays a 4 % grey over pure white, so pure white edges read grey. It rejects blurry images, buttons that
  mimic its UI, more than 2 font styles, heavy capitals and flashing effects.
- Board covers are not uploads: save a pin to the board and pick it (the tile shows its centre square).

## 15. Blog featured images and link cards (blog-featured, og-image, article-hero, x-card)

Pattern: `blog-featured.html`. One 1200x675 master serves the post and every share card.

- Keep type inside x 140 to 1060 and y 40 to 635: that survives WordPress's 3:2 crop, Substack's 14:10 and the 1.91:1
  Open Graph crop. Export `og-image` (1200x630) for Open Graph, Beehiiv and Hashnode.
- Anatomy: the article's promise in at most 10 words, a category label, an optional byline; a photo or illustration on
  one side. Google advises against text-heavy or logo-only images for Discover and article markup: the title in the
  image is a label, the real title is the HTML.
- X draws its own title over the bottom of a large card: nothing in the bottom 140 px there.

## 16. Product image stack, A+ content and store banners

Patterns: `product-infographic.html` (secondary images), `cover.html` (store banners). Presets: `amazon-main`,
`amazon-secondary`, `shop-square`, `gmc-product`, `daraz-product`, `shopee-product`, `lazada-product`, `aplus-*`,
`amazon-store-*`, `etsy-*`, `ebay-*`.

The stack, in selling order (the search tile is 120 to 180 px wide on a phone):

1. **Main image:** the whole product, the variant sold, on pure white (Amazon RGB 255), filling 85 % of the frame,
   soft contact shadow only. No text, badges, props that do not ship, borders, watermarks or collages.
2. **Feature callouts:** the product at 55 to 65 % of the frame, 3 to 5 callouts of 2 to 5 words on leader lines, a
   headline of 6 words or fewer; at most 25 words; repeat the facts in the bullets and alt text.
3. **In use:** a real person or setting; the product at least a third of the frame; models of several body types for
   wearables, with the model's size.
4. **Scale:** in a hand, on a person, beside a known object; one measurement label.
5. **Dimensions:** line drawing with each number beside the part it measures; cm and inches for global markets.
6. **Comparison:** your own range only (never a competitor), 2 to 4 columns, 5 to 6 rows.
7. **In the box:** everything included, with quantities; mark anything sold separately.
8. **Texture or detail:** a macro of the material, finish or port.

Text on images is **banned on every image** at eBay, Google Merchant Center, TikTok Shop, the Meta catalogue, Daraz,
Mercado Libre and Noon: tell the story with arrows, icons, scale objects and composition, or skip the slot. Shopee
allows text on secondary images up to 25 % of the area, never on the product. One 2000x2000 master covers Amazon,
Shopify, WooCommerce, eBay and Google; export 1000x1000 under 1 to 2 MB for Daraz, Lazada and Shopee; Etsy prefers
landscape 2667x2000; fashion is portrait (`amazon-apparel` 10:13, Myntra 3:4).

**A+ content** (Amazon): render at 2x the module minimum; the story runs hook (image header), three reasons, proof,
use, comparison chart (live text, your range), Brand Story. Rejected: prices, promotions, shipping, QR codes, links,
contact details, "best-selling", warranty claims, competitor references, reviews, time words ("new", "now"), more
than one logo. Words baked into a 970 px module need 27 px or more (60 px headings) because phones show it at 40 %.

**Store banners:** everything inside the centre crop (Amazon Store hero: the centre 2100 of 3000 px; Shopify Dawn: the
centre square on phones); headline 6 words or fewer (Amazon: under 30 characters), one support line, the call to
action as live HTML where the platform allows it; five slides or fewer, never auto-rotating on phones.

## 17. App store screenshots (appstore-iphone-69, play-phone-screenshot, play-feature-graphic)

Pattern: `app-screenshot.html`.

- Screenshots 1 to 3 show in search results about 115 px wide each: they must work as a set at that size. Caption
  120 to 180 px on the 1320 px Apple canvas, 90 to 130 px on the 1080 px Play canvas; 2 to 6 words, benefit first.
- Sequence: 1 the core promise on the best real screen; 2 and 3 the two strongest features, one per image; then
  secondary features, personalisation, trust; last a recap. One dark-mode screen if the app has one.
- Frameless real UI by default (Google Play advises against device frames; any frame shrinks the UI). No prices,
  rankings, awards, testimonials or "Download now" (store rules); full battery and signal in the status bar.
- Design Apple (0.46) and Google (0.5625) separately; localise the captions per language.

## 18. Course and event covers

Presets: `udemy-course`, `skillshare-cover`, `teachable-thumbnail`, `thinkific-card`, `kickstarter-project`,
`eventbrite-event`, `luma-event`, `meetup-cover`, `fb-event-cover`.

- One subject, one idea, one focal point; run the **square test**: the centre square must still make sense (Udemy's
  app, Eventbrite search and Luma crop to it).
- Udemy, Skillshare and Thinkific banners want no baked-in title (the platform prints it beside the image); where
  text is allowed (Eventbrite, Meetup, Facebook), only the event name and date, inside the centre square.

## 19. Book, magazine and report covers

Pattern: `book-cover.html` (the e-book front, or the whole print wrap).

- **E-book** (`ebook-master` 1600x2560 passes every store; per store `ebook-kdp`, `ebook-kobo`, `ebook-d2d`,
  `ebook-bookbaby`): title and author must match the store listing and read at about 94 to 136 px wide in search
  results and recommendation strips: two to five big words, the author's name large, one strong image or shape, no
  small print on the front. No price, "free", store names, other stores' stars or 3D mockups. On KDP only, a white
  cover gets a 3 to 4 px mid-grey border (Apple forbids unnecessary borders).
- **Print wrap:** `design.py bookcover --platform kdp|ingram|lulu --binding paperback|hardcover --trim 6x9 --pages N
  --paper white|cream|colour --preset-file book.json` computes the spine from the page count and paper, the full
  canvas with bleed (or the hardcover wrap and hinge), the barcode box and whether spine text is allowed (KDP from 79
  pages, IngramSpark 48, Lulu over 80), and writes a preset with keep-outs and CSS variables (`--spine-x`, `--spine-w`,
  `--front-x`, `--wrap`, `--spine-text`). Then `render --preset <id> --preset-file book.json --out cover.pdf`.
  Back cover: a hook or quote, a 100 to 200 word blurb, one to three real endorsements, author line, publisher mark,
  the barcode box left empty. One ground runs round the spine: spines drift up to 1/16 in, so a colour change on the
  fold shows as a sliver (the render warns). Right-to-left books mirror the wrap.
- **Magazine** (`magazine-us`, `magazine-a4`): masthead and the main cover line in the top band (racks overlap
  covers), 3 to 6 cover lines, issue date and price, the distributor's barcode.
- **Report, proposal, assignment cover** (`report-cover-a4`, `report-cover-letter`): title in the upper half,
  subtitle, organisation and logo (top or bottom, not both), date or period; 12 mm more on a bound edge (15 mm wiro).

## 20. Podcast, album, audiobook and artist art

Pattern: `square-cover.html`. Presets: `podcast-cover`, `album-cover`, `audiobook-cover`, `spotify-header`,
`apple-artist-image`, `soundcloud-header`.

- Square art is seen at 55 to 180 px: the name large, one image, high contrast.
- Release covers: 3000x3000 passes every distributor (keep a 4000 master for Apple Music). Only the artist name and
  the exact title may appear; rejected: URLs, QR codes, handles, store names or logos, prices, "CD" or "vinyl",
  format claims, blur, reused art, unlicensed stock.
- Audiobooks (ACX): 2400x2400 or larger, title and author present; no Audible branding, prices, running time,
  barcodes or borders; exclusive titles may get Audible's badge in the bottom-right corner (the preset keeps it clear).
- Podcasts: 3000x3000, no alpha; episode art without text (the titles show beneath it).
- Artist profile images (Spotify, Apple Music): no text at all; faces inside the crop guides.

## 21. Certificates, invitations, greeting cards and stationery

Patterns: `certificate.html`, `invitation.html`, `business-card.html`.

- **Certificate** (`certificate-a4-landscape`, `certificate-letter-landscape`): logo, the title ("Certificate of
  ..."), the recipient's name as the biggest line, the reason, date, one or two signature blocks with printed names and
  titles, an optional seal or verification number or QR. Frames sit well inside the safe area (trim drift makes a
  frame near the edge uneven). Signatures are the signer's own scans, never drawn.
- **Invitation** (`invite-5x7`, `invite-a5`, `invite-a6`, `invite-dl`, `invite-square-148`): host line, the names or
  event, date and time, venue, how to reply, dress code or notes; about 40 words on the front, details on an insert.
  A Bangladeshi wedding card is usually bilingual (Bangla and English), names both families, and has separate cards
  or panels for gaye holud, aqd and reception (bou-bhat or walima): keep the family's wording exactly. Nothing under
  8 pt; lines 0.5 pt or more. Envelope pairs: A7 for 5x7, C6 for A6, C5 for A5, DL for DL.
- **Greeting and Eid cards** (`greeting-a6-folded` and the other folded sizes): designed on the flat sheet with the
  fold in the preset; the outside spread is back (left) and front (right); text keeps clear of the fold.
- **Postcards** (`postcard-4x6`, `postcard-a6`, `postcard-6x9`): the back splits into a message half and an address
  half; in the US keep the bottom-right 4.75 x 0.625 in barcode zone empty and the address type 8 pt or more.
- **Letterhead, compliments slip, envelopes** (`letterhead-a4`, `letterhead-letter`, `comp-slip-dl`, `envelope-*`):
  logo and name in the header, contact and registration details in the footer, the address window and body clear;
  no heavy full-bleed colour on sheets that go through office printers; envelopes have no bleed.

## 22. Tickets, badges, tags, stickers, labels and packaging

- **Tickets and vouchers** (`ticket-2x5.5`, `ticket-dl`, `voucher-dl`, `gift-certificate-us`): event, date, time,
  venue, seat or tier, price, terms, serial number; the stub on one end; the number area at least 24 x 6 mm, 5 mm from
  the edge.
- **ID cards and badges** (`id-card-cr80`, `badge-4x3`, `lanyard-0.75in`): the first name very large (read at 1 to 2 m:
  about 22 mm capitals), the slot punch area at the top kept clear, both sides printed on hanging badges.
- **Hang tags, door hangers, bookmarks, table tents** (`hang-tag-2x3.5`, `door-hanger-3.5x8.5`, `bookmark-2x6`,
  `table-tent-4x6`): nothing within about 10 mm of a hole; the die cuts through the art, so use the printer's
  template; every face of a tent works alone and upright.
- **Stickers and labels** (`sticker-*`, `label-*`): bleed 1/8 in outside the cut, safe 1/16 to 1/8 in inside; the cut
  line is a separate vector path in a named spot colour (CutContour and the like), never in the Chrome PDF; clear
  stickers need a white ink layer. Product labels carry the legal copy of the market (US net quantity in the bottom 30 %
  of the front panel; Bangladesh BSTI: Bangla first, MRP, maker, dates).
- **Packaging:** always the printer's dieline (never a drawn one); cut, crease and bleed on their own named layers;
  art 3 to 5 mm from cuts and folds; design each panel upright as it will stand, not the flat sheet as one picture.

## 23. Merch and print on demand (tshirt-*, hoodie-*, mug-*, tote-*, phone-case-*, sticker-redbubble)

- The merch presets render a **transparent PNG** where the product prints only the art (garments, totes, stickers,
  embroidery): no body background in the HTML. Full-print products (phone cases, pillows, PopSockets, mugs) run a
  background to the edge; transparent areas print white.
- One short phrase or one mark reads best; type at least 32 pt at 300 dpi on light tees and 48 pt on hoodies; big
  front graphics about 10 to 12 in wide even on a 15 in canvas; the top of the art 1.5 to 3 in below the collar;
  left-chest logos 3 to 4 in wide; embroidery letters 0.25 in tall or more, 6 thread colours at most, no gradients.
- No semi-transparent glows (they print faded); dark art on dark garments vanishes; no trademarked words, watermarks
  or contact details (Merch by Amazon rejects them). Mugs: keep key elements off the seam and the handle gap.

## 24. Messaging and regional formats

Presets: `wa-status`, `wa-business-cover`, `wa-catalog`, `wa-sticker`, `tg-post`, `tg-story`, `tg-sticker`,
`viber-image`, `line-richmenu-large`, `line-rich-message`, `kakao-msg-4x3`, `wechat-cover`, `weibo-cover`, `xhs-note`,
`douyin-cover-16x9`, `vk-cover`.

- WhatsApp compresses Status media: clean, high-contrast art; catalog images follow Meta's catalogue rules (no text
  over the product). Stickers: exactly 512x512 WebP, static 100 KB, an 8 px white outline; the first frame of an
  animated sticker shows the whole sticker.
- Telegram stories are exactly 1080x1920; stickers one side exactly 512 px; custom emoji 100x100.
- LINE rich menus (2500x1686 or 2500x843) do not show on LINE for PC; KakaoTalk channel messages have character caps.
- Bangladesh: WhatsApp Status, Business and stickers do the heavy lifting for festivals; Telegram channels for
  education and deals; Google Business Profile for local shops. China uses its own set (WeChat 2.35:1 plus 1:1 covers,
  Xiaohongshu 3:4 notes); Chinese type needs larger minimum sizes than Latin.
- Right-to-left markets mirror avatars and buttons: mirror the keep-outs and check before delivery.

## 25. Calendars, CVs, academic posters and zines

- **Calendars** (`calendar-wall-a3`, `calendar-desk-a5`, `calendar-wall-bd-18x23`): a picture area and a month grid;
  room at the top for the wiro or hanger; dates 8 pt or more; weekend and holiday colours consistent; in Bangladesh,
  Bangla, English and often Hijri dates together.
- **CV** (`cv-a4`, `cv-letter`): one or two pages, body 10 to 12 pt, no bleed, live text for applicant tracking
  systems; a Bangladeshi "biodata" may add a photo and personal details: confirm what the recipient expects.
- **Academic poster** (`a0-poster`, `poster-academic-56x36`): title readable from about 3 m, 300 to 800 words, 150 to
  200 ppi at full size.
- **Zines** (`zine-mini-letter`, `zine-mini-a4`): eight panels from one sheet (the top row prints upside down); margins
  1/8 to 1/4 in because copiers crop edges.

## 26. Signage, billboards, transit, events and screens

Presets (`presets --group signage`): `yard-sign-24x18`, `a-frame-insert-24x36`, `a-board-a1`, `banner-3x6ft`,
`pvc-banner-2000x1000`, `pvc-banner-bd-3x4ft`, `rollup-850` and `rollup-*`, `x-banner-60x160`, `festoon-election-bd`,
`billboard-us-bulletin`, `billboard-uk-48sheet`, `billboard-bd-20x10ft`, `transit-bus-king`, `step-repeat-8x8ft`,
`popup-10ft-straight`, `table-throw-6ft`, `window-cling-900x600`, `floor-decal-24in`, `signage-1080p`, `signage-d6`,
`led-wall-16x9-p2.6`. Patterns: `sign.html` for landscape signs, banners, billboards, bus sides and screens (every line kept above the distance floor, the headline fitted to what is left); `poster.html` for portrait ones.

- **Distance sets the type.** Every sign preset carries its farthest reader (`view_distance_m`, an estimate unless the
  source gives one): signs read on foot follow ADA 703.5.5; billboards, bus sides and roadside screens are read in
  passing and follow the legibility index (`legibility_index` 30: capitals = distance / 30 ft per inch, 2.78 mm per
  metre). Give the real site's distance with `--view-distance`; for a custom roadside size add `--legibility-index 30`.
- **Copy:** billboards 7 words or fewer in the headline and about 10 on the board, at most 3 visual elements, about 5
  seconds of viewing; roadside digital 5 to 7 words; yard signs a headline and a phone number or URL; roll-ups the
  brand and headline in the top third, details in the lower third where people stand close.
- **Billboards and bus sides are supplied at a scale** (US bulletin 1/2 in = 1 ft, UK 48-sheet 10 %, bus kings 1/8):
  the preset's `file_scale` makes the floors and the image check work at the real size. The media owner decides the
  scale and bleed: build per owner. Bold sans serif, a thin dark stroke round light text, no white grounds on digital
  boards, no all-black grounds on paper 48-sheets.
- **Hardware eats the edges:** hems, grommets and pole pockets on banners (text 2 in from the edges, 3 in from a
  pocket), hidden top 1 in and bottom 3 in on roll-up stands, frame lips on A-boards (25 mm), corner rings on
  X-banners, panel breaks on pop-up walls, the crumpled bottom of a table throw. The safe zones in the presets allow
  for them; the supplier's template wins.
- **Screens:** design at the native size (1920x1080, 3840x2160, portrait 1080x1920); keep text inside the TV title-safe
  area (5 % from each edge); menu boards made of several screens keep text off the bezel lines; an LED wall's canvas is
  cabinets times pixels per cabinet (read the spec sheet).
- **Bangladesh:** large format is quoted in feet and printed on PVC flex; demy (18x23 in) and crown (15x20 in) for
  posters and calendars; X-banners sold as "2 x 5 ft". Election material follows the Election Commission's codes: no
  posters, festoons at most 18x24 in, banners 10x4 ft, billboards 16x9 ft, black and white only, no PVC, a print date on
  local-election pieces, only the candidate's own photo and symbol. Send PDFs with embedded Unicode Bangla fonts (never
  SutonnyMJ); convert Bangla to outlines only when a shop insists on editable files.

## 27. A request that fits none of these

Find the format (`presets --find`), then follow `formats.md`: the spec ladder for an unknown size or platform (§3)
and the archetype table for an unknown kind of design (§4). Record what you learn as a project preset so the next job
starts from it.

## 28. Video and motion

Anything delivered as a video (animated posts, reels, stories, intros, HyperFrames or Remotion renders) goes through
the `agy-watch-video` skill before delivery:

1. `qa VIDEO --platform reels --strict`: black and frozen frames, flicker, loudness, specs and safe zones. It exits 2
   on a failure.
2. `watch VIDEO --goal motion --expect copy.txt`: each approved on-screen line, found or not.
3. `verify` any finding before you act on it.

To study a reference or a competitor's video, use `watch VIDEO --goal promo`.
