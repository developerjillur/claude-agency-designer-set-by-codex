# codex-design command reference

The prefix is `python3 ~/.claude/skills/codex-design/scripts/design.py`. Every command prints JSON on stdout (the
`presets` list and `copylint` print one line per item unless `--json`); logs go to stderr. Rendering uses the
installed Google Chrome (or Chromium/Edge; `CODEX_DESIGN_CHROME` overrides) over the DevTools pipe: no npm.

- **Run times** (measured 2026-09-24): `render` and `pack` 1 to 2 s; `judge` about 50 s a run (up to 2.5 min);
  `copyjudge` about 40 s; `--runs 3` about 100 s (up to 3 runs side by side); `direct` 2 to 7 min; `pairwise` runs
  its 2 or 4 votes side by side, each about as long as a judge run. Start the Codex commands (judge, copyjudge,
  pairwise, patch, direct) in the background and keep working. Judge a draft with one run, the version you ship with
  `--runs 3`.
- **Short output:** `render`, `judge` and `copyjudge` print a summary; the whole report is in the file they name
  (`qa_json`, `report`), and `--json` prints it.
- **Text or a file:** `--brief` (judge, copyjudge, pairwise) and `--caption` (copylint, copyjudge, deliver) take a
  file or the text itself. A value that looks like a path (it ends in .md, .txt or .json, starts with /, ~/ or ./, or
  is one word with a slash) must exist, or the command stops with `brief file not found: X (working folder: Y)`. Give
  files by their absolute path: the working folder can change between commands.
- **A copy.json** (the `--copy` file of render, pack, judge, copylint, copyjudge and deliver):

  ```json
  {"locale": "US", "platform": "instagram", "strings": [
   {"role": "headline", "text": "The 36-hour loaf"},
   {"role": "key_fact", "text": "Fresh at 7 am, every day"},
   {"role": "cta", "text": "Order by 9 pm"},
   {"role": "caption", "text": "Our sourdough rests for 36 hours before it bakes. Order by 9 pm for tomorrow."},
   {"role": "alt", "text": "A sourdough loaf cooling on a wooden bench"}]}
  ```

  Each string may also carry `"lang"` (`"bn"`), `"on_image": false` and `"must_exact"`. A plain list of strings or
  `{"role": "text"}` works too. The rules for roles are under `--copy` in "More render flags" below.

- **Offline renders.** Every http(s) and WebSocket request, loopback included, goes to a proxy that does not exist, so
  a design renders the same everywhere and cannot send anything anywhere. Kit links (`https://codex-design.invalid/`)
  are answered from the skill folder. A blocked or missing file is an error in the checks that names the file.
  `--allow-net` lets a page load web resources.
