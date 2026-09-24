# Commerce, marketplace, app store, creator and event formats

Research for the codex-design presets, verified 2026-09-24. Companion to `commerce.json`, which holds 111 new presets: 68 e-commerce, 40 app and 3 web. This file holds the playbooks, the corrections to existing presets, the policy traps and the Bangladesh notes.

## 0. How to read this

**Confidence labels.** Each preset in the JSON has one label, describing where its size rules and limits come from. Nuance goes in its `notes`.
- **official**: the platform's own help centre, seller centre, developer docs or policy page.
- **widely-cited**: a named third-party guide, used only where the official page could not be read.
- **practice**: measured from what a platform actually serves, or derived from a theme's code.
- **estimate**: a geometric estimate (mostly on-screen widths that could not be measured).

Where the platform states only a ratio or a minimum, we chose the render size (usually 2x the minimum). The label then still describes the rules, and the notes say "practice" for the size. The official minimum is always kept in `min_size` or in `notes`.

**Text sizes.** `min_text_px` and `large_text_px` follow the existing presets: 11 CSS px and 24 CSS px at the width the image is seen, so `round(11 * w / view_width_px)` and `round(24 * w / view_width_px)`. One exception: `amazon-store-hero` uses Amazon's own 90 pt floor.

**`view_width_px` is the CSS width of the whole canvas as displayed.** `design.py` computes the seen size as `size * view_width_px / w`. When a phone crops an image (Amazon Store hero, Shopify Dawn banner), the value is the full-canvas equivalent, for example 557 for a 3000 px hero whose centre 2100 px fills a 390 px phone.

**Measured widths (2026-09-24, real browser):**
- Amazon mobile web search tile: 129 CSS px on a 375 px phone (list layout; sponsored carousels 190).
- eBay mobile web search tile: 120x120 CSS px.
- Daraz search tile: 174 CSS px on a 375 px phone.
- Daraz product page image: 375x375 CSS px (served 720x720).
- Myntra desktop grid tile: 210x280.
- Flipkart desktop grid tile: 139x185.
- Shopify Dawn product card: `calc((100vw - 35px) / 2)`, which is 177.5 px on a 390 px phone (from the theme code).

Other on-screen widths are estimates and say so.

**Safe areas** are `[top, right, bottom, left]` in px at the preset size. Where a platform states a fill rule (Amazon 85%, Google 75 to 90%, TikTok beauty 80%), the safe box is the fill boundary: the product should reach it. Where a platform states a crop (Amazon Store hero, Eventbrite square thumbnail, Udemy mobile crop, Google Play cutoff zones, Microsoft bottom third), the numbers come from that statement or from the platform's own diagram, measured. All other margins are practice and marked so.

**How this was researched.** The shared WebSearch budget for the session was already used up when this work started. Sources were read directly instead:
- official pages by known URL;
- help-centre search APIs (Zendesk) and in-site search;
- the Shopify Dawn source on GitHub;
- the Wayback Machine for two pages behind bot checks;
- a real browser for JavaScript-only pages (TikTok Shop Academy, Daraz University, Meta Business Help, Eventbrite, Walmart).

Pages behind a bot challenge were not forced; they are listed in section 10.

---

## 1. The e-commerce product image system

### 1.1 Why the stack matters (evidence)
- **Images come first.** 56% of Baymard test users started by exploring the images on a product page (Baymard, 30 May 2017; repeated in later articles).
- **Sites still miss the slots users need** (Baymard, "Product Page UX 2026", published 24 Oct 2023, updated 18 Mar 2026):
  - 37% of sites have no in-scale image;
  - 23% have no human-model image for wearables.
- **Slot-specific findings:**
  - 42% of users try to judge size from the images (Baymard, 2017).
  - 31% of sites have no "included accessories" image. Without one, 63% of test users could not tell what came in the box (Baymard, 19 Feb 2019).
  - 52% of sites add no descriptive text or callouts to images (Baymard, 28 Nov 2018).
  - Dimension images must be readable without zooming on a phone (Baymard, 15 Oct 2024).
- **Platforms ask for several images:**
  - Amazon: at least 6 recommended, up to 9 slots.
  - TikTok Shop: at least 5 recommended, up to 9 (US minimum 600x600, UK 800x800).
  - Meta catalogue: 4 or more recommended.
  - Daraz Bangladesh: at least 4, from different angles (its declutter criteria).
  - Etsy: up to 20 photos and 2 videos.
  - eBay: up to 24.
  - Google Merchant Center: up to 10 additional images.
- **Resolution and zoom.** 25% of sites fail on resolution or zoom: 14% have low-resolution images and 11% poor zoom (Baymard, 2 Apr 2020). Amazon needs more than 1,000 px for zoom.

### 1.2 Text on images, by platform (check before adding any words)

| Platform | Main image | Secondary images | Source |
|---|---|---|---|
| Amazon | No text, logos, badges, borders, props | Allowed in practice (infographics); no promo text or watermarks | sell.amazon.com; Amazon style guides |
| Google Merchant Center | No overlays, text, logos, borders | Same for additional images; lifestyle images no text | Merchant Center help 6324350, 9103186 |
| eBay | No added text, borders, artwork, watermarks | Same on every photo | eBay picture policy |
| TikTok Shop (US; UK similar) | No added text, logos, borders, graphics | Same on every image (policy); promo stickers cause rejection. UK allows the product's own branding | TikTok Shop listing policy, 1 Sep 2026; UK page, 17 Nov 2025 |
| Meta catalogue | No text over the product, CTAs, promo codes, watermarks | Same | Meta Business Help |
| Daraz (BD) | No text: price, contact details, links cause rejection | Same guidance | Daraz University, 28 Feb 2024 |
| Lazada | Text-only images score lowest; promotion images: no marketing copy | Same | Lazada University; Open Platform 2023 |
| Shopee | Cover: avoid text and graphics | Text, graphics and watermarks at most 25% of the background, never on the product; Mall rules vary by country | Shopee Seller Education Hub, 2026 |
| Mercado Libre | No text, logos, watermarks, QR codes | Packaging allowed from photo 2 | Mercado Libre help 805 |
| Noon | No logos, watermarks, price, warranty or expiry text | Same | Noon partner help, 22 Apr 2026 |
| Allegro | No store text or logo; brand and technology logos allowed | Infographics for invited sellers only, never the thumbnail | Allegro help |
| Etsy | Not banned in the help pages read; a collage, dark or blurry first photo ranks lower | Allowed | Etsy help |
| Shopify / WooCommerce | Your own site: allowed, but keep grid thumbnails clean and consistent | Allowed | Shopify help |

So on eBay, Google Shopping, TikTok Shop, Meta catalogue, Daraz, Mercado Libre and Noon, the "infographic" slot must carry its information without baked-in words: use arrows, icons, scale objects and a clean composition, or skip the slot.

### 1.3 The slots, in selling order

**How the copy budgets were derived.** No primary source gives word counts. They come from the legibility floor instead. On a 2000 px square seen 390 CSS px wide on a phone:
- 11 CSS px is 56 px in the file;
- 24 CSS px is 123 px.

Allowing 5% margins, a headline at about 120 px fits about 25 to 30 characters per line.

**1. Main image (hero packshot).**
- **Job:** win the search tile, about 120 to 180 CSS px wide on a phone. Measured: eBay 120, Amazon 129, Daraz 174, Dawn 177.5.
- **Anatomy:** the whole product, front or three-quarter view, on pure white (Amazon: RGB 255; TikTok and others: white). It fills the frame: Amazon at least 85%, Google 75 to 90%, TikTok beauty about 80%. Soft contact shadow only. One unit, unless it is a multipack.
- **Copy:** none.
- **Do:** shoot the variant being sold. Keep the angle and scale consistent across the catalogue (NN/g, "Product photos on listing pages", 27 Feb 2022).
- **Don't:** props that do not ship, badges ("Best seller", "-40%"), watermarks, borders, collages, renders or placeholders. Each is a suppression or rejection cause on at least one platform (section 7).

**2. Infographic (feature callouts).**
- **Job:** answer the top three to five questions at thumbnail speed.
- **Anatomy (practice):** the product large (about 55 to 65% of the frame), with three to five callouts joined by thin leader lines to the part they describe. Put a short headline at the top or left.
- **Copy budget (practice, from the legibility floor):**
  - headline of 6 words or fewer, 2 lines at most, about 120 px or more on a 2000 px canvas;
  - each callout 2 to 5 words at 56 to 80 px;
  - at most about 25 words on the whole image.
