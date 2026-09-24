# Formats: the catalogue, and what to do when a size or a kind of design is unknown

Every deliverable starts from a canvas: a size, a safe zone, the platform's UI that covers part of it, the width or
distance people see it at, and the file limits. `presets.json` holds the ones researched so far (with a source, a
date and a confidence on each). This file says how to find one, and what to do when there is none: an unknown size,
an unknown platform, or a kind of design the skill has not made before. The research behind it is in
`references/research/formats-*.md` (2026-09-24).

## 1. Find the format first

```bash
python3 ~/.claude/skills/codex-design/scripts/design.py presets --find "pinterest pin"      # words people use, Banglish too
python3 ~/.claude/skills/codex-design/scripts/design.py presets --find "biye card"
python3 ~/.claude/skills/codex-design/scripts/design.py presets --id fb-cover               # one preset in full: notes, source
python3 ~/.claude/skills/codex-design/scripts/design.py presets --group ecommerce
python3 ~/.claude/skills/codex-design/scripts/design.py presets --nearest 1500x3000         # an unknown size: the closest ratios
```

- `--find` searches ids, labels, aliases (including Banglish such as "fb cover banano", "thumbnail banao"), platforms and
  notes, and ranks the exact phrase first.
- A retired format answers with its replacement: a "YouTube story" request gets `yt-shorts-frame` and `yt-post`
  (Stories closed on 2023-06-26); IGTV, LinkedIn Stories, Twitter Fleets, Idea Pins and the removed Meta placements
  do the same. Tell the client, and design the replacement.
- A typo in `--preset` gets "did you mean".
- Read the preset's `notes` before designing: they carry the crops and overlays (the 3:4 grid crop of a 4:5 post, the
  avatar over a cover, the duration badge on a thumbnail, the bottom 40 % of a Reels ad with a disclaimer).

## 2. The catalogue by family

`presets --group NAME` lists every id of a family; `presets --id ID` shows one in full. Counts as of 2026-09-24.

### 2.1 Common requests and where they land

