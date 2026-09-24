---
name: codex-design
description: "Designs finished graphics like a senior human designer, at each platform's exact size: social posts, stories, carousels, pins, thumbnails, covers, banners, ads, blog and product listing images, app screenshots, book and e-book covers, album art, posters, flyers, brochures, cards, certificates, invitations, merch, infographics, day posts, logos, brand kits, signs and billboards, photo resizes; 526 researched formats and a stated method for any unknown size or kind. Use it whenever a request asks to design, make, edit or resize a graphic that carries text or layout, or to write or fix its copy, Banglish asks included ('banner banao', 'post design kore dao', 'biye card'). Prefer it to plain image generation when words go on the image. Copy reads human: no em dash, no AI or translated tells; natural Bangladeshi Bengali and 22 more languages. Compose (primary): real type in HTML/CSS over codex-imagegen plates, rendered by headless Chrome. Direct (secondary): one GPT Image prompt, OCR-verified. Global by default."
allowed-tools: Bash(python3 ~/.claude/skills/codex-design/scripts/design.py:*), Bash(python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py:*), Read, Write, Edit
---

# Codex Design

Claude is the designer: the research, facts, idea, copy and art direction are Claude's. Two routes turn them into
pixels. **Compose is the primary route.** In a blind comparison on 2026-09-24 (four deliverables, Codex and Claude
judges, both orders), Compose won 3 of 4 deliverables and 17 of 24 votes, for the exact brand fonts, one alignment
axis, restraint and an editable, photo-swappable source.

- **Compose** (primary; `references/ai-visuals.md`, `templates/`): the design is HTML/CSS that `design.py` renders
  and checks, over text-free AI plates, the client's photos and SVG. Exact by construction. The default for posts,
  covers, banners, ads, carousels, print, brand work, series and templates, Bengali and other scripts, and anything
  the client will later drop real photos into.
- **Direct** (secondary; `references/direct.md`): the brief becomes a *dossier* and GPT Image makes the finished
  design in one pass; every word is read back by OCR and repaired region by region, and the real logo is composited.
  For type-as-image concepts (it won a story 4-0 with a giant "100% rye"), fast exploration, and as a challenger on
  hero pieces: make both, ship the `pairwise` winner. A Direct run that still fails leaves Compose a text-free plate.

Command prefix: `python3 ~/.claude/skills/codex-design/scripts/design.py` (every flag, check and exit code:
`references/cli.md`). Visuals: `python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py`.
Scope: this skill owns every deliverable with layout or text, and the copy on it; codex-imagegen owns stand-alone
photos and illustrations; website UI belongs to the frontend skills.

## 0. Preflight

- `doctor` must say `"ready": true` (it exits 1 otherwise and lists optional parts that are missing, with what they
  unlock). `doctor --setup` once per Python version builds the skill venv.
- Renders are offline and run with local file access: render only HTML you wrote. `doctor --clean-tmp` clears temp
  folders of killed runs.
- The judges need codex-imagegen and a Codex login (`doctor` shows both).

## 1. Quick starts

**One feed post (any language).**
1. `brief.md` + `copy.json` with `"locale"`, `"platform"`, the on-image strings, a caption and alt text (`copy.md`).
2. `copylint --copy copy.json` (zero errors), then `copyjudge --copy copy.json --brief brief.md --goal order --runs 3`
   (PASS_NATIVE for client work).
3. `ledger --ledger clients/<client>/ledger.jsonl --client <client> --recipe recipe.json` (no `similar`).
4. Plate: codex-imagegen `batch` with `--strict` and the text zone reserved; then
   `analyze --src plates/x.png --zone 0,0,100,40` (calm, or plan a scrim or panel).
5. HTML from `templates/patterns/post-photo.html`; `render --html design/post.html --preset ig-portrait --copy
   copy.json --out out/post.png --overlay` until the checks are clean.
6. `judge --image out/post.png --brief brief.md --copy copy.json --brand brand/brand.json --kind "Instagram post"
   --runs 3`, fix, re-render, re-judge.
7. `deliver --design out/post.png --copy copy.json --out final/ --ledger … --recipe recipe.json --client <client>`.

**A Bengali carousel.** The same, with `--slides 5` on `render`, the judge on `out/<name>-strip.jpg` (it judges
slide by slide), a varied anchor per slide, Bengali at 12 px or more at viewing size, and `alt_1` … `alt_5` in
copy.json. `deliver --design out/<name>-strip.jpg` ships the five slides.

