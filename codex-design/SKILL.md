---
name: codex-design
description: "Designs finished graphics like a senior human designer, at each platform's exact size: social posts, stories, carousels, pins, thumbnails, covers, banners, ads, blog and product listing images, app screenshots, book and e-book covers, album art, posters, flyers, brochures, cards, certificates, invitations, merch, infographics, day posts, logos, brand kits, signs and billboards, photo resizes; 526 researched formats and a stated method for any unknown size or kind. Use it whenever a request asks to design, make, edit or resize a graphic that carries text or layout, or to write or fix its copy, Banglish asks included ('banner banao', 'post design kore dao', 'biye card'). Prefer it to plain image generation when words go on the image. Copy reads human: no em dash, no AI or translated tells; natural Bangladeshi Bengali and 22 more languages. Compose (primary): real type in HTML/CSS over codex-imagegen plates, rendered by headless Chrome. Direct (secondary): one GPT Image prompt, OCR-verified. Global by default."
allowed-tools: Bash(python3 ~/.claude/skills/codex-design/scripts/design.py:*), Bash(python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py:*), Read, Write, Edit
---

# Codex Design

Claude is the designer: the research, facts, idea, copy and art direction are Claude's. Two routes turn them into
pixels (§3). **Compose is the primary route.** In a blind comparison on 2026-09-24 (four deliverables, Codex and
Claude judges, both orders), Compose won 3 of 4 deliverables and 17 of 24 votes, for the exact brand fonts, one
alignment axis, restraint and an editable, photo-swappable source.

Command prefix: `python3 ~/.claude/skills/codex-design/scripts/design.py` (every flag, check and exit code:
`references/cli.md`). Visuals: `python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py`.
Scope: this skill owns every deliverable with layout or text, and the copy on it; codex-imagegen owns stand-alone
photos and illustrations; website UI belongs to the frontend skills.

## Fast path (every draft: do exactly this)

Most requests are a draft: one post, banner, card or thumbnail for the user, or a first version for a client. Do
it in four steps and about five tool calls, with no judge:

1. **Pick** the preset and the pattern. Presets: `ig-portrait` 1080x1350, `ig-square`, `ig-story` 1080x1920,
   `fb-feed`, `fb-cover`, `li-landscape`, `x-post`, `yt-thumbnail` (`presets --find WORDS` for anything else).
   Patterns in `templates/patterns/`: `post-type.html` (type only), `post-photo.html`, `post-product.html`,
   `story.html`, `carousel.html`, `thumbnail.html`, `ad-banner.html`, `flyer.html`, `poster.html`, `card.html`,
   `invitation.html`, `day-post.html`. The pattern already carries the craft: read no references for a simple piece.
2. **Write** copy.json (the example in §1) and the HTML in one step each: the pattern with your words, and the client's colours
   and fonts set in the page's own `<style>` on `:root` (`--paper`, `--ink`, `--primary`, `--accent`, `--muted`,
   `--font-display`, `--font-text`, `--font-bengali`). The kit ships Bricolage Grotesque, Figtree and Anek Bangla;
   `fonts --family 'Name:400,700' --out design/` fetches any other Google font in one call. Swap or drop the sample
   wordmark.
   Keep the pattern's stylesheet and script links: they load the kit and its fonts. Keep every copy.json string
   whole in one element (a `<span>` around part of a string fails the exact-copy check); give a styled part
   its own string instead.
3. **Render**: `render --html design/post.html --preset ig-portrait --copy copy.json --out out/post.png` (1 to 2 s).
   It checks the picture and lints the copy in the same call (`copy_lint`). Fix what it reports and render again.
4. **Look** at the PNG once with Read, then deliver it. Offer the art-director judge in one line.

A photo in a draft: one codex-imagegen `generate --no-judge` for the plate (about 50 s), started in the background
while you write the HTML; wait for it to finish before you render (in a `claude -p` run, run it in the foreground). Never run `doctor`, read cli.md or open design.py unless a command fails.

