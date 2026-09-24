# Canva and Adobe Express design-type catalogue: a gap checklist

Compiled 2026-09-24 for the HTML/CSS design skill. It lists the design types Canva and Adobe Express offer, with the size each one uses, and marks each against the 84 presets in `existing-ids.txt` and the 39 new presets proposed in `web.json`.

## How this was collected

- **Canva design types (section 1).** Canva's public template library has 217 English category pages (from `https://www.canva.com/landing_page_sitemap_1.xml` and `https://sitemap.canva.com/sitemap_index.xml`). For each category the first two templates were opened and the `Dimensions` field Canva shows on the template page was read (for example the template page for an Instagram Post shows `1080 × 1350 px`, Portrait). Where the two templates differed, both are given. These are the sizes Canva's own templates use, which normally equals the design type's default. They are not the logged-in "Create a design" menu, which could not be read without an account. Read in a browser session on 2026-09-24/25, paced to respect Canva's rate limit.
- **Canva size guide (section 2).** The tables on `https://www.canva.com/sizes/` and its 32 sub-pages (Canva's "Design Wiki").
- **Canva create pages (section 3).** Size sentences found in the FAQ text of 46 of Canva's 318 `canva.com/create/...` pages.
- **Canva limits (section 4).** Canva Help `resize` and `margins-bleed-crop-marks`, and the Canva Connect API reference.
- **Adobe Express (section 5).** Adobe's size guides (`adobe.com/express/discover/sizes/...`, only five exist), the size sentences on 39 of its 96 `adobe.com/express/create/...` pages, and the print product pages. Adobe's in-editor preset list needs an account and was not read.

**Coverage legend.** `covered: id` means an existing preset has the same size (or 2x of it) for the same use. `covered by size` or `covered by ratio` means a preset of the same size or aspect exists for a different use, which the skill can reuse. `new: id` means a preset in `web.json`. `partial` means the size exists but a feature (fold, die line, binding, UI zone) is not modelled. `MISSING` is a gap. `out of scope` means video timelines, live documents, whiteboards, websites or merchandise that need a vendor's product template.

Canva's own values are reproduced as Canva states them, units included; a few are outdated or contain typos, flagged in section 8.

## 1. Canva design types, sampled from Canva's template library (217 categories)

| # | Canva category (URL slug) | Design type as Canva names it | Size on Canva's template page | Orientation | Coverage |
|---|---|---|---|---|---|
| 1 | `academic-poster-uk` | Poster / Poster | 594 × 420 mm / 42 × 59.4 cm | Landscape / Portrait | covered: a2-poster (rotate for landscape) |
| 2 | `album-covers` | Album Cover | 1400 × 1400 px | Square | MISSING: music cover 1:1 (podcast-cover is the nearest) |
| 3 | `amazon-product-images` | Amazon Product Image | 1080 × 1080 px | Square | covered by ratio: shop-square |
| 4 | `amazon-sponsored-brands-video` | Amazon Sponsored Brands video | 1920 × 1080 px | Landscape | out of scope (video); frames: title-card-1080 (new) |
| 5 | `animated-logos` | Animated Logo | 500 × 500 px | Square | out of scope (animation); logo masters are MISSING as a preset |
| 6 | `animated-social-media` | Animated Social Media | 1080 × 1080 px | Square | covered (static frame): ig-square |
| 7 | `announcements` | Announcement | 105 × 148 mm | Portrait | covered: a6-flyer |
| 8 | `avatars` | Avatar | 1080 × 1080 px | Square | MISSING: profile / avatar with circle crop |
| 9 | `baby-shower-invitations` | Invitation | 105 × 148 mm | Portrait | covered: a6-flyer; MISSING: 5x7 in card |
| 10 | `banners` | Banner | 1000 × 500 mm | Landscape | MISSING: large-format vinyl banner (hems, eyelets) |
| 11 | `bi-fold-brochures` | Bifold Brochure | 297 × 210 mm | Landscape | covered: bifold-a4 |
| 12 | `billboard-ads` | Billboard | 2592 × 864 px | Landscape | MISSING: billboard / digital out-of-home |
| 13 | `bingo-card` | Bingo Card | 5 × 7 in | Portrait | MISSING: 5x7 in card |
| 14 | `blog-banners` | Blog Banner | 2240 × 1260 px | Landscape | covered by ratio: article-hero (16:9) |
| 15 | `blog-graphics` | Blog Graphic | 800 × 1200 px | Portrait | covered by ratio: pin-standard (2:3) |
| 16 | `book-covers` | Book Cover | 1410 × 2250 px | Portrait | MISSING: book / ebook cover |
| 17 | `booklets` | Booklet | 14.8 × 21 cm | Portrait | partial: a5-flyer (single page); MISSING: booklet imposition and creep |
| 18 | `bookmarks` | Bookmark | 2 × 6 in | Portrait | MISSING: bookmark 2x6 in |
| 19 | `bound-documents` | Bound Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 20 | `brochures` | Brochure | 297 × 210 mm | Landscape | covered: trifold-a4 |
| 21 | `bumper-stickers` | Bumper Sticker | 11 × 3 in | Landscape | MISSING: sticker / die-cut |
| 22 | `business-cards` | Business Card | 3.5 × 2 in | Landscape | covered: bc-us |
| 23 | `calendars` | Calendar | 1920 × 1080 px | Landscape | covered by size: deck-16x9 (digital); print calendars MISSING |
| 24 | `canvas-prints` | Canvas Print | 16 × 20 in | Portrait | MISSING: wall art / canvas wrap |
| 25 | `cards` | Card | 14.8 × 10.5 cm | Landscape | covered by size: a6-flyer (landscape) |
| 26 | `certificates` | Certificate | 297 × 210 mm | Landscape | new: deck-a4-landscape (A4 landscape); US Letter landscape MISSING |
| 27 | `checklists` | Checklist | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 28 | `christmas-cards` | Card | 105 × 148 mm / 14.8 × 10.5 cm | Portrait / Landscape | covered by size: a6-flyer |
| 29 | `class-schedules` | Class Schedule | 29.7 × 21 cm | Landscape | new: deck-a4-landscape |
| 30 | `classroom-banners` | Classroom Banner | 96 × 24 in | Landscape | MISSING: large-format banner 96x24 in |
| 31 | `coasters` | Coaster | 9.5 × 9.5 cm | Square | out of scope (product template) |
| 32 | `code` | Doc / Presentation | Auto size / 1920 × 1080 px | Unbounded / Landscape | out of scope (Canva Code / Docs) |
| 33 | `coloring-pages` | Coloring Page | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 34 | `comic-strips` | Comic Strip | 25 × 20 cm | Landscape | MISSING: comic strip 25x20 cm |
| 35 | `compliment-slips` | With Compliments Slip | 210 × 99 mm | Landscape | covered by size: dl-flyer (landscape) |
| 36 | `coupons` | Coupon | 21 × 29.7 cm | Portrait | covered by size: a4-doc; coupon strip 2.5x6 in MISSING |
| 37 | `cover-pages` | Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 38 | `decals` | Decal | 12 × 12 in | Square | MISSING: sticker / decal |
| 39 | `desktop-wallpapers` | Desktop Wallpaper | 1920 × 1080 px | Landscape | covered by size: web-hero / deck-16x9 |
| 40 | `diaries` | Diary | 8.5 × 11 in | Portrait | covered by size: letter-flyer |
| 41 | `digital-notebook-covers` | Digital Notebook Cover | 1365 × 1764 px | Portrait | MISSING: digital notebook cover |
| 42 | `docs` | Doc | Auto size | Unbounded | out of scope (Canva Docs) |
| 43 | `documents` | Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 44 | `ebook-covers` | Ebook Cover | 512 × 800 px | Portrait | MISSING: ebook cover |
| 45 | `ecards` | eCard | 14.8 × 10.5 cm | Landscape | covered by size: a6-flyer |
| 46 | `email-headers` | Email Header | 600 × 200 px | Landscape | covered: email-header (1200x400 = 600x200 at 2x) |
| 47 | `email-newsletters` | Email Newsletter | 794 × 1123 px | Portrait | out of scope (HTML email); image slots: email-hero, email-column-2up (new) |
| 48 | `email-signatures` | Email Signature | 400 × 200 px | Landscape | MISSING: email signature banner |
| 49 | `emails` | Email | Auto size | Unbounded | out of scope (Canva Email builder) |
| 50 | `envelopes` | Envelope (8.875 x 3.875 in) / Envelope DL | size in the type name; DL not captured | Landscape | MISSING: envelopes (printer template) |
| 51 | `exit-tickets` | Exit Ticket | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 52 | `facebook-ads` | Facebook Ad | 1200 × 628 px | Landscape | covered by size: gads-landscape; Meta recommends meta-ad-feed |
| 53 | `facebook-app-ads` | Facebook Post | 1200 × 630 px | Landscape | covered: og-image (1200x630) |
| 54 | `facebook-covers` | Facebook Cover | 851 × 315 px | Landscape | covered: fb-cover (1702x630 = 851x315 at 2x) |
| 55 | `facebook-event-covers` | Facebook Event Cover | 1920 × 1080 px | Landscape | covered: fb-event-cover (Canva template is 1920x1080, its size guide says 1920x1005) |
| 56 | `facebook-posts` | Facebook Post | 940 × 788 px | Landscape | covered by ratio: fb-square / fb-feed (940x788 is a legacy size) |
| 57 | `facebook-profile-frames` | Facebook Profile Frame | 1500 × 1500 px | Square | MISSING: profile frame (circle overlay) |
| 58 | `facebook-shops-ads` | Facebook Shops Ad | 1200 × 628 px | Landscape | covered by size: gads-landscape |
| 59 | `facebook-shops-covers` | Facebook Shops Cover | 1024 × 1024 px | Square | covered by ratio: fb-square |
| 60 | `facebook-stories` | Your Story | 1080 × 1920 px | Portrait | covered: ig-story / vertical-safe |
| 61 | `facebook-videos` | Facebook Video | 1080 × 1080 px | Square | covered (static frame): fb-square |
| 62 | `feed-ad-videos` | Feed Ad Video | 1080 × 1350 px | Portrait | covered (static frame): fb-feed / meta-ad-feed |
| 63 | `feed-ads` | Feed Ad (Square) | 1080 × 1080 px | Square | covered: ig-square / fb-square |
| 64 | `flags` | Flag | 18 × 12 in | Landscape | MISSING: flag (large format) |
| 65 | `flashcards` | Flashcard | 29.7 × 21 cm | Landscape | new: deck-a4-landscape (size) |
| 66 | `floor-decals` | Decal | 12 × 12 in | Square | MISSING: sticker / decal |
| 67 | `flyers` | Flyer | 210 × 297 mm | Portrait | covered: a4-flyer |
| 68 | `folded-cards` | Folded Card | 21 × 14.8 cm | Landscape | partial: a5-flyer (size); MISSING: folded card with fold line |
| 69 | `folder-labels` | Folder Label | 210 × 297 mm | Portrait | covered by size: a4-doc |
| 70 | `framed-arts` | Framed Art | 59.4 × 84.1 cm | Portrait | covered by size: a1-poster |
| 71 | `gift-certificates` | Gift Certificate | 14.8 × 10.5 cm | Landscape | covered by size: a6-flyer; 8x3.75 in gift certificate MISSING |
| 72 | `graphic-organizers` | Graphic Organizer | 29.7 × 21 cm | Landscape | new: deck-a4-landscape (size) |
| 73 | `graphs` | Graph | 1024 × 768 px | Landscape | new: deck-4x3 (1024x768) |
| 74 | `hoodies` | Hoodie | 355 × 290 mm | Landscape | out of scope (apparel print template) |
| 75 | `id-cards` | ID Card | 50 × 85 mm | Portrait | MISSING: ID card (ISO/IEC 7810 ID-1) |
| 76 | `infographics` | Infographic | 800 × 2000 px | Portrait | MISSING: tall infographic 800x2000 (pin-standard / ig-portrait are the nearest) |
| 77 | `instagram-posts` | Instagram Post | 1080 × 1350 px | Portrait | covered: ig-portrait |
| 78 | `instagram-reels` | Mobile Video | 1080 × 1920 px | Portrait | covered (static frame): vertical-safe / tiktok |
| 79 | `instagram-stories-videos` | Instagram Story Video | 1080 × 1920 px | Portrait | covered: ig-story |
| 80 | `instagram-stories` | Your Story | 1080 × 1920 px | Portrait | covered: ig-story |
| 81 | `invitations` | Invitation | 105 × 148 mm | Portrait | covered: a6-flyer; MISSING: 5x7 in invitation |
| 82 | `invoice` | Invoice | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 83 | `ios` | iOS Icon | 1024 × 1024 px | Square | new: app-icon-1024 |
| 84 | `journals` | Journal | 8.5 × 11 in | Portrait | covered by size: letter-flyer |
| 85 | `labels` | Label | 6 × 4 in | Landscape | covered by size: postcard-4x6 (landscape); die-cut labels MISSING |
| 86 | `lemon8-posts` | Lemon8 Post | 3000 × 4000 px | Portrait | covered by ratio: ig-3x4 |
| 87 | `lesson-plans` | Lesson Plan | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 88 | `lessons` | Presentation | 1920 × 1080 px | Landscape | covered: deck-16x9 |
| 89 | `letterheads` | Letterhead | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 90 | `letters` | Letter | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 91 | `linkedin-banners` | LinkedIn Background Photo | 1584 × 396 px | Landscape | covered: li-profile-cover |
| 92 | `linkedin-carousel` | LinkedIn Carousel | 1200 × 1500 px | Portrait | covered by ratio: li-doc (4:5) |
| 93 | `linkedin-posts` | LinkedIn Post | 1200 × 1200 px | Square | covered: li-square |
| 94 | `linkedin-video-ads` | LinkedIn Video Ad | 1920 × 1920 px | Square | covered by ratio: li-square (static) |
| 95 | `lists` | List | 1080 × 1920 px | Portrait | covered: ig-story / vertical-safe |
| 96 | `logos` | Logo | 2000 × 2000 px | Square | MISSING: logo master (square) |
| 97 | `magazine-covers` | Magazine Cover | 21 × 29.7 cm | Portrait | covered by size: a4-doc (cover furniture MISSING) |
| 98 | `magnets` | Magnet | 6 × 4 in | Landscape | covered by size: postcard-4x6 |
| 99 | `mailing-labels` | Mailing Label | 1.8 × 0.5 in | Landscape | MISSING: mailing label |
| 100 | `maps` | Map | 1600 × 900 px | Landscape | covered by size: x-post (1600x900) |
| 101 | `media-kits` | Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 102 | `meet-the-student-teacher` | Meet the Student or Teacher | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 103 | `memes` | Meme | 1080 × 1080 px | Square | covered: ig-square |
| 104 | `memos` | Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 105 | `menus` | Menu | 21 × 29.7 cm | Portrait | covered: menu-a4 |
| 106 | `microsoft-teams-backgrounds` | Microsoft Teams Background | 1920 × 1080 px | Landscape | new: virtual-bg |
| 107 | `mind-maps` | Brainstorm | 1920 × 1080 px | Landscape | out of scope (whiteboard); deck-16x9 by size |
| 108 | `mobile-first-presentations` | Presentation | 1920 × 1080 px | Landscape | covered: deck-16x9 |
| 109 | `mobile-videos` | Mobile Video | 1080 × 1920 px | Portrait | covered (static frame): vertical-safe |
| 110 | `mouse-pads` | Mouse Pad | 9 × 7.5 in | Landscape | out of scope (product template) |
| 111 | `mugs` | Mug | 3.3 × 3.3 in | Landscape | out of scope (product template) |
| 112 | `newsletters` | Newsletter | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 113 | `note-cards` | Note Card | 148 × 105 mm | Landscape | covered by size: a6-flyer (landscape) |
| 114 | `notebook-wraps` | Notebook (Wrap) | 309 × 200 mm | Landscape | out of scope (product template) |
| 115 | `notebooks` | Notebook Cover | 8.5 × 11 in | Portrait | covered by size: letter-flyer |
| 116 | `notepads` | Notepad | 10.5 × 14.8 cm | Portrait | covered by size: a6-flyer |
| 117 | `online-whiteboard` | Whiteboard | Unlimited | Unbounded | out of scope (whiteboard) |
| 118 | `page-borders` | Page Border | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 119 | `paper-bags` | Paper Bag with Handles | 6 × 5.3 in / 8 × 7 in | Landscape | out of scope (packaging dieline) |
| 120 | `phone-wallpapers` | Phone Wallpaper | 1080 × 1920 px | Portrait | partial: ig-story size; lock-screen clock and dock zones MISSING |
| 121 | `photo-books` | Photo Book | 11 × 8.5 in | Landscape | out of scope (multi-page print product) |
| 122 | `photo-collages` | Photo Collage | 20 × 30 cm | Portrait | covered by ratio: postcard-4x6 (2:3) |
| 123 | `pint-glasses` | Pint Glass | 9.1 × 4.3 in | Landscape | out of scope (product template) |
| 124 | `pinterest-ads` | Pinterest Carousel Ad | 1000 × 1500 px | Portrait | covered: pin-standard |
| 125 | `pinterest-pins` | Pinterest Pin | 1000 × 1500 px | Portrait | covered: pin-standard |
| 126 | `place-cards` | Place Card | 3.5 × 4 in | Portrait | MISSING: folded place card |
| 127 | `placemats` | Placemat | not captured | Landscape | MISSING (size not captured) |
| 128 | `planner-covers` | Planner Cover | 8.5 × 11 in | Portrait | covered by size: letter-flyer |
| 129 | `planners` | Planner | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 130 | `playlist-covers` | Playlist Cover | 1400 × 1400 px | Square | partial: podcast-cover (1:1) |
| 131 | `podcasts` | Podcast | 3000 × 3000 px | Square | covered: podcast-cover; episode art new: podcast-episode |
| 132 | `postcards` | Postcard | 148 × 105 mm | Landscape | covered: a6-flyer / postcard-4x6 |
| 133 | `posters` | Poster | 42 × 59.4 cm | Portrait | covered: a2-poster |
| 134 | `presentation-folders` | Presentation Folder | 12 × 18 in | Portrait | out of scope (dieline) |
| 135 | `presentations` | Presentation | 1920 × 1080 px | Landscape | covered: deck-16x9; room version new: deck-16x9-room |
| 136 | `profile-pictures` | Instagram Profile Picture / YouTube Profile Picture | 320 × 320 px / 800 × 800 px | Square | MISSING: profile pictures (320, 400, 800 px circles) |
| 137 | `programs` | Program | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 138 | `proposals` | Proposal | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 139 | `prototypes` | Mobile Prototype / Desktop Prototype | 414 × 896 px / 1280 × 800 px | Portrait / Landscape | out of scope (UI prototypes) |
| 140 | `rack-cards` | Rack Card | 9.9 × 21 cm | Portrait | covered by size: dl-flyer |
| 141 | `recipe-cards` | Recipe Card | 105 × 148 mm | Portrait | covered: a6-flyer |
| 142 | `report-cards` | Report Card | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 143 | `reports` | Report | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 144 | `resumes` | Resume | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 145 | `retractable-banners` | Retractable Banner | 850 × 2000 mm | Portrait | covered: rollup-850 |
| 146 | `return-address-labels` | Return Address Label | 2.4 × 1.1 in | Landscape | MISSING: address label |
| 147 | `road-safety-poster-uk` | Poster / Infographic | 42 × 59.4 cm / not captured | Portrait | covered: a2-poster |
| 148 | `rounded-corner-business-cards` | Rounded Business Card | 3.5 × 2 in | Landscape | covered: bc-us (corner radius from the printer) |
| 149 | `scrapbooks` | Scrapbook | 25 × 20 cm | Landscape | MISSING: scrapbook 25x20 cm |
| 150 | `seating-charts` | Seating Chart | 42 × 59.4 cm | Portrait | covered: a2-poster |
| 151 | `sell-sheets` | Sell Sheet | 8.5 × 11 in | Portrait | covered: letter-flyer |
| 152 | `sheets` | Sheet | Unlimited | Unbounded | out of scope (Canva Sheets) |
| 153 | `shipping-envelopes` | Shipping Envelope | 9.5 × 6.8 in | Landscape | out of scope (packaging) |
| 154 | `sketchbooks` | Sketchbook | 8.5 × 11 in | Portrait | covered by size: letter-flyer |
| 155 | `snap-envelopes` | Envelope (C5) | size in the type name | Landscape | MISSING: C5 envelope |
| 156 | `snapchat-collection-ad-thumbnails` | Snapchat Collection Ad Thumbnail | 160 × 160 px | Square | MISSING: Snap collection thumbnail 160x160 |
| 157 | `snapchat-collection-ad-videos` | Snapchat Collection Ad Video | 1080 × 1920 px | Portrait | covered (static frame): snap-ad |
| 158 | `snapchat-commercial-ads` | Snapchat Commercial Ad | 1080 × 1920 px | Portrait | covered (static frame): snap-ad |
| 159 | `snapchat-geofilters` | Snapchat Geofilter | 1080 × 2340 px | Portrait | MISSING: Snapchat geofilter 1080x2340 |
| 160 | `snapchat-story-ads` | Snapchat Snap Ad Static | 1080 × 1920 px | Portrait | covered: snap-ad |
| 161 | `snapchat-video-ads` | Snapchat Snap Ad Video | 1080 × 1920 px | Portrait | covered (static frame): snap-ad |
| 162 | `social-graphics` | Presentation | 1920 × 1080 px | Landscape | covered by size: deck-16x9 |
| 163 | `square-business-cards` | Business Card (Square) | 50 × 50 mm | Square | MISSING: square business card 50x50 mm |
| 164 | `square-pillows` | Square Pillow | 24.8 × 24.8 in | Square | out of scope (product template) |
| 165 | `square-videos` | Square Video | 800 × 800 px | Square | covered by ratio: ig-square |
| 166 | `stickers` | Sticker | 100 × 100 mm | Square | MISSING: sticker with die line |
| 167 | `storyboards` | Storyboard | 25 × 20 cm | Landscape | out of scope (planning document) |
| 168 | `student-portfolio` | Student Portfolio | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 169 | `sweatshirts` | Sweatshirt | 355 × 455 mm | Portrait | out of scope (apparel) |
| 170 | `t-shirts` | T-Shirt | 14 × 18 in | Portrait | out of scope (apparel) |
| 171 | `table-of-contents` | Document | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 172 | `tags` | Tag | 3.5 × 2 in | Landscape | covered by size: bc-us |
| 173 | `talking-presentations` | Talking Presentation | 1920 × 1080 px | Landscape | covered: deck-16x9 |
| 174 | `tarpaulins` | Tarpaulin | 36 × 24 in | Landscape | covered by size: poster-24x36 (landscape); eyelet allowance MISSING |
| 175 | `thank-you-cards` | Card | 14.8 × 10.5 cm | Landscape | covered by size: a6-flyer |
| 176 | `threads` | Threads Post | 1080 × 1350 px | Portrait | covered: threads-post |
| 177 | `tickets` | Ticket | 8.5 × 2.8 in | Landscape | MISSING: ticket with stub |
| 178 | `tier-lists` | Tier List | 1600 × 900 px | Landscape | covered by size: x-post |
| 179 | `tiktok-profile-picture` | TikTok Profile Picture | 200 × 200 px | Square | MISSING: profile picture |
| 180 | `tiktok-videos` | TikTok Video | 1080 × 1920 px | Portrait | covered: tiktok |
| 181 | `tote-bags` | Tote Bag | 250 × 250 mm | Square | out of scope (product template) |
| 182 | `tumblers` | Acrylic Tumbler | 9.9 × 4.3 in | Landscape | out of scope (product template) |
| 183 | `twitch` | Twitch Panel / Twitch Overlay | 320 × 100 px / 1920 × 1080 px | Landscape | new: twitch-panel, stream-overlay |
| 184 | `twitter` | Twitter / X Header | 1500 × 500 px | Landscape | covered: x-header |
| 185 | `vertical-business-cards` | Business Card | 3.5 × 2 in | Landscape | covered: bc-us (rotate) |
| 186 | `video-collages` | Video Collage | 800 × 800 px | Square | covered by ratio: ig-square (video out of scope) |
| 187 | `video-editor` | Landscape Video | 1920 × 1080 px | Landscape | out of scope (video); frames: title-card-1080 (new) |
| 188 | `video-messages` | Video Message | 1920 × 1080 px | Landscape | out of scope (video) |
| 189 | `virtual-classrooms` | Virtual Classroom | 1920 × 1080 px | Landscape | covered by size: deck-16x9 |
| 190 | `virtual-invitations` | Virtual Invitation | 1240 × 1748 px | Portrait | covered by ratio: a6-flyer (1240x1748 = A6 at 300 ppi) |
| 191 | `wall-calendars` | Wall Calendar | 297 × 210 mm | Landscape | partial: deck-a4-landscape (size); binding and grid MISSING |
| 192 | `waterbottles` | Water Bottle | 8.3 × 7.7 in | Landscape | out of scope (product template) |
| 193 | `web-ads` | Leaderboard Ad | 728 × 90 px | Landscape | covered: iab-leaderboard |
| 194 | `web-banners` | YouTube Banner | 2560 × 1440 px | Landscape | covered: yt-banner |
| 195 | `website-builder` | Website | 1366 × 768 px | Landscape | out of scope (Canva Websites); hero images: web-hero, web-hero-2560 (new) |
| 196 | `wedding-invitations` | Invitation | 105 × 148 mm | Portrait | covered: a6-flyer; MISSING: 5x7 in invitation |
| 197 | `welcome-sign` | Welcome Sign | not captured | Landscape | MISSING: event sign (size not captured) |
| 198 | `whatsapp-statuses` | Your Story | 1080 × 1920 px | Portrait | covered: wa-status |
| 199 | `wizer-worksheets` | Wizer Worksheet | 210 × 297 mm | Portrait | covered: a4-doc |
| 200 | `worksheets` | Worksheet | 21 × 29.7 cm | Portrait | covered: a4-doc |
| 201 | `wrapping-paper` | Wrapping Paper | 43.3 × 29.4 in | Landscape | out of scope (product template) |
| 202 | `yard-signs` | Yard Sign | 600 × 450 mm | Landscape | MISSING: yard sign (600x450 mm / 24x18 in) |
| 203 | `yearbooks` | Yearbook | 21 × 29.7 cm | Portrait | covered: a4-doc (multi-page) |
| 204 | `your-story` | Your Story | 1080 × 1920 px | Portrait | covered: ig-story |
| 205 | `youtube-ads` | YouTube Ad | 1080 × 1080 px / 1920 × 1080 px | Square / Landscape | covered by ratio: ig-square; 16:9 frames: title-card-1080 (new) |
| 206 | `youtube-channel-art` | YouTube Banner | 2560 × 1440 px | Landscape | covered: yt-banner |
| 207 | `youtube-channel-logos` | YouTube Channel Logo | 800 × 800 px | Square | MISSING: channel icon / profile picture |
| 208 | `youtube-display-ads` | YouTube Display Ad | 300 × 60 px | Landscape | MISSING: YouTube display ad 300x60 |
| 209 | `youtube-intros` | Landscape Video | 1920 × 1080 px | Landscape | new: title-card-1080 (frames) |
| 210 | `youtube-outros` | Landscape Video | 1920 × 1080 px | Landscape | covered: yt-endscreen |
| 211 | `youtube-shorts` | YouTube Shorts | 1080 × 1920 px | Portrait | covered: yt-shorts-thumb / vertical-safe |
| 212 | `youtube-thumbnails` | YouTube Thumbnail | 1280 × 720 px | Landscape | covered: yt-thumbnail |
| 213 | `youtube` | Landscape Video | 1920 × 1080 px | Landscape | out of scope (video); frames: title-card-1080 (new) |
| 214 | `z-fold-brochures` | Z-Fold Brochure | 11 × 8.5 in | Landscape | covered by size: trifold-letter (z-fold panel maths differ) |
| 215 | `zoom-events` | Zoom Events | 600 × 600 px / 744 × 484 px | Square / Landscape | MISSING: Zoom Events images 600x600 and 744x484 |
| 216 | `zoom-profile` | Zoom Profile Cover | 1280 × 720 px | Landscape | covered by size: li-event-cover (1280x720) |
| 217 | `zoom-virtual-backgrounds` | Virtual Background | 1280 × 720 px | Landscape | new: virtual-bg (1920x1080; Zoom's minimum is 1280x720) |

Tally by first label: covered (incl. by size or ratio) 130, MISSING 40, out of scope 32, partial 5, new in web.json 10. Rows whose coverage also names a second gap (for example `covered: a6-flyer; MISSING: 5x7 in card`) count under their first label; 55 rows mention MISSING somewhere.

## 2. Canva size guide tables (canva.com/sizes)

| Page | Item | Canva size | Coverage |
|---|---|---|---|
| YouTube | YouTube Thumbnail | 1,280 × 720 px | covered: yt-thumbnail |
| YouTube | YouTube Banner | 2,560 × 1,440 px | covered: yt-banner |
| YouTube | YouTube Video (4K) | 3,840 × 2,160 px | new: title-card-2160 (frames) |
| YouTube | YouTube Profile Picture | 800 × 800 px | MISSING: profile picture |
| YouTube | Banner in Desktop / Tablet / Mobile / TV display | 2,560 × 423 / 1,855 × 423 / 1,546 × 423 / 2,560 × 1,440 px | covered: yt-banner safe zone |
| Facebook | Profile Picture | 400 × 400 px | MISSING: profile picture |
| Facebook | Cover Photo | 1,125 × 633 px | conflict: existing fb-cover is 1702x630 (R5, measured); Canva's value differs |
| Facebook | Image Post / Shared Link Images | 1,200 × 630 px | covered: og-image |
| Facebook | Tab Images | 113 × 74 px | out of scope (legacy) |
| Facebook | Event Image | 1,920 × 1,005 px | covered: fb-event-cover |
| Facebook | Facebook Ad (Carousel) / (Single Image) | 1,080 × 1,080 / 1,200 × 628 px | covered: fb-square / gads-landscape |
| Instagram | Profile Photo | 110 × 110 px | MISSING: profile picture |
| Instagram | Square Images / Images / Stories | 1,080 × 1,080 / 1,080 × 1,350 / 1,080 × 1,920 px | covered: ig-square / ig-portrait / ig-story |
| X/Twitter | Header Photo | 1,500 × 500 px | covered: x-header |
| X/Twitter | Profile Photo | 400 × 400 px | MISSING: profile picture |
| X/Twitter | Twitter Post | 1,024 × 512 px | covered by ratio: x-card (2:1); in-stream posts use x-post |
| X/Twitter | Cards Image / Summary Card Image | 800 × 320 / 280 × 150 px | outdated: X now documents 2:1 (x-card) and 1:1 min 144x144 (new: x-card-summary) |
| LinkedIn | Profile Photo | 400 × 400 px | MISSING: profile picture |
| LinkedIn | Cover Photo | 1,584 × 396 px | covered: li-profile-cover |
| LinkedIn | Shared Image | 180 × 110 px | outdated: link images are 1200x627 (li-landscape / og-image) |
| Pinterest | Profile Photo / Board Cover Photo | 165 × 165 / 222 × 150 px | MISSING (small UI images) |
| Pinterest | Pin Sizes (Portrait) | 735 × 1,102 px | covered by ratio: pin-standard (1000x1500) |
| Twitch | Profile Photo | 800 × 800 px | MISSING: profile picture |
| Twitch | Profile Banner | 1,920 × 480 px | conflict: Twitch Help recommends 1200x480 (new: twitch-banner) |
| Twitch | Video Player Banner | 1,920 × 1,080 px | new: twitch-offline |
| Twitch | Video Thumbnail | 1,280 × 720 px | new: video-thumb-16x9 (alias) |
| Twitch | Cover Image | 380 × 1,200 px | MISSING (unverified purpose) |
| Twitch | Info Panels | 320 × 200 px | new: twitch-panel (Twitch max 320 wide, 300 high) |
| SoundCloud | Profile Photo / Album Cover / Minimum Header | 1,000 × 1,000 / 800 × 800 / 2,480 × 520 px | MISSING: SoundCloud header; covers see album gap |
| Tumblr | Profile Photo / Banner / Shared Image | 128 × 128 / 3,000 × 1,055 / 500 × 750 px | MISSING (Tumblr) |
| Etsy | Cover | 3,360 × 840 px | covered by ratio: etsy-banner (4:1) |
| Etsy | Profile Photo / Shop Icon | 400 × 400 / 500 × 500 px | MISSING: profile picture |
| Etsy | Shop Banner / Thumbnail / Team Logo | 760 × 100 / 570 × 456 / 170 × 100 px | out of scope (legacy Etsy sizes) |
| Etsy | Item Listing | 800 × 1,000 px | conflict: existing etsy-listing is 2000x1500 (Etsy help: at least 2000 px) |
| Presentation | 4:3 / 16:9 | 1,024 × 768 / 1,920 × 1,080 px | new: deck-4x3 / covered: deck-16x9 |
| Poster | Smallest / Small / Medium / Large | 8.5 × 11 / 11 × 17 / 18 × 24 / 24 × 36 in | covered: letter-flyer / tabloid-poster / poster-18x24 / poster-24x36 |
| Poster | Movie / Bus Stop | 27 × 40 / 40 × 60 in | MISSING: 27x40 one-sheet (in R5 table, no preset), 40x60 bus shelter |
| Brochure | A3 / A4 / A5 / DL | 29.7 × 42 / 21 × 29.7 / 14.8 × 21 / 11 × 22 cm | covered: trifold-a4, bifold-a4, a5-flyer, dl-flyer (A3 brochure MISSING) |
| Brochure | Letter / Legal / Half Letter / Tabloid | 27.94 × 21.59 / 21.59 × 35.56 / 21.59 × 13.97 / 27.94 × 43.18 cm | covered: trifold-letter, half-letter; Legal and Tabloid brochures MISSING |
| Flyer | Half Sheet / Standard / Large Format | 5.5 × 8.5 / 8.5 × 11 / 11 × 17 in | covered: half-letter / letter-flyer / tabloid-poster |
| Book | Ebook: General / Kindle / Wattpad / Kobo | 20.8 × 33.3 / 22.2 × 35.6 / 7.1 × 11.1 / 14.9 × 20.1 (Canva writes in) | MISSING: ebook covers (units look wrong, see section 8) |
| Book | Royal / Medium / Crown series (folio to sixty-four-mo) | e.g. Royal Octavo 6.25 × 10 in, Crown Octavo 5 × 7.5 in | MISSING: book covers and interiors |
| Resume | United States / Europe | 8.5 × 11 (Canva writes cm) / 21 × 29.7 cm | covered: letter-flyer size / a4-doc |
| Greeting card | A0 to A10 | A-series in cm | covered: a0-poster ... a6-flyer; A7 to A10 MISSING |
| Photo | 3R / 4R / 5R / 8R / 9R / 10R / 11R | 3 × 5 / 4 × 6 / 5 × 7 / 8 × 10 / 8.5 × 11 / 9 × 16 / 11 × 14 in | covered: postcard-4x6, letter-flyer; 3x5, 5x7, 8x10, 11x14 MISSING |
| Invitation | A1/Baronial to A10 (folded and unfolded) | e.g. A7/Lee 5.13 × 7 in folded, 10.5 × 7 in unfolded | MISSING: US invitation card family |
| Invitation | Square small / medium / large | 5.5 / 6.25 / 6.75 in square | MISSING: square invitations |
| Letter | US (Letter) / International (A4) | 21.59 × 27.94 / 21 × 29.7 cm | covered: letter-flyer / a4-doc |
| Wedding invitation | Common / Square / Large Rectangle / Skim | 12.7 × 17.78 / 13.34 × 13.34 / 44.87 × 22.23 / 10.16 × 23.5 cm | MISSING: 5x7 in (12.7 x 17.78 cm) invitation and others |
| Wedding invitation | A5 to A10, C0 to C10, DL | ISO sizes in cm | covered: a5-flyer, a6-flyer, dl-flyer; C-series envelopes MISSING |
| Label | Wine / Beer / Water bottle 16 oz / 8 or 12 oz / Address tag / Name tag | 3.5 × 4 / 4 × 3 / 8 × 2 / 8.25 × 1.75 / 2.63 × 1 / 3.38 × 2.31 in | MISSING: labels |
| Business card | Country table | 3.5 × 2 in (US, CA); 3.35 × 2.17 in (UK, DE, FR...); 3.58 × 2.17 in (JP); 3.54 × 2.17 in (AU, BD, IN, NZ, VN...); 3.54 × 2.13 in (CN, HK, SG, MY); 3.54 × 1.97 in (many EU/LatAm); 3.43 × 2.24 in (EG); 3.35 × 1.89 in (IR) | covered: bc-us, bc-eu, bc-jp; MISSING: 90x55 mm (Bangladesh, India, Australia), 90x54, 90x50 and others |
| Web ad | Leaderboard / Medium Rectangle / Wide Skyscraper | 728 × 90 / 300 × 250 / 160 × 600 px | covered: iab-leaderboard / iab-mrec / iab-skyscraper |
| Web ad | Large Rectangle / Skyscraper / Button 1 / Button 2 / Microbar | 336 × 280 / 120 × 600 / 120 × 90 / 120 × 60 / 88 × 31 px | MISSING: 336x280; the rest are legacy |

Paper pages (`a4-paper-size`, `a-series-paper`, `b-series-paper`, `c-series-paper-sizes`, `north-american-paper`) repeat ISO 216 and North American sizes; A0 to A6, B2, DL, Letter, Half Letter and Tabloid are covered by existing print presets, B-series except B2 and C-series are not.

## 3. Sizes stated in the text of Canva create pages

| Create page | Size sentence on the page (paraphrased, numbers exact) | Coverage |
|---|---|---|
| avatars | at least 150 x 150 pixels, max 1 MB | MISSING: profile picture |
| banners | Facebook Cover Photo 851 x 315; X Banner 1500 x 500; Tumblr 3,000 x 1055 | covered: fb-cover, x-header; Tumblr MISSING |
| banners/etsy-banners | Etsy banner 760 x 100; cover 3360 x 840 | covered by ratio: etsy-banner |
| bookmarks | around 2 x 8 inches | MISSING: bookmark |
| birthday-invitations / invitation-cards | 4 x 6 in or 5 x 7 in; formal 5 x 7 | covered: postcard-4x6; 5x7 MISSING |
| brochures | 8.5 x 14, 11 x 17 and 11 x 25.5 in (text garbled on the page) | MISSING: legal and tabloid folds |
| certificates | 8.5 x 11 in; also 8.5 x 14, 11 x 14, 11 x 17 | covered: letter-flyer size (landscape Letter MISSING) |
| coupons | 2.5 x 6 inches | MISSING: coupon |
| discord-emotes | max 128x128 px, 256 KB | MISSING: emoji / emote |
| ebook-covers | Amazon 2560 x 1600 (Canva says ratio 1:1, which contradicts the numbers); Kobo 1448 x 1072; Wattpad 512 x 800 | MISSING: ebook cover (verify with the store) |
| event-programs | 5.5 x 8.5 inches | covered: half-letter |
| facebook-ad-videos | at least 1080 x 1080, max 4 GB | out of scope (video) |
| facebook-ads | feed image 1200 x 628; carousel 600 x 600 minimum | covered: gads-landscape / fb-square |
| facebook-event-covers | at least 1200 x 628 | covered: fb-event-cover |
| flags | 4 x 6 in; 11 x 15 in; 12 x 18 in | MISSING: flags |
| flyers | 8.5 x 11 in; 11 x 17; 5.5 x 8.5 | covered: letter-flyer, tabloid-poster, half-letter |
| flyers/business-flyers | long flyer 3.75 x 8.25 in | MISSING: US rack/long flyer |
| gift-certificates | about 8 x 3.75 in; 8.5 x 4; 3.5 x 2 | MISSING: gift certificate |
| gift-tags | 3-5 x 2.5 in; 2 x 1 in; 9 x 4 in | MISSING: tags |
| id-cards | 2.125 x 3.37 in (credit card) | MISSING: ID card |
| infographics | blogs about 663 x 2000; Facebook 1200 x 628 | MISSING: tall infographic |
| instagram-logos / png-logos | logo templates 500 x 500; Instagram shows 110 x 110 | MISSING: logo master, profile picture |
| labels/water-bottle | 8 x 2 in (16 oz), 8.25 x 1.75 in (8 or 12 oz) | MISSING: labels |
| name-tags | 4 x 3 in; evening 3.5 x 2.25 in | MISSING: name tag |
| posters | 18 x 24, 24 x 36 and 27 x 40 in | covered: poster-18x24, poster-24x36; 27x40 MISSING |
| profile-pictures | YouTube 800 x 800; Instagram 320 x 320; Facebook 170 x 170 | MISSING: profile pictures |
| recipe-cards | 3 x 5, 4 x 6, 5 x 7 in | covered: postcard-4x6; others MISSING |
| scrapbooks | 12 x 12, 8.5 x 11, 8 x 6 in | MISSING: 12x12 scrapbook |
| seating-charts | up to 24 x 36 in | covered: poster-24x36 |
| snapchat-geofilters | typically 1080 x 1920, under 300 KB (the template library uses 1080 x 2340) | MISSING: geofilter (sizes conflict) |
| tickets | event ticket with stub 1.97 x 5.63 in | MISSING: ticket |
| twitch-banners / twitch-panels / twitch-overlays / twitch-logos / twitch-emotes | banner 1920 x 480; panel 320 x 160; overlay 1920 x 1080; logo 800 x 800; emotes 112 to 4096 px square, 1 MB (manual 28, 56, 112 px under 100 KB) | new: twitch-panel, stream-overlay; twitch-banner uses Twitch's 1200x480; emotes MISSING |
| twitter-headers | "1500 x 1500 pixels" (typo on Canva's page; the header is 1500 x 500) | covered: x-header |
| youtube-thumbnails | 1280 x 720, minimum width 640 | covered: yt-thumbnail |

## 4. Canva limits and resize behaviour

- **Custom size in the editor (Magic Resize).** "Minimum dimensions: 40 x 40 px" and "Maximum dimensions: 8000 x 3125 px". Resize handles up to 50 designs at once, up to 5 new sizes per design and at most 250 outputs per bulk action; each use counts against the monthly AI usage limit; plans: Pro, Business, Enterprise, Education, Nonprofits, Teams. A workaround for out-of-range sizes: lock the aspect ratio, enter a size inside the limits, and download PNG at 0.5x to 3.125x. Source: Canva Help, Resize designs and size limits, `https://www.canva.com/help/resize/`.
- **Canva Connect API.** Preset design types are only `doc`, `email`, `presentation` and `whiteboard`; custom designs take a width and height "between 40 and 8000 pixels" with a total area of at most 25,000,000 px (for example 5000 x 5000). Source: `https://www.canva.dev/docs/connect/api-reference/designs/create-design/`.
- **Print.** Canva adds 0.125 in (3.175 mm) of bleed on all sides for trimmed products, and says to check with your print provider when printing outside Canva Print; the minimum recommended print resolution is 300 DPI; colours are converted from RGB to the closest CMYK when a design is sent for print. Sources: Canva Help `margins-bleed-crop-marks`, `print-looks-blurry`, `cmyk-for-print`.
- **Resize is a copy-and-reflow, not a guarantee.** Canva's help describes choosing sizes and "Copy & resize"; it does not claim the result needs no edits. Treat any automatic resize as a first draft and re-check safe zones and text floors (this skill's rule, see `unknown-format-protocol.md` section 6).

## 5. Adobe Express

### 5.1 Size guides (`adobe.com/express/discover/sizes/...`; only Instagram, Facebook, X, YouTube and aspect-ratio pages exist)

| Guide | Item | Adobe's stated size | Coverage |
|---|---|---|---|
| Instagram | Square / landscape / vertical post; story; video | 1080x1080 / 1080x566 / 1080x1350; 1080x1920; 1080x1920 | covered: ig-square / ig-landscape / ig-portrait / ig-story |
| YouTube | Channel art; safe area; thumbnail; profile | 2560x1440; 1546x423 centre; 1280x720; 800x800 (shown at 98x98) | covered: yt-banner / yt-thumbnail; profile MISSING |
| Facebook | Cover; minimum; displayed | 851x315; at least 400x150; shown 820x312 desktop, 640x360 phone | covered: fb-cover |
| Facebook | Profile picture | shown 170x170 desktop, 128x128 phone, 36x36 feature phones | MISSING: profile picture |
| Facebook | Event photo; group cover; link share; posts | 1200x628; 1640x856; 1200x630 (under 600x315 shows small); at least 1080x1080 | covered: fb-event-cover (conflict: 1920x1005 in R5), fb-group-cover, og-image, fb-square |
| X/Twitter | Header; profile; in-stream; cards | 1500x500; 400x400; 600x335 shown, up to 1200x675; Website Card 800x418, App Card 800x800 | covered: x-header, x-post; profile MISSING; website card is 1.91:1 like og-image |

### 5.2 Sizes stated on Adobe Express create pages

| Create page | Size sentence (numbers exact) | Coverage |
|---|---|---|
| post/facebook | horizontal 1200x630; vertical 1080x1350 | covered: og-image, fb-feed |
| story/facebook, story/instagram, highlight cover | 1080x1920 | covered: ig-story |
| banner/facebook-cover | 820x312 standard; cropped to 640x360 on mobile | covered: fb-cover |
| banner/youtube, banner/youtube-channel-art | 2560x1440; safe area 1235x338 | covered: yt-banner (R5 scales the same safe area to 1546x423 at 2560) |
| banner/linkedin | personal 1536x396 (sic); company 1128x191 | conflict: LinkedIn now uses 1584x396 (li-profile-cover) and 1512x256 (li-company-cover) |
| banner/twitter-header | 1500x500, max 2 MB; keep details inside the central 1500x360 | covered: x-header (Adobe's 1500x360 band is a useful extra safe hint) |
| banner/soundcloud | at least 2480x520, no larger than 2 MB | MISSING: SoundCloud header |
| banner/etsy | big banner min 1200x300, recommended 3360x840; mini 1200x160 | covered by ratio: etsy-banner |
| banner/twitch-overlay | 1920x1080 for larger webcams, 1600x1200 (4:3) for smaller webcams | new: stream-overlay |
| banner (general) | YouTube 2560x1440, Facebook cover 820x312, LinkedIn 1584x396, X 1500x500; IAB 728x90, 300x250, 160x600; print banners typically 72 x 36 in | covered (digital); print banner MISSING |
| banner/vertical | templates start at 1200x2400 (1:2) | MISSING: 1:2 vertical banner |
| post/pinterest-pin | 735x1102 or another 2:3; templates 1000x1500 | covered: pin-standard |
| profile-picture | Facebook 170x170, Instagram 320x320, X and LinkedIn 400x400 | MISSING: profile pictures |
| logo | downloads as 500x500; many templates 1200x1200 | MISSING: logo master |
| thumbnail/youtube | 1280x720 default canvas; shown as small as 168x94 on mobile | covered: yt-thumbnail |
| sticker/whatsapp | exactly 512x512 | MISSING: WhatsApp sticker (R5 lists it as unverified) |
| cover/album | Spotify recommends 640x640; Apple Music requires at least 4000x4000 (Adobe's claim) | MISSING: music cover |
| wallpaper/desktop | 1920x1080 is one of the most common | covered by size: web-hero |
| meme | 1080x1080 | covered: ig-square |
| animation/youtube | Shorts 1080x1920 | covered: yt-shorts-thumb |
| card (greeting) | 5 x 7 in; with bleed 5.25 x 7.25 in | MISSING: 5x7 card |
| invitation | 5 x 7 in standard; also A5, 7 x 5, 3.5 x 5, 5 x 3.5 in | covered: a5-flyer; 5x7 and 3.5x5 MISSING |
| poster | 11 x 17, 18 x 24, 20 x 20 in; 11 x 17 with bleed 11.25 x 17.25 | covered: tabloid-poster, poster-18x24; 20x20 MISSING |
| brochure | 11 x 8.5 in (letter) | covered: trifold-letter |
| menu | 8.5 x 11 in | covered by size: letter-flyer (menu-a4 for A4) |
| cover/book | 4.25 x 6.87 in up to 6 x 9 in | MISSING: book cover |
| background/zoom | Zoom recommends 1920x1080 (16:9) | new: virtual-bg |

### 5.3 Adobe Express print products (`adobe.com/express/create/print/...`)

| Product | Adobe's sizes | Coverage |
|---|---|---|
| Business card | Portrait 2 x 3.5 in (50.8 x 88.9 mm); Landscape 3.5 x 2 in; Square 2 x 2 in (50.8 x 50.8 mm) | covered: bc-us; square card MISSING |
| Card | Portrait 5 x 7 in (127 x 177.8 mm), 3.5 x 5 in; Landscape 5 x 3.5, 7 x 5 in | MISSING: 5x7 and 3.5x5 cards |
| Flyer | Portrait 8.5 x 11 in (215.9 x 279.4 mm); Landscape 11 x 8.5 in | covered: letter-flyer (landscape by rotation) |
| Invitation | Landscape 7 x 5, 5 x 3.5 in; Portrait 5 x 7, 3.5 x 5 in | MISSING: 5x7 and 3.5x5 invitations |
| Poster | 8 x 10, 16 x 20, 18 x 24, 24 x 36, 11 x 17 in (portrait and landscape) | covered: poster-18x24, poster-24x36, tabloid-poster; 8x10 and 16x20 MISSING |
| T-shirt | size not stated on the page | out of scope (apparel) |

### 5.4 Adobe Express resize

Adobe's image resizer page: upload a JPG or PNG, then "select the size you need"; it "includes standard aspect ratio presets plus presets for social media channels including Instagram, Facebook, X, YouTube, Pinterest, and more", and you "can also scale, pan, and crop". That is a crop-and-scale tool for single images, not a layout re-composer (`https://www.adobe.com/express/feature/image/resize`). Adobe Express custom-size limits were not published on any page read this session.

## 6. PowerPoint, Google Slides and Keynote presets (for completeness)

| App | Preset | Size as the vendor states it | Coverage |
|---|---|---|---|
| PowerPoint | Widescreen (default) | 13.333 x 7.5 in (33.867 x 19.05 cm) | covered: deck-16x9; new: deck-16x9-room |
| PowerPoint | Standard (4:3) / On-screen Show (4:3) / Letter Paper / Overhead | 10 x 7.5 in (25.4 x 19.05 cm) | new: deck-4x3 |
| PowerPoint | On-screen Show (16:9) | 10 x 5.625 in (25.4 x 14.288 cm) | covered by ratio: deck-16x9 |
| PowerPoint | On-screen Show (16:10) | 10 x 6.25 in (25.4 x 15.875 cm) | new: deck-16x10 |
| PowerPoint | A4 Paper | 10.833 x 7.5 in (27.517 x 19.05 cm), not true A4 | new: deck-a4-landscape is true A4 |
| PowerPoint | A3 Paper / Ledger / B4 (ISO) / B5 (ISO) / 35 mm Slides / Banner | 14 x 10.5 / 13.319 x 9.99 / 11.84 x 8.88 / 7.84 x 5.88 / 11.25 x 7.5 / 8 x 1 in | MISSING (rare) |
| PowerPoint | Custom limits | 1 in (2.54 cm) to 56 in (142.24 cm) | n/a |
| PowerPoint | Default image export | 96 dpi: 1280 x 720 (widescreen), 960 x 720 (4:3); up to 100 MP | render with the skill instead |
| Google Slides | Presets | Standard (4:3), Widescreen (16:9), Widescreen (16:10), Custom in inches, cm, points or pixels; Google's page gives no dimensions | covered: deck-16x9; new: deck-4x3, deck-16x10 |
| Keynote | Slide sizes | Apple's guide names the menu but gives no pixel sizes; Canva's size guide gives 1024 x 768 (4:3) and 1920 x 1080 (16:9) | covered: deck-16x9; new: deck-4x3 |

## 7. What the skill is missing, by priority

1. **Profile pictures and avatars with a circle crop** (Canva: Instagram 320, Facebook 170/400, X and LinkedIn 400, YouTube 800, TikTok 200, Twitch 800). Needed by almost every brand kit; R5 already has most sizes, but no preset exists.
2. **US card and invitation family:** 5 x 7 in (and 3.5 x 5, 4.25 x 5.5 A2, 5.5 x 5.5 square), plus folded versions with a fold line. Canva, Adobe Express and Canva's invitation guide all lead with 5 x 7 in.
3. **90 x 55 mm business card** (Bangladesh, India, Australia, New Zealand, Vietnam per Canva's table) and 90 x 54 / 90 x 50 mm. R5 has bc-au but no preset; this matters for the user's home market.
4. **Stickers, labels and decals with die lines** (Canva: stickers 100 x 100 mm, bumper 11 x 3 in, labels 6 x 4 in, wine 3.5 x 4 in, address 2.63 x 1 in).
5. **Large-format banners and signs:** vinyl banner 1000 x 500 mm, 72 x 36 in (Adobe), classroom 96 x 24 in, tarpaulin 36 x 24 in, yard sign 600 x 450 mm / 24 x 18 in, flags. They need hem and eyelet allowances from the printer.
6. **Book, ebook and music covers** (Canva book cover 1410 x 2250 px, ebook 512 x 800 px, album and playlist 1400 x 1400 px).
7. **Tall infographic** (Canva 800 x 2000 px) and **logo master** (Canva 2000 x 2000 px, Adobe 500 x 500 or 1200 x 1200 px).
8. **Smaller digital gaps:** email signature (Canva 400 x 200 px), Snapchat geofilter (1080 x 2340 px), YouTube display ad (300 x 60 px), IAB 336 x 280, Zoom Events (600 x 600 and 744 x 484 px), phone wallpaper with lock-screen zones, tickets, bookmarks (2 x 6 in), certificates in US Letter landscape.

Out of scope for an HTML/CSS still-image renderer unless a vendor template is supplied: video timelines, Canva Docs, Sheets, Whiteboards, Websites, apparel, drinkware, bags, packaging and other product templates.

## 8. Conflicts and errors noticed in the vendor lists

- Canva's size guide gives the Facebook cover as 1,125 x 633 px, the Canva template library uses 851 x 315 px, Adobe Express says 851 x 315 (820 x 312 shown). The skill's fb-cover (1702 x 630) came from measurement and Meta's help (R5). Keep fb-cover.
- Facebook event cover: Canva's template is 1920 x 1080, Canva's size guide says 1920 x 1005, Adobe says 1200 x 628. R5 records that Meta publishes no official spec. Keep fb-event-cover (1920 x 1005) and keep the key content inside a 16:9 centre.
- Twitch profile banner: Canva says 1920 x 480, Twitch Help says 1200 x 480 recommended. Twitch wins (twitch-banner).
- LinkedIn: Adobe still lists 1536 x 396 and 1128 x 191; LinkedIn's current sizes are 1584 x 396 and 1512 x 256 (R5).
- Etsy listing: Canva says 800 x 1,000 px; Etsy's help (R5) asks for at least 2000 px. Keep etsy-listing.
- Canva's ebook sizes are written in inches ("20.8 × 33.3 in" for a general ebook, "22.2 × 35.6 in" for Kindle), which reads like centimetres; its US resume is "8.5 × 11 cm" (should be inches); its wedding invitation "A9" is "23.7 × 5.2 cm" (A9 is 3.7 x 5.2 cm); its create page for X headers says 1500 x 1500. Do not import Canva numbers without a second source.
- Snapchat geofilter: Canva's create page says 1080 x 1920, its template library uses 1080 x 2340.
- Adobe's Instagram post page calls 1.91:1 "1080px by 566px" and Canva's X page still lists 1024 x 512 for posts: both are older than the 2025 Instagram 3:4 grid and X's current in-stream sizes (see R5).

## Sources

- Canva template library (217 category pages and their template pages), read 2026-09-24/25: https://www.canva.com/<category>/templates/ (list from https://www.canva.com/landing_page_sitemap_1.xml)
- Canva Design Wiki size guide: https://www.canva.com/sizes/ and sub-pages
- Canva create pages (318 pages scanned): https://www.canva.com/create/
- Canva Help: https://www.canva.com/help/resize/, https://www.canva.com/help/margins-bleed-crop-marks/, https://www.canva.com/help/print-looks-blurry/, https://www.canva.com/help/cmyk-for-print/
- Canva Connect API, Create design: https://www.canva.dev/docs/connect/api-reference/designs/create-design/
- Adobe Express size guides: https://www.adobe.com/express/discover/sizes/instagram, /facebook, /twitter, /youtube, /photo-aspect-ratio
- Adobe Express create pages (96 scanned): https://www.adobe.com/express/create
- Adobe Express image resizer: https://www.adobe.com/express/feature/image/resize
- Microsoft Support, Change the size of your slides: https://support.microsoft.com/en-us/office/change-the-size-of-your-slides-040a811c-be43-40b9-8d04-0de5ed79987e
- Microsoft Learn, export slide resolution: https://learn.microsoft.com/en-us/office/troubleshoot/powerpoint/change-export-slide-resolution
- Google Docs Editors Help, slide size: https://support.google.com/docs/answer/3447672
- Apple Keynote User Guide, Change the slide size: https://support.apple.com/guide/keynote/change-the-slide-size-tan929f13a1f/mac
- Twitch Help, Channel Page Setup: https://help.twitch.tv/s/article/channel-page-setup
- Existing preset notes: codex-design references/research/R5-formats-specs-playbooks.md (2026-09-23)

Figma's frame-preset list was not read this session (no search budget, and help.figma.com pages for presets were not located), so Figma is not in this catalogue.