**A client photo to every size.** `analyze` → `reframe --presets ig-portrait,ig-story,fb-cover,li-profile-cover`
(or `cutout`) → one responsive HTML → `pack --presets … --copy copy.json --strict` → judge the master size →
`deliver` every file.

## 2. Workflow

1. **Brief.** Before designing, settle:
   - the deliverables and their presets (`presets --find WORDS`; §4); an unknown size, platform or kind of design
     follows `formats.md` (below §4);
   - the one message, the audience and the action;
   - the market: place, language, script and calendar come from the client, never from the requester's language,
     location or clock; for day posts, the occasion's tone class and a verified date (`occasions.md`);
   - the brand: the client's `brand/brand.json` and logo files, otherwise create or extend one (`brand.md`);
   - the facts: Claude writes copy from the client's facts but never invents prices, claims, statistics, awards,
     testimonials or contact details; placeholders are visibly marked and listed. For client and hero work, file every
     claim in `facts.json` with a status; `refuted` or `needs_client` stops the design (and `deliver --facts`);
   - the route for every deliverable and element (§3).

   Ask once, at most four short questions, only for real gaps; otherwise decide and say what you assumed. For client
   and hero work, fan out 2-3 background research agents (market and references, occasion and culture, brand and
   competitors) and one fact-checker.
2. **Copy (`copy.md`)**, before the design, in the reader's everyday language, written with the `natural-copy`
   skill (the audience's own words, the register, casual without fake casual):
   - no em dash, no spaced en dash, no AI vocabulary or structures, no translated, calqued, poetic or bookish
     wording, and no slang, emoji or feelings added to sound human;
   - the market's register, address form, loanwords, spelling and digits;
   - three hooks from three patterns (`copy.md` §5), keep the one a stranger gets in two seconds;
   - one call to action that fits the goal, or none; the action fact (time, deadline, price) as `key_fact` on its
     own line;
   - a caption and alt text for every social piece (roles `caption`, `alt`; they never go on the image).

   `copylint` must end with zero errors (`--lang` for a language the copy.json does not tag). `copyjudge`: PASS is
   the floor, PASS_NATIVE the target for client and hero
   work, with `--runs 3` (identical copy spanned 0.18 in six runs). When the runs disagree the report says to run 5.
   Take the judge's better rewrites; check a disputed local term against a local source. A native reader signs off
   non-Latin copy.
3. **Direction contract (at most 150 words)**, given to the judge:
   THESIS (the idea), MESSAGE (what they take in 2 seconds), FIRST GLANCE (the focal point), FORM (a direction from
   `styles.md`, the colour strategy, the type pair, the grid) and FINISH (texture and image treatment).
   - Consider three concepts and reject the category cliché. Swap-the-logo test: if a competitor's logo fits as well,
     find the specific idea.
   - Write the recipe (structure, archetype, focal, device, type mode, palette roles, finish) and check it with
     `ledger`: at least 3 axes away from the client's last six designs, a composition device (`craft.md`, the ten
     devices) the client has not seen in the last three pieces, a hook they have not read lately.
4. **Brand setup** (both routes): `brand --json brand/brand.json` (fonts, `brand.css`). Fonts from `fonts.md`; a
   second script gets its size-adjust (`"Noto Sans Bengali:400,700@110"`) and comes first for text in that script.
5. **Direct route** (only when §3 says so): write the dossier (`direct.md` §4-5), `direct --plan` (its copy is linted
   first), read the prompt, references, safe area and notes, then `direct --judge`. For hero work explore 2-3
   dossiers with `--variants 1` and compare them pairwise. Exit 3 (beyond 3:1) or 4 (still wrong) means compose; exit
   4 leaves a text-free plate. Then go to step 10.
6. **Visuals (Compose).**
   - AI plates, cut-outs and lettering layers come from one codex-imagegen `batch` at the canvas aspect, with the text
     zone reserved, no text in the pixels and `--strict` (a zone miss must spend a fix round; `ai-visuals.md` §3).
   - Measure each reserved zone: `analyze --zone`. Calm: type straight on it. Scrim: a gradient scrim. Busy: one solid
     panel (at most 35 % of the photo, never over the subject) or a new plate.
   - Use only the file the batch kept, never a rejected `-c2` or `-raw` candidate (render warns).
   - Client photos go through `analyze`, `reframe` or `cutout`. Icons are SVG (Lucide, Tabler, Phosphor), charts SVG
     from the data, QR codes from `qr`. Flags, maps, monuments and sacred text are never generated.
