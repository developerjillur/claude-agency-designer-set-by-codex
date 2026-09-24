# Changelog: codex-design

The version is `SKILL_VERSION` in `scripts/design.py`; `doctor` reports it. After every change run the offline tests,
`python3 -m unittest discover -s ~/.claude/skills/codex-design/tests`, and render the pattern library (every pattern
on its presets must stay free of errors and warnings; `templates/README.md` lists them).

## 2026.09.24.4 · faster, and patterns that pass as finished work

The user asked for a last pass before publishing: faster, better organised and better output, never at the cost of
quality. Four audits ran first: a profile of the offline paths, one of codex-imagegen, a release audit, and a baseline
in which every pattern was rendered and judged as a finished piece (22 FAIL, 4 REVISE, 0 PASS, mean 2.97: stand-ins
where the pictures go, logos under the brand's minimum at phone size, 30 to 32 px labels, the same accent-bar formula).

- **Speed, output identical** (decoded pixels, `.qa.json` and copylint output compared): `pack` 5.8 to 2.5 s, one
  render 1.83 to 1.48 s, the pattern library 41 to 35 s, copylint 0.33 to 0.25 s. Screenshots taken in Chrome's fast
  mode where they are decoded again anyway, the contrast check counts colours instead of sorting pixels (2.49 to
  0.31 s over 656 text items), images are encoded in worker threads while the checks run, `pack` writes one canvas
  while Chrome renders the next, voice rules are compiled only for the languages being linted, and PNGs are saved at
  compression level 6 (the same pixels about 12 times faster, files about 8 % larger).
- **The judges are not asked twice:** `judge` and `copyjudge` reuse the verdict already on disk for exactly the same
  file (or deck), brief and settings (`"cached": true`, no Codex session); `--fresh` asks again.
- **Checks the judges enforced, now caught before a judge run:** a logo under the brand's own minimum (brand.json
  `min_size`, px at viewing size on screens, mm in print) is an error; labels, dates and captions under 34 px on a
  1080 post (`--label-min`) are a warning, while fine print marked `class="legal"` (or a source line) may sit at the
  floor; a weight a font family does not have (Figtree 600 when the brand ships 400, 500 and 700: the browser draws
  700 while the page says 600) is a warning; a weekday that does not match its date ("Sat 11 Oct" in 2026) is a
  copylint warning.
- **Pages get the numbers to meet them:** `--view-scale` and `--label-min` from the renderer, `--mark-min`,
  `--wordmark-min` and `--motif-mask` from brand.css (`design.py brand` writes the logo minimums from brand.json, 5 %
  over so a measured logo is never a pixel short).
- **The patterns:** real sample photos (generated and judged with codex-imagegen, AI-labelled, in
  `templates/patterns/assets/photos/`) replace the gradient stand-ins on the photo post, story, pin, blog image,
  thumbnail, product post, product infographic and sign; every logo meets the brand minimum at every preset; labels
  meet the floor; the brand's tide line replaces the generic accent bar; the story's call to action moved up under
  the sticker space with a logo lockup at the foot; the thumbnail's cut-out leaves the frame at its edges; the sign's
  picture shrank so the headline leads, with the wordmark and opening hours instead of a web pill; the infographic's
  note moved to the month the lines really cross; two dates were a Sunday in 2026; every text weight is one the
  brand ships (the same pixels); the brand book's type scale now follows the brand's own 1.333 ratio. Re-judged the
  same way, ten changed patterns went from a mean of 2.65 to 3.37: the photo post FAIL 2.45 to PASS 3.85, the story
  FAIL 2.60 to PASS 3.65, six more from FAIL to REVISE; the two left at FAIL carry sample figures and claims that only
  a client can make true.
- **Fixes:** ordinary English that repeats a word Spanish shares ("No filler, no fluff") was read as undetermined and
  lost every English check; two patterns (the URL finder and a list rule) were quadratic on long text without spaces
  or commas; a sentence ending in a two-letter word was merged with the next; `.webp` assets were served without
  their type.
- Tests: 106 (plus the pattern library, clean on every preset).

## 2026.09.24.3 · the voice: copy that sounds like the audience, in 24 languages

The user asked for every piece of copy (banners, captions, ads, posts, replies, scripts, in any language) to read
the way people and the brands they like talk on social media: easy everyday words, casual and conversational, with
no AI tone and nothing bookish, poetic, old or stiff "shuddho", because the project only works if it talks and thinks
like its audience. Five research runs read the evidence and public opinion, casual English craft, Bangla and Banglish
for Bangladesh (724 brand texts and 3,322 human and ChatGPT passage pairs measured), 18 more languages, and 89
humanizer and anti-slop projects with their data lists (`references/research/voice-*.md`).

- **A new skill, `natural-copy`**, writes and fixes any text a reader sees or hears: learn the audience's own words
  first, pick the register (a ladder for English and one for Bangladesh), write the way people talk, never fake
  casual, check with `copylint` and `copyjudge`. References: `voice.md` (the craft, replies, writing for the ear),
  `bangla.md` (Bangla and Banglish for Bangladesh), `languages.md` (18 more languages). The design skill's copy step
  now writes with it.
