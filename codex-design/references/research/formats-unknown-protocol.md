# Unknown-format protocol

A decision procedure for the design skill when a request names a size, surface or kind of design that no preset covers. Compiled 2026-09-24. Every number carries a source; anything without one is marked **heuristic** (a practitioner rule or a reasoned default) or **derived** (computed from a cited rule, formula shown).

Labels used below: **official** (the platform's, standard body's or printer's own page), **secondary** (a third party), **derived**, **heuristic**.

---

## 0. The procedure at a glance

1. **Name the medium.** Screen, print, or both (section 2).
2. **Climb the spec ladder** until a rung gives a real number (section 1). Stop at the first rung that answers; record source, date and confidence.
3. **If the ladder runs out, use first principles:** screen (section 3) or print (section 4). State every assumption in the render report, as the skill already does for custom sizes (`canvas.assumed`).
4. **Ask at most four questions** (section 5). If the person cannot or will not answer, apply the stated defaults and say so.
5. **Classify the job** into an archetype (section 7) and build that archetype's anatomy.
6. **Design one master, then adapt** by crop or re-composition (section 6), and run the same checks on every output.

The gap list in `canva-catalog.md` shows which common design types have no preset yet; treat any of them as "unknown" until a preset exists.

---

## 1. The spec ladder: how professionals find an unknown spec, in order

| Rung | What to do | Evidence that it is the right order |
|---|---|---|
| 1. The platform's own spec page | Read the help centre, ads guide or developer docs of the surface where the design will live. Prefer the newest dated page; an archived official page beats a current blog. | Official pages carry numbers blogs get wrong. Examples from this run: X's card docs (2:1, minimum 300x157, maximum 4096x4096, under 5 MB, first GIF frame only, no SVG; archived 2025-05-31); Meta's og:image page (at least 1200x630, keep close to 1.91:1, minimum 200x200, under 8 MB); Apple Podcasts, which tells creators to "Avoid using your podcast logo or any text" in Episode Art; Teams admin backgrounds (PNG or JPEG, 360x360 to 3840x2160). Canva's own size guide still lists a 1,024 x 512 "Twitter Post" and a 1,920 x 480 Twitch banner where Twitch recommends 1200x480 (see `canva-catalog.md` section 8). |
| 2. The printer's template or dieline | Ask the print shop for its template before designing anything folded, bound, die-cut, large-format or packaged. A template beats every generic number. | Canva: "If you're printing outside Canva Print, check with your print provider for bleed requirements. They may trim at different margins." Solopress (UK printer): minimum 3 mm bleed, a safe area 3 mm inside the trim, 300 ppi, a 10 mm allowance on wiro-bound edges, and an extra artwork page or layer for spot UV or foil. Apple ships downloadable templates for every podcast artwork type for the same reason. |
| 3. The client's existing assets | Ask for last year's file of the same item, the brand guidelines and the logo files, then measure and match them. | Canva's design-brief guide lists "What previous design and marketing materials have they used?", "Are there existing brand guidelines?", the logo's file format, required fonts and colours, and "Clarify what formats are needed for all of the deliverables." |
| 4. Measure the live surface | Open the real page at a phone width (390 CSS px) and a desktop width (1440 CSS px), read the rendered box of the slot with `getBoundingClientRect`, note its `object-fit` crop and every overlay (badges, avatars, buttons), and screenshot it. Date the measurement, because UIs change and run A/B tests. | The skill's R5 research measured the YouTube thumbnail badge and the Facebook cover and avatar this way, and found Facebook's help text ("16:9 on computers / 2.4:1 on mobile") disagreed with the rendered 2.7:1. |
| 5. The device's screen | Use viewport statistics and platform layout guides (section 3.4). | StatCounter, Apple HIG, Android TV guidelines (below). |
| 6. First principles | Only now fall back to the rules in sections 3 and 4, and label the result heuristic. | |

**Stop rule (heuristic).** When two rungs disagree, the higher rung wins, and the disagreement is written into the preset's `notes`. Re-verify platform numbers every quarter (the skill's existing preset note says the same).

No agency process document could be fetched this session (the search budget was spent), so the ordering above rests on the printer and platform statements quoted, plus the skill's own measurement practice.

---

## 2. Screen, print or both?