7. **Build the HTML.** Start from `templates/patterns/` (`templates/README.md`) or from scratch; link
   `templates/kit/cd-kit.css`, then `brand/brand.css`, then the design's own styles (`cd-kit.js` for `data-fit`). One
   grid, margins and the preset's safe zone; a type scale from `craft.md`; `lang` on every run. Build the master
   format first, then re-compose the other sizes in the same HTML (`html[data-preset=…]`). Never just scale. Avoid
   the template tells in `craft.md` (a pill button on every design, awnings, card stacks, a corner-headline-and-footer
   formula, the same layout on every slide).
8. **Render and check.** `render --preset … --out … --overlay --copy copy.json` (`--locale` comes from copy.json;
   `--occasion` for day posts; `--simulate deuteranopia,achromatopsia` when colour carries meaning). Every error is
   fixed: the judge refuses a render with errors. Fix or justify every warning. Text that is not in the copy is an
   error: add it to copy.json or mark a fixed element `data-allow`.
9. **Self-review.** Read the PNG and the overlay at full size, then think at phone size. Run the seven critique tests
   in `craft.md` §8 and name one thing you removed.
10. **Judge.** `judge --image … --brief brief.md --copy copy.json --brand brand/brand.json --kind "…"`, with
    `--runs 3` for hero, client-facing and ad work and the first piece of every series. PASS is the floor,
    PASS_SENIOR the target. With AI stand-in plates the judge usually stops at PASS (imagery and originality 3): say
    so, and name the client photos that will lift it. At most 2 fix rounds, remedies in this order: deterministic fix
    (retype, respace, scrim, swap a plate), a single-scope edit, one new plate, a rebuilt region, and only then a new
    concept. A fix never changes approved copy, the logo or locked tokens. Every change to the file needs a new judge
    run (the verdict is tied to the file's hash).
11. **Export and deliver.** `pack` renders every size; carousels use `--slides N` (LinkedIn gets the slides as a
    PDF); print is a `.pdf` with bleed; `sheet` makes the review sheet. Then `deliver` (level `client` by default):
    it refuses anything whose render report, judge verdict or copy judge does not match the current files, copies the
    finals and the font licences into the delivery folder (an older file there moves to `archive-<time>/`), adds the
    design to the ledger, and writes `DELIVERY.md` with the checks, caption, alt text and notes. Tell the client which
    images are AI, what their real photos will replace, and the AI-label decision.

## 3. Routes (details in `direct.md` §1 and `ai-visuals.md`)

| Route | When | How |
|---|---|---|
| **Compose** (primary) | the default for finals: posts, covers, banners, ads, carousels, print, brand work; dense text, data, charts, QR, legal lines; print with small text; the exact brand font; series, templates and multi-size sets that must match; editable source; Bengali, Hindi and other scripts OCR cannot read; beyond 3:1; Direct exit 4 (use its plate) | text-free AI plates, cut-outs and SVG + HTML type |
| **Direct** (secondary: type-as-image concepts, exploration, challenger) | one canvas between 1:3 and 3:1; at most 8 strings and about 150 characters, each at most 12 words; a few numbers at most; scripts OCR reads (Latin, Cyrillic, Greek, Arabic, CJK); type and picture working together (thumbnails, stories, campaign heroes). On brand-strict finals blind pairwise preferred Compose, so for hero and client finals make both and ship the pairwise winner | dossier, then `direct` (compiled prompt + brand sheet + wireframe + client references, candidates, OCR + a second reader, region repairs, the real logo, judge, one revision) |
| **Hybrid** | a Direct design that also carries exact small print (addresses, hours, prices, legal lines) or a script OCR cannot read | in the dossier, `"route": "typeset"` with a `"zone"`: the model keeps the area calm and `direct` sets the string in HTML with the brand's fonts |
| **Edit** | a client photo stays the hero (image to banner or social) | `analyze`, `reframe`/`cutout`, HTML type, `pack`; the subject is never regenerated |

Logos: AI makes concept sketches at most; the mark is SVG built by Claude, with the wordmark from `outline`.

## 4. Deliverables and budgets (playbooks in `genres.md`)

| Deliverable | Presets | Budget and key rules |
|---|---|---|
| Feed post | `ig-portrait` (cross-post), `ig-3x4`, `ig-square`, `fb-feed`, `li-square`, `x-post` | one message, at most 25 words on the image, headline at least 72 px, the CTA in the caption for organic posts |
| Carousel | `ig-carousel` + `--slides N`; `li-doc` as a PDF | hook slide at most 8 words, one idea per slide, a CTA slide, varied anchors, nothing within 40 px of a cut |
| Story / Reel / TikTok | `ig-story` (organic), `vertical-safe` (cross-platform, ads) | text inside the safe box, a sticker slot, the CTA above the bottom band |
| YouTube thumbnail | `yt-thumbnail` (`--scale 3` for 3840×2160) | 2-4 words, cap height at least 100 px, a face or object at 35-60 %, bottom-right clear, at most 3 people, adds what the title lacks |
| Covers / banners | `yt-banner`, `fb-cover`, `li-profile-cover`, `li-company-cover`, `x-header`, `web-hero`, `email-header` | at most 6 words, the message in the always-visible area, nothing (and no subject) under the avatar |
| Ads | `meta-ad-feed`, `meta-ad-story`, `gads-*`, `iab-*` | exact copy and claims, every size rendered, clean images for Google responsive assets |
| Poster / flyer | `a3-poster` … `poster-24x36`, `a5-flyer`, `a4-flyer`, `dl-flyer`, `letter-flyer` | AIDA, an info block, QR at least 18.5 mm, PDF with bleed, text 3-5 mm inside the trim; `--cmyk` only when the printer refuses RGB |
| Brochure | `trifold-a4`, `trifold-letter`, `bifold-a4` + `--pages 2` | panel order and widths, text 4 mm from folds |
| Business card | `bc-eu`, `bc-us`, `bc-jp` + `--pages 2` | at most 7 lines, at least 7 pt, 100 % black small text |
| Infographic / stat card | `ig-portrait`, `vertical-safe`, `pin-standard`, `deck-16x9` | charts from data in SVG, a source line, the integrity lint |
| Day post | any feed/story preset + `--occasion` | tone class, verified date, one tradition, typeset greeting, no selling on solemn days |
| Logo / brand kit / guidelines | `deck-16x9 --pages 10` for the book | `brand.md` process and system; the book is built from `brand.json` |
| Pinterest pin | `pin-standard`, `pin-square`, `pin-9x16` | a 3-8 word promise, nothing under 60 px, 2:3 (taller gets cut) |
| Blog featured image / link card | `blog-featured` (one master), `og-image`, `x-card` | at most 10 words, type inside x 140-1060 so every CMS crop keeps it |
| Product listing images | `amazon-main`, `shop-square`, `gmc-product`, `daraz-product`, `aplus-*` | main image: product on white, no text; secondary: at most 25 words; eBay, Google, TikTok Shop, Meta and Daraz ban text on every image |
| App store screenshots | `appstore-iphone-69`, `play-phone-screenshot` | frameless real UI, a 2-6 word caption that reads at 115 px, no prices or "Download now" |
| E-book / print book cover | `ebook-master`; the wrap from `bookcover` | the title reads at 94 px; spine from pages and paper; barcode box empty; one ground round the spine |
| Podcast / album / audiobook | `podcast-cover`, `album-cover`, `audiobook-cover` | reads at 55 px; only the name and title on release art |
| Certificate / invitation / cards | `certificate-a4-landscape`, `invite-5x7`, `greeting-a6-folded`, `postcard-4x6` | the name the biggest line; frames well inside the trim; nothing under 8 pt |
| Merch | `tshirt-merch-amazon`, `hoodie-*`, `mug-11oz`, `sticker-redbubble` | transparent PNG (the preset sets it), one phrase, no soft glows |
| Signs, banners, billboards, screens | `banner-3x6ft`, `pvc-banner-bd-3x4ft`, `rollup-850`, `festoon-election-bd`, `billboard-us-bulletin`, `signage-1080p` | the text floor follows the farthest reader (`--view-distance`); billboards and bus sides are scaled files; about 7 words; election pieces follow the local code |
| Image to banner / social | any | `analyze`, then `reframe` or `cutout`, then type, then `pack` |

Everywhere: Latin CTAs at most 4 words and Bengali at most 6; one emoji at most on the image and 3 in a caption;
Bengali, Devanagari and Arabic at 12 px or more at viewing size (about 42 px on a 1080 story, 96 px for a thumbnail
subtitle). Every row has a starting pattern in `templates/README.md`, and the brand book is
`templates/brand/guidelines.html`.

**Unknown size, platform or kind of design** (`references/formats.md`):
1. `presets --find` the client's own words (Banglish and Bangla work: "biye card", "visiting card", "boi er
   prochchhod") and read the preset's notes; a retired format names its replacement (a "YouTube story" becomes
   `yt-shorts-frame` or `yt-post`: say so).