- **Voice rules** (`scripts/voice_rules.json`): 930 tested rules in 24 languages (en 257, bn 92, zh 52, pt 44, es 39,
  fr 39, de 38, ja 38, ar 34, ko 34, tr 31, id 30, ur 22, hi 21, th 20, vi 20, tl 19, ms 18, ne 18, ru 18, ta 18,
  fi 10, it 10, he 8) and 2 for every language (invisible characters, look-alike letters). 351 carry the author's own
  bad and good lines, which the tests run. Rules can be for one market only (Brazilian words in a Portugal post,
  mainland words in a Taiwan post, vosotros in Latin America, standard Arabic in an Egyptian or Levantine post), for
  some roles only (Title Case in headlines, how an image was made in alt text), or need a repeat ("fine once, a tell
  when it repeats"). Built from `references/research/voice-data/` by `build_voice_rules.py`, checked by `evaluate.py`.
- **Each line is read in its own language:** the `lang` tag (`--lang`, with a region such as zh-TW or pt-PT), else
  its script (Cyrillic and Hebrew added, by majority), else a Latin line's small words (es, pt, fr, de, it, id, ms,
  tl, tr, fi, vi); Banglish is read as Bangla and Hinglish as Hindi, so the English word lists run on English only.
  One "!" may end a hook outside English; CJK headlines and CTAs are counted in characters.
- **English:** the rest of the "not X, it's Y" family, inflected tier-1 verbs (garnered, leveraging), the 2026 social
  formulas ("Meet X, your new favorite", "Thank me later", a bare "Save this for later.", "What do you think?" as the
  closer), launch templates counted as a stack, two colon reveals, two ", not X" tails, candour worn as a costume.
- **Bangla:** stacked literary praise, slang piles, particle stacks, reactions, এবং with no ও or আর, repeated এটি,
  essay scaffolding, উপভোগ করুন as the ask, English Gen Z slang, Banglish, and opuu/bangla-writer's checks.
- **Platforms and roles:** whatsapp, email, web, sms and voiceover platforms; the length X counts (a link 23, an emoji
  2) as an error over 280, Threads' 500, SMS parts, markdown in feeds, "link in bio" where a post can carry the link,
  thread numbering (1/, (1/5), 🧵; not 3/4 cup) off X; replies skip the fold and greeting checks and get a note when sent as one block; scripts
  and voiceovers get the checks for the ear.
- **The piece:** grief with an offer in it, a joke on bad news, the same reply three times, উপভোগ করুন twice. The repeat
  note now says "cut it, or keep the same word" (rotating synonyms is itself a tell).
- **brand.json `voice.keep`:** the brand's own tagline or slang is never flagged.
- **copyjudge** scores fidelity to the brief first (blind judges reward invented experience), reads naturalness with
  the friend test (poetic, literary, textbook, sadhu, corporate and forced casual all lose), does not reward length,
  and lints its own rewrites, hooks and call to action (`rewrite_lint`, `hooks_lint`, `cta_lint`).
- **Fixes:** a sentence ending in a two-letter word ("it.", "up.") was read as an abbreviation and merged with the
  next, which skewed every sentence count; Python folds ı and i under IGNORECASE, so the non-English letter check now
  reads lowercased text without it.
- **Calibration:** 287 natural lines in 20 languages draw no finding at all; 232 of 234 robotic lines are caught. On
  1,671 real brand posts the most frequent new rule fires on 21 (a note); the rules that fired on plain brand copy
  were narrowed ("deep dive", Swiss prices, a single "Honestly?").
- **Other skills:** pointers to `natural-copy` in `bangla-voice-script` (a new §১৫; its narration register is
  unchanged) and in `hyperframes-creative/references/narration.md`.
- Tests: 104, all passing, and the pattern library renders clean (`CODEX_DESIGN_PATTERNS=1`).

## 2026.09.24.2 · the format catalogue: 526 formats, unknown sizes and kinds of design

The user asked whether the catalogue was missing design types (Instagram, Pinterest, blog thumbnails, cover pages,
cover photos, e-book covers, YouTube stories, product images, square banners and the like) and how the skill should
act on a size, a platform or a kind of design it has never seen: research it, then make all of it ready. Six research
runs (social; creator, messaging and regional; commerce and app stores; web and email; print, publishing and merch;
signage and out of home) and a scan of Canva's design types found the gaps.

- **Catalogue: 84 to 526 presets** in 13 families (social 146, print 98, e-commerce 71, signage 47, web 39, app 38,
  document 22, publishing 18, merch 16, audio 10, ads 9, video 9, email 3), each with a source, a date and a
  confidence (413 official). Corrections to existing ones from measured pages: the Instagram story and Pinterest
  9:16 bands, the Facebook cover and X card keep-outs, X and Threads viewing widths, the Shorts thumbnail, Snap ads,
  the Etsy listing, the roll-up's hidden zones. Every preset has aliases in English, Banglish or Bangla (64 had none).
- **Retired formats** answer with their replacement: YouTube Stories (Shorts or a post), IGTV covers, LinkedIn
  Stories, Fleets, Idea Pins and four Meta placements.
- **Finding a format:** `presets --find` matches at word starts ("ebook" is not in "facebook"), ranks the exact phrase
  first, and reads a misspelt word as its closest catalogue word ("pintarest", "thumbnil", "youtute", "squrae",
  "bilboard"); `--id` shows one preset in full; `--nearest WxH` lists the closest ratios; a wrong `--preset` says
  "did you mean".