**Client work** (the client's final files, anything published under a client's name, or the user asks for the best
or final version): add the gates below: the ledger, judged plates, the design judge (one run while iterating),
copyjudge and `deliver`. The last step is one command, `deliver --judge --brief brief.md …`: it runs both final
judges (3 runs each) at the same time, then every gate. `brief.md` holds only what the client gave (their words,
facts, audience, brand): the judges fail a design on anything in it, so your own photo prompts and notes stay out.
Before designing, check the brief has what the format needs (an event: date, time and place; an offer: the deal and
its dates; a product: the price and where to buy): ask for what is missing, or show it as an agreed placeholder, and
never invent it (a poster with no place failed essentials in every run).
At most two fix rounds after the first verdict; each re-judge sees the last round's fixes. PASS ships, and the
report lists what the judges still want; still REVISE or FAIL after two rounds: stop, and show the user the design,
the verdicts and the notes. Never copy files into the delivery folder by hand: when `deliver` stops, it stays empty.

## 0. Preflight

- Only on a new machine, after an update or when a command fails: `doctor` must say `"ready": true` (it exits 1
  otherwise and lists optional parts that are missing, with what they unlock). `doctor --setup` once per Python
  version builds the skill venv.
- Renders are offline and run with local file access: render only HTML you wrote. `doctor --clean-tmp` clears temp
  folders of killed runs.
- The judges need codex-imagegen and a Codex login (`doctor` shows both).

## 1. Client work: inputs, run times and quick starts

**Inputs, run times and waiting.**

```json
{"locale": "US", "platform": "instagram", "strings": [
 {"role": "headline", "text": "The 36-hour loaf"},
 {"role": "key_fact", "text": "Fresh at 7 am, every day"},
 {"role": "cta", "text": "Order by 9 pm"},
 {"role": "caption", "text": "Our sourdough rests for 36 hours before it bakes. Order by 9 pm for tomorrow."},
 {"role": "alt", "text": "A sourdough loaf cooling on a wooden bench"}]}
```

- That is a whole copy.json. Every string must be on the design exactly once, except the roles that never go on it
  (`caption`, `alt`, `alt_1` and on, `hashtags`, `video_title`) and a string marked `"on_image": false`. Give a
  string in another language its `"lang"` (`"bn"`). A value the client will send later (a phone number, a link) is
  an agreed placeholder: `"placeholder": true` on its string. Print pieces take `"platform": "print"`.
- `--brief` takes a file by its absolute path (the working folder can change between commands) or the brief's text
  in quotes. A path that does not exist stops the command; it is never judged as the brief.
- Run times: `render` and `pack` 1 to 2 s; `judge` about 50 s a run (up to 2.5 min); `copyjudge` about 40 s (60 to 110 s for long Bengali copy or lyrics);
  `--runs 3` about 100 s; `direct` 2 to 7 min. Start judge, copyjudge, pairwise and direct with Bash
  `run_in_background` and keep working (plates, HTML) while they run: a foreground call can hit the Bash tool's
  2 minute limit. `deliver --judge` runs both final judges together (a short Bengali post: 43 s, where the two
  took 43 s and 32 s); it is the last step, so run it in the foreground with a Bash timeout of 600000.
- One run while iterating, three to confirm: judge a draft with one run, and the version you ship with `--runs 3`.
  The same file, brief and settings reuse the saved verdict at no cost.
- The judges and `render` print a short summary. The whole report is in the file named by `report` (or `qa_json`),
  and `--json` prints it.

**Client work: one feed post (any language).**
1. `brief.md` + `copy.json` with `"locale"`, `"platform"`, the on-image strings, a caption and alt text (`copy.md`).
2. `copylint --copy copy.json` (zero errors), then `copyjudge --copy copy.json --brief brief.md --goal order` while
   drafting and `--runs 3` on the final copy (PASS is the floor, PASS_NATIVE the target; fix `fix_first` lines
   first).
