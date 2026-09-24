# Social formats: what is missing, what changed, and how to design each one

Research for the codex-design preset registry. Scope: Instagram, Facebook, Meta ads (Facebook, Instagram, Messenger, Threads), Threads, WhatsApp Status, Pinterest, YouTube, TikTok, LinkedIn, X, Bluesky, Mastodon and Snapchat. TikTok Shop and other commerce formats are out of scope.

Companion file: `social.json` holds the new presets in the skill's schema.

## How this was done

- **Dates.** Dates follow the brief: verified 2026-09-24. The machine clock read 2026-09-24 (+06). Most platform help pages show no date; where a page shows "Last updated", it is converted to a month.
- **Sources, in order of trust.**
  1. The platform's own help centre, ads guide or developer docs.
  2. Official source code or design systems (Bluesky lexicons, Pinterest Gestalt).
  3. Widely cited guides (Hootsuite, Sprout Social, Buffer), only where no official page exists, and labelled.
- **Measured.** Some facts were measured in a Chromium pane with `getBoundingClientRect` on live, logged-out web pages (Instagram, Facebook, YouTube, Pinterest, X, Bluesky, Mastodon, Threads, TikTok). They are listed in [Measurements](#measurements-log). Web layouts can differ from the native apps, and UIs run experiments, so treat them as dated snapshots.
- **Pages that only render with JavaScript** (Snapchat Business Help, Meta Business Help, X Help and X Ads specs, TikTok Ads help) were read in the browser. So were two images whose numbers matter: the Snapchat safe-zone diagram, and Google's YouTube vertical overlay PNG, which was checked pixel by pixel.
- **Search budget.** Parallel research threads exhausted the session's WebSearch cap (200) partway through. Later discovery used direct fetches and a browser search page. Everything still open is listed under [Could not verify](#could-not-verify).
- **Confidence labels.**
  - official: the platform says it.
  - widely-cited: several reputable third parties agree and no official page exists.
  - practice: a common designer convention or a single source.
  - estimate: derived by us, with the maths shown.
- **Pixel conventions.** Safe boxes are `[top, right, bottom, left]` in px at the preset's own size. Keep-outs are `[x0, y0, x1, y1]`. For circles, the safe box is the circle's bounding square inset by 10 %, as the brief asks. That box pokes slightly outside the circle at its corners, so keep marks round or centred.
- **Text floors in `social.json`** use the skill's own rule from `design.py` `apply_spec`: 11 CSS px (`min_text_px`) and 24 CSS px (`large_text_px`) at `view_width_px`. The formula is `round(11 x w / view)`. Where the viewing width is unknown, all three fields are `null`.

## Counts

- **New formats in `social.json`: 59.** None repeats an id in `existing-ids.txt`. By platform:
  - LinkedIn 12
  - Pinterest 9
  - Meta ads 8 (3 Meta-wide, 3 Facebook, 2 Threads)
  - Snapchat 6
  - YouTube 5
  - TikTok 5
  - X 4
  - Bluesky 3
  - Mastodon 3
  - organic Instagram, Facebook and Threads profile formats 4
- **Confidence of the new formats:** 46 official, 7 widely-cited, 5 practice, 1 estimate. Some fields inside an official entry, such as a viewing width, are estimates; each entry's `notes` says which.
- **Corrections: 39 existing presets checked.**
  - 21 need a change: 11 value changes, 8 wrong or outdated notes or confidence labels, and 2 unverified heuristics with suggested replacements.
  - 12 are right but need a note.
  - 6 are confirmed as they are.
  - [Details](#corrections-to-existing-presets).
- **Discontinued or changed formats: 39 entries**, plus 2 formats confirmed as still live (Facebook right column, TikTok Stories). [Details](#discontinued-or-changed-formats).

---

## Instagram

**Sources**
- [IG1] Image resolution: https://www.facebook.com/help/instagram/1631821640426723 (undated). Feed photos 1.91:1 to 3:4. Widths from 320 to 1080 px are kept; narrower photos are enlarged, wider ones reduced.
- [IG2] Carousels: https://www.facebook.com/help/instagram/269314186824048. Up to 20 items, one orientation for all, and the first item shows in the grid.
- [IG3] Hashtags: https://www.facebook.com/help/instagram/351460621611097. Up to 5 tags per post; the post fails with more.
- [IG4] Reels: https://www.facebook.com/help/instagram/1038071743007909. 1.91:1 to 9:16; the cover is listed as 420x654 px.
- [IG5] Highlights: https://www.facebook.com/help/instagram/813938898787367 (no sizes given).
- [IG6] Tall grid tiles, January 2025: https://www.socialmediatoday.com/news/instagram-rolls-out-vertically-aligned-profile-grid/737777/
- [IG7] "Adjust preview" grid crop, about 2026-03-01: https://www.socialmediatoday.com/news/instagram-introduces-thumbnail-post-editing-for-grids/813444/
- [IG8] Hashtag cap news, 2025-12-18: https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/
- [IG9] Originality, 2026-04-30: https://creators.instagram.com/blog/rewarding-original-creators-on-instagram/. Re-uploads that only add a border, watermark, subtitles or credit are not recommended.
- [IG10] Graph API media, updated 2025-07-09: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media. The API still says 4:5 to 1.91:1, 10 carousel items and 30 hashtags; captions 2,200 characters.
- [IG11] Grid rearranging, 2026-06-08: https://www.socialmediatoday.com/news/instagram-releases-profile-grid-rearranging/822304/
- [M-IG] Measured on instagram.com, 2026-09-24:
  - Grid tiles are exactly 3:4 and centre-cropped: 310.7x414.2 on desktop at a 1280 px viewport; 124x165.3 on phone web at 375 px.
  - Profile picture: 150 px (desktop), 96 px (phone web).
  - Highlights: 77 px, stored as 150 px squares.

**Feed post** (ig-3x4, ig-portrait, ig-square, ig-landscape)
- **Anatomy.** One idea, one focal image, a headline, and at most a short support line. The logo sits in a consistent corner inside the safe box.
- **Copy budget (practice).**
  - Headline up to 8 words.
  - Total on the image up to 25 words.
  - The caption carries the rest (2,200 characters, [IG10]).
- **Which size.**
  - 1080x1440 (3:4) when the post is Instagram only. It fills the most feed height and the grid shows it whole [IG1][M-IG].
  - 1080x1350 when the same file goes to Facebook, LinkedIn or Threads.
- **Grid crop.** Tiles are a centred 3:4 crop [M-IG]. Owners can drag the crop per post with "Adjust preview" since about March 2026 [IG7], but design for the default.
  - 4:5 loses 33.75 px each side.
  - 1:1 keeps x 135 to 945.
  - 1.91:1 keeps only x 328 to 752 (39 % of the width).
- **Text size.** A tile is about 124 to 129 CSS px wide on a phone, so grid-legible words need a cap height of about 90 px or more (estimate: 11 CSS px x 1080 / 129).
- **Mistakes.**
  - A headline in the outer 135 px of a square.
  - Body text under about 30 px (below 11 CSS px on a 390 px phone).
  - A 1.91:1 image carrying text.
- **Rejects or penalises.**
  - More than 5 hashtags fails to post [IG3].
  - Reposts that only add a border or watermark lose recommendation reach [IG9].
  - Publishing through the API caps you at 4:5 and 10 slides [IG10].

**Carousel** (ig-carousel, ig-carousel-3x4)
- **Rules.** Up to 20 items; one orientation for every slide; the first slide is the grid tile [IG2].
- **Mixed ratios.** Kapwing and Buffer describe a late-2024 "Mixed" option that pads each slide. The official help says one orientation, so design all slides at one ratio.
- **Anatomy.** Hook slide (up to 8 words, surviving the grid crop), body slides with one idea each, and a final CTA slide.

**Story** (ig-story, organic)
- **UI.** The top holds the progress bars, avatar, name and close button. The bottom holds the reply bar and send button.
- **Safe zone.** Instagram publishes no organic safe zone. Meta's ad zone (14 % top, 35 % bottom, 6 % sides) is the official number for ads [MA1] and the safe superset.
- **Copy.** Up to about 20 words per frame. Leave a clear block for stickers, which are added in the app.

**Story Highlight cover** (new: ig-highlight-cover)
- **Canvas.** Make it as a 1080x1920 story frame. The editor crops a circle you can pan and zoom [IG5]. By default we assume the circle spans the width at the centre (estimate), so only y 420 to 1500 matters.
- **Display.** 77 px on desktop web [M-IG]. The highlight name is live text under the circle, so do not repeat it.
- **Copy.** None. Use one bold glyph with thick strokes, one palette across the set.

**Reel cover** (ig-reel-cover)
- **Cover.** The 9:16 cover shows full size in the Reels tab and viewer. The grid shows its centre 1080x1440 (y 240 to 1680) unless the owner adjusts it [IG7][M-IG].
- **Legacy spec.** The official help still lists a 420x654 cover [IG4]. That is 1:1.55, which equals y 119 to 1801 at full width.
- **Copy.** Title in 2 to 6 words, kept between y 285 and 1635.
- **Text inside the video.** Use Meta's 14/35/6 zone. Captions, audio and the right action rail sit there.

**Profile picture** (new: ig-profile)
- **Size.** 320x320, circle (widely cited). Shown at 150 px on desktop and 96 px on phone web [M-IG]. No text; a monogram at most.

**Notes and Instants**
- Nothing to design. Notes are up to 60 characters of text plus optional music (Hootsuite, 2026-04-06, https://blog.hootsuite.com/instagram-notes/). Instants are camera-only.

**Ads.** See Meta ads.

---

## Facebook

**Sources**
- [FB1] Page profile picture and cover: https://www.facebook.com/help/125379114252045 (undated, read in the browser 2026-09-24).
  - Profile picture: 176 px on computers, 196 on smartphones, 36 on feature phones; circle; 320x320 best.
  - Cover: "left aligns with a full bleed" at 16:9 on computers and 2.4:1 on mobile. At least 400x150. Loads fastest at 851x315 under 100 KB. The picture overlaps the cover by about 40 px on mobile. Use PNG for logos or text.
- [FB2] Group cover: https://www.facebook.com/help/212144952271305. 1,640x856 (1.91:1); keep important information out of the grey areas that mobile may not show.
- [FB3] Personal cover: https://www.facebook.com/help/220070894714080. At least 720 px wide.
- [FB4] Event cover: https://www.facebook.com/help/1910675759253872. No size given; the cover size cannot be edited after adding.
- [FB5] Link-share images: https://developers.facebook.com/docs/sharing/webmasters/images/. At least 1200x630; 600x315 minimum for the large layout; 200x200 absolute minimum; 8 MB; stay near 1.91:1.
- [FB6] Page Stories API: https://developers.facebook.com/docs/page-stories-api/. Stories 1080x1920; photos up to 10 MB.
- [FB7] Reels Publishing API: https://developers.facebook.com/docs/video-api/guides/reels-publishing. 9:16, 1080x1920, minimum 540x960.
- [M-FB] Measured on facebook.com/facebook, 2026-09-24:
  - Desktop, 1440 viewport: cover 940.5x348 (2.70:1), served as a 1945x720 crop. Profile picture 152 px at x 44 to 196 from the cover's left edge, overlapping the cover's bottom by 49 px.
  - Phone web, 390 viewport: cover 375x132 (2.84:1). Profile picture ring 122 px at x 12, overlapping by 33 px.

**Page cover** (fb-cover, 1702x630)
- **What renders.** The official text (16:9 / 2.4:1) does not match what renders: 2.70:1 on desktop and 2.84:1 on phone web [M-FB]. Design dual-safe:
  - Keep text within x 40 to 1512, which also survives a left-aligned 2.4:1 crop that cuts the right 190 px.
  - Keep the bottom-left clear for the picture.
    - Desktop avatar, in cover px: [80, 541, 355, 630].
    - Phone web avatar: [54, 465, 608, 630].
    - Official 40 px mobile overlap: starts at y 462 at a 360 px view.
- **Copy.** Up to 8 words: value line plus one proof point.
- **File.** PNG for text or logos [FB1].
- **Mistakes.** Headline bottom-left; contact details at the right edge.

**Profile picture** (new: fb-profile). 320x320, circle, PNG for logos [FB1]. On phone web it is about 104 px inside its rings [M-FB].

**Event cover** (fb-event-cover)
- 1920x1005 is the widely cited size (Sprout, 2026-05-11). Facebook's help gives no size [FB4].
- Keep the title inside the central area and put date and venue in the event fields, not only on the image.

**Group cover** (fb-group-cover). Official 1640x856 [FB2]. Mobile shows less than the whole image, so keep text in the middle band.

**Personal profile cover.** At least 720 px wide [FB3]. Assumed to share the Page layout, so reuse fb-cover (practice).

**Stories and Reels.** Same canvas and UI as Instagram [FB6][FB7]. Use ig-story or vertical-safe, and ig-reel-cover for covers.

**Link images.** 1200x630 [FB5]. This is the existing og-image preset. The title and domain print as live text below the image.

**Messenger.** No organic image format to design. Messenger ad placements are gone or going (see Discontinued).

---

## Meta ads (Facebook, Instagram, Threads, Messenger, WhatsApp Status)

**Sources**
- [MA1] Business Help, "About text overlays and the safe zone for ads in Stories and Reels": https://www.facebook.com/business/help/980593475366490 (read in the browser 2026-09-24).
  - For 9:16 ads in Stories, Reels, Feed and Facebook in-stream reels, keep the top, bottom and side edges clear.
  - For Instagram Feed ads at 1:1 or 4:5, keep the bottom and side edges clear.
  - Taller-than-9:16 screens may zoom the creative, cropping outside the zone, or letterbox it on black.
  - With a disclaimer on Reels ads, leave the bottom 40 % clear.
  - Ads that were labelled "Sponsored" now show "Ad".
- [MA2] Aspect ratios by placement: https://www.facebook.com/business/help/682655495435254 (table read in the browser).
- [MA3] Recommended minimum pixels by placement: https://www.facebook.com/business/help/469767027114079.
  - Facebook Feed 1080x1080 (1:1) or 1440x1800 (4:5).
  - Right column and Marketplace 1200x1200.
  - Stories and Reels 1080x1080.
  - Messenger inbox 1200x1200.
  - WhatsApp Status 500x320.
- [MA4] Ads Guide, Facebook Feed image: https://www.facebook.com/business/ads-guide/update/image/facebook-feed. 4:5, 1440x1800, primary text 50 to 150, headline 27, 30 MB, minimum 600x750, 3 % tolerance.
- [MA5] Ads Guide, Instagram Feed image: https://www.facebook.com/business/ads-guide/update/image/instagram-feed. 4:5, 1440x1800, 1.91:1 to 4:5 accepted, primary 125, headline 40, 500 px minimum width, 1 % tolerance.
- [MA6] Ads Guide, Instagram Reels: https://www.facebook.com/business/ads-guide/update/video/instagram-reels. 1440x2560; leave at least 14 % top, 35 % bottom and 6 % each side free; primary text 44.
- [MA7] Instagram Stories image: https://www.facebook.com/business/ads-guide/update/image/instagram-story
- [MA18] Facebook Reels image: https://www.facebook.com/business/ads-guide/update/image/facebook-facebook-reels. Primary 40, headline 55.
- [MA8] Facebook Feed carousel: https://www.facebook.com/business/ads-guide/update/carousel/facebook-feed. 1:1, 2 to 10 cards; primary 80, headline 20, description 18.
- [MA9] Instagram Feed carousel: https://www.facebook.com/business/ads-guide/update/carousel/instagram-feed. 4:5 when all cards are images; 1:1 if any card is a video.
- [MA10] Right column: https://www.facebook.com/business/ads-guide/update/image/facebook-right-hand-column. 1:1, at least 1080x1080, minimum 254x133, headline 40, desktop only.
- [MA11] Marketplace: https://www.facebook.com/business/ads-guide/update/image/facebook-marketplace
- [MA12] Ads on Facebook Reels (overlay): https://www.facebook.com/business/ads-guide/update/image/facebook-facebook-reels-overlay
- [MA13] Business Help, Ads on Threads: https://www.facebook.com/business/help/655859553779869 (read in the browser).
  - Images 1.91:1 to 9:16; taller than 4:5 is cropped and centred to 4:5.
  - 1440x1440 recommended.
  - Primary text 80 to 160, headline 40; no CTA button renders.
  - Carousel cards outside 4:5 are centre-cropped to 4:5; 2 to 10 cards.
  - From September 2026 a Threads-only profile can run ads.
- [MA19] Marketing API, Threads ads: https://developers.facebook.com/docs/marketing-api/ad-creative/threads-ads/creation/. Carousel cards centre-cropped to 1:1, which conflicts with [MA13].
- [MA14] Out-of-cycle changes 2025: https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2025. Messenger inbox placement removed, effective 2025-11-11.
- [MA15] Graph API v26.0 changelog (2026-07-29): https://developers.facebook.com/docs/graph-api/changelog/version26.0. Messenger Stories and the Instagram Explore (feed) placement removed; poll components removed, for all versions by 2026-10-27; WhatsApp Status carousels up to 10 cards.
- [MA16] Graph API v24.0 changelog (2025-10-08): https://developers.facebook.com/docs/graph-api/changelog/version24.0. Facebook video feeds delivery stopped.
- [MA17] Advertising Standards: https://transparency.meta.com/policies/ad-standards/

**Which master for which placement** [MA2][MA4][MA5][MA6][MA13]

| Master | Placements | Preset |
|---|---|---|
| 4:5, 1440x1800 | Facebook and Instagram Feed, Instagram Explore home, Instagram search | meta-ad-feed |
| 9:16, 1440x2560 | Stories and Reels on both apps, Messenger Stories (deprecated), WhatsApp Status | meta-ad-story |
| 9:16 with a disclaimer | Reels | new: meta-ad-reels-disclaimer |
| 1:1, 1440x1440 | Facebook and Instagram Feed (1:1 option), Facebook search, collection cover | new: meta-ad-square |
| 1:1, 1200x1200 | Marketplace grid (1:1 recommended there) | new: meta-ad-marketplace |
| 1:1, 1200x1200 (or 1.91:1) | Facebook right column, desktop only | new: meta-ad-right-column |
| 1:1, 1080x1080 | Carousel cards | new: meta-ad-carousel |
| 1:1, 1080x1080, exact | Ads on Facebook Reels (overlay banner or sticker) | new: meta-ad-reels-overlay |
| 1:1, 1440x1440 | Threads feed | new: threads-ad, threads-ad-carousel |

**Playbook**
- **Anatomy.**
  - Feed: product or person, a 3 to 7 word headline on the image (optional), brand mark.
  - The headline and CTA fields print below the image in feeds, so do not repeat them or draw a fake button.
- **9:16.** Only about half the height is safe (x 86 to 1354, y 358 to 1664 at 1440x2560). Put the hook in the upper part of that box.
- **Copy budgets.** These are Meta's truncation recommendations, not hard caps:
  - Facebook Feed: primary 50 to 150, headline 27 [MA4].
  - Instagram Feed: primary 125, headline 40 [MA5].
  - Instagram Reels: primary 44 [MA6].
  - Facebook Reels: primary 40, headline 55 [MA18].
  - Threads: primary 80 to 160, headline 40 [MA13].
- **Mistakes.**
  - Text in the bottom 35 % of 9:16.
  - Letting Advantage+ centre-crop a 4:5 ad into 1:1 placements. Supply a square per placement instead.
  - Relying on carousel order: Meta may reorder cards unless you switch that off.
  - Putting text on the right column or Reels overlay images, which Meta advises against.
- **Rejects or penalises.**
  - Wrong ratio beyond tolerance (1 % on Instagram, 3 % on Facebook).
  - Files over 30 MB.
  - Anything against the Advertising Standards [MA17].
  - The old 20 % text rule is gone. It was retired in September 2020 (Search Engine Journal, https://www.searchenginejournal.com/facebook-removes-the-20-text-limit-on-ad-images/381844/), and heavy text is now only a performance risk.
- **WhatsApp Status ads.** Accept 1.91:1 to 9:16, with 9:16 recommended [MA2]. Meta's minimum-pixel help says 500x320 [MA3], which looks like a stale landscape value. No Status-specific safe zone was found; use meta-ad-story.

---

## Threads

**Sources**
- [TH1] Threads API overview: https://developers.facebook.com/docs/threads/overview.
  - JPEG or PNG, 8 MB, sRGB.
  - Width 320 to 1440; images outside that range are rescaled.
  - Aspect ratio up to 10:1.
  - Carousels 2 to 20; text 500 characters.
- [M-TH] Measured on threads.com phone web at 375 px, 2026-09-24:
  - Single images are 303 px wide, inset by a 60 px avatar gutter and 12 px right padding. That makes 318 px at 390.
  - Carousels scroll sideways at a fixed height of 184 px.
  - Avatars: 64 px on the profile, 36 px beside posts; served at 320x320.

**Playbook**
- **Size.** 1080x1350 (threads-post) reads well. The feed column is narrower than Instagram's (318 px vs 390 on a 390 px phone), so raise body text to about 37 px at 1080 wide.
- **Carousels.** They show as a sideways strip of short tiles: put the hook on card 1 at large size.
- **Other.** No banner. Profile picture is new: threads-profile. Ads: threads-ad.

## WhatsApp Status

- **Organic.** No official pixel spec for Status or Channels exists. The 5 MB in wa-status is the Cloud API limit for image messages [WA1: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media], not a Status rule.
- **Ads.** Status ads are a Meta placement, 9:16 recommended [MA2]. The v26.0 changelog adds Status carousels [MA15].
- **Design.** Use the 9:16 zone of wa-status and meta-ad-story.

---

## Pinterest

**Sources**
- [PI1] Ad specs: https://help.pinterest.com/en/business/article/pinterest-product-specs (read in the browser 2026-09-24).
  - Standard: 2:3 or 1000x1500 recommended; Pins taller than 2:3 "might get cut off in people's feeds"; 20 MB on desktop, 32 MB in-app.
  - Title 100 characters, of which the first 40 may show.
  - Idea ads at 1080x1920: safe zones top 270, left 65, right 195, bottom 440.
  - Showcase: safe zone 342x430; the bottom 80 px of the card is covered; text overlay up to 10 words.
  - Video: shorter than 1:2 and taller than 1.91:1.
- [PI2] Review Pin specs (organic): https://help.pinterest.com/en/article/review-pin-specs (read in the browser). Organic 9:16 safe zones: top 270, left 65, right 195, **bottom 790**. Web images up to 20 MB. Descriptions do not show in the home or search feed.
- [PI3] Edit a board: https://help.pinterest.com/en/article/edit-a-board.
  - The board cover is the largest image on your profile's board tile, picked from the board's Pins.
  - The header image is a separate featured image, set on Android or iOS only.
- [PI4] Personalize your profile: https://help.pinterest.com/en/business/article/personalize-your-profile. Profile cover at least 800x450, 16:9 recommended.
- [PI5] Carousels: https://help.pinterest.com/en/business/article/create-a-carousel. 2 to 5 images, 1:1 or 2:3.
- [PI6] Collections ads: https://help.pinterest.com/en/business/article/collections-ads-on-pinterest. One main image over three smaller ones; up to 24 secondaries; one ratio for all.
- [PI7] Advertising guidelines: https://policy.pinterest.com/en/advertising-guidelines. They are being updated, effective 2026-11-12.
- [PI8] Gestalt Masonry: https://gestalt.pinterest.systems/web/masonry. Default column width 236 px.
- [PI9] Long-pin guides:
  - postfa.st (2026-06): https://postfa.st/sizes/pinterest/pin
  - Recurpost (2026-09): https://recurpost.com/blog/pinterest-pin-dimensions/
- [M-PI] Measured on pinterest.com, logged out, 2026-09-24:
  - Profile cover 640x360 (16:9), beside the avatar, not under it.
  - Avatar 120 px, served at 280x280.
  - Board tiles: main image 176x175 (1:1) plus two 87 px squares.
  - Board page header 540x360 (3:2, centre crop).
  - Pins on a board page: 267 px wide at a 1440 viewport.

**Standard Pin** (pin-standard, 1000x1500)
- **Anatomy.** Image that shows the result, a 3 to 8 word title overlay, and a small logo. The title field (first 40 characters) prints under the Pin [PI1].
- **Phone column.** On phones the Pin shows about 183 px wide (estimate, two columns), so body text under about 60 px on the canvas is unreadable.
- **White backgrounds.** A 4 % black tint is laid over pure white in light mode [PI1], so pure white edges read grey.
- **Rejects or penalises** [PI7]:
  - Blurry images (try at least 600x900).
  - Buttons or UI that mimic Pinterest features.
  - More than 4 frames or 2 font styles.
  - Excessive capitalisation.
  - Flashing effects.

**Long Pin** (new: pin-long). Official: taller than 2:3 may be cut [PI1]. Guides put the hard limit at 1:2.1 and say the bottom is hidden [PI9]. Keep the hook and brand inside the top 1000x1500.

**Square Pin** (new: pin-square). Never cut in the feed, but it takes a third less height.

**9:16 Pins**
- **Organic** (pin-9x16): official bottom 790 [PI2].
- **Idea ads** (new: pin-ad-idea): official bottom 440 [PI1].
- The wide right margin (195) clears the action rail.

**Board cover** (new: pin-board-cover). Not an upload: save a Pin to the board and pick it [PI3]. The profile tile shows a centred square [M-PI]. If the same Pin is the header image, only the centred 3:2 band shows.

**Profile cover** (new: pin-profile-cover) and **profile picture** (new: pin-profile) [PI4][M-PI].

**Ads**
- **Carousel** (new: pin-ad-carousel): 2 to 5 cards, one ratio [PI5].
- **Collections:** hero (new: pin-ad-collection-hero) and secondaries (new: pin-ad-collection-item, about 58 px on screen, no text) [PI6].
- **Showcase and Quiz ads** exist in some markets only. Showcase keeps the bottom 80 of 513 display px clear (about 16 %, so about 243 px on a 1000x1500 card, estimate) [PI1]. They are not added as presets.
- **Shopping ads** follow standard Pin specs [PI1].

---

## YouTube

**Sources**
- [YT1] Custom thumbnails: https://support.google.com/youtube/answer/72431.
  - 3840x2160 recommended for videos, 2160x3840 for Shorts.
  - Minimum 640 px wide (videos) or 640 px tall (Shorts).
  - JPG or PNG; 2 MB from a phone (10 MB for podcasts), 50 MB from a computer.
  - Account must be verified; Shorts custom thumbnails only in Studio on a computer.
- [YT2] Channel branding: https://support.google.com/youtube/answer/10456525.
  - Banner 2560x1440 recommended, 2048x1152 minimum, safe area 1235x338 at the minimum, 6 MB.
  - Profile picture renders at 98x98; JPG, GIF, BMP or PNG, no animation; 15 MB.
  - Watermark square, at least 150x150, under 1 MB; last 15 s, custom start or entire video.
- [YT3] Posts: https://support.google.com/youtube/answer/7124474. Up to 10 images; 1:1 suggested because the feed shows 1:1; 16 MB; JPG, PNG, GIF or WEBP.
- [YT4] Learn about posts: https://support.google.com/youtube/answer/9409631. Image posts can also appear in the Shorts feed.
- [YT5] End screens: https://support.google.com/youtube/answer/6388789. Video at least 25 s; last 5 to 20 s; up to 4 elements; custom images at least 300x300.
- [YT6] Create a podcast: https://support.google.com/youtube/answer/12751636. Podcast playlists need 1:1; 1280x1280 recommended.
- [YT7] Playlist thumbnail: https://support.google.com/youtube/answer/15400119. Custom images allowed; no size given.
- [YT8] Thumbnail policy: https://support.google.com/youtube/answer/9229980. No sexual, violent, gory, vulgar or misleading thumbnails.
- [YT9] Test and compare: https://support.google.com/youtube/answer/13861714. Up to 3 variants. If any is under 1280x720, all are downscaled to 854x480. Not for Shorts.
- [YT10] YouTube Blog, 2025-10-29 (thumbnail limit 2 MB to 50 MB, 4K): https://blog.youtube/news-and-events/new-features-to-help-creators/
- [YT11] YouTube Blog, 2026-07-24 (custom Shorts thumbnails for Partner Program creators): https://blog.youtube/news-and-events/youtube-studio-custom-thumbnail-updates/
- [YT12] YouTube Blog, 2024-10-15 (custom playlist thumbnails): https://blog.youtube/news-and-events/youtube-features-and-updates-2024/
- [YT13] Google Ads video specs: https://support.google.com/google-ads/answer/13547298. It links the official vertical overlay https://services.google.com/fh/files/misc/youtubesafezoneoverlay_vertical_final.png ("YouTube | Vertical Video Ads, Safe Zone Overlay", 1080x1920). The clear window measured pixel by pixel is x 48 to 888, y 288 to 1248.
- [YT14] Google Business, Shorts ads: https://business.google.com/us/ad-solutions/youtube-ads/shorts-ads/. Avoid the top 10 %, bottom 25 % and right 10 %.
- [YT15] TechCrunch, 2023-05-25 (Stories shut down on 26 June 2023): https://techcrunch.com/2023/05/25/youtube-stories-are-shutting-down-june-26-as-company-focuses-on-shorts/
- [M-YT] Measured on youtube.com and m.youtube.com, 2026-09-24:
  - **Banner.** Shows as a 6.2:1 rounded strip: 1070x172 at a 1440 viewport, 856x138 at 1024, 343x55 at 375.
    - The served file is cropped to the full width and y 35.3 % to 64.7 % of the height (the `fcrop64` parameter), which is 2560 x about 423 at y 508 to 932.
    - The avatar sits below the banner, not on it: 160 px on desktop, 72 px on phone web.
  - **Shorts.** Shelves and the channel Shorts tab render 2:3 tiles (CSS class `AspectRatio2By3`) with a centred cover crop: 172x258 on the channel tab and 217.6x326.4 in desktop search.

**Video thumbnail** (yt-thumbnail)
- **Anatomy.** Subject with a readable emotion or result, up to 4 words that add to the title, and one contrasting background.
- **Keep clear.** Bottom-right for the duration, LIVE or Premiere badge.
- **Size.** Design at 1280x720 and export 3840x2160 for desktop upload (up to 50 MB). Keep a 1920x1080 JPEG under 2 MB for phone upload [YT1].
- **Rejects or penalises.** Policy strikes for sexual, violent, vulgar or misleading thumbnails [YT8]. Repeat offences can remove custom thumbnail rights for 30 days [YT1]. Test-and-compare winners are judged by watch time [YT9].

**Shorts cover** (yt-shorts-thumb)
- **Upload.** Partner Program creators can upload a custom 9:16 cover in Studio on a computer since 2026-07-24 [YT11][YT1]. Everyone else picks a frame.
- **Where it shows.** Shelves, search and the channel tab show a centred 2:3 crop on web (y 150 to 1770 at 1080x1920) [M-YT]. The Shorts player plays the video instead of the cover.
- **Copy.** Put the face and 2 to 5 words in the middle band. One report quotes a YouTube staffer calling the usable area "closer to 3:2" (ppc.land, 2026-07-25, https://ppc.land/youtube-ends-2-year-wait-for-shorts-thumbnails-but-blocks-a-b-testing/). If that means landscape, the core band is y 600 to 1320. Keep the hook there for TV.

**Shorts video frame** (new: yt-shorts-frame)
- **Organic text.** Keep it inside Google's Shorts ads zone: top 10 %, bottom 25 %, right 10 % [YT14], plus the 48 px left margin from Google's overlay [YT13].
- **Ads.** Use the overlay window [288, 192, 672, 48].
- **Stories.** A request for a "YouTube story" maps here, or to yt-post. Stories ended 2023-06-26 [YT15].

**Channel banner** (yt-banner). Text and logo only in the centre 1546x423 [YT2]. Desktop and phone web now show the full-width 2560x423 band [M-YT]; TV shows the whole image. Put the upload schedule on it (YouTube's own tip, https://support.google.com/youtube/answer/12950272).

**Profile picture** (new: yt-profile). 800x800, circle, no wordmark [YT2][M-YT].

**Watermark** (new: yt-watermark). Square, at least 150x150, under 1 MB [YT2]. One-colour mark on transparency.

**Posts** (yt-post). 1:1, up to 10 images [YT3]. Posts can surface in the Shorts feed [YT4].

**Podcast and playlist art**
- New: yt-podcast-thumb, 1280x1280 [YT6].
- New: yt-playlist-thumb, 1280x720 as practice; no official size [YT7][YT12].
- podcast-cover (3000x3000) stays the Apple and Spotify master. Apple wants no transparency (https://podcasters.apple.com/support/5514-show-cover-template).

**End screen** (yt-endscreen). Last 5 to 20 s, up to 4 elements, video at least 25 s. Not shown on mobile web (except iPad), YouTube Music, Kids, 360 video or made-for-kids videos [YT5]. Leave element zones empty; never bake fake buttons.

---

## TikTok

**Sources**
- [TT1] TikTok Auction In-Feed Ads, last updated June 2026: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads (read in the browser 2026-09-24).
  - Sizes: 9:16 at least 540x960, 16:9 at least 960x540, 1:1 at least 640x640; up to 500 MB and 10 minutes.
  - The safe zone depends on the dimension, the caption length and any add-ons. It is published only as downloadable files (about 3.9 MB each: standard, Arabic, and with anchors).
  - Ad profile image 98x98, under 50 KB, key element in the centre 66x66.
  - Account name 20 characters (10 in CJK); Spark captions show at most 4 lines; non-Spark captions cannot carry links, @ or hashtags.
- [TT2] Carousel ads specs, September 2026: https://ads.tiktok.com/help/article/specifications-for-carousel-ads. Vertical 720x1280 recommended, square 640x640, horizontal 1200x628; 2 to 35 images; JPG or PNG; 100 KB or less suggested; music required.
- [TT3] Carousel playbook (PDF): https://ads.tiktok.com/business/library/Image_Ads_Carousel_Ads_Playbook.pdf. Other ratios may show black bars; 3 or 7 to 9 images recommended.
- [TT4] Content Posting API media transfer, 2026-08-04: https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide. Photos JPEG or WebP, up to 20 MB, maximum 1080p.
- [TT5] Photo post API, 2026-08-24: https://developers.tiktok.com/doc/content-posting-api-reference-photo-post. Up to 35 photos; title 90, description 4,000.
- [TT6] Profile photo: https://www.tiktok.com/support/faq_detail?id=7581821549855038008. At least 20x20; a profile video replaces the photo.
- [TT7] Creative best practices, June 2025: https://ads.tiktok.com/help/article/creative-best-practices. Shoot at 720p or more; show 5 to 10 words per second of on-screen text.
- [TT8] Stories: https://www.tiktok.com/support/faq_detail?id=7605444292726905364. Still live; 24 hours; now also in For You and Following, and can be kept in Highlights.
- [TT9] CreaMate safe-zone guide, 2026-08 (third-party): https://creamate.ai/en/blog/tiktok-safe-zone-guide. Top 140, right 180, bottom 400, left 60, and it says these are not official.
- [TT10] Zeely (third-party): https://zeely.ai/blog/tiktok-safe-zones/
- Other third-party sets found (Ignite Social, PostPlanify, Recharm, AdManage, Xyla, Quso) range over:
  - top 108 to 150
  - right 100 to 180
  - bottom 270 to 484
  - left 60
- [M-TT] Measured: tiktok.com desktop profile avatar 172 px (the video grid failed to load logged out).

**Vertical video and Photo Mode** (tiktok, new: tiktok-photo)
- **UI.** Top tabs and search; right rail with avatar, like, comment, save, share and sound; bottom username, caption and sound.
- **Safe zone.** TikTok says it varies with caption length [TT1]. Use the organic box [140, 164, 370, 60] (third-party consensus).
- **Photo Mode.** Up to 35 photos [TT5]. The first slide is the cover. 9:16 fills the screen; other ratios are letterboxed (practice, per [TT3]'s warning for ads).
- **Copy.**
  - On video, 5 to 10 words per second of screen text [TT7].
  - On a still slide, about 15 words (practice).
  - The caption carries hashtags.

**Ads**
- **In-feed** (new: tiktok-ad): conservative box [140, 180, 400, 60] [TT9]; bottom 484 for 3 to 4 line captions. Official pixels are in the template files [TT1].
- **Carousel** (new: tiktok-carousel-ad): 720x1280, one ratio [TT2].
- **Ad profile image** (new: tiktok-ad-profile): 98x98, under 50 KB [TT1].

**Profile** (new: tiktok-profile). 200x200 circle (widely cited); at least 20x20 [TT6].

**Rejects or penalises**
- Ad review rejects low-quality creative; TikTok recommends at least 720p [TT7].
- Non-Spark captions with links, @ or hashtags are not allowed [TT1].
- TikTok Stories are not discontinued [TT8].

---

## LinkedIn

**Sources** ("last updated" converted to a month; checked 2026-09-24 and 25)
- [LI1] Pages and Career Pages images, about Aug 2026: https://www.linkedin.com/help/linkedin/answer/a563309.
  - Logo 400x400 (minimum 268).
  - Cover 1512x256, which may be trimmed; keep key content centred.
  - Life tab main 1128x376, modules 502x282, photos 900x600.
  - All PNG or JPEG, 3 MB.
- [LI2] Profile cover, about Mar 2026: https://www.linkedin.com/help/linkedin/answer/a568217. 1584x396, JPG or PNG, under 8 MB; replaced by the stream while the member is live.
- [LI3] Profile photo won't upload, about 2024: https://www.linkedin.com/help/linkedin/answer/a549049. 400x400 to 7680x4320, 8 MB, PNG or JPG.
- [LI4] Create an Event, about May 2026: https://www.linkedin.com/help/linkedin/answer/a554183. Cover 16:9, 480x270 or 1280x720, minimum width 480.
- [LI5] Media file types, Sep 2026: https://www.linkedin.com/help/linkedin/answer/a564109. Images up to 36 MP; no GIF profile or background photos; documents 100 MB, 300 pages, 1 million words.
- [LI6] Share photos, about 2024: https://www.linkedin.com/help/linkedin/answer/a527229. Up to 20 photos; 3:1 to 4:5; minimum 552x276.
- [LI7] Documents, about 2023: https://www.linkedin.com/help/linkedin/answer/a518909.
- [LI8] Newsletter best practices, about 2024: https://www.linkedin.com/help/linkedin/answer/a517940. Logo 300x300; cover 1920x1080.
- [LI9] Article media and covers, about 2025: https://www.linkedin.com/help/linkedin/answer/a521719. Covers 1920x1080, cropped to 16:9, no GIF.
- [LI10] Single image ads, about Jul 2026: https://www.linkedin.com/help/lms/answer/a426534.
  - Landscape 1200x628, square 1200x1200, vertical 720x900 (4:5, mobile only).
  - 5 MB.
  - Intro 150 before truncation (3,000 max); headline 70 (200 max).
- [LI11] Carousel ads, about Nov 2025: https://www.linkedin.com/help/lms/answer/a427022. 1080x1080; shown at 312x312; 2 to 10 cards; 10 MB; card headline 45.
- [LI12] Document ads, about Nov 2025: https://www.linkedin.com/help/lms/answer/a493903.
- [LI13] Message ads, about Aug 2026: https://www.linkedin.com/help/lms/answer/a425533.
- [LI14] Conversation ads, about Jul 2026: https://www.linkedin.com/help/lms/answer/a426057.
- [LI15] Sponsored Messaging banners, about Apr 2026: https://www.linkedin.com/help/linkedin/answer/a421730. 300x250, 40 KB, desktop right rail only.
- [LI16] Live encoder settings, about 2025: https://www.linkedin.com/help/linkedin/answer/a567498. 16:9, 720p recommended, 1080p maximum.
- [LI17] Group cover, about 2025: https://www.linkedin.com/help/linkedin/answer/a544662. 1776x444.
- [LI18] Dynamic Page covers, about Apr 2026: https://www.linkedin.com/help/linkedin/answer/a7433061. Premium, up to 5 rotating images; keep key details away from the edges, especially the lower-right.
- [LI19] Spotlight ads (marketing page, undated): https://business.linkedin.com/advertise/ads/dynamic-ads/spotlight-ads. Logo 100x100; background 300x250; 2 MB.
- [LI20] Ads policy, revised 2025-11-18: https://www.linkedin.com/legal/ads-policy
- [LI21] Professional Community Policies: https://www.linkedin.com/legal/professional-community-policies. The profile photo must be your likeness.

**Feed image** (li-landscape, li-square, li-portrait)
- **Size.** 4:5 is the tallest organic ratio [LI6] and the vertical ad ratio [LI10], and vertical ads are mobile only.
- **View width.** About 552 CSS px on desktop and 390 on phones.
- **Copy.** Headline up to 8 words; LinkedIn truncates intro text at about 150 characters in ads [LI10].
- **Rejects** [LI20]:
  - Using the name "LinkedIn" (except "find me on LinkedIn").
  - Poor spelling or grammar.
  - Excessive emojis, odd capitalisation or unrelated hashtags.

**Document carousel** (li-doc)
- One PDF, all pages one size, layers flattened; 100 MB, 300 pages [LI7][LI5]. It cannot be edited after posting.
- Page 1 is the feed cover. Print page numbers.
- Under 10 pages is recommended for document ads [LI12].

**Profile photo and banner**
- **Photo** (new: li-profile-photo): 800x800, circle, your own likeness only [LI3][LI21].
- **Banner** (li-profile-cover): 1584x396 [LI2]. LinkedIn publishes no overlap geometry; the photo covers the lower left. Blogs disagree on the phone crop (see corrections).

**Company Page**
- New: li-company-logo, 400x400 [LI1].
- li-company-cover, 1512x256 [LI1]: one line of text, centred, and nothing in the lower-right when dynamic covers are used [LI18].
- New: li-life-main (1128x376) and li-life-module (502x282) [LI1].

**Newsletter and article**
- New: li-newsletter-logo, 300x300 [LI8].
- New: li-article-cover, 1920x1080 cropped to 16:9 [LI9]. The title is live text, so the image needs up to 6 words.

**Event and Live**
- li-event-cover: 16:9, 1280x720 [LI4].
- LinkedIn Live runs as an Event, so its thumbnail is the event cover.
- Stream slates and lower thirds use new li-live-frame at 1280x720 [LI16].

**Ads**
- Single image: li-landscape, li-square, li-portrait [LI10].
- Carousel card (new: li-ad-carousel-card): shown at 312 px, so 3 to 8 words [LI11].
- Message and Conversation ad banner (new: li-message-banner): 300x250, 40 KB; Conversation banners are not clickable [LI15].
- Spotlight, Follower and Text ads: logo (new: li-ad-logo, 100x100) and background (new: li-spotlight-bg, 300x250) [LI19].
- Group cover (new: li-group-cover, 1776x444) [LI17].

---

## X

**Sources**
- [X1] X Help, profile photos and headers: https://help.x.com/en/managing-your-account/common-issues-when-uploading-profile-photo (read in the browser 2026-09-24; plain fetches return 403).
  - Profile 400x400, header 1500x500; JPEG, GIF or PNG; profile photos up to 2 MB.
  - "60 pixels on the top and bottom could be cropped" from headers.
  - Profile photos with nudity are removed.
- [X2] X Ads creative specs: https://business.x.com/en/help/campaign-setup/creative-ad-specifications (read in the browser).
  - Image ads: PNG or JPEG, 5 MB, no BMP or TIFF; GIFs render static.
  - Website and app cards: 800x418 (1.91:1) or 800x800 (1:1). The card headline (70 characters, 50 to avoid truncation) sits 8 to 12 px from the image's left and bottom edges.
  - Standalone image ads: 1200x1200 or 1200x628.
  - Expanded ratios: 4:5 at 1440x1800, 2:3 at 1080x1620, 1:1 at 1080x1080, 1.91:1 at 2064x1080, 16:9 at 1920x1080, 9:16 at 1080x1920.
  - Carousels: 2 to 6 slides, one ratio. Post copy 280 characters, 257 with a link.
- [X3] X API media best practices: https://docs.x.com/x-api/media/quickstart/best-practices. JPG, PNG, GIF or WEBP; images up to 5 MB; GIF up to 15 MB and 1280x1080.
- [X4] Summary card with large image, archived developer docs (Wayback snapshot 2026-01-12): https://web.archive.org/web/20260112050218/https://developer.x.com/en/docs/x-for-websites/cards/overview/summary-card-with-large-image.
  - 2:1; minimum 300x157, maximum 4096x4096; under 5 MB; JPG, PNG, WEBP or GIF (first frame only); no SVG; alt text 420 characters.
  - The live page is gone: docs.x.com returns 404.
- [X5] X Ads API cards, via https://docs.x.com/llms-full.txt: card images at most 3 MB and at least 800 px wide; website cards 1:1 or 1.91:1.
- [X6] TechCrunch, 2023-10-05: https://techcrunch.com/2023/10/05/x-cuts-headlines-from-link-previews-as-musk-wants-users-posting-directly-on-the-platform/
- [X7] Timeline of Twitter: https://en.wikipedia.org/wiki/Timeline_of_Twitter. Saliency crop removed in May 2021; headlines re-added as small text on 2024-01-02.
- [X8] Goodbye Fleets (official blog): https://blog.x.com/en_us/topics/product/2021/goodbye-fleets
- [X9] Buffer: https://buffer.com/resources/social-media-image-sizes/. Single images from 2:1 to 3:4 show in full.
- [M-X] Measured on x.com, logged out, 2026-09-24:
  - **Desktop, 1440 viewport.**
    - Header 598x200 (3:1).
    - Avatar 128 px inside a 136 px box, 16 to 152 px from the header's left, overlapping its bottom by 68 px. In canvas px that is [40, 331, 381, 500].
    - Timeline media 516 px wide.
  - **Phone web, 375 viewport.**
    - The header box is 375x200 (1.875:1) with a cover fit, so only x 281 to 1219 of a 1500 px header shows.
    - Avatar 78 px (86 px box), overlapping 43 px: [321, 392, 536, 500].
    - Media about 292 px wide, so about 308 px at 390.
    - @NASA shows a square avatar.

**In-stream images** (x-post, x-square, new: x-portrait)
- **Crop.** Single images from 2:1 to 3:4 show uncropped [X9]. X crops around the centre since it removed its saliency crop [X7].
- **Width.** Media sits right of the avatar column: about 310 px on a 390 px phone, 516 px on desktop [M-X]. Text needs to be larger than on Instagram.
- **Multi-image posts.** 2 to 4 images crop to tiles, so keep text in the centre square (practice).
- **Copy.** Up to 10 words on the image; the post (280 characters) carries the message.

**Header** (x-header)
- 1500x500, and the top and bottom 60 px may be cut [X1].
- The avatar covers the lower left: desktop [40, 331, 381, 500] [M-X].
- Logged-out phone web shows only the centre 938 px. Keep the message centred, right of x 400 and above y 330.
- Native app crop: not measured.

**Profile photo** (new: x-profile). 400x400, 2 MB [X1]. Circle; a rounded square for Verified Organizations [M-X].

**Link card** (x-card)
- 2:1 per X's own (archived) docs [X4].
- Headlines were removed in October 2023 [X6] and returned in January 2024 as small text on the image [X7]. The ad spec places it 8 to 12 px from the left and bottom [X2], so keep the bottom-left band clear.

**Ads.** New: x-ad-card (800x418) and x-ad-card-square (800x800) cover website cards, app cards and carousels [X2]. Standalone image ads reuse x-square or a 1200x628 canvas.

**Rejects or penalises**
- BMP and TIFF are refused, and GIFs go static in image ads [X2].
- Profile photos with nudity are removed [X1].

---

## Bluesky and Mastodon

**Bluesky sources** (official source code, read 2026-09-24 and 25)
- [BS1] Lexicon, embed images: https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json. Up to 4 images; up to 2 MB each, raised from 1 MB on 2026-04-08.
- [BS2] Lexicon, actor profile: https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/actor/profile.json. Avatar and banner PNG or JPEG, up to 1,000,000 bytes.
- [BS3] App constants: https://github.com/bluesky-social/social-app/blob/main/src/lib/constants.ts.
  - Posts resized to at most 4000 px and 2 MB (2026-06-04).
  - Alt text 2,000; post text 300 graphemes.
  - Link card ratio 1200/630.
- [BS4] App components: https://github.com/bluesky-social/social-app/tree/main/src.
  - Single images show up to 1:2 in feeds.
  - The banner is 150 px tall at full width with a cover fit.
  - Avatars are 90 px on the profile and 42 px in the feed.
  - The content column is the screen width minus 85 px.
- [M-BS] Measured on bsky.app, 2026-09-24:
  - Desktop: banner 600x150, 90 px avatar at 12 px from the banner's left, overlapping 44 px.
  - Phone web (375): banner 375x150, avatar 90 px at the same spot.

**Bluesky playbook**
- **Post image** (new: bsky-post): a single image shows at its own ratio unless it is taller than 1:2, which is cropped to 1:2 with a full-screen icon [BS4]. Nothing overlays it. Write real alt text; 2,000 characters are allowed.
- **Banner** (new: bsky-banner): 1500x500 (3:1).
  - The fixed 150 px height crops the top and bottom on desktop (4:1) and the sides on phones (2.5:1). Keep text in x 125 to 1375 and y 63 to 437.
  - Keep the lower-left clear for the avatar.
- **Avatar** (new: bsky-avatar): 1000x1000, circle.
- **Link card:** 1200x630, the existing og-image preset [BS3].

**Mastodon sources**
- [MD1] Profile docs, 2026-04: https://docs.joinmastodon.org/user/profile/.
  - Avatar up to 2 MB, downscaled to 400x400.
  - Header up to 2 MB, 1500x500.
  - PNG, GIF or JPG.
- [MD2] Posting docs: https://docs.joinmastodon.org/user/posting/. Up to 4 images; downscaled to 8.3 megapixels.
- [MD3] Instance API: https://docs.joinmastodon.org/methods/instance/.
  - `configuration.media_attachments.image_size_limit` is 16,777,216 bytes by default, and the matrix limit is 33,177,600 px.
  - Instances can change every limit.
- [MD4] Releases: https://github.com/mastodon/mastodon/releases.
  - 4.4.0 (2025-07-08): 8 MB avatars and headers.
  - 4.6.0 (2026-06-17): alt text up to 10,000 characters.
  - 4.7.2 (2026-09-15): HEIF disabled.
- [MD5] Pull request 26132 (2023-07-24), which removed the 16:9 crop: https://github.com/mastodon/mastodon/pull/26132
- [M-MD] Measured on mastodon.social web, 2026-09-24:
  - Desktop: header 598x160 (3.74:1). The stored file keeps its own ratio (1107x677, about 750,000 px). Avatar 80 px overlapping the header by 62 px.
  - Phone (375): header 375x120 (3.1:1).
  - Link cards: 564x295 (desktop) and 341x178.5 (phone).

**Mastodon playbook**
- **Post image** (new: mastodon-post).
  - Shows at its own ratio, capped at 566 px tall on desktop.
  - Galleries crop to 3:2 or 3:4 around the focal point the poster sets.
  - Set a focal point and alt text.
- **Header** (new: mastodon-header): 1500x500. Keep text in the centre band; each app crops differently [M-MD].
- **Avatar** (new: mastodon-avatar): 400x400. A rounded square on the web, a circle in many apps.

---

## Snapchat

**Sources**
- [SN1] Single Image or Video specs: https://businesshelp.snapchat.com/s/article/top-snap-specs (read in the browser 2026-09-24).
  - 1080x1920 canvas; image minimum 720x1280; JPG or PNG, 5 MB; an image becomes a 5-second video.
  - Brand name 32 characters, headline 34.
- [SN2] Safe Zones for Ads on Snapchat: https://businesshelp.snapchat.com/s/article/safe-zones.
  - One spec across Stories, Spotlight and Commercials, and for Single Image or Video, Story and Collection ads.
  - The diagram gives 10 % top, 35 % bottom and 6 % sides, plus a bottom-right notch 15 % wide and 45 % tall.
  - Ads Manager has a Safe Zone toggle.
- [SN3] Story Ad specs: https://businesshelp.snapchat.com/s/article/story-ad-specs.
  - Tile 360x600 PNG up to 2 MB; 175 px top buffer; 269 px bottom buffer with a CTA; text inside 300x128.
  - Logo 993x284 transparent PNG; headline 55.
  - 1 to 10 Snaps per Story ad.
- [SN4] Collection Ad specs: https://businesshelp.snapchat.com/s/article/collection-ad-specs.
  - 2, 3 or 4 square thumbnails, at least 160x160, 2 MB each, JPG or PNG.
  - Avoid the bottom 450 px of the main Snap.
  - Snap adds an AD slug top right and the CTA top left of the thumbnail row.
- [SN5] Public Profile setup: https://businesshelp.snapchat.com/s/article/public-profiles-business. Profile photo at least 320x320, PNG or JPG, 2 MB; display name 30.
- [SN6] Public Profile header: https://businesshelp.snapchat.com/s/article/public-profiles-header. Upload 375x569, visible 375x258, under 2 MB.
- [SN7] Ads API media: https://developers.snap.com/api/marketing-api/Ads-API/media. Top Snap 1080x1920, 5 MB; tile 3:5; logo 993x284; filter 1080x2340, 300 KB, at least 50 % transparent.
- [SN8] Public Profile API: https://developers.snap.com/api/marketing-api/Public-Profile-API/Profiles. Keeps a 1280 px wide original logo.
- [SN9] Public Profile API, Spotlight: https://developers.snap.com/api/marketing-api/Public-Profile-API/ProfileAssetManagement. MP4, 6 to 60 s, at least 540x960.
- [SN10] Snapchat help, Spotlight: https://help.snapchat.com/hc/en-us/articles/7012288096532. Video Snaps of 5 s or longer.
- [SN11] Recommendation quality rules: https://values.snap.com/policy/content-guidelines-recommendation-eligibility/recommendation-eligibility/quality. Demotes blurry, low-resolution, wrongly oriented, letterboxed or poorly reformatted content; favours human-made over wholly AI-generated content made outside Snapchat.
- [SN12] Ad formats: https://forbusiness.snapchat.com/advertising/ad-formats. Brand name 25 characters, which conflicts with [SN1].

**Single Image or Video ad** (snap-ad)
- **Keep clear** [SN2]:
  - Top 192 px (profile and "For You / Following" bar).
  - Bottom 672 px (brand, headline, CTA pill).
  - The right action rail from y 1056 down.
- **Copy.** Brand name and headline are live text [SN1]. Keep on-image text to about 10 words inside x 65 to 1015 and y 192 to 1248, and left of x 918 below y 1056.
- **Brand name.** Use up to 25 characters to satisfy both pages [SN1][SN12].

**Story ad tile** (new: snap-story-tile) and **logo** (new: snap-story-logo)
- Snap composes the tile from your 360x600 image, your logo on top and your headline at the bottom [SN3].
- Design the image as a photo with at most a 300x128 text block between y 175 and 331.

**Collection ad thumbnails** (new: snap-collection-thumb). Product only, no text [SN4].

**Spotlight** (new: snap-spotlight)
- Video only, so the canvas is for frames and overlays.
- No organic safe zone is published; reuse [SN2].
- Avoid letterboxing and low-resolution sources; wholly AI-generated content made outside Snapchat is ranked down [SN11]. That matters for this skill's generated plates.

**Public Profile.** Photo (new: snap-profile) [SN5][SN8]; header (new: snap-profile-header) [SN6].

**Filters.** Audience Filter ads are 1080x2340 PNG, at most 300 KB, at least 50 % transparent [SN7]. The self-serve geofilter site now redirects to Filter ads. Not added as a preset, because no safe area is published.

---

## Corrections to existing presets

Each row gives the field, the current value, the suggested value and the evidence. "Confirmed" rows need no change.

**Summary: 39 presets checked.**
- 6 are right as they are.
- 11 need a value changed: safe box, keep-out or viewing width.
- 8 need the notes or confidence label fixed, because the current text is wrong or out of date.
- 12 are right but should gain a note.
- 2 carry heuristics that can't be settled without a logged-in measurement.

Verdicts in the table:
- **Wrong:** a value is contradicted by an official source or a measurement.
- **Outdated:** the platform has since changed.
- **Add note:** the value is right but a known crop or limit is missing.
- **Unverified:** the current value is a heuristic and no better evidence was found.

| Preset | Verdict | Change (now → suggested) | Evidence |
|---|---|---|---|
| ig-portrait | Confirmed | none | [IG1], [M-IG] (grid trims 33.75 px a side; the 74 px inset covers it) |
| ig-3x4 | Add note | notes: add "the Graph API still caps at 4:5 and 10 carousel items: 3:4 needs posting in the app" | [IG1], [IG10] |
| ig-square | Confirmed | none | [M-IG] (centred 3:4 grid crop keeps x 135 to 945) |
| ig-landscape | Add note | notes: add "the 3:4 grid keeps only x 328 to 752 (39 % of the width)" | [M-IG] |
| ig-story | Outdated (minor) | safe top 250 → 270, to match Meta's 14 % top band where the progress bar and avatar sit; still practice for organic | [MA1], [MA6] |
| ig-reel-cover | Wrong (notes) | notes: "1012x1350" is not a crop. Use: "Grid shows the centre 1080x1440 (y 240 to 1680) unless the owner uses Adjust preview (about March 2026). The help lists a 420x654 (1:1.55) cover. Title inside y 285 to 1635." Safe box unchanged. | [IG4], [IG7], [M-IG] |
| ig-carousel | Add note | notes: add "the Graph API allows only 10 items; third-party 'Mixed' ratio option is not in the official help" | [IG2], [IG10] |
| ig-carousel-3x4 | Confirmed | none (app posting only) | [IG1] |
| meta-ad-feed | Wrong (notes) | notes: "primary text 125, headline 40" is Instagram only. Use: "Facebook: primary 50 to 150, headline 27, min 600x750, 3 % tolerance. Instagram: primary 125, headline 40, min width 500, 1 % tolerance. Also Explore home. Meta asks to keep bottom and side edges clear on non-9:16 Instagram Feed ads." Aliases: add "instagram explore ad". | [MA4], [MA5], [MA1] |
| meta-ad-story | Add note | notes: add "IG Reels primary 44; FB Reels primary 40, headline 55; Stories primary 125. With a Reels disclaimer use meta-ad-reels-disclaimer (bottom 40 %). Taller screens may zoom (cropping outside the zone) or letterbox. The label now reads Ad." | [MA1], [MA6], [MA18] |
| vertical-safe | Outdated | safe [269,164,672,65] → [288,192,672,65]; notes: "text only inside x 65 to 888, y 288 to 1248: covers Meta 14/35/6, YouTube's vertical ad overlay (top 288, right 192), Snapchat (top 192, right notch 162) and every TikTok right-rail figure (100 to 180)" | [YT13] (pixel-checked), [SN2], [TT9], [MA6] |
| fb-feed | Wrong (confidence) | confidence official → widely-cited (Facebook publishes no organic feed size; Sprout gives 1080x1350) | organic-spec research; [MA4] is ads only |
| fb-square | Wrong (confidence) | confidence official → widely-cited | as above |
| fb-cover | Outdated | keep-out [0,470,660,630] → [0,462,660,630]. Notes: "Official text: left-aligned 16:9 on computers, 2.4:1 on mobile. Measured 2026-09-24: 2.70:1 desktop (940x348), 2.84:1 phone web (375x132). Avatar covers [80,541,355,630] on desktop and [54,465,608,630] on phone web; official overlap about 40 px on mobile." | [FB1], [M-FB] |
| fb-event-cover | Outdated (confidence) | confidence third-party → widely-cited; notes: "Facebook's help gives no size; the cover size can't be changed after adding it" | [FB4] |
| fb-group-cover | Outdated (confidence) | confidence third-party → official; notes: "Facebook recommends 1,640x856 (1.91:1) and keeping important information out of the grey areas mobile may not show" | [FB2] |
| threads-post | Wrong (viewing width) | view_width 390 → 318; min_text 30 → 37; large_text 66 → 82 (media is inset by a 60 px avatar gutter) | [M-TH], [TH1] |
| wa-status | Wrong (notes) | notes: "5 MB is the WhatsApp Cloud API image-message limit, not a Status rule. No official Status pixel spec. Status ads exist (Meta placement, 9:16 recommended)." | [WA1], [MA2], [MA15] |
| li-landscape | Confirmed | none | [LI10] |
| li-square | Confirmed | none | [LI10] |
| li-portrait | Add note | notes: add "vertical single image ads recommend 720x900 (4:5), mobile only; 1080x1350 is within the 2430x4320 maximum" | [LI10] |
| li-doc | Add note | notes: add "cannot be edited after posting; under 10 pages recommended for document ads" | [LI7], [LI12] |
| li-profile-cover | Unverified | LinkedIn publishes no overlap geometry. Third-party guides disagree (photo zone 200 to 400 px from the left, 150 px from the bottom; phone crop 15 to 20 % a side). If adopted (estimate): keep-out [0,160,475,396], safe [40,240,150,520]. Measure logged in first. | [LI2]; blogs listed in the LinkedIn research |
| li-company-cover | Unverified | Official: the cover may be trimmed on either axis; keep key content centred. Dynamic covers: keep details away from the lower-right. Suggested (estimate): safe [30,60,30,60] → [40,280,40,280], keep-out [1260,160,1512,256]. | [LI1], [LI18] |
| li-event-cover | Confirmed | none | [LI4] |
| x-post | Wrong (viewing width) | view_width 390 → 310 (desktop media measured 516); min_text 45 → 57; large_text 98 → 124 | [M-X] |
| x-square | Wrong (viewing width) | view_width 390 → 310; min_text 30 → 38; large_text 66 → 84 | [M-X] |
| x-header | Outdated | keep-out [0,350,400,500] → [0,330,400,500] (desktop avatar box measured at [40,331,381,500]). Top and bottom 60 are now official. Confidence heuristic → official (size and crop) plus measured (avatar). Notes: add "logged-out phone web shows only x 281 to 1219; for that, safe [60,281,60,400]" | [X1], [M-X] |
| x-card | Outdated (confidence) | confidence unverified → official (archived X docs: 2:1, 300x157 minimum, 4096x4096 maximum, under 5 MB; the live page is gone). Add keep-out for the small headline label drawn on the image since January 2024 (estimate): [0,461,1200,600]. | [X4], [X7], [X2] |
| yt-thumbnail | Outdated (notes) | notes: "YouTube now recommends 3840x2160 (render --scale 3). 2 MB from a phone (10 MB for podcast thumbnails), 50 MB from a computer. Test and compare downscales to 854x480 if any variant is under 1280x720." Keep max_bytes at 2 MB as the phone-safe export. | [YT1], [YT9], [YT10] |
| yt-shorts-thumb | Wrong | safe [269,65,672,65] (a player-UI zone) → [380,60,380,60]; add keep-outs [0,0,1080,150] and [0,1770,1080,1920] (web shelves and grids show a centred 2:3 crop, measured). Notes: "Custom covers since 2026-07-24 for Partner Program creators, in Studio on a computer; 2160x3840 recommended (render --scale 2); up to 50 MB." | [YT1], [YT11], [M-YT] |
| yt-banner | Add note | notes: add "desktop and phone web now show the full-width 2560x423 band as a 6.2:1 strip with the avatar below it, not on it; TV shows the whole image" | [YT2], [M-YT] |
| yt-post | Add note | notes: add "up to 10 images; JPG, PNG, GIF or WEBP; image posts can appear in the Shorts feed" | [YT3], [YT4] |
| yt-endscreen | Add note | notes: add "video at least 25 s; last 5 to 20 s; up to 4 elements; not shown on mobile web, YouTube Music, Kids, 360 or made-for-kids" | [YT5] |
| podcast-cover | Add note | notes: "~55-180 px" is unverified. Add "YouTube recommends 1280x1280 (yt-podcast-thumb); Apple wants no transparency" | [YT6], Apple show-cover page |
| tiktok | Add note | notes: add "third-party box; TikTok's official zone varies with caption length and add-ons and ships as template files; ads: use tiktok-ad" | [TT1], [TT9] |
| pin-standard | Add note | notes: add "phones show about 183 px (two-column estimate): text under about 60 px on the canvas is unreadable there" (view_width stays 236, the Gestalt desktop column) | [PI8] |
| pin-9x16 | Wrong | safe [270,195,440,65] → [270,195,790,65] for organic Pins (official Review Pin specs); 440 applies to Idea ads only (new pin-ad-idea). Notes: "Official organic 9:16 safe zone" | [PI2], [PI1] |
| snap-ad | Wrong | safe [269,65,672,65] → [192,65,672,65]; add keep-out [918,1056,1080,1920] (right rail notch); confidence heuristic → official. Notes: "image becomes a 5 s video; minimum 720x1280; brand name 32 (Business Help) or 25 (ad formats page), headline 34" | [SN1], [SN2], [SN12] |

### Aliases to add to existing presets

The new presets in `social.json` carry their own aliases. These words, including common Banglish, should also resolve to existing ids:

| Existing id | Add aliases |
|---|---|
| fb-cover | fb cover photo, facebook cover pic, fb page er cover, fb cover banano, facebook profile cover (personal covers share the layout) |
| yt-banner | youtube channel art, yt banner, channel art, yt channel er banner, youtube cover |
| yt-thumbnail | yt thumbnail, thumbnail banao, youtube thumbnail banano, video er thumbnail, live thumbnail, premiere thumbnail, channel trailer thumbnail |
| yt-shorts-thumb | shorts cover, shorts thumbnail, shorts er thumbnail |
| ig-portrait, ig-3x4 | insta post, instagram post design, insta post er size |
| ig-story, vertical-safe | insta story, fb story, story design, story banao, whatsapp status design |
| ig-reel-cover | reels cover, reels er thumbnail, insta reels cover, fb reels cover |
| meta-ad-feed | fb ad, facebook ad post, boost post, insta ad, instagram explore ad |
| meta-ad-story | story ad, reels ad, insta story ad, whatsapp status ad |
| li-profile-cover | linkedin banner, linkedin cover photo, linkedin er cover |
| li-doc | linkedin carousel, linkedin pdf post |
| x-header | twitter header, twitter banner, x cover photo |
| og-image | facebook link preview, link share image, bluesky link card |
| pin-standard | pinterest pin, pin design, pin banao |
| snap-ad | snapchat ad, snap story ad, snapchat collection ad |
| tiktok | tiktok video, tiktok cover, tiktok er safe zone |
| wa-status | whatsapp status, wa status design, status banao |

## Discontinued or changed formats

| Format | What happened | Date | Use instead | Source |
|---|---|---|---|---|
| YouTube Stories | Shut down; stories already posted stayed up for 7 days | 2023-06-26 | yt-shorts-frame for vertical content, yt-post for an image update | [YT15] |
| YouTube "Reels" (the name) | Name used in testing before Stories rolled out | 2017 to 2018 | n/a | https://en.wikipedia.org/wiki/History_of_YouTube |
| YouTube Community tab | Now called Posts | date not confirmed | yt-post | [YT3] |
| YouTube 2 MB thumbnail cap | 50 MB from a computer, 4K thumbnails | 2025-10-29 | yt-thumbnail | [YT10] |
| YouTube Shorts covers (frame only) | Custom cover upload for Partner Program creators | 2026-07-24 | yt-shorts-thumb | [YT11] |
| YouTube playlist thumbnails (auto) | Custom images allowed | 2024-10-15 | yt-playlist-thumb | [YT12] |
| IGTV | Merged into Instagram Video; the app closed | 2021-10 and 2022-03 | ig-reel-cover | https://en.wikipedia.org/wiki/IGTV |
| Instagram square profile grid | Tall 3:4 tiles | 2025-01 | ig-3x4 | [IG6], [M-IG] |
| Instagram 4:5 as the tallest ratio | 3:4 allowed | 2025-05 | ig-3x4 | [IG1]; https://petapixel.com/2025/05/29/instagram-finally-adds-support-for-34-aspect-ratio-photos/ |
| Instagram 10-item carousel | 20 in the app (the API still allows 10) | 2024-08-08 | ig-carousel | https://www.macrumors.com/2024/08/08/instagram-20-photos-carousel-posts/, [IG10] |
| Instagram 30 hashtags | At most 5; more fails to post | 2025-12 | n/a | [IG3], [IG8] |
| Instagram fixed grid crop | Owners can adjust each post's grid preview | about 2026-03-01 | n/a | [IG7] |
| Instagram Explore (feed) ad placement | Removed; Explore home remains | 2026-07-29 (Graph API v26.0) | meta-ad-feed | [MA15] |
| Messenger inbox ads | Placement removed | 2025-11-11 | meta-ad-square, meta-ad-feed | [MA14] |
| Messenger Stories ads | Placement deprecated | 2026-07-29 (v26.0) | meta-ad-story | [MA15] |
| Facebook video feeds ad placement | Delivery stopped; Meta points to Reels | 2025-10-08 (v24.0) | meta-ad-story | [MA16] |
| Poll stickers in Meta ads | Removed | v26.0; all API versions by 2026-10-27 | design without a poll slot | [MA15] |
| Meta 20 % text rule | Retired; heavy text is now only a delivery risk | 2020-09 | n/a | https://www.searchenginejournal.com/facebook-removes-the-20-text-limit-on-ad-images/381844/ |
| "Sponsored" label on Facebook, Instagram and Threads ads | Now "Ad" | 2026 (no date on the page) | n/a | [MA1], [MA13] |
| Facebook Instant Articles | Ended (announced October 2022) | 2023-04 | n/a | https://en.wikipedia.org/wiki/Instant_Articles |
| Facebook right column | **Not** discontinued: still live on desktop | n/a | meta-ad-right-column | [MA10], [MA3] |
| Meta Spark third-party AR effects | Removed | 2025-01-14 | n/a | https://spark.meta.com/blog/meta-spark-announcement/ |
| Twitter Fleets | Ended | 2021-08-03 | x-post, x-portrait | [X8] |
| X link-card headlines | Removed, then back as small text on the image | 2023-10-05 and 2024-01-02 | x-card (keep the bottom-left clear) | [X6], [X7] |
| X automatic image cropping | Saliency crop removed; centre crops | 2021-05 | x-portrait | [X7] |
| X Cards developer docs | Removed from docs.x.com (404); archived copy only | by 2026 | x-card | [X4] |
| LinkedIn Stories | Removed | 2021-09-30 | li-portrait, li-doc | https://www.searchenginejournal.com/linkedin-removing-stories-on-september-30/418153/ |
| LinkedIn Audio Events | Discontinued; events are now Online, In person, LinkedIn Live or External link | 2023 | li-event-cover, li-live-frame | https://en.wikipedia.org/wiki/LinkedIn, [LI4] |
| LinkedIn company cover 1128x191 | Now 1512x256 (same ratio) | not dated; current by 2026-08 | li-company-cover | [LI1] |
| LinkedIn event cover 4:1 | Now 16:9 | by 2024 | li-event-cover | [LI4] |
| LinkedIn GIF article covers | No longer allowed | by 2025 | li-article-cover | [LI9] |
| LinkedIn vertical ads at 2:3 (600x900) | 4:5 (720x900) is now the main vertical size | by 2026-07 | li-portrait | [LI10] |
| Pinterest Idea Pins | Merged into standard Pins | 2023-05-11 (announced), 2023-08-25 (rolled out) | pin-9x16, pin-standard | https://techcrunch.com/2023/05/11/pinterest-is-combining-pins-and-idea-pins-into-a-single-format/, https://create.pinterest.com/blog/new-pin-format-update/ |
| Pinterest long-pin guidance | Now "taller than 2:3 might get cut off" | undated | pin-long | [PI1] |
| Snapchat self-serve geofilters | create.snapchat.com redirects to Filter ads | observed 2026-09-24 | Filter ads (1080x2340) | [SN7] |
| Snapchat Story ads | 1 to 10 Snaps per Story ad in Ads Manager (the API says 1 to 20) | current | snap-story-tile | [SN3], [SN7] |
| Bluesky post image limit | 1 MB → 2 MB (lexicon); 2000 → 4000 px (app) | 2026-04-08 and 2026-06-04 | bsky-post | [BS1], [BS3] |
| Mastodon 16:9 preview crop | Removed; single images show at their own ratio | 2023-07-24 | mastodon-post | [MD5] |
| Mastodon 2 MB avatar and header | 8 MB on 4.4+ servers (docs still say 2 MB) | 2025-07-08 | mastodon-avatar, mastodon-header | [MD4] |
| Mastodon HEIF uploads | Temporarily disabled | 2026-09-15 (4.7.2) | JPEG, PNG or WebP | [MD4] |
| TikTok Stories | **Not** discontinued: now also in For You and Following, with Highlights | n/a | tiktok-photo | [TT8] |

## Retired-format entries for the skill

`design.py` already supports a `"retired"` list (id, label, retired, notes, use). These entries let `presets --find` answer a request for a dead format with its replacement:

```json
[
 {"id": "yt-story", "label": "YouTube Story", "retired": "2023-06-26",
  "notes": "YouTube shut Stories down on 26 June 2023 to focus on Shorts and posts.",
  "use": ["yt-shorts-frame", "yt-post"], "aliases": ["youtube story", "yt story", "youtube stories"]},
 {"id": "ig-igtv-cover", "label": "IGTV cover", "retired": "2022-03",
  "notes": "IGTV merged into Instagram Video in October 2021 and the app closed in March 2022.",
  "use": ["ig-reel-cover"], "aliases": ["igtv", "igtv cover"]},
 {"id": "li-story", "label": "LinkedIn Story", "retired": "2021-09-30",
  "notes": "LinkedIn removed Stories on 30 September 2021.",
  "use": ["li-portrait", "li-doc"], "aliases": ["linkedin story"]},
 {"id": "x-fleet", "label": "Twitter Fleet", "retired": "2021-08-03",
  "notes": "Fleets ended on 3 August 2021.",
  "use": ["x-post", "x-portrait"], "aliases": ["twitter fleet", "fleets"]},
 {"id": "pin-idea", "label": "Pinterest Idea Pin", "retired": "2023-08",
  "notes": "Idea Pins merged into standard Pins in 2023; 9:16 Pins keep the old safe zone.",
  "use": ["pin-9x16", "pin-standard"], "aliases": ["idea pin", "story pin"]},
 {"id": "meta-ad-messenger-inbox", "label": "Messenger inbox ad", "retired": "2025-11-11",
  "notes": "Meta removed the Messenger inbox placement.",
  "use": ["meta-ad-square", "meta-ad-feed"], "aliases": ["messenger ad", "messenger inbox ad"]},
 {"id": "meta-ad-messenger-story", "label": "Messenger Stories ad", "retired": "2026-07-29",
  "notes": "Deprecated in Graph API v26.0.",
  "use": ["meta-ad-story"], "aliases": ["messenger story ad"]},
 {"id": "meta-ad-ig-explore", "label": "Instagram Explore (feed) ad", "retired": "2026-07-29",
  "notes": "Removed in Graph API v26.0; Explore home remains and takes the 4:5 feed ad.",
  "use": ["meta-ad-feed"], "aliases": ["instagram explore ad"]},
 {"id": "fb-video-feeds-ad", "label": "Facebook video feeds ad", "retired": "2025-10",
  "notes": "Delivery stopped with Graph API v24.0; Meta points advertisers to Reels.",
  "use": ["meta-ad-story"], "aliases": ["facebook video feed ad"]}
]
```

## Measurements log

All measurements were taken in a Chromium pane on public, logged-out web pages with `getBoundingClientRect`, `naturalWidth` and computed `object-fit` / `object-position`. Viewports were emulated at 1440, 1280, 1024, 390 and 375 CSS px. Native apps were not measured.

| Page | Viewport | What was measured |
|---|---|---|
| instagram.com/nasa | 1280 | Profile picture 150 px. Highlights 77 px (150 px files). Grid tiles 310.7x414.2 (3:4), cover fit, centred. |
| instagram.com/nasa | 375 | Profile picture 96 px. Grid tiles 124x165.3 (3:4). |
| facebook.com/facebook | 1440 | Cover 940.5x348.1 at x 250 (served 1945x720, 2.70:1). Profile picture 152 px at (294, 355), 49 px over the cover. |
| facebook.com/facebook | 390 (page laid out at 375) | Cover 375x132 (served 750x264, 2.84:1). Avatar rings 122, 112, 104 and 96 px from x 12, top at y 155, 33 px over the cover. |
| youtube.com/@YouTube | 1440 and 1024 | Banner 1070x172.5 and 856x138 (6.2:1, inset, rounded). Served 2048x339 via `fcrop64` = full width, y 35.29 % to 64.71 %. Avatar 160 px below the banner. |
| m.youtube.com/@YouTube | 375 | Banner 343x55.3; avatar 72 px below it. |
| youtube.com channel Shorts tab and search | 1440 | Shorts tiles 172x258 and 217.6x326.4 (2:3), cover fit, centred. |
| m.youtube.com search | 375 | Shorts tiles use `ytThumbnailViewModelAspectRatio2By3`. |
| pinterest.com/pinterest and a board page | 1440 | Profile cover 640x360. Avatar 120 px (280x280 file). Board tile 176x175 plus two 86.7 px tiles. Board header 540x360 (3:2, centred). Pins 267 px wide. |
| x.com/X and x.com/NASA | 1440 | Header 598x200 at (349, 53). Avatar 128 px image in a 136 px box at (365, 185). Media 516 px wide. |
| x.com/X and x.com/NASA | 375 | Header box 375x200 (image 375x125, cover fit). Avatar 77.8 px (85.8 px box) at (16, 210). @NASA avatar is square. |
| bsky.app/profile/bsky.app | 1440 | Banner 600x150 at x 420. Avatar 90 px at (432, 106). |
| bsky.app/profile/bsky.app | 375 | Banner 375x150. Avatar 90 px at (12, 106). |
| mastodon.social/@Mastodon | 1440 | Header 598x160 at (421, 62) (1107x677 file). Avatar 80 px at (436, 160). Link-card image 564x295.3. |
| mastodon.social/@Mastodon | 375 | Header 375x120 at y 51. Avatar 80 px at (15, 109). Link-card image 341x178.5. |
| threads.com/@nasa | 375 | Profile picture 64 px (320x320 file); 36 px beside posts. Single image 303x241.5 at x 60. Carousel tiles 184 px tall. |
| tiktok.com/@tiktok | 1440 | Avatar 172 px (video grid did not load logged out). |
| Snapchat safe-zone diagram (businesshelp) | n/a | Read visually: 6 % and 6 % sides, 10 % top, 35 % bottom, bottom-right notch 15 % wide by 45 % tall. |
| Google's vertical overlay PNG (1080x1920) | n/a | Alpha scan: clear window x 48 to 887 and y 288 to 1247 inclusive, so the safe box is [288, 192, 672, 48]. |

## Could not verify

- **TikTok ad safe-zone pixels.**
  - Official numbers exist only in template files on [TT1] (about 3.9 MB each).
  - Downloading them needs the user's permission, so tiktok and tiktok-ad rest on third-party figures.
  - Organic Photo Mode handling of non-9:16 photos, the carousel hard file limit and in-app avatar sizes are also open.
- **Native apps.** Every measurement is from the web. Not measured in the apps:
  - Instagram: Story UI bands, highlight size, whether Reels play 4:5 or 9:16 in the home feed.
  - Facebook: cover.
  - X: header.
  - LinkedIn: banner.
  - YouTube: Shorts shelves.
  - Pinterest: profile cover.
- **Instagram.** The highlight editor's default circle (an estimate here). Whether a carousel can mix ratios, which only third parties claim. The official date of the 3:4 grid, which is reported from a Mosseri post.
- **Facebook.**
  - Official event cover size.
  - The grey areas in the group-cover diagram (it did not render).
  - Personal cover layout.
  - On-screen sizes for the right column and Marketplace tiles.
- **Meta ads.**
  - Instagram profile feed and search specs (Ads Guide pages return 404).
  - Status of sponsored messages.
  - Instant Experience component sizes.
  - Audience Network specs.
  - The 500x320 WhatsApp Status minimum.
  - Official date of the 20 % rule's end.
  - Official width of the Reels right rail.
- **Threads.** How tall and wide images crop in the feed. Two official Meta pages disagree on carousel crops (4:5 against 1:1).
- **LinkedIn.**
  - Banner avatar overlap and phone crop.
  - Company cover display width and logo overlap.
  - Newsletter logo shape.
  - Document viewer overlays.
  - Avatar display sizes.
  - Organic video thumbnail spec.
  - Dates of the 1128x191 → 1512x256 and 4:1 → 16:9 changes.
- **X.**
  - Phone media width (estimate).
  - Multi-image tile crops.
  - Size of the headline label on link cards.
  - Native app header crop.
- **YouTube.**
  - Duration badge, progress bar and "New" badge sizes.
  - Shorts cover crop in the apps and on TV.
  - The "closer to 3:2" remark, which is secondhand.
  - Watermark formats and on-screen size.
  - End-screen element sizes.
  - Playlist thumbnail limits.
  - Podcast display sizes.
  - Studio's 4 MB profile-picture hint, which conflicts with 15 MB in the help.
- **Pinterest.**
  - Feed overlay positions: save button, menu, "Promoted by", video badge.
  - Board header size in the app.
  - Profile cover on phones.
  - Showcase and Quiz safe-zone geometry. The page gives 342x430 and 342x376 without a canvas; the bottom 80 px note suggests a 342x513 display card.
- **Snapchat.**
  - Which 258 px band of the profile header shows.
  - Profile photo shape and on-screen size.
  - Discover tile on-screen size (180 px is an estimate).
- **Mastodon and Bluesky.**
  - Mastodon phone media width.
  - How other Mastodon apps crop headers.
  - Bluesky native apps, where only the web was measured and the code read.
- **Could not be reached.** web.archive.org (plain fetch; the browser worked for one page), theverge.com, and the X and TikTok help pages via plain fetch (read in the browser or through a reader proxy instead).