- **Unknown sizes and platforms** (`references/formats.md`, new): the spec ladder, a project preset file
  (`--preset-file`, `CODEX_DESIGN_PRESETS`), and for a bare `--size` the flags `--safe`, `--keepout`, `--view-width`
  and `--min-text`; whatever is missing is assumed and stated in the report, as a warning and in the delivery note.
- **Reading distance:** `--view-distance` sets the text floor (ADA 703.5.5 on foot), `--legibility-index` for signs
  read from a road (USSC, MUTCD), `--screen-height` for screens in a room (DISCAS), `--file-scale` for billboard and
  bus files built at a scale. Image resolution follows the distance and the file scale, and a poster's own 150 ppi in
  hand. Pages receive the floor as `--min-text`, and the kit's `data-fit` takes `floor` or a percentage.
- **Unknown kinds of design and topics:** twelve archetypes by job, a method for an unfamiliar industry or regulated
  topic (with an industry style table), and what file to hand over by destination.
- **Book covers:** `bookcover` builds the KDP, IngramSpark or Lulu wrap (paperback or hardcover) as a preset with the
  spine, barcode box, hinges, spine-text rule and CSS variables; it matches the platforms' worked examples (KDP 6x9 in,
  240 pages, cream: 12.85 x 9.25 in; hardcover 364.84 x 264.6 mm).
- **Checks:** a colour change on a fold or spine (they drift up to 1.6 mm); folded sheets and wraps judged panel by
  panel for type sizes; keep-out messages name their reason; merch presets render on a transparent ground; the judge
  sees the preset's own viewing width and, for formats listed small, the listing size (e-books at 94 px).
- **Patterns** (26, all clean on 89 renders): `pin`, `blog-featured`, `product-infographic`, `square-cover`,
  `app-screenshot`, `book-cover` (e-book fronts and print wraps), `certificate`, `invitation`, `sign` (banners,
  billboards, bus sides, screens); the brochure's cover colour now wraps 3 mm past its fold.
- **Docs:** `formats.md`; `genres.md` §14 to §27 (pins, blog images, the product image stack and A+, app screenshots,
  course and event covers, book and magazine covers, audio art, certificates and invitations, tickets to packaging,
  merch, messaging and regional, calendars and CVs, signage); SKILL.md, cli.md and the research notes
  (`references/research/formats-*.md`).
- **Dates:** the research runs wrote tomorrow's date on every spec; they now say 2026-09-24, and the previous release
  is relabelled 2026.09.24.1.
- **Code review fixes:** a misspelt search word is read only at 0.8 similarity and the reading is printed ("read
  'pintarest' as 'pinterest'"), so an unknown but correct word such as "invoice" no longer lands on "notice"; a
  two-sided folded sheet (`--pages 2`) is judged panel by panel on each side; `data-fit` raises a line whose CSS size
  is under the floor instead of leaving it there.
- 98 offline tests pass; the pattern library renders clean.

## 2026.09.24.1 · production readiness: review, fixes and a delivery gate

(Reports rendered with this release say `2026.09.25`: the label carried the wrong date; it was released on 2026-09-24.)

The user asked for an end-to-end review with ratings, then for every gap to be fixed so the skill is production
ready. Six reviews drove this release: traceability against every request, the code, the docs, failure modes (about
75 timed commands), copy calibration on four corpora, and 70 design-judge runs aggregated.

- **Start-up on Python 3.14.** A bare `%` in the `sketch` help crashed every command there. Fixed, and a test now
  formats every command's help. The venv is per Python version (`.venv-3.X` beside a `.venv` built by another one).
- **Offline, sandboxed renders.** Every http(s) and WebSocket request, loopback included, goes to a dead proxy; kit
  links are served locally; `--allow-net` opts in. A missing or blocked CSS, script, font or image is an error that
  names the file. cli.md states the trust model (pages have local file access: render only HTML you wrote).
- **Output integrity.** Files are written to a temporary name and renamed; two runs on one output name are refused
  (3 in 32 racing runs had mixed one design's PNG with the other's report). `.qa.json` records its source (HTML hash,
  preset, locale, every file with its hash, versions); `judge` and `deliver` refuse a report from another render. A
  PDF's preview is `<out>.preview.png` (it used to overwrite a 300 dpi `<out>.png`). Stale slide files are reported.
- **Big canvases.** Chrome now and then returned an unpainted 8000 px tile (a white 8100 px page, 1 run in 4). Tiles
  are 4096 px and each is compared with a small capture of the whole page, captured again when blank, and the run
  stops rather than write a blank patch. Pages above 8192×8192 CSS px (Chrome paints them blank) and rasters above 400
  MP are refused with a way out. A roll-up raster (237 MP) now renders.
- **Errors people can act on.** One line instead of a traceback (`CODEX_DESIGN_DEBUG=1` for it); a page that hangs
  names the request it waits for or a busy script (`--timeout`); SIGTERM cleans up (exit 143); copy.json shape is
  validated; `CODEX_DESIGN_CHROME`, `--html <folder>`, `--preset` with `--size`, `--locale`, `--platform` and
  `--group` are checked; `--size` names the presets of that size; `outline` needs `--font` or `--family` and escapes
  its SVG title; `fonts --search` says when it cut the list; `sheet` skips side files; rendering a template without
  `--out` writes to the current folder, not into the skill.
- **doctor.** The test render is saved through Pillow; it reports uharfbuzz, fontTools, pdffonts, the Codex version
  and login, lists optional parts with what they unlock, exits 1 when not ready, and `--clean-tmp` removes folders of
  killed runs.
- **Checks the judge fails are now errors** (from the 28 FAIL runs): text outside the safe zone, text or a logo in a
  platform keep-out, dense script under 12 px at viewing size, contrast below the need, a logo too small or on a busy
  area, and text that is not in the approved copy. New: failed loads, a `.page` document rendered as one canvas,
  detail under a keep-out (warning), a logo recoloured by a CSS filter (warning), and plate notes: a rejected
  candidate or an image-judge FAIL read from the plate's `.meta.json` (Tokjhal used a rejected `-c2` plate in both
  jobs). Re-rendering the 17 shipped designs raised no false errors once two checker gaps were fixed: an on-image
  `note` role and a headline split over `<em>`.
