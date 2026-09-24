# R5: Format specs, print specs and deliverable playbooks

Research notes for the HTML/CSS → headless-Chrome graphics skill (PNG/JPG at exact pixel sizes, plus print PDFs).
Compiled 2026-09-23. Every number carries a source ID such as `[S05]`. §9 maps each ID to its URL and to the source's date or version.

## How to read these notes

- **Official first.** Help centres, ads guides and developer docs come first. Reputable 2025–2026 roundups fill gaps. Where they disagree, both values are listed in §7, with the official one marked.
- **Measured (M).** Five UI facts were measured this session in a Chromium pane with `getBoundingClientRect` `[S36]`: YouTube thumbnail and badge sizes, and the Facebook Page cover and avatar geometry. UIs change and run A/B experiments, so treat these as a dated snapshot.
- **Derived (D).** Pixel conversions (for example 14 % of 1920 = 269 px), crop maths and fold maths were computed from the cited rules. The formula is stated each time.
- **Heuristic (H).** Practitioner rules with no fetched source are labelled H. They must not be presented as evidence.
- **Verification gap.** The session-wide WebSearch budget (200 calls, shared with parallel research threads) ran out partway through this work. After that, only known URLs could be fetched. Pages that were login-walled or bot-blocked (Amazon Seller Central, X developer docs, Adobe HelpX, most printer template pages) could not be verified. Every affected item is marked **UNVERIFIED** and listed in §10.
- **Safe insets.** `T/R/B/L` means pixels measured from each edge, at the preset's own size, that must stay clear of text, logos and key subject matter, because of UI overlays or crops. "grid" means the inset exists only because of the Instagram profile-grid crop.

---

## 0. What changed in 2024–2026 (the deltas a stale preset set would get wrong)

| Change | Current value | Src |
|---|---|---|
| Instagram carousel limit | Raised from 10 to **20** items (announced 8 Aug 2024) | [S04] |
| Instagram profile grid | Tiles went from square to **3:4 portrait** (Jan 2025) | [S02] |
| Instagram feed aspect range | Official range is now **1.91:1 to 3:4**: 1080 wide × 566–1,440 tall. Native 3:4 photos arrived in late May 2025, for single posts and carousels | [S01][S03] |
| Instagram hashtags | Official help: "You can use up to **5** tags on a post" (was 30) | [S87] |
| Meta ads recommended resolution | Feed image ads **1440×1800 (4:5)**. Stories and Reels **1440×2560 (9:16)**. The 9:16 safe zone is **14 % top / 35 % bottom / 6 % sides** | [S05][S06][S07][S08] |
| YouTube custom thumbnails | Upload up to **3840×2160** (Shorts **2160×3840**, 9:16). File limit **50 MB on desktop** but **2 MB on mobile**. Custom Shorts thumbnails can be set only in Studio on a computer | [S30] |
| YouTube A/B testing | "Test & compare" now tests up to **3 titles and/or thumbnails**. The winner has the highest **watch time** | [S32] |
| LinkedIn company cover | Official size is now **1512×256** (was 1128×191; same ≈5.9:1 ratio). Help page last updated ≈Aug 2026 | [S17] |
| LinkedIn events | Cover image is **16:9** (480×270 or 1280×720, min width 480). Older 4:1 specs are obsolete | [S19] |
| Google Merchant Center | Minimum image is now **500×500 for all products**. Recommended ≈1500×1500 | [S58] |
| Facebook Page cover | Help text now says "16:9 on computers / 2.4:1 on mobile", **but** the web renders ≈2.7:1 on both (M). Design dual-safe (§5.5) | [S10][S36] |
| Threads | Carousels 2–20 items. Images ≤8 MB, width 320–1440 px, aspect ≤10:1, sRGB. Text posts 500 characters | [S11] |
| Email clients | Apple **62.26 %**, Gmail **27.03 %**, Outlook **5.83 %** of 1B+ opens (July 2026). Apple's share is inflated by Mail Privacy Protection | [S88] |

---

## 1. Master spec table (digital presets)

Columns: `id | platform | surface | W×H px | aspect | safe insets T/R/B/L px | max file | format | notes | src`.
"—" means no inset or no published limit. When a surface has both an organic and an ads spec, both rows are given.