3. `ledger --ledger clients/<client>/ledger.jsonl --client <client> --recipe recipe.json` (no `similar`).
4. Plate: codex-imagegen `batch` with `--strict` and the text zone reserved; then
   `analyze --src plates/x.png --zone 0,0,100,40` (calm, or plan a scrim or panel).
5. HTML from `templates/patterns/post-photo.html`; `render --html design/post.html --preset ig-portrait --copy
   copy.json --out out/post.png --overlay` until the checks are clean.
6. `judge --image out/post.png --brief brief.md --copy copy.json --brand brand/brand.json --kind "Instagram post"`,
   fix, re-render, re-judge.
7. `deliver --judge --brief brief.md --kind "Instagram post" --design out/post.png --copy copy.json --brand
   brand/brand.json --out final/ --ledger … --recipe recipe.json --client <client>`: the final design judge and copy
   judge (3 runs each) at the same time, then the gates. When it stops, its `failed` lines carry the judges' fixes.

**A Bengali carousel.** The same, with `--slides 5` on `render`, the judge on `out/<name>-strip.jpg` (it judges
slide by slide), a varied anchor per slide, Bengali at 12 px or more at viewing size, and `alt_1` … `alt_5` in
copy.json. `deliver --design out/<name>-strip.jpg` ships the five slides.

**A client photo to every size.** `analyze` → `reframe --presets ig-portrait,ig-story,fb-cover,li-profile-cover`
(or `cutout`) → one responsive HTML → `pack --presets … --copy copy.json --strict` → judge the master size →
`deliver` every file.

## 2. Workflow