- **Copy on the design.** Off-image roles (`caption`, `alt`, `alt_1`…, `video_title`, `hashtags`, `first_comment`,
  or `"on_image": false`) are skipped by render, judge, pairwise and verify and kept for the copy tools; a string split
  over inline elements matches; `data-allow` and text inside a logo are allowed; copy.json's `"locale"` and
  `"platform"` are the defaults everywhere; the Bengali word checks on rendered text follow the locale (they assumed
  Bangladesh before).
- **judge.** It refuses a render with errors (exit 2, `--force`). `--brand` puts the supplied logo files, logo rules,
  colours and motif in the brief: on the Sutokotha story it failed a 14 px mark-to-wordmark gap (the rule is half the
  mark, 24 px) in all three runs, which earlier runs without it had passed. Plate notes go into the brief. `--runs N`
  takes each criterion's median, fails a gate only when most runs fail it, and keeps every verdict in
  `<image>.judge-history.jsonl` with the image hash.
- **copyjudge.** `--runs N` (median per criterion, pooled hooks; the report asks for 5 runs when runs disagree or the
  median sits within 0.10 of 3.6 or 4.3), a 180 s timeout with one retry, the deck's hash and settings recorded, and
  rewrites in the copy's own script whatever the session's language instructions say.
- **Copy lint calibrated** on natural and robotic Bengali and English (review r5): natural Bangladeshi Bengali
  flagged 8 → 1 of 26 (the one is a greeting opener, by design), robotic Bengali caught 14 → 24 of 27, AI-sounding
  English 13 → 26 of 26, natural English 3 → 2 (tag-the-friend bait and the caption fold, both by design).
  - সুস্বাদু, মূল্যছাড় and দ্রুততম left the formal list; 18 standard but stiff words became notes.
  - New: Bengali calques (শুধু একটি X নয়, অন্বেষণ করুন, নতুন উচ্চতায়, নিখুঁত সমন্বয়, আরাম থেকে, প্রতিটি মুহূর্ত,
    উদযাপন করুন, প্রতিশ্রুতিবদ্ধ, যাত্রা as a metaphor) and English stock lines (not just X. It's Y, where X meets Y,
    the perfect blend of, made with love, like never before, you deserve it, every step of the way).
  - One "!" may end a Bengali hook; Bengali CTAs go to 6 words and Latin CTAs to 4; the caption fold counts visible
    letters (ক্ষে is one); urgency that states a fact passes; "seamless" alone is a soft word; visarga abbreviations
    (মোঃ) are a note; পাইলট no longer reads as sadhu and পিসি no longer as a kinship word; emoji: 1 on the image, 3 in a
    caption.
- **New commands.** `ledger` (the never-repeat check for Compose: recipe axes, the composition device of the last
  three pieces, hooks close to recent ones, CTA notes), `deliver` (the final gate: render report, judge and copy judge
  must match the current files; `--facts`; `--ledger`; files, font licences and a `DELIVERY-<name>.md` per delivery,
  earlier files moved to `archive-<time>/`) and `analyze --zone` (a plate's reserved zone measured as calm, scrim or
  busy, calibrated on 17 judged plates).
- **Direct and verify.** The dossier's copy is linted before any generation; verify flags an em dash in what the
  picture says; pairwise without `--copy` no longer tells the judge the approved copy is an empty list.
- **Templates.** The pill button is opt-in (`class="cta pill"`) in the post and story patterns; display ads keep a
  button. README and the sample licences no longer carry dashes.
- **Docs.** SKILL.md rewritten around quick starts and the gates; cli.md covers the new commands, checks, exit codes
  and troubleshooting; copy.md, craft.md (template tells, the ten composition devices, judge lessons), ai-visuals.md,
  direct.md, fonts.md and the rest agree with the code; the research notes ship in `references/research/`.
- **Verified end to end** on Sutokotha: the story and carousel were rebuilt from `build.py`, judged three times each
  (story FAIL on the brand gate, then PASS 3.8; carousel PASS 3.8), their copy judged (story PASS_NATIVE 4.43 after
  the hook moved to the headline; carousel PASS_NATIVE 4.55 with its new caption, 4 of 5 runs), and shipped with
  `deliver` and the ledger (a re-delivery neither duplicates the ledger entry nor archives identical files).
  The v1 finals are in `final/archive-v1-2026-09-24/`.
- Tests: 89 offline tests plus the pattern library for codex-design; 76 for codex-imagegen.

