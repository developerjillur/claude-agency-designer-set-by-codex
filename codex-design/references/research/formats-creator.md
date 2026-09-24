# Creator, community, messaging, regional and publishing formats

Research date: 2026-09-24, recorded as verified 2026-09-24. New presets are in `creator.json` (71 entries). Every claim below points to a source in the list at the end as [S#].

## How to read this

- **Confidence.** `official` means the platform's own help, developer docs or source code. `widely-cited` means several third-party guides agree but the platform says nothing. `practice` means what working designers or live pages show. `estimate` means my own reading, labelled as such.
- **Measured.** Some numbers come from loading the live site in a browser at 390, 1440 or 1920 CSS px wide on 2026-09-24 and reading element boxes with JavaScript. The sources list marks these as "Measured". They can change with any redesign.
- **Text sizes.** `min_text_px` and `large_text_px` use the rule the existing presets follow: 11 and 24 CSS px at `view_width_px`. So min = round(11 × w / view) and large = round(24 × w / view).
- **Dates.** Some help centres only say "updated 6 months ago". I turned those into approximate months (for example 2026-03).
- **Not downloaded.** Apple's template ZIPs and Spotify's podcast spec PDF hold the exact safe areas. The safety rules need your permission for file downloads, so I did not fetch them. Say the word and I will pull the safe-area geometry.

---

## Playbooks by family

### Twitch

- **Anatomy.**
  - Profile banner: 1200x480, scaled to 480 px high [S1].
  - Offline screen (video player banner): 1920x1080 is the widely cited size [S5]. Static only, because Twitch does not support animated player banners [S1].
  - Info panels: 320 px wide [S1][S2].
  - Emotes: 112/56/28 [S3]. Badges: 72/36/18 [S4].
- **Where text can go.**
  - The profile banner is now background art. On desktop, a centred offline card plus a trailer carousel covers x 81 to 1114, y 91 to 389. On 1920-wide screens the file is scaled 1.4x and loses 67 px top and bottom [S6].
  - Twitch still says "concentrate the graphics on the left" [S1]. The measured layout puts the offline card exactly there, so treat that advice as outdated. Keep the channel name in the panels, the offline screen or the overlay instead.
- **Panels.**
  - The two official pages disagree. One says 2.9 MB and 320x300 maximum [S1]. The other says 1 MB and 320x600 [S2]. Stay under 1 MB and 300 px tall to satisfy both.
  - Panels never show above 320 CSS px, so a 2x file gains nothing [S1].
  - Twitch's own channel uses 320x60 title strips and 320x256 image panels [S6].
- **Overlay canvas.** Use the OBS output size, 1920x1080 for 1080p (practice). Phone viewers see a 1080p frame at about 390 CSS px, so on-stream text needs about 54 px to stay legible (derived from the text rule).
- **Emotes and badges.**
  - Emotes: PNG, or GIF for animated. Upload one square of 112 to 4096 px under 1 MB (auto-resize), or three files of 28, 56 and 112 px, each under 512 KB [S3]. Animated emotes allow at most 60 frames and no more than 3 flashes per second [S3].
  - Badges: PNG, transparent, 25 KB or less per size [S4].
- **Rejection rules.**
  - Badges must follow Twitch's guidelines: no nudity, drugs, hate, or explicit words or gestures [S4].
  - Single letters are not allowed unless they are the channel's brand [S4].
  - Emotes are reviewed against the Emote Guidelines. Instant upload is a privilege that can be revoked [S3].
- **Common mistakes.** Putting the name in the middle of the profile banner. Designing panels at 640 wide for "retina". Using animated player banners.

### Kick

- **Anatomy.** Profile banner at least 1280x700. Offline banner 1920x1080. Avatar at least 128x128. All 4 MB max, JPG or PNG [S7].
- **Crops.** The banner "is displayed at the top of your channel page when your stream is offline" [S7]. The test channel was live, so I could not measure the crop. The preset uses a 5% practice inset.
- **Copy.** Social links are entered as usernames only, not URLs [S7].

### Discord

- **Anatomy.**
  - Server banner: at least 960x540 at 16:9 (Boost Level 2). An animated GIF needs Level 3 and plays for 5 s, then again on hover [S8].
  - Invite background: exactly 1920x1080, JPG or PNG, no GIF (Level 1) [S9].
  - Profile banner (Nitro): at least 680x240, under 10 MB, PNG, JPG or GIF [S10].
  - Emoji: under 256 KB, in JPEG, PNG, GIF or WEBP [S11].
  - Stickers: exactly 320x320, PNG or APNG, 512 KB, rendered at 160 dp [S12].
- **Where text can go.**
  - Discord asks for no logo or text on either the banner or the invite background [S8][S9].
  - Keep the top 48 px of the banner simple, because the server name sits there [S8].
  - On the invite page, the logged-out pop-up covers x 720 to 1200, y 246 to 834 of a 1920x1080 window [S13].
- **Crops.** The invite background is drawn with `object-fit: fill`, so it stretches on other window shapes [S13]. Avoid circles, faces and type near the edges.
- **Common mistakes.** Using the old 600x240 profile banner size (the minimum is now 680x240 [S10]). Putting server names on the banner.
- **Not official.** The 512x512 server icon and avatar size is widely cited, not stated by Discord [S103].

### Reddit

- **Anatomy.**
  - Desktop banner at least 1072x128 (about 8.4:1) [S14]. Mobile banner at least 1080x128 [S14].
  - Community icon 300x300 [S15].
  - For posts, Reddit's ad spec recommends 4:3 at 1440x1080 as the one image that works on every device. It also takes 1:1, 3:4, 4:5 and 16:9 on mobile [S16].
- **Copy budget.** Ad headlines allow 300 characters. Reddit recommends 100 or fewer, and 80 when truncation matters [S16].
- **Crops.** Other ratios may be letterboxed [S16]. I could not measure the banner crop because the test browser blocks reddit.com.
- **Changed.** 1920x384 desktop banners, 1600x480 mobile banners and 256x256 icons belong to older layouts [S14][S15].

### Tumblr

- **Anatomy.**
  - Header: 2048x1152 (16:9), 10 MB, JPEG, PNG, WEBP or GIF [S17].
  - Avatar: ideal 128x128, 10 MB; GIFs are converted to static [S17].
- **Crops and overlays (measured).**
  - The header shows uncropped at 16:9: 390x219 on phones, 580x326 on desktop.
  - A 96 px avatar overlaps the bottom centre. The keepout is x 772 to 1276, y 824 to 1152 at full size [S18].
  - The header avatar was square on @changes, and post avatars are round [S18].
- **Changed.** The widely cited 3000x1055 header is outdated [S17].

### WhatsApp (Status, profile, Business, catalog, stickers)

- **Status.**
  - Video is limited to 90 s; longer videos are cut to the first 90 s. Formats are 3GP or MP4 [S19][S20].
  - Media is compressed and can look blurry [S20]. Send clean, high-contrast art.
- **Profile photo.** Shown as a circle. A WhatsApp Business Platform partner documents a 640 px maximum edge and 5 MB [S25]. WhatsApp's own help gives no size.
- **Business cover photo.** It exists and is public by default; you can crop and rotate it on upload [S21]. WhatsApp publishes no size. 1211x681 comes from WABetaInfo's testing [S22].
- **Catalog.**
  - WhatsApp requires at least one image per item [S26].
  - If a Meta catalog is linked, Meta's rules apply: JPEG or PNG, 8 MB max, square, at least 500x500, 1024x1024 recommended [S23].
  - Do not put text over the product. No calls to action, promo codes, watermarks or temporary prices [S23].
- **Stickers.**
  - Exactly 512x512 WebP. Static 100 KB max; animated 500 KB max and 10 s max, with frames of at least 8 ms [S24].
  - The first frame must show the complete sticker [S24]. An 8 px white outline is recommended [S24].
  - Tray icon 96x96, 50 KB [S24]. 3 to 30 stickers per pack [S24].
- **Channels.** I found no image spec for Channels. Treat channel updates like chat images.

### Telegram

- **Posts.**
  - Telegram keeps photos at up to 2560 px on the long side and generates 1280, 800 and 320 px versions [S29].
  - Bot uploads are capped at 10 MB, with width plus height at most 10000 and a ratio of at most 20 [S28].
  - The public preview shows posts about 327 px wide on a 390 px phone [S30].
- **Stories.** Photos must be exactly 1080x1920 and 10 MB or less. Videos are 720x1280, H.265, MPEG4, 30 MB or less, 0 to 60 s [S28].
- **Stickers.**
  - Static: one side exactly 512 px and the other 512 or less, PNG or WEBP [S27].
  - Animated TGS: 512x512, 3 s, 64 KB, 60 fps [S27]. Video WEBM (VP9): 3 s, 30 fps, 256 KB [S27].
  - Custom emoji: exactly 100x100 [S27]. Set thumbnail: 100x100, 128 KB [S28].
- **Avatars.** Telegram makes square crops of 160, 320, 640 and 1280 px [S29]. Which crop avatars use is not documented.

### Viber

- **Account icon.** JPEG 720x720, 512 KB. The conversation background is JPEG up to 1920x1920, 512 KB [S31].
- **Picture messages.** JPEG, PNG or static GIF. The limit is 1 MB on iOS and 3 MB on Android [S31]. Thumbnails are 400x400, 100 KB [S31].
- **Business message images.** Partners disagree. Infobip says 800x800 [S32]; other partners say 400x400. Keep files under 1 MB.

### LINE (Official Account)

- **Rich menu.**
  - OA Manager templates are 2500x1686 (large) or 2500x843 (compact), JPEG or PNG, 1 MB [S34].
  - The API also takes 1200 and 800 px widths. Its rule is width 800 to 2500, height 250 or more, and width divided by height at least 1.45 [S33].
  - Rich menus do not show on LINE for PC [S34].
  - One image carries every tap tile, so keep each label inside its tile.
- **Rich message.** OA Manager uses a 1040x1040 square, 10 MB [S35]. API imagemaps must be served at 240, 300, 460, 700 and 1040 px wide [S33].
- **Profile and cover.**
  - Icon 640x640, and it can change only once per hour [S36].
  - Background (cover) 1080x878 recommended; LINE notes it may vary slightly by viewing environment (translated from Japanese) [S36].
  - The business profile page background is cropped at 2:1 (200x200 minimum, under 10 MB) [S37].
- **Message images through the API.** Up to 10 MB; the preview image is 1 MB [S33]. Template thumbnails are 1.51:1 or 1:1, 1024 px wide at most [S33].
- **Stickers (Creators Market).**
  - Up to 370x320 with even width and height, about 10 px margin, transparent PNG, 1 MB each [S38].
  - Main image 240x240, chat tab 96x74, sets of 8 to 40 [S38].
  - Rejected: ads, logos alone, requests for personal data, references to other messaging services, and sexual, violent or nationalist content [S38].

### KakaoTalk Channel

- **Profile image.** 640x640, 10 MB, JPG or PNG [S39].
- **Brand card.** Business channels only. 16:9, 1:1 or 3:4, 10 MB [S39].
- **Channel messages.**
  - Wide-image type: 800x600 (4:3), with up to 76 characters of text and an 8-character button [S40].
  - List type: header 800x400 (2:1), items 800x800 [S40].
  - Carousel: 800x400 or 800x600, with every card in the same ratio [S40].
  - Bubbles accept 2:1 to 3:4; anything outside that is centre-cropped [S40].
  - Promo title up to 20 characters, copy 50 characters [S40].

### WeChat Official Account

- **Covers.**
  - A news article's cover is cropped from one uploaded image into 2.35:1 and 1:1 [S41].
  - Image posts (newspic) also allow 16:9, take up to 20 images, and use the first image as the cover [S41].
- **Pixels.**
  - 900x383 is the practice size used by editors and many open-source tools; GitHub code search finds 499 files with "900x383 wechat" [S43]. WeChat itself only states the ratios.
  - A common trick is one 1283x383 canvas: 900 for the 2.35:1 crop plus a 383 square for the 1:1 crop [S43].
- **Limits.**
  - Library images: 10 MB, in bmp, png, jpeg, jpg or gif [S42]. Thumbnails: 64 KB JPG [S42].
  - Images inside the article body must be jpg or png under 1 MB [S42]. External image links in the body are filtered [S42].
- **Moments.** The article card in Moments uses the square crop. That is practice; I did not verify it. Moments ads are a separate Tencent Ads spec, not covered here.

### Weibo, Xiaohongshu, Douyin, VK

- **Weibo (measured, no official size found) [S44].**
  - Weibo's own account uses a square 1242x1242 cover.
  - Desktop web shows the centre 16:9, so only y 272 to 970 is visible there, with the 100 px avatar over the lower left.
- **Xiaohongshu (measured) [S45].**
  - Mobile web requests every feed cover as a 3:4 crop (360x480) in 188 px cards.
  - Desktop shows covers between 4:3 and 3:4; 26 of 31 were 3:4.
  - The first image is the cover and the title sits below it, not on it. Big cover text must read at 188 px wide.
- **Douyin (measured) [S46].** The PC featured feed shows 16:9 cards (50 of 52 at 400x225). This is the main difference from TikTok. Vertical video can reuse the existing `tiktok` preset.
- **VK (measured) [S47].**
  - The official VK community cover is 1822x728 (5:2).
  - Desktop shows it at about 3:1, anchored to the bottom, so the top 17% is cut.
  - Phones show the full 5:2, with the avatar over the lower left and buttons in the top corners.

### Google Business Profile

- **All photos, including the logo and cover.** JPG or PNG, 10 KB to 5 MB, 720x720 recommended, 250x250 minimum, in focus, "no significant alterations or excessive use of filters" [S48].
- **Cover.**
  - Setting a cover does not guarantee it shows first [S48].
  - Google may choose a customer photo instead if yours looks low quality [S48].
  - Maps desktop shows the top photo at 426x240 (16:9) [S51]. BrightLocal uses 1332x750 [S50].
- **Posts.**
  - Google may remove posts containing unverified phone numbers, email addresses or social handles; use the Call now button instead [S49].
  - Hotels cannot post offers [S49].
  - Duplicate photos can make a profile look spammy [S50].
- **Products.** Product images must meet Google's Shopping ads policy [S50].

### Portfolios: Behance, Dribbble, ArtStation

- **Behance.**
  - Cover: at least 808x632 [S52]. Tiles are 330x258 on desktop and the CDN serves at most 808 px wide [S55].
  - Project images: shown at 1400 wide and up to 2800 in the lightbox; 10 MB or less recommended; uploads over 50 MB are refused [S53]. No GIF covers [S53].
  - Banner: 3200x410 [S54].
- **Dribbble.**
  - Feed thumbnails are 4:3 (297x223) and centre-cropped from sources such as 1600x1200 [S59].
  - API uploads must be exactly 400x300 or 800x600, 8 MB [S58].
  - Pro masthead: at least 1600x1200, 5 MB. Avatar: 800 KB, with no custom crop [S57].
  - Rejected [S56]:
    - contact details in the shot or description;
    - asset-sale and "download free" shots;
    - ads for services;
    - wholly AI-generated work;
    - unaltered stock;
    - photography.
- **ArtStation.**
  - Explore tiles are square (about 205 px), served as 800x800 [S62].
  - Project images must be over 400x400, under 10000x10000 and under 10 MB. ArtStation recompresses to JPG 90% at 1920 wide and recommends a 3840 px JPG in sRGB [S61].
  - Profile header: over 1920x640 [S60].

### Blogs and newsletters

- **WordPress.**
  - Core makes 150, 300, 768, 1024, 1536 and 2048 px sizes and scales anything over 2560 px down to 2560 [S63].
  - The default theme, Twenty Twenty-Five, crops featured images to 3:2 in both the post and the query loop [S64]. Its content is 645 px wide, and 1340 px for wide blocks [S64].
- **Medium.** Images up to 25 MB, in JPG, GIF or PNG. At least 1192 px wide unlocks every placement [S65]. The featured image drives the social card, and a focal point guides the automatic crops [S66][S67].
- **Substack.**
  - Logo 256+ px, email banner 1100x220 (transparent), cover 600+ px [S68].
  - Post preview at least 1200x630 with a 14:10 crop [S68].
  - Full-width images taller than 1:1 are cropped to 1:1 [S68].
- **Ghost.** Icon: square, 60+ px. Logo: 600x72 or larger, transparent. Cover: 1500+ px wide [S69]. Post feature image sizes depend on the theme.
- **Beehiiv.** Thumbnails 1200x630, according to beehiiv's help pages as quoted in search snippets [S70]. The pages sit behind a bot check.
- **Hashnode.** 1200x630 per its support doc [S71]; the official starter kit renders covers at 1600x840 (the same ratio) [S71].
- **dev.to.** 1000x420, cropped by the Forem code; 25 MB upload limit [S72].
- **Blogger.** No official size found; it depends on the theme.
- **LinkedIn newsletter.** Its help pages list no image sizes; left to the LinkedIn agent.

**One blog thumbnail that works across CMSs.** Use a 1200x675 (16:9) master and export three versions.

1. **Canvas.** Google Discover wants 1200 px or wider, more than 300,000 pixels and 16:9 [S74].
2. **Text zone.** Keep type inside x 140 to 1060 and y 40 to 635. That survives:
   - the WordPress Twenty Twenty-Five 3:2 crop (x 94 to 1106) [S64];
   - Substack's 14:10 crop (x 128 to 1072) [S68];
   - the 1.91:1 Open Graph crop (y 24 to 651).
   This is the `blog-featured` preset.
3. **Light on text.** Google advises against logo-only or text-heavy images in `og:image` and schema markup [S74].
4. **Exports.**
   - 1200x630 for Beehiiv, Hashnode and Open Graph: the existing `og-image` preset [S70][S71].
   - 1200x1200 and 1200x900 for Article structured data, which recommends 16:9, 4:3 and 1:1 images [S73].

### Music and audio

- **Release cover art.** 3000x3000 RGB passes every store I checked:
  - DistroKid: JPG, 1000 px minimum, 3000 ideal [S89].
  - TuneCore: square, 1600 to 3000 px, under 10 MB [S90].
  - Spotify: 640 to 10000 px, sRGB, no upscaling [S78].
  - Bandcamp: square, 1400+ px [S94].

  Apple Music for Artists now asks for at least 4000x4000 [S85]. TuneCore caps uploads at 3000 [S90], so keep a 4000 master and export per distributor.
- **Text allowed on cover art.** Only the artist name and the exact release title [S85][S90].
- **Rejection rules for cover art.**
  - URLs, QR codes, X page names, emails, social handles or logos [S85][S89][S90].
  - Store names or logos: Spotify, iTunes, "Apple Music" [S85][S88][S89][S90].
  - Prices [S85][S88][S89][S90].
  - "CD", "DVD", vinyl or "Digital Exclusive" [S85][S88][S89][S90].
  - Blur or pixelation, rotation, cut-off art, art squeezed into a corner [S88][S89][S90].
  - Unlicensed stock [S89].
  - The same art reused across releases [S89].
  - A parental advisory logo on a release that is not explicit [S85].
  - Audio-format claims such as Dolby Atmos or 24-bit on Apple [S88].
- **Explicit labels.** Explicit tracks must be flagged in metadata. Titles must not include "(Explicit)" or self-censored asterisks [S88].
- **Spotify artist profile.**
  - Avatar at least 750x750; header at least 2660x1140; gallery images at least 690x500; 20 MB max [S75].
  - No text, ads or busy backgrounds, and no tour or release promotion [S75].
  - The header shows on desktop, the web player and TV. The mobile app shows the avatar instead [S76].
  - At 1440 desktop the header box is 1150x396, with about 34 px lost at the top and 191 px at the bottom, and the name over the lower-left band [S82].
- **Spotify video.**
  - Canvas: 3 to 8 s, 9:16, "between 720px - 1080px tall", MP4 or JPG. Edges can be cut on some phones. The song and artist name already show [S77].
  - Countdown videos: vertical with audio, 3 to 30 s, at least 1280x720 [S80].
- **Spotify Marquee and Showcase.** These are now paid "display campaigns" [S79]:
  - Marquee: a full-screen pop-up on mobile for new releases within 21 days. You pick a background colour.
  - Showcase: a Home banner with a headline picked from a list.
  - Neither takes custom creative. The release artwork is the creative.
- **Playlist cover.** API uploads are Base64 JPEG, 256 KB max [S81]. The app publishes no size.
- **Apple Music artist image and logo.**
  - Artist image: 2400x2400 preferred, 800x800 minimum. Keep eyebrows and lips inside the crop guides. No text, borders or third-party logos [S86].
  - Artist logo (new with iOS 27): 2880 px wide or 960 px tall, transparent, the artist name only, not solid black [S87].
- **SoundCloud.**
  - Header: at least 2480x520, 2 MB; SoundCloud says avoid text because small screens crop it [S91]. Measured on the web, the header is anchored left and shows at 1208x254. The avatar and name cover the left third, and narrow windows cut the right [S93].
  - Track art: at least 800x800, under 2 MB [S92]. Export a JPG so a 3000 px album file stays under the cap.
- **Bandcamp.**
  - Custom header: 975 px wide [S94]. A live page shows 975x180, and the header is hidden on phones [S95].
  - Background: 1280x1440 recommended [S94].
- **Audiobook covers.**
  - ACX: square, at least 2400x2400, JPG, PNG or TIF, 24-bit RGB, 8 MB, and the title and author must appear [S96].
  - ACX rejects:
    - pixelated text or Audible branding;
    - watermarks or physical media;
    - other marketplaces, websites, running time or price;
    - barcodes, QR codes, book jackets or borders.
  - Exclusive titles may get an "Only from Audible" triangle placed 41% in from the bottom-right corner (984 px on a 2400 cover) [S96].
  - Google Play: 1:1, ideally 2400x2400, 1024 to 7200 px [S97].
  - Spotify for Authors: 3000x3000 recommended [S98].
- **Podcasts.**
  - Apple show cover and episode art: 3000x3000 (1400 to 3000 through RSS), PNG or JPG, no alpha [S83].
  - Episode art should carry no text or logo, because the titles show beneath it [S83].
  - Full Page Show Art is 2048x2732, and the Showcase Hero is 4320x1080, both as layered PSD [S83].
  - Apple rejects Apple logos, terms and hardware; blurry or pixelated art; stock with watermarks; and art for content not on Apple Podcasts [S84].
  - Spotify for Creators video thumbnails: 16:9, 1920x1080 [S99]. Videos: 16:9, 1080p or better, 24 to 60 fps [S99]. Clips: 15 to 90 s, at least 768x1024 [S99].
  - Substack podcasts pull episode art from the podcast logo, the post's social preview or images in the post, in an order Substack says can vary [S100].

---

## Corrections to existing presets

| Preset | Finding | Suggested change |
|---|---|---|
| `wa-status` | Status video is now up to 90 s, and longer videos are cut to the first 90 s. Formats are 3GP or MP4, and media is compressed [S19][S20]. WhatsApp states no image size or byte limit. The FAQ that gave "16 MB for all media" now returns 404. | Keep 1080x1920 and the heuristic safe box. The 5 MB `max_bytes` has no official basis: set it to null, or note it as a practice cap. Add "90 s video" to the notes. |
| `tg-story` | The Bot API requires story photos to be exactly 1080x1920 and 10 MB or less. Videos are 720x1280, H.265, 30 MB or less, 0 to 60 s [S28]. | Raise confidence to `official` for size, set `max_bytes` to 10000000, and keep the safe box as heuristic. |
| `gbp-post` | Google publishes no 4:3 post size. Post photos follow the general photo rules: 10 KB to 5 MB, 720x720 recommended, 250x250 minimum [S48]. Posts with unverified phone numbers, emails or social handles may be removed [S49]. BrightLocal reports 720x720 for posts [S50]. | Keep 1200x900 as `practice`, set `min_size` to 250x250, and add the contact-info removal rule to the notes. Consider a 1:1 alternative at 1080x1080. |
| `podcast-cover` | Apple's 3000x3000 (1400 to 3000 through RSS) is still correct. It must have no transparency or alpha [S83]. Apple rejects Apple logos and terms, blurry or pixelated art, and watermarked stock [S84]. Apple states no byte limit, so the preset's 10 MB is not Apple's. For Spotify playlist covers uploaded through the API, the limit is 256 KB JPEG [S81]. | Add "no alpha" and the rejection rules to the notes. Drop "playlist" from the label, or note the 256 KB API limit. Use the new `podcast-episode-art` preset for episode art, since its rule is no text. |
| `og-image` | 1200x630 still matches Beehiiv and Hashnode [S70][S71] and the Substack minimum [S68]. Substack's thumbnail crops it to 14:10 [S68]. Google Discover prefers 16:9 and discourages text-heavy or logo-only images [S74]. | Keep the size. Note that the centre 882 px survives a 14:10 crop. Add aliases: "beehiiv thumbnail", "hashnode cover", "social preview". |
| `x-card` | X's Cards markup pages now return 404 at docs.x.com, and the full docs dump has no card specs (checked 2026-09-24) [S102]. The 2:1 spec cannot be re-verified. | Keep it `unverified` and note that the docs were withdrawn. `og-image` is the safer default because X crops it. |
| `article-hero` | This matches Google Discover: 1200 px or wider, 16:9, more than 300K pixels [S74]. Medium needs at least 1192 px wide [S65]. WordPress Twenty Twenty-Five crops featured images to 3:2 [S64]. | Keep the size. Adopt the crop-safe box from `blog-featured` (x 140 to 1060), or merge the two presets. Mention the 1:1 and 4:3 exports for Article schema [S73]. |

## Discontinued or changed formats

- **Spotify Marquee and Showcase.** These are now "display campaigns" with no custom creative [S79]:
  - Marquee: the cover art plus a chosen colour.
  - Showcase: a headline picked from a list plus the cover art colour.

  The old Marquee help URL returns 404. Campaigns are open only to teams based in selected European countries, the US, Canada and Mexico, Australia and New Zealand, and Argentina, Brazil, Chile and Colombia. No Asian or African countries are listed [S79].
- **Spotify for Podcasters.** Help now lives under Spotify for Creators (URLs under /creators/) [S99]. The podcast delivery spec is now v1.10, a PDF [S101].
- **Findaway Voices.** help.findawayvoices.com did not respond. Spotify's self-serve audiobook upload is documented under Spotify for Authors [S98].
- **Apple Music.** Album cover guidance rose to at least 4000x4000 [S85]. Artist logos arrived with iOS 27 [S87].
- **Discord.** The profile banner minimum is now 680x240, not 600x240 [S10].
- **Tumblr.** The header is now 2048x1152 at 16:9; the 3000x1055 advice is outdated [S17].
- **Reddit.** The icon is now 300x300 (was 256) [S15]. Banner minimums are now 1072x128 on desktop and 1080x128 on mobile. The old sizes (1920x384, 4000x192 and a 1600x480 mobile banner) are gone [S14].
- **WhatsApp Status.** Video is now up to 90 s; older guides still say 30 s [S19][S20].
- **Twitch.** The banner advice "concentrate the graphics on the left" [S1] no longer fits the offline layout, where the left sits under the offline card [S6]. The two official panel pages also disagree [S1][S2].
- **X.** The Cards documentation was removed [S102].
- **Dribbble.** Help moved to a new help centre that no longer states shot pixel sizes. Only the API page does [S56][S58].

## Regional notes (practice judgement, not measured market data)

- **Bangladesh.** In this scope, WhatsApp does the heavy lifting:
  - Status: `wa-status`.
  - Business cover and catalog.
  - Stickers, which are popular for festival greetings.

  Telegram channels matter for education and deal communities. Google Business Profile matters for local shops. Spotify display campaigns are not open to teams based in Asia [S79]. Bengali script has dense conjuncts, so treat `min_text_px` as a floor, not a target.
- **India.**
  - WhatsApp: Business catalog, Status and Channels.
  - Telegram channels.
  - Google Business Profile.
  - For creators: Spotify (profile images and cover rules) and Discord or Reddit for gaming and tech audiences.

  Distributors' cover rules (DistroKid, TuneCore) apply to regional-language releases too.
- **China.** Use the local set: WeChat Official Account (2.35:1 plus 1:1 covers), Weibo, Xiaohongshu (3:4 notes) and Douyin (plus 16:9 on PC). Chinese type needs larger minimum sizes than Latin script. Western platforms are not the channel there.
- **Japan and Thailand.** LINE Official Account comes first:
  - rich menu at 2500x1686 or 2500x843;
  - rich message at 1040x1040;
  - account icon and cover;
  - LINE stickers (Creators Market).

  Rich menus do not show on LINE for PC [S34].
- **Korea.** KakaoTalk Channel: profile at 640x640, the brand card, and channel messages at 800x600, 800x400 or 800x800, with character caps [S39][S40].
- **MENA.**
  - WhatsApp Business (cover, catalog, stickers) and Telegram.
  - Discord, Twitch and Kick for gaming.
  - Right-to-left interfaces mirror many overlays, such as avatars and buttons, which move to the other side. I did not measure RTL layouts, so mirror the keepouts and check before delivery.
- **Russia and CIS (bonus).** The VK community cover is 5:2. Desktop shows it bottom-anchored at 3:1 [S47].

## Could not verify

- **Twitch.** The profile picture size (256x256 is widely cited), an official size for the offline screen, and the mobile app banner crop.
- **Kick.** Banner crop, because the test channel was live.
- **Discord.** Official server icon and avatar sizes; the widths of the desktop sidebar, profile pop-up and emoji (the view widths used are estimates); and where the avatar overlaps the profile banner (needs login).
- **Reddit.** All crops, because reddit.com is blocked in the test browser. The organic image size limit.
- **WhatsApp.**
  - Official profile photo size and Status image byte limit.
  - Business cover size (only WABetaInfo) [S22].
  - Any image spec for Channels.
  - Sticker display size in chat.
- **Telegram.** Which crop sizes avatars use, and the best post ratio.
- **Viber.** Business message image size (partners disagree), and Viber Channels or Communities images.
- **LINE and Kakao.** Chat bubble display widths (estimates used).
- **WeChat.**
  - 900x383 as a WeChat statement (it is practice).
  - The Moments grid behaviour, and Moments ads.
- **Weibo, Xiaohongshu, Douyin.**
  - Official pixel specs, the mobile app crops, and Xiaohongshu's image count per note.
  - Douyin's creator-centre cover ratios (login wall).
  - Search engines served captchas or empty pages for Chinese queries, and I did not bypass them.
- **VK.** The official help text, because vk.com/faq rejects non-browser clients and the developer docs have no sizes.
- **Google Business Profile.** The post image crop, the product image size, and the cover crop in mobile Search.
- **Portfolios.**
  - Behance banner crop.
  - ArtStation header crop, and whether larger thumbnail variants exist.
  - Dribbble's web upload file limit.
- **Blogs.**
  - Beehiiv pages: only search snippets, because of the bot check.
  - Blogger and Ghost post feature image sizes (theme-dependent).
  - LinkedIn newsletter: deferred.
- **Spotify.**
  - The podcast delivery spec PDF (not downloaded).
  - Playlist cover limits in the app.
  - How the mobile app crops the header and avatar.
- **Apple.** The template ZIP safe areas for podcast art and artist logos (not downloaded).
- **SoundCloud.** Mobile app header crop.
- **Bandcamp.** The header height rule (180 is measured, not stated).
- **X.** The card spec.

---

## Sources

- [S1] Twitch Help, "Channel Page Setup", last modified 2025-06-18. https://help.twitch.tv/s/article/channel-page-setup
- [S2] Twitch Help, "How to Edit Info Panels". https://help.twitch.tv/s/article/how-to-edit-info-panels
- [S3] Twitch Help, "Emote Formatting & Instant Emote Upload Requirements". https://help.twitch.tv/s/article/emote-guidelines
- [S4] Twitch Help, "Subscriber Badge Guide". https://help.twitch.tv/s/article/subscriber-badge-guide
- [S5] StreamScheme, "Twitch Image Sizes", 2026-01-10 (secondary). https://www.streamscheme.com/twitch-image-sizes/
- [S6] Measured: twitch.tv/twitch/about at 1440 and 1920 CSS px, 2026-09-24.
- [S7] Kick Help Center, "How to update your profile", 2026-05-22. https://help.kick.com/en/articles/7120563-how-to-update-your-profile
- [S8] Discord Support, "Server Banners". https://support.discord.com/hc/en-us/articles/360028716472-Server-Banners
- [S9] Discord Support, "Server Invite Background". https://support.discord.com/hc/en-us/articles/4415841146391-Server-Invite-Background
- [S10] Discord Support, "Custom Profiles", updated about 2026-03. https://support.discord.com/hc/en-us/articles/4403147417623-Custom-Profiles
- [S11] Discord Support, "How to Add Custom Emojis", updated about 2025-11. https://support.discord.com/hc/en-us/articles/360036479811-Custom-Emojis
- [S12] Discord Support, "Tips for Sticker Creators FAQ". https://support.discord.com/hc/en-us/articles/4402687377815
- [S13] Measured: discord.com/invite/discord-developers at 1920x1080, 2026-09-24.
- [S14] Reddit Help, "Banner", updated about 2025. https://support.reddithelp.com/hc/en-us/articles/15484339588884-Banner
- [S15] Reddit Help, "Community icon", updated about 2025. https://support.reddithelp.com/hc/en-us/articles/15484265952660-Community-icon
- [S16] Reddit Ads Help, "Image Ad Specifications". https://business.reddithelp.com/s/article/image-ad-specifications
- [S17] Tumblr Help, "Changing Your Blog's Appearance", modified 2025-12-16. https://help.tumblr.com/knowledge-base/appearance-options/
- [S18] Measured: tumblr.com/staff and tumblr.com/changes at 390 and 1440 CSS px, 2026-09-24.
- [S19] WhatsApp Help, "About status". https://faq.whatsapp.com/454876960047011
- [S20] WhatsApp Help, "Can't create or share status". https://faq.whatsapp.com/896930805262380
- [S21] WhatsApp Help, "How to edit your business profile". https://faq.whatsapp.com/smba/account-and-profile/how-to-edit-your-business-profile/
- [S22] WABetaInfo, "WhatsApp is releasing cover photos for business profiles", updated 2025-10-23 (secondary). https://wabetainfo.com/whatsapp-is-releasing-cover-photos-for-business-profiles/
- [S23] Meta Business Help, "Product image specifications for catalogs". https://www.facebook.com/business/help/686259348512056
- [S24] WhatsApp, stickers README, last commit 2025-04-17. https://github.com/WhatsApp/stickers/blob/main/Android/README.md
- [S25] HighLevel Support, "WhatsApp Business Profile Management" (secondary, partner docs). https://help.gohighlevel.com/support/solutions/articles/155000002349-whatsapp-business-profile-management
- [S26] WhatsApp Help, "About catalog". https://faq.whatsapp.com/405903568419894
- [S27] Telegram, "Stickers". https://core.telegram.org/stickers
- [S28] Telegram Bot API (sendPhoto, InputStoryContentPhoto and InputStoryContentVideo, setStickerSetThumbnail). https://core.telegram.org/bots/api
- [S29] Telegram API, "Files" (image thumbnail types). https://core.telegram.org/api/files
- [S30] Measured: t.me/s/telegram at 390 CSS px, 2026-09-24.
- [S31] Viber, REST Bot API. https://developers.viber.com/docs/api/rest-bot-api/
- [S32] Infobip, "Viber Business Messages: message templates" (secondary). https://www.infobip.com/docs/viber/business-messages/message-templates
- [S33] LINE Developers, Messaging API reference (Markdown version). https://developers.line.biz/en/reference/messaging-api/
- [S34] LY Corporation for Business, "リッチメニュー" (Rich menus), 2025-07-29. https://www.lycbiz.com/jp/manual/OfficialAccountManager/rich-menus/
- [S35] LY Corporation for Business, "リッチメッセージ" (Rich messages), 2025-07-29. https://www.lycbiz.com/jp/manual/OfficialAccountManager/rich-messages/
- [S36] LY Corporation for Business, account settings, 2026-04-24. https://www.lycbiz.com/jp/manual/OfficialAccountManager/account-settings/
- [S37] LY Corporation for Business, profile, 2026-09-16. https://www.lycbiz.com/jp/manual/OfficialAccountManager/profile/
- [S38] LINE Creators Market, sticker guidelines. https://creator.line.me/en/guideline/sticker/
- [S39] Kakao Business guide, "채널홈 설정" (channel home settings). https://kakaobusiness.gitbook.io/main/partner/smb/channel/step1/profile
- [S40] Kakao Business guide, channel message "제작 가이드" (production guide). https://kakaobusiness.gitbook.io/main/ad/moment/messagead/channelmessage/content-guide
- [S41] WeChat Developers, draft add API (cover crop ratios). https://developers.weixin.qq.com/doc/service/api/draftbox/draftmanage/api_draft_add.html
- [S42] WeChat Developers, add permanent material and upload image. https://developers.weixin.qq.com/doc/service/api/material/permanent/api_addmaterial.html
- [S43] GitHub code search "900x383 wechat" (499 files, 2026-09-24), for example https://github.com/xstongxue/best-skills (skills/wechat-article-writer/reference/cover_guide.md), practice evidence.
- [S44] Measured: weibo.com @微博小秘书 and @人民日报 profiles, 2026-09-24.
- [S45] Measured: xiaohongshu.com explore at 390 and 1440 CSS px, 2026-09-24.
- [S46] Measured: douyin.com/jingxuan at 1440 CSS px, 2026-09-24 (behind the login modal, not interacted with).
- [S47] Measured: vk.com/team at 1440 and 390 CSS px, 2026-09-24.
- [S48] Google Business Profile Help, "Manage your Business Profile photos & videos". https://support.google.com/business/answer/6103862
- [S49] Google Business Profile Help, "Business Profile photos, videos & posts content policy". https://support.google.com/business/answer/7213077
- [S50] BrightLocal, "How to Upload and Manage Google Business Profile Photos", 2025-11-18 (secondary). https://www.brightlocal.com/learn/google-business-profile/optimization/google-business-profile-photos/
- [S51] Measured: Google Maps place panel (desktop web), 2026-09-24.
- [S52] Behance Help, "Guide: Cover Images" and "Guide: Cover Image & Project Title". https://help.behance.net/hc/en-us/articles/360033998134-Guide-Cover-Images
- [S53] Behance Help, "Guide: Formatting Images For Display On Behance". https://help.behance.net/hc/en-us/articles/204484614-Guide-Formatting-Images-For-Display-On-Behance
- [S54] Behance Help, "Guide: Profile Banner". https://help.behance.net/hc/en-us/articles/360015540594-Guide-Profile-Banner
- [S55] Measured: behance.net/galleries/graphic-design at 1440 CSS px, 2026-09-24.
- [S56] Dribbble Help, "Dribbble Shot Guidelines", 2025-04-08. https://help.dribbble.com/en/articles/11056039-dribbble-shot-guidelines
- [S57] Dribbble Help, "Creating & Managing your Dribbble Profile", 2025-04-14. https://help.dribbble.com/en/articles/11056066-creating-managing-your-dribbble-profile
- [S58] Dribbble API v2, Shots. https://developer.dribbble.com/v2/shots/
- [S59] Measured: dribbble.com/shots/popular at 1440 CSS px, 2026-09-24.
- [S60] ArtStation Help, "How do I change my background profile image?". https://help.artstation.com/en/articles/16155203-how-do-i-change-my-background-profile-image
- [S61] ArtStation Help, "How do I get the best quality of images on ArtStation?". https://help.artstation.com/en/articles/16155253-how-do-i-get-the-best-quality-of-images-on-artstation
- [S62] Measured: artstation.com explore at 1440 CSS px, 2026-09-24.
- [S63] WordPress core source (trunk): schema.php, image.php, media.php (media.php last commit 2026-09-10). https://github.com/WordPress/wordpress-develop
- [S64] WordPress Twenty Twenty-Five theme: templates/single.html, patterns/template-query-loop.php, theme.json (trunk). https://github.com/WordPress/wordpress-develop/tree/trunk/src/wp-content/themes/twentytwentyfive
- [S65] Medium Help, "Using images". https://help.medium.com/hc/en-us/articles/215679797-Using-images
- [S66] Medium Help, "Setting a featured image on your post". https://help.medium.com/hc/en-us/articles/215680047-Setting-a-featured-image-on-your-post
- [S67] Medium Help, "Trouble controlling post previews on feeds". https://help.medium.com/hc/en-us/articles/228036227-Trouble-controlling-post-previews-on-feeds
- [S68] Substack Support, "What are the optimal image dimensions for my Substack publication?", updated about 2026-03. https://support.substack.com/hc/en-us/articles/4408381685268-What-are-the-optimal-image-dimensions-for-my-Substack-publication
- [S69] Ghost Help, design and branding settings. https://ghost.org/help/design-settings/
- [S70] beehiiv Help, "Adding thumbnails, images, and GIFs to your posts" and related pages, read through Brave Search snippets (the pages are behind a bot check). https://www.beehiiv.com/support/article/4413248838423-how-to-add-a-thumbnail-to-a-post
- [S71] Hashnode support docs, cover-photo.md (2021-03-05), and the Hashnode starter kit post-header.tsx. https://github.com/Hashnode/support/blob/main/docs/cover-photo.md
- [S72] DEV, editor guide; Forem source cloud_cover_url.rb and settings/user_experience.rb (main branch). https://dev.to/p/editor_guide
- [S73] Google Search Central, "Article structured data", last updated 2026-09-08. https://developers.google.com/search/docs/appearance/structured-data/article
- [S74] Google Search Central, "Google Discover", last updated 2026-03-09. https://developers.google.com/search/docs/appearance/google-discover
- [S75] Spotify for Artists, "Artist image guidelines". https://support.spotify.com/us/artists/article/artist-image-guidelines/
- [S76] Spotify for Artists, "Managing your artist images on Spotify". https://support.spotify.com/us/artists/article/managing-your-artist-images-on-spotify/
- [S77] Spotify for Artists, "Canvas guidelines". https://support.spotify.com/us/artists/article/canvas-guidelines/
- [S78] Spotify for Artists, "Cover art requirements". https://support.spotify.com/us/artists/article/cover-art-requirements/
- [S79] Spotify for Artists, "Getting started with display campaigns", "Customizing your display campaign", "Creating a display campaign". https://support.spotify.com/us/artists/article/getting-started-with-display-campaigns/
- [S80] Spotify for Artists, "Countdown videos". https://support.spotify.com/us/artists/article/countdown-videos/
- [S81] Spotify Web API, "Upload Custom Playlist Cover Image". https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover
- [S82] Measured: open.spotify.com artist page at 1440 CSS px, 2026-09-24.
- [S83] Apple Podcasts for Creators, Artwork Guide and the Show Cover (5514), Episode Art (5516), Full Page Show Art (5515) and Showcase Hero (5522) pages. https://podcasters.apple.com/support/896-artwork-requirements
- [S84] Apple Podcasts for Creators, "Artwork Policies". https://podcasters.apple.com/support/5510-artwork-policies
- [S85] Apple Music for Artists, "Album cover art on Apple Music". https://artists.apple.com/support/1120-cover-art
- [S86] Apple Music for Artists, "View guidelines for artist images". https://artists.apple.com/support/1104-artist-image-guidelines
- [S87] Apple Music for Artists, "Artist logo guidelines". https://artists.apple.com/support/5606-artist-logo-guidelines
- [S88] Apple Music Style Guide, sections 6 (Parental Advisory) and 7 (Artwork). https://help.apple.com/itc/musicstyleguide/en.lproj/static.html
- [S89] DistroKid Help, "What Are the Requirements for Album Artwork?". https://support.distrokid.com/hc/en-us/articles/360013534334-What-Are-the-Requirements-for-Album-Artwork
- [S90] TuneCore Help, "What are TuneCore's cover art formatting requirements?". https://support.tunecore.com/hc/en-us/articles/115006685728-What-are-TuneCore-s-cover-art-formatting-requirements
- [S91] SoundCloud Help, "Update Your Profile Image and Header". https://help.soundcloud.com/hc/en-us/articles/115003450007-Update-Your-Profile-Image-and-Header
- [S92] SoundCloud Help, "Edit and customize your tracks". https://help.soundcloud.com/hc/en-us/articles/46022345620123-Edit-and-customize-your-tracks
- [S93] Measured: soundcloud.com/soundcloud at 1440 and 390 CSS px, 2026-09-24.
- [S94] Bandcamp Help, "Bandcamp design tutorial". https://get.bandcamp.help/en/articles/15263106-bandcamp-design-tutorial
- [S95] Measured: sufjanstevens.bandcamp.com at 1440 and 390 CSS px, 2026-09-24.
- [S96] ACX Help, "Cover art requirements". https://help.acx.com/s/article/cover-art-requirements
- [S97] Google Play Books Partner Center Help, "3. Upload or update a cover image" and "Book file guidelines". https://support.google.com/books/partner/answer/14187606
- [S98] Spotify for Authors, "Uploading audiobooks to Spotify for Authors". https://support.spotify.com/us/authors/article/uploading-audiobooks/
- [S99] Spotify for Creators, "Thumbnails", "Video specs", "Clips". https://support.spotify.com/us/creators/article/thumbnails/
- [S100] Substack Support, "What artwork appears for my Substack podcast?". https://support.substack.com/hc/en-us/articles/8503114939412-What-artwork-appears-for-my-Substack-podcast
- [S101] Spotify Provider Support, "Podcast Delivery Specification" (now v1.10, PDF, not downloaded). https://providersupport.spotify.com/article/podcast-delivery-specification-1-9
- [S102] X developer docs: the cards overview and summary_large_image pages return 404 at docs.x.com, and llms-full.txt has no card markup section (checked 2026-09-24).
- [S103] Krumzi, "Discord Banner Size 2026" (secondary, for the 512x512 server icon convention). https://www.krumzi.com/size-guide/discord-banner-size