2. No preset: climb the spec ladder (the platform's page, the printer's template, the client's past files, a
   measurement of the live surface) and record the spec as a project preset (`--preset-file`), with source and date.
3. No spec in time: `render --size WxH` with what is known (`--safe`, `--keepout`, `--view-width`, or
   `--view-distance` for signs and screens across a room, with `--legibility-index 30` for a road and `--file-scale`
   for a billboard file built at a scale); whatever is missing is assumed, stated in the report and in the delivery
   note, and told to the client. `presets --nearest WxH` lends the closest preset's zones.
4. An unfamiliar kind of design maps by its job (announce, sell, teach, invite, celebrate, brand, recruit, fundraise,
   compare, warn, direct, entertain) to an anatomy and the closest pattern (`formats.md` §4).

Video and motion: anything delivered as a video (animated posts, reels, stories, intros, HyperFrames or Remotion
renders) goes through the `agy-watch-video` skill before delivery: `qa VIDEO --platform reels --strict` (black and
frozen frames, flicker, loudness, specs, safe zones; exit 2 on a failure), then `watch VIDEO --goal motion --expect
copy.txt` (the approved on-screen lines, each found or not) and `verify` for any finding before you act on it. To
study a reference or competitor video, use `watch VIDEO --goal promo`.

## 5. Non-negotiables