- **Do:** repeat the facts in bullets and alt text. Baymard found 64% of sites handle text inside images badly for accessibility (10 Aug 2021). Keep 4.5:1 contrast (NN/g, text over images).
- **Don't:** use it on platforms that ban text (section 1.2), or make claims you cannot substantiate.

**3. Lifestyle / in use.**
- **Job:** show context, scale and who the product is for.
- **Anatomy:** a real person or setting using the product. The product should be obvious at a glance and take at least about a third of the frame (practice). For wearables, show real models of several body types and state the model's size (Baymard, 1 Dec 2020).
- **Copy:** none, or a 3 to 5 word caption band.
- **Evidence:** NN/g eye-tracking. Users study real product photos and ignore generic stock scenes (Photos as web content, reviewed 13 Aug 2026).

**4. Scale.**
- **Job:** remove the "how big is it?" doubt.
- **Anatomy:** the product in a hand, on a person, or beside an object everyone knows (a coin, phone, A4 sheet, 500 ml bottle). Amazon names a "PT12" scale image with rulers.
- **Copy:** one measurement label at most.
- **Evidence:** Baymard, 42% of users judge size from images; 37% of sites lack an in-scale image.

**5. Dimensions.**
- **Job:** give exact sizes for fit.
- **Anatomy:** a clean line drawing or photo with dimension lines. Put each number next to the part it measures. Show both units where the market needs them (cm plus inches for global; cm for Bangladesh).
- **Copy:** numbers only, 56 px or larger. Baymard: readable without zooming on mobile, and repeat the numbers in text beside the image.

**6. Comparison.**
- **Job:** push the buyer up to a better model or across to a bundle.
- **Anatomy:** a 2 to 4 column chart of your own products, with ticks and short values.
- **Copy (practice):** row labels of 1 to 3 words; at most 5 to 6 rows on a square image.
- **Don't:** name or picture competitors. Amazon A+ rejects competitor comparisons; its A+ comparison chart module takes up to 6 products and 10 rows as live text, which is better than a picture of a table.

**7. In the box.**
- **Job:** show everything included. Missing on 31% of sites; 63% of users were unsure without it (Baymard).
- **Anatomy:** a flat lay or knolling of every included item, with quantity labels (for example "x2").
- **Don't:** show optional accessories without marking them as sold separately. 13% of sites fail at this (Baymard).

**8. Texture or detail close-up.**
- **Job:** material, finish and quality, which zoom cannot fully give.
- **Anatomy:** a macro of the fabric, surface, stitching, port or ingredient. Amazon has a "PT88" texture slot (500x500 or larger).
- **Copy:** none, or a 2 to 3 word material label.

**Video (bonus slot).**
- Amazon allows up to 4 shoppable videos. It claims an average 23.8% sales lift (Amazon internal data, 2024, vendor claim).
- Recommended length: 30 to 90 s, with the key feature in the first 5 to 10 s, and text overlays for sound-off viewing.
- Watch out: Amazon's video page says videos show in the main media block only when there are fewer than six images. That conflicts with its "six images" advice.
- Other platforms:
  - Etsy: 2 videos, 3 to 15 s, no audio.
  - TikTok Shop US: 1 video, 5 MB.

### 1.4 Render sizes for the stack
- **One square master:** 2000x2000 covers Amazon, Shopify, WooCommerce, eBay and Google Shopping.
- **Smaller copies:** export 1000x1000 for Daraz, Lazada and Shopee, where the file caps are 1 to 2 MB.
- **Etsy:** Etsy prefers landscape, 2667x2000 (see section 6).
- **Fashion portrait masters:**
  - Amazon Fashion: 10:13 (`amazon-apparel`).
  - Myntra: 3:4, 1080x1440 observed.
  - Flipkart: about 3:4 observed.
- **Export:** sRGB, JPEG at quality 80 to 90.
  - Under 1 MB: Etsy, Lazada and Daraz.
  - Under 2 MB: Shopee, A+ modules and the TikTok Shop header.
  - Under 5 MB: Amazon Store tiles.

---

## 2. A+ content storytelling (Amazon)