## 2026.09.24 · copy that reads human: no em dash, natural Bengali, hooks, CTAs, captions

The user asked for three things:
- no em dash (the AI dash) anywhere on a graphic;
- copy that reads natural, personal and native, never robotic, translated or bookish, above all in multilingual work;
- hooks, social vibe and calls to action that engage.

Four research passes fed this release, each with sources in `references/copy.md`:
- **AI-writing tells:** Wikipedia's "Signs of AI writing", corpus studies, and 15 humanizer and anti-slop repos.
- **Natural Bangladeshi Bengali:** 2024–26 brand posts, the Bangla Academy, and Prothom Alo, Niropekho and Bigganchinta
  on AI-written Bengali.
- **Hooks, CTAs, captions and platform data:** Meta, Instagram, LinkedIn, YouTube and TikTok sources, and marketing
  skill repos.
- **Transcreation for 12 languages**, plus an audit of the local skills.

- **The em dash is an error.**
  - `checks` fails any em dash, "--" or spaced en dash in rendered text. `dash_issues()` holds the rule.
  - An en dash stays only between two numbers in Latin text. Between words it becomes "to" (warning). Bengali ranges
    are written ১০-১২ or ১০ থেকে ১২.
  - The old advice to replace a spaced hyphen with an en dash is gone.
  - The skill's own templates no longer carry a word en dash or an em dash.