- **Trust.** Pages run with file access (Chrome's `--allow-file-access-from-files`), so a page can read local files.
  Render only HTML that you or this skill wrote, never a page from an untrusted source.
- **Exit codes:** 0 fine; 1 a usage or tool error (one readable line; `CODEX_DESIGN_DEBUG=1` shows the traceback);
  2 a quality gate failed (`--strict` checks, copylint errors, a judge refused over render errors, `deliver`, `ledger
  --strict`, `analyze --zone --strict`); 3 and 4 are the direct route's fallbacks; 130 interrupted; 143 terminated
  (both first end every Codex session the run started, and remove the temporary files).
- **Files are written whole:** each output goes to a temporary file and is renamed into place, and two runs writing the
  same output name are refused (the second exits 1), so a report never describes another run's picture.

## Commands

| Command | Does | Overwrites |
|---|---|---|
| `doctor [--setup] [--clean-tmp]` | Python, Chrome, Pillow (a test render saved through it), presets, codex-imagegen and the Codex login, segno, pypdf, uharfbuzz, fontTools, pdffonts, the Vision helper, and temp folders left by killed runs. `ready` needs Chrome, Pillow and a passing test render (exit 1 otherwise); missing optional parts are listed in `optional_missing` with what they unlock. `--setup` creates the venv for the running Python (`.venv`, or `.venv-3.X` when `.venv` was built by another version) with Pillow, segno, pypdf, uharfbuzz and fontTools. `--clean-tmp` removes run folders whose process is gone and that are over an hour old. | none |
| `presets [--group G] [--find WORDS] [--id ID] [--nearest WxH] [--preset-file F] [--json]` | The canvas catalogue (526 presets; groups social, print, ecommerce, web, signage, app, document, publishing, merch, audio, ads, video, email): size, safe insets, keep-outs with their reasons, viewing width and text floors, byte limit, bleed, folds, source, date and confidence. The list (all, or `--group`) prints one line per preset (id, size, group); `--json` prints every field (361 KB for the whole catalogue). `--find` ranks presets by the words people use (aliases in English, Banglish and Bangla; words match at a word start, so "ebook" is not found in "facebook") and answers a retired format with its replacements; `--id` prints one preset in full; `--nearest` lists the closest aspect ratios to an unknown size (sizes in mm, cm or in compare with print presets). An unknown group is an error; no match logs what to do next (`formats.md`). | none |
| `render --html F --out O (--preset ID \| --size WxH) [--json]` | One design to PNG/JPG/WebP/PDF, with checks. `--size` alone names the presets of that size (they also set a safe zone). Prints the files, the checks and the report's path (`qa_json`); every text item and image is in that report, and `--json` prints them too. With `--copy` it also lints that copy.json (`copy_lint`: errors, warnings and what they found; `--strict` fails on a copy error too), so one render is the whole check of a draft. | `--out` and its `.qa.json`/`.overlay.png` |
| `pack --html F --presets a,b,c --out-dir D [--strict]` | One responsive design on several canvases in one Chrome session, plus a review sheet. An unknown or retired preset stops it before anything renders, with the nearest names or the replacement. | same-named files in `D` |
| `bookcover --platform kdp\|ingram\|lulu [--binding paperback\|hardcover] --trim 6x9 --pages N [--paper cream] [--id ID] [--preset-file F]` | A printed book's flat cover as a preset: the spine from the page count and paper (the KDP and Lulu formulas; IngramSpark's calculator table, interpolated, with a note to confirm), the full canvas with bleed (hardcover: boards, wrap and hinges), the barcode box, the hinge bands, and the whole spine as a keep-out when the page count allows no spine text (KDP under 79 pages, IngramSpark under 48, Lulu 80 or fewer); CSS variables place the panels. `--trim` takes 6x9, 5.5x8.5, 5x8, 7x10, a5, b-format, a4 or WxH in inches. Prints the preset; `--preset-file` writes (or replaces) it there for `render --preset ID --preset-file F`. | the entry in `F` |
| `copylint (--copy C \| --caption T \| --text S) [--role R] [--lang L] [--locale BD] [--platform P] [--brand B] [--strict] [--json]` | Offline lint of copy before it goes on a design (`copy.md`): em and pause dashes (errors), AI and template words and structures, chatbot leftovers (error), bookish, sadhu, translated or calqued Bengali (standard but stiff words are notes), West Bengal words for Bangladesh, honorific mix-ups, Bangla Academy spellings, visarga colons, hidden prices, headline, cover, thumbnail and CTA length (4 words in Latin script, 6 in Bengali), generic CTAs, bait, greeting openers, the caption fold (counted in visible letters), hashtag caps, emoji (1 on the image, 3 in a caption), emoji bullets, per-language punctuation, 𝗯𝗼𝗹𝗱 Unicode letters, a thumbnail that repeats the title, and the brand's avoid list. The voice rules (`scripts/voice_rules.json`: 932 tested rules in 24 languages, plus invisible characters and look-alike letters in any language) run for the line's language: `--lang` or copy.json's `lang`, else the script, else a Latin line's small words. A rule for one market runs only for it (`--locale PT`, or `--lang pt-PT`); headline, alt and casual rules only for those roles; frequency rules only on a repeat. Also: the length X counts (a link 23, an emoji 2: error over 280), Threads' 500, SMS parts, markdown in feeds, "link in bio" where a post can carry the link, thread numbering off X, a reply sent as one block, two colon reveals, two ", not X" tails. `--role`: headline, cta, caption, body, reply, script or voiceover (checks for the ear), alt, or lyric (also song, verse, chorus, mukhra, antara, sanchari, abhog, bridge, poem, jingle): song rules keep the dashes, calques, chatbot leftovers and West Bengal words as findings, make the voice rules and word lists advice (notes), and drop what is the craft of a song (an even rhythm, repeated openings, a refrain, stacked praise, আহা). `--platform` also takes whatsapp, email, web, sms and voiceover. `--brand` adds the brand's avoid and prefer words and never flags its `keep` lines. `--locale` and `--platform` default to copy.json's `"locale"` and `"platform"`. Exit 2 on errors (and on warnings with `--strict`); `--json` prints the whole report. | `<copy>.copylint.json` |
| `copyjudge (--copy C \| --caption T \| --text S) --brief B [--role R] [--lang L] [--locale BD] [--platform P] [--goal G] [--reader R] [--brand B] [--runs N]` | Fresh Codex sessions read the deck as the named reader: ten 0-5 scores (naturalness 20 %, hook 14, clarity 12, specificity 10, register 10, locale 10, cta 8, voice 6, emotion 5, no_ai_tells 5), a natural rating, a problem and a rewrite for every string, the AI tells, stronger hooks and the best CTA. It scores fidelity to the brief first (an invented detail is a defect), does not reward length, and its rewrites, hooks and CTA come back linted (`rewrite_lint`, `hooks_lint`, `cta_lint`). FAIL on any lint error, naturalness ≤ 2, heavy tells or a string ≤ 1; REVISE under 3.6 or any score ≤ 2; PASS ≥ 3.6; PASS_NATIVE ≥ 4.3 with naturalness, locale and hook ≥ 4. `--runs 3` (client work) takes each criterion's median and pools the hooks; when runs disagree or the median sits within 0.10 of a verdict edge the report says to run 5. A run that fails (a timeout, Codex's usage limit) is listed in `runs_failed` with its reason, and the verdict stands on the others: it needs 2 of 3 (3 of 5); fewer stops with Codex's reason. `--timeout 150` per run, retried once; one run takes about 40 s for short English copy and 60 to 110 s for long Bengali copy or lyrics, `--runs 3` about 100 s (up to 3 run in parallel), `--effort medium` is quicker for a draft. `--brief` takes a file or the brief's text itself. Prints a summary: the verdict, scores, each string's rating with its problem and rewrite, hooks, notes, the runs and the report's path; `--json` prints the whole report. Song lyrics (every role a lyric role, see copylint) get a lyricist's rubric instead: song_language 20 %, imagery 16, singability 16, emotion 14, genre_fit 12, hook 10, freshness 7, no_ai_tells 5, no CTA, the songwriter's own lines never rewritten; FAIL on a lint error, song_language ≤ 2, heavy tells or a section ≤ 1; REVISE under 3.6, any score ≤ 2, or song_language or singability under 3; PASS_NATIVE ≥ 4.3 with song_language, genre_fit and singability ≥ 4 (`settings.mode`: `lyric`). The report keeps `deck_sha256`, so `deliver` knows it judged this copy; the same deck, brief and settings reuse its verdict (`--fresh` asks again). | `<copy>.copyjudge.json` |
| `judge --image O --brief B --kind K [--brand B] [--runs N] [--fresh] [--json]` | Independent senior-art-director review (Codex vision) with the renderer's measurements. Refuses (exit 2) while the render report has errors. The same image, brief and settings reuse the verdict already in `<out>.judge.json` (no Codex session; the report says `"cached": true`); `--fresh` asks again. One run takes about 50 s (up to 2.5 min); `--timeout 240` per run, retried once. Prints a summary (verdict, scores, failed gates, fixes, P0 and P1 findings, text differences, notes, runs, the report's path); `--json` prints the whole report. | `<out>.judge.json`; every verdict is also appended to `<out>.judge-history.jsonl` |
| `ledger --ledger L --client C --recipe R [--image I] [--add]` | Never two designs alike, on both routes: the recipe must differ from the client's last 6 designs on 3 of its axes (structure, archetype, focal, device, type mode, palette, finish); the device of the last 3 pieces and a hook close to one of the last 12 are flagged; `--add` records a finished design (refused when too close, unless `--force`); `--list N` prints the last entries. | `L` (appended) |
| `deliver --design F [--design …] --out D --copy C [--caption T] [--level client\|draft] [--facts J] [--ledger L --recipe R --client C]` | The last gate (`--caption` as given to copyjudge: a file, or the text). Each design needs a render report without errors that matches the file (hash), a design-judge PASS or PASS_SENIOR on that exact file, and copy that passes copylint and a copy judge that saw this deck (PASS_NATIVE at `--level client`, the default); `--facts` stops on refuted or needs_client claims; `--ledger` rejects a close repeat and records the design. Then the files (a carousel strip brings its slides, a PDF its pages) and the fonts' licences are copied into `D` with `DELIVERY.md` (checks, caption, alt text, notes) and `delivery.json`. Nothing is copied when a gate fails (exit 2); `--dry-run` only runs the gates. | a file already in `D` is moved to `D/archive-<time>/`, never overwritten |
| `fonts --family 'Inter:400,700' [--family …] --out brand/fonts` | Downloads open-licensed fonts (Fontsource: Google Fonts and more) and writes `fonts.css` with unicode-range rules and `FONT-LICENSES.md`. | files in `--out` |
| `fonts --search WORDS [--subset bengali] [--category serif]` | Lists families (`'*'` for all) with weights, subsets and licence; at most 60 rows (the log says how many matched). | none |
| `brand --json brand/brand.json` | Fonts + `brand.css` (CSS variables for colours, fonts, radius, logo paths). | `brand.css`, `fonts/` |
| `analyze --src photo [--zone x,y,w,h …] [--strict]` | Faces, subject (saliency), the focus box, and calm zones for text with their brightness. `--zone` (percent of the image, repeatable) measures a plate's reserved text zone: `calm` (detail ≤ 8: text straight on it), `scrim` (8 to 15), `busy` (above 15: a solid panel or a new plate), and `subject_covered`. `--strict` exits 2 unless every zone is calm. | none |
| `reframe --src photo --presets a,b,WxH --out-dir D` | Smart crop around faces/subject to every canvas; warns when the subject would be cut or the photo is too small. A misspelled preset stops it before any file is written, with the nearest names. A print preset gets the printer's pixels (its ppi, 300 by default, never upscaled, with the dpi in the file) and a warning when the photo gives less than the print check wants (240 ppi in hand; under 150 the render reports an error). | same-named files |
| `cutout --src photo --out subject.png` | Lifts the subject(s) onto transparency with Apple Vision (macOS 14+, local, instant). | `--out` |
| `qr --data URL --out qr.svg` | QR code (SVG with a viewBox, scales for print; PNG with `--scale`); `--error h` when a logo covers the centre. | `--out` |
| `outline --text T --family F --weight 800 --out wordmark.svg` | Text to SVG outlines shaped by HarfBuzz (kerning, Bengali conjuncts, Arabic joining): wordmarks and print logos with no font dependency. `--font file.ttf` for a licensed font, `--tracking -0.01`. | `--out` |
| `kit --out design --html design/*.html [--sample-brand]` | Copies the kit (and the sample brand) next to the designs and rewrites their `https://codex-design.invalid/` links, so the source opens anywhere. | the kit copy, the HTML links |
| `sheet --src files/folders --out sheet.jpg` | Contact sheet for side-by-side review. | `--out` |
| `direct --dossier D.json [--plan]` | The single-prompt route (`direct.md`): the dossier's copy is linted first (errors stop it, exit 2, unless `--force`), then brand sheet + wireframe + references + one compiled prompt → candidates → OCR verify (second reader for doubtful glyphs) → region repairs → the real logo → final file (→ judge → one revision). Exit 3: beyond 3:1; exit 4: still wrong, with `<id>-plate.png` for composing. | files in `<dossier dir>/direct/<id>/`, `ledger.jsonl` (appended) |
| `verify --image I --copy C [--preset P] [--brand B] [--allow a,b] [--strict]` | A raster design's text read back (Apple Vision, three scales) against the copy: missing, altered, repeated, case, punctuation, extra; an em dash or spaced en dash in what the picture says (an image model adds them); safe zone, keep-outs and size at viewing width. Off-image roles (captions, alt text) are skipped. | `<image>.verify.json`, `<image>.verify.png` |
| `patch --image I --instruction T (--box x,y,w,h \| --point x,y[,r] \| --find TEXT \| --extra --copy C)` | Changes only the pointed-at regions and composites them back (pixel-exact outside). `--timeout 240` per edit session (codex-imagegen retries a failed one once); an edit that times out or makes no image stops with one line. | `--out` (default `<image>-patched.png`) |
| `pairwise --a X --b Y [--brief B --copy C] [--kind K] [--out votes.json]` | Blind A/B choice by fresh Codex sessions in both orders (and client + blind modes with a brief): a side wins only when it wins after the swap too; reports the position bias. For direction rounds and before/after checks. `--timeout 300` per vote, asked once more on a timeout or a broken answer. Fewer than 2 votes that answer is an error with Codex's reason (exit 1), never a tie; failed votes are listed in `votes_failed`. | `--out` |
| `ocr --src I [--langs en-US,ar-SA] [--correct]` | Apple Vision lines and words with boxes and alternative readings. | none |
| `refsheet --brand brand.json --out sheet.png [--for-model]` | The brand on one reference image; `--for-model` drops the logo and every word (what `direct` attaches). | `--out` |
| `sketch --zones JSON --preset P --out sketch.png` | A labelled layout sketch for people (the direct route draws its own label-free wireframe). | `--out` |