- **Print** if it will be trimmed, folded, bound, mounted, hung or handed out. Units are mm or inches, and bleed, safe margin, ppi and colour mode apply (section 4).
- **Screen** if it is shown on a phone, desktop, TV, signage display or projector. Units are px, and the viewing width or viewing distance sets the text floor (section 3).
- **Both** (for example a poster that is also posted on Instagram): design the master at print size, then adapt to screen formats (section 6). Never upscale a screen export for print.

---

## 3. First principles for an unknown SCREEN graphic

### 3.1 Pick the aspect-ratio family by where it is seen

| Family | Where it is used (source) | Existing or new presets |
|---|---|---|
| 1:1 | Square feed posts (Instagram, Facebook, LinkedIn, X), X summary card (official, "cropped to a square on all platforms"), podcast and app icons (Apple 1024x1024), profile pictures, Google Ads square 1200x1200 | ig-square, li-square, podcast-cover, x-card-summary, app-icon-1024 |
| 4:5 | Instagram, Facebook, Threads and LinkedIn portrait feed posts; Meta feed ads 1440x1800; Google Ads portrait 960x1200 (R5) | ig-portrait, meta-ad-feed, gads-portrait |
| 3:4 | Instagram 3:4 posts and the 3:4 profile grid since 2025; X shows 3:4 single images uncropped (R5); Canva's Lemon8 post is 3000x4000 | ig-3x4 |
| 2:3 | Pinterest standard pin 1000x1500 (R5); Canva's blog graphic 800x1200 | pin-standard |
| 9:16 | Stories, Reels, TikTok, Shorts, WhatsApp Status, Snapchat (R5); full-screen phone heroes | ig-story, vertical-safe, web-hero-mobile-9x16 |
| 16:9 | YouTube, TV and broadcast (ITU/EBU safe areas), slides, video thumbnails (Vimeo, Wistia, LinkedIn: match the video), meeting backgrounds (Zoom 1920x1080), Google Discover article images | yt-thumbnail, deck-16x9, video-thumb-16x9, virtual-bg, article-hero |
| 1.91:1 | Open Graph and link previews (Meta 1200x630; LinkedIn 1200x627 minimum, 5 MB); Google Ads landscape 1200x628; Instagram landscape 1080x566 | og-image, og-whatsapp, li-landscape, gads-landscape |
| 2:1 | X summary_large_image (official 2:1); email hero at 600x300 CSS | x-card, email-hero, email-hero-660 |
| 3:1 | X header 1500x500; email header 600x200 CSS (Canva's Email Header is 600x200 px); section banners | x-header, email-header, web-banner-3x1 |
| 4:1 | LinkedIn profile cover 1584x396; Etsy big banner 1600x400 / 3360x840; Apple Podcasts Showcase Hero 4320x1080; IAB billboard 970x250 is about 3.9:1 | li-profile-cover, etsy-banner, podcast-hero, iab-billboard |

When the family is still unclear, pick the one used by the most likely surface and add the neighbouring family as an adaptation (section 6).

### 3.2 Canvas pixels

- **Rule (derived).** Canvas width = the width the image occupies in CSS px x the device pixel ratio. Default to 2x for web and email images; the skill's email presets already export 600 CSS px at 1200 px.
- **Platform caps to respect (official):** WordPress scales uploads larger than 2560 px down to 2560 (`big_image_size_threshold`); Squarespace calls 2500 px wide ideal and warns that under 1500 px may blur; Webflow generates variants up to 3200 px and caps uploads at 4 MB; HubSpot does not auto-resize images above 4096 px; X accepts up to 4096x4096; Teams admin backgrounds up to 3840x2160; Canva's editor allows 40x40 to 8000x3125 px, and its API allows 40 to 8000 px per side with a 25,000,000 px area cap.
- **Heuristic.** Beyond 2x, file weight grows faster than visible sharpness for photos; reserve 3x for small UI art such as icons.

### 3.3 Safe margins

| Case | Margin | Source |
|---|---|---|
| Default for an unknown screen graphic | 5% of the short side on every edge | Skill default; the same 5% as broadcast graphics safe and Android TV (below) |
| Video frames (HD, UHD) | **Graphics (title) safe: 5% per edge** (the inner 90%); **action safe: 3.5% per edge** (the inner 93%). 1920x1080: 96 px sides and 54 px top/bottom for graphics, 67 px and 38 px for action. 3840x2160: 192 and 108 px for graphics (3456x1944 box), 134 px and about 76 px for action (3572x2008 box). | ITU-R BT.1848-1 (10/2015); EBU R 95 v1.1 (June 2017). SMPTE ST 2046-1 covers the same topic; its text was not readable this session. |
| Old convention | Title safe = inner 80%, action safe = inner 90%. Still the Final Cut Pro overlay. Use it only when the output may reach old or unknown TVs (heuristic). | Apple Final Cut Pro User Guide |
| TV apps (10-foot UI) | Android TV: a 5% margin, 48 dp left and right and 27 dp top and bottom on a 960x540 dp layout, while noting "Most modern TVs no longer have overscan issues". tvOS: inset 60 pt top and bottom, 80 pt at the sides. | Android Developers, TV layouts; Apple HIG, Layout |
| Vertical social video (pointer only) | Meta: keep text out of 14% top, 35% bottom and 6% of each side; add TikTok's right-hand action rail. Already modelled in `vertical-safe`. | R5 (Meta Ads Guide); TikTok's guidance is qualitative |
| Unknown `object-fit: cover` box | Derive the safe box as the intersection of the centre crops for every likely box ratio. Example: a 3:2 image that may show at 16:9 and 1:1 keeps its subject inside the centre 16:9 band and the centre square. | Derived (used for `blog-featured-3x2` from WordPress theme crops) |

### 3.4 The viewing width people actually see

- **Phones.** StatCounter, August 2026, top phone screen sizes (CSS px): 414x896 (13.63%), 360x800 (9.25%), 390x844 (6.81%), 393x873 (5.27%), 384x832 (4.35%), 360x780 (3.17%). Use **390** as the default viewing width (the skill's current default) and **360** as a strict mode for text that must be read (heuristic: the narrowest common width).
- **Desktops.** StatCounter, August 2026: 1920x1080 (22.22%), 1536x864 (6.7%), 1366x768 (5.2%), 1280x720 (3.52%); the page also lists "1366x1366" (8.59%) and "384x832" (4.2%) as desktop resolutions, which look like data oddities.
- **Content columns.** WordPress Twenty Twenty-Five: content 645 px, wide 1340 px; Twenty Twenty-Four: 620 and 1280 px. Email templates: 600 px by default in Klaviyo ("the default width of every template is 600px") and Kit (max-width 600px); Mailchimp's new builder uses 660-1320 px images and its legacy builder 600-1200; Mailchimp lists 600-800 px as the safe template width. So a "desktop column" is about 600 to 800 CSS px wide (derived from these).
- **Thumbnails and small cards.** YouTube thumbnails render at 200-375 CSS px (R5, measured); podcast covers at 55-180 px (R5); an X summary card image is a small square (heuristic 150 px).
- **TVs, signage and rooms.** Do not use CSS width; use viewing distance (section 3.6).

### 3.5 Minimum text size at viewing size

**Formula (derived, already in the skill):** `min_text_px_on_canvas = floor_css_px x canvas_width / viewing_width_css`.

| Floor | Value | Source |
|---|---|---|
| Hard floor | 11 CSS px | Apple HIG minimum text size on iOS and iPadOS: 11 pt (default 17 pt). macOS minimum 10 pt (default 13), visionOS 12 (17), watchOS 12 (16), tvOS 23 (29). |
| Warning line | 12 CSS px | Google Lighthouse flags pages when "40% or more of the text has a font size smaller than 12 px" and advises at least 12 px on at least 60% of the text. This is the "about 12 px" floor for graphics seen at phone width. |
| Sentence-length text | 16 to 19 CSS px | GOV.UK body text is 19 px and its smallest size 16 px; Apple's iOS default is 17 pt. Heuristic: any text longer than a label should reach 16 px at viewing size. |
| "Large text" for contrast | 24 CSS px (18 pt), or 18.67 CSS px (14 pt) when bold | WCAG 2.2 definition of large-scale text; px values derived at 1 pt = 1.333 CSS px. WCAG sets no minimum font size. |
| Contrast | 4.5:1 normal text, 3:1 large text, 3:1 for UI and graphical objects; 7:1 enhanced | WCAG 2.2 SC 1.4.3, 1.4.6, 1.4.11 |

**Recommendation for the skill:** keep 11 px as the hard floor, add a 12 px warning (Lighthouse), and require 16 px at viewing size for sentence-length copy (heuristic). Worked examples (derived): a 1080-wide post seen at 390 px needs 30.5 px text on the canvas (33.0 px in strict 360 mode); a 1920-wide video frame watched on a phone needs 54 px; a 1280x720 YouTube thumbnail seen at 200 px needs 70 px.

### 3.6 Screens seen from a distance (TV, signage, projection)

- **AVIXA DISCAS (ANSI/INFOCOMM V202.01:2016), Basic Decision Making (official):** the viewing ratio is farthest viewer distance divided by image height, and the minimum element height (a character at a given font size) rises with it: ratio up to 1.0: 0.5% of image height; 1.0-1.5: 0.75%; 1.5-2: 1.0%; 2-3: 1.5%; 3-4: 2.0%; 4-5: 2.5%; 5-6: 3.0%; 6-7: 3.5%; 7-8: 4.0%; 8-9: 4.5%; 9-10: 5.0%. The acuity factor for Basic Decision Making is 200, so **element height = farthest viewer distance / 200** (derived from the table). The acuity factor for Analytical Decision Making (resolving single pixels) is 3438.
- **Slides (official + derived):** Microsoft's accessibility guidance says "Use a larger font size (18pt or larger)". PowerPoint's default Widescreen slide is 13.333 x 7.5 in and its 4:3 slide is 10 x 7.5 in, so 18 pt is 1/30 of the slide height: 36 px on a 1080-high canvas and 25.6 px on a 768-high one. DISCAS agrees: 3.5% of 1080 is 38 px when the farthest viewer sits 6 to 7 image heights away. The existing `deck-16x9` floor (16 px at a 1280 viewing width) suits decks read on a screen, not projected ones; use `deck-16x9-room` for rooms.
- **Worked example (derived):** a 55-inch menu screen (image height about 0.68 m) read from 4 m has a viewing ratio near 5.9, so characters need about 3% of the height: 32 px on 1080 lines. Prices and the headline should be well above that (heuristic).
- **"Element" is ambiguous.** DISCAS measures a character; if you read it as cap height, the font size must be about 1.4x larger because cap height is roughly 0.7 em in common sans faces (heuristic; measure the real font's cap height).

### 3.7 File weight

Use the platform's limit when one exists. Defaults found this run: email images 1 MB or less (Mailchimp, Klaviyo; Klaviyo's upload maximum is 10 MB, Mailchimp's Content Studio 1 MB per image); pop-up side images 50-100 KB and backgrounds under 200 KB (Klaviyo), about 300 KB (Mailchimp); WhatsApp link previews need images under 300 KB (Wix Help, secondary); display ads by pixel area per the IAB table in R5. Gmail clips messages whose HTML is larger than 102 KB, but images do not count toward that limit (Mailchimp; Email on Acid, 2023-04-11).

---

## 4. First principles for an unknown PRINT piece

### 4.1 Bleed by size class

| Class | Bleed | Source |
|---|---|---|
| Cards, flyers, postcards, leaflets, booklets | 3 mm per edge (a 210x297 mm A4 file is 216x303 mm); 0.125 in (3.175 mm) for US printers | Solopress Bleed Guide ("Industry-standard is 3mm of bleed on each edge"); Canva Help (0.125 in on all trimmed products) |
| Large-format posters | about 0.25 in (6.35 mm) is common | Wikipedia "Bleed (printing)", via R5 (secondary) |
| Die-cut items | sometimes 0.25 in | Wikipedia via R5 (secondary) |
| Wiro-bound documents | 10 mm allowance on the bound edge (in addition to bleed) | Solopress Supplying Artwork Guide |
| Roll-up banners, vinyl banners, fabric, signs | follow the stand's or printer's template (hidden base area, hems, eyelets vary). Solopress roll-ups: PDF at 300 DPI; widths 800, 850, 1000, 1200, 1500 or 2000 mm, mostly 2000 mm tall (XL up to 2000 x 3000 mm) | Solopress Roller Banners page; base allowance not published on the page read |
| Office or home printing | none; keep content inside the printer's unprintable edge (heuristic 5 mm) | heuristic |

### 4.2 Safe margin

- Solopress: the safe area "starts 3mm inside the document edge"; "No text or essential details should appear outside of this area".
- Heuristic by size: 3-5 mm for cards and flyers, 10 mm or more for posters, more again for anything viewed across a room or hung (the skill's R5 uses 3-5 mm and "more for posters"). Double the margin beside folds and bindings (heuristic).

### 4.3 Resolution by viewing distance

- **Close reading (official):** 300 ppi at final size. Solopress: "a minimum resolution of 300ppi"; Canva: "The minimum recommended resolution for print is 300 DPI."
- **Formula (derived):** a viewer with normal acuity resolves about 1 arcminute (Wikipedia, Visual acuity: 20/20 letters subtend 5 arcminutes, their critical detail 1 arcminute). A pixel smaller than that is invisible, so `ppi_needed = 3438 / distance_in_inches`, or `87.3 / distance_in_metres`. The same constant, 3438, is DISCAS's acuity factor for Analytical Decision Making. Check: at 11 to 12 in the formula gives about 286 to 313 ppi, matching Apple's "about 300 ppi ... held 10 to 12 inches" claim for Retina displays.
- **Table (derived):** 0.3 m: 291 ppi; 0.5 m: 175; 1 m: 87; 2 m: 44; 3 m: 29; 5 m: 17; 10 m: 9.
- **Rule:** use the larger of the formula result and the printer's minimum. Many printers still ask for 300 ppi regardless of size; the 100-150 ppi often quoted for large format was not verified this session (heuristic), which is why the skill renders large print through the vector PDF path.

### 4.4 Text size by viewing distance

- **Signs (official): ADA 2010 Standards, Table 703.5.5**, character height measured on the uppercase "I":
  - mounted 40-70 in above the floor: 5/8 in (16 mm) under 72 in (1830 mm) viewing distance; beyond that, 5/8 in plus 1/8 in (3.2 mm) per foot (305 mm) of distance over 72 in;
  - mounted over 70 up to 120 in: 2 in (51 mm) under 180 in (4570 mm); plus 1/8 in per foot beyond;
  - mounted over 120 in: 3 in (75 mm) under 21 ft (6400 mm); plus 1/8 in per foot beyond.
  - Metric form (derived): cap height in mm = 16 + 10.5 x (distance in m - 1.83), for eye-level signs read from 1.83 m or more. The same section sets stroke width at 10-30% of the character height, letter spacing at 10-35% and line spacing at 135-170%.
- **Screens and projection (official):** DISCAS, element height = farthest viewer distance / 200 (section 3.6).
- **Safety tags (official):** OSHA 1910.145 requires the signal word to be "readable at a minimum distance of five feet (1.52 m) or such greater distance as warranted by the hazard".
- **From cap height to font size (heuristic):** font size is about cap height / 0.7 for common sans faces; measure the chosen font.
- **Worked examples (derived):** a poster read at 3 m at eye level needs capitals about 28 mm tall, so roughly 40 mm (about 114 pt) type; a gate banner read at 10 m needs capitals about 102 mm tall (about 145 mm type). The ADA values are generous because they are set for people with low vision; that is the point for public signs.

### 4.5 Colour

- Deliver CMYK unless the printer says otherwise. Solopress converts RGB to CMYK and warns "this could affect your colours"; Canva converts RGB to "the closest possible CMYK match" and names bright blues and hot pinks as out of gamut. Pantone colours are converted to CMYK unless quoted separately (Solopress).
- Ask for the printer's ICC profile and ink limit. R5 already records the profile families (FOGRA39, FOGRA51 / PSO Coated v3, GRACoL) and its lint of 300% total ink on coated stock is a heuristic, not a profile value.
- Special finishes (spot UV, foil) travel as a separate page or layer (Solopress).

### 4.6 What to ask the printer (minimum)

1. The product and trim size, and **is there a template or dieline?**
2. Bleed and safe margin (and any allowance for binding, hems, eyelets or a banner base).
3. File format and colour: PDF/X version, ICC profile, ink limit, spot colours, RGB accepted or not.
4. Minimum resolution, and how finishes (folds, die-cut, foil, spot UV) must be supplied.
5. Proof method and deadline.

Every item comes from the checklists in Solopress's Supplying Artwork, Bleed and Resolution guides and Canva's print help; a printer's own answer overrides this list.

---

## 5. The minimum questions to ask a client (at most four) and the defaults

Canva's design-brief guide lists ten questions (client, scope, audience, competition, tone, goal and measure, budget, approvals, previous materials, other contributors). The four below keep only those that change the canvas or the content; the rest can wait.

| # | Question | Default when there is no answer | Reasoning |
|---|---|---|---|
| 1 | **Where will people see it?** (platform and placement; or, for print, the printer and product) | Screen, phone feed: a 1080x1350 (4:5) master, adapted to 1080x1920 (9:16) and 1200x630 (1.91:1) on request. Print with no printer: A4 (US Letter for US and Canadian clients), 3 mm / 0.125 in bleed, 3-5 mm safe, 300 ppi, CMYK PDF, all stated as assumptions. | 4:5 is accepted as a feed post by Instagram, Facebook, Threads and LinkedIn (R5), so one master reaches the most placements. The paper size follows the client's market, not the requester's (the skill's global-by-default rule). |
| 2 | **What should someone do or know after three seconds?** | Infer the archetype from the content (section 7): one message, one call to action. | The archetype decides the anatomy; a design with two jobs usually does neither (heuristic, shared by the skill's playbooks). |
| 3 | **What must it say or show, exactly?** (words, date, time and place, price, logo, legal line, link or QR) | Use only the facts supplied; leave clearly marked placeholders for anything missing; never invent dates, prices, names, reviews or statistics. | Invented facts are the costliest error in client work; the skill's genres already require real sources for prices and testimonials. |
| 4 | **Who is it for, and are there brand rules or past examples?** (audience and language; logo files, colours, fonts) | Neutral, legible type; the audience's language and script; ask for a vector logo. | Canva's brief asks for brand guidelines, logo formats, fonts and colours; the skill's copy rules decide language by audience. |

---

## 6. One master design into many sizes

### 6.1 Crop or re-compose? (derived rule, heuristic thresholds)

- Let `r = max(a1/a2, a2/a1)`, where a1 and a2 are the two aspect ratios.
- **Crop (or extend the background)** when r is at most 1.25 (for example 4:5 to 1:1, or 16:9 to 1.91:1), the orientation does not flip, and every text block and logo already sits inside the intersection of the two safe boxes.
- **Re-compose** when r is above 1.25, when landscape becomes portrait or the reverse, when the new viewing width makes text fall below the floor (a 1080 feed post turned into a 200 px thumbnail), or when the new platform adds overlays (for example the 9:16 UI bands).
- Why: InDesign's own "Scale" rule "may introduce gaps if the aspect ratios differ", Figma needs explicit constraints to decide what moves, and Canva's Magic Resize produces a copy for the user to fix. None of these tools claims a finished result, so the skill must check every output.

### 6.2 What moves, what stays

| Element | Behaviour in the adaptation | Tool analogue |
|---|---|---|
| Background photo | Re-crop around the focal point; extend with generative fill only when the crop would cut the subject; never stretch | Shopify focal points (Dawn 7.0.0 and later); CSS `object-position` |
| Logo | Pinned to the same corner inside the safe box, sized from the short side | Figma constraints Left/Right/Top/Bottom |
| Headline | Reflows; size follows the short side but never drops below the text floor; line count may change | InDesign Guide-based rule (text reflows) |
| CTA or button | Stays near the bottom but above platform overlays; live HTML on web and email | |
| Legal line | Keeps its minimum size; moves to the caption, alt text or HTML if it does not fit | |
| Secondary elements | Removed before primary ones shrink (heuristic) | |

Tool models, for reference (official): Figma constraints are Left, Right, Left and right, Center, Scale (default Top and Left). InDesign liquid page rules are Scale, Re-center, Guide-based and Object-based. Canva Magic Resize: up to 5 new sizes per design, 50 designs per batch, 250 outputs, custom sizes 40x40 to 8000x3125 px. Adobe Express's image resizer offers ratio and social presets, then "scale, pan, and crop". Google's responsive display ads "adjust the size, appearance, and format of your ads to fit just about any available ad space". The IAB portfolio already defines ad units by aspect ratio (R5 section 3.1).

**Agency practice (heuristic; no agency document was fetched this session):** studios keep one master key visual and an adaptation matrix (sizes x languages x placements), lay a safe-zone overlay per platform over each size, and review every adaptation, not just the master.

---

## 7. Classify an unknown topic or kind of design by its job

Pick the archetype from the main verb of the brief. When two apply, the one that carries the call to action wins (for example an Eid sale is **sell** with celebratory styling; a webinar is **invite**; a new branch opening is **announce**, then **invite**). Existing playbooks in the skill's `genres.md` and `occasions.md` cover several of these in detail.

| Archetype | Job | Anatomy, in order of prominence | Must-haves and traps | Source |
|---|---|---|---|---|
| Announce | Make one piece of news known | Headline with the news, then when and where it applies, why it matters, CTA, brand | Front-load the news; date time-bound news | Inverted pyramid (Wikipedia: the most important information first, less vital details later); genres.md "Announcement" |
| Sell | Get a purchase or a click | Offer or product hero, one benefit, proof, price and conditions, CTA, legal line | Real reference prices for was/now claims; no invented urgency | AIDA, E. St. Elmo Lewis, 1910: "attract attention, maintain interest, arouse desire, get action"; genres.md "Promo / sale" |
| Teach or inform | Make something understood or remembered | Title that states the question, numbered steps or the key figure, one diagram or chart, the takeaway, a source line | Put the key words first; source and date on every statistic | NN/g F-pattern (put the most important points first; start headings with the words carrying most information); genres.md "Tip" and "Infographics" |
| Invite | Get people to attend | Who is hosting, what, when (date, time, time zone), where (venue or link), how to join (RSVP, ticket, QR), extras (dress code, price) | Unambiguous date with weekday and year; one way to respond | Wikipedia "Wedding invitation": hosts, request line, names, date and time, location, RSVP card; mailed five to eight weeks ahead; genres.md "Event" |
| Celebrate or commemorate | Mark an occasion with the audience | Greeting or occasion, honoree, one warm line, sender | Respect religious and cultural rules; keep offers separate | occasions.md; R7 |
| Brand or identity | Make the organisation recognisable | Name, logo, tagline, colours, type, imagery, voice, used consistently | Consistency across every piece | Wikipedia "Brand": a name, a design, images, a slogan, writing style, a font or a symbol that sets the brand apart |
| Recruit | Get the right people to apply | "We're hiring", role title, fact chips (place or remote, contract, pay range), two or three perks, how to apply, deadline | Pay range where the law requires it (EU Directive 2023/970, per R5); neutral job titles | genres.md "Hiring"; R5 |
| Fundraise | Get a donation | The need (who and what), what a gift does (a concrete unit), proof or credibility, the ask (amount and deadline), how to give (link or QR) | Honest numbers; a single ask | Heuristic, shaped like AIDA; no fundraising body's guidance was fetched |
| Compare | Help someone choose | The question, options as columns, the same attributes as rows, differences highlighted, a verdict | At most five items; consistent units | NN/g "Comparison Tables" (2024-02-09): "Use Comparison Tables for Up to 5 Items" |
| Warn or safety | Prevent harm | Signal word panel, the hazard, the consequence, how to avoid it, a pictogram | Colours by signal word (OSHA: danger in red, black and white; caution yellow with a black panel; safety instructions white with a green panel); ISO 7010 shapes (W yellow triangle, P red circle with a slash, M blue circle, E green rectangle, F red square); legible at the required distance | OSHA 29 CFR 1910.145 (tags: "a signal word and a major message", readable at 5 ft or more); Wikipedia "ISO 7010"; the ANSI Z535.4 layout was not fetched |
| Direct or wayfinding | Get people to a place | Where you are, the destination name, an arrow, the distance or time, then supporting information and rules | Character heights by distance (ADA 703.5); one destination per line | ADA 2010 Standards 703.5; the sign-type taxonomy (identification, directional, informational, regulatory) is common practice but was not verified this session |
| Entertain | Earn attention and a share | A hook in the first glance (surprise, question, contrast), the payoff (joke or reveal), a light brand mark | Keep the payoff readable at the viewing size | Heuristic; no source fetched |

---

## 8. Changes this research suggests for the skill

1. Add the 39 presets in `web.json`, keeping their `confidence` labels.
2. Keep the 11 px hard text floor, add a 12 px warning (Lighthouse) and a 360 px strict viewing width for text-critical phone graphics.
3. For distance-viewed pieces, compute the floor from distance: DISCAS (screens, distance / 200) and ADA 703.5.5 (signs); for slides use 1/30 of the slide height (18 pt on PowerPoint's 7.5-in slides) and the new `deck-16x9-room`.
4. Upgrade `x-card` from "unverified" to "official (archived 2025-05-31)": 2:1, minimum 300x157, maximum 4096x4096, under 5 MB, JPG/PNG/WEBP/GIF (first frame), no SVG.
5. `og-image` stays 1200x630 (Meta); add the WhatsApp weight note (under 300 KB, via Wix) or use `og-whatsapp`.
6. `email-header` (1200x400) and `email-hero` (1200x600) are sensible for 600 px templates (Klaviyo, Kit, Mailchimp legacy); Mailchimp's new builder wants 660-1320 px, hence `email-hero-660`. The official ceiling is 1 MB per image; the existing 200 KB is a stricter heuristic.
7. Add aliases to existing presets: HubSpot and Wix featured images use `og-image`; "Twitch VOD thumbnail" and "Facebook video thumbnail" use `video-thumb-16x9`; "webinar title slide" uses `deck-16x9-room`.

---

## Sources (read 2026-09-24/25 unless noted)

- ITU-R BT.1848-1 (10/2015), Safe areas of wide-screen 16:9 aspect ratio digital productions: https://www.itu.int/rec/R-REC-BT.1848
- EBU R 95 v1.1 (June 2017), Safe areas for 16:9 television production: https://tech.ebu.ch/docs/r/r095.pdf
- SMPTE ST 2046-1 landing page (title only): https://pub.smpte.org/pub/st2046-1/
- Apple, Final Cut Pro User Guide, Use overlays in the viewer: https://support.apple.com/guide/final-cut-pro/use-overlays-in-the-viewer-verded6d49d7/mac
- Apple HIG, Typography and Layout (layout page updated 2026-09-09): https://developer.apple.com/design/human-interface-guidelines/typography
- Android Developers, TV layouts: https://developer.android.com/design/ui/tv/guides/styles/layouts
- Google Lighthouse, legible font sizes (2019-05-02): https://developer.chrome.com/docs/lighthouse/seo/font-size
- W3C, WCAG 2.2: https://www.w3.org/TR/WCAG22/
- GOV.UK Design System, Type scale: https://design-system.service.gov.uk/styles/type-scale/
- StatCounter Global Stats, screen resolution, August 2026: https://gs.statcounter.com/screen-resolution-stats/mobile/worldwide and /desktop/worldwide
- AVIXA, DISCAS vocabulary and Basic Decision Making table: https://www.avixa.org/resources/display-image-size-calculators/learn-more-about-display-size
- Microsoft Support, Make your PowerPoint presentations accessible: https://support.microsoft.com/en-us/office/make-your-powerpoint-presentations-accessible-to-people-with-disabilities-6f7772b2-2f33-4bd2-8ca7-dae3b2b3ef25
- Microsoft Support, Change the size of your slides: https://support.microsoft.com/en-us/office/change-the-size-of-your-slides-040a811c-be43-40b9-8d04-0de5ed79987e
- US Access Board, ADA 2010 Standards, 703.5: https://www.access-board.gov/ada/
- OSHA 29 CFR 1910.145: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.145
- Wikipedia, Visual acuity; Retina display; AIDA (marketing); Inverted pyramid (journalism); Wedding invitation; Brand; ISO 7010: https://en.wikipedia.org/wiki/Visual_acuity (and the matching titles)
- Nielsen Norman Group, F-shaped pattern (2017-11-12, reviewed 2026-08-19): https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/ ; Comparison tables (2024-02-09): https://www.nngroup.com/articles/comparison-tables/
- Solopress, Supplying Artwork, Bleed, Resolution guides and Roller Banners: https://www.solopress.com/support-guides/supplying-artwork/
- Canva Help, resize, margins and bleed, print resolution, CMYK: https://www.canva.com/help/resize/ ; Canva Connect API: https://www.canva.dev/docs/connect/api-reference/designs/create-design/ ; Canva, design brief: https://www.canva.com/learn/effective-design-brief/
- Figma Help, Apply constraints: https://help.figma.com/hc/en-us/articles/360039957734
- Adobe HelpX, InDesign liquid page rules: https://helpx.adobe.com/indesign/desktop/layout-and-grid-tools/apply-layout-adjustments/liquid-page-rules-overview.html ; Adobe Express image resizer: https://www.adobe.com/express/feature/image/resize
- Google Ads Help, About responsive display ads: https://support.google.com/google-ads/answer/6363750
- Shopify Help, Uploading images (focal points, 20 MB, 20 MP): https://help.shopify.com/en/manual/online-store/images/theme-images
- Platform pages for sizes and weights are listed in each `web.json` entry's `source`.
- The skill's own research note R5 (2026-09-23) for Meta safe zones, IAB weights and print profiles.