- **`scripts/copyrules.py`** (new, pure Python) holds the lint. It checks:
  - English: tier-1 AI words (one sighting), tier-2 clusters, 20 structural and marketing patterns (not-X-but-Y,
    "Whether you're", sign-posting, trailing "-ing" clauses, launch hype, bait, urgency without a fact, stock
    endings), and chatbot leftovers (error);
  - generic CTAs, colon reveals, staccato runs, flat rhythm, same openers and triads;
  - Bengali:
    - a list of formal → everyday words;
    - sadhu forms (গুরুচণ্ডালী), notice chains and translated clichés;
    - West Bengal words for Bangladesh, with a note on kinship words (Bangladeshi Hindu families use them too);
    - honorific mix-ups (আপনি … করো), pronoun overuse, Latin words inside Bengali lines;
    - "." for "।", a visarga used as a colon, Bangla Academy spellings;
    - "দাম জানতে ইনবক্স" (Bangladesh's Digital Commerce Guideline asks for clear prices);
  - other languages: Spanish ¿¡, French spacing and quotes, CJK half-width marks, German quotes, and 𝗯𝗼𝗹𝗱 Unicode
    letters;
  - platforms: the caption fold (Instagram 125, Facebook 80, LinkedIn 140), hashtag caps (an error over the cap),
    emoji, emoji bullets, greeting openers, bait, headline, cover and thumbnail length, a thumbnail that repeats the
    title, and one CTA;
  - the brand: `brand.json` `voice.avoid` and `voice.prefer`.
- **`copylint`:** the offline command over that module. It exits 1 on errors.
- **`copyjudge`:** a native-reader review by a fresh Codex session.
  - It scores ten criteria, gives every string a natural rating, a problem and a rewrite, and offers three hooks and
    the best CTA.
  - It returns FAIL, REVISE, PASS or PASS_NATIVE.
  - The house style (no dashes) is written into its prompt, so it does not argue the rule.
- **Rendered-text checks** also warn on bookish, translated or West Bengal Bengali that is not in the approved copy.
- **`judge --allow`** now tells the judge what the allowed text is (the logo's wordmark). Before, the list only fed the
  Latin text diff, so the judge failed text accuracy on a Bengali wordmark such as টকঝাল.
- **`references/copy.md`** (new, 750 lines):
  - house rules;
  - English tells, with tables;
  - Bangladeshi Bengali: the tells, formal → everyday, code-mixing, Bangladesh vs West Bengal, address forms,
    punctuation, digits and spelling, native hooks and CTAs;
  - transcreation for 12 languages;
  - a hook library by format, CTA rules and a library in English and Bengali;
  - caption structure and a platform table;
  - attention;
  - the copy loop;
  - frameworks;
  - a brand-voice schema, variants, series and the copy ledger;
  - accessibility.
- **`SKILL.md`:**
  - the workflow gains step 2, Copy (lint, then rate, before the design);
  - Non-negotiables add the copy rules;
  - new core commands;
  - the description covers copy, hooks and captions.
- **`craft.md` and `cli.md`** now point to the new tools and rows.
- **Tests (69):** dashes, the English and Bengali lint, a render test that fails an em dash, and the copy verdict
  bands.

Measured with `copyjudge`, Bengali, 24 September 2026:

| Deck | Before | After |
|---|---|---|
| Sutokotha carousel | FAIL 3.46 | PASS_NATIVE 4.55 (hook 3 → 5, locale 3 → 5, AI tells 3 → 5) |
| Sutokotha story | FAIL 4.0 (the spaced dash; CTA 2) | PASS 4.26 |
| Tokjhal post and caption | PASS 4.01 | PASS 4.29 |
| Tokjhal story | PASS 3.9 | PASS 4.46 (the fourth draft) |

On the Tokjhal story, stripping the context to "ফুচকা খাবেন?" fell to REVISE (hook 2, emotion 2). The copy judge can
also be wrong about local usage: it called অধরা সাংস্কৃতিক ঐতিহ্য a translation tell, but it is the standard
Bangladeshi term. Check disputed terms against a local source.

## 2026.09.24: dense scripts and carousel judging (the Sutokotha set)

Found on the Sutokotha set: five Bengali designs for a Bangladeshi Jamdani label.

- **Dense-script size floor.**
  - What went wrong: every design passed the checks, then the art-director judge failed three of them on legibility.
    Their Bengali supporting text was 26–30 px on 1080–1200 px canvases. Bengali letters are denser than Latin at the
    same px size, so the Latin `min_text_px` floor is too low for them.
  - The fix: `checks` now warns when Bengali, Devanagari or Arabic text is under 12 px at the preset's viewing width
    (about 34 px on a story or post, 77 px on a thumbnail), and says what size to use.
  - Test: `test_dense_scripts_need_twelve_px_at_viewing_size`.
- **Carousel strips are judged slide by slide.**
  - What went wrong: `judge` scaled a 5-slide strip to one phone width, which gave each slide 78 px, so the
    legibility gate could not pass.
  - The fix: when the image is a whole `--slides` track, Image 2 shows every slide at 390 px, side by side.
    `<out>-strip.jpg` also finds `<out>.qa.json` on its own.
  - Test: `test_judge_shows_a_carousel_strip_slide_by_slide`.

## 2026.09.24: kit, `data-fit-lines` counts lines, not rect tops

Found on the Vela Cycles set (story, LinkedIn banner, YouTube thumbnail).

`cd-kit.js` counted lines as the distinct tops of the range's client rects, so a headline that fitted was marked
`data-fit-failed` at every size in two cases:
- **Blockified spans** (spans in a flex column), because a span's box is shorter than its text's content area.
- **A smaller run on the same baseline**, such as the "km" in "200 km", which starts lower.

The kit now joins a rect to a line when their middles are within 0.35 of the smaller height. The test is
`test_fit_counts_lines_not_rect_tops`. The old kit fails that page and the new one passes. All 62 tests and the
pattern regression pass.

## 2026.09.24: the Direct route

Built on four more research notes: R8 (GPT Image 2.5: region edits, references, sizes, access), R9 (single-prompt
professional designs: the dossier method), R10 (2026 trends, platform data, attitudes to AI-looking work) and R11
(multi-agent generation, verification and region repair). Then an end-to-end run on the Northloaf brand. Everything
below is measured on the Codex engine (gpt-image-2).

### `direct`: one dossier → one compiled prompt → a finished, verified design
- **The dossier** is the single source for the prompt, the verifier and the repairs. Its fields:
  - brief, market and goal;
  - the facts ledger (with statuses; `refuted` and `needs_client` block);
  - the proof slot;
  - the concept (idea, layout axis, focus and eye path, picture, medium, camera, light, materials, type-image device,
    typography, palette by role and share, style and finish);
  - frozen copy;
  - zones;
  - references with roles (a person needs consent);
  - logo placement;
  - the variety recipe.
- **The prompt compiler** follows R9's order (manifest, artifact, purpose and idea, layout, focus, picture, device,
  typography, exact text, colour, brand space, style, safe zones, constraints). It adds:
  - layout zones and safe zones in the generated image's own percentages, with a 2.5% buffer, because the model sets
    type nearer the edge than asked;
  - the strips a crop will trim;
  - a readable-size floor (the first judge asked for 36–40 px on 1080);
  - physics hints without hand talk when no people appear;
  - realism rules for photographed people and products;
  - 3–8 exclusions from R10's list of dated and AI-template looks.
  With a brand sheet attached, the hex codes are dropped from the text.
- **References:**
  - a word-free, logo-free brand sheet (`refsheet --for-model`);
  - a label-free wireframe (text bars, picture crosses, dashed empty spaces);
  - the client's images, ordered fidelity-critical first, within Codex's limit of 5 and the API's 16.
- **Engines:** Codex (`--aspect` in words, `--raw-prompt`: the prompt now reaches the tool byte for byte) or the API
  (Sunburst `xhigh` at an exact multiple-of-16 size up to 3.69 MP). With a key in the keychain, `auto` picks the API.
- **Crop to format:** the window slides to where OCR finds text and saliency finds the main objects. Text that cannot
  fit becomes an error, and the retry names the strips to keep clear.
- **Rounds:** K candidates per attempt, ranked by verification. A retry names the last attempt's mistakes. Bounded
  repairs follow, then the real logo (reversed on dark ground, with its contrast and ground calm measured), then the
  final verification.
  - `--judge` runs the art director.
  - `--revise 1` regenerates with its notes on REVISE or FAIL and keeps the better version.
  - Notes about the logo never reach the model: a revision that asked it to "add the client's logo" drew a fake arc.
  - Exit 3 means beyond 3:1; exit 4 means still wrong, and `<id>-plate.png` (the attempt with its text removed) is
    left for composing.
- **Hybrid typeset:** copy marked `"route": "typeset"` is kept out of the pixels, and the prompt keeps its zone calm.
  It is then set in HTML with the brand's fonts:
  - at least the preset's readable size;
  - a box too narrow is widened towards its free side or wrapped;
  - grouped lines share one size;
  - ink or paper, whichever contrasts more with the band the letters sit on, flipped when the renderer measures a
    failure;
  - checked by the renderer.
  For covers' addresses and hours, prices, legal lines, and Bengali.
- **Placement like a designer:**
  - left-aligned strings snap to the picture's headline axis (a judge had seen a 32 px outdent);
  - every string is shifted inside the safe area;
  - a busy planned zone (edge density plus tone spread) is traded for the calmest nearby spot. The search tries
    shifts up to about half the box, and wider, shorter boxes that reflow the text into fewer lines. It keeps clear
    of the picture's own text, the logo and the other strings.
  - Every move is reported.
  - Measured [L]: a four-line paragraph whose last word ("morning.") sat on the bread, a legibility FAIL, reflowed
    into three lines on the dark wall, with no regeneration.
- **Small-text sizes:** close sizes are unified (steps under 1.25× read as muddled levels). The weights default to one
  per group.
- **`--retypeset`:** sets edited typeset copy (new hours, a new price) over the kept `<id>-picture.png` in about 5 s,
  with no generation.
- **Ledger:** `ledger.jsonl` records every delivered design.
  - The recipe must differ from the client's last 6 designs on at least 3 axes, and not repeat the last design's
    archetype and focal type.
  - Concept-word overlap of 40% or more, a repeated style anchor, or a finished image within 10 bits of difference
    hash of an earlier one also block. `--force` overrides.
- **Guards:** a lock per run folder; every run's candidates carry a timestamp, so no stale file is picked up.

### Verification (`verify`, used by `direct`)
- **Three OCR scales:** the full size, 40% and 22%. Giant display words that Vision misses at full size are found in
  the smaller copies.
- **Cyrillic and Greek look-alikes** read as Latin when the copy is Latin: an ultra-condensed "rye" came back as
  "гуe".
- **Matching:**
  - strings that are there as written claim their words first, and fuzzy matches come after (a fuzzy "100% rye"
    had stolen "Dark," from the next line);
  - fuzzy runs never jump between distant lines;
  - word-level boxes, so an extra word inside a matched line is repaired alone;
  - repeated strings are named as duplicates.
- **A blind second reader** (Codex vision, no copy in its context, spelling letter by letter) settles:
  - near misses (a soft-serif f read as t);
  - strings Vision cannot find at all.
  It keeps real typos: a "betore" drawn in Georgia stayed an error. A second, language-corrected Vision pass supplies
  alternative readings.

### Region repair (`patch`, used by `direct`)
- **`--mode crop`:** edits a close-up window grown to an aspect the model makes, so small text gets several times
  more pixels. `auto` crops below a third of the image.
- **The pointer copy:**
  - drawn in a colour the design does not use;
  - the region described in words and percentages;
  - a leak of the pointer colour rejects the edit.
- **Registration:**
  - pixels that came from outside the edited image are left out (before, a 1% zoom always beat the true shift);
  - refined on a copy up to 1024 px wide (sub-pixel);
  - borders the shift uncovers are filled from the original.
- **Frame-edge text** is left to a regeneration: a repair only repainted a cut "S" at the edge.
- **`--point x,y[,r]`:** a pin, like a comment on a spot. The region is a square around it. Demo: "a band of morning
  sunlight on this wall" changed only that area; every other pixel stayed the original.

### Judging
- **`pairwise`:** a blind A/B vote in both orders, in client and blind modes. A win counts only when it survives the
  swap. In the first run the image shown second won all 4 votes.
- **`judge --allow`:** the brand name in a composited wordmark is no longer "extra text".
- **The brief** states the logo policy: a thumbnail without a logo failed "essentials" before.

### Compose is the primary route
- Blind comparison on 2026-09-24, Northloaf, Codex and Claude judges, both orders; a win counted only if it survived
  the swap. Compose won the post, the thumbnail and the cover; Direct won the story. Votes 17–7.
- SKILL.md, direct.md and the description now set Compose as primary. Direct is for type-as-image concepts, fast
  exploration, and as a challenger on hero pieces.
- Kit: display text (h1–h3, `.display`, `[data-fit]`) gets lining figures. Young Serif's default old-style "3" dropped
  into the next line in a judged thumbnail.

### Code review fixes (independent reviewer)
- `vision()`: a hung or broken helper, timed out or returning bad JSON, is "no answer", not a crash. `verify`,
  `direct`, `patch` and `ocr` no longer die with a traceback.
- `direct_judge`: a judge that times out is a soft failure in the report; the run's result is kept.
- `zone_kind`: whole words only. "Start button", "Chart" and "Heart rate" were being drawn as picture boxes in the
  wireframe.
- `pairwise`: two files with the same stem are no longer merged into one side.
- The run-folder lock is created atomically (`O_EXCL`); a lock left by a dead run is taken over.
- The scrim step uses the text box's own coordinates (it was reading a scrim's inflated box) and never stacks a
  second scrim.