## render / pack flags

- `--preset ID` or `--size 1080x1350` / `210mmx297mm` / `8.5inx11in`; print canvases take `--bleed 3mm` (presets carry their own).
- `--scale N`: device scale (2 = retina). Print rasters default to 300 dpi (`scale = 300/96`), are cropped to the exact pixel size and carry the dpi.
- `--out` extension picks the format: `.png` (lossless, alpha), `.jpg` (`--quality`, default 90, 4:4:4 at ≥ 90), `.webp`, `.pdf`.
- PDF: vector text and shapes; Chrome prints 1 mm oversize, then the MediaBox is cropped exactly and the BleedBox/TrimBox are set (pypdf). sRGB, which most printers convert themselves; label it "print-ready RGB PDF", never PDF/X.
- `--cmyk [ICC]` (print presets, `.pdf`): also writes `<out>.cmyk.pdf`, the 300 ppi render converted to the printer's CMYK profile (relative colorimetric, black point compensation; default the macOS Generic CMYK profile, better the printer's FOGRA/GRACoL file). Text becomes pixels and black becomes four-colour, so send it only when the printer refuses RGB.
- `--slides N`: the page is N canvases wide (carousel). Writes `<out>-01…N` plus `<out>-strip.jpg`; with `.pdf` it writes one page per slide (LinkedIn document post). Slide or page files left by an earlier render with more slides are reported, never deleted.
- `--preview` with `.pdf`: also writes `<out>.preview.png` (its own name, so a 300 dpi `<out>.png` beside it is safe).
- `--locale BD`: the market for the Bengali word checks on rendered text (default: copy.json's `"locale"`; without one the West Bengal and Bangladesh word checks stay off).
- `--allow-net`: let the page load http(s) resources (renders are offline by default). `--timeout 60`: seconds to load and settle; a page that does not load names what it still waits for, or says a script is busy.
- Size limits: one page may be at most 8192×8192 CSS px (Chrome paints larger pages blank; design smaller and raise `--scale`, or use a print preset), and a raster at most 400 MP (write a `.pdf` beyond it). Big canvases are captured in tiles that are each compared with a small capture of the whole page; an unpainted tile is captured again, and the run stops rather than write a file with a blank patch.
- `--transparent`: transparent page background (PNG/WebP). A preset with `"transparent": true` (garments, stickers,
  embroidery) does this by itself for PNG and WebP; a JPG keeps the page's own background.
- `--preset-file F` (repeatable; `CODEX_DESIGN_PRESETS` holds a path list for every command): a project's or a
  client's presets, as a list or `{"presets": [...], "retired": [...]}`; each needs `id`, `w` and `h`; later files win,
  and an entry with a skill preset's id replaces it (a client's correction). `render`, `pack`, `presets`, `verify`,
  `reframe` and `sketch` read it.
