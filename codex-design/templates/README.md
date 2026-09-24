# Templates

A starting point for every deliverable, built the way the checks want it. Every pattern renders with no errors and
no warnings on the presets listed below, in the sample brand (`CODEX_DESIGN_PATTERNS=1` runs that regression). Start from the closest pattern,
never from a blank page, and change the idea, the copy and the visuals: a pattern is a structure, not a look.

```
templates/
  kit/            cd-kit.css (reset, canvas, .safe, .page, print boxes, helpers) and cd-kit.js (data-fit)
  sample-brand/   a fictional brand (Tidewater Coffee Roasters): brand.json, brand.css, fonts, logo files,
                  applications/ (renders for the brand book)
  patterns/       the designs below, plus assets/ (QR codes)
  brand/          guidelines.html, the brand book built from brand.json
```

## Use a pattern

1. Copy the pattern into the project (for example `design/post.html`).
2. Point the second stylesheet at the client's `brand/brand.css` (made by `design.py brand --json brand/brand.json`).
   The kit link (`https://codex-design.invalid/kit/…`) can stay: the renderer serves it. For source files that must
   open outside the renderer, run `design.py kit --out design --html design/*.html`, which copies the kit and rewrites
   the links.
3. Replace the copy with the approved copy (and write `copy.json`), the sample visuals with the client's photos or
   codex-imagegen plates, and the sample logo with the client's files.
4. Render or pack on the presets below, fix every error, fix or justify every warning, then judge.