- **Text:** every approved on-image string appears exactly once with real punctuation, and nothing else is written
  (Compose proves it with `--copy`; Direct with OCR, a second reader and repairs). No text in AI pixels except on the
  Direct route, none in plates. Bengali, Devanagari and Arabic are typeset with proper fonts and `lang`, never
  letter-spaced, and read by a native reader.
- **Copy reads human** (`copy.md`): no em dash or spaced en dash anywhere, in any language, even when the client's
  draft has one (propose the dash-free line); no AI or template vocabulary; no translated, calqued, bookish or sadhu
  wording; one call to action; the price printed, not hidden behind "inbox".
- **Craft floor:** clean checks; contrast measured on real pixels; text and logos inside safe zones and off keep-outs,
  seams and folds; logos with their clear space (the mark-to-wordmark gap too), on a calm ground or a plate, reversed
  on dark grounds, never recoloured with a filter; 1-2 families, 3-4 sizes; no AI or template tells (`craft.md` §7).
- **Never two alike:** the recipe passes `ledger`; `deliver --ledger` records every final.
- **Legal and ethics:** no third-party logos, no event marks, no real people without a release, no invented reviews,
  prices or claims, no fake UI, no generated before/after for health; contests carry their terms (`occasions.md` §2).
- **Culture:** day posts follow `occasions.md`; flags, maps, monuments and sacred text come from verified vectors or
  licensed photos.
- **Provenance:** designs with AI visuals carry IPTC `compositeSynthetic` (written by the renderer); photorealistic AI
  people, places or products shown to EU audiences get a visible "AI-generated" label; never fake camera EXIF; never
  strip C2PA from masters.
- **Honesty:** report the image model as codex-imagegen reports it; say which images are AI and what the client must
  replace; generated people are never presented as real staff or customers; report a judge's verdict as it came,
  including a FAIL.

## 6. Core commands