| The request | Preset | Pattern | Watch for |
|---|---|---|---|
| Instagram post | `ig-portrait` (4:5, the default), `ig-square`, `ig-3x4` | `post-photo`, `post-type`, `card` | the profile grid shows posts cropped to 3:4 |
| Instagram or Facebook story, reel cover | `ig-story`, `vertical-safe`, `ig-reel-cover` | `story` | UI bands top and bottom; the reel cover is cropped to 3:4 on the grid |
| Carousel | `ig-carousel`, `li-doc` (PDF) | `carousel` | one idea per slide; nothing on the seams |
| Pinterest design | `pin-standard` (2:3), `pin-9x16`, `pin-square` | `pin` | taller than 2:3 gets cut in the feed |
| Blog post thumbnail, featured image | `blog-featured` (1200x675, safe for 3:2 and 1.91:1 crops), `og-image`, `article-hero` | `blog-featured` | the same file is the link card on every network |
| YouTube thumbnail | `yt-thumbnail` | `thumbnail` | the duration badge, bottom right |
| YouTube story | retired: `yt-shorts-frame` or `yt-post` | `story`, `post-type` | Stories closed on 2023-06-26; say so |
| Cover photo (a profile or page) | `fb-cover`, `li-profile-cover`, `li-company-cover`, `x-header`, `yt-banner`, `fb-group-cover`, `fb-event-cover` | `cover` | avatars and buttons cover part of it; phones crop the sides |
| Cover page (a report, proposal, assignment) | `report-cover-a4`, `report-cover-letter` | `book-cover` front, `poster` | a bound edge needs 12 mm more |
| E-book cover | `ebook-master` (1600x2560, passes every store), `ebook-kdp`, `ebook-kobo`, `ebook-d2d`, `ebook-bookbaby` | `book-cover` | the title must read about 94 px wide in search results |
| Print book cover | the wrap from `bookcover` (KDP, IngramSpark, Lulu; paperback or hardcover); `book-6x9` and the other trims for the front alone | `book-cover` | spine width from pages and paper; barcode box; spine text only above the page minimum |
| Magazine cover | `magazine-us`, `magazine-a4` | `poster` | masthead and main line in the top band (racks overlap covers) |
| E-commerce product image | `amazon-main` (product on white, nothing else), `amazon-secondary`, `shop-square`, `daraz-product`, `shopee-product`, `lazada-product`, `gmc-product` | `product-infographic` (secondary images only) | main images allow no text, badges or props |
| Store banner, A+ content | `amazon-store-hero`, `aplus-*`, `etsy-banner`, `shopee-shop-cover`, `lazada-store-*` | `cover` | desktop and app crop differently |
| Square banner | social: `ig-square`, `fb-square`; ads: `gads-square`; a website: `popup-square` | `post-type`, `ad-banner` | ask where it will run; social is the default |
| Web banner, hero, slider | `web-hero`, `web-hero-mobile`, `web-banner-3x1`, `promo-strip` | `cover` | text inside the centre crop of every breakpoint |
| Display ad | `iab-*`, `gads-*` | `ad-banner` | byte limits; `pack --format jpg` |
| App store screenshots | `appstore-iphone-69`, `play-phone-screenshot`, `play-feature-graphic` | `app-screenshot` | no prices, rankings or "download now" |
| Podcast, album, audiobook cover | `podcast-cover`, `album-cover`, `audiobook-cover` | `square-cover` | reads at 55 px |
| Poster, flyer, leaflet, handbill | `a3-poster`, `a4-flyer`, `a5-flyer`, `poster-demy` (Bangladesh), `poster-18x24` | `poster`, `flyer` | distance sets the type size (§3.4) |
| Brochure | `trifold-a4`, `trifold-letter`, `bifold-a4` | `brochure-trifold` | panels are printer-specific; colour across folds |
| Business or visiting card | `bc-us`, `bc-eu`, `visiting-card-bd` (Bangladesh) | `business-card` | shop sizes differ: confirm |
| Certificate | `certificate-a4-landscape`, `certificate-letter-landscape` | `certificate` | a frame near the trim shows drift |
| Invitation (wedding, biye card, dawat card, gaye holud) | `invite-5x7`, `invite-a5`, `invite-dl` | `invitation` | nothing under 8 pt; confirm local sizes |
| Greeting or Eid card | `greeting-a6-folded`, `greeting-5x7-folded` | `invitation` (front) | folds per side |
| T-shirt, hoodie, mug, sticker | `tshirt-merch-amazon`, `hoodie-*`, `mug-11oz`, `sticker-redbubble` | none; `post-type` for type-led art | transparent PNG (the preset sets it); no soft glows |
| Presentation | `deck-16x9`, `deck-16x9-room`, `deck-4x3` | `brand/guidelines` | 18 pt floor when projected |
| Calendar | `calendar-wall-a3`, `calendar-desk-a5`, `calendar-wall-bd-18x23` | `poster` | room for the hanger strip |
| Banner, PVC flex, X-banner, roll-up | `banner-3x6ft`, `pvc-banner-bd-3x4ft`, `pvc-banner-2000x1000`, `x-banner-60x160`, `rollup-850` | `sign` (landscape), `poster` (portrait: roll-ups, X-banners) | hems, grommets and stand zones; read from metres away |
| Festoon (Bangladesh) | `festoon-election-bd` (election rules), `pvc-banner-bd-3x4ft` (commercial) | `poster` | election pieces: black and white, size caps |
| Yard sign, A-frame, window, floor | `yard-sign-24x18`, `a-frame-insert-24x36`, `a-board-a1`, `window-cling-900x600`, `floor-decal-24in` | `poster` | read from a car or across a pavement |
| Billboard, bus side | `billboard-us-bulletin`, `billboard-uk-48sheet`, `billboard-bd-20x10ft`, `transit-bus-king` | `sign` | files at a scale (`file_scale`); 7 words; legibility index 30 |
| Digital signage, menu board, LED wall | `signage-1080p`, `signage-1080p-portrait`, `signage-4k`, `signage-d6`, `led-wall-16x9-p2.6` | `sign` (landscape), `poster` (portrait) | the text floor follows the distance and the screen height |
| Trade show, event backdrop | `step-repeat-8x8ft`, `popup-10ft-straight`, `table-throw-6ft` | `sign`, `poster` | logos at head height; nothing on panel breaks |