### 2.1 What the modules are
**Basic A+** (Amazon's "Types of A+ Content" sheet, modified 13 Jan 2026):
- up to 5 modules, 14 module types;
- sits under "Product description".

**Premium A+:**
- up to 7 modules, 19 types;
- adds video, hotspots, carousels, Q&A and 1464 px wide images;
- eligibility is shown in Seller Central.

**Brand Story:**
- up to 19 modules, 4 types;
- cards are 362x453;
- sits under "From the brand" on every listing of the brand.

Only one enhanced description (Basic or Premium) can be live on a listing.

**Minimum image sizes** (Amazon SP-API documentation):

| Module | Minimum |
|---|---|
| Company logo | 600x180 |
| Image header with text | 970x600 |
| Image and text overlay | 970x300 (KDP recommends 1940x600) |
| Single image and sidebar | 300x400, sidebar 300x175 |
| Three images and text, single side image, multiple image A, highlights, specs detail | 300x300 |
| Four image/text | 220x200 (Jungle Scout says 220x220) |
| Four image quadrant | 135x135 |
| Comparison chart | 150x300 per product |

**File rules:** images 2 MB or less; alt text up to 100 characters.

**Render at 2x the minimum.** Amazon's own KDP A+ help recommends exactly 2x for the overlay and three-image modules.

### 2.2 The story arc (a practice recipe that stays inside Amazon's rules)
1. **Hook (image header, 970x600).**
   - One lifestyle image showing the product in its best moment.
   - Put the promise in the live headline (150 characters), not in the image.
2. **Three reasons (three images and text).**
   - Three benefits, each with a close-up and a 2 to 4 word live headline.
3. **Proof or detail (single image and sidebar, or image with highlights).**
   - Materials, certification and how it works.
   - Awards must name the body and the year (Amazon's A+ guide).
4. **Use or routine (overlay, or four image/text).**
   - Steps or scenarios. Keep the text side of an overlay image calm.
5. **Choose your model (comparison chart).**
   - Your own range only. The chart is live text and shoppable (Add to Cart).
6. **Brand Story carousel.**
   - Who you are, plus cards linking to other products and the Store.

### 2.3 Rules that decide approval
**Rejected** (Amazon A+ design guide, 24 Sep 2025):
- prices, promotions or shipping details;
- QR codes, links or contact details;
- "best-selling" or "top-rated" claims;
- warranty or guarantee claims;
- competitor references;
- low-resolution or animated images.

**Also rejected** (KDP A+ guidelines):
- time-sensitive words ("new", "now", "latest");
- customer reviews;
- more than one logo.

**Text in images.** Amazon advises against embedding text in images, because phones shrink it. The Basic column is 970 px wide on desktop and scales to about 390 CSS px on a phone, a factor of about 0.4. So baked-in words need to be at least about 27 px in a 970 px image (60 px or more for headings), which is about 55 px and 120 px at the 2x render.

**Evidence and claims.** Amazon says Basic A+ can lift sales by up to 8% and Premium by up to 20% (Amazon internal data, no method: treat as a vendor claim).

---

## 3. Store banners

### 3.1 Amazon Brand Store (Amazon Ads specs, re-checked)
**Hero:**
- at least 3000x600, 5 MB;
- up to 15% of the width is cropped on each side, so all copy and products go inside the centre 2100 px.

**Amazon's mobile tips:**
- header copy under 30 characters;
- text at least 90 pt;
- no more than 3 products in the header.

**Tiles** (minimums; 3000 px wide recommended):
- full width 1500 px wide, flexible height;
- large 1500x1500;
- medium 1500x750;
- small 750x750.

**Link-title bars** cover about 19% of a rectangular tile and about 12% of a square one, at the bottom (the JSON keepouts).

**Tiles with small text:** Amazon discourages text inside tile images and says to upload a separate mobile image for them.

**Evidence** (Amazon data, vendor claims):
- 78% of Store visits came from mobile in Q1 2024.
- Stores updated within the last 90 days saw 9% more repeat visitors and 10% more sales per visitor (2024 data).

### 3.2 Marketplace store banners

| Platform | Banner | Size | Notes |
|---|---|---|---|
| eBay Stores | Billboard | 1280x290 | Logo 300x300, marketing banner 640x640, 12 MB (eBay help) |
| Etsy | Big banner | 1600x400 (min 1200x300) | Existing `etsy-banner` |
| Etsy | Mini banner | 1600x213 (min 1200x160) | |
| Etsy | Carousel (Etsy Plus) | 1200x300 | |
| Etsy | Logo | 500x500 | |
| TikTok Shop (US) | Header background | 780x720, 2 MB | Logo PNG/WEBP, transparent; also shown mid product page |
| Shopify Dawn | Image banner / slideshow | 3840x1440 master | Heights 420/560/720 px desktop and 280/340/390 px phone; phones see about the centre square |
| Lazada (Daraz proxy) | Store header | 1200x128 desktop; 750x478 app | Logo 600x600; single banners 1200 wide x 50 to 2000 px, 1 MB (section 9.1) |
| Shopee | Shop cover and carousel | 1200x675; carousel 2000x1000, 2000x1125 or 2000x2000 | 2 MB; no contacts or other marketplaces (section 9.2) |
| Noon | Store banner | 1440x240 minimum (6:1) | Sides may crop; separate English and Arabic banners (section 9.4) |

### 3.3 Banner craft that holds up
- **Put text in HTML where the platform allows it.**
  - Shopify: slideshow and background images should not contain text, because the theme moves or crops it (Shopify help).
  - Baymard: slide text should be real HTML, because shrunk desktop images make text unreadable on mobile (3 Apr 2025).
- **Carousels:**
  - Use 5 slides or fewer and never auto-rotate on mobile (NN/g, reviewed 7 Aug 2026).
  - The first slide gets most of the attention. On ND.edu, about 1% of visitors clicked the carousel, and 84% of those clicks were on slide 1 (Erik Runyon, 2013, practitioner data).
- **Design for the crop, not the canvas.**
  - Place the subject and any words inside the documented safe box (Amazon centre 2100 px; Dawn centre square).
  - Set focal points where the platform supports them (Shopify Dawn 7 and later; Eventbrite).
- **Copy budget (practice):** headline of 6 words or fewer, support line of 12 words or fewer, one call to action. Amazon's own limit for Store headers is under 30 characters.

---

## 4. App store screenshot storytelling

### 4.1 What decides the install
**Apple (official):**
- Up to 10 screenshots.
- When there is no app preview, the first one to three screenshots appear in search results; orientation decides how many (Apple, App Store product page).
- App previews autoplay muted, and a portrait preview takes the first gallery slot.
- Up to 3 previews, 15 to 30 s.

**Google (official):**
- Up to 8 screenshots per device type.
- Prioritise UI in the first three screenshots.
- Taglines should not take more than 20% of the image.
- Screenshots may appear in search and on the home page, not only on the listing.
- Recommendation formats require at least 4 screenshots of 1080 px or more for apps, and 3 for games.

**Apple's own test results** (Product Page Optimization page, official case studies):
- **Simply Piano** (12 days): the screenshots-only original beat the version that led with an app preview video. Apple's page shows a 3% conversion difference. A video is not automatically better.
- **Peak Brain Training** (44 days): out of 3 icon designs tested against the control, the brain icon won by about 8% (over 98% confidence). The robot icon was about 3.5% worse.

Apple Product Page Optimization tests up to three alternate versions against the original. Google Play store listing experiments test icon, feature graphic and screenshot variants.

**Vendor claims (no method published):**
- SplitMetrics (updated 14 Sep 2026): users decide within about 7 seconds of opening a product page.
- AppTweak (21 Nov 2025): users rarely scroll past the first three screenshots.

**Consequence:** screenshots 1 to 3 must work as a set at thumbnail size. Portrait screenshots in iPhone search results are about a third of the screen width each (estimate: about 115 CSS px), so a 1320 px wide screenshot is scaled by about 0.09 there. A caption needs to be about 120 px or larger in the file to stay near 11 CSS px, and about 200 px or larger to read as a headline.

### 4.2 The sequence (practice)
1. **Screenshot 1:** the core promise, with the best real screen, a 2 to 5 word caption and optional social proof. Apple bars unverifiable claims in metadata (2.3.7). Google bans ranking, award and testimonial claims in screenshots.
2. **Screenshots 2 and 3:** the two strongest features, one per image, each showing real UI (Google says so explicitly).
3. **Screenshots 4 to 6 or more:** secondary features, personalisation, integrations and trust (security, offline, languages).
4. **Last screenshot:** a recap or brand close. No "Download now": Google bans calls to action in screenshots.
5. **Dark Mode:** if the app supports it, Apple suggests including at least one dark screenshot.

### 4.3 Captions
- **Length (practice):** 2 to 6 words, one idea, benefit first.
  - Google: keep text minimal, taglines 20% of the area or less, localise the text.
  - Apple: captions and overlays are allowed (2.3.3), but no prices (2.3.7).
- **Placement:** top 20 to 25% of the canvas on phones (practice). Keep the phone status-bar area of the UI clean. Google asks for full battery, Wi-Fi and signal icons and no notifications.
- **Size:** on a 1320 px Apple canvas, captions of 120 to 180 px. On a 1080x1920 Play canvas, 90 to 130 px (derived from the thumbnail arithmetic above).
- **Localise:** captions are text, so each language needs its own set (Apple and Google both say so).

### 4.4 Device frames: yes or no
- **Google Play: avoid them.**
  - Its preview-asset rules list device imagery among elements to avoid, for both the feature graphic and screenshots, because it dates quickly and can alienate users.
  - Wear OS screenshots must not use device frames at all.
- **Apple: not required and not banned.**
  - Overlays are allowed (2.3.3).
  - Other platforms' devices or names are not allowed (2.3.10).
  - Any frame shrinks the real UI.
- **Evidence.** No public A/B data on frames with a stated method was found. Apple's published PPO cases cover a preview video and icons, not frames. One former source of such studies (storemaven.com) now serves unrelated content and was not used. Decide by testing: use Apple Product Page Optimization or Google Play store listing experiments, with frameless and framed variants of screenshots 1 to 3.
- **Default for the skill:** frameless, full-bleed UI with a caption band. It is compliant on both stores and gives the most UI per pixel. A frame at 85% of the canvas width keeps only about 72% of the UI area (0.85 squared), which is arithmetic, not a study.

### 4.5 Sizes to design once
- **Apple iPhone:** 1320x2868. It covers 6.9-inch, and 6.5-inch is optional.
- **Apple iPad:** 2064x2752, if the app runs on iPad.
- **Mac:** 2880x1800.
- **Google phone:** 1080x1920. This is a different aspect ratio (0.5625 against Apple's 0.46), so design it separately rather than cropping the Apple set.
- **Google tablets and Chromebook:** 1920x1080 or 1080x1920.
- **Chrome Web Store:** 1280x800, shown at 640x400.
- **Microsoft Store:** 1920x1080 or 3840x2160, with nothing important in the bottom third.
- **Steam:** 1920x1080, gameplay only, no text.

---

## 5. Course and event covers

| Platform | Size (render) | Text | Crop to design for | Source |
|---|---|---|---|---|
| Udemy | 750x422 minimum (render 1500x844) | Not allowed (logo only) | The app crops to the centre square | support.udemy.com, 10 Jul 2026 |
| Skillshare | 1280x720 | Avoid text and icons | Keep the top-left clear (Staff Pick badge) | help.skillshare.com, 11 Sep 2025 |
| Teachable | 1024x576 thumbnail; banners 1800x600 or 1500x800 | Allowed | Responsive pages crop | support.teachable.com, 1 Jul 2025 |
| Thinkific | 760x420 card, 4 MB; banners 1440x720 | Card: not restricted; banners: no text | Banners crop at top/bottom and sides | support.thinkific.com, 2025 to 2026 |
| Kickstarter | 1024x576 | Avoid banners, badges, extra text | Also the social share image | kickstarter.com/help/images (Wayback, 2024) |
| Eventbrite | 2160x1080 (2:1) | Allowed | The search thumbnail is a SQUARE crop from your focus point | Eventbrite help |
| Luma | Square, 800x800 or larger | Little | Square everywhere; used for the share image | help.luma.com |
| Meetup | 1200x675, 16:9 (group cover minimum) | Allowed | Event photo size not stated | help.meetup.com |
| Facebook event | No official pixel size (Meta Help) | Allowed | Hosts reposition on upload | facebook.com/help/1910675759253872 |

**Recipe (practice):**
- **One subject, one idea, one focal point.** Udemy asks for exactly this and rejects busy images.
- **Run the "square test."** Check that the cover still makes sense as a centre square: Udemy app, Eventbrite search, Luma everywhere.
- **Keep titles live.** Udemy, Skillshare, Thinkific banners and Apple in-app events all ask for no baked-in title. The platform prints the title next to the image.
- **Where text is allowed** (Eventbrite, Meetup, Facebook): keep it to the event name and date, inside the centre square, with 4.5:1 contrast.

---

## 6. Corrections to existing presets

### `shop-square` (2048x2048)
- **Size:** keep it. Shopify says 2048x2048 usually displays best for square product images, and the size also satisfies eBay (about 1600), Google (about 1500), Meta (1024) and Amazon (500 to 10,000).
- **Label:** "Shopify, eBay, Merchant Center" undersells it. Add Amazon, WooCommerce, TikTok Shop, Daraz and Meta catalogue as aliases, or keep the dedicated presets now in `commerce.json`.
- **`view_width_px` 400 is the product-page view.**
  - The make-or-break view of a main image is the search or collection tile, about 120 to 180 CSS px on a phone (measured: eBay 120, Amazon 129, Daraz 174, Shopify Dawn 177.5).
  - Suggest `view_width_px: 180` for the main-image use, or a note saying so. Text is banned on main images anyway, so this changes guidance, not the text floor.
- **`notes`:** say "main image" rules differ by platform:
  - Amazon: pure white RGB 255 and 85% fill.
  - Google: 75 to 90% fill; no overlays; 500x500 is the hard minimum from 31 Jan 2027.
  - eBay, TikTok Shop (US) and Google ban added text on every image, not only the main one.
  - Daraz rejects price or contact text.
- **Limits worth adding:**
  - Shopify product media: up to 5000x5000 or 25 MP, under 20 MB.
  - Shopify theme images: 20 MP and 20 MB.
  - Colour: export sRGB. Shopify strips embedded profiles; Etsy converts to sRGB.

### `etsy-listing` (2000x1500, safe 180/240)
- **Size fails Etsy's own recommendation.**
  - Etsy's help (updated 23 Sep 2026) recommends listing photos with a width and a height of at least 2000 px each. 1500 px tall misses that.
  - Change to **2667x2000** (the smallest 4:3 that meets both) or 3000x2250.
  - Etsy still warns that files over 1 MB may not finish uploading on slow connections, so export JPEG at about 80.
- **Safe area does not protect the crops.**
  - Etsy crops thumbnails to square, portrait and landscape. From a 4:3 master, the square crop keeps the centre 2000 px of 2667 (333 px off each side).
  - Etsy does not document the portrait crop ratio. At 3:4 it keeps only the centre 1500 px (583 px off each side).
  - Suggested safe at 2667x2000: `[160, 583, 160, 583]`. The subject sits in the centre 1500x1680; the scene and negative space fill the rest.
  - The current 240 px side margin protects neither the square nor the portrait crop.
- **Orientation:** Etsy says the first photo should be landscape or square, and the same page advises against square crops in favour of horizontal images. Keep 4:3 landscape as the default.
- **Other facts to add:**
  - Up to 20 photos and 2 videos.
  - Supported formats: jpg, gif, png, svg, heic. Animated GIF and transparent PNG are not supported, and transparent areas turn black.
  - A dark, blurry or collage first photo can rank lower.
  - The first photo must be 635 px or more to avoid ranking lower.
  - The thumbnail preview tool shows the crops before publishing.

### `etsy-banner` (1600x400)
- **Size:** confirmed as the Etsy big shop banner: recommended 1600x400, minimum 1200x300 (Etsy help, 23 Sep 2026).
- **Changes:**
  - Rename the label to "Etsy big shop banner 4:1" and add `min_size [1200, 300]`.
  - The 60 px side safe is practice. Etsy does not document the mobile crop, so keep the message in the centre half.
  - The 1 MB warning applies to all shop images.
- **New related presets in `commerce.json`:** `etsy-mini-banner` (1600x213), `etsy-carousel-banner` (1200x300, Etsy Plus), `etsy-logo` (500x500) and `etsy-receipt-banner` (760x100).

### `fb-event-cover` (1920x1005): verified as "no official size"
- Meta's Help Center article on event cover photos gives no pixel dimensions. It says hosts can reposition the photo and cannot resize it after adding it. Meta's own support assistant says the same.
- Keep 1920x1005 labelled third-party. Its 1.91:1 ratio matches Meta's link-image convention, but that is inference.

---

## 7. Rejection and policy traps

### Amazon
- **Main image that is not compliant** (non-white background, less than 85% fill, text, logos, badges, props, renders, placeholders, multiple views): the listing can be suppressed from search and appears in "Suppressed listings". Sources: Amazon style guides; third-party guides list the automatic triggers.
- **Apparel on the MAIN image:**
  - models must stand;
  - a visible mannequin or hanger is refused;
  - children's underwear and swimwear must be shown flat.
- **A+ content is rejected for:**
  - prices, promotions or shipping details;
  - QR codes, links or contact details;
  - "best-selling" or "top-rated" claims;
  - warranties or guarantees;
  - competitor comparisons;
  - low-resolution or animated images;
  - time-sensitive words (KDP);
  - customer reviews (KDP).
- **Sponsored Brands custom images are rejected for:**
  - added text (text on the packaging is fine) or logos;
  - a packshot on a solid or transparent background;
  - reusing one of the ad's selected product images;
  - letterbox or pillarbox bars.
  - Ads without a border also cannot use a white or off-white background.
  - Logos must not include extra text or product photos.
- **Amazon Posts:** retired in 2025. Do not design for it.

### eBay
- Added borders, text, artwork, marketing and watermarks (including ownership credits) are prohibited on listing photos.
- Stock photos are prohibited for used items.
- eBay says badges and logos can hurt search placement.

### Google Merchant Center
- **Disapproved:** promotional overlays (price, CTA, "free shipping", condition), watermarks, logos not on the product, borders, placeholders, generic images and upscaled thumbnails. Automatic image improvements can strip overlays if they are switched on.
- **Minimum size:** 500x500 becomes the minimum for all products from 31 Jan 2027.
- **AI-generated images:** keep their IPTC `DigitalSourceType` metadata (Merchant Center help, as read by a research agent; re-check before relying on it).

### Meta catalogue
- **Ads:** text over the product, calls to action, promo codes, watermarks and time-sensitive prices break the image guidance; ads are also held to Advertising Standards.
- **Shops:** Commerce Policies apply.
- **Changed images:** a replaced image needs a new URL, or Meta keeps the old one.

### TikTok Shop (US and UK)
- The US policy bans added logos, text, borders, watermarks and graphics on **every** product image, not only the main one.
- The main image must be a front view on pure white.
- Marketing or promotional stickers can cause rejection.
- Black-and-white images, mosaics and filters are not allowed.
- Placeholders and renders are not allowed.
- Information that sends buyers off TikTok Shop is not allowed.
- Children's swimwear and underwear must be flat.
- Header images are hidden automatically if the system judges them low quality.
- **UK:** the best-practice page (17 Nov 2025) sets at least 800x800 per image (the US policy says 600x600). It allows the product's own branding or logos, but no other text or watermarks.

### Daraz (Bangladesh, Pakistan, Sri Lanka, Nepal)
- Text on images (price, phone or WhatsApp numbers, links) is a stated rejection reason (Daraz Image Guidelines, 28 Feb 2024).
- **Product Image Policy** (13 Jul 2026): real-model images that expose restricted body areas, and see-through garments, are not allowed. The first violation removes the product; the second brings 48 non-compliance points and delisting. Mannequins and flat lays are allowed.
- **Duplicate Products Policy:** reused images or titles for the same product lead to deactivation or locking of the lower-selling copies.
- **Declutter:** web-sourced images and the same image URL plus title as other shops are flagged. Upload at least 4 angles.
- **Brand-owned images** need the brand's authorisation (Pakistan listing policy).

### Lazada
- Frames, collages, off-centre products, low resolution and text-only images lower the image quality score.
- Promotion images with watermarks, borders or marketing copy, or with the wrong ratio, are dropped.
- Obscene images: up to 2 non-compliance points and the listing is locked.

### Shopee
- Watermarks, irrelevant images, photos grabbed from other sites, and links or contact information are listed violations; inappropriate images are deboosted.
- The listing-quality score penalises non-1:1 covers, white borders, a product over 90% or under 85% visible, and text or graphics over 25% of the background or on the product.
- Mall: text rules per country, and the first 3 images must be the actual product.
- Thailand bans on-image text in languages other than Thai or English.

### Mercado Libre
- Covers that are not on pure white, or that carry logos, text, watermarks, borders, QR codes or contact details, are flagged as poor-quality thumbnails and pushed down.
- Imitating Mercado Libre's own badges ("Más vendido", "Full") is not allowed.

### Noon
- Logos, watermarks, borders, price, warranty text or expiry dates on the image cause rejection.
- Only JPEG is accepted.
- Images under 660 px wide, or narrower than 1:2, fail the requirements.

### Allegro
- No store text or logo on images.
- Infographics are for invited sellers only, and never as the thumbnail.

### Tokopedia
- Watermarks, collages and heavy text are not allowed (archived rules).
- Official Store: text 30% or less of the main image.

### Etsy
- Transparent PNG areas render black; animated GIFs are not supported.
- A dark, blurry or collage first photo ranks lower.
- A first photo under 635 px ranks lower.
- Having no shop logo may reduce search visibility.
- Images of minors must follow Etsy's policy.

### Shopify and WooCommerce
There is no platform rejection. The trap is cropping: text baked into slideshows gets cut on phones. Dawn fixed-height banners show only about the centre square on a phone.

### Apple App Store
- **2.3.3:** screenshots must show the app in use, not only title art, a login screen or a splash screen.
- **2.3.4:** previews may use only screen captures of the app.
- **2.3.7:** no prices in names, subtitles, screenshots or previews. App names are limited to 30 characters.
- **2.3.8:** icons, screenshots and previews must suit a 4+ audience.
- **2.3.10:** no names, icons or imagery of other mobile platforms or app marketplaces.
- **Screenshots:** no alpha channel or transparency.
- **In-app events:**
  - specific prices lead to rejection;
  - avoid unverifiable claims ("the best", "#1").

### Google Play
- **Metadata policy:** no text or images in the title, icon or developer name that indicate store performance, ranking, price or promotion, or a link to Google Play programmes. Examples:
  - "#1", "App of the year", "Best of Play 20XX", "Popular";
  - "10% off", "free for a limited time";
  - "Editor's choice", "New".
- **Preview assets:**
  - avoid "Best", "#1", "Top", "New", "Free", "Discount", "Sale" and "Million Downloads";
  - no calls to action ("Download now");
  - no device imagery and no store badges;
  - no people interacting with the device;
  - taglines take 20% of the image or less.
- **Icons:** misleading symbols, such as a fake notification dot or a download symbol on an unrelated app, are not allowed.
- **Other formats:**
  - Wear OS: no frames or added text.
  - Android Automotive: generic system UI only.

### Microsoft Store
- No title or text on the 16:9 super hero art.
- Nothing key in the bottom third of posters, box art, hero art and screenshots (text overlays and gradients).
- No extra logos or marketing messages on screenshots.
- Trailers must not include age ratings (inside the Store).

### Chrome Web Store
- Promo images are reviewed and can be rejected (reasons are shown in the dashboard).
- Items without a small promo tile are listed after items that have one.

### Steam
- Base capsules may carry only game art, the name and the official subtitle:
  - no review scores, awards, discount copy or other products;
  - update text only through a one-month, localised Artwork Override.
- Screenshots must be gameplay only.
- Library hero: no text at all.
- Games that break these rules may have their visibility limited and become ineligible for featuring in Steam sales and events.

### Courses and events
- **Udemy:** course-image violations are among the most common reasons a course is rejected in quality review. No course title text; no frames, borders or letterboxing; one image per course.
- **Skillshare:** text and icons hurt thumbnails; keep the upper-left clear for the Staff Pick badge.
- **Kickstarter:** avoid banners, badges and extra text.
- **Eventbrite:** you must own the image or have permission.

---

## 8. Bangladesh notes

### 8.1 Daraz (Bangladesh, Pakistan, Sri Lanka, Nepal)

**What Daraz publishes openly** (Daraz University, read in a browser):
- **Text on images.** To avoid image-related rejections, do not include text in the image, for example price, any contact information or external links (Daraz Image Guidelines tutorial, Bangladesh, 28 Feb 2024, in English and Bengali). Daraz's own "bad" example images show:
  - a phone-number watermark across a product;
  - a price-and-discount overlay ("175/- 105/- Taka Only", "40% off").
- **Product Image Policy** (published the same day, 13 Jul 2026, in Bangladesh, Pakistan, Sri Lanka and Nepal; Bangladesh text read):
  - Mannequins, dress forms and flat lays are allowed, including for lingerie and swimwear.
  - Real-model images that expose or emphasise body areas restricted under local cultural rules are not allowed, and neither are sheer or see-through garments that show the body.
  - First violation: the product is removed. Second: 48 non-compliance points and the seller is delisted.
- **Declutter criteria** (Content Issues and Solutions Center, 28 Feb 2024):
  - Upload at least 4 images from different angles.
  - Items with the same image URL and title as another seller's are decluttered: use your own or Daraz-assisted photography, not web images.
  - Non-performing SKUs are suspended after 12 months without sales.
- **Duplicate Products Policy** (Bangladesh, 1 Apr 2026; also in Pakistan, Sri Lanka and Nepal):
  - One listing per product.
  - Reusing images, titles or descriptions to create another listing of the same product counts as a duplicate.
  - The lower-selling duplicates are deactivated or locked.
- **Pakistan Product Listing Policy** (23 Apr 2026):
  - Upload real images of the actual product.
  - Brand-owned images need the brand's written authorisation.
  - Images must match the exact variant and packaging.

**What is not open.**
- Pixel limits, file size, the white-background rule and Store Decoration banner sizes sit inside Seller Center or in downloadable PDFs and videos. The "Daraz Image Guidelines - BD.pdf" (28 Feb 2024) and "English - Fashion Photography Guide.pdf" (21 Aug 2026) were not downloaded; downloads need the user's approval.
- The "All About Store Decoration" article showed no body text without a login.
- Daraz runs on Alibaba's Lazada seller platform, so Lazada's published limits are the best proxy (section 9.1, labelled as Lazada).

**What Daraz actually serves** (measured on a 375 px phone, 24 Sep 2026):
- The search tile image is 174 CSS px wide.
- The product page image is full width and square: 375x375 CSS px, served as 720x720 WebP.
- Originals seen on one listing were 1254x1254, 4032x3024, 3313x2484 and 1133x2428, so Daraz does not force a size or ratio. The product-page frame is square, so non-square uploads waste space.
- **Design rule:** square masters, product centred and large, readable at 174 px.

**Proxy sizes from Lazada** (section 9.1):
- Product images 330x330 to 5000x5000, up to 8 per field, 1:1 and white recommended.
- 1000x1000 recommended for promotion squares.
- Keep files under 1 MB, because Lazada's own API docs disagree on 1 MB versus 3 MB.
- Store Builder header 1200x128 (desktop) and 750x478 (app); logo 600x600; banners 1200 px wide.

**Recommended presets:**
- `daraz-product` (1000x1000, 1:1, no text, no contact details, no price);
- `lazada-store-header-app`, `lazada-store-header-pc` and `lazada-store-banner` for Daraz store decoration, to confirm in Seller Center.

### 8.2 Other Bangladeshi platforms

None of these publishes a public seller or vendor image guideline that could be found. What they serve (measured 24 Sep 2026, practice):

| Platform | Type | What it serves |
|---|---|---|
| Chaldal | Grocery, mostly first-party | Product pictures 400x400 (1:1) |
| Pickaboo | Electronics | Product originals 600x600 (1:1), shown as 380x380 |
| Othoba | Marketplace (nopCommerce) | Thumbnails at 200, 300 and 1200 px widths |
| Rokomari | Books | Covers served at 260x372 and 130x186 (about 0.70, a typical book-cover ratio) |
| Shajgoj | Beauty | Hero sliders 2880x735 and 1920x490 on web (about 3.9:1); 980x632 in the app (about 1.55:1). Two different compositions, not one crop |

**Rule for these sites (practice):** deliver a square 2000x2000 master on white, plus the site's banner sizes on request. Their banners are made by their own teams, so ask for the current slot size before designing.

### 8.3 Facebook-commerce sellers (note only)
- **What Bangladeshi F-commerce sellers bake into product posts** (common practice, not measured):
  - price, "Cash on Delivery" and home-delivery badges;
  - phone or WhatsApp numbers and page watermarks;
  - Bengali offer text.
- **These habits break the rules** of Daraz, TikTok Shop, Meta catalogue, Google Shopping and eBay. Daraz uses exactly such images as its rejection examples.
- **Keep two sets of images:**
  - Social posts: `fb-square`, `ig-portrait`, `ig-story`. Offer text is fine there, within Meta's ad and commerce policies.
  - Catalogue and marketplace images: clean, square, white, no text.
- **Bengali text needs more size.** The skill's own judge already asks for about 12 CSS px seen size for Bengali (denser than Latin), so offer lines in Bengali need about 10% more pixel height than the `min_text_px` floor.

---

## 9. Regional marketplaces: quick reference

Read from each platform's own pages unless marked. Presets: `lazada-*`, `daraz-product`, `shopee-*`, `tokopedia-product`, `noon-*`, `mercadolibre-*` and `allegro-product`.

### 9.1 Lazada (and the Daraz proxy)

**Product images:**
- **Size range:**
  - 330x330 to 5000x5000, with up to 8 images per field (2021 guide; the API says the same).
  - The 2019 guide said 300 to 5000, recommended 500x500 and 1:1, and at least 3 images.
- **Promotion images** (Open Platform, 28 Mar 2023):
  - Square: 1:1, minimum 330, **1000x1000 recommended**, pure white or transparent background.
  - Long: 3:4 at 750x1000.
  - JPG or PNG, 3 MB.
  - No watermarks, borders or marketing copy.
  - A wrong ratio is dropped silently.
- **File size conflict:** the API upload doc says 1 MB; the community answer and the error text say 3 MB.
- **Quality score:**
  - A white background is recommended; a 1:1 white image "may boost visibility" on the homepage.
  - Frames, collages, off-centre products, low resolution and text-only images score 1 to 3 out of 5. A clean background scores 5.
  - Obscene images: up to 2 non-compliance points and the listing is locked.

**Store Builder** (Lazada University courses, 3 Nov 2025 and 11 Mar 2026):

| Slot | Size |
|---|---|
| Header, desktop | 1200x128 |
| Header, app | 750x478 (a 2021 LazMall PDF said 750x180) |
| Store logo | 600x600 |
| Category cover | 500x500 |
| Single banner | 1200 wide x 50 to 2000 px, 1 MB, up to 32 |
| Carousel | up to 6 images at 1200 or 1920 wide |
| Multi-clickable banner | 1200 or 1920 wide, up to 8 hotspots |
| 3-image banner | 600x300 |
| 4 and 5-image banners | 291x291 |

**Daraz uses the same seller platform.** Its own Store Decoration sizes were not readable, so treat these as the best available proxy and check them in Daraz Seller Center before a big campaign.

### 9.2 Shopee

**Product images:**
- **Count:** up to 9 including the cover (Taiwan 9 or 12).
- **Minimum:** 500x500 at 72 dpi.
- **Ratio:** 1:1 mandatory; 3:4 optional. 3:4 images are auto-cropped and may clash with campaign frames.
- **File size:** Seller Centre caps uploads at 2 MB (the API allows 10 MB).
- **Cover:** the product fills at least 70%, preferably on white, with no text or graphics.

**Listing-quality score** (Singapore, 6 Jul 2026; same in Indonesia and Malaysia). An image counts against you when:
- under 85% of the product is visible;
- it has white borders or edge space;
- it is not 1:1;
- the background is under 10% of the image, or the product is over 90%;
- text, graphics or watermarks take more than 25% of the background, or sit on the product.

**Violations** (Philippines, 25 May 2026):
- watermarks;
- irrelevant images;
- photos taken from other sites;
- links or contact information;
- for Mall listings: text concerns, and the first 3 images must show the actual product.

**Mall and official-store covers by country:**
- Singapore: logo top-left, 10% or less; at least 60% fill; no watermarks, montages, borders or text.
- Thailand: one banner strip, top or right only, 30% or less; logo 10% or less; product at least 60%.
- Taiwan: text 20% or less; product 80% or more.
- Philippines and Indonesia: allow edge text or graphics.

**Badge overlays** (Vietnam example):
- Mall or Preferred badge at top-left;
- discount badge at top-right;
- campaign strip along the bottom;
- Sponsored tag at bottom-right.

Keep the product and any allowed text clear of these corners.

**Shop decoration:**
- Cover 1200x675, 2 MB.
- Carousels at 2:1 (2000x1000), 16:9 (2000x1125) or 1:1 (2000x2000), up to 6 images.
- Single image and hotspot components 1200 wide, 100 to 2200 px high.
- Banner and category components 1200 wide, 100 to 900 px high.
- Campaign page 1200x600.
- No contacts, links to other marketplaces or Shopee logos.

**Description images:**
- ratio 0.5 to 32, 2 MB, up to 12;
- minimum 1000x32 (Singapore, Malaysia, Indonesia) or 700x32 (Philippines, Thailand, Brazil).

### 9.3 Tokopedia (Indonesia): archived pages only
From Wayback copies dated 2022 and 2024:
- 5 photo slots, square;
- minimum 300x300, maximum 2048x2048, "optimal" 700x700;
- plain or white background; no watermark, collage or heavy text;
- Official Store: product about 70%, text 30% or less.

The live pages could not be read, and Tokopedia now runs with TikTok Shop, so check before use.

### 9.4 Noon (UAE, Saudi Arabia, Egypt)
**Product images** (help centre, 22 Apr 2026):
- JPEG only; width 660 px or more; width-to-height ratio 0.5 or more; sRGB; 10 MB.
- Margins: 10% top and bottom for vertical products, 5% each side for horizontal ones.
- The product fills 70 to 80%.
- Primary image: front view on pure white (fashion: light grey).
- **Rejected for:** logos, watermarks, borders, price, warranty text or expiry dates on the image.
- At least 3 images recommended.

**Store:**
- Banner minimum 1440x240 (6:1). Its sides may be cropped on small screens.
- English and Arabic banners are separate.
- Logo minimum 100x100.

**A+ banners:**
- 2400 px wide (1800 to 3600), 10 MB, up to 10.
- JPEG, PNG, WebP or AVIF.

### 9.5 Mercado Libre / Mercado Livre
**Developer docs** (24 Mar 2026):
- Upload 1200x1200; maximum 1920x1920 (larger is resized); minimum 500x500.
- Zoom appears above 800 px wide.
- 10 MB; JPG or PNG; RGB.
- The product fills 95% of the frame.

**Cover rules:**
- pure white, digitally created background (some fashion and home categories may use a real setting);
- no watermarks, logos, QR codes, text, borders or contact details;
- do not imitate Mercado Libre's own badges;
- packaging only from the second photo.

**Counts and fashion:**
- 12 photos per item and 10 per variation in general categories.
- Fashion: vertical 1200x1540.

**Moderation:** flags weak covers with a poor-quality-thumbnail tag. Its API checks white background, size, text or logos, and watermarks.

### 9.6 Allegro (Poland)
- Longer side 500 px or more; up to 2560x2560 (scaled down above that) and 26 MP; any proportions.
- JPG, PNG or WebP; sRGB.
- **Any background colour.** No white-first-image rule was found.
- No store text or store logo. Brand, technology and certificate logos, numbers and dimension graphics are allowed.
- Infographics only for invited sellers, and never as the thumbnail.
- Image count: 10 (regular account), 16 (business), 40 (classifieds).

### 9.7 Not verified
- **OTTO Market:** the API docs carry no image rules in their static HTML.
- **Zalando:** the partner docs return 403.
- **Taobao and Tmall:** the rule pages are JavaScript-only shells, so 800x800, 750x1000, the image count, the white-background image and the anti-text-overlay rule are all unconfirmed.
- **Rakuten Ichiba:** the rule of 20% or less text on the first image, with no frames, was not found in any public source.

No presets were added for these four.

### 9.8 India

**Amazon.in.** Same image rules as global Amazon. sell.amazon.in lists 500x500 or 1,000x1,000 for better listing quality and links to the same help page (1881). Use `amazon-main`.

**Flipkart.**
- The Seller Hub image specs are login-only, and robots.txt disallows the Learning Center.
- The public seller blog (product photography, fashion photography) gives no pixel sizes. It recommends white or neutral backgrounds and mentions a paid Premium Catalogue Program.
- **Practice, measured:** fashion search tiles are 139x185 CSS px on desktop. Images are served in a 612 px box, and originals run from 2:3 to 4:5, mostly 3:4.
- **Advice:** 3:4 portrait masters for fashion and 1:1 for hardgoods, on white or light grey. Confirm in Seller Hub before a large shoot.

**Myntra.** The partner portal is login-only. All three sampled originals were 1080x1440 (3:4) (`myntra-product`, practice).

**Meesho.** Blocked automated browsing ("Access Denied"). Not verified.

---

## 10. Could not verify

**Walmart Marketplace (everything).**
- Marketplace Learn shows a "Robot or human? Press and hold" challenge to automated browsers. It was not bypassed.
- Seller Help returned 503, and the developer image pages returned 404.
- The commonly quoted 2200x2200 figure is therefore unconfirmed. No preset was added.

**Amazon:**
- The live Seller Central G1881 wording (it loads as a JavaScript shell).
- The 10 MB file cap and sRGB versus CMYK today.
- Current US apparel and mannequin wording.
- Premium A+ module-by-module sizes (only 1464 px width, widely cited).
- The Brand Story background size (1464x625 from SellerApp).
- The Sponsored Brands custom image and logo pixel specs (Amazon's spec page returned 404, so third-party figures are used).

**Meesho.**
- Access denied to automated browsing.

**Flipkart.**
- Seller Hub image specs are login-only, and robots.txt disallows the Learning Center. Only practice measurements were taken.

**Myntra.**
- The partner portal is login-only. 1080x1440 is observed practice.

**Daraz:**
- Pixel limits, file size and Store Decoration banner sizes (inside Seller Center or downloadable PDFs).
- The Lazada proxy is in section 9.1.

**Lazada:**
- File cap: 1 MB versus 3 MB (Lazada's own documents disagree).
- App header: 750x478 versus 750x180 (the newer courses say 750x478).
- The pixel size of the product-page banner is not published.

**Shopee:**
- No official maximum pixel size.
- No published pixel size for 3:4 images.
- Badge overlay positions are shown in an example graphic only, without px.

**Tokopedia:** current limits (only 2022 and 2024 archived pages were readable).

**Noon:** a home-category guide says "660x9", which is probably a typo.

**Allegro:** the white-first-image rule in the brief (not found; Allegro allows any background).

**OTTO, Zalando, Taobao/Tmall and Rakuten Ichiba:** everything. Pages were empty JavaScript shells, 403, or not found. The "text under 20% on the first image" rule for Rakuten and the 800x800 / 750x1000 rules for Taobao remain unconfirmed.

**Zoom Events.**
- The Zoom support site search did not return results to automated browsing. Event cover and hub banner sizes are unverified.

**Indiegogo.**
- Moved to a Gamefound-powered platform on 16 Oct 2025. The new image specs were not found.

**Coursera.**
- No public creator image specification was found (partner resources are private).

**Facebook event cover.**
- Meta publishes no pixel size. 1920x1005 stays third-party.

**Kickstarter and Product Hunt.**
- The live pages are behind bot checks, so the Wayback copies (2024) were used. The specs may have changed since.

**On-screen widths:**
- Amazon, Etsy, eBay, App Store and Play tiles were not measured (estimates are marked). The Apple and Google store apps cannot be measured from a desktop browser.

**Screenshot A/B data:**
- No public study with a stated method was found for device frames versus frameless screenshots, or for caption length. The vendor claims are labelled as such.

**Steam library hero safe area:**
- The 860x380 safe area does not state whether it applies to the 3840 px template or the 1920 px half size. The stricter reading is used.

---

## 11. Sources

All fetched 2026-09-24 or 2026-09-24. "Undated" means the page shows no date.

### Amazon
- sell.amazon.com, "Product photos" blog, https://sell.amazon.com/blog/product-photos (4 Dec 2024): official.
- sell.amazon.com, listings blog, https://sell.amazon.com/blog/amazon-product-listings (29 Apr 2026): official.
- sell.amazon.com, video blog, https://sell.amazon.com/blog/amazon-product-video (12 May 2025): official (the sales-lift figure is a vendor claim).
- Amazon Fashion Clothing Image Style Guide, https://m.media-amazon.com/images/G/65/SG3P/LISTING_GUIDES/Amazon_Fashion_Clothing_Image_Style_Guide.pdf (Mar 2022): official, dated.
- Amazon.ae Clothing Style Guide, https://m.media-amazon.com/images/G/39/help/Clothing_Styleguide_EN_AE._CB1198675309_.pdf (Dec 2018): official, dated.
- Amazon Home image guide, https://m.media-amazon.com/images/G/01/Home_Image_Guide/Home_SG_Q3-2020_-_Draft_Finalized_-_seller_facing_-_1218.pdf (Q3 2020): official, dated.
- sell.amazon.in, https://sell.amazon.in/sell-online/list-your-products (undated): official.
- Selling Partner API, A+ content examples, https://developer-docs.amazon/sp-api/docs/a-plus-content-examples (undated): official.
- A+ content model, https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/models/aplus-content-api-model/aplusContent_2020-11-01.json (undated): official.
- A+ content design guide, https://sell.amazon.com/blog/a-plus-content-design-guide (24 Sep 2025): official.
- A+ tool page, https://sell.amazon.com/tools/a-content (undated): official (lift figures are vendor claims).
- "Types of A+ Content", https://m.media-amazon.com/images/G/01/bx-marketing/types-of-aplus-content.pdf (modified 13 Jan 2026): official.
- KDP A+ guidelines and examples, https://kdp.amazon.com/en_US/help/topic/G4WB7VPPEAREHAAD and https://kdp.amazon.com/en_US/help/topic/GCKLH8V7ULLD5EXY (undated): official (KDP).
- Amazon Ads, Stores specs, https://advertising.amazon.com/resources/ad-specs/stores (undated): official.
- Six tips to optimise your Store for mobile, https://advertising.amazon.com/library/expert-advice/six-tips-to-optimize-your-store-for-mobile (undated): official.
- Store freshness data, https://advertising.amazon.com/en-us/library/guides/reduce-friction-to-purchase-on-your-store/ (2024 data): vendor claim.
- Sponsored Brands and Display moderation, https://advertising.amazon.com/library/guides/sponsored-brands-display-ads-moderation (undated): official.
- Sponsored Brands video specs, https://advertising.amazon.com/resources/ad-specs/sponsored-brands-video (undated): official.
- Amazon Posts page, https://advertising.amazon.com/solutions/products/posts: official. Creation was switched off in June 2025 and Posts were discontinued in July 2025.
- Third-party guides, all widely-cited:
  - Jungle Scout A+ guide, https://www.junglescout.com/resources/articles/amazon-a-plus-content/ (5 Apr 2024);
  - SellerApp, https://www.sellerapp.com/blog/amazon-a-plus-content/ (24 Aug 2026);
  - goaspi, https://www.goaspi.com/blog/amazon-sponsored-brands-custom-image-creative/ (12 May 2026);
  - getricardo, https://getricardo.com/blogs/news/sponsored-brand-ads-on-amazon-requirements-dimensions (24 Dec 2025).

### eBay, Google, Meta
- eBay adding pictures, https://www.ebay.com/help/selling/listings/adding-pictures-listings?id=4148 (undated): official.
- eBay picture policy, https://www.ebay.com/help/policies/listing-policies/picture-policy?id=4370 (undated): official.
- eBay Stores, https://www.ebay.com/help/selling/ebay-stores/manage-ebay-store?id=4090 (undated): official.
- Google Merchant Center image_link, https://support.google.com/merchants/answer/6324350 (undated): official.
- Google Merchant Center, related answers 6324370, 9103186 and 9242973 (undated): official.
- Meta Business Help, product image specifications for catalogues, https://www.facebook.com/business/help/686259348512056 (undated, read in a browser): official.
- Meta catalogue fields, https://developers.facebook.com/docs/commerce-platform/catalog/fields (undated): official.
- Meta Help Center, event cover photo, https://www.facebook.com/help/1910675759253872 (undated): official.

### Shopify, WooCommerce, Etsy, TikTok Shop
- Shopify product media types, https://help.shopify.com/en/manual/products/product-media/product-media-types (undated): official.
- Shopify theme images, https://help.shopify.com/en/manual/online-store/images/theme-images (undated): official.
- Shopify Dawn source, https://github.com/Shopify/dawn (v16.0.0, 10 Aug 2026): official code.
- WooCommerce image sizes, https://woocommerce.com/document/image-sizes-theme-developers/ (undated): official.
- WooCommerce product images and galleries, https://woocommerce.com/document/adding-product-images-and-galleries/ (undated): official.
- Etsy image requirements, https://help.etsy.com/hc/en-us/articles/115015663347 (updated 23 Sep 2026, edited 4 May 2026): official.
- Etsy help articles 115015663247, 360016260113, 115015628707 and 360053206073 (updated 21 to 23 Sep 2026): official.
- TikTok Shop Academy (US), Product Listing Policy, https://seller-us.tiktok.com/university/essay?knowledge_id=3196690250417921 (1 Sep 2026): official.
- TikTok Shop Academy (US), articles 7073362639816491 (10 Aug 2026), 3026065007494925 (26 Jun 2026) and 3029412015458091 (15 Sep 2026): official.
- TikTok Shop Academy (UK), Best Practices for Product Listings, https://seller-uk.tiktok.com/university/essay?knowledge_id=7753820806006530 (17 Nov 2025): official.

### App stores and software listings
- Apple, screenshot specifications, https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications (undated): official.
- Apple, app preview specifications, https://developer.apple.com/help/app-store-connect/reference/app-preview-specifications (undated): official.
- Apple, In-App Event media specifications, https://developer.apple.com/help/app-store-connect/reference/in-app-events/in-app-event-media-and-audio-specifications (undated): official.
- Apple, In-App Events guidance, https://developer.apple.com/app-store/in-app-events/ (undated): official.
- Apple, product page, https://developer.apple.com/app-store/product-page/ (undated): official.
- Apple, Product Page Optimization (with the Simply Piano and Peak Brain Training cases), https://developer.apple.com/app-store/product-page-optimization/ (undated): official.
- Google Play, store listing experiments, https://support.google.com/googleplay/android-developer/answer/6227309 (undated): official.
- Apple, App Review Guidelines, https://developer.apple.com/app-store/review/guidelines/ (undated): official.
- Apple, HIG app icons, https://developer.apple.com/design/human-interface-guidelines/app-icons (change log 8 Jun 2026): official.
- Google Play preview assets, https://support.google.com/googleplay/android-developer/answer/9866151 (undated): official.
- Google Play metadata policy, https://support.google.com/googleplay/android-developer/answer/9898842 (undated): official.
- Google Play store listing best practices, https://support.google.com/googleplay/android-developer/answer/13393723 (undated): official.
- Google Play icon specifications, https://developer.android.com/distribute/google-play/resources/icon-design-specifications (updated 15 Jun 2026): official.
- Microsoft Store screenshots and images, https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images (updated 24 Aug 2026): official.
- Chrome Web Store images, https://developer.chrome.com/docs/webstore/images (updated 11 Jun 2018): official.
- Product Hunt, how to post a product, https://help.producthunt.com/en/articles/479557-how-to-post-a-product (Wayback copy of 13 Mar 2024): official, archived.
- Steam, https://partner.steamgames.com/doc/store/assets/standard, /libraryassets, /rules and /eventassets (undated; rules effective 1 Sep 2022): official.
- SplitMetrics, https://splitmetrics.com/blog/app-store-screenshots/ (updated 14 Sep 2026): vendor.
- AppTweak, https://www.apptweak.com/en/aso-blog/how-to-optimize-your-app-screenshots (updated 21 Nov 2025): vendor.

### Creator commerce, courses, events
- Gumroad, https://gumroad.com/help/article/60-adding-a-cover-image (undated): official.
- Lemon Squeezy, https://docs.lemonsqueezy.com/help/products/adding-products and https://docs.lemonsqueezy.com/help/marketplace/guidelines (undated): official.
- Patreon, https://support.patreon.com/hc/en-us/articles/203913369 (15 Sep 2026): official.
- Patreon, https://support.patreon.com/hc/en-us/articles/360038982432 (3 Sep 2026): official.
- Ko-fi, https://help.ko-fi.com/hc/en-us/articles/360004243378 (12 Aug 2026): official.
- Ko-fi, articles 360009712917 and 360020081893 (2026): official.
- Kickstarter, https://www.kickstarter.com/help/images (Wayback copy of 18 May 2024): official, archived.
- Kickstarter help centre, articles 16236740 and 16236743 (undated): official.
- Indiegogo, https://support.indiegogo.com/hc/en-us/articles/39600950083988 (16 Oct 2025): official.
- Udemy, https://support.udemy.com/hc/en-us/articles/229232347 (10 Jul 2026) and 229232487 (10 Sep 2026): official.
- Teachable, https://support.teachable.com/en/articles/11682492-image-size-guide (1 Jul 2025): official.
- Thinkific, https://support.thinkific.com/hc/en-us/articles/360035064553 (13 May 2026) and 360058142034 (26 Nov 2025): official.
- Skillshare, https://help.skillshare.com/hc/en-us/articles/204541718 and 4416498545165 (11 Sep 2025): official.
- Eventbrite, https://www.eventbrite.com/help/en-us/articles/682424/how-to-choose-a-great-event-image/ (undated, read in a browser): official.
- Luma, https://help.luma.com/p/event-cover-images and https://help.luma.com/p/updating-social-images (undated): official.
- Meetup, https://help.meetup.com/hc/en-us/articles/39287743789325 (19 Nov 2025), 360002879831 (16 Sep 2026) and 40378101429389 (9 Aug 2026): official.

### Regional marketplaces (read by a research agent, re-checked where noted)
- Lazada University, https://university.lazada.sg:
  - image guideline lectures 4677, 528 and 524 (PDFs 2019 to 2023; 2019 limits re-checked);
  - store decoration courses 45980 and 46814 (3 Nov 2025 and 11 Mar 2026; header and banner sizes re-checked).
- Lazada Open Platform, https://open.lazada.com/apps/announcement/detail?docId=1798 (28 Mar 2023) and https://open.lazada.com/apps/community/detail?id=286: official.
- Shopee Seller Education Hub, articles PH 284, 2989, 2997, 12680, 17355, 24772, 24855 and 24949; SG 6913, 7013, 7081, 16368, 17318, 17821 and 27838; MY 127, 370, 1928 and 12477; ID 6918, 6924, 7344, 16726, 27339 and 28064; TH 2215, 12631 and 19781; VN 238 and 3663; TW 171, 594, 2046, 2757 and 17316; BR 2822, 15216 and 16842 (2024 to 2026): official.
- Mercado Libre developers, https://developers.mercadolibre.com.ar/es_ar/trabajar-con-imagenes (24 Mar 2026), and help articles 805, 21874 and 22501: official.
- Noon partner help centre, https://helpcenter.noon.partners/en/category/product-listing/image-requirements-and-rejection-reasons-for-the-seller-sku (22 Apr 2026): official.
- Allegro, https://help.allegro.com/en/sell/a/rules-for-images-in-the-gallery-and-in-descriptions-8dvWB8Y2PIq (undated): official.
- Tokopedia seller education, Wayback copies of 28 Sep 2022 and 4 Jul 2024: official, archived.

### Research and evidence
- Baymard Institute:
  - https://baymard.com/blog/in-scale-product-images (30 May 2017);
  - https://baymard.com/blog/current-state-ecommerce-product-page-ux (updated 18 Mar 2026);
  - https://baymard.com/blog/human-model (1 Dec 2020);
  - https://baymard.com/blog/included-accessories-image (19 Feb 2019);
  - https://baymard.com/blog/product-images-descriptive-text (28 Nov 2018);
  - https://baymard.com/research-articles/dimensions-measurements-product-size-image (15 Oct 2024);
  - https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom (2 Apr 2020);
  - https://baymard.com/research-articles/informational-image-accessibility (10 Aug 2021);
  - https://baymard.com/research-articles/homepage-carousel (updated 3 Apr 2025).
- Nielsen Norman Group:
  - https://www.nngroup.com/articles/photos-as-web-content/ (reviewed 13 Aug 2026);
  - https://www.nngroup.com/articles/product-photos-listing-pages/ (27 Feb 2022);
  - https://www.nngroup.com/articles/designing-effective-carousels/ (reviewed 7 Aug 2026);
  - https://www.nngroup.com/articles/text-over-images/ (reviewed 13 Jan 2026).
- Erik Runyon, https://erikrunyon.com/2013/01/carousel-interaction-stats/ (22 Jan 2013): practitioner data.

### Bangladesh, India, measurements
- Daraz University (Bangladesh):
  - https://university.daraz.com.bd/course/learn?id=47452 (Product Image Policy, 13 Jul 2026);
  - id=7377 (Daraz Image Guidelines, 28 Feb 2024);
  - id=41506 (Content Issues and Solutions Center, 28 Feb 2024).
- Daraz University (Bangladesh): https://university.daraz.com.bd/course/learn?id=46924 (Duplicate Products Policy, 1 Apr 2026).
- Daraz University (Pakistan): https://university.daraz.pk/course/learn?id=46981 (Product Listing Policy, 23 Apr 2026).
- Daraz University (Sri Lanka and Nepal): the same Product Image Policy, both dated 13 Jul 2026, at https://university.daraz.lk/course/learn?id=47458 and https://university.daraz.com.np/course/learn?id=47457.
- Daraz, Myntra, Flipkart, Rokomari, Pickaboo, Chaldal and Shajgoj: public pages measured in a browser or with curl on 24 Sep 2026 (practice).
- Flipkart seller blog, https://seller.flipkart.com/seller-blog/product-photography (undated): official, but gives no pixel sizes.