```bash
python3 ~/.claude/skills/codex-design/scripts/design.py doctor
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --copy design/copy.json --brand brand/brand.json
python3 ~/.claude/skills/codex-design/scripts/design.py copyjudge --copy design/copy.json --brief design/brief.md --goal order --runs 3
python3 ~/.claude/skills/codex-design/scripts/design.py ledger --ledger clients/acme/ledger.jsonl --client acme --recipe design/recipe.json
python3 ~/.claude/skills/codex-design/scripts/design.py brand --json brand/brand.json
python3 ~/.claude/skills/codex-design/scripts/design.py analyze --src plates/post.png --zone 0,0,100,40
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/post.html --preset ig-portrait --out out/post.png --overlay --copy design/copy.json
python3 ~/.claude/skills/codex-design/scripts/design.py pack --html design/post.html --presets ig-portrait,ig-square,ig-story,fb-feed --out-dir out --copy design/copy.json --strict
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/carousel.html --preset ig-carousel --slides 6 --out out/carousel.png --copy design/copy.json
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/flyer.html --preset a5-flyer --out out/flyer.pdf --preview
python3 ~/.claude/skills/codex-design/scripts/design.py judge --image out/post.png --brief design/brief.md --copy design/copy.json --brand brand/brand.json --kind "Instagram feed post" --runs 3
python3 ~/.claude/skills/codex-design/scripts/design.py deliver --design out/post.png --copy design/copy.json --out final --ledger clients/acme/ledger.jsonl --recipe design/recipe.json --client acme
python3 ~/.claude/skills/codex-design/scripts/design.py direct --dossier dossiers/post.json --plan
python3 ~/.claude/skills/codex-design/scripts/design.py direct --dossier dossiers/post.json --judge
python3 ~/.claude/skills/codex-design/scripts/design.py verify --image out/post.png --copy design/copy.json --preset ig-portrait
python3 ~/.claude/skills/codex-design/scripts/design.py patch --image out/post.png --extra --copy design/copy.json --instruction "remove the text; continue the background"
python3 ~/.claude/skills/codex-design/scripts/design.py reframe --src client/photo.jpg --presets ig-portrait,ig-story,fb-cover --out-dir out/reframed
python3 ~/.claude/skills/codex-design/scripts/design.py outline --text "Tidewater" --family "Bricolage Grotesque" --weight 800 --out brand/wordmark.svg
python3 ~/.claude/skills/codex-design/scripts/design.py presets --find "biye card"
python3 ~/.claude/skills/codex-design/scripts/design.py presets --nearest 1500x3000
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/kiosk.html --size 1080x1920 --safe 5% --view-distance 3 --screen-height 1.2 --out out/kiosk.png
python3 ~/.claude/skills/codex-design/scripts/design.py bookcover --platform kdp --binding paperback --trim 6x9 --pages 240 --paper cream --preset-file design/book.json
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/cover.html --preset kdp-pb-6x9-240-cream --preset-file design/book.json --out out/cover.pdf --preview
```

## 7. References

- `references/cli.md`: every command, flag, exit code, page variable, kit class, check, judge field, the ledger and
  delivery files, troubleshooting.
- `references/copy.md`: copy that reads human: house rules, AI tells, natural Bangladeshi Bengali (register,
  code-mixing, formal to everyday, calques, Bangladesh vs West Bengal, spelling, digits), transcreation for 12
  languages, hooks, CTAs, captions and platform limits, the copy loop and judge variance, brand voice, accessibility.
  The voice craft is the `natural-copy` skill; its lint rules (932, 24 languages) are `scripts/voice_rules.json`,
  built from `references/research/voice-data/`.
- `references/craft.md`: type floors at display size, the type system, scripts, layout, colour, images in designs,
  template tells to avoid, the ten composition devices, lessons the judges enforced, critique tests, the pre-export
  checklist.
- `references/fonts.md`: pairings by mood; Latin + Bengali, Arabic, Devanagari and CJK tables with size-adjust and
  line-height.
- `references/direct.md`: the Direct route: when, engines, the multi-agent workflow, the dossier, recipes and the
  ledger, type-and-image devices, verification and repairs.
- `references/ai-visuals.md`: plates for Compose (reserved zones, `--strict`, `analyze --zone`), text budget tiers,
  edits, failures.
- `references/formats.md`: the catalogue by family and the common requests; what to do for an unknown size or
  platform (the spec ladder, stated assumptions, screens and print from first principles, the four questions) or an
  unknown kind of design (twelve archetypes); one master into many sizes.
- `references/genres.md`, `styles.md`, `brand.md`, `occasions.md`: playbooks per deliverable, ten style directions,
  brand kits and the book, day posts and legal.
- `references/research/`: the research notes behind these rules (R1 to R11 and the copy research), as evidence.
- `templates/README.md`: the pattern library and the brand-book template.
- `tests/`: `python3 -m unittest discover -s ~/.claude/skills/codex-design/tests` after every change; add
  `CODEX_DESIGN_PATTERNS=1` after changing checks, the kit or a template (renders the whole pattern library).