- `resolve_ambiguous`: a string with no readable tokens is never "found" by an empty match.
- `place_typeset`: a box wider than the safe area is fitted to it before it is positioned.

### Measured on Northloaf (Codex engine, 2026-09-23/24)
- **Instagram post:** 5 strings, two times, all exact in 1 of 2 candidates on the first attempt, twice.
  - PASS 3.65 in 124 s.
  - Blind pairwise, both orders: 4–0 against a naive prompt; 2–2 against the composed version.
- **YouTube thumbnail:** PASS 3.85; both candidates exact.
- **Story:** exact after the OCR fixes. REVISE 3.55; the judge wants the client's real rye photo.
- **Facebook cover:** the 3:1 crop and the 52 px floor defeated pixel details, so the hybrid route was built for it.

## 2026.09.23: first release

Built on seven research notes (skills and repositories including higgsfield-ai/skills and anthropics/skills, community
tools, GPT Image design prompting, design craft, platform specs, rendering tooling, culture and law).

### Engine (`scripts/design.py`, standard library + an optional venv)
- Renders Claude-written HTML/CSS with the installed Chrome over the DevTools pipe: exact canvas sizes, `--scale`,
  PNG/JPG/WebP/PDF, byte limits, transparent PNG, carousels (`--slides N`, per-slide files, strip, LinkedIn PDF),
  documents (`--pages N`, each page captured on its own), tiling beyond Chrome's 16,384 px texture limit.