The brand tokens the patterns use: colours `ink`, `paper`, `primary`, `accent`, `muted`, `line`, `sand`
(`--ink` … in brand.css); fonts `--font-display`, `--font-text` and, for a second script, `--font-bengali` (or the
script's own role); logo files `mark`, `mark_reversed`, `wordmark`. A client brand with other names needs the
variables renamed in the copied pattern.

## Patterns

| Pattern | Deliverable | Presets (all clean) | Render |
|---|---|---|---|
| `post-photo.html` | photo-led post, eased scrim, CTA | ig-portrait, ig-square, ig-story, fb-feed | `pack` |
| `post-type.html` | type-led post; `v-announce`, `v-event`, `v-hiring` | same | `pack` |
| `post-product.html` | product offer ("Bold committed") | same + vertical-safe | `pack` |
| `card.html` | info card; `v-quote`, `v-tip`, `v-stat` (SVG chart) | same | `pack` |
| `story.html` | story / reel cover with a sticker slot | ig-story, vertical-safe, wa-status | `render` |
| `carousel.html` | seamless ("chain") carousel, 5 slides | ig-carousel `--slides 5`; li-doc as PDF | `render --slides 5` |
| `thumbnail.html` | YouTube thumbnail; overlays `ov-beast` `ov-fire` `ov-lime` `ov-glass` `ov-marker` | yt-thumbnail (`--scale 3` for 4K) | `render` |
| `day-post.html` | special day, celebratory; `bilingual` adds the audience's script | ig-portrait, ig-square, ig-story, fb-feed | `pack --occasion celebratory` |
| `day-solemn.html` | memorial or solemn day | ig-portrait, ig-square, ig-story | `pack --occasion solemn` |
| `cover.html` | channel and profile covers | yt-banner, fb-cover, li-profile-cover, li-company-cover, x-header | `pack` |
| `ad-banner.html` | static display ads | iab-mrec, iab-leaderboard, iab-halfpage, iab-skyscraper, iab-mobile-banner, iab-billboard, gads-landscape, gads-square | `pack --format jpg` for byte limits |
| `infographic.html` | one chart, one finding, drawn from a JSON data block | ig-portrait, pin-standard, ig-story, li-square | `pack` |
| `pin.html` | Pinterest pin: a guide or list, the photo with an overlapping panel | pin-standard | `render` |
| `blog-featured.html` | blog featured image and link card (Open Graph, X, LinkedIn, WhatsApp) | blog-featured, og-image, article-hero, x-card | `pack` |
| `product-infographic.html` | marketplace secondary image: feature callouts with leader lines (never the main image) | shop-square | `render` |
| `square-cover.html` | podcast, album, single and audiobook cover that reads at 55 px | podcast-cover, album-cover, audiobook-cover, yt-podcast-thumb | `pack` |
| `app-screenshot.html` | app store screenshot: frameless real UI under a 2 to 5 word caption | appstore-iphone-69, play-phone-screenshot | `pack` |
| `book-cover.html` | book cover: the e-book front, or the full print wrap (back, spine, front) from `bookcover` | ebook-master, ebook-kobo, ebook-bookbaby; wraps from `bookcover` (KDP paperback and hardcover, a thin book with no spine text) | `render`; a wrap: `bookcover ... --preset-file book.json`, then `render --preset <id> --preset-file book.json --out cover.pdf` |
| `certificate.html` | certificate: who gives it, what, the name, what for, then date, seal and signature line | certificate-a4-landscape, certificate-letter-landscape | `render --out certificate.pdf` |
| `invitation.html` | invitation card (wedding, gaye holud, launch, dinner): names, occasion, then date, place and reply | invite-5x7, invite-a5 | `render --out invite.pdf` |
| `sign.html` | landscape sign read from a distance: banner, PVC flex, billboard, bus side, screen; every line kept above the distance floor (`--min-text`), the headline fitted to what is left | banner-3x6ft, banner-2x4ft, pvc-banner-2000x1000, pvc-banner-bd-4x6ft, billboard-us-bulletin, billboard-uk-48sheet, billboard-bd-20x10ft, transit-bus-king, signage-1080p, signage-4k | `render --out sign.pdf` (screens: `.png`) |
| `poster.html` | event poster, AIDA, info block, QR | a3-poster, a2-poster, tabloid-poster, poster-18x24 | `render --out poster.pdf` |
| `flyer.html` | A5 flyer, two sides | a5-flyer `--pages 2` | `render --out flyer.pdf` |
| `brochure-trifold.html` | tri-fold brochure, outside and inside | trifold-a4 `--pages 2` | `render --out brochure.pdf` |
| `business-card.html` | business card, two sides | bc-eu, bc-us, bc-jp `--pages 2` | `render --out card.pdf` |
| `brand/guidelines.html` | brand book (10 pages) from brand.json | deck-16x9 `--pages 10` | `render --out brand-guidelines.pdf` |

Print pieces: add `--preview` for PNG proofs, and `--cmyk` (or `--cmyk printer.icc`) only when the printer refuses
RGB PDFs.

## Conventions the checks rely on

- Text and logos live inside `.safe` (the preset's safe zone; on print it sits inside the trim). Backgrounds that
  must reach the paper edge go in `.bleedbox` or are positioned in bleed coordinates.
- Multi-page documents are `.page` elements rendered with `--pages N`; carousels are `.slide`s in a `.track`
  rendered with `--slides N`. Text never crosses a slide cut or a fold (folds come from the preset).
- Size text to its box with `data-fit="min,max"` (and `data-fit-lines`); pages that build DOM in a script call
  `window.__cdFit()` when done and assign their promise to `window.__cdReady`.
- Mark logos with `.logo`, `.wordmark`, `.logo-mark` or `data-logo` (an `<img>` whose file or alt says logo counts
  too): the checks keep text and graphics out of half the logo's height around it. On dark grounds and photos use the
  reversed mark and a paper-coloured wordmark (a CSS mask of wordmark.svg), never the full-colour mark on its own
  colour.
- Keep logos at the brand's own minimum at any preset: `width: max(…, var(--wordmark-min))` or
  `height: max(…, var(--mark-min))`. `design.py brand` writes both from brand.json `min_size` (px at the size people
  see a screen design, from the renderer's `--view-scale`; mm in print), and the checks fail a logo under them. A
  lockup (mark and wordmark together) is one logo: put `data-logo` on its wrapper.
- Labels, dates and captions keep above `var(--label-min)` (34 px on a 1080 post; fine print may sit at
  `--min-text`, marked `class="legal"`): `font: 600 max(34px, var(--label-min, 0px))/1 …`.
- A brand motif reaches the patterns through `--motif-mask` in brand.css (the sample brand's tide line): the accent
  mark before a kicker or a date takes it as a CSS mask, and stays a plain bar for a brand without one.
- Sample photos live in `patterns/assets/photos/` (see its README): real, judged, AI-labelled images of the fictional
  sample brand, so a pattern shows the finished look; a project swaps in its own plates.
- Small dark print text uses `var(--print-black)` (#000) so it prints in black only.
- Numbers and units stay together (`94&nbsp;°C`, `250&nbsp;g`); typographic quotes and the ellipsis (’ “ ” …). No em dash and no spaced en dash anywhere; a range is a hyphen or "to" (09:00-13:00, 10 to 12).
- `data-qa-ignore` is only for deliberate specimens (a failing contrast pair in a brand book, logo misuse examples),
  never to silence a real problem.
- Sample people, numbers and data are fictional and labelled as such; a client design uses the client's facts only.