| id | platform | surface | W×H px | aspect | safe T/R/B/L | max file | format | notes | src |
|---|---|---|---|---|---|---|---|---|---|
| ig-feed-3x4 | Instagram | Feed photo, portrait max | 1080×1440 | 3:4 | 0/0/0/0 (grid shows all) | not published (organic) | JPG/PNG, sRGB | Tallest ratio Instagram supports. Fills the most feed height and matches the 3:4 grid exactly. Native since late May 2025 | [S01][S03] |
| ig-feed-4x5 | Instagram | Feed photo, portrait | 1080×1350 | 4:5 | 0/34/0/34 (grid) | — | JPG/PNG | The grid's 3:4 centre crop keeps 1012.5×1350 (D) | [S01][S13] |
| ig-feed-1x1 | Instagram | Feed photo, square | 1080×1080 | 1:1 | 0/135/0/135 (grid) | — | JPG/PNG | The grid keeps the centre 810×1080 (D) | [S01][S02] |
| ig-feed-191 | Instagram | Feed photo, landscape | 1080×566 | 1.91:1 | 0/328/0/328 (grid) | — | JPG/PNG | Smallest in feed. The grid keeps only the centre ≈425 px (D) | [S01] |
| ig-carousel-3x4 | Instagram | Carousel slide | 1080×1440 | 3:4 | slide 1: 0/0/0/0 | — | JPG/PNG | 2–20 items. Keep one aspect ratio across all slides (widely reported that slides take the first slide's crop; **UNVERIFIED**) | [S04][S03] |
| ig-carousel-4x5 | Instagram | Carousel slide | 1080×1350 | 4:5 | slide 1: 0/34/0/34 (grid) | — | JPG/PNG | The classic carousel size | [S04][S13] |
| ig-story | Instagram | Story (organic) | 1080×1920 | 9:16 | 269/65/672/65 | — | JPG/PNG | Uses Meta's ads zone (14/35/6 % → px, D) as the conservative organic zone | [S06] |
| ig-reel-cover | Instagram | Reel cover frame | 1080×1920 | 9:16 | 285/34/285/34 | — | JPG/PNG | Grid shows the centre 1080×1440 (trims 240 T/B). A 4:5 feed crop would trim 285 T/B, and the 34 px L/R covers a 3:4 re-crop of that (D, H). Keep the title inside the centre 1012×1350 | [S13][S02] |
| ig-profile | Instagram | Profile photo | 320×320 | 1:1 → circle | inscribed circle | — | JPG/PNG | Displays at ≈110×110. Upload ≥320 | [S13][S14] |
| ig-ad-feed | Instagram ads | Feed image ad | 1440×1800 | 4:5 | — | 30 MB | JPG/PNG | Min width 500. Accepted range 1.91:1–4:5 (±1 %). Primary text 125 chars, headline 40, ≤30 hashtags (ads) | [S05] |
| ig-ad-story | Instagram ads | Stories image ad | 1440×2560 | 9:16 | 358/86/896/86 | 30 MB | JPG/PNG | 14 % top, 35 % bottom, 6 % sides. Min width 500. Primary text 125 | [S06] |
| ig-ad-reel | Instagram ads | Reels ad (frame master) | 1440×2560 | 9:16 | 358/86/896/86 | 4 GB (video) | MP4/MOV | Same zone. Primary text 44 chars. Video 0 s–15 min | [S08] |
| fb-feed-ad-4x5 | Facebook ads | Feed image ad | 1440×1800 | 4:5 | — | 30 MB | JPG/PNG | Min 600×750. Tolerance ±3 %. Primary text 50–150, headline 27 | [S07] |
| fb-feed-4x5 | Facebook | Feed photo (organic) | 1080×1350 | 4:5 | — | — | JPG/PNG | Roundup value | [S13] |
| fb-feed-1x1 | Facebook | Feed photo, square | 1080×1080 | 1:1 | — | — | JPG/PNG | Roundup value | [S13] |
| fb-story | Facebook | Story | 1080×1920 (ads 1440×2560) | 9:16 | 269/65/672/65 | 30 MB (ads) | JPG/PNG | Meta reportedly unified the 9:16 zone across Stories and Reels (Mar 2026, third-party). The IG Stories guide already shows 14/35/6 | [S06][S09] |
| fb-page-cover | Facebook | Page cover | 1702×630 (2× of 851×315) | ≈2.7:1 | 20/190/40/40 **plus** a bottom-left 660×160 keep-clear block (avatar) | <100 KB for fastest load at 851×315 | sRGB JPG. PNG if logo or text | Official: min 400×150, left-aligned, profile picture overlaps ~40 px on mobile, "16:9 on computers / 2.4:1 on mobile". Measured on web: 940×348 (2.70:1) desktop, 360×132 (2.73:1) mobile. Avatar 122 px at x=12, overlapping the cover by 33 px at 360 px width. The R190 inset (2×) survives a left-aligned 2.4:1 crop (D) | [S10][S36] |
| fb-page-profile | Facebook | Page profile picture | 320×320 | 1:1 → circle | inscribed circle | — | PNG for logos | Displays at 176 (computer), 196 (smartphone), 36 (feature phone) | [S10] |
| fb-event-cover | Facebook | Event cover | 1920×1005 | ≈1.91:1 | ≈5 % all sides (H) | not published | JPG/PNG | Meta publishes no official spec. Third-party consensus. Reportedly changed from 1920×1080 around mid-2024 | [S15] |
| fb-group-cover | Facebook | Group cover | 1640×856 | ≈1.91:1 | 97/0/97/0 | not published | JPG/PNG | Third-party: desktop shows ≈1640×662 of the height | [S16] |
| threads-4x5 | Threads | Image / carousel | 1080×1350 | 4:5 | — | 8 MB | JPEG/PNG, sRGB | Width 320–1440 (auto-scaled). Aspect ≤10:1. Carousel 2–20. Text 500 chars | [S11] |
| threads-3x4 | Threads | Image, max width | 1440×1920 | 3:4 | — | 8 MB | JPEG/PNG | Hootsuite gives 1440×1920 as the post image size | [S11][S14] |
| wa-status | WhatsApp | Status image | 1080×1920 | 9:16 | 269/65/672/65 (H: reuse the Stories zone) | 5 MB (Cloud API image limit, proxy) | JPEG/PNG, 8-bit RGB/RGBA | **No official Status pixel spec found** | [S12] |
| wa-sticker | WhatsApp | Sticker | 512×512 (**UNVERIFIED**) | 1:1 | — | 100 KB static / 500 KB animated | WebP | The fetched doc gives only the byte limits | [S12] |
| li-post-191 | LinkedIn | Single image post or ad, landscape | 1200×628 | 1.91:1 | — | 5 MB (ads). Organic ≤36 MP | Ads: JPG/PNG/GIF. Organic: also HEIC/WEBP | Ads min 640×360, max 7680×4320 | [S23][S20] |
| li-post-1x1 | LinkedIn | Square post or ad | 1200×1200 | 1:1 | — | 5 MB (ads) | JPG/PNG/GIF | Ads min 360×360, max 4320×4320 | [S23] |
| li-post-4x5 | LinkedIn | Vertical post or ad | 1080×1350 (ads rec 720×900) | 4:5 | — | 5 MB (ads) | JPG/PNG/GIF | LinkedIn recommends 4:5 "to avoid borders on vertical". Also 2:3 (600×900) and 1:1.91 (628×1200) | [S23] |
| li-doc-page-4x5 | LinkedIn | Document "carousel" page | 1080×1350 (H) | 4:5 | 60/60/60/60 (H) | 100 MB, 300 pages, 1M words | PDF (also PPT/PPTX/DOC/DOCX) | All pages must be one size. Flatten layers. No official page-size recommendation | [S22][S24][S20] |
| li-doc-page-1x1 | LinkedIn | Document page | 1080×1080 (H) | 1:1 | 60 all (H) | same | PDF | Same rules | [S22][S24] |
| li-carousel-ad | LinkedIn ads | Carousel ad card | 1080×1080 | 1:1 | — | 10 MB | JPG/PNG/GIF (static) | 2–10 cards. Card headline 45 chars | [S25] |
| li-profile-cover | LinkedIn | Personal profile cover | 1584×396 | 4:1 | keep the lower-left ≈30 % × 50 % clear for the avatar (H) | <8 MB | JPG/PNG | No official overlap geometry. GIFs not allowed | [S18][S20] |
| li-company-cover | LinkedIn | Company page cover | 1512×256 | ≈5.9:1 | — | 3 MB | PNG/JPEG | New official size (was 1128×191) | [S17] |
| li-company-logo | LinkedIn | Company logo | 400×400 (min 268×268) | 1:1 | — | 3 MB | PNG/JPEG | — | [S17] |
| li-life-main | LinkedIn | Life tab main image | 1128×376 | 3:1 | — | 3 MB | PNG/JPEG | Custom modules 502×282. Photos 900×600 (min 264×176) | [S17] |
| li-event-cover | LinkedIn | Event cover | 1280×720 (min width 480) | 16:9 | — | not stated | — | Local upload only (no cloud pickers) | [S19] |
| li-newsletter-cover | LinkedIn | Newsletter article cover | 1920×1080 | 16:9 | — | — | — | — | [S21] |
| li-newsletter-logo | LinkedIn | Newsletter logo | 300×300 | 1:1 | — | — | — | — | [S21] |
| li-link-share | LinkedIn | og:image link preview | 1200×627 | 1.91:1 | — | 5 MB | — | Images under 401 px wide show as a thumbnail | [S50] |
| x-post-16x9 | X | In-stream image | 1600×900 | 16:9 | — | 5 MB | JPG/PNG/GIF | Single images at 16:9, 4:3, 2:1 and 3:4 display uncropped on iOS/Android (since May 2021) | [S26][S29][S13] |
| x-post-1x1 | X | In-stream image, square | 1080×1080 | 1:1 | — | 5 MB | JPG/PNG | — | [S13][S26] |
| x-post-3x4 | X | In-stream image, portrait | 1080×1440 | 3:4 | — | 5 MB | JPG/PNG | 3:4 is on the "shown in full" list | [S29] |
| x-gif | X | Animated GIF | — | — | — | 5 MB mobile / 15 MB web | GIF | — | [S26] |
| x-header | X | Profile header | 1500×500 | 3:1 | 60/0/60/0 **plus** bottom-left avatar block ≈400×150 (H) | not verified | JPG/PNG | Official gives only the size. Overlap geometry is heuristic | [S27] |
| x-profile | X | Profile photo | 400×400 | 1:1 → circle | circle | 2 MB | JPG/PNG | — | [S27] |
| x-ad-card | X ads | Website card image | 800×418 or 800×800 | 1.91:1 / 1:1 | — | 5 MB | JPG/PNG | — | [S28] |
| x-card-large | X | `summary_large_image` link card | 1200×600 | 2:1 | centre-weighted | <5 MB (**UNVERIFIED**) | JPG/PNG/WEBP/GIF (**UNVERIFIED**) | Previously published spec: min 300×157, max 4096×4096. Docs returned 402/404 this session | — |
| yt-thumb | YouTube | Video thumbnail | 1280×720 (min width 640). Export up to 3840×2160 | 16:9 | bottom-right keep-clear ≈270×155 (duration badge, M/D) | 2 MB (mobile upload) / 50 MB (desktop) | JPG/PNG | Requires a verified account. Tested at 200×113, 248×139 and 375×210 display sizes (M) | [S30][S36] |
| yt-thumb-4k | YouTube | Video thumbnail, 4K master | 3840×2160 | 16:9 | bottom-right ≈810×465 | 50 MB (desktop only) | JPG/PNG | Same design, 3× scale | [S30] |
| yt-shorts-thumb | YouTube | Shorts thumbnail | 1080×1920 (up to 2160×3840) | 9:16 | 269/65/672/65 (H) | 50 MB desktop | JPG/PNG | Upload in Studio on a computer only. Min height 640 | [S30] |
| yt-podcast-thumb | YouTube | Podcast playlist thumbnail | 3000×3000 (H) | 1:1 | — | 10 MB mobile / 50 MB desktop | JPG/PNG | Official says "1:1 instead of 16:9" | [S30] |
| yt-banner | YouTube | Channel banner | 2560×1440 (min 2048×1152) | 16:9 | 508/507/509/507 (centre 1546×423 safe) | 6 MB | JPG/PNG | Official safe area is 1235×338 at 2048×1152, which scales to ≈1546×423 at 2560 (D). Third-party display bands: TV full, desktop 2560×423, tablet 1855×423, mobile 1546×423 | [S31][S37] |
| yt-profile | YouTube | Profile picture | 800×800 | 1:1 → circle | circle | 15 MB | JPG/GIF/BMP/PNG, no animated GIF | Renders at 98×98 | [S31] |
| yt-watermark | YouTube | Video watermark | 150×150 min | 1:1 | — | <1 MB | — | — | [S31] |
| yt-post-image | YouTube | Posts (Community) image | 1080×1080 | 1:1 | — | 16 MB | JPG/PNG/GIF/WEBP | Up to 10 images. Shown as 1:1 in the feed | [S34] |
| yt-endscreen-frame | YouTube | End-screen background | 1920×1080 | 16:9 | reserve element zones (§5.3) | — | video frame | Last 5–20 s. Video must be ≥25 s. Up to 4 elements. Custom element images ≥300×300 | [S33] |
| tt-vertical | TikTok | Organic video or photo | 1080×1920 | 9:16 | 140/164/370/60 (third-party ads values) | 20 MB per photo (API) | JPEG/WebP (API) | Photo Mode takes up to 35 images. API caps photos at 1080p. **Official: the safe zone varies with caption length and add-ons** | [S38][S39][S40][S41] |
| tt-ad-infeed | TikTok ads | In-feed ad | 1080×1920 (min 540×960) | 9:16 | 140/180/400/60 (conservative) | 500 MB | mp4/mov/mpeg/3gp/avi | Also 16:9 (≥960×540) and 1:1 (≥640×640). Ad profile image 98×98, <50 KB, 66×66 safe | [S38][S41] |
| pin-standard | Pinterest | Standard pin | 1000×1500 | 2:3 | — | 20 MB desktop / 32 MB app | PNG/JPEG | Taller than 2:3 "might get cut off". Title 100 chars (≈40 shown). Description 800 | [S42] |
| pin-carousel | Pinterest | Carousel pin card | 1000×1500 or 1000×1000 | 2:3 / 1:1 | — | 20 MB per image | PNG/JPEG | 2–5 images | [S42] |
| pin-9x16 | Pinterest | Idea ad / 9:16 | 1080×1920 | 9:16 | 270/195/440/65 | — | — | Official Idea-ad safe zone | [S42] |
| snap-ad | Snapchat | Single image or video ad | 1080×1920 (min 720×1280) | 9:16 | 269/65/672/65 (H, no px published) | 5 MB image / 1 GB video | JPG/PNG. MP4/MOV (H.264) | Brand name ≤32 (help) vs ≤25 (ad-formats page). Headline ≤34. Help page links "Safe Zones for Ads" but gives no numbers in text | [S43][S44] |
| tg-photo | Telegram | Photo (Bot API upload) | ≤10,000 px (W+H) | ratio ≤20 | — | 10 MB (5 MB by URL) | JPG/PNG | Client-side compression limits not verified | [S46] |
| tg-sticker | Telegram | Static sticker | 512×512 (one side exactly 512) | ≤1:1 | — | not stated | PNG/WEBP | Video sticker: WEBM, ≤256 KB, ≤3 s, looped. Animated TGS: 512×512, 64 KB | [S45] |
| tg-emoji | Telegram | Custom emoji | 100×100 | 1:1 | — | — | as stickers | — | [S45] |
| tg-story | Telegram | Story | 1080×1920 (H) | 9:16 | reuse the 9:16 zone (H) | — | — | **No official spec found** | — |
| gbp-photo | Google Business Profile | Photos, including post images | 1200×900 (H) (official rec 720×720; min 250×250) | 4:3 (H) | centre-weighted | 10 KB–5 MB | JPG/PNG | Google publishes no post-specific image spec. Video ≤30 s, ≤75 MB, ≥720p | [S47][S48] |
| og-image | Web / Meta sharing | Open Graph image | 1200×630 | 1.91:1 | ≈60 all (H: some apps crop to 1:1 or 2:1) | 8 MB (Meta) | JPG/PNG | Min 200×200 (Meta). Declare `og:image:width/height` | [S49] |
| article-hero-16x9 | Google Search / Discover | Article image | 1200×675 (≥1200 wide) | 16:9 | — | — | JPG/PNG/WebP | Discover: ≥1200 px wide, >300K px, `max-image-preview:large`. Avoid logo-only or text-heavy images | [S51][S52] |
| article-4x3 / article-1x1 | Google Search | Article image set | 1200×900 / 1200×1200 | 4:3 / 1:1 | — | — | — | Supply 16:9, 4:3 and 1:1, each ≥50K px (w×h) | [S52] |
| email-header | Email | Header / banner | 600×200 CSS → **export 1200×400** | 3:1 (H) | — | keep light (H ≤150–200 KB) | JPG/PNG (GIF: first frame only in some clients) | Templates 600–800 px wide are safe (Mailchimp). 2× export for retina (H) | [S90] |
| email-hero | Email | Hero image | 600×300 CSS → **export 1200×600** | 2:1 (H) | — | (H ≤200 KB) | JPG/PNG | Never put the only copy of key text in the image (§5.12) | [S90][S89] |
| web-hero | Web | Full-bleed hero | 1920×1080 (plus 2560×1440 for HiDPI) | 16:9 | central 60 % for copy (H) | budget-driven (LCP) | AVIF/WebP/JPG | Art-direct a mobile crop at 1080×1350 or 1080×1920. Avoid auto-rotating carousels (§5.5) | [S81] |
| blog-featured | Web | Blog featured / OG | 1200×675 | 16:9 | — | — | JPG/WebP | Doubles as Discover and Article image | [S51][S52] |
| gads-pmax-191 | Google Ads | PMax landscape image | 1200×628 (min 600×314) | 1.91:1 | centre-weighted (H) | 5,120 KB | JPG/PNG | Up to 20 per set (4+ recommended) | [S55] |
| gads-pmax-1x1 | Google Ads | PMax square image | 1200×1200 (min 300×300) | 1:1 | — | 5,120 KB | JPG/PNG | Up to 20 | [S55] |
| gads-pmax-4x5 | Google Ads | PMax portrait image | 960×1200 (min 480×600) | 4:5 | — | 5,120 KB | JPG/PNG | Up to 20 (2+ recommended) | [S55] |
| gads-logo-1x1 | Google Ads | Logo, square | 1200×1200 (min 128. Demand Gen min 144) | 1:1 | — | 5,120 KB | JPG/PNG | Transparent backgrounds may render on white | [S55][S56] |
| gads-logo-4x1 | Google Ads | Logo, landscape | 1200×300 (min 512×128) | 4:1 | — | 5,120 KB | JPG/PNG | Up to 5 | [S55] |
| gads-rda-1x1 | Google Ads | Responsive display ad, square | 1200×1200 (RDA recommends 600×600, min 300×300) | 1:1 | — | 5,120 KB | JPG/PNG | 1–15 images (5 recommended) | [S57] |
| gads-dg-4x5 | Google Ads | Demand Gen portrait | 960×1200 (min 480×600) | 4:5 | — | — | JPG/PNG | 1–20 (3 recommended) | [S56] |
| iab-* | Display | IAB fixed units | see §3.1 | — | — | K-weight table §3.1 | JPG/PNG/GIF/HTML5 | — | [S53][S54] |
| amazon-main | Amazon | Main product image | 2000×2000 (H) | 1:1 | product fills ≈85 % | — | JPEG/PNG/TIFF/GIF | **UNVERIFIED** (Seller Central G1881 is login-walled). Commonly documented: pure white RGB 255/255/255, ≥1000 px for zoom, ≤10,000 px, no text/logos/watermarks on the main image | — |
| etsy-listing | Etsy | Listing photo | 2000×1500 (H, landscape) | 4:3 (H) | ≈12 % margin all round so square, portrait and landscape crops survive (H) | >1 MB may fail on slow uploads | .jpg/.gif/.png/.svg | Official: ≥2000 px width **and** height. First photo ≥635 px, landscape or square. Thumbnails crop to square, portrait and landscape | [S61] |
| etsy-banner-big | Etsy | Big shop banner | 1600×400 (min 1200×300) | 4:1 | — | — | — | Mini banner 1600×213 (min 1200×160). Carousel banner 1200×300 | [S61] |
| etsy-logo | Etsy | Shop logo / profile | 500×500 / 400×400 | 1:1 | — | — | — | — | [S61] |
| ebay-photo | eBay | Listing photo | 1600×1600 (min 500×500) | 1:1 (H) | — | 12 MB each | JPEG/PNG/GIF/TIFF/BMP/WEBP/HEIC/AVIF | Up to 24 photos. No badges, logos, copyright notices or watermarks (they hurt search placement) | [S60] |
| shopify-product | Shopify | Product image | 2048×2048 | 1:1 | — | 20 MB. ≤5000×5000 or 25 MP | PNG best, then JPEG | — | [S59] |
| gmc-product | Google Merchant Center | Product image (`image_link`) | 1500×1500 (min 500×500) | 1:1 (H) | — | 16 MB. ≤64 MP | JPEG/WebP/PNG/GIF/BMP/TIFF | No CTAs, prices, watermarks, logos or brand-name overlays, barcodes, borders or placeholders | [S58] |

---

## 2. Platform notes: crops, overlays and behaviour

### 2.1 Instagram
- **Upload scaling** [S01]. Instagram uploads "up to a width of 1,080 pixels".
  - Images narrower than 320 px are enlarged to 320.
  - Images wider than 1080 are downsized to 1080.
  - Images 320–1080 wide keep their resolution.
  - Ratios outside 1.91:1–3:4 "will be cropped to fit a supported ratio".
  - **Implication:** render organic IG assets at exactly 1080 px wide. Extra width is thrown away and only adds recompression. The exception is Meta *ads*, which recommend 1440-wide masters [S05][S06].
- **Profile grid (Jan 2025)**: 3:4 portrait tiles [S02]. The grid shows a centred 3:4 crop (D):
  - 1:1 posts lose 135 px on each side.
  - 4:5 posts lose ≈34 px on each side.
  - 9:16 reels lose 240 px top and bottom.
  - Reports say creators can now adjust the grid thumbnail crop (third-party, ALM Corp via [S02] search results; **UNVERIFIED**). Default to designing covers that survive the centred crop.
- **3:4 native (late May 2025)**: single photos and carousels [S03]. 1080×1440 matches the grid with zero crop and takes the most feed height of any allowed ratio [S01].
- **Carousels**: up to 20 photos or videos since 8 Aug 2024 [S04]. Socialinsider's 2025 data (35M posts) says carousels "are the only content format that can show up twice in someone's feed" [S84]. See §5.2 for the chain technique.
- **Hashtags**: "You can use up to 5 tags on a post" [S87]. Meta *ads* guidance still says ≤30 hashtags [S05]. For organic posts, cap at 5.
- **Stories and Reels UI**: Meta's current ads guidance is to leave "at least 14% of the top, 35% of the bottom and 6% on each side" clear [S06][S08]. In pixels at 1080×1920 that is T269 / B672 / L65 / R65, a safe box of 950×979 (D). At 1440×2560 it is T358 / B896 / L86 / R86 (D). Third-party roundups report the zone was unified across Stories and Reels in Mar 2026, and that it grows to 40 % bottom when a Reels ad carries a disclaimer [S09] (**third-party**).

### 2.2 Facebook
- **Page cover** [S10], verbatim:
  - Computers: "Left aligns with a full bleed and a 16:9 aspect ratio."
  - Mobile: "Left aligns with a full bleed and a 2.4:1 aspect ratio."
  - "Must be at least 400 pixels wide and 150 pixels tall."
  - "Loads fastest as an sRGB JPG file that's 851 pixels wide, 315 pixels tall and less than 100 kilobytes."
  - "The profile picture overlaps with the cover photo by approximately 40 pixels on mobile devices."
  - "For … logo or text, you may get a better result by using a PNG file."
- **Measured on the web** [S36] contradicts the 16:9 wording.
  - facebook.com/facebook at a 1024 px viewport: cover rendered at **940×348 (2.70:1)**.
  - m.facebook.com at 360 px: **360×132 (2.73:1)**. The avatar (122 px) sits at x=12 and overlaps the cover's bottom by 33 px.
  - Native apps were not measured.
  - **Design rule (D):** use a 1702×630 master (2× of 851×315). Keep key content inside x 40–1512 and y 20–590. Keep the bottom-left 660×160 clear. That also covers a left-aligned 2.4:1 crop, which cuts the right 190 px at 2×.
- **Page profile picture**: displays at 176×176 on computers, 196×196 on smartphones and 36×36 on feature phones. It is cropped to a circle. Upload 320×320 [S10].
- **Event and group covers**: Meta publishes no official spec. Third-party consensus is 1920×1005 for events [S15] and 1640×856 for groups, where desktop shows ≈662 px of the height [S16].
- **Feed ads**: 4:5, 1440×1800 recommended. Minimum 600×750. Aspect tolerance 3 %. Primary text 50–150 characters. Headline 27 [S07].

### 2.3 Threads and WhatsApp
- **Threads** [S11]:
  - JPEG/PNG, 8 MB maximum, "Aspect Ratio Limit: 10:1".
  - Width 320–1440; outside that range the image is scaled.
  - sRGB. Carousels 2–20 children. Text posts 500 characters.
- **WhatsApp** [S12]:
  - Cloud API images are JPEG/PNG, ≤5 MB, 8-bit RGB/RGBA.
  - Stickers are WebP only: ≤100 KB static, ≤500 KB animated.
  - No official pixel spec for Status or Channels was found. Use 1080×1920 with the 9:16 zone as a heuristic.

### 2.4 LinkedIn
- **Personal cover**: 1584×396 recommended, under 8 MB, JPG/PNG [S18]. GIFs are not supported on profile or background photos [S20]. LinkedIn publishes no avatar-overlap geometry, so keep the lower-left area clear (H).
- **Company page** [S17]:
  - Logo 400×400 recommended, minimum 268×268.
  - **Cover 1512×256**.
  - Life-tab main image 1128×376. Custom modules 502×282. Company photos 900×600 (minimum 264×176).
  - Custom image for a page post with a URL: 1.91:1 (1200×627), more than 200 px wide.
  - All images PNG/JPEG, 3 MB maximum. Page "last updated 1 month ago".
- **Events**: "480x270 or 1280x720 pixels. The minimum width is 480 pixels, and the aspect ratio must be 16:9" [S19].
- **Newsletters**: logo 300×300. Per-article cover 1920×1080 [S21].
- **Media limits** [S20]:
  - Images up to **36 megapixels**.
  - Documents ≤100 MB, ≤300 pages, ≤1M words.
  - GIFs ≤500 frames or 36,152,320 pixels.
- **Documents and document ads** [S22][S24]:
  - Accepted types: PPT/PPTX/DOC/DOCX/PDF. Lead-gen document ads accept PDF only.
  - "PDFs with multiple layers must be flattened … PDFs with multiple sized pages must be fit to the same page size."
  - Document ads text: intro ≤150 characters to avoid truncation (3,000 maximum). Headline ≤70 (200 maximum).
- **Single-image ads** [S23]:
  - Landscape 1200×628 (min 640×360, max 7680×4320).
  - Square 1200×1200 (min 360×360).
  - Vertical 628×1200, 600×900 or 720×900 (min 360×640, max 2430×4320). "To avoid borders on vertical images … use a 4:5 aspect ratio."
  - 5 MB, JPG/PNG/GIF. Headline 70 characters. Intro 150.
- **Carousel ads**: 2–10 cards, 1080×1080, 10 MB, JPG/PNG/static GIF. Card headline 45 characters [S25].
- **Link previews**: og:image at least 1200×627, 1.91:1, ≤5 MB. Images under 401 px wide display as a thumbnail [S50].

### 2.5 X
- **Posting images** [S26]: photos up to 5 MB. GIFs up to 5 MB on mobile and 15 MB on web. Formats GIF/JPEG/PNG; BMP and TIFF are rejected.
- **Profile** [S27]: header 1500×500. Profile photo 400×400, 2 MB maximum.
- **Cropping**: since May 2021, single images in standard ratios (16:9, 4:3, 2:1, 3:4) show uncropped in the iOS/Android timeline. Extreme ratios are still cropped [S29].
- **Ads**: 800×418 (1.91:1) or 800×800 (1:1), 5 MB [S28].
- **Header overlap**: X does not publish where the avatar and UI cover the header. Keep a centred band clear of the bottom-left avatar (H).

### 2.6 YouTube
- **Thumbnails** [S30]:
  - Resolution: "3840 x 2160 pixels for videos and 2160 x 3840 for Shorts, with a minimum width of 640 pixels for videos".
  - Aspect: 16:9 for videos, 9:16 for Shorts, 1:1 for podcast playlists.
  - Formats: JPG or PNG.
  - File size: "Mobile: 2 MB for video thumbnails or 10 MB for podcasts; Desktop: 50MB for video, Shorts, and podcast thumbnails".
  - The account must be verified. Custom Shorts thumbnails can be added only "in YouTube Studio on a computer".
  - **Implication:** design on a 1280×720 logical canvas and export at 1920×1080 or 3840×2160. Keep a ≤2 MB JPEG variant for mobile upload.
- **Where thumbnails are shown, and what covers them (M, 2026-09-23)** [S36]:
  - Desktop "Up next" rail: **200×113** CSS px at a 1024 px viewport, **248×139** at 1440 px.
  - Mobile web search: full-width **375×210**.
  - The duration badge measured **32–38×20 px**, inset 4 px from the bottom-right on desktop and ≈8 px on mobile, with a 12 px font.
  - Scaled to the 1280×720 canvas, the keep-clear block is ≈269×153 (200-wide rail), ≈217×124 (248 rail) and ≈157×96 (mobile).
  - **Use ≈270×155 px bottom-right** (D).
  - A "New" badge also rendered in the top-left 36×20 of the rail thumbnails. The watched-progress bar along the bottom edge was not measured (**UNVERIFIED**).
- **Channel banner** [S31]:
  - "Minimum dimension for upload: 2048 x 1152 px with an aspect ratio of 16:9".
  - "At the minimum dimension, the safe area for text and logos: 1235 x 338 px".
  - "Recommended dimension (especially for TV): 2560 x 1440 px". File size ≤6 MB.
  - The safe area scales to ≈1546×423 at 2560×1440 (D), which matches third-party guides [S37].
- **Profile and watermark** [S31]: profile renders at 98×98 as JPG/GIF/BMP/PNG, no animated GIF, ≤15 MB. Watermark is square, ≥150×150, <1 MB.
- **Posts** [S34]: JPG/PNG/GIF/WEBP, up to 16 MB, up to 10 images, 1:1 suggested "because that's how images are shown in the feed".
- **End screens** [S33]:
  - Appear in the last 5–20 s. The video must be ≥25 s.
  - Up to 4 elements for 16:9. Custom images ≥300×300.
  - Not shown on mobile web (except iPad), YouTube Music, YouTube Kids, 360° video or made-for-kids content.
- **A/B testing** [S32]:
  - Up to 3 titles and/or thumbnails. Tests take "a few days or up to 2 weeks".
  - The winner has the highest watch time. If inconclusive, the first upload stays.
  - Requirements: desktop only, advanced features enabled.
  - Not available for Shorts, scheduled lives, Premieres, made-for-kids, mature or private videos.
- **CTR context** [S35]: "Half of all channels and videos on YouTube have an impressions CTR that can range between 2% and 10%." YouTube warns against clickbait because it "typically produces high CTR but low average view duration".

### 2.7 TikTok
- **In-feed ads** [S38] (updated June 2026):
  - Sizes: 9:16 ≥540×960, 16:9 ≥960×540, 1:1 ≥640×640.
  - Files ≤500 MB, ≤10 min, ≥516 kbps.
  - Ad profile image 98×98, <50 KB, with a "66px*66px" safe zone.
  - Spark Ads captions are capped at 4 lines.
  - TikTok states that the safe zone "is determined by the dimension …, the ad caption length and any interactive add-on usage; the longer the caption, the smaller the safe zone". It supplies downloadable templates and a preview tool (search summary of ads.tiktok.com pages) [S38].
- **Fixed px (third-party measured)** [S41]: about top 140, bottom 370, right 164, left 60. A more conservative set is 140/400/60/180 (T/B/L/R).
  - **Universal 9:16 box (D)** = Meta 14/35/6 plus the TikTok right rail: T269, R164, B672, L65. That leaves a safe box of 851×979 at 1080×1920.
- **Photo posts**: API photos are JPEG/WebP, ≤20 MB each, max 1080p [S39]. Photo Mode takes up to 35 images [S40].

### 2.8 Pinterest, Snapchat, Telegram, Google Business Profile
- **Pinterest** [S42]:
  - Standard pins: 2:3, 1000×1500, PNG/JPEG, ≤20 MB (desktop) or ≤32 MB (in-app).
  - "Pins with an aspect ratio greater than 2:3 might get cut off." Long pins are therefore risky; keep the story in the top 1000×1500.
  - Title ≤100 characters, of which the first ≈40 may display. Description ≤800.
  - Carousels 2–5 images at 1:1 or 2:3.
  - Idea-ad safe zones: top 270, left 65, right 195, bottom 440.
- **Snapchat** [S43]:
  - Canvas 1080×1920, 9:16. Image ≤5 MB, JPG/PNG, minimum 720×1280. Video ≤1 GB, MP4/MOV with H.264.
  - Brand name ≤32 characters. Headline ≤34.
  - The ad-formats page instead says 720×1280, brand ≤25, headline ≤34, 3–180 s [S44].
- **Telegram**:
  - `sendPhoto`: "at most 10 MB … width and height must not exceed 10000 in total … ratio must be at most 20". By URL: 5 MB for photos [S46].
  - Stickers: "one side must be exactly 512 pixels", PNG/WEBP. Video stickers WEBM ≤256 KB, ≤3 s. Animated TGS 512×512, 64 KB. Custom emoji 100×100 [S45].
- **Google Business Profile** [S47]:
  - Photos JPG/PNG, 10 KB–5 MB. Recommended 720×720, minimum 250×250.
  - Video ≤30 s, ≤75 MB, ≥720p.
  - The posts help page gives no image spec [S48]. Third-party guides use 4:3 at 1200×900 (H). Keep subjects centred, because posts appear in several crops.

---

## 3. Display ads, link cards, email and web: detail

### 3.1 IAB New Standard Ad Unit Portfolio (Tech Lab, v1.1, July 2017) [S53]
The portfolio defines flexible sizes by aspect ratio. The old fixed units map onto them as "transition" sizes. Maximum weights are in kB, gzipped, and cover initial load plus subload.

| Flex unit | Transition fixed unit(s) | Min–max size (dp) | Initial / subload kB | Static image size |
|---|---|---|---|---|
| 2×1 X-Large | "Half Page" (as printed) | 900×450 – 1800×900 | 250 / 500 | 1800×900 |
| 2×1 Small | — | 300×150 – 450×225 | 100 / 200 | — |
| 4×1 | **Billboard 970×250** | 900×225 – 1800×450 | 250 / 500 | 1800×450 |
| 6×1 | **Smartphone banner 300×50, 320×50** | 300×50 – 450×75 | 50 / 100 | 450×75 |
| 8×1 | **Leaderboard 728×90** | 600×75 – 1200×150 | 150 / 300 | 1200×150 |
| 10×1 | **Super leaderboard / pushdown 970×90** | 900×90 – 1800×180 | 200 / 400 | 1800×180 |
| 1×2 | **300×600** | 300×600 – 450×900 | 200 / 400 | 450×900 |
| 1×3 | **Portrait 300×1050** | 300×900 – 450×1350 | 250 / 500 | 450×1350 |
| 1×4 | **Skyscraper 160×600** | 160×640 – 240×960 | 150 / 300 | 240×960 |
| 1×1 | **Medium rectangle 300×250** | 300×300 – 450×450 | 150 / 300 | 450×450 |
| 2×1 tile | **120×60 Financial** | 200×100 – 300×150 | 50 / 100 | 300×150 |
| 9×16 | — | 300×540 – 450×800 | 200 / 400 | 450×800 |
| Full-page portrait | 9:16 / 10:16 / 2:3 / 3:4 | 600×1067–900×1600 · 800×1280–1200×1920 · 300×450–450×675 · 600×800–900×1200 | 300/600 · 300/600 · 200/400 · 300/600 | — |
| Full-page landscape | 16:9 L / 16:9 XL / 16:10 / 3:2 / 4:3 | 540×300–800×450 · 1067×600–1600×900 · 1280×800–1920×1200 · 450×300–675×450 · 800×600–1200×900 | 200/400 · 300/600 · 300/600 · 200/400 · 300/600 | — |

**Other IAB LEAN rules** [S53]:
- At most **10 file requests** at initial load.
- **≤30 % CPU** per ad.
- The ad choices (IBA) control is ≤5 kB.
- Animation must "not exceed **15 seconds**. No looping beyond 15 seconds."
- Hover must not trigger expansion.
- Flashing, high-contrast, fast-moving animation is "not recommended".

**Static-image weight grid by pixel area at 2×** (initial / subload / static kB) [S53]:

| Pixel area (2×) | Example units | Initial / subload / static kB |
|---|---|---|
| <180K px | 320×50, 300×50 | 50 / 100 / 50 |
| 180–300K | 728×90 | 100 / 200 / 100 |
| 300–500K | 970×90, 160×600, 300×250 | 150 / 300 / 150 |
| 500–700K | small-phone full page | 200 / 400 / 200 |
| 700–900K | 300×600, 970×250 | 250 / 500 / 250 |
| 700K–1M | large-phone full page | 300 / 600 / 300 |
| 1M+ | full page on tablets | 350 / 700 / 350 |

On slow (3G) connections, weights should be 30 % lower. The portfolio is an industry recommendation, not a law. IAB tells creatives to "consult directly with publishers".

**Google Display (responsive display) serving sizes** [S54]:
- Mobile: 300×200, 300×50, 300×100, 250×250, 200×200.
- Desktop: 300×250, 336×280, 728×90, 970×90, 468×60, 300×600, 160×600, 250×250, 200×200.

**Uploaded image-ad weight:** the usual Google Ads limit of **150 KB** is **UNVERIFIED** this session, because the old help ID now serves the responsive-display page. The IAB static weights above give the same order of magnitude.

### 3.2 Google Ads asset specs (PMax / Demand Gen / RDA) [S55][S56][S57]

| Asset | PMax | Demand Gen | RDA |
|---|---|---|---|
| Landscape 1.91:1 | 1200×628 (min 600×314), ≤20 | 1200×628 (min 600×314), 1–20 (3 recommended) | 1200×628 (min 600×314), 1–15 (5 recommended) |
| Square 1:1 | 1200×1200 (min 300×300), ≤20 | 1200×1200 (min 300×300), 1–20 | 600×600 recommended (min 300×300), 1–15 |
| Portrait 4:5 | 960×1200 (min 480×600), ≤20 | 960×1200 (min 480×600), optional | — |
| Logo 1:1 | 1200×1200 (min 128×128), ≤5 | 1200×1200 (**min 144×144**), 1–5 | 1200×1200 (min 128×128) |
| Logo 4:1 | 1200×300 (min 512×128), ≤5 | — | 1200×300 (min 512×128) |
| File | .jpg/.png, **5,120 KB** | not stated on page | not stated on page |

**Preset rule (D):** export 1200×628, 1200×1200, 960×1200, logo 1200×1200 and logo 1200×300. These satisfy all three campaign types.

The Google Ads policy pages on text overlay and borders were not reachable this session. The detailed "image assets format requirements" page is linked from `support.google.com/adspolicy/answer/6363786`. Treat these as H until verified: no overlaid logos or buttons, no borders, no collages, keep text overlays minimal.

### 3.3 Link cards (OG / X / LinkedIn / Google)
- **Meta** [S49]:
  - "Use images that are at least 1200 x 630 pixels."
  - "The minimum allowed image dimension is 200 x 200 pixels."
  - Keep "as close to 1.91:1 … as possible".
  - "must not exceed 8 MB".
  - Declare `og:image:width` and `og:image:height` so the crawler can render immediately.
- **LinkedIn**: minimum 1200×627, 1.91:1, ≤5 MB. It needs `og:title`, `og:image`, `og:description` and `og:url` [S50].
- **Google Discover**: ≥1200 px wide, >300,000 pixels, 16:9, `max-image-preview:large`. "Avoid using generic images (for example, your site logo)" and "avoid using text-heavy images" in `og:image` and schema [S51].
- **Article structured data**: supply 16:9, 4:3 and 1:1 images, each with at least 50K pixels (w×h) [S52].
- **X `summary_large_image`**: 2:1. Previously published limits are min 300×157, max 4096×4096 and <5 MB (**UNVERIFIED**; docs returned 402/404).
- **Preset rule (D):** a 1200×630 OG master with all key content in the central 1080×566 region, plus a 1200×675 (16:9) Discover or article variant.

### 3.4 Email
- **Width**: Mailchimp lists a "template width of 600px-800px" as safe, because "viewing panes are narrow" [S90]. Background images and animated GIFs are not universally supported [S90].
- **Client mix (July 2026, 1B+ opens)** [S88]: Apple 62.26 %, Gmail 27.03 %, Outlook 5.83 %, Yahoo 2.59 %, Google Android 1.45 %. Apple Mail Privacy Protection affects "roughly 55–60% of all email opens", so Apple's share is inflated.
- **Dark mode (Litmus, 27 Feb 2025)** [S89]:
  - No change: Apple Mail, Gmail desktop, AOL, Yahoo.
  - Partial invert: Outlook.com, Outlook iOS/Android, Office 365 Mac.
  - Full invert: Gmail iOS app, Outlook 2021 Windows, Office 365 Windows, Windows Mail.
  - Tactics: transparent PNG logos with a subtle outline or glow, mid-tone colours, and no pure-white-on-pure-black.
- **UNVERIFIED this session**:
  - Gmail clips messages whose HTML exceeds ≈102 KB.
  - Outlook for Windows desktop blocks images by default and shows only the first frame of a GIF.

### 3.5 Marketplace and e-commerce image rules
- **Google Merchant Center** [S58]:
  - "At least 500 x 500 pixels" for all products. Recommended "around 1500x1500 pixels or above".
  - Limits: ≤64 MP, ≤16 MB.
  - Formats: JPEG/WebP/PNG/GIF/BMP/TIFF.
  - Prohibited: calls to action ("buy"), price information, "any overlay, for example, watermarks, brand names, logos", barcodes, borders, placeholders.
- **Shopify** [S59]: "PNG, followed by JPEG". Images <20 MB, "up to 5000 x 5000 px, or 25 megapixels". "2048 x 2048 px usually displays best" for square images.
- **eBay** [S60]: minimum 500×500, about 1600×1600 recommended, up to 24 pictures, ≤12 MB each, JPEG/PNG/GIF/TIFF/BMP/WEBP/HEIC/AVIF. "Do not add graphics … such as badges, logos, copyright notices or watermarks as they can affect your listing's placement in search results."
- **Etsy** [S61]:
  - Listing photos ≥2000 px in width and height. First photo ≥635 px "to avoid showing up lower in searches".
  - ">1MB … may not finish uploading" on slow connections.
  - The first photo should be landscape or square. Thumbnails are cropped to square, portrait and landscape, so keep the subject central with negative space. The same page also says "Avoid square crops. Upload horizontal … images."
  - Banners: big 1600×400 (min 1200×300), mini 1600×213 (min 1200×160), carousel 1200×300.
  - Logo 500×500. Profile 400×400.
- **Amazon (UNVERIFIED this session; Seller Central is login-walled)**:
  - Commonly documented: main image on pure white RGB 255,255,255, product filling ≈85 % of the frame, ≥1000 px on the longest side to enable zoom (1600–2000+ recommended), ≤10,000 px.
  - Formats JPEG/TIFF/PNG/non-animated GIF. No text, logos, watermarks or props on the main image.
  - Verify in Seller Central help G1881 before shipping presets.
- **Evidence**: 56 % of users' first action on a product page was exploring the images. 25 % of sites failed on image resolution or zoom (14 % low resolution, 11 % poor zoom) (Baymard, 2 Apr 2020) [S91].

---

## 4. Print specs

### 4.1 Size table with bleed and pixel maths
- **Trim sizes**:
  - ISO A and B series [S62]: A0 841×1189 … A6 105×148. B1 707×1000, B2 500×707.
  - US sizes and Arch C/D [S63]: 18×24 and 24×36 in.
  - DL 99×210 = ⅓ A4 [S63].
  - Business cards [S64].
- **Bleed** (details in §4.2): 3 mm for metric jobs [S75]. 0.125 in for imperial jobs [S74].
- **Resolution**: px = mm ÷ 25.4 × ppi (D). Most sizes use 300 ppi. Large-format rows use 150 ppi (see §4.2 for when that is acceptable).
- **CSS page size** for Chrome at 96 CSS px/in (D):
  - A4 = 793.7×1122.5 CSS px; with 3 mm bleed 816.4×1145.2.
  - Letter = 816×1056; with bleed 840×1080.
  - Always declare `@page { size }` in **mm or in**, not in px.

| id | name | trim mm | trim in | ppi | px (trim) | bleed / side | canvas with bleed, mm | canvas with bleed, in | px with bleed |
|---|---|---|---|---|---|---|---|---|---|
| iso-a0 | A0 poster | 841×1189 | 33.110×46.811 | 150 | 4967×7022 | 3 mm (5 mm+ large-format, see §4.2) | 847×1195 | 33.346×47.047 | 5002×7057 |
| iso-a1 | A1 poster | 594×841 | 23.386×33.110 | 150 | 3508×4967 | 3 mm | 600×847 | 23.622×33.346 | 3543×5002 |
| iso-a2 | A2 poster | 420×594 | 16.535×23.386 | 300 | 4961×7016 | 3 mm | 426×600 | 16.772×23.622 | 5031×7087 |
| iso-a3 | A3 poster / menu | 297×420 | 11.693×16.535 | 300 | 3508×4961 | 3 mm | 303×426 | 11.929×16.772 | 3579×5031 |
| iso-a4 | A4 flyer / menu | 210×297 | 8.268×11.693 | 300 | 2480×3508 | 3 mm | 216×303 | 8.504×11.929 | 2551×3579 |
| iso-a5 | A5 flyer | 148×210 | 5.827×8.268 | 300 | 1748×2480 | 3 mm | 154×216 | 6.063×8.504 | 1819×2551 |
| iso-a6 | A6 flyer / postcard | 105×148 | 4.134×5.827 | 300 | 1240×1748 | 3 mm | 111×154 | 4.370×6.063 | 1311×1819 |
| iso-b2 | B2 poster | 500×707 | 19.685×27.835 | 300 | 5906×8350 | 3 mm | 506×713 | 19.921×28.071 | 5976×8421 |
| iso-b1 | B1 poster | 707×1000 | 27.835×39.370 | 150 | 4175×5906 | 3 mm | 713×1006 | 28.071×39.606 | 4211×5941 |
| dl | DL flyer (⅓ A4) | 99×210 | 3.898×8.268 | 300 | 1169×2480 | 3 mm | 105×216 | 4.134×8.504 | 1240×2551 |
| us-letter | US Letter | 215.9×279.4 | 8.5×11 | 300 | 2550×3300 | 0.125 in | 222.3×285.8 | 8.75×11.25 | 2625×3375 |
| us-legal | US Legal | 215.9×355.6 | 8.5×14 | 300 | 2550×4200 | 0.125 in | 222.3×361.9 | 8.75×14.25 | 2625×4275 |
| us-tabloid | Tabloid / Ledger | 279.4×431.8 | 11×17 | 300 | 3300×5100 | 0.125 in | 285.8×438.2 | 11.25×17.25 | 3375×5175 |
| us-half-letter | Half Letter flyer | 139.7×215.9 | 5.5×8.5 | 300 | 1650×2550 | 0.125 in | 146.1×222.3 | 5.75×8.75 | 1725×2625 |
| us-4x6 | Postcard | 101.6×152.4 | 4×6 | 300 | 1200×1800 | 0.125 in | 108×158.8 | 4.25×6.25 | 1275×1875 |
| us-5x7 | Card / flyer | 127×177.8 | 5×7 | 300 | 1500×2100 | 0.125 in | 133.4×184.2 | 5.25×7.25 | 1575×2175 |
| poster-18x24 | Poster (Arch C) | 457.2×609.6 | 18×24 | 150 | 2700×3600 | 0.125 in (0.25 in large-format) | 463.6×616 | 18.25×24.25 | 2738×3638 |
| poster-24x36 | Poster (Arch D) | 609.6×914.4 | 24×36 | 150 | 3600×5400 | 0.125–0.25 in | 616×920.8 | 24.25×36.25 | 3638×5438 |
| poster-27x40 | Movie one-sheet | 685.8×1016 | 27×40 | 150 | 4050×6000 | 0.125–0.25 in | 692.2×1022.4 | 27.25×40.25 | 4088×6038 |
| bc-us | Business card US/CA | 88.9×50.8 | 3.5×2 | 300 | 1050×600 | 0.125 in | 95.3×57.2 | 3.75×2.25 | 1125×675 |
| bc-eu | Business card W. Europe | 85×55 | 3.346×2.165 | 300 | 1004×650 | 3 mm | 91×61 | 3.583×2.402 | 1075×720 |
| bc-jp | Business card Japan | 91×55 | 3.583×2.165 | 300 | 1075×650 | 3 mm | 97×61 | 3.819×2.402 | 1146×720 |
| bc-cn | Business card China/HK | 90×54 | 3.543×2.126 | 300 | 1063×638 | 3 mm | 96×60 | 3.780×2.362 | 1134×709 |
| bc-au | Business card AU/IN | 90×55 | 3.543×2.165 | 300 | 1063×650 | 3 mm | 96×61 | 3.780×2.402 | 1134×720 |
| bc-id1 | ISO/IEC 7810 ID-1 (credit card) | 85.60×53.98 | 3.370×2.125 | 300 | 1011×638 | 3 mm | 91.6×60 | 3.606×2.361 | 1082×708 |
| rollup-850 | Roll-up banner | 850×2000 | 33.465×78.740 | 150 | 5020×11811 | per stand template | 850×2000 (+ base allowance) | — | 5020×11811 |
| rollup-1000 | Roll-up banner, wide | 1000×2000 | 39.370×78.740 | 150 | 5906×11811 | per stand template | — | — | 5906×11811 |

**Other business-card sizes** [S64]: Latin America / Eastern Europe 90×50 mm. The ID-1 and Western European formats share nearly identical proportions.

**Pixel budgets at 300 ppi (D)**:
- A1 is 7016×9933 (69.7 MP).
- A0 is 9933×14043 (139.5 MP).
- 24×36 in is 7200×10800 (77.8 MP).
- A roll-up is 10039×23622 (237 MP).

Those budgets are why large formats are rendered at 150 ppi here. Headless Chrome screenshots at these sizes are memory-hungry, so render print through the PDF path (vector) and rasterise only photos.

### 4.2 Production rules

**Bleed**
- Solopress: "There must be a minimum 3mm bleed." Its worked example: an A6 of 148×105 mm is supplied at 154×111 mm [S75].
- Imperial bleeds are "generally … 1/8 of an inch". Metric bleeds are "2mm-5mm" [S74].
- Large-format posters: "an extra 0.25 inches (6.35mm) is usually allowed" [S74].
- Die-cuts "sometimes require a 1/4" bleed" [S74].
- **Defaults**:
  - 3 mm (metric) or 0.125 in (imperial).
  - 0.25 in / 6 mm for large-format jobs.
  - 0.125 in / 3 mm around sticker die lines.
  - Always obey the printer's template when one exists.

**Safe margin (H)**
- 3–5 mm (0.125–0.25 in) inside the trim for small items. More for posters.
- Solopress requires **10 mm** on the bound edge of wiro-bound work [S75].
- No standards body defines a universal safe margin.

**Resolution**
- Solopress asks for 300 dpi throughout [S75].
- 150 ppi for A1+ posters and roll-ups is common practice for work viewed from a distance, but no printer page stating it was fetched this session (**UNVERIFIED**).
- The skill should flag placed raster images whose effective ppi falls below 300 (small print) or 150 (large format).

**Colour**
- Supply CMYK, not RGB. Solopress sets the profile to **FOGRA39** (ISO Coated v2) [S75].
- ECI profiles: PSO Coated v3 (FOGRA51), PSO Uncoated v3 (FOGRA52), ISO Coated v2 (ECI), ISO Coated v2 300 % (ECI), eciCMYK v2 (FOGRA59), and others [S71].
- **Rich black** [S72]:
  - Cool black is 70C 35M 40Y 100K.
  - Warm black is 35C 60M 60Y 100K.
  - A typical mix is 50/50/50/100.
  - Rich black for small text causes "a white or coloured halo" on misregistration. Use **100K only** for body text and fine lines.
- **Total ink**:
  - Wikipedia: "ink coverage should not exceed 240% on normal papers" [S72].
  - The commonly cited 300–330 % for coated FOGRA39/51 profiles and 260–300 % for uncoated is **UNVERIFIED**: the TAC values are not on the ECI download page [S71].
  - **Default lint threshold**: 300 % for coated and 260 % for uncoated, overridable per printer.
- **Overprint (H)**: set 100K text and lines to overprint. Never overprint white or knock-out objects. Chrome cannot set overprint, so this has to happen in post-processing.

**PDF/X** [S73]
- **PDF/X-1a:2001** (ISO 15930-1): PDF 1.3. CMYK and spot colours only. Fonts embedded. Output intent required.
- **PDF/X-3:2002**: adds calibrated RGB and Lab with ICC profiles. Still no transparency.
- **PDF/X-4** (ISO 15930-7:2008): PDF 1.6. Allows **live transparency, optional content (layers), RGB/ICC**. The X-4p variant allows an external profile.
- All PDF/X versions forbid forms, comments and multimedia, and require TrimBox and BleedBox.

**Chrome / Puppeteer output**
- Chrome implements `@page` `size`, `margin` and `page-orientation`. Other page-box properties in the spec "have not been supported by any user agent yet". **`marks` and `bleed` are not usable** [S68].
- Puppeteer `page.pdf()` [S69]:
  - `format` overrides `width` and `height` (default `letter`).
  - `preferCSSPageSize` gives the CSS `@page` size priority.
  - `printBackground` defaults to **false**, so set it to true.
  - `scale` accepts 0.1–2.
  - `tagged` (accessible PDF) defaults to true. `outline` is available.
  - `omitBackground` allows transparency.
  - `waitForFonts` defaults to true.
- Chrome writes **RGB PDFs**. It cannot write CMYK, overprint or TrimBox/BleedBox, and it does not produce PDF/X (H, consistent with [S68]).

**Ghostscript**
- It "supports creation of PDF/X-1 and PDF/X-3 formats, other formats of PDF/X are *not supported*" [S70].
- It needs `-dPDFX`, `-sColorConversionStrategy=CMYK` (RGB is prohibited) and an edited `PDFX_def.ps` that carries the output-intent ICC profile and `OutputConditionIdentifier` [S70].
- So the practical route is: **Chrome RGB PDF (with the bleed built into the page size) → Ghostscript to PDF/X-1a or X-3 in CMYK with a FOGRA39 / GRACoL profile**.
- Also set the Trim and Bleed boxes, for example with qpdf or pikepdf (H, not verified).
- Check black-text handling after conversion. RGB #000 turns into rich four-colour black unless it is mapped to K only (**test before shipping**).

### 4.3 Folded brochures: panel math and order
**Rule (D, H)**
- For roll, tri and letter folds, the panel that folds inside is **narrower**.
- The US printer convention is **1/16 in**. Metric printers use about **2–3 mm**.
- Z-folds use **equal** panels.
- For gatefolds, each outer flap is about **half the centre panel minus 1/16 in (≈2 mm)**.
- The exact numbers vary by printer and paper weight (creep), so always load the printer's template. Printer template pages were not reachable this session (**UNVERIFIED**).
- Solopress sells "6pp DL (Roll Fold)" made from an A4 297×210 sheet [S76]. DL is 99×210 [S63].

**Tri-fold (roll / letter fold): six panels, three per side (D)**

| Sheet | Outside, left → right | Inside, left → right | Fold x, outside | Fold x, inside | Fold x at 300 ppi (out / in) |
|---|---|---|---|---|---|
| US Letter 11×8.5 in | flap 3.625 · back 3.6875 · **front** 3.6875 | 3.6875 · 3.6875 · fold-in 3.625 | 3.625, 7.3125 in | 3.6875, 7.375 in | 1088, 2194 / 1106, 2212 of 3300 px |
| US Legal 14×8.5 in | 4.625 · 4.6875 · 4.6875 | 4.6875 · 4.6875 · 4.625 | 4.625, 9.3125 | 4.6875, 9.375 | 1388, 2794 / 1406, 2812 of 4200 |
| A4 297×210 mm → ≈DL | flap 97 · back 100 · **front** 100 | 100 · 100 · fold-in 97 | 97, 197 mm | 100, 200 mm | 1146, 2327 / 1181, 2362 of 3508 |
| A3 420×297 mm | 138 · 141 · 141 | 141 · 141 · 138 | 138, 279 | 141, 282 | 1630, 3295 / 1665, 3331 of 4961 |

Formula: full panel = (W + d) / 3, where d is the fold-in reduction (1/16 in or 3 mm); fold-in panel = full − d. Add the bleed around the *whole sheet*, not per panel. Keep 3–5 mm from every fold for text (H).

**Tri-fold reading order (D, from the folding geometry)**
1. **Front cover** (outside right).
2. Lifting the cover reveals **inside-left** together with the **outside of the fold-in flap** (outside left). The flap is the natural "intro / teaser / problem" panel.
3. Opening the flap reveals the **full inside spread** (inside left, middle and right). The right-hand inside panel is the narrower fold-in.
4. **Back cover** (outside middle) holds contact details, a map, a QR code, the CTA and legal text.

**Z-fold / accordion (D)**
- Equal thirds: US Letter 3 × 3.6667 in (folds at 1100 and 2200 px at 300 ppi). A4 3 × 99 mm (folds at 1169 and 2339 px).
- Panels do not nest, so each face can carry one continuous three-panel image.
- The piece reads sequentially, which suits steps, timelines and maps.

**Gatefold (D)**
- Formula: centre = W/2 + a and flap = W/4 − a/2, where a ≈ 1/16 in or 2 mm.

| Sheet | Flap · centre · flap | Closed size | Fold x at 300 ppi |
|---|---|---|---|
| Letter 11×8.5 in | 2.71875 · 5.5625 · 2.71875 in | 5.5625×8.5 in | 816, 2484 of 3300 |
| Tabloid 17×11 in | 4.21875 · 8.5625 · 4.21875 in | 8.5625×11 in | 1266, 3834 of 5100 |
| A4 297×210 mm | 73.25 · 150.5 · 73.25 mm | 150.5×210 mm | 865, 2643 of 3508 |
| A3 420×297 mm | 104 · 212 · 104 mm | 212×297 mm | 1228, 3732 of 4961 |

- **Order**: the outside flaps meet in the middle and form the **front** (design across both, with the split through the centre). The outside centre is the **back**. Opening the gates gives the **reveal**: the inside centre is the hero, with supporting content on the inner flaps.

**Bi-fold / half-fold (D)**
- Letter 11×8.5 folds to 2 × 5.5×8.5 in (fold at 1650 px). Tabloid 17×11 folds to 2 × 8.5×11 in.
- A4 folds to 2 × 148.5×210 mm (A5). A3 folds to 2 × A4.
- Outside spread: [back | front]. Inside spread: [inside left | inside right].
- For heavy stock (≥170 gsm), ask for scoring (H).

### 4.4 Posters, flyers, roll-ups, business cards, stickers, menus
- **Posters**:
  - ISO sizes: A3 297×420, A2 420×594, A1 594×841, A0 841×1189 [S62]. B2 500×707, B1 707×1000 [S62].
  - US sizes: 11×17 (Tabloid), 18×24 (Arch C), 24×36 (Arch D) [S63]. 27×40 in is the US movie one-sheet (H).
  - Solopress also sells 20×30, 30×40 and 40×60 in posters (seen on its product listings, [S75] site).
- **Flyers**: A4, A5, A6, DL 99×210 [S63][S76]. US: 8.5×11, 5.5×8.5 and 4×6 in (derived from [S63]).
- **Roll-up / pull-up banners**:
  - Solopress sells **850×2000 mm** (Premium, Style) and **800×2000 or 1000×2000 mm** stands, plus desktop A3/A4 [S77].
  - Artwork usually includes an extra strip that disappears into the base cassette. The commonly quoted 100–200 mm is **UNVERIFIED** and depends on the stand.
  - Keep logos and headlines in the top ~⅔ of the banner, above table height (H).
  - Render at 150 ppi (5020×11811 px) and supply as a vector PDF.
- **Business cards**:
  - Sizes in §4.1 [S64]. Use 3 mm or 0.125 in bleed.
  - Keep text at least 3–5 mm inside the trim (H).
  - Minimum type about 7 pt, and 8 pt for phone numbers and emails (H).
  - Keep a QR code ≥15–20 mm with its quiet zone (§4.5).
- **Stickers and labels (H, UNVERIFIED this session)**:
  - Die-cut stickers are cut through the backing to the sticker's shape. Kiss-cut stickers are cut through the vinyl only, leaving the backing sheet.
  - Supply the cut path as a separate spot-colour vector line. "CutContour" is the common name in RIP software.
  - Extend the artwork 2–3 mm (or 0.125 in) beyond the cut line. Keep text 3 mm inside it.
  - White ink on clear stickers needs its own spot layer.
- **Menus**:
  - Common sizes are A4, A3 folded to A4, US Letter, Legal 8.5×14, Tabloid 11×17 folded, and DL table cards (sizes from [S62][S63]).
  - Evidence on layout is in §5.13.

### 4.5 QR codes in print
- **Quiet zone**: "QR Code requires a four-module wide margin at all sides of a symbol" [S65]. Micro QR needs only "a two-module wide margin", but holds at most 35 numerals [S66].
- **Module size** [S67]:
  - "Printed as large as possible within the available printing area."
  - At 300 dpi with 5 dots per module, a module is 0.42 mm.
  - DENSO WAVE "recommends … each module is made up of 4 or more dots".
  - Standard scanners read ~0.25 mm modules; high-resolution scanners read 0.1 mm.
- **Sizing formula (D)**: printed width = (modules + 8) × module size.
  - A version-3 code (29 modules) at 0.5 mm per module is (29+8) × 0.5 = **18.5 mm**, the practical minimum for a business card.
  - For posters, the rule of thumb is code width ≈ scanning distance ÷ 10 (H, **UNVERIFIED**; vendor pages were not reachable).
- **Practice (H)**:
  - Use dark modules on a light ground.
  - Encode short URLs, because fewer modules means a larger module.
  - Use error-correction level M. Use level H if a logo covers the centre, and keep the logo under ~20 % of the area.
  - Test-scan the final PDF at print size.

---

## 5. Deliverable playbooks

**What the evidence can and cannot support.** Hard data found this session was mostly at format level: which *format* performs, not which *layout*. Sources: Socialinsider [S84][S85], Metricool via Hootsuite [S86], Netflix artwork research [S83], YouTube's own statements [S32][S35], Baymard [S91], NN/g [S81], Litmus [S88][S89], plus regulators [S78][S79][S80]. Layout patterns are practitioner heuristics (H) unless a source is cited. The skill must not present H items as proven.

### 5.0 Cross-cutting rules for every social graphic

**Legibility maths (D)**
- Phones show a 1080-px-wide post at roughly 360–430 CSS px, a scale of ≈0.33–0.40.
- So on a 1080 canvas (H):
  - body text ≥ **34–36 px** (≈12–14 px on screen);
  - secondary text ≥ **28 px**, used sparingly;
  - headlines **72–140 px**.

**Contrast** [S82]
- WCAG 2.2 requires 4.5:1 for normal text and 3:1 for large text: ≥18 pt, or ≥14 pt bold, which is ≈24 px or ≈18.5 px *at display size*.
- On a 1080 canvas shown at 0.36×, "large" therefore starts at ≈65 px (or ≈51 px bold) (D).
- Logotypes are exempt.
- The skill should lint contrast at display scale, not canvas scale.

**Text density** [S51]
- Google advises against "text-heavy images" for `og:image`.
- Default (H): keep on-image copy ≤25 words per frame. Put detail in the caption.

**Copy limits (official unless marked)**

| Where | Limit | Src |
|---|---|---|
| Instagram hashtags | ≤5 per post | [S87] |
| Instagram feed ad | primary text 125, headline 40 | [S05] |
| Facebook feed ad | primary text 50–150, headline 27 | [S07] |
| Instagram Reels ad | primary text 44 | [S08] |
| Threads | 500 characters | [S11] |
| LinkedIn post / document ad intro | 3,000 max; ≤150 before truncation (ads) | [S24] |
| LinkedIn single-image ad | headline 70, intro 150 | [S23] |
| LinkedIn carousel ad card | 45 | [S25] |
| Pinterest | title 100 (≈40 visible), description 800 | [S42] |
| Snapchat ad | brand 32 (help) or 25 (formats page), headline 34 | [S43][S44] |
| TikTok ad | account name 20 (10 in CJK), Spark caption ≤4 lines | [S38] |
| X post | 280 (**UNVERIFIED** this session) | — |
| Instagram caption | 2,200 (**UNVERIFIED** this session) | — |

**Format evidence**
- **Instagram 2025** (35M posts, 447,613 pages) [S84]:
  - Carousels 0.55 % engagement, Reels 0.52 %, images 0.37 %. Images fell 17 % year on year; the overall rate is 0.48 %, down 24 %.
  - Brands' monthly mix moved: images 10 → 7, Reels 6 → 8, carousels 4 → 5.
- **LinkedIn 2024–2025** (1.3M posts, 16,645 pages) [S85]:
  - Native documents 7.00 % (up 14 % year on year), multi-image 6.45 %, video 6.00 %, image 5.30 %, text 4.50 %, poll 4.20 %, link 3.25 %.
- **Metricool via Hootsuite** (3 Dec 2025) [S86]: carousels 10 %, single images 7 %, Reels 6 %. This uses a different engagement-rate definition, so do not compare it with Socialinsider's figures.

**Faces**
- Netflix artwork tests found:
  - "faces with complex emotions outperform stoic or benign expressions";
  - recognisable and polarising characters raise engagement;
  - images with **more than three people** did markedly worse [S83].
- This is streaming artwork, not social media: a strong hypothesis, not proof.

### 5.1 Social posts by intent
Default canvas: 1080×1350 (4:5) or 1080×1440 (3:4) for feeds, 1080×1920 for Stories and Reels, 1200×628 or 1200×1200 for LinkedIn and X.
Put the logo in a consistent corner, at least 64 px from the edges and outside all safe insets.

**5.1.1 Announcement**
- **Purpose.** Deliver one new fact (news, change, milestone) that can be read in under 2 seconds (H), then send people to details.
- **Anatomy (in order of prominence).**
  1. News headline.
  2. Visual anchor (product, photo or icon).
  3. Kicker label ("New", "Update").
  4. One supporting line (what and when).
  5. Brand mark.
  6. CTA, which belongs in the caption for organic posts.
- **Copy limits (H).** Headline ≤8 words. Supporting line ≤15 words. ≤25 words on the image in total. Put the news in the first 125 characters of the caption, since Meta truncates primary text at about that point in ads [S05].
- **Patterns.**
  1. *Big-type poster.* Solid brand background. Kicker chip at top-left (y≈120). Headline 110–140 px bold, left-aligned, 2–3 lines in the middle band. Sub-line 40 px. Logo bottom-right.
  2. *Photo with scrim.* Full-bleed photo. Bottom 40 % gradient (0 → 70 % black). White headline 88–110 px on the gradient.
  3. *Split.* Top 55 % image, bottom 45 % solid panel holding the headline and date.
  4. *Date stamp.* A 220–300 px date numeral with the headline beside or under it, for time-bound news.
- **Do.** One message. Include a date when the news is time-bound. Keep the same series frame across posts. Add alt text.
- **Don't.** Paragraphs on the image. Several CTAs. Hiding the news inside a logo lock-up.
- **Evidence.** Format-level only [S84][S85]. No announcement-specific study was found. The patterns are heuristic.

**5.1.2 Promo / sale**
- **Purpose.** Drive a purchase inside a real time window.
- **Anatomy.**
  1. Offer ("30 % off", "2 for 1").
  2. Product visual.
  3. Conditions: dates, "selected items", code.
  4. CTA.
  5. Brand.
  6. Legal microcopy.
- **Copy limits (H).** Offer ≤4 words. Conditions ≤12 words. Code ≤10 characters, set in a monospace or tracked style.
- **Patterns.**
  1. *Offer badge plus hero.* A large circle or rosette badge (≥260 px) overlapping the product.
  2. *Was/now price.* Strike-through old price at 60 % of the new price's size. Use only with a lawful reference price (see below).
  3. *Deadline ribbon.* "Ends Sun 28 Sep". Use only when the deadline is real.
  4. *Product grid carousel.* One product per slide, with the price chip at a fixed position.
- **Do.** Show the real end date. Say "up to" when discounts vary. Keep T&Cs readable at display size.
- **Don't.**
  - Fake urgency or an invented "was" price.
  - **Promo overlays on marketplace or feed product images.** Google Merchant Center bans price, CTA, logo and watermark overlays [S58]. eBay bans badges and logos [S60].
- **Legal.**
  - **EU:** a price reduction must quote the lowest price of the previous 30 days (Price Indication Directive Art. 6a; Commission guidance 2021) [S98] (**not re-fetched**).
  - **UK:** CMA guidance under the DMCC Act was published 4 Apr 2025 and updated on price transparency on 18 Nov 2025 [S79].
  - The skill should require a `referencePrice` and date range before it renders any "was/now" graphic.
- **Evidence.** Legal and platform rules above. No layout-level study was found.

**5.1.3 Product launch**
- **Purpose.** Introduce the product and its one key benefit, and create desire.
- **Anatomy.** Product hero (largest element), product name, one-line benefit, three feature points (icons), availability (date, price, where), CTA.
- **Copy limits (H).** Name ≤4 words. Benefit ≤10 words. Each feature ≤5 words.
- **Patterns.**
  1. *Hero on a seamless background.* Product fills 55–70 % of the frame. Name and tagline above it.
  2. *Launch carousel.* Teaser → hero → three feature slides → real proof → CTA (see §5.2).
  3. *Problem / solution split.*
  4. *Exploded callouts.* Thin leader lines from features to labels.
- **Do.** Use a sharp, real product image.
- **Don't.** Render ungrounded claims such as "best", "#1" or "clinically proven" without a source.
- **Evidence.** Carousels lead Instagram engagement [S84]. Images are the first thing product shoppers explore (56 %) [S91].

**5.1.4 Event**
- **Purpose.** Registrations and attendance.
- **Anatomy.** Event name, date and time **with timezone**, place (venue and city, or "Online"), headliners (faces), price or "Free", CTA with a short URL (or a QR code in print).
- **Copy limits (H).** Title ≤6 words. The info block is four lines: date · time · place · price.
- **Patterns.**
  1. *Info-block poster.* Oversized date, name, venue line, CTA chip.
  2. *Speaker grid.* ≤3 faces per slide, following Netflix's finding on more than three people [S83].
  3. *Countdown series.* 7, 3 and 1 days out, with one template and only the number changing.
  4. *Platform covers.* Facebook event 1920×1005 [S15]. LinkedIn event 16:9 at 1280×720 [S19].
- **Do.** Use ISO-unambiguous dates such as "Sat 11 Oct 2026". Write the timezone for online events.
- **Don't.** Overlap faces with text. Leave off the year for cross-year events.
- **Evidence.** Platform specs, plus the Netflix faces analogy.

**5.1.5 Hiring**
- **Purpose.** Attract qualified applicants and build the employer brand.
- **Anatomy.**
  1. "We're hiring" kicker.
  2. Role title (dominant).
  3. Meta chips: location or remote, contract type, **pay range**.
  4. Two or three perks or requirements.
  5. How to apply (short URL).
  6. Team or brand image.
- **Copy limits (H).** Role title ≤6 words. ≤5 chips. ≤3 bullets of ≤8 words each.
- **Patterns.**
  1. *Role card.* Title 96–120 px, chips row, apply line.
  2. *Team photo with overlay.*
  3. *Carousel.* Role → what you'll do → what we offer → how to apply.
  4. *LinkedIn document version* in PDF [S22][S85].
- **Legal.**
  - **EU Pay Transparency Directive (EU) 2023/970** [S97] (**not re-fetched**):
    - candidates must get pay information before interview or in the vacancy notice;
    - job titles must be gender-neutral;
    - transposition deadline 7 Jun 2026.
  - US state and city pay-range laws were not verified this session.
  - Make `payRange` a required field for EU and US-state jobs, and use inclusive, gender-neutral titles.
- **Evidence.** LinkedIn document and multi-image formats lead engagement [S85]. No hiring-specific study was found.

**5.1.6 Quote**
- **Purpose.** Share an insight or voice; thought leadership.
- **Anatomy.** Quote text (dominant), attribution (name, role), optional headshot, oversized quote-mark glyph, brand.
- **Copy limits (H).** Quote ≤25–30 words. Attribution ≤8 words.
- **Patterns.**
  1. 400 px quote-mark glyph at 20 % opacity behind a 56–72 px serif quote.
  2. Headshot circle (≥240 px) with the quote.
  3. Photo with a 60 % scrim and the quote.
  4. Minimal typographic layout: the quote as headline, attribution in small caps.
- **Do.** Verify the quote's wording and source. Get permission for headshots.
- **Don't.** Misattribute. Invent people.
- **Evidence.** None specific. Legibility and contrast rules apply [S82].

**5.1.7 Tip / educational**
- **Purpose.** A saveable micro-lesson that builds authority.
- **Anatomy.** Topic title, numbered tips or steps, icons, a "save / share" cue, brand, series number.
- **Copy limits (H).** Title ≤8 words. ≤5 tips per slide at ≤12 words each. On carousels, one tip per slide.
- **Patterns.**
  1. *Numbered list card.* Numbers 120 px in the accent colour.
  2. *Checklist* with ticks.
  3. *Do / don't split.* Green and red with icons as well as colour, for colour-blind readers.
  4. *Mini-infographic* (§5.8).
  5. *Carousel lesson* (§5.2).
- **Evidence.** Carousels lead Instagram at 0.55 % [S84]. Documents lead LinkedIn at 7.00 % [S85].

**5.1.8 Testimonial (real only)**
- **Purpose.** Credible social proof.
- **Anatomy.**
  1. Short **verbatim** excerpt.
  2. Customer name with role or company, used with consent.
  3. Photo (with consent) or company logo.
  4. Star rating **only** when it comes from a real review source.
  5. Source line, e.g. "Google review · May 2026".
- **Legal.**
  - **FTC rule, announced 14 Aug 2024.** It prohibits reviews or testimonials that misrepresent "that they are by someone who does not exist, such as AI-generated fake reviews", or by people without real experience. It also covers undisclosed insider reviews and incentives conditioned on sentiment. Civil penalties apply [S78].
  - **UK.** CMA fake-review guidance was published 4 Apr 2025, alongside the DMCC Act changes introduced in April 2025 [S80][S79].
- **Skill rule.** Never generate names, faces, quotes or ratings. Require `source`, `date` and `consent` fields. Add "Paid partnership" or "Employee" when there is a material connection.
- **Patterns.**
  1. Quote card with stars and source.
  2. Result card with a real metric and the timeframe.
  3. Customer photo with a short quote.
  4. A real review screenshot, reframed (with permission).
- **Evidence.** The legal framework above. No layout study was found.

**5.1.9 Behind-the-scenes**
- **Purpose.** Humanise the brand and build trust.
- **Anatomy.** Candid real photos, a short label ("In the studio"), light branding.
- **Copy limits (H).** ≤8 words on the image.
- **Patterns.**
  1. *Photo-dump carousel*, 2–20 slides [S04].
  2. *Process sequence*: step 1 → 4.
  3. *Team spotlight*: portrait, name, role.
  4. *Detail close-ups.*
- **Do.** Use real, unretouched photos (see the user's "natural photo look" memory) and faces.
- **Don't.** Pass off stock or AI-generated people as staff.
- **Evidence.** Format-level only [S84].

**5.1.10 Special day / occasion**
- **Purpose.** Take part in cultural moments and show brand values.
- **Anatomy.** Greeting headline, occasion name, a culturally appropriate motif, a small brand mark.
- **Copy limits (H).** ≤10 words.
- **Patterns.**
  1. Typographic greeting on the brand colour.
  2. Motif frame or illustration border.
  3. Photo with greeting.
  4. Product tie-in. Use this sparingly, and never on solemn days.
- **Do.** Check the local date, spelling and customs for the client's market (global by default, per the user's memory).
- **Don't.**
  - Use event trademarks or logos. For example, "Super Bowl" and Olympic marks are protected (**UNVERIFIED** this session; use generic wording such as "the big game").
  - Use religious symbols as decoration.
- **Evidence.** None fetched. This playbook is heuristic.

**5.1.11 Info / quote / tip cards as a series system**
- **Purpose.** Recognisable, repeatable "cards" that train the audience.
- **Anatomy.**
  - A fixed 12-column grid with 64–80 px outer margins on a 1080 canvas.
  - A type scale such as 36 / 48 / 72 / 110 px.
  - A series tag and number ("Tip #12").
  - The logo always in the same corner.
  - One accent colour per series.
- **Patterns.**
  1. Header band with title and body.
  2. Centred single statement.
  3. Icon plus statement.
  4. Stat card: a 200 px number, a label and the source line.
- **Do.**
  - Put a *source and date* on every stat [S92].
  - Keep contrast ≥4.5:1 at display scale [S82].
  - Export each card at 4:5 **and** 1:1 when the card goes to several platforms.
- **Don't.** Change the grid from card to card.

### 5.2 Carousels (Instagram, LinkedIn documents, TikTok photo mode)
- **Purpose.** Hold attention across a sequence that teaches, tells a story or shows a range, and earn saves and shares.
- **Anatomy.**
  1. **Hook slide.** A promise or tension in ≤8 words. It must work in the 3:4 grid crop.
  2. **Body slides.** One idea per slide.
  3. **Swipe cues.** An arrow or "swipe" chip, a "1/7" counter, and an element that carries across to slide 2.
  4. **Final CTA slide.** Save, share, follow or comment, plus the link in bio or URL.
  5. **Brand mark and series tag.** Same position on every slide.
- **Copy limits (H).** Hook ≤8 words. Body ≤30 words per slide. CTA ≤10 words.
- **Slide count.**
  - Instagram allows up to 20 [S04]. TikTok Photo Mode allows up to 35 [S40]. LinkedIn documents allow up to 300 pages [S20].
  - No verified data on the *optimal* count was found. Heuristic defaults: 5–10 slides for education, up to 20 for photo dumps.
- **Chain / seamless panorama technique (D).**
  1. Build **one wide canvas** of N×1080 by 1350 (4:5) or N×1080 by 1440 (3:4).
  2. Slide *i* is the crop x ∈ [1080(i−1), 1080·i). In HTML, render one page and take N clipped screenshots, or wrap the artboard and set `transform: translateX(-${(i-1)*1080}px)` per slide.
  3. Rules:
     - All slides share one aspect ratio, because Instagram crops to one ratio (**UNVERIFIED**).
     - **No text crosses a seam.** Keep text ≥64 px away from seams (H).
     - Let *bridging* elements cross seams: photos, lines, shapes, and a character "walking" into the next slide.
     - Every slide must also stand alone. Socialinsider notes carousels "can show up twice in someone's feed" [S84], so a viewer may land on a later slide first.
     - On 4:5, keep slide 1's hook inside the central 1012 px so it survives the grid crop (D, [S02]).
  4. Pitfalls:
     - Seams that cut through faces.
     - Colour-banding differences between slides, because each is JPEG-encoded separately. Export PNG or use high-quality JPEG.
     - Forgetting that the last slide may be seen first.
- **LinkedIn document carousels.**
  - One PDF in which all pages are the same size. Flatten layers [S22][S24]. Limits: ≤100 MB, ≤300 pages [S20].
  - Page size 1080×1350 (4:5) or 1080×1080 (H). Page 1 is the feed cover.
  - Print page numbers. Body text ≥32 px at 1080 width.
  - Native documents had the highest engagement rate on LinkedIn: **7.00 %** [S85].
- **Patterns.**
  1. *Listicle.* Hook → N tips → recap → CTA.
  2. *Story arc.* Problem → stakes → solution → proof → CTA.
  3. *Panorama chain.* One continuous illustration or photo.
  4. *Before/after.* Pairs on alternating slides.
  5. *Product range.* One product per slide with a fixed price-chip position (organic only; see §5.1.2 for legal rules).
- **Do.** Put the strongest idea on slide 1. Close on a single CTA. Keep a consistent grid.
- **Don't.** Put tiny text on slides. Split sentences across slides. Change the aspect ratio mid-set.
- **Evidence.**
  - Instagram engagement: carousels 0.55 % vs Reels 0.52 % vs images 0.37 % [S84]. Metricool: carousels 10 % vs images 7 % vs Reels 6 % [S86].
  - LinkedIn documents 7.00 % [S85].
  - Carousels can be resurfaced in the feed [S84].

### 5.3 YouTube thumbnails (plus end screens)
- **Purpose.** Win the click from the *right* viewer and set accurate expectations.
  - YouTube picks A/B winners by **watch time**, not CTR [S32].
  - It warns that clickbait "typically produces high CTR but low average view duration", which makes a video "less likely" to be recommended [S35].
- **Anatomy (in order of prominence).**
  1. **Subject.** A face with a clear, specific emotion, *or* the object or result. Aim for 35–60 % of frame height (H).
  2. **Short text (optional)** that complements the title rather than repeating it (H).
  3. A background that separates the subject: contrast, a rim light or an outline.
  4. A small, consistent series or brand element (optional).
  5. Keep-clear zones:
     - **bottom-right ≈270×155 px** at 1280×720 for the duration badge (M/D) [S36];
     - top-left ≈210×125 px where a "New" badge rendered on rail thumbnails (M, may be an experiment) [S36].
- **Copy limits (H).** ≤4 words. Cap height ≥**100 px** on a 1280×720 canvas. At the 200-px-wide rail (scale 0.156, M), that is ≈16 px on screen. Never use more than 2 lines.
- **Mobile legibility test.** The historical 168 px width is out of date. This session measured:
  - **200×113** (desktop rail at a 1024 px viewport);
  - **248×139** (desktop rail at 1440 px);
  - **375×210** (mobile web, full width) [S36].
  - The skill should render a contact sheet at those three sizes, plus 168×94 as a stress test, and fail any design whose text x-height falls under ≈7 px at 200 px width (H).
- **Patterns (1280×720).**
  1. *Face plus reaction plus object.* Face on the left 45 % (eyes on the upper third line). Object or result on the right. 2–3 words at top-right. Bottom-right kept empty.
  2. *Before / after split.* A vertical divider at x=640, an arrow across the split, labels at the top of each half.
  3. *Big result number.* 200–260 px numerals with the subject cut out. A thick outline or drop shadow for separation.
  4. *Single hero object.* The object fills 60 % of the frame on a saturated flat or gradient background that contrasts with YouTube's white and dark UIs.
  5. *Series template* for podcasts and tutorials. A fixed layout with a guest face and a 2–3-word topic. Consistent colour builds recognition.
- **Do.**
  - Separate subject from background.
  - Keep ≤3 people in frame. Netflix saw engagement drop with more than three [S83].
  - Use complex, readable emotions, which beat "stoic or benign" expressions [S83].
  - Test up to 3 variants with Test & Compare. Allow up to 2 weeks and judge on watch-time share [S32].
- **Don't.**
  - Misleading promises (see YouTube's CTR guidance [S35]).
  - Text or key objects in the bottom-right.
  - Thin fonts, low contrast, busy backgrounds.
  - Repeating the title word for word.
- **Evidence.**
  - Typical impressions CTR is 2–10 % for half of channels [S35].
  - Netflix: artwork was "the biggest influencer" of choice and "over 82% of their focus while browsing". Members spend about 1.8 s per title. Complex emotions win. More than three people hurts [S83].
  - Creator-tool studies on faces (vidIQ, TubeBuddy, 1of10) could not be verified this session. Treat the "faces always win" advice as a hypothesis to A/B test, not a rule.
- **Exports.** Upload a 1280×720 or 1920×1080 JPG under 2 MB for mobile, or up to 3840×2160 (≤50 MB) on desktop [S30]. Shorts use 9:16, and custom Shorts thumbnails are set in Studio on desktop [S30].
- **End screen frame (1920×1080).**
  - Rules: last 5–20 s, video ≥25 s, ≤4 elements [S33].
  - Design a background that leaves two element zones clear, for example a left "watch next" zone and a right "subscribe" zone, each about 35 % of the width (H).
  - Put a live, attention-holding visual behind them. Don't bake fake buttons into the video.

### 5.4 Stories (Instagram, Facebook, WhatsApp Status, Snapchat)
- **Purpose.** Quick, sequential, interactive frames that drive replies, taps and link clicks.
- **Anatomy.**
  1. Frame 1 is the hook.
  2. Content frames carry one point each.
  3. An interactive frame leaves room for a poll, quiz, question or slider sticker.
  4. The CTA frame carries a link sticker and an action verb.
- **Safe areas at 1080×1920.**
  - Meta: **T269 · B672 · L65 · R65** (14/35/6 %) [S06][S08].
  - Pinterest's 9:16 Idea ads: T270 · L65 · R195 · B440 [S42].
  - TikTok's right rail is ≈164 px (third-party) [S41].
  - **Universal box (D):** x 65–916 by y 269–1248, i.e. 851×979 px.
- **Sticker space (H).** Stickers are added in the app, so leave a clear ≈700×300 px block inside the universal box (for example y 780–1080). Don't place text behind it.
- **CTA placement (D).** Keep the link sticker and CTA above y≈1248, the start of the bottom 35 %.
- **Copy limits (H).** ≤20 words per frame. 3–7 frames per sequence.
- **Patterns.**
  1. Full-bleed photo with a headline in the upper safe band.
  2. Text frame on the brand colour with a sticker slot.
  3. Countdown or teaser.
  4. "Tap for more" sequence with a progress motif.
  5. Product frame with a link-sticker slot.
- **Do.** Use one idea per frame, big type (≥56 px), and high contrast. Put captions on any video.
- **Don't.** Put text in the top 269 px or the bottom 672 px. Crowd the right edge, because platforms put action buttons there.
- **Evidence.** Platform safe-zone guidance [S06][S08][S42][S38]. No sticker-performance study was verified this session.

### 5.5 Banners and covers (YouTube, Facebook, LinkedIn, X, web hero)
- **Purpose.** Establish identity and one value proposition in the most-viewed brand surface, working around avatars, buttons and device crops.
- **Anatomy.** Background (photo, texture or brand colour), value line (≤8 words), optional proof or cadence ("New videos every Tue"), and optional faces. Don't repeat the avatar or logo in large size, because the platform already shows it.
- **Per-surface geometry.**
  - **YouTube** (2560×1440): all text and logos inside the centred **1546×423** box [S31] (D). TV shows the whole image, so give the outer area pleasant non-critical imagery.
  - **Facebook Page** (master 1702×630):
    - The avatar overlaps the bottom-left. Keep the lower-left 660×160 clear.
    - The image is left-aligned, and a 2.4:1 crop could cut the right 190 px.
    - Keep content within x 40–1512 [S10][S36].
    - Use PNG when the cover carries text or a logo [S10].
  - **LinkedIn personal** (1584×396): the avatar sits over the lower-left on desktop (H). Put the message in the right 60 % [S18].
  - **LinkedIn company** (1512×256): a very thin strip. Use one line of text or a pattern [S17].
  - **X header** (1500×500): the avatar overlaps the lower-left. Use a central band y 60–440 with the message on the right half (H) [S27].
  - **Web hero**:
    - One static hero with a live-HTML H1 and CTA.
    - **Avoid auto-rotating carousels.** In NN/g's Siemens example the offer was visible only 20 % of the time. Moving content hurts accessibility, and carousels should advance only when users ask [S81].
    - Art-direct separate mobile crops: 1080×1350 or 1080×1920.
- **Patterns.**
  1. Right-weighted message (left side reserved for the avatar).
  2. Centred strip inside the safe band.
  3. Panoramic photo with small text.
  4. Pattern or texture with a tagline.
  5. Team collage with ≤3 prominent faces [S83].
- **Do.** Check the preset's overlay previews on desktop and mobile before export.
- **Don't.** Put CTAs or contact details in crop-prone edges. Bake body text into web hero images (it hurts accessibility and SEO, and Google advises against text-heavy og images [S51]).
- **Evidence.** Official geometry [S10][S17][S18][S31]. Measured Facebook render [S36]. NN/g [S81]. No banner-CTR study was found.

### 5.6 Posters and flyers
- **Purpose.** Stop a passer-by and convert them within seconds, then hand over the details.
- **Framework.** AIDA (Attention → Interest → Desire → Action):
  - First appeared as a formula in *Printers' Ink* in 1898 and was later articulated by E. St. Elmo Lewis.
  - Criticised as "a poor predictor of actual consumer behaviour", with "little empirical support" in a review of 250+ papers (Vakratsas & Ambler 1999) [S95].
  - Use it as a layout checklist, not a law.
- **Anatomy.**
  1. Attention: one image or headline, the largest element.
  2. Interest: a subhead with the benefit.
  3. Desire: proof, price or offer.
  4. Action: the **info block** (What · When · Where · Price · How: short URL or QR).
  5. Brand.
- **Copy limits (H).** Headline ≤7 words. Info block ≤5 lines. ≤40 words in total on an A3/A2 poster. Flyers may carry more on the reverse.
- **Hierarchy at distance (H, UNVERIFIED).** The common signage rule of about 25 mm of letter height per ~3 m (≈distance/120) for comfortable reading. Put the headline in the top third and keep the info block at eye level.
- **QR.** Size by module (§4.5): ≥18.5 mm for arm's-length reading, larger for far reading. Label it with the action and the URL.
- **Patterns.**
  1. Image-led: a full-bleed image in the top 60 % and an info band at the bottom.
  2. Typographic poster: one huge word.
  3. Swiss grid: a 12-column grid with asymmetric text.
  4. Z-pattern: logo top-left → headline → image → CTA bottom-right.
  5. Flyer with a tear-off or coupon strip.
- **Do.**
  - Build in bleed (§4.2).
  - Convert and proof brand colours in CMYK. Solopress warns RGB→CMYK conversion compromises some shades, "particularly … vivid oranges and greens" [S99].
  - Use 100K for small text [S72].
- **Don't.** Put text within the safe margin. Mix more than three type sizes. Place light text on busy photos without a scrim.
- **Evidence.** AIDA history and criticism [S95]. Printer colour guidance [S99]. No poster-effectiveness data was fetched.

### 5.7 Brochures (panel content order)
- **Purpose.** A self-guided explanation that unfolds in a predictable sequence.
- **Order by fold (D, §4.3).**
  - **Tri-fold:**
    1. **Front cover** (outside right): hook and brand.
    2. **Inside flap** (outside left), seen when the cover lifts, beside inside-left: the problem or teaser.
    3. **Inside spread** (3 panels): solution, services and proof. The right-hand inside panel is the narrower fold-in.
    4. **Back** (outside middle): contact, map, QR code and legal text.
  - **Bi-fold:** cover → inside-left (story) → inside-right (offer or pricing) → back (contact).
  - **Gatefold:** the front spans both flaps. The inside centre is the "reveal" hero, with supporting points on the inner flaps.
  - **Z-fold:** sequential steps or a timeline, and one continuous image per face.
- **Copy limits (H).** ≤60–80 words per panel. One heading per panel.
- **Patterns.**
  1. Photo cover with a bold title.
  2. Icon-led services grid across the inside spread.
  3. A bridging image across the inside spread (image only, never text across folds).
  4. Pricing table on the inside-right panel.
  5. Map and contact block on the back.
- **Do.** Keep 3–5 mm clear of every fold (H). Mark fold lines on a non-printing proof layer. Print and fold a dummy.
- **Don't.** Treat all panels as equal width on roll folds, or put a QR code across a fold.
- **Evidence.** Folding geometry only. No reading-behaviour study was fetched.

### 5.8 Infographics
- **Purpose.** Make data or processes understandable, and be shareable without distorting the truth.
- **Types and best fit.** These map onto the FT Visual Vocabulary's nine relationships: deviation, correlation, ranking, distribution, change over time, magnitude, part-to-whole, spatial and flow [S93].

| Type | Use it for |
|---|---|
| Statistical | Magnitude, part-to-whole, distribution |
| Timeline | Change over time |
| Process | Flow |
| Comparison | Deviation, ranking |
| Hierarchical | Part-to-whole trees, org charts |
| List | Tips or steps with icons |
| Geographic | Spatial data. Use **rates, not totals** on choropleths [S93] |

- **Data-integrity rules** (the lint checklist):
  1. Bars and columns start at 0. Line charts need not [S93][S92].
  2. No 3D, shadows or decorative textures [S92].
  3. No dual axes [S92].
  4. Pie charts ≤5 categories, only for a meaningful whole [S92].
  5. Label directly instead of using colour-matched legends [S92].
  6. State the source, with a link and the data date [S92].
  7. Lie factor = effect shown ÷ effect in data ≈ 1 [S94].
  8. Pictograms scale by **area**, not by height alone [S94].
  9. No truncated axes that exaggerate change [S94].
  10. Show units, n and the time frame (H).
  11. Percentages add to 100 %, or carry a rounding note (H).
  12. Keep one scale across small multiples (H).
  13. Meet WCAG 2.2 AA contrast, use light-grey gridlines (≤10) and horizontal text [S92].
  14. Use a colour-blind-safe palette (H).
- **Sizes.**
  - Social: 1080×1350.
  - Stories: 1080×1920 with the universal box.
  - Pinterest: 1000×1500. Taller pins risk truncation [S42].
  - Long-form web: e.g. 800×2000+ (H).
- **Patterns.**
  1. One big number with context and source.
  2. One chart with a headline that states the finding and a stats subtitle, as the Analysis Function asks for "headline title and statistical subtitle" [S92].
  3. Vertical timeline.
  4. Horizontal process with numbered steps.
  5. Versus comparison table.
- **Don't.** Invent data, cherry-pick ranges, or chart without a source line.
- **Evidence.** Government and FT guidance [S92][S93], and the misleading-graph literature [S94]. These are guidance, not engagement data.

### 5.9 Business cards
- **Purpose.** Identity plus contact details in the hand.
- **Anatomy (in order of prominence).** Name → role → company logo → phone, email and web → address, social handle or QR (optional).
- **Sizes.** US 3.5×2 in, EU 85×55 mm, JP 91×55 mm, CN 90×54 mm, AU/IN 90×55 mm, ID-1 85.60×53.98 mm [S64]. Bleed 3 mm or 0.125 in [S74][S75].
- **Copy limits (H).** ≤7 lines per side. Name 10–14 pt. Details 7.5–9 pt, never below 7 pt.
- **Patterns.**
  1. Front: logo only on the brand colour. Back: details.
  2. Left-aligned details with a vertical rule.
  3. Centred name with a monogram.
  4. QR back with a ≥18.5 mm code (D, §4.5).
  5. Photo card (real estate, creative work).
- **Do.** Keep 3–5 mm safe margins (H). Set small text in 100K [S72]. Supply spot-UV and foil as extra artwork [S75].
- **Don't.** Use hairline rules under 0.25 pt (H), light-grey small text, or rich black for small type.
- **Evidence.** No performance studies. Production sources only.

### 5.10 E-commerce banners (site hero, promo strips, store banners)
- **Purpose.** Sell the current offer or collection without hurting page speed or accessibility.
- **Anatomy.** Product or lifestyle visual, offer headline, 1-line support, CTA button **as live HTML**, and optional countdown or legal line.
- **Sizes.**
  - Web hero 1920×1080 and 2560×1440, plus mobile crops (H).
  - Etsy banners: big 1600×400, mini 1600×213, carousel 1200×300 [S61].
  - Amazon Store banner sizes **UNVERIFIED**.
- **Copy limits (H).** Headline ≤6 words. Support ≤12 words. One CTA.
- **Patterns.**
  1. Split hero: product image on one side, text on the other.
  2. Full-bleed lifestyle image with a text panel.
  3. A thin promo strip rendered in HTML, not as an image.
  4. Category tiles: 3–4 cards with labels.
  5. Seasonal takeover.
- **Do.** Keep text live, give images alt text, compress for LCP, and art-direct the mobile crop.
- **Don't.** Use **auto-rotating sliders** [S81], bake text into images, or reuse a marketplace main image with overlays [S58][S60].
- **Evidence.** NN/g on carousels [S81]. Baymard on image importance [S91].

### 5.11 Marketplace product images
- **Purpose.** Pass each marketplace's image rules and answer buyers' questions visually.
- **Main image.**
  - A clean product shot, square (H), 2000×2000.
  - That size satisfies Shopify's 2048 recommendation [S59], eBay's ≈1600 [S60], Etsy's ≥2000 [S61] and GMC's ≈1500 recommendation and 500 minimum [S58].
  - Amazon's white-background and 85 %-fill rules are **UNVERIFIED** this session.
- **Secondary set (H).**
  1. Feature-callout infographic: 3–5 callouts with leader lines.
  2. In-use or lifestyle shot.
  3. Scale shot (in a hand or next to an object).
  4. Dimensions diagram with units.
  5. What's in the box.
  6. Detail or texture close-up for zoom.
  7. Comparison chart (own products only).
- **Copy limits (H).** ≤5 callouts of ≤5 words each. No text at all on GMC and eBay images [S58][S60].
- **Do.** Use sRGB, consistent light and angles, and generous margins so thumbnails can crop. Etsy crops thumbnails to square, portrait and landscape [S61].
- **Don't.** Add promotional overlays, watermarks, borders, badges or prices on GMC or eBay [S58][S60]. Use placeholder images [S58].
- **Evidence.** Baymard: 56 % of users explore images first. 25 % of sites fail on resolution or zoom [S91]. eBay: graphics "can affect your listing's placement in search results" [S60].

### 5.12 Email headers
- **Purpose.** Brand recognition plus the campaign hook, in whatever rendering conditions the reader's client imposes.
- **Anatomy.** Logo bar, then the hero image. Headline, body and CTA go in **live HTML text** below the image.
- **Sizes (D, H).** Design at 600 CSS px wide (templates of 600–800 px are "safe" [S90]) and export at 2×:
  - logo bar 1200×160–240 px;
  - hero 1200×600 px.
- **Copy limits (H).** Hero overlay text ≤6 words. The real headline lives in HTML.
- **Dark mode** [S89]:
  - Gmail's iOS app and Outlook for Windows fully invert colours. Apple Mail does not change them.
  - Use transparent-PNG logos with a subtle outline or glow and mid-tone backgrounds, and avoid pure black on pure white.
- **Patterns.**
  1. Centred logo bar.
  2. Hero image with an HTML headline below.
  3. "Bulletproof" HTML button, not an image button.
  4. Animated GIF hero whose **first frame** carries the full message, because some clients don't animate [S90].
- **Do.** Write alt text on every image. Keep file weights light (H). Test in Apple Mail and Gmail, which cover about 89 % of opens between them [S88].
- **Don't.** Build an all-image email, bake the CTA into the image, or rely on CSS background images [S90].
- **Evidence.** Litmus market share and dark-mode research [S88][S89]. Mailchimp HTML limitations [S90]. Image blocking and Gmail's ≈102 KB clipping are **UNVERIFIED** this session.

### 5.13 Menus
- **Evidence.**
  - "To date, there is no empirical evidence on the efficacy of the sweet spots on menus" [S96].
  - Dollar signs and other monetary cues "may cause guests to spend less" (Yang, Kimes & Sessarego, Cornell, 2009) [S96].
- **Anatomy.** Sections with clear headers, item name, a short description (≤15 words, H), price as a bare number without a currency sign [S96], and dietary or allergen icons with a legend.
- **Patterns.**
  1. Single-page A4 or Letter with two columns.
  2. A3 folded to A4 (four pages).
  3. DL table card for specials.
  4. Board or poster menu.
- **Do.** Use ≥10–11 pt item text for dim rooms (H). Use high contrast. Keep prices aligned.
- **Don't.** Use leader dots that pull the eye to prices (H), or rely on "golden triangle" placement claims [S96].

### 5.14 Stickers
- **Anatomy.** A die-cut silhouette or roundel, a bold mark or word, and an optional outline border.
- **Copy limits (H).** ≤5 words. Minimum text 6–7 pt.
- **Patterns.**
  1. Die-cut logo with a white keyline.
  2. Circular badge.
  3. Text-only sticker.
  4. Sheet of kiss-cut mini stickers.
- **Do.** Supply the cut line as a separate spot-colour vector. Extend 2–3 mm of bleed beyond the cut. Keep text 3 mm inside it (H; **UNVERIFIED** printer guidance).
- **Don't.** Draw ultra-thin appendages that tear, or put text on the cut line.

---

## 6. Preset schema and lint rules (ready to implement)

```jsonc
{
  "id": "ig-feed-4x5",
  "platform": "instagram", "surface": "feed-portrait",
  "width": 1080, "height": 1350, "aspect": "4:5",
  "export": { "formats": ["png", "jpg"], "jpgQuality": [82, 92], "maxBytes": null, "colorSpace": "sRGB" },
  "safe": { "top": 0, "right": 34, "bottom": 0, "left": 34, "reason": "profile-grid 3:4 centre crop" },
  "keepClear": [],                      // e.g. yt-thumb: [{ "x": 1010, "y": 565, "w": 270, "h": 155, "why": "duration badge" }]
  "cropPreviews": [ { "name": "grid-3x4", "rect": [34, 0, 1012, 1350] } ],
  "displaySizesPx": [375, 430],         // widths the asset is shown at on target devices, used for legibility and contrast lint
  "copy": { "maxWordsOnImage": 25, "captionLimit": null },
  "sources": ["S01", "S02", "S13"], "confidence": "official+derived", "verifiedOn": "2026-09-23"
}
```

**Lint checks.** The layouts are HTML, so the DOM gives exact geometry.

1. **Safe zones.** Every text node's bounding rect must sit inside the safe box and outside every keepClear rect. Enforce this for logos too.
2. **Legibility.** Rendered font size × (display width ÷ canvas width) must be ≥12 px for body text, and headlines should reach ≥16 px on screen (H). For YouTube thumbnails, use display widths 200 / 248 / 375 [S36].
3. **Contrast.** Check WCAG 4.5:1 and 3:1 at *display* scale [S82]. For text over images, sample the rendered pixels behind each text box.
4. **Text density.** Count words and measure text area against `copy.maxWordsOnImage` and the preset's policy. Examples: GMC and eBay images allow **zero** overlay text [S58][S60]; the Discover and OG image should avoid being text-heavy [S51].
5. **Carousel seams.** No text rect may intersect x = k·1080 ± 64 px.
6. **Infographic integrity.** When charts are generated from data: check bar baselines, the lie factor, that a source line is present, that pie charts have ≤5 slices, and that percentages sum to 100 [S92][S93][S94].
7. **Export budget.** Reduce JPEG quality until the file fits `maxBytes`. Examples: Facebook cover <100 KB [S10], YouTube mobile 2 MB [S30], Meta 30 MB [S05], Pinterest 20 MB [S42], GMC 16 MB [S58], eBay 12 MB [S60], Threads 8 MB [S11], LinkedIn 5 MB (ads) [S23], X 5 MB [S26], Google Ads 5,120 KB [S55].
8. **Print preflight.**
   - Page size equals trim + 2 × bleed.
   - Every placed raster image reaches ≥300 ppi, or ≥150 ppi for large format.
   - Fonts are embedded.
   - Small black text is 100K after CMYK conversion.
   - TAC is ≤300 % coated or ≤260 % uncoated (defaults, overridable).
   - A QR code has its 4-module quiet zone and ≥0.25 mm modules [S65][S67].

---

## 7. Disagreements log

| Item | Value A (source) | Value B (source) | Which is official | Use |
|---|---|---|---|---|
| Facebook Page cover display | "16:9 on computers / 2.4:1 on mobile", upload 851×315 (<100 KB) [S10] | Rendered 2.70:1 on desktop web and 2.73:1 on mobile web (M) [S36]. Roundups: 851×315 desktop / 640×360 mobile [S13] | A is official, but contradicts the rendered UI | 1702×630 master with the dual-safe box (§2.2). Re-measure in the native apps |
| LinkedIn company cover | **1512×256** [S17] (≈Aug 2026) | 1128×191 [S14] (Sep 2026 roundup). 4200×700 [S13] | A | 1512×256. The 1128×191 ratio is identical, so older assets still fit |
| LinkedIn personal cover | 1584×396, <8 MB [S18] | 4200×700 [S13] | A | 1584×396; a 2× export of 3168×792 is fine if under 8 MB |
| LinkedIn event cover | 16:9: 480×270 or 1280×720, min width 480 [S19] | Older 4:1 (1776×444) and 1600×900 in roundups (search results) | A | 1280×720, or 1920×1080 for sharpness |
| YouTube thumbnail size and weight | 3840×2160 max. 50 MB desktop, 2 MB mobile [S30] | "1280×720, 2 MB" in most roundups [S14] | A | Design at 1280×720, export 1920×1080 ≤2 MB, plus an optional 4K master for desktop upload |
| YouTube banner safe area | 1235×338 at the 2048×1152 minimum [S31] | 1546×423 at 2560×1440 [S37] | Same area scaled (D) | Centred 1546×423 at 2560×1440 |
| Instagram grid tile | 3:4. Sprout "1012×1350" [S13] | "1080×1440" (search summaries) [S02] | Both are 3:4 | For a 4:5 post the grid shows 1012.5×1350. For a 3:4 post, the full 1080×1440 |
| Instagram hashtags | ≤5 per post (organic help) [S87] | ≤30 (ads guide) [S05] | Both official, different contexts | Organic ≤5 |
| Meta 9:16 safe zone | 14 % / 35 % / 6 % (Stories and Reels ads guide) [S06][S08] | Older "14 % top and bottom (≈250 px)" Stories guidance (widely repeated) | A | 14/35/6. Add 40 % bottom when a disclaimer is present (third-party) [S09] |
| Facebook feed ad size | 1440×1800, min 600×750 [S07] | 1080×1350 organic [S13] | A for ads | Ads 1440×1800. Organic 1080×1350 or 1440 |
| Snapchat brand-name length | 32 characters [S43] | 25 characters [S44] | Both official Snap pages | ≤25 satisfies both |
| Snapchat resolution | 1080×1920 canvas, min 720×1280 [S43] | "Resolution: 720x1280" [S44] | Both official | Design at 1080×1920 |
| TikTok safe zone | Varies with caption length and add-ons; use templates and preview [S38] | Fixed px ≈T140/B370/R164/L60 [S41] | A (qualitative) | Conservative box plus preview in Ads Manager |
| Google square image | RDA recommends 600×600 [S57] | PMax and Demand Gen 1200×1200 [S55][S56] | Both official | 1200×1200 satisfies all |
| Google logo minimum | 128×128 (PMax, RDA) [S55][S57] | 144×144 (Demand Gen) [S56] | Both official | ≥144, ideally 1200×1200 |
| GMC minimum image | 500×500 for all products [S58] | Older 100×100 / 250×250 (legacy guides) | A | ≥500. Target ≥1500 |
| Etsy first-photo orientation | "horizontal (landscape) or square" [S61] | "Avoid square crops. Upload horizontal … images" (same page) [S61] | Same page | Landscape 4:3 master with wide margins |
| Pinterest file size | 20 MB desktop [S42] | 32 MB in-app [S42] | Same page | ≤20 MB |
| Metric bleed | 3 mm minimum [S75] | 2–5 mm [S74] | Printer vs encyclopedia | 3 mm default. Follow the printer's template |
| Total ink limit | ≤240 % "on normal papers" [S72] | 300–330 % coated profile TACs (commonly cited; **UNVERIFIED**) | Neither is a profile document | Lint at 300 % coated / 260 % uncoated. Always prefer the printer's ICC and TAC |
| Carousel engagement rate | Carousels 0.55 % vs Reels 0.52 % vs images 0.37 % [S84] | Carousels 10 % vs images 7 % vs Reels 6 % [S86] | Both third-party; different ER definitions | Quote each with its own definition; never mix them |

---

## 8. Recommendations for our skill

1. **Ship a versioned preset registry, not hard-coded sizes.**
   - Use §1 plus the schema in §6. Every preset carries `sources`, `confidence` and `verifiedOn`.
   - Re-verify volatile presets quarterly: Facebook cover, LinkedIn covers, YouTube thumbnail limits, Meta ad resolutions and zones, Instagram aspect and hashtag rules, GMC minimums. At least five of these changed between 2024 and 2026 (§0).
2. **Default choices for 2026.**
   - Instagram organic single posts and carousels: **1080×1440 (3:4)**. It is the largest in-feed area and needs no grid crop [S01][S03].
   - Cross-posted organic content (IG, FB, LinkedIn, Threads): **1080×1350 (4:5)**, since LinkedIn recommends 4:5 for vertical [S23].
   - Meta ads: **1440×1800** and **1440×2560** [S05][S06][S07].
   - Any 9:16 asset: the **universal safe box** x 65–916, y 269–1248 at 1080×1920 (D, from [S06][S41]).
   - YouTube thumbnails: 1280×720 logical, exported at 1920×1080 in JPEG under 2 MB [S30].
3. **Render exact pixels deterministically.**
   - Set the viewport to the *logical* size and `deviceScaleFactor` so the output hits the preset's pixel size exactly. Example: 540×675 CSS at 2× gives 1080×1350.
   - Wait for `document.fonts.ready`, disable animations and fix the random seed before taking the screenshot.
   - For organic Instagram, never export wider than 1080; anything wider is downscaled [S01].
4. **Make QA visual and automatic.**
   - For every export, also write a `.debug.png` with the safe zones, keep-clear rects and crop previews drawn on: IG grid 3:4, 4:5 feed, 1:1, the YouTube badge, the Facebook avatar.
   - Run the DOM lint in §6 and fail the build on violations.
   - For thumbnails, write a contact sheet at 200 / 248 / 375 / 168 px width.
5. **Design once, re-flow per preset, don't just crop.**
   - Build layouts on CSS variables (safe-box insets, type scale based on canvas width) and use container queries, so one design re-flows into 3:4, 4:5, 1:1, 9:16 and 16:9 with each preset's safe box.
   - Reserve naive cropping for photographic backgrounds only.
6. **Carousel engine.**
   - Render one wide artboard and take clipped screenshots per slide (§5.2).
   - Lint seams. Automatically add a "1/N" counter and a swipe cue.
   - Emit a LinkedIn PDF version, with every page the same size and flattened, from the same slides [S22][S24].
7. **Print pipeline (Chrome is RGB-only).**
   1. Render the HTML with `@page { size: <trim + 2×bleed> }`. Set `preferCSSPageSize: true` and `printBackground: true` [S68][S69].
   2. Extend backgrounds to the page edge. Keep text inside the trim minus the safe margin.
   3. Post-process to set TrimBox and BleedBox (qpdf or pikepdf, H).
   4. Convert to **CMYK PDF/X-1a or PDF/X-3 with Ghostscript** (`-dPDFX -sColorConversionStrategy=CMYK` plus a `PDFX_def.ps` carrying a FOGRA39 / PSO Coated v3 / GRACoL ICC). Ghostscript cannot write PDF/X-4 [S70][S71][S75].
   5. Verify pure-K black text after conversion, and add overprint for black text in post-processing.
   6. Ship a preflight report (§6, item 8).
   7. Keep fold guides and crop marks in a separate, optional layer or output.
   8. If a printer accepts RGB PDFs (many online printers auto-convert), say so explicitly and still warn about gamut. Vivid oranges and greens shift [S99].
8. **Fold templates as components.**
   - Provide bi-fold, roll-fold tri-fold (with the narrower fold-in panel), Z-fold and gatefold.
   - Parameters: sheet size, fold-in reduction d (1/16 in or 3 mm default), bleed, and outside/inside page order (§4.3).
   - Always tell the user to load the printer's own template when one exists.
9. **Content guardrails built into the playbooks.**
   - **Testimonials:** require `source`, `date` and `consent`; refuse fabricated names, faces, quotes or stars [S78][S80].
   - **Prices:** require a reference price and dates before rendering "was/now" (EU 30-day rule [S98]; UK CMA [S79]).
   - **Marketplace images:** no promotional overlays for GMC or eBay [S58][S60].
   - **Hiring posts:** pay-range field for the EU (Directive 2023/970, transposition 7 Jun 2026 [S97]) and gender-neutral titles.
   - **Events:** trademark caution on event names.
   - **Imagery:** people and places come from the client's context (per the user's "global by default" memory), and photos must look unretouched.
10. **Treat evidence honestly in the UI.**
    - When the skill explains a design choice, it should cite the §9 source ID, or label the choice "heuristic".
    - Format-level data (for example carousels 0.55 % vs images 0.37 % [S84], LinkedIn documents 7.00 % [S85]) can justify *format* recommendations. It does not prove that a *layout* works.
11. **Close the gaps in §10 before the presets are frozen.** Priorities: Amazon image rules, the X card spec, the Snapchat and TikTok px safe zones, a printer trifold/gatefold template, and printer TAC values. Each needs one authenticated or non-blocked fetch.

---

## 9. Sources (ID → publisher · title · URL · date/version · type)

- **S01** Instagram Help Centre · "Image resolution of photos you share on Instagram" · https://help.instagram.com/1631821640426723 (read via https://www.facebook.com/help/instagram/1631821640426723) · undated, accessed 2026-09-23 · official
- **S02** Kapwing · "Instagram's New Grid Layout: Size and Dimensions (2026)" · https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/ · 2026 edition (seen via search summary 2026-09-23). Summary also cites Mosseri's Threads announcement (Jan 2025) and ALM Corp "Instagram Now Lets You Edit Post Thumbnails on Your Profile Grid" (https://almcorp.com/blog/instagram-thumbnail-editing-profile-grid/) · third-party
- **S03** PetaPixel · "Instagram Finally Adds Support for 3:4 Aspect Ratio Photos" · https://petapixel.com/2025/05/29/instagram-finally-adds-support-for-34-aspect-ratio-photos/ · 2025-05-29 (search summary; corroborated by Lindsey Gamble and Slashdot, 2025-05-30) · third-party news
- **S04** Adam Mosseri, Threads post (carousel up to 20) · https://www.threads.com/@mosseri/post/C-c-E5FppV_ · Aug 2024. MacRumors · https://www.macrumors.com/2024/08/08/instagram-20-photos-carousel-posts/ · 2024-08-08 (search summary) · official exec + news
- **S05** Meta Ads Guide · Instagram Feed image · https://www.facebook.com/business/ads-guide/update/image/instagram-feed · undated, accessed 2026-09-23 · official
- **S06** Meta Ads Guide · Instagram Stories image · https://www.facebook.com/business/ads-guide/update/image/instagram-story · undated, accessed 2026-09-23 · official
- **S07** Meta Ads Guide · Facebook Feed image · https://www.facebook.com/business/ads-guide/update/image/facebook-feed · undated, accessed 2026-09-23 · official
- **S08** Meta Ads Guide · Instagram Reels video · https://www.facebook.com/business/ads-guide/update/video/instagram-reels · undated, accessed 2026-09-23 · official
- **S09** billo.app · "Meta Ads Safe Zones: 2026 Unified Creative Updates" · https://billo.app/blog/meta-ads-safe-zones/ · AdNabu https://blog.adnabu.com/meta-ads/meta-safe-zones/ · 2026 (search summary) · third-party
- **S10** Facebook Help Centre · "Facebook Page profile picture and cover photo dimensions" · https://www.facebook.com/help/125379114252045 · undated, text read verbatim 2026-09-23 · official
- **S11** Meta for Developers · Threads API overview (media specs, limits) · https://developers.facebook.com/docs/threads/overview · undated, accessed 2026-09-23 · official
- **S12** Meta for Developers · WhatsApp Cloud API: Media reference · https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media · undated, accessed 2026-09-23 · official
- **S13** Sprout Social · "Social media image sizes guide" · https://sproutsocial.com/insights/social-media-image-sizes-guide/ · updated 2026-05-11 · third-party
- **S14** Hootsuite · "Social media image sizes for all networks [September 2026]" · https://blog.hootsuite.com/social-media-image-sizes-guide/ · 2026-09-02 · third-party
- **S15** Sprout Social · "Facebook event photo size" · https://sproutsocial.com/insights/facebook-event-cover-photos/ (plus Typeform and Snappa 2026 guides) · 2026 (search summary; notes Meta publishes no official event-cover spec) · third-party
- **S16** Snappa · "The Proper Facebook Group Cover Photo Size (2026 Update)" · https://snappa.com/blog/facebook-group-cover-photo-size/ · 2026 (search summary) · third-party
- **S17** LinkedIn Help a563309 · "Image specifications for your LinkedIn Pages and Career Pages" · https://www.linkedin.com/help/linkedin/answer/a563309 · "Last updated: 1 month ago" (≈Aug 2026) · official
- **S18** LinkedIn Help a568217 · "Add or change the cover image on your profile" · https://www.linkedin.com/help/linkedin/answer/a568217 · "Last updated: 6 months ago" (≈Mar 2026) · official
- **S19** LinkedIn Help a554183 · "Create a LinkedIn Event" · https://www.linkedin.com/help/linkedin/answer/a554183 · "Last updated: 4 months ago" (≈May 2026) · official
- **S20** LinkedIn Help a564109 · "Media file types supported on LinkedIn" · https://www.linkedin.com/help/linkedin/answer/a564109 · "Last updated: 9 hours ago" (2026-09-23) · official
- **S21** LinkedIn Help a517940 · "LinkedIn Newsletters best practices" · https://www.linkedin.com/help/linkedin/answer/a517940 · undated (official-domain search summary, 2026-09-23) · official
- **S22** LinkedIn Help a518909 · "Upload and share documents on LinkedIn" · https://www.linkedin.com/help/linkedin/answer/a518909 · undated (official-domain search summary) · official
- **S23** LinkedIn Marketing Solutions Help a426534 · "Single image ads advertising specifications" · https://www.linkedin.com/help/lms/answer/a426534 · undated (official-domain search summary) · official
- **S24** LinkedIn Marketing Solutions Help a493903 · "Document ads advertising specifications" · https://www.linkedin.com/help/lms/answer/a493903 · "Last updated: 10 months ago" (≈Nov 2025) · official
- **S25** LinkedIn Marketing Solutions Help a427022 · "Carousel Ads advertising specifications" · https://www.linkedin.com/help/lms/answer/a427022 · "Last updated: 10 months ago" (≈Nov 2025) · official
- **S26** X Help · "How to Post pictures or GIFs" · https://help.x.com/en/using-x/posting-gifs-and-pictures · undated (official-domain search snippet, 2026-09-23) · official
- **S27** X Help · "How to upload X profile photos and headers and best sizes" · https://help.x.com/en/managing-your-account/common-issues-when-uploading-profile-photo · undated (search snippet; direct fetch returned 403) · official
- **S28** X Business · "X Ads creative specs" · https://business.x.com/en/help/campaign-setup/creative-ad-specifications-old · undated (search snippet; fetch returned 402) · official
- **S29** TechCrunch · "Twitter rolls out bigger images and cropping control on iOS and Android" · https://techcrunch.com/2021/05/05/twitter-image-cropping-changes/ · 2021-05-05 (search summary) · news
- **S30** YouTube Help 72431 · "Add video thumbnails" · https://support.google.com/youtube/answer/72431 · undated, accessed 2026-09-23 · official
- **S31** YouTube Help 10456525 · "Manage your channel branding" · https://support.google.com/youtube/answer/10456525 · undated, accessed 2026-09-23 · official
- **S32** YouTube Help 13861714 · "A/B test titles & thumbnails" · https://support.google.com/youtube/answer/13861714 · undated, accessed 2026-09-23 · official
- **S33** YouTube Help 6388789 · "Add end screens to videos" · https://support.google.com/youtube/answer/6388789 · undated · official
- **S34** YouTube Help 7124474 · "Create a post" · https://support.google.com/youtube/answer/7124474 · undated · official
- **S35** YouTube Help 7628154 · "Impressions & click-through-rate FAQs" · https://support.google.com/youtube/answer/7628154 · undated · official
- **S36** First-hand measurement (this session) · Chromium pane, `getBoundingClientRect` on live pages: youtube.com watch page at 1024 and 1440 px viewports; m.youtube.com/results at 375×812; facebook.com/facebook at 1024 px; m.facebook.com/facebook at 360 px · 2026-09-23 · primary observation (subject to UI experiments)
- **S37** Have Camera Will Travel · "YouTube Banner Dimensions: Ideal, Min, and Safe Area Size" · https://havecamerawilltravel.com/workflow/youtube-banner-size/ (also Wyzowl https://wyzowl.com/youtube-banner-size/) · 2026 (search summary) · third-party
- **S38** TikTok Ads Manager · "TikTok Auction In-Feed Ads" · https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads · last updated June 2026. The safe-zone wording comes from ads.tiktok.com search summaries · official
- **S39** TikTok for Developers · "Content Posting API: Media Transfer Guide" · https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide · undated · official
- **S40** TikTok Newsroom · "Inspiring creativity with our new editing tools" (Photo Mode, up to 35 images) · https://newsroom.tiktok.com/en-us/editing-tools · date not captured (search summary) · official
- **S41** CreaMate · "TikTok Safe Zone in 2026" · https://creamate.ai/en/blog/tiktok-safe-zone-guide (also Zeely https://zeely.ai/blog/tiktok-safe-zones/) · 2026 (search summary) · third-party
- **S42** Pinterest Business Help · "Pinterest product specs" · https://help.pinterest.com/en/business/article/pinterest-product-specs · undated, accessed 2026-09-23 · official
- **S43** Snapchat Business Help · "Single Image or Video Specifications" · https://businesshelp.snapchat.com/s/article/top-snap-specs?language=en_US · undated, read in browser 2026-09-23 · official
- **S44** Snapchat for Business · "Ad formats" · https://forbusiness.snapchat.com/advertising/ad-formats · undated, accessed 2026-09-23 · official
- **S45** Telegram · "Stickers" · https://core.telegram.org/stickers · undated · official
- **S46** Telegram · Bot API (sendPhoto; sending files) · https://core.telegram.org/bots/api#sendphoto · current, read 2026-09-23 · official
- **S47** Google Business Profile Help 6103862 · photo and video requirements · https://support.google.com/business/answer/6103862 · undated · official
- **S48** Google Business Profile Help 7662907 · "Create & manage posts on your Business Profile" · https://support.google.com/business/answer/7662907 · undated (no image spec) · official
- **S49** Meta for Developers · "Images in Link Shares" · https://developers.facebook.com/docs/sharing/webmasters/images/ · undated · official
- **S50** LinkedIn Help a521928 · "Make your website shareable on LinkedIn" · https://www.linkedin.com/help/linkedin/answer/a521928 · "Last updated: 2 years ago" (≈2024) · official
- **S51** Google Search Central · "Google Discover" · https://developers.google.com/search/docs/appearance/google-discover · last updated 2026-03-09 · official
- **S52** Google Search Central · "Article structured data" · https://developers.google.com/search/docs/appearance/structured-data/article · last updated 2026-09-08 · official
- **S53** IAB Tech Lab · "IAB New Standard Ad Unit Portfolio" · https://www.iab.com/wp-content/uploads/2017/08/IABNewAdPortfolio_FINAL_2017.pdf · July 2017, v1.1 · industry standard
- **S54** Google Ads Help 7031480 · responsive display ad sizes · https://support.google.com/google-ads/answer/7031480 · undated · official
- **S55** Google Ads Help 17091269 · "Performance Max campaigns specs and format requirements" · https://support.google.com/google-ads/answer/17091269 · undated · official
- **S56** Google Ads Help 17091672 · "Demand Gen campaigns specs and format requirements" · https://support.google.com/google-ads/answer/17091672 · undated · official
- **S57** Google Ads Help 17090561 · "Responsive display ads specs and format requirements" · https://support.google.com/google-ads/answer/17090561 · undated · official
- **S58** Google Merchant Center Help 6324350 · "Image link [image_link]" · https://support.google.com/merchants/answer/6324350 · undated, accessed 2026-09-23 · official
- **S59** Shopify Help · "Product media types" · https://help.shopify.com/en/manual/products/product-media/product-media-types · undated · official
- **S60** eBay Help · "Adding pictures to your listings" · https://www.ebay.com/help/selling/listings/adding-pictures-listings?id=4148 · undated · official
- **S61** Etsy Help · "Requirements and Best Practices for Images in Your Etsy Shop" · https://help.etsy.com/hc/en-us/articles/115015663347 · undated, read in browser 2026-09-23 · official
- **S62** Wikipedia · "ISO 216" (A, B and C series; tolerances) · https://en.wikipedia.org/wiki/ISO_216 · accessed 2026-09-23 · secondary (ISO 216 itself is paywalled)
- **S63** Wikipedia · "Paper size" (US, ANSI, Arch, envelopes, ⅓ A4) · https://en.wikipedia.org/wiki/Paper_size · accessed 2026-09-23 · secondary
- **S64** Wikipedia · "Business card" (sizes table) · https://en.wikipedia.org/wiki/Business_card · accessed 2026-09-23 · secondary
- **S65** DENSO WAVE (QR inventor) · QR Code capacity and margin · https://www.qrcode.com/en/howto/code.html · undated · official
- **S66** DENSO WAVE · "Micro QR Code" · https://www.qrcode.com/en/codes/microqr.html · undated · official
- **S67** DENSO WAVE · module size · https://www.qrcode.com/en/howto/cell.html · undated · official
- **S68** MDN · "@page" · https://developer.mozilla.org/en-US/docs/Web/CSS/@page · last modified 2026-09-12 · reference
- **S69** Puppeteer · "PDFOptions" · https://pptr.dev/api/puppeteer.pdfoptions · current docs (accessed 2026-09-23) · official
- **S70** Ghostscript documentation · "High Level Devices" (PDF/X) · https://ghostscript.readthedocs.io/en/latest/VectorDevices.html · "latest" (accessed 2026-09-23) · official
- **S71** European Color Initiative · Downloads (ICC profiles) · https://www.eci.org/en/downloads · profile versions 2008–2022 · official
- **S72** Wikipedia · "Rich black" · https://en.wikipedia.org/wiki/Rich_black · accessed 2026-09-23 · secondary
- **S73** Wikipedia · "PDF/X" · https://en.wikipedia.org/wiki/PDF/X · accessed 2026-09-23 · secondary (ISO 15930-1:2001, -3:2002, -7:2008)
- **S74** Wikipedia · "Bleed (printing)" · https://en.wikipedia.org/wiki/Bleed_(printing) · accessed 2026-09-23 · secondary
- **S75** Solopress (UK printer) · "Supplying Artwork Guide" · https://www.solopress.com/support-guides/supplying-artwork/ · ©2026, read 2026-09-23 · printer house rules
- **S76** Solopress · "Roll Fold Leaflets" · https://www.solopress.com/folded-flyers-leaflets/roll-fold/ · ©2026 · printer
- **S77** Solopress · "Roller Banners" · https://www.solopress.com/roller-banners/ · ©2026 · printer
- **S78** US FTC · "Federal Trade Commission Announces Final Rule Banning Fake Reviews and Testimonials" · https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials · 2024-08-14 · regulator
- **S79** UK CMA · "Unfair commercial practices (CMA207)" · https://www.gov.uk/government/publications/unfair-commercial-practices-cma207 · published 2025-04-04, updated 2025-11-18 · regulator
- **S80** UK CMA · "Fake reviews (CMA208)" · https://www.gov.uk/government/publications/fake-reviews-cma208 · 2025-04-04 · regulator
- **S81** Nielsen Norman Group · "Auto-Forwarding Carousels and Accordions Annoy Users and Reduce Visibility" (Jakob Nielsen) · https://www.nngroup.com/articles/auto-forwarding/ · 2013-01-19 · research
- **S82** W3C WAI · "Understanding SC 1.4.3: Contrast (Minimum)", WCAG 2.2 · https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html · WCAG 2.2 · standard
- **S83** Netflix · "The Power of a Picture" (Nick Nelson) · https://about.netflix.com/en/news/the-power-of-a-picture · 2016-05-03 · first-party research
- **S84** Socialinsider · "2026 Instagram organic engagement benchmarks" · https://www.socialinsider.io/social-media-benchmarks/instagram · data Jan–Dec 2025, 35M posts / 447,613 pages · third-party study
- **S85** Socialinsider · "LinkedIn organic benchmarks 2026" · https://www.socialinsider.io/social-media-benchmarks/linkedin · data Jan 2024–Dec 2025, 1.3M posts / 16,645 pages · third-party study
- **S86** Hootsuite · Instagram carousel guide (citing Metricool) · https://blog.hootsuite.com/instagram-carousel/ · 2025-12-03 · third-party
- **S87** Instagram Help Centre · hashtags ("up to 5 tags on a post") · https://help.instagram.com/351460621611097 (read via https://www.facebook.com/help/instagram/351460621611097) · undated, accessed 2026-09-23 · official
- **S88** Litmus · "Email Client Market Share" · https://www.litmus.com/email-client-market-share · July 2026 data (1B+ opens) · third-party data
- **S89** Litmus · "The Ultimate Guide to Dark Mode for Email Marketers" · https://www.litmus.com/blog/the-ultimate-guide-to-dark-mode-for-email-marketers · 2025-02-27 · third-party
- **S90** Mailchimp · "Limitations of HTML Email" · https://mailchimp.com/help/limitations-of-html-email/ · undated · vendor docs
- **S91** Baymard Institute · "Ensure Sufficient Image Resolution and Zoom" · https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom · 2020-04-02 · UX research
- **S92** UK Government Analysis Function · "Data visualisation: charts" · https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/ · 2022-05-19 · government guidance
- **S93** Financial Times · Visual Vocabulary (chart-doctor README) · https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary · undated · publisher guidance
- **S94** Wikipedia · "Misleading graph" (Tufte's lie factor) · https://en.wikipedia.org/wiki/Misleading_graph · accessed 2026-09-23 · secondary
- **S95** Wikipedia · "AIDA (marketing)" · https://en.wikipedia.org/wiki/AIDA_(marketing) · accessed 2026-09-23 · secondary
- **S96** Wikipedia · "Menu engineering" (citing Yang, Kimes & Sessarego 2009, Cornell Hospitality Report) · https://en.wikipedia.org/wiki/Menu_engineering · accessed 2026-09-23 · secondary
- **S97** EUR-Lex · Directive (EU) 2023/970 (pay transparency) · https://eur-lex.europa.eu/eli/dir/2023/970/oj · adopted 2023-05-10. **Page did not render for the fetcher**; articles cited from the directive as known (Art. 5 pre-employment pay information and gender-neutral notices; Art. 34 transposition by 2026-06-07). Re-verify · law
- **S98** EUR-Lex · Commission guidance on Art. 6a of Directive 98/6/EC (price reductions; 30-day prior price) · https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021XC1229(06) · 2021-12-29. **Did not render**; re-verify · law / guidance
- **S99** Solopress · "Colour Guide" · https://www.solopress.com/support-guides/colour/ · ©2026, read 2026-09-23 · printer house rules

---

## 10. Unverified items and gaps (fix before freezing presets)

| Item | Why unverified | Next step |
|---|---|---|
| Amazon main-image rules (white RGB 255, 85 % fill, 1000 px zoom, 10,000 px max, formats) and A+ / Store sizes | Seller Central G1881 is login-walled; logging in is off-limits | The user opens G1881 while signed in, or we find a public Amazon mirror |
| X `summary_large_image` spec (2:1, 300×157 min, 4096×4096 max, <5 MB) and the header overlap | X developer docs returned 402 / 404 / redirect; help returned 403 | Fetch docs.x.com once the new path is known |
| Snapchat safe-zone pixels | Help page links "Safe Zones for Ads" only as an image or example | Open the Snap example or Ads Manager preview |
| TikTok safe-zone pixels | Official guidance is qualitative (varies with caption and add-ons) | Download the official TikTok safe-zone template (needs a user download OK) |
| WhatsApp Status / Channels pixel spec; WhatsApp sticker 512×512 | No official page found | WhatsApp FAQ and sticker-maker docs |
| Instagram caption limit (2,200), carousel single-aspect enforcement, grid-thumbnail adjust feature | Search budget exhausted before they were fetched | Instagram Help / @creators |
| X 280-character limit | Not fetched this session | help.x.com |
| Tri-fold / gatefold exact printer templates; roll-up base allowance; 150 ppi guidance; sticker cut-contour naming | Printer sites blocked the fetcher, or templates are downloads | Get a printer's template (with user OK) or its FAQ pages in the browser |
| TAC per ICC profile (FOGRA39/51/52, GRACoL, SWOP, newsprint) | Not on the ECI download page | ECI / FOGRA characterization docs or printer spec sheets |
| Gmail clipping (~102 KB), Outlook image blocking and GIF first frame | Email vendor URLs 404'd | Litmus / Email on Acid articles |
| Google Ads uploaded-image-ad 150 KB, and text-overlay / border policy | Help IDs moved | support.google.com/adspolicy image requirements |
| QR distance rule (≈10:1) and 2 cm minimum | Vendor pages 404'd | Bitly / QR Code Generator Pro docs |
| EU pay-transparency and price-reduction texts; US pay-range laws; event trademark rules (NFL, IOC) | EUR-Lex did not render; search budget exhausted | Re-fetch with a working renderer |
| YouTube watched-progress-bar height; creator-tool face/CTR studies | Not measured / not found | Measure on a logged-in history page; fetch vidIQ / 1of10 studies |
| Facebook cover in native apps; LinkedIn and X avatar overlap geometry | Only the web was measured | Measure in the iOS/Android apps (manual) |