1. **Brief.** Before designing, settle:
   - the deliverables and their presets (`presets --find WORDS`; §4); an unknown size, platform or kind of design
     follows `formats.md`;
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
2. **Copy (`copy.md`)**, before the design, in the reader's everyday language, written with the `natural-text`
   skill (the audience's own words, the register, casual without fake casual):
   - the copy rules under Non-negotiables (§5 below);
   - the market's register, address form, loanwords, spelling and digits;
   - three hooks from three patterns (`copy.md` §5), keep the one a stranger gets in two seconds;
   - one call to action that fits the goal, or none; the action fact (time, deadline, price) as `key_fact` on its
     own line;
   - a caption and alt text for every social piece (roles `caption`, `alt`; they never go on the image).

   `copylint` must end with zero errors (`--lang` for a language the copy.json does not tag). `copyjudge`: PASS is
   the floor, PASS_NATIVE the target for client and hero work, confirmed with `--runs 3` (identical copy spanned 0.18
   in six runs). When the runs disagree the report says to run 5.
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
    run (the verdict is tied to the file's hash); the new run checks last round's fixes instead of starting over.
11. **Export and deliver.** `pack` renders every size; carousels use `--slides N` (LinkedIn gets the slides as a
    PDF); print is a `.pdf` with bleed; `sheet` makes the review sheet. Then `deliver --judge --brief brief.md` (level
    `client` by default): it runs the final judges at the same time (a verdict that already matches is reused), then
    refuses anything whose render report, judge verdict or copy judge does not match the current files, copies the
    finals and the font licences into the delivery folder (an older file there moves to `archive-<time>/`), adds the
    design to the ledger, and writes `DELIVERY.md` with the checks, caption, alt text and notes. Tell the client which
    images are AI, what their real photos will replace, and the AI-label decision.

## 3. Routes (details in `direct.md` §1 and `ai-visuals.md`)

| Route | When | How |
|---|---|---|
| **Compose** (primary; `ai-visuals.md`, `templates/`) | the default for finals: posts, covers, banners, ads, carousels, print, brand work; dense text, data, charts, QR, legal lines; print with small text; the exact brand font; series, templates and multi-size sets that must match; editable source, and designs the client will later drop real photos into; Bengali, Hindi and other scripts OCR cannot read; beyond 3:1; Direct exit 4 (use its plate) | text-free AI plates, the client's photos, cut-outs and SVG + HTML type that `design.py` renders and checks: exact by construction |
| **Direct** (secondary: type-as-image concepts, fast exploration, challenger; `direct.md`) | one canvas between 1:3 and 3:1; at most 8 strings and about 150 characters, each at most 12 words; a few numbers at most; scripts OCR reads (Latin, Cyrillic, Greek, Arabic, CJK); type and picture working together (thumbnails, stories, campaign heroes; it won a story 4-0 with a giant "100% rye"). On brand-strict finals blind pairwise preferred Compose, so for hero and client finals make both and ship the pairwise winner | the brief becomes a dossier, then `direct` (compiled prompt + brand sheet + wireframe + client references, candidates, every word read back by OCR + a second reader, region repairs, the real logo composited, judge, one revision); a run that still fails leaves Compose a text-free plate |
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

**Unknown size, platform or kind of design:** `presets --find` the client's own words first (a retired format names
its replacement: say so), then follow `formats.md`: the spec ladder, a project preset with its source, `render --size`
with every assumption stated to the client, `presets --nearest`, and the twelve archetypes by job.

**Video and motion:** anything delivered as a video goes through the `agy-watch-video` skill's QA before delivery
(`genres.md` §28).

## 5. Non-negotiables

- **Text:** every approved on-image string appears exactly once with real punctuation, and nothing else is written
  (Compose proves it with `--copy`; Direct with OCR, a second reader and repairs). No text in AI pixels except on the
  Direct route, none in plates. Bengali, Devanagari and Arabic are typeset with proper fonts and `lang`, never
  letter-spaced, and read by a native reader.
- **Copy reads human** (`copy.md`): no em dash or spaced en dash anywhere, in any language, even when the client's
  draft has one (propose the dash-free line); no AI or template vocabulary or structures; no translated, calqued,
  poetic, bookish or sadhu wording; no slang, emoji or feelings added to sound human; one call to action; the price
  printed, not hidden behind "inbox".
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

## 6. More commands

The quick starts and the workflow show the everyday commands; these cover the rest.

```bash
python3 ~/.claude/skills/codex-design/scripts/design.py render --html design/flyer.html --preset a5-flyer --out out/flyer.pdf --preview
python3 ~/.claude/skills/codex-design/scripts/design.py direct --dossier dossiers/post.json --plan
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

- `references/cli.md`: every command, flag, exit code, check and report field, the run times, a copy.json example.
- `references/copy.md`: copy that reads human, natural Bangladeshi Bengali, 12 languages, hooks, CTAs and captions;
  the lint's 932 voice rules are `scripts/voice_rules.json`, built from `references/research/voice-data/`.
- `references/craft.md`: type, layout and colour floors, template tells, the ten devices, critique tests, checklist.
- `references/fonts.md`: pairings by mood; Latin with Bengali, Arabic, Devanagari and CJK, with size-adjust.
- `references/direct.md`: the Direct route: the dossier, engines, repairs and the ledger.
- `references/ai-visuals.md`: plates for Compose: reserved zones, `--strict`, `analyze --zone`, edits.
- `references/formats.md`: the 526 presets by family, and any unknown size, platform or kind of design.
- `references/genres.md`, `styles.md`, `brand.md`, `occasions.md`: playbooks and video QA, styles, brand kits, day posts.
- `references/research/`: the research notes behind these rules (R1 to R11 and the copy research), as evidence.
- `templates/README.md`: the pattern library and the brand-book template.
- `tests/`: `python3 -m unittest discover -s ~/.claude/skills/codex-design/tests` after every change; add
  `CODEX_DESIGN_PATTERNS=1` after changing checks, the kit or a template (renders the whole pattern library).
