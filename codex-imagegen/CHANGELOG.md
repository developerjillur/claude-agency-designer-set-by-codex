# Changelog: codex-imagegen

The version is `SKILL_VERSION` in `scripts/codex_image.py`; `doctor` reports it. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests`. Run `doctor --image-smoke` after every Codex CLI update.

## 2026.09.25.1 · the judge sees only what it is given

- The image judge's Codex session now starts in its own empty folder (`-C` its temp folder) and is told to use only
  the message and the attached image. It started in the project folder, where a judge can read the files there; in
  a test on 2026-09-25 a design judge read a banner's HTML and failed the PNG for it.
- **Tests:** 100 offline tests.

## 2026.09.24.2 · a fast path for drafts

- SKILL.md opens with the draft path: brief, `generate --no-judge` in the foreground (about 50 s instead of 90; a
  background job ended with a `claude -p` session before the image was saved), look at it yourself, deliver;
  several images in one `batch --no-judge` in the background. Anything shipped keeps the judge. No code change.
  Measured on real tasks: a draft hero photo in 58 s, a Bangla post in 37 s, a 3-slide carousel in 44 s.

## 2026.09.24.1 · no more half-hour waits, and batches that keep their work

Found by reading the skill's own session logs (single images: median 87 s, slowest 488 s; judges: median 38 s).

- **Stuck sessions:** image sessions stop at 480 s and judges at 150 s (were 900 and 420); a timeout is never retried
  at full length, so a hang costs one wait, not two or three. Codex's own error text reaches the result, the event log
  of a failed session is always kept, and a usage limit or a lost login stops the whole run at once (exit 3).
- **Batches keep their work:** sizes, refs, targets, candidates and style files are checked before any session; each
  job writes its meta and a progress line as it ends; the report is written even when a run is cut short; one bad
  export no longer stops the others; `--resume` keeps the jobs that passed.
- **A judge error is not a failed image:** `batch --only X --rejudge` judges the existing image again from its meta and
  exports it on a pass; the report tells ERROR (re-judge) from FAIL (make a new image). `judge` checks every path
  first, judges in parallel at medium effort and prints every result it has.
- **Wrong inputs say so in one line:** style, refs and targets resolve next to the jobs file; a missing style file,
  an empty brief or an audit root that is not a folder stops at once; a job's own style wins; any file or value error
  is one `ERROR:` line instead of a traceback.
- **Short output:** `batch --dry-run` prints one row per job (3.7 KB instead of 59.7 KB for 10 jobs) and writes the
  full prompts to files.
- **Docs:** a run-time table and the rule to run generate, batch and judge in the background, a `judge` section,
  path rules and the `--size` format; SKILL.md is shorter (about 3,190 tokens); master.md's contents give line numbers.
- **Tests:** 99 offline tests.

## 2026.09.24 · faster and safer runs

Measured offline with a fake Codex that replays the medians of 658 real sessions; no quality setting changed (judge
prompt, schema, thresholds, candidates, fix rounds, sizes and encoders are as before).

- **Candidates judged together:** in a 2-candidate job the second candidate's judge no longer waits for the first;
  the first usable verdict cancels the rest (122 s to 98 s when candidate 1 fails).
- **Batch results read as they land:** the image call's result is taken from the session log the moment it returns,
  instead of waiting for the agent to repeat it (a median 5.5 s per session). `CODEX_IMAGEGEN_WAIT_FOR_REPLY=1`
  turns it off.
- **Web export in parallel** across images and widths, byte-identical (3 photos and a transparent image: 10.6 s to
  3.1 s).
- **Agent-mode batches** no longer sleep 3 s times their index after getting a slot (6 jobs at concurrency 3: 42 s to
  27 s).
- `CODEX_IMAGEGEN_EXTRA_FLAGS` adds flags to every automated `codex exec`, to A/B a leaner Codex start-up.
- **Reliability:** Ctrl-C, a killed task or SIGHUP now stop the running Codex sessions (they used to keep spending
  quota); a judge that disconnects quickly is retried once, and an image whose judge failed is listed in the report's
  next steps instead of vanishing; telemetry can no longer fail a batch after the images were made; JSON reports are
  written atomically; the API engine retries the same model once on a 503 and reads `Retry-After` safely; timeouts
  kill the whole process group.
- **Fix:** an inline style lock longer than a file name (255 bytes) crashed with "File name too long"; it is now read
  as text.
- Tests: 82 (6 new), all passing.

## 2026.09.23

All of the following landed on the same day, listed in the order they were built.

### Plates, lint and the direct route (later the same day)
- **`PLATE`:** a brief that says it is a text-free plate ("background plate", "typography is added later", "no
  text") is never compiled as a design, even when it quotes words, so codex-design's plates do not get the design
  rules.
- **Lint:** `MOTION_FALSE` knows "falls into shadow", "fall out of focus" and "falls away" (not motion); the hands
  lint only fires when the brief names a person or a hand.
- **`--raw-prompt` on the Codex engine:** with the fast mode's compiled prompt writer, the brief is now sent as
  written, without the format, place, look, realism and physics layers. codex-design's `direct` route compiles its
  own complete prompt (aspect in the first line, realism and physics lines included where they apply) and needs it
  to reach the image tool byte for byte. Before, the flag applied to the API engine only.
- Tests: 75 → 76 (`test_raw_prompt_reaches_the_codex_tool_verbatim`).

### Designed graphics move to codex-design
- **Routing:** the description and §3 send posts, stories, carousels, thumbnails, banners, covers, ads, posters,
  flyers, brochures, cards, infographics, day posts, logos, brand kits and guidelines to the new `codex-design` skill.
  This skill keeps stand-alone photos, illustrations, textures, cut-outs and the plates that designs are built on.
- **`image_kind(brief)`** tells a photo, a styled image (illustration, 3D, watercolour …) and a graphic design apart;
  the first medium named wins, and a design needs quoted text when a photo is also named.
- **`DESIGN_RULES`:** a full-AI design job (the route codex-design allows for ≤ 3 short Latin strings) gets rules for
  a finished layout by a senior designer: the quoted text spelled exactly, once each, nothing else written. A people
  photo inside a design still gets the real-people rules.
- `og` stays Latin-only; other scripts use codex-design's `og-image` preset with typeset text.
- Tests: 74 → 75 (`test_image_kind_separates_photos_styled_art_and_designs`).

### Production hardening (full review: code, docs and test audits)
- **Never lose a judged image:**
  - a failed finish, `--size` crop, transparent refine or grey judge view now logs and keeps the image;
  - the `-raw.png` original is always kept.
- **Safety:**
  - job and export names are validated (no paths or `..`), and aspects are checked before anything runs;
  - a bad or corrupt jobs file stops with a clear message;
  - temp folders live under one run root that is removed at exit (`CODEX_IMAGEGEN_KEEP_TMP=1` keeps it).
- **Parity:** agent mode and the API engine now get the compiled place/look/realism/physics prompt, the style lock, transparent output and the finish. Agent-mode batch jobs forward `finish` and `transparent`.
- **Cost:** only failure-library checks count toward the two-candidate rule; place and realism checks no longer double the plan usage.
- **Looks:** the Intent/Camera lines pick the look, so a prop such as "a smartphone on the desk" no longer switches to the phone look. Phone looks ignore a brief's prime focal length.
- **Edits:**
  - no capture line;
  - a keep-the-frame rule;
  - a finish marker, so an edit of a finished image is not finished twice.
- **Illustration jobs:** a style lock's `style`/`medium` line now counts as non-photo.
- **Provenance:**
  - the IPTC tag carries over to crops, refined alpha and every export format (PNG too);
  - `finish` tags only generated sources, so a client's photo is never mislabelled;
  - an output that lost its metadata (an older transparent refine re-saved it) is still tagged on export when the skill's own `.meta.json` names it.
- **Web output:**
  - `assets.json` holds relative paths only (no local `/Users/...` paths);
  - `audit` counts `srcset` and skips generated masters, candidates and `-vN` re-run attempts.
- **Fix rounds:** a leftover mark or stray word gets the judge's local edit instead of a `model_limit` skip. One extra edit round runs after the configured rounds. Among equal verdicts, the newest fix wins.
- **Batch:**
  - `--only a,b` reruns failures and keeps the original casting;
  - `--dry-run` shows every job's compiled prompt, checks, lint, place, look and finish;
  - `batch-report.md` ends with *Next steps for failed images* and the exact rerun command.
- **Judge:** fix instructions are written in English (Codex's `AGENTS.md` asks for Banglish).
- **Lint and people:** lint reads only the job's own brief, not the shared style lock. "No people" and possessives ("the receptionist's chair") no longer count as people in the frame.
- **End-to-end check:** a 4-image website set (style lock, global cast rotation, looks, finish, transparent asset, export) ran on real Codex. Its two failures were fixed by the documented flow: read *Next steps*, simplify the brief, rerun `--only`. All four images were then usable.
- **Docs:**
  - SKILL.md is rewritten: 165 lines instead of ~3,900 words, covering preflight, lint, run, verify, fix and deliver; the description is 829 characters;
  - the full reference is in `references/cli.md`;
  - web-assets, server-setup, image-judge and master.md are corrected against the code.
- **Tests:** 42 → 74 offline tests, including:
  - the batch CLI, argparse wiring and the `finish`/`audit` wrappers;
  - Codex output recovery, budget, and locale fallback;
  - provenance and sidecars, audit, edits, agent parity and local edits;
  - `doctor` without Codex, a missing Pillow, output planning, reference roles and the API dry-run.
- `doctor` now also reports:
  - the skill version
  - the locales data
  - the Codex timezone override
  - the SVG rasterizer
  - an `AGENTS.md` reply-language override
- New `doctor --image-smoke` makes one real image, which checks that Codex's code-mode image path still works.
- Lint no longer warns about:
  - layout space "for the headline"
  - the style lock's "avoid: text" line
  - unheld bottles and jars

### Natural look (photos that do not read as AI)
- **Capture profiles (`look`):**
  - Profiles: editorial, portrait, phone, phone-flash, film, product and interior.
  - Picked automatically from the intent; the brief's focal length is kept.
- **Realism checks** for people, scenes and products; the judge verifies them.
- **Judge:**
  - Lists `ai_tells`.
  - Realism 3 means stock polish, which is a FAIL.
  - Text fields are always written in English.
- **Light photographic `finish`**, applied after judging:
  - shades-of-grey white balance (highlights protected, brightness kept), 0.3 px soften, luminance grain, a light vignette, and 3 % less saturation;
  - the untouched original stays as `-raw.png`;
  - the finished file and web exports of generated sources carry IPTC `DigitalSourceType = trainedAlgorithmicMedia`.
- **Text leaks:** hints stop them in no-text briefs, covering signs, menus, screens and maker's marks.
- **Other hints:** night scenes; clocks (no 10:10).
- **Measured:**
  - Blind review, 10 briefs: the new skill beat the old one 10/10.
  - The finish alone won 8/10.
  - The final light finish won 7, tied 3 and lost none.

### Global by default
- Place resolution order: a `Locale:` line (job > jobs file > `--locale` > style lock), then a place the brief names, then a global neutral setting.
- **Country logic** for 77 countries (`scripts/locales.json`): traffic side, signage script and seasons.
- **`locale` command**, also run inside `audit`: detects a project's audience from its address, phone codes, postcodes, currency, domain, language and place names.
- Codex runs with `TZ=UTC`.
- Global batches rotate the main person's background. Shop signs get invented names.

### Website, app and brand assets
- New commands:
  - `export`: AVIF/WebP/JPEG, widths, blur placeholder, `<picture>` markup and `assets.json`
  - `favicon`
  - `og`
  - `cutout`
  - `audit`
  - `doctor --setup`: skill venv with Pillow
- Batch style lock; `transparent` jobs with alpha refine and grey-backdrop judging; `--export-dir`; `--max-images`.

### Fast mode
- Features:
  - compiled prompts with prompt-time judge checks
  - lean parallel Codex sessions
  - two candidates with early exit for complex briefs
  - parallel judges
  - verdict v2 (`PASS_WITH_NOTES`)
  - `model_limit` skip
  - telemetry
- 10 complex briefs: 36.8 → 3.5 min.

### Foundations
- Codex CLI engine (ChatGPT login, no API key), agent mode with self-QA, and an optional API engine.
- Physics and hand-object rules; the independent judge with physics and hand-object traces.
- Master doc `references/master.md`.