### 2.2 The families

| Family (`--group`) | Count | What it covers |
|---|---|---|
| social | 146 | Instagram, Facebook, Threads, WhatsApp, LinkedIn, X, YouTube, TikTok, Pinterest, Snapchat, Bluesky, Mastodon; creator and community (Twitch, Kick, Discord, Reddit, Tumblr); regional (Telegram, Viber, LINE, Kakao, WeChat, Weibo, Xiaohongshu, Douyin, VK); Google Business Profile; profile photos, covers, highlights, ads per placement |
| print | 98 | posters (ISO, US, demy and crown), flyers, postcards, invitations, greeting cards, letterheads, envelopes, notepads, ID cards and badges, tickets and vouchers, business cards, bookmarks, table tents, hang tags, door hangers, stickers and labels, roll-up |
| ecommerce | 71 | Amazon (main, secondary, A+, Store, Sponsored Brands), eBay, Etsy, Shopify, WooCommerce, Google Merchant, Meta catalogue, TikTok Shop, Daraz, Lazada, Shopee, Tokopedia, noon, Mercado Libre, Allegro, Myntra; creator stores and courses (Gumroad, Patreon, Ko-fi, Kickstarter, Udemy, Teachable, Thinkific, Skillshare) |
| web | 39 | link cards (Open Graph, X, WhatsApp), heroes and banners, pop-ups, favicons and app icons, portfolio sites (Behance, Dribbble, ArtStation), newsletters (Substack), events (Eventbrite, Meetup, Luma) |
| app | 38 | App Store, Google Play, Microsoft Store, Chrome Web Store, Product Hunt, Steam |
| document | 22 | slides, A4 pages, report covers, calendars, CVs, academic posters, zines |
| publishing | 18 | e-book covers, print book fronts (wraps come from `bookcover`), magazine covers |
| merch | 16 | t-shirts, hoodies, mugs, totes, phone cases, pillows, tumblers, caps, stickers (print-on-demand files) |
| audio | 10 | Spotify, Apple Music, SoundCloud, album, audiobook, podcast pages |
| ads | 9 | IAB display units, Google responsive display (Meta, LinkedIn, X, TikTok and Pinterest ads live under social) |
| video | 9 | thumbnails, lower thirds, title cards, stream overlays, podcast video, meeting backgrounds |
| email | 3 | email hero, two-up columns, animated hero |
| signage | 47 | yard signs, A-frames, vinyl and PVC banners, roll-ups, X-banners, festoons, billboards (US, UK, Bangladesh; scaled files), bus sides and rears, window clings, floor decals, step-and-repeat, pop-up walls, table throws, digital signage and LED walls |

Retired formats answer with their replacement: YouTube Stories, IGTV covers, LinkedIn Stories, Twitter Fleets,
Pinterest Idea Pins, the Messenger inbox and story ads, Instagram Explore ads and Facebook video feed ads.

## 3. When the size or the platform is unknown

### 3.1 The spec ladder

Climb until a rung gives real numbers; stop there, and write down the source, the date and how sure it is.

| Rung | What to do |
|---|---|
| 1. The platform's own spec page | Help centre, ads guide or developer docs of the surface where the design will live. An archived official page beats a current blog. Official text and the live page can disagree (Facebook's help says 16:9 for covers; they render 2.70:1): when they do, measure (rung 4) and note both. |
| 2. The printer's template or dieline | For anything folded, bound, die-cut, large format or packaged, ask the print shop for its template before designing. A template beats every generic number. |
| 3. The client's existing assets | Last year's file of the same item, the brand guidelines, the logo files: measure and match them. |
| 4. Measure the live surface | Open the real page at a phone width (390 CSS px) and a desktop width (1440), read the slot's rendered box, its `object-fit` crop and every overlay (badges, avatars, buttons, the like rail), screenshot it and date it: UIs change and run tests. The built-in browser does this. |
| 5. The device's screen | Viewport and layout statistics (§3.3). |
| 6. First principles | Only now: §3.3 for screens, §3.4 for print. Label the result a heuristic. |