- Print: exact MediaBox with TrimBox/BleedBox, 300 dpi rasters with the exact pixel size and dpi, canvases laid out on
  whole CSS pixels (the fraction goes into the bleed), `--cmyk [ICC]` raster CMYK PDF, font embedding report with
  Type 3 detection, fold positions per side for brochures.
- Every raster carries sRGB ICC; designs with generated visuals get IPTC `compositeSynthetic`; every report records
  the Chrome version.
- 84 presets (social, web, ads, e-commerce, print, documents) with safe zones, keep-out zones for platform UI, text
  floors at viewing size, byte limits, bleed and folds, each with its source and verification date.
- The kit (`cd-kit.css`, `cd-kit.js`) served from the skill at `https://codex-design.invalid/`; `kit` copies it for
  editable delivery. `data-fit` keeps every line inside its box.

### Checks (measured, not guessed)
- Cut, off-canvas and fit failures per slide and per page; safe zones, keep-out zones, seams and folds.
- Contrast on real pixels behind each line's ink band, which is measured from the font's real ascent and descent
  (canvas metrics), so Bengali and other tall scripts are judged fairly.
- Text hidden under a painting element (named in the error; transparent layout boxes ignored); a line, shape or colour
  edge running behind the letters; logo clear space (text and graphics).
- Fonts that did not load, script fallback to system fonts, letter-spacing on Bengali/Devanagari/Arabic, leading by
  script and size (h1/h2 count as display on wide banners), runts, overlaps, tracking, thin weights, hierarchy per
  slide/page, too many families.
- Copy: exact-once approved strings (NFC, dash and quote normalised), placeholders, generic marketing phrases,
  straight quotes, three dots, spaced hyphens; special-day lint (`--occasion solemn|fast`).
- Print prepress: small near-black text (use #000), small reversed text, image ppi at printed size, Type 3 or
  unembedded fonts, PDF page count.
- Colour-vision and squint simulations (`--simulate`, also on `pack`).

### Photos and brand
- `analyze` (faces, attention and objectness saliency, calm zones), `reframe` (smart crop to every preset),
  `cutout` (Apple Vision subject lift, local): all apply EXIF orientation first.
- `fonts` (Fontsource, unicode-range, size-adjust for a second script, licence file), `brand` (brand.json →
  brand.css + fonts), `outline` (HarfBuzz-shaped SVG wordmarks), `qr` (SVG with a viewBox, quiet zone).

### Judge
- `judge`: a fresh Codex vision session as a senior art director, with the renderer's measurements; views at full
  size, at viewing size and squinted; 10 hard gates, 10 weighted criteria; FAIL / REVISE / PASS / PASS_SENIOR
  computed in code; findings with before/after fixes; a text diff against the approved copy.

### Templates
- 16 patterns on the fictional Tidewater brand, each clean on its presets: photo, type-led and product posts; quote,
  tip and stat cards; story; seamless carousel; YouTube thumbnail with five overlays; celebratory and solemn day
  posts; covers for YouTube, Facebook, LinkedIn and X; the IAB and Google display set; a data infographic; an A3
  poster; an A5 flyer; a tri-fold brochure; a business card.
- A 10-page brand book built from brand.json (logo, clear space, misuse, colour, computed contrast matrix, type with
  a Bengali conjunct specimen, graphic elements, applications).

### Found by the end-to-end run (a new brand, real Codex plates, the judge)
- Word-level contrast: a headline that runs onto a shelf of loaves passed the whole-text contrast; each line is now
  also measured in word-sized pieces.
- Display compounds broken at a hyphen ("36-" / "hour"), logos too small at viewing size (a 58 px mark is 9 px on a
  phone thumbnail), and the reversed mark on the brand colour (the full-colour mark loses its circle there).
- `data-fit` allows for fonts whose content area is taller than a tight line box (Young Serif), and checks every line
  stays inside the box (bottom-aligned text no longer creeps upwards).
- Overlap is measured line by line (a headline and a coloured span inside it no longer collide), h1/h2 count as
  display type whatever their weight, and the judge no longer fails a design for a missing copy list.
- codex-imagegen: plate briefs ("text-free background plate for a YouTube thumbnail") were classified as designs
  and got the design rules; lint no longer fires on plates, "falls into shadow" or "shelves hold".

### Tests
- 42 offline tests (units, photos, Chrome renders, tools), plus `tests/test_patterns.py`, which renders the whole pattern
  library (57 renders, ~25 s, all clean) when `CODEX_DESIGN_PATTERNS=1` is set.