- **A size without a spec** (`--size WxH`) takes what is known: `--safe 40`, `--safe 40,40,120,40` (top, right,
  bottom, left), `--safe 5%` or, for print, `--safe 5mm`; `--keepout x0,y0,x1,y1` (canvas px, repeatable);
  `--view-width 390` (CSS px it is seen at); `--min-text 30` (canvas px); `--view-distance 3` (metres) with
  `--screen-height 1.2` (metres) for screens across a room. What stays missing is assumed and **stated**: a 5 %
  safe margin, a 390 px phone view (not when a distance is given), 11 px at that view; print gets no bleed unless
  `--bleed`. The assumptions go to `canvas.assumed` and `source.assumed` in the report, a warning, and a note in
  `DELIVERY.md`. The same flags refine a preset (a printer's safe margin, a client's keep-out).
- **Distance floors:** printed text read on foot follows ADA 2010 §703.5.5 (capitals 16 mm up to 1.83 m plus 10.5 mm
  per metre beyond; font size about capitals / 0.7); text read in passing from a road (billboards, bus sides, roadside
  screens) follows the legibility index with `--legibility-index 30` (USSC, MUTCD: capitals = distance x 83.33 / LI
  mm); a screen in a room follows AVIXA DISCAS (characters the distance / 200 tall on a screen of `--screen-height`).
  `--file-scale N` says the artwork file is 1/N of the real object (24 for a bulletin at 1/2 in = 1 ft), so the floor
  is divided by N. The floor is raised, recorded as `distance_floor`, and named in the size warning; placed images are
  checked against `ppi = 87.3 / metres` on the real object (never under 10), times the file scale, at most 240; in
  hand 240, or the preset's own lower figure (posters and roll-ups 150).
- `--max-bytes N`: JPG/WebP quality drops in steps of 5 until the file fits (presets such as `yt-thumbnail` carry a limit).
- `--overlay`: also writes `<out>.overlay.png` (safe zone cyan, bleed magenta, text boxes green/amber/red).
- `--strict`: exit 2 when a check fails. `--no-qa` skips the checks.
- `pack` takes `--copy`, `--locale`, `--occasion`, `--overlay`, `--simulate`, `--allow-net`, `--timeout`, `--strict` and `--format png|jpg|webp` for every size.
- `<out>.qa.json` records where it came from in `source`: the HTML and its sha256, the preset, the locale, every file written with its sha256, whether a generated visual is in it, the time, the skill and Chrome versions. `judge` and `deliver` use the hashes to refuse a report that belongs to another render.
- Every report records the Chrome version that rendered it (`chrome`): rendering can change between releases.

## What the page receives

The renderer sets these before the page loads, so one HTML file can adapt to every canvas:

- CSS variables on `<html>`: `--canvas-w`, `--canvas-h`, `--slides`, `--pages`, `--bleed`, `--safe-top`, `--safe-right`, `--safe-bottom`, `--safe-left`, and `--min-text` (the canvas's text floor in px, raised by a reading distance: `font-size: max(…, var(--min-text))` keeps a line above it). Also `--label-min` (the floor for labels, dates and captions: 34/30 of `--min-text` where the platform shrinks the canvas, the same elsewhere) and `--view-scale` (canvas width ÷ viewing width, 0 in print), which brand.css turns into `--mark-min` and `--wordmark-min`.
  Print canvases are laid out at the next whole CSS pixel (Chrome paints boxes on whole pixels); the fraction lands in the bleed and the exact trim is cut afterwards.
- `html[data-preset="ig-story"]` for per-format rules; media queries on width, height and aspect-ratio also work.
- `window.__CD = {safe, preset, slides, pages}`.
- A preset's own `css_vars` (lower-case custom-property names; plain values of letters, digits, `.`, `%`, `#`, commas, spaces and parentheses; anything else stops the render): a book wrap
  from `bookcover` passes `--back-x`, `--board-w`, `--spine-x`, `--spine-w`, `--front-x`, `--wrap`, `--hinge`,
  `--spine-margin`, `--text-safe` and `--spine-text` (1 or 0), so one HTML lays out any page count
  (`templates/patterns/book-cover.html`).
- It waits for web fonts, images, and `window.__cdReady` before capturing. A page that builds its content in a script
  (charts, the brand book) assigns its own promise to `window.__cdReady` and calls `window.__cdFit()` when done.

## Preset fields

A preset (in `scripts/presets.json` or a project file) is one JSON object:

| Field | Meaning |
|---|---|
| `id`, `group`, `label`, `platform`, `aliases` | the name used on the command line (kebab case; dots only inside numbers, `book-5.5x8.5`), its family, a readable label, and the words people use for it (English, Banglish, Bangla), which `--find` searches |
| `w`, `h` | pixels for screens (`1080`), physical units for print (`210mm`, `8.5in`); `print: true` marks a physical page |
| `safe` / `safe_mm` | screens: top, right, bottom, left in canvas px; print: mm inside the trim |
| `keepout`, `keepout_why` | rectangles `[x0, y0, x1, y1]` in canvas px (print: from the trim's top-left) where the platform draws UI or the printer forbids art, and a reason per rectangle for the check's message |
| `bleed`, `ppi`, `folds_mm`, `fold_gap_mm` | print: bleed per edge, target resolution, fold positions per side (`[[outside], [inside]]`, mm from the left trim edge), and the clearance from a fold (4 mm by default; a book spine uses its margin) |
| `view_width_px`, `thumb_width_px` | the CSS width it is seen at, and the smallest width it is listed at (search results); the judge shows both |
| `min_text_px`, `large_text_px` | the text floor on the canvas and the size from which the 3:1 contrast rule applies |
| `view_distance_m`, `screen_height_m`, `legibility_index`, `file_scale` | read from a distance: the floor follows the distance (see the render flags); signs read in passing carry a legibility index; billboard and bus files built at a scale carry it |
| `transparent`, `css_vars` | render on a transparent ground; CSS variables the page receives |
| `max_bytes`, `formats`, `min_size`, `max_size`, `text_allowed`, `background_rule` | the platform's file rules |
| `source`, `source_date`, `verified`, `confidence`, `notes`, `source_notes` | where the numbers come from (official, widely cited, practice, estimate), when they were checked, what to watch for, and the research note behind them |

A `retired` entry (`id`, `label`, `retired` date, `use` list, `source`, `notes`) answers a closed format with its
replacements (`presets --find "youtube story"`, and `--preset yt-story` stops with the same message).

## The kit (`templates/kit/`)

Link `cd-kit.css` first, then `brand.css`, then the design's own styles; add `cd-kit.js` for text fitting.

- Canvas: `.canvas` / `.slide` (one canvas), `.track` (carousel row), `.page` (one page of a `--pages N` document; each is captured on its own), `.safe`, `.bleedbox`, `.trimbox`, `--print-black` (#000 for small print text).
- Images: `.fill` (object-fit cover), `.scrim-bottom`, `.scrim-top`, `.grain` (SVG noise overlay, `--grain` opacity).
- Type: `.balance`, `.pretty`, `.nums` (tabular lining figures), `.caps`, `.cap-trim` (text-box trim), `.nowrap`.
- Fitting: `<h1 data-fit="56,140" data-fit-lines="2">` takes the largest size that fits its box (every line inside the box, so bottom-aligned text cannot creep upwards); `data-fit="56"` uses the CSS size as the maximum; a value can be a share of the CSS size (`data-fit="60%"`) or `floor`, the canvas's text floor (`data-fit="floor"`), so one pattern fits canvases of any size; if even the minimum does not fit, the check reports an error.
- Logos: `.logo`, `.wordmark`, `.logo-mark`, `data-logo` (or an `<img>` whose file or alt says logo) get the clear-space check.
- `class="show-grid"` on `<body>` draws a 12-column grid inside the safe area while designing (remove before delivery).

## Checks (in `checks` and `<out>.qa.json`)

| Check | Level | Meaning |
|---|---|---|
| clipped / off-canvas / fit-failed | error | text is cut off or cannot fit (per slide and per page) |
| failed to load | error | a CSS, script, font or image file is missing, or a web resource was blocked because renders are offline; the message names the file |
| `.page` blocks on one canvas | error | a document with N `.page` blocks rendered without `--pages N` (the clipping errors that follow come from that) |
| hidden under an element | error | part of a letter is covered by something that paints (the report names it); transparent layout boxes do not count |
| font missing | error | a font did not load for that weight/style/text; a fallback was drawn |
| contrast below the need | error | needs 4.5:1, or 3:1 for large text (`large_text_px` of the preset; bold counts from 80 %) |
| a word on a darker or busier patch | warning / error | the text reads as a whole, but one word-sized piece of a line sits where contrast drops below the need (a headline running onto a shelf, a face, a bright window) |
| outside-safe | error | inside the canvas but outside the preset's safe zone (platform UI, trimming) |
| keep-out zone | error | text or a logo where the platform draws its UI inside the canvas (YouTube duration badge, profile photos on covers), or a print keep-out (a book's barcode box and hinges, the spine when the page count allows no spine text); the message names the preset's reason (`keepout_why`) |
| detail under a keep-out zone | warning | the picture is detailed where the avatar or badge will sit: if that is the subject, reframe |
| line or shape behind the letters | warning | on a flat ground, a stroke, shape or colour edge runs through a line of text (contrast alone misses it) |
| logo clear space | warning | text, or a graphic edge, within half the logo's height around it |
| logo on a detailed part of the image | error | move it to a calm area, onto a solid band, or put a plate behind it |
| logo recoloured with a CSS filter | warning | invert, hue-rotate and the like instead of the supplied variant (drop shadows are fine) |
| logo too small at viewing size | error | a mark under 16 px (a wordmark under 10 px tall) at the preset's viewing width; enlarge it or leave it to the platform avatar |
| plate notes | warning | the photo plate is a candidate the image judge rejected (`-c2`, `-raw`), or the judge flagged it (FAIL, or major defects such as a busy text zone), read from its `.meta.json` |
| spills | warning | text is wider than its box (overflow visible) |
| below minimum size | warning | smaller than the preset's `min_text_px`; with a viewing distance the floor comes from the distance and the message says so |
| em dash, `--`, spaced en dash | error | readers take them as AI-written copy; an en dash stays only between two numbers in Latin text (10–12); Bengali ranges are ১০-১২ or ১০ থেকে ১২ |
| en dash between words, spaced hyphen | warning | write 'to' (Tuesday to Sunday), or rewrite with a comma or a colon |
| bookish, translated or West Bengal Bengali | warning | on rendered text that is not in the approved copy; `copylint` checks the deck earlier (`copy.md` §3) |
| script fallback | warning | e.g. Bengali text in a font without Bengali glyphs (a system font draws it) |
| dense script too small | error | Bengali, Devanagari or Arabic text under 12 px at the preset's viewing width (≈ 34 px on a 1080 story or post, 37 px on a 1200 LinkedIn image, 77 px on a thumbnail) |
| > 3 font families | warning | professional sets use 1–2 |
| upscaled image > 1.25x / broken image | warning / error | soft pixels / not loaded |
| placeholder text | error | lorem ipsum, TODO, "your text here", [insert …], xxx |
| approved copy missing / altered | error | with `--copy`; a string split over inline elements (`The <em>36-hour</em> loaf`) counts as one |
| text that is not in the approved copy | error | with `--copy`; add it to copy.json, or mark a fixed element (a slide counter) `data-allow`; text inside a logo element is allowed |
| case-only difference, repeated string | warning | with `--copy` |
| letter-spacing on Bengali / Devanagari / Arabic | warning | breaks conjuncts, the headline stroke and joins |
| line-height `normal` or too tight | warning | set it explicitly; scripts need more (display ≥ 1.25, body ≥ 1.45) |
| headline runt | warning | a 2+-line headline whose last line is under 25 % of the longest; a two-line text ending in one short word |
| compound broken at its hyphen | warning | display text wrapping "36-" / "hour"; use a non-breaking hyphen or `white-space: nowrap` |
| text overlaps text | warning | boxes overlapping by more than 8 % of the smaller one |
| text on a carousel seam | warning | within 40 px of a cut between slides |
| text near a fold | warning | within 4 mm of a brochure fold (the folds come from the preset, per side), or within the spine margin of a book's spine (`fold_gap_mm`) |
| colour change on a fold | warning | the ground changes colour within 3 mm of a fold or a spine edge: folds and spines drift up to 1.6 mm, so a sliver of the wrong colour shows; carry one colour across, or move the change 3 mm onto a panel |
| occasion words / selling | error | with `--occasion solemn`: Happy, Congratulations, Mubarak, শুভ, "!", celebration emoji, prices, offers, CTAs; `fast`: Happy/celebrate |
| more than 5 sizes / two sizes within 12 % | warning | an unclear hierarchy; carousels are judged slide by slide, documents page by page, and a folded sheet or a book wrap panel by panel (a spine and a front are never seen together) |
| custom size | warning | a `--size` render without a spec: names the safe margin, viewing width and text floor that were assumed |
| tracking below −0.04 em, thin weight at small size | warning | collisions / weak strokes |
| straight quotes, "..." | warning | typeset ’ “ ” … (a spaced hyphen is a dash: see the dash rows) |
| generic marketing phrase | warning | game-changing, seamlessly, elevate, unleash … (not in the client's approved copy) |
| print: small near-black text | warning | dark grey under 12 pt prints in four inks and blurs; use #000 (`--print-black`) |
| print: small reversed text | warning | light text under 9 pt in a light weight on colour fills in on press |
| print: image resolution | warning / error | under 240 ppi at its printed size / under 150 ppi |
| PDF fonts | warning | not embedded, or Type 3 in a print PDF (variable, CFF or restricted fonts, blurred text-shadows, faux bold); use static TrueType web fonts |
| PDF page count | warning | a `--pages N` document that printed to a different number of pages |

Contrast is measured on pixels: the page is captured a second time with the text hidden, and each line's ink band
(measured from the font's real ascent and descent for that text) is compared with what really sits behind it (10th
percentile), so text over photos is measured honestly. The cut, safe-zone and overlap checks use the same measured ink,
so tall scripts such as Bengali are not flagged for their font's generous line box. Mark a purely decorative text (a
giant background word) or a deliberate specimen (a failing pair in a brand book) with `data-qa-ignore`.

## Provenance

A design that shows a generated visual (C2PA, IPTC tag or a codex-imagegen sidecar on any `file:` image) is written with
IPTC `DigitalSourceType = compositeSynthetic` ("several elements, at least one generative AI"; PNG iTXt XMP, JPG/WebP XMP). Designs without
generated visuals are not tagged. Never add fake camera EXIF.

## judge

`judge --image post.png --brief brief.md --copy copy.json --brand brand/brand.json --kind "Instagram feed post"
--canvas "4:5 1080x1350" [--runs 3] [--route hybrid|full-ai] [--print] [--effort high] [--plate-meta P.meta.json]
[--force]`:

- **Render errors first.** When the design's `.qa.json` has errors the judge refuses (exit 2) and names the first:
  the judge fails those anyway, so fix them before spending a run. `--force` judges regardless. A `.qa.json` whose
  file hashes do not include the image is ignored (a note says so).
- `--brand` puts the brand's names on the allowed-text list (the wordmark) and its supplied logo files, logo rules,
  colours, fonts and motif into the brief: a variant that was never supplied, a recoloured logo or a motif in the wrong
  colour fails the brand gate there.
- The plates' image-judge notes (from each plate's `.meta.json`, found automatically, or `--plate-meta`) go into the
  brief, so the judge checks whether the design suffers from them.
- `--runs 3` (client and hero work): independent sessions, each criterion's median, a gate fails only when most runs
  fail it, a P0 finding counts only when most runs raise one; `runs` lists each run's verdict. A run that fails is
  listed in `runs_failed` with its reason and the verdict stands on the others; it needs 2 of 3 (3 of 5), and fewer
  stops with Codex's reason. Every verdict is also appended to `<image>.judge-history.jsonl`, and `image_sha256` ties
  it to the exact file.
- The brief is cut at 9,000 characters (a log line says so); the approved copy, brand facts and plate notes that
  follow it always reach the judge in full.

- A fresh read-only Codex session sees three images: the design at full size, a copy at viewing size (the preset's
  `view_width_px` recorded in the render report; otherwise 390 px wide, 168 px for thumbnails; none with `--print`) and
  a grey, blurred copy (squint test). A format that is listed smaller than it is viewed (`thumb_width_px`: e-books in
  search results at 94 px) adds one more copy at that size: the title and the main shape must read there. It also gets the brief, the
  approved copy and the renderer's measurements (`.qa.json`); it never judges exact colours, fonts or spacing by eye.
- **10 hard gates** (any FAIL = FAIL): `text_accuracy`, `script_rendering`, `legibility`, `clipping_collision`,
  `format_fit`, `brand`, `ai_artifacts`, `rights_ethics`, `essentials_present`, `technical_quality`. Case set by
  styling is not a text change.
- **10 weighted criteria, 0–5**: message_fit 15 %, hierarchy 15 %, typography 15 %, layout 10 %, colour 10 %,
  imagery 10 %, brand_consistency 10 %, originality 5 %, finish 5 %, platform_fit 5 %.
- **Verdict** (computed here): FAIL = a gate, a criterion ≤ 1 or a P0 finding; REVISE = weighted < 3.5, a criterion
  at 2, or message/hierarchy/typography < 3; PASS = weighted ≥ 3.5 with every criterion ≥ 3; PASS_SENIOR = weighted
  ≥ 4.2 with message, hierarchy and typography ≥ 4 (the target for client and hero work).
- **A carousel strip** (`<out>-strip.jpg`, found with `<out>.qa.json`) is shown slide by slide at phone width in Image 2, so
  legibility is judged per slide; scaled to one phone width, a 5-slide strip gave each slide 78 px and failed.
- **Output** `<image>.judge.json`: `two_second_read`, `reading_flow`, `text_read`, `gates` + `gate_evidence`,
  `scores`, `ai_tells`, `findings` (P0–P3, element, before, after, why), `fixes` (≤ 5, in fix order), `keep`,
  `disposition` (ship / fix / rebuild / recapture), `weighted`, `verdict`.
- With `--copy`, `text_diff` compares what the judge read with the approved Latin strings (lines read separately are
  joined; Bengali, Arabic and other Indic scripts need a native reader). With `--route full-ai` (text drawn by the image
  model) any difference fails `text_accuracy`. Without `--copy` the judge checks spelling, names and numbers against the
  brief only; put real URLs and facts in the brief so it does not treat them as placeholders.

## More render flags

- `--copy copy.json`: every on-image string must appear exactly once in the rendered text; missing strings and text
  that is not in the copy are errors; case-only differences and repeats are warnings. Formats: a list of strings,
  `{"role": "text"}`, or `{"locale": "BD", "platform": "instagram", "strings": [{"role", "text", "lang",
  "must_exact", "repeat", "on_image"}]}`. A malformed file (a string where a list belongs, a number as text, no
  strings) is an error.
  - Roles that never appear on the design are skipped by render, judge, pairwise and verify but kept for copylint,
    copyjudge and deliver: `caption`, `post_text`, `body_long`, `alt` / `alt_text` (also `alt_1`, `alt_2` for slides),
    `video_title` (the YouTube title; the thumbnail check compares it with the `thumb` text), `hashtags`,
    `first_comment`. Any other string can opt out with `"on_image": false`.
  - `"role": "key_fact"` marks the action fact (time, deadline, price) that gets its own line (`craft.md`).
- `--simulate deuteranopia,achromatopsia,blurredVision` (also protanopia, tritanopia, reducedContrast): writes
  `<out>.sim-<kind>.png` for colour-blind, grey-value and squint checks.
- `--pages N`: a document of N stacked canvases (`.page` elements with `break-after: page`): the PDF gets N vector
  pages with exact boxes; PNG/JPG writes `<out>-p01…N`, each page captured on its own at its exact size.
- Every raster carries an embedded sRGB profile; print rasters carry their dpi; every PDF reports its fonts
  (`fonts.types`, `fonts.not_embedded` and `fonts.type3` must be clean, via Poppler's `pdffonts` when installed).
- Photos: `analyze`, `reframe` and `cutout` apply the EXIF orientation first, so a phone photo stored sideways is
  measured and cropped as it is seen.

## fonts: sizing a second script

`--family "Noto Sans Bengali:400,700@110"` adds `size-adjust: 110%` to that face, so its headline stroke lines up with
the Latin partner (the percentages per pairing are in `fonts.md`). For text in that script put its family first
(`font-family: var(--font-bengali)`): the script check reads the first family, so a Latin-first stack is reported as a
fallback. Wrap Latin words inside such a line in a span with the Latin family; `unicode-range` makes each file draw
only its own script.

## Environment

| Variable | Effect |
|---|---|
| `CODEX_DESIGN_CHROME` | Chrome/Chromium/Edge binary |
| `CODEX_DESIGN_CACHE` | cache root (fonts, Vision helper); default `~/.cache/codex-design` |
| `CODEX_DESIGN_KEEP_TMP=1` | keep the temporary run folder |
| `CODEX_DESIGN_DEBUG=1` | show the Python traceback instead of the one-line error |
| `CODEX_IMAGEGEN_SCRIPT` | path to `codex_image.py` (AI visuals, judge plumbing) |
| `CODEX_DESIGN_PRESETS` | extra preset files, separated by `:` (a client's or project's verified specs; `--preset-file` adds more) |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Google Chrome ... not found` | install Chrome or set `CODEX_DESIGN_CHROME` |
| `this command needs Pillow` | `doctor --setup` |
| `font '…' is not available` | run `fonts`/`brand`, link `fonts.css`, and use the weight you downloaded |
| `script fallback: bengali` | put the Bengali family first for that text (`font-family: var(--font-bengali)`) |
| `pdf_boxes: Chrome page size …` | `doctor --setup` (pypdf) for exact boxes |
| QR text reported as too small to scan | print it at least 2 cm wide with a 4-module quiet zone |
| `Type 3 fonts in a print PDF` | the text uses a system or variable font: install static web fonts with `fonts`/`brand`, drop blurred text-shadows on print |
| `hidden under div.x` | that element paints over the letters: move it, lower its z-index, or give the text its own layer |
| `a line … runs behind the letters` | a stroke or shape crosses the text: move one of them so every letter sits on one ground |
| `vision … unavailable` | macOS 14+ with Xcode command line tools; otherwise analyze/reframe use the centre, ocr and verify do not run, and cutout needs codex-imagegen |
| `failed to load … blocked: renders are offline` | download the font with `fonts`, keep images in the project, or pass `--allow-net` |
| `… did not finish loading in 60s` | the message names the request it waits for, or a busy script; fix the page or raise `--timeout` |
| `another codex-design run is writing …` | two runs on one output name: wait, or choose another `--out` |
| `the page is … CSS px` / `unpainted tile` | the page is too big for Chrome: design smaller and raise `--scale`, use a print preset, or render fewer slides |
| `the render found N error(s) the judge would fail` | fix the render errors first (or `judge --force`) |
| `brief file not found: X (working folder: Y)` | the value looks like a path and no file is there: give the file's absolute path, or pass the brief's text itself in quotes |
| `only N of 3 … runs answered (2 needed): …` / `pairwise: only N of … votes answered` | the reason after the colon is Codex's own (a usage limit, a login, a timeout): wait and run it again, or `codex login` |
| `unknown preset 'X'; did you mean …` | use one of the names given, or `presets --find WORDS` |
| `not delivered: N gate(s) failed` | the report lists each gate: re-render, re-judge (the file changed), run copyjudge again (the copy changed), or fix the copy |
| a Python 3.X venv problem | `doctor --setup` builds `.venv-3.X` for that Python; the first `.venv` is kept |

## direct flags and outputs

- `--dossier D.json` (fields in `direct.md` §4); paths inside it are relative to its folder.
- `--plan`: build the references and the prompt, run every check (fact blockers, ledger, text budget, proof slot, copy
  size floors, trust-sector people), write `prompt.txt` and `plan.json`, print them, stop. Read the plan's
  `safe_area_pct` before writing zones.
- `--engine auto|codex|api` (auto = API when an OpenAI key is in the keychain), `--model gpt-image-2.5-sunburst`,
  `--quality xhigh` (API only).
- `--variants 2` candidates per attempt; `--tries 2` attempts (a retry names the last attempt's mistakes);
  `--repair-rounds 2`; `--judge` + `--revise 1` (regenerate with the judge's notes on REVISE or FAIL, keep the better).
- `--retypeset`: set the dossier's typeset copy again over the kept `<id>-picture.png` (a changed price, date,
  address or hours): no generation, the renderer's checks and OCR run again.
- `--out final.jpg` also sets the format (a byte limit lowers JPG/WebP quality); `--out-dir`, `--ledger`, `--refresh`
  (rebuild the brand sheet), `--no-plate`, `--force` (past blocking facts or a repeated concept).
- `--timeout 240`: seconds per Codex session, for the generation, each edit and the judge (each takes about 50 s and
  is retried once, so a step waits at most twice that plus 2 min). An attempt or an edit that times out costs that
  attempt or that repair, not the run; its reason is in the report.
- Outputs in the run folder:
  - `prompt.txt`, `plan.json`, `copy.json`, `brief.md` and `refs/` (the brand sheet and wireframe);
  - `prompt-r<n>a<k>.txt` and `gen-r<n>a<k>/` (the raw candidates and their Codex logs);
  - the cropped candidates with `.verify.json` and `.verify.png`, and the `repair-r<n>-*.png` files;
  - one final per round, `<id>-r<n>.png` with `<id>-r<n>-master.png`;
  - the chosen `<id>.png` and `<id>-master.png`, and the report `<id>.direct.json` (rounds, attempts, crops, repairs,
    logo, verify, judge, timings).

## verify statuses

`exact` · `case` / `punctuation` / `case_punctuation` (warnings) · `mark_added` (warning: OCR invents ® on serif
terminals) · `ambiguous` (a second Vision reading spells it right) · `confirmed` (Vision misread it, a blind second
reader reads it exactly: a warning to look at once) · `altered` / `missing` (errors) · extra runs: `text nobody
approved` (error), `text repeated` (a duplicate of an approved string, error), a one-letter stray mark (warning).
Latin copy reads Cyrillic and Greek look-alikes as Latin (a condensed "rye" comes back as "гуe").

## patch flags

- `--mode auto|crop|full`:
  - `crop` edits a close-up window, grown to an aspect the model makes, so the text gets more pixels;
  - `full` edits the whole image with the regions marked;
  - `auto` crops when the regions cover under a third of the image.
- `--pad 0.5` (a share of the line height) and `--protect x,y,w,h` (approved words are protected automatically with
  `--extra`).
- `--engine codex|api`: the API engine also sends an alpha mask; `--model`, `--quality`.
- Report fields:
  - `pointer_colour`: a hue the design does not use, so a leak can be seen;
  - `annotation_leak`: true when that hue appears in the edit, which is then rejected;
  - `alignment`: shift and scale found on the unchanged area;
  - `outside_changed_px` (0 by construction), `change_inside` and `text_now_in_boxes`.

## ledger and deliver

`recipe.json` (the same axes as a dossier's `recipe`, `direct.md` §6):

```json
{"id": "tokjhal-rain-post", "deliverable": "facebook post", "preset": "ig-portrait",
 "structure": "full-bleed photo, type band at the top", "archetype": "weather forecast", "focal": "the bowl",
 "device": "borrowed format", "type_mode": "display Bengali + tabular numbers", "palette": "ink on paper, red accent",
 "finish": "matte print", "concept": {"idea": "a fuchka forecast for rainy Dhaka"},
 "hook": "বৃষ্টি নামলেই ফুচকা", "cta": "অর্ডার করুন"}
```

- `ledger --ledger clients/tokjhal/ledger.jsonl --client tokjhal --recipe recipe.json` before designing: prints
  `similar` (too few differing axes, the same archetype and focal as the last design, shared concept words, a look
  close to an earlier image with `--image`, the device of one of the last three pieces, a hook close to a recent one)
  and `notes` (a repeated CTA). `--strict` exits 2 when `similar` is not empty.
- `deliver … --ledger L --recipe R --client C` checks the same and records the delivered design (the hook and CTA
  default to copy.json's headline and CTA roles).
- `deliver` writes `DELIVERY.md`: files and sizes, a table of the render checks and judge verdict per design, the
  caption, the alt text, and notes (the copy verdict, facts, the AI-imagery label, native-reader proofreading for
  Bengali, Hindi and Arabic, warnings such as a single judge run at client level, and the spec behind each size when
  it was assumed for a custom size or is not official: its confidence, source and date, to confirm with the platform
  or printer).