When two rungs disagree, the higher one wins and the disagreement goes into the preset's notes.

### 3.2 Record it, then render

- **A verified spec becomes a preset** in the project's (or the client's) preset file, never a one-off `--size`:

  ```json
  {"presets": [
   {"id": "acme-kiosk-portrait", "group": "signage", "label": "Acme mall kiosk, portrait",
    "w": 1080, "h": 1920, "safe": [96, 60, 96, 60], "keepout": [[0, 1760, 1080, 1920]],
    "view_distance_m": 2.5, "screen_height_m": 1.2, "aliases": ["acme kiosk"],
    "source": "Acme signage spec sheet v3 (client email 2026-09-20)", "verified": "2026-09-24",
    "confidence": "client spec", "notes": "The bottom 160 px shows the mall's ticker."}
  ]}
  ```

  `render --preset acme-kiosk-portrait --preset-file clients/acme/presets.json …`, or set `CODEX_DESIGN_PRESETS` to the
  file so every command sees it. A project preset with the id of a skill preset replaces it (a client's correction).
  Presets can pass their own CSS variables (`"css_vars": {"--spine-w": "0.54in"}`) for wraps, dielines and panels.
- **No spec and no time to find one:** `render --size WxH` and give what you do know: `--safe` (px, mm for print, or
  a share such as `5%`), `--keepout x0,y0,x1,y1` (repeatable), `--view-width` (CSS px where it is seen),
  `--view-distance` (metres, for signs and screens across a room) with `--screen-height`, and `--min-text`. Whatever is
  missing is assumed and **stated** in the report (`canvas.assumed`) and as a warning: a 5 % safe margin, a 390 px
  phone viewing width, an 11 px floor there; for print, no bleed. Tell the client which numbers were assumed.
- `--size` alone names the presets of that size (they carry a platform's safe zone), and `presets --nearest` lists the
  closest ratios: borrow the nearest preset's safe zone and pattern.

### 3.3 First principles for a screen

- **Ratio family by where it is seen:** 1:1 square feeds, icons, avatars, podcast art; 4:5 portrait feed posts (the
  most reusable master: Instagram, Facebook, Threads, LinkedIn); 3:4 the Instagram grid; 2:3 Pinterest; 9:16 stories,
  reels, Shorts, TikTok, WhatsApp Status, full-screen phone; 16:9 video, TV, slides, thumbnails, meeting backgrounds;
  1.91:1 link previews and landscape ads; 2:1 X large cards and email heroes; 3:1 headers and section banners; 4:1
  LinkedIn and Etsy banners. Unsure: pick the likeliest surface and add its neighbour as an adaptation (§5).
- **Canvas pixels:** the width it occupies in CSS px times 2 for web and email (a 600 px email image is 1200 px);
  respect platform caps (WordPress scales above 2560; X accepts up to 4096).
- **Safe margins:** 5 % of the short side for an unknown screen graphic; for video frames the broadcast title-safe
  area is the inner 90 % (5 % per edge) and action-safe the inner 93 % (ITU-R BT.1848-1, EBU R 95); for an unknown
  `object-fit: cover` box, keep the subject inside the intersection of the centre crops of every likely ratio.
- **Viewing width:** a phone feed about 390 CSS px (360 when every word must read); a desktop content column 600 to 800;
  thumbnails 168 to 375; podcast and app art 55 to 180; X, Threads and Bluesky images about 310.
- **Text floor at viewing size:** 11 px hard floor (Apple HIG), 12 px where most text is small (Lighthouse), 16 px for
  sentence-length copy; on the canvas: `floor x canvas width / viewing width`. A 1080 post seen at 390 needs 30.5 px;
  a 1280 thumbnail seen at 200 needs 70 px.
- **Screens across a room** (menu boards, signage, kiosks, projected slides): the floor follows the distance, not a
  phone: characters at least the farthest viewer's distance / 200 tall (AVIXA DISCAS). `--view-distance 4
  --screen-height 0.68` works it out (45 px on a 1080-high screen). Projected slides: 18 pt, 1/30 of the slide height
  (36 px on 1080): `deck-16x9-room`.
- **Contrast:** 4.5:1 for text, 3:1 for large text (24 px, or 18.7 px bold, at viewing size) and for graphics
  (WCAG 2.2).
- **File weight:** the platform's limit when one exists; email images under 1 MB (200 KB is kinder); WhatsApp link
  previews under 300 KB.

### 3.4 First principles for print

- **Bleed:** 3 mm per edge for cards, flyers, leaflets and booklets (0.125 in for US printers), about 6 mm on large
  posters and some die-cuts; banners, roll-ups, fabric and signs follow the stand's or printer's template (bases,
  hems, eyelets); office printing has none (keep 5 mm from the edge).
- **Safe margin:** 3 to 5 mm on cards and flyers, 10 mm or more on posters, more on anything hung or read across a
  room; double it beside folds and bindings.
- **Resolution:** 300 ppi in hand; from a distance, `ppi = 87.3 / metres` (0.5 m 175, 1 m 87, 2 m 44, 5 m 17, never
  under 10: billboards print at 12.5 to 45): the renderer checks placed images against it when the preset or
  `--view-distance` gives a distance (times the file scale for a scaled billboard file), and against the preset's own
  figure in hand (posters and roll-ups 150). Many printers still ask for 300 ppi whatever the size: their minimum
  wins. Big print goes through the vector PDF.
- **Text by distance, on foot (posters, banners, festoons, A-frames, wayfinding):** capitals 16 mm up to 1.83 m, plus
  10.5 mm per metre beyond (ADA 2010 §703.5.5); font size is about capitals / 0.7. `--view-distance` sets the floor: a
  banner read at 5 m needs capitals of about 49 mm (70 mm type).
- **Text by distance, in passing (billboards, bus sides, roadside screens, yard signs read from a car):** capitals =
  distance / legibility index, 30 on average (USSC, MUTCD: 2.78 mm per metre; 25 or 20 on busy streets):
  `--legibility-index 30`. A bulletin read from 152 m needs capitals of about 422 mm.
- **Scaled files:** billboards and bus sides are supplied at a scale the media owner sets (1/2 in = 1 ft is 1:24, a
  10 % file is 1:10): `--file-scale 24` makes the floor and the image check work at the real size (a 300 ppi file at
  1:24 prints at 12.5 ppi, which is what billboards use).
- **Colour:** deliver what the printer asks for; most take the RGB PDF and convert, some want CMYK (`--cmyk`, with
  their ICC profile). Special finishes (foil, spot UV) go on a separate page or layer.
- **Ask the printer:** the product and trim size and whether there is a template or dieline; bleed and safe margin
  (binding, hems, base); file format and colour (PDF/X, ICC, ink limit, RGB accepted?); minimum resolution; proof
  method and deadline.

### 3.5 The four questions (and the defaults)

Ask at most these, once; without answers, apply the defaults and say so.

| Question | Default |
|---|---|
| Where will people see it? (platform and placement; for print, the printer and product) | Screen: a 1080x1350 master (4:5 feed), adapted to 9:16 and 1.91:1 on request. Print without a printer: A4 (US Letter in the US and Canada), 3 mm bleed, 3 to 5 mm safe, 300 ppi. The paper size follows the client's market. |
| What should someone do or know after three seconds? | The archetype the content implies (§4): one message, one call to action. |
| What must it say or show, exactly? | Only the facts supplied; marked placeholders for anything missing; never an invented date, price, name, review or number. |
| Who is it for, and are there brand rules or past examples? | The audience's language and script; neutral legible type; ask for a vector logo. |

## 4. When the kind of design is unknown

Map it onto a proven structure by its **job**, the main verb of the brief. When two apply, the one that carries the
call to action wins: an Eid sale is **sell** with celebratory styling; a webinar is **invite**; a new branch is
**announce**, then **invite**.

| Archetype | Anatomy, in order of prominence | Must-haves and traps | Closest playbook and pattern |
|---|---|---|---|
| Announce | the news as the headline; when and where it applies; why it matters; CTA; brand | front-load the news; date anything time-bound | `genres.md` §1 announcement; `post-type.html` (v-announce) |
| Sell | offer or product hero; one benefit; proof; price and conditions; CTA; legal line | real reference prices for was/now; no invented urgency | §1 promo, §10 e-commerce; `post-product.html`, `product-infographic.html`, `ad-banner.html` |
| Teach or inform | the question as the title; numbered steps or the key figure; one diagram or chart; the takeaway; source line | key words first; source and date on every number | §1 tip, §8 infographics; `card.html`, `infographic.html`, `pin.html`, `carousel.html` |
| Invite | who hosts; what; when (weekday, date, time, time zone); where (venue or link); how to join (RSVP, ticket, QR); extras | an unambiguous date; one way to respond | §1 event, §6 posters; `post-type.html` (v-event), `poster.html`, `flyer.html`, `invitation.html` |
| Celebrate or commemorate | the occasion; the honoree; one warm line; the sender | the day's tone class and customs; offers stay separate | `occasions.md`; `day-post.html`, `day-solemn.html` |
| Brand or identity | name, logo, tagline, colours, type, imagery, voice, used consistently | consistency across every piece | `brand.md`; `brand/guidelines.html`, `cover.html` |
| Recruit | "we're hiring"; role title; fact chips (place or remote, contract, pay range); two or three perks; how to apply; deadline | pay range where the law requires it; neutral titles | §1 hiring; `post-type.html` (v-hiring) |
| Fundraise | the need (who and what); what one gift does (a concrete unit); proof; the ask (amount, deadline); how to give (link or QR) | honest numbers; a single ask | `post-type.html`, `poster.html` |
| Compare | the question; options as columns; the same attributes as rows; the differences marked; a verdict | at most five options; consistent units | `infographic.html`, `card.html` (v-stat) |
| Warn or safety | signal word panel; the hazard; the consequence; how to avoid it; a pictogram | signal-word colours (danger red, caution yellow, notice blue, safety green) and ISO 7010 shapes; legible at the required distance | `poster.html` with `--view-distance` |
| Direct or wayfinding | where you are; the destination; an arrow; distance or time; supporting rules | character heights by distance (§3.4); one destination per line | `sign.html` or `poster.html` on a signage preset (its distance sets the floor) |
| Entertain | a hook at first glance (surprise, question, contrast); the payoff; a light brand mark | the payoff readable at viewing size | `post-type.html`, `thumbnail.html`, `carousel.html` |

Then write the direction contract (SKILL.md step 3), pick the closest pattern, and judge it with a `--kind` that names
the real deliverable ("mall kiosk screen, portrait, read at 2.5 m").

### 4.1 An unfamiliar topic, industry or audience

1. **Learn the category first** (minutes for a post, longer for a brand): what a customer must know to act; the words
   the audience itself uses (the client's site, reviews, competitors' pages, local forums); three to five real pieces
   from that market, to read its visual codes (colour, photography, type, density). Then decide on purpose: follow the
   codes where trust decides (health, finance, law, education), break one of them where the category is crowded. Never
   copy an example.
2. **Regulated or sensitive topics change the design** before any style does: health, beauty and finance (no cure,
   guarantee or "risk-free" words, no generated before and after, risk warnings where the law asks); alcohol, tobacco,
   gambling and weapons (read the platform's ad policy before designing: several refuse them or need age targeting);
   politics and elections (stop and escalate; Bangladesh's 2025 and 2026 election codes ban posters, cap festoon,
   banner, billboard and leaflet sizes, and allow black and white only: `research/formats-print.md`); religion and sacred text (`occasions.md` §1.4); children
   (no pressure copy); medicines (local advertising law). Safe defaults: `occasions.md` §2.
3. **Style by industry**, then check it against the brief (from `research/R10-trends-preferences-2026.md` §5.2 and §6;
   the ten directions are in `styles.md`):

| Industry | Lead with | Avoid |
|---|---|---|
| Food and cafés | real food with people, direct flash at night or daylight, handwriting, scrapbook | AI food, identical plate grids |
| Beauty and salons | neo-minimal with real skin, liquid italics for young audiences | AI skin, clone "clean girl" looks |
| Health and dental | calm, claim-first layouts with one warm accent; the real team and rooms | AI people, stock smiles |
| Real estate | editorial magazine grids, ambient photos, address-level facts | HDR, AI-staged rooms, template "just sold" |
| Education and coaching | editorial or notes-app carousels, one idea per slide, a mascot or a face | walls of text, lightbulb clichés |
| Events and nightlife | maximalist type-led posters, direct flash, ticket-stub frames | glass, gradients, chrome |
| Fashion | direct flash, controlled chaos, liquid italics | beige clone minimalism |
| Fitness | real bodies in motion, condensed or oversized type | AI-perfect bodies |
| Retail and e-commerce | the product as the star, one loud move on a quiet grid | starbursts, fake scarcity |
| B2B, SaaS, finance | editorial and data-proof layouts, hand-made illustration, restrained colour | AI sparkle, glowing brains, 3D blobs |

4. **The audience decides the language and the register**, never the requester: a Dhaka agency designing for a
   Toronto clinic writes Canadian English; a Bangladeshi audience gets natural Bangladeshi Bengali (`copy.md`).

## 5. One master into many sizes

- Let `r` be the larger of the two ratios divided by the smaller. **Crop or extend the background** when `r` is at
  most 1.25, the orientation stays, and every text block and logo already sits inside both safe zones (4:5 to 1:1,
  16:9 to 1.91:1). **Re-compose** when `r` is above 1.25, portrait becomes landscape, the new viewing width pushes text
  under the floor (a feed post into a 200 px thumbnail), or the new platform adds overlays (9:16 UI bands).
- In the adaptation: the photo re-crops around its focal point (extend it rather than cut the subject; never stretch);
  the logo stays in the same corner inside the safe zone, sized from the short side; the headline reflows and keeps
  the floor; the CTA stays above the platform's bottom band; a legal line keeps its size or moves into the caption,
  alt text or HTML; secondary elements go before primary ones shrink.
- One responsive HTML with `html[data-preset=…]` rules and `pack --presets …` does this; judge the master and look at
  every adaptation (the checks run on each).
- **Pictures for an unusual ratio:** codex-imagegen makes plates in 12 aspects (1:1, 3:2, 2:3, 4:3, 3:4, 4:5, 5:4,
  16:9, 9:16, 21:9, 3:1, 1:3). Take the nearest, reserve the text zone, and let the page crop it (`object-fit: cover`
  around the subject) or extend it in CSS; beyond 3:1 (a bulletin, a bus side, a page banner) generate at 3:1 or
  narrower and extend the ground, or give the picture only part of the canvas, as `sign.html` does
  (`ai-visuals.md`).

## 6. Delivering an unknown format

What to hand over, by where it goes:

| Destination | File | Notes |
|---|---|---|
| A screen (social, web, app, email) | PNG at the exact pixel size, sRGB; JPG or WebP when the platform has a byte limit (`--max-bytes`) or recompresses anyway | a 2x export for web and email slots |
| Print, small or large | vector PDF at trim plus bleed, fonts embedded, with `--preview` for the client; `--cmyk` only when the printer refuses RGB | the printer's own template wins; large format keeps images at `87.3 / metres` ppi or better |
| Merch | transparent PNG at the platform's pixel size (the merch presets set transparency) | full-print products run the ground to the edge |
| E-book and store listings | JPG, sRGB, under the store's limit (KDP under 5 MB, most stores 2 MB) | no border except KDP's grey keyline on white covers |
| Unknown | PNG and a vector PDF, both at the stated size | ask which one they need, and say what was assumed |

The delivery note (`deliver`) states the spec's source and confidence for any preset that was not official, and the
assumptions of a `--size` render: tell the client which numbers to confirm. Keep the project's preset file with the
source files: the next piece for that client starts from it.
