# CLI reference: `codex_image.py`

`python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py <command> [flags]`. Every command prints JSON on stdout; logs go to stderr.

## Commands

| Command | Does | Overwrites? |
|---|---|---|
| `generate` / `edit` | One brief → 1–4 images (fast mode by default), judged and fixed | never (`-v2`) |
| `batch` | Many jobs from a JSON file, all concurrent, one report; `--resume`, `--rejudge` | never (`-v2`) |
| `judge` | Independent verdict for existing images, judged at once | none |
| `export` | AVIF/WebP/JPEG (PNG for alpha) widths + blur placeholder + `<picture>` + `assets.json` | **replaces** same-named variants and the `assets.json` entry |
| `favicon` | `.ico`, PNG sizes, apple/android/maskable, `site.webmanifest` | **replaces** (manifest rewritten whole) |
| `og` | 1200×630 social card, text typeset (Latin script only) | **replaces** `--out` |
| `cutout` | Transparent PNG from a flat-background image | **replaces** |
| `finish` | Photographic finish of existing photos | in place keeps `-raw.png`; `--out-dir` never overwrites |
| `audit` | Image inventory and issues of a site, plus its locale | none |
| `locale` | Where a project's audience is (site and/or text) | none |
| `doctor` | Health check; `--setup` venv with Pillow; `--image-smoke` real one-image test | none |
| `compare` | Same brief on several API models (needs `OPENAI_API_KEY`) | never |

On an existing site, write `export`/`favicon`/`og`/`cutout` output to a new folder first, review, then merge (merge `site.webmanifest` by hand).

## `generate` / `edit`

| Group | Flags |
|---|---|
| Brief | `--prompt TEXT` (the brief itself; a file name here gets a warning), `--prompt-file FILE` (`-` = stdin; a missing file stops the run), `--dry-run` (prints compiled prompt, checks, lint). An empty brief stops the run |
| Output | `--out FILE`, `--out-dir DIR` (default `<workdir>/output/imagegen`), `--name STEM` (letters, digits, `.-_`), `--workdir DIR`, `--log-dir DIR` |
| Frame | `--aspect` (below), `--size WxH` (centre crop + resize, keeps `-raw.png`; format below), `--n 1-4`, `--explore` (varies camera angle/framing only; useless for logos) |
| Look and place | `--look editorial\|portrait\|phone\|phone-flash\|film\|product\|interior\|auto\|none`, `--locale "City, Country"\|global`, `--style TEXT\|FILE` |
| Finish | `--finish natural\|portrait\|phone\|film\|clean\|auto\|none` (default auto: from the look; none for illustrations, transparent, and edits of finished files) |
| Transparent + web | `--transparent`, `--export-dir DIR`, `--alt`, `--eager`, `--url-prefix /images`, `--export-all` (also FAIL images) |
| Inputs | `edit --image TARGET` (required), `--ref PATH[=ROLE]` (≤ 5 images incl. target; fast mode ignores ROLE, so say in the brief what each image is for). Relative paths: the current folder, then `--workdir` |
| Judge and fix | judged by default in fast mode; `--no-judge`, `--fix-rounds N` (fast default 1, max 3), `--judge-effort` (fast default medium), `--judge-model`, `--judge-timeout 150`, `--threshold 4`, `--strict` (PASS_WITH_NOTES → FAIL) |
| Speed and cost | `--candidates 1-4`, `--no-auto-candidates`, `--no-early-exit`, `--concurrency 10`, `--max-images N`, `--timeout` (seconds per image session: fast default 480; agent mode and the API engine 900), `--gen-effort low`, `--prompt-writer compiled\|codex`, `--prompt-effort`, `--max-parallel`, `--judge-workers` |
| Agent mode (`--mode agent`) | `--effort xhigh`, `--codex-model`, `--max-attempts 2`, `--no-qa`, `--judge`, `--auto-fix` (judging only with these) |
| API engine (`--engine api`) | `--model`, `--tier draft\|final\|premium`, `--quality`, `--api-size`, `--mask`, `--raw-prompt` (send the brief without compiled layers) |

**Modes.** All modes get the compiled prompt: place rules, capture line, realism and physics checks, style lock, transparent background, finish.
- **Fast mode** (the default, for everything) adds: the automatic judge, candidates, early exit, `--export-dir` and `--max-images`.
- **Agent mode** (`--mode agent`, an art-director session with self-QA) suits short or vague briefs where Codex should art-direct one image.
- **The API engine** (`--engine api`) is for a specific 2.5 model, masks or exact sizes. It needs `OPENAI_API_KEY` (see Troubleshooting).
- Agent mode and the API engine judge only with `--judge` or `--auto-fix`.

**Failed sessions.** A session that stops for a reason Codex gives (an error event, a failed turn, its stderr) reports Codex's own words. Its event stream is kept, and the error names the file: `(events: <path>)`. The folder is `--log-dir`, else `<out-dir>/logs` (generate), `<out>/logs` (batch) or `./output/imagegen/logs` (judge). A quick failure is retried once. A timeout is not retried. A usage-limit or login error stops the whole run at once: `stopped` in the output, exit code 3.

## `batch`

`batch --jobs jobs.json [--out-dir DIR] [--export-dir public/images] [--only a,b] [--resume] [--rejudge] [--dry-run]` plus the fast-mode flags above.

```json
{"style": "brand/style.json", "locale": "global", "look": "editorial", "finish": "auto",
 "jobs": [{"name": "hero", "aspect": "16:9", "brief": "Intent: ...", "alt": "…", "eager": true}]}
```
- **Top-level keys** (all optional):
  - `style`: a style lock file or text, appended to every job.
  - `locale`, `look`, `finish`: defaults for every job.
- **Job keys:**
  - `name` and `brief` are required. The name must be a safe file stem. The brief is the text itself, not a file name.
  - Framing: `aspect`, `size`.
  - Web export: `alt`, `eager`, `sizes`, `widths` ([160, 320]), `export_name`.
  - Image: `transparent`, `refs` (paths), `target` (edit), `candidates` (1–4).
  - Overrides: `locale`, `look`, `finish`; `cast: false` (no auto-cast); `style`: a file, text or object that replaces the shared lock for this job, or `false` to skip the lock.
  - `args`: agent-mode extra flags.
- **Precedence:** job > jobs file > CLI flag > style lock.
- **Paths** (`style`, `refs`, `target`): absolute and `~` paths as given. A relative path is looked up next to the jobs file first, then in `--workdir` (default: the current folder), then in the current folder. So `brand/jobs.json` can say `"style": "style.json"` or `"style": "brand/style.json"`. A style value that ends in `.json`, `.txt`, `.md` or `.yaml` is a file: when it is not found, the run stops instead of using the file name as the style.
- **`size` format** (also `--size`): `WIDTHxHEIGHT` in pixels with a lowercase `x` and no spaces, like `1200x630`. `1200 x 630`, `1200X630` and `1200×630` are refused.
- **Validated before any Codex session:** JSON shape, names (unique), non-empty briefs, aspects, sizes, candidates (1–4), `refs` and `target` files (they must exist, at most 5 input images per job) and style files. Anything wrong stops with a one-line message.
- **`--only a,b`** reruns only those jobs. Casting stays as in the full set. Use the same `--out-dir`: new files get `-v2`, and `batch-report.*` then lists only those jobs.
- **`--resume`** (needs the same `--out-dir`): keeps every job whose image and `.meta.json` already passed (PASS or PASS_WITH_NOTES), runs only the others, and reports them all. Use it after a run that was cut short or stopped.
- **`--rejudge`** (needs the same `--out-dir`): judges the jobs' existing images again, all at once, from each newest `.meta.json` (the same brief, style lock and checks). No image is made. The meta file gets the new verdict. Add `--export-dir` to export the images that now pass. Use it for ERROR verdicts: `--only cup --rejudge`.
- **`--dry-run`** checks everything above, then prints one compact row per job (`name`, `lint`, `risks`, `place`, `look`, `finish`, `checks`, `prompt`) and writes each full compiled prompt to `<out>/prompts/<name>.txt` (the `prompt` field names the file). Use it to lint a new batch.
- **While it runs:** each job writes its `.meta.json` as it ends and adds a line to `<out>/batch-progress.jsonl` (`name`, `verdict`, `path`, `meta`, `error`). If the run is cut short, `batch-report.*` is still written, with the unfinished jobs listed.

## `judge`

`judge --image A.png [--image B.png …] (--prompt TEXT | --prompt-file FILE) [--judge-effort medium|high] [--timeout 150] [--threshold 4] [--judge-model M]`
- **`--image` repeats:** give one per image. Every path is checked before any judge starts. The images are judged at once (about 40 s in all), each in its own fresh read-only Codex session.
- **Effort:** `medium` by default. `high` gave the same pass/fail in tests and is slower.
- **Output:** one object for one image, a list for several, in the order given. Each has `image`, `computed_verdict` (PASS, PASS_WITH_NOTES, FAIL or ERROR), `score_total`, `gates`, `scores`, `defects`, `ai_tells`, the physics and hand-object traces, `fix_mode`, `fix_instruction`, `summary`, or `error` when that judge failed. One failed judge never hides the others' results.
- **A batch image:** use `batch --jobs … --only NAME --rejudge --out-dir DIR [--export-dir DIR]`, not `judge`. It judges with the stored brief, style lock and checks, updates the `.meta.json` and exports what passes. `judge` alone updates no meta file and exports nothing.

## Aspects

`1:1 3:2 2:3 4:3 3:4 4:5 5:4 16:9 9:16 21:9 3:1 1:3` (anything else is rejected). Codex has no size control. Native sizes seen:

| Aspect | Native size |
|---|---|
| 3:2 | 1536×1024 |
| 2:3 | 1024×1536 |
| 4:5 | 1122×1402 |
| 1:1 | 1254×1254 |
| 16:9 | 1672×941 |

A larger `--size` is upscaled, so choose the aspect of the final slot.

## Outputs

- **Files per job:**
  - `<name>.png`: the deliverable, or `<name>-v2.png` when that name exists; `--n` gives `-1` … `-4`.
  - Other candidates: `-c1`/`-c2`, `-first`, `-fix1`, `-regen1`.
  - `-raw.png`: the untouched original with its C2PA manifest.
  - `<name>.meta.json`: brief, compiled prompt, checks, place, look, finish, every candidate's judge result, timings, sessions.

  Take paths from the JSON; never guess them.
- **`generate` stdout:** `images[]` with these fields:
  - `path`, `verdict`, `first_pass`, `scores`, `defects`
  - `rounds`, `model_limit`, `remaining_fix`, `lint`, `place`, `look`, `meta`

  Plus `timing`, `passed` and `telemetry.plan_usage_percent`. An image that failed to export has `export_error`.
- **`batch` stdout:** only `out_dir`, `report` (the path of `batch-report.md`), `timing`, `passed`, `first_pass` and `[file, verdict]` pairs, plus `stopped`, `unfinished` and `export_errors` when there are any. It exits 0 even when jobs fail (`null` = no image). Read `batch-report.md`: it ends with **Next steps for failed images** and the exact command for each group. `batch-report.json` has the same `images[]` fields as `generate`; open it only for one field.
- **Agent mode summary:** `judge_verdict`, `judge_scores`, `judge_fix`, `judge_rounds`.
- **Exit codes:**
  - 0 = ran
  - 1 = refused (bad input, a missing file, missing Codex)
  - 2 = `generate` produced no image, or argparse rejected a flag
  - 3 = stopped: Codex reported a usage limit or a lost login (`stopped` has its words)

## Verdicts (computed in code, `--threshold 4`)

- **PASS:** every gate PASS/NA, every score ≥ 4, no critical defect.
- **PASS_WITH_NOTES:** usable; only brief precision is short. Conditions:
  - every quality gate passes (`text_exact`, `physics`, `hand_object`, `anatomy`, `no_unrequested_elements`);
  - realism, artifacts and physics_plausibility are ≥ 4;
  - no critical defect;
  - `instruction_following` FAIL and/or composition or brief_fidelity = 3.

  No fix round. `--strict` makes it FAIL.
- **FAIL:** anything else. Realism 3 (stock polish) is a FAIL. The image was rejected: simplify the brief and make a new one (`--only`).
- **ERROR:** the judge timed out, failed or returned no JSON. The image itself was never judged, so it is kept but not exported. Judge it again, no new image: `batch --only NAME --rejudge`.
- **No image** (no verdict): the generation session failed. Read the error and the events file it names, fix the cause, then rerun `--only`.
- **Fix rounds:**
  - One per FAIL: a local defect gets an "edit", a pose, grip or composition problem gets a "regenerate".
  - When the only remaining failure is a stray mark or word (`text_exact` / `no_unrequested_elements`) and the judge proposes an edit, one extra edit round runs.
- **`model_limit`:** set when 2+ candidates all failed quality gates that a local edit cannot fix. Lists those gates (e.g. `["physics"]`); the element is in `defects`. Simplify that element and rerun `--only`.

## Looks (capture profiles)

**Auto-selection:** decided by the brief's Intent/Camera/Style/Output lines, not by props. The first match wins:

| Look | Words that pick it |
|---|---|
| phone-flash | flash |
| phone | UGC, selfie, phone photo, Instagram, snapshot |
| film | 35mm film, film stock, disposable camera |
| product | product photo, packshot, online shop (only without people) |
| interior | interior photo, rental listing (only without people) |
| portrait | portrait, headshot |
| editorial | everything else |

**Overrides:**
- A brief that names a camera, phone or film stock keeps its own words (`brief`).
- The brief's focal length is kept, except for phone looks (24mm main camera).
- A prop like "a smartphone on the desk" does not pick the phone look.

## Finish profiles (after judging; the original stays `-raw.png`)

| Profile | Used for | White balance | Grain | Other |
|---|---|---|---|---|
| natural | editorial | 0.6 | 4 (fades in bright areas) | 0.3 px soften, vignette 0.08, saturation 0.97 |
| portrait | portrait | 0.6 | none | vignette 0.04, saturation 0.98 |
| phone | phone, phone-flash | 0.35 | 3.5 + colour noise | vignette 0.02 |
| film | film | 0.3 | 8, larger | halation, black lift, vignette 0.12 |
| clean | product, interior | 0.6 | none | none |

- **White balance** is shades-of-grey over near-neutral pixels. Highlights are protected and brightness is kept. Warm scenes (lamp, candle, neon, sunset) keep their warmth (`finish --warm` by hand).
- **Provenance:** a file counts as generated when it carries C2PA or the IPTC tag, or when the skill's own `<stem>.meta.json` names it as its `output_path`. Only such files are tagged `DigitalSourceType = trainedAlgorithmicMedia`. The tag carries over to finished files, `--size` crops, transparent cleanup and web exports. A client's photo is never tagged, even when it shares a stem with a generated file. The `-raw.png` master keeps the signed C2PA manifest. Never write fake camera EXIF, never add noise to fool AI detectors, and never strip C2PA from the master.
- **Finish marker:** a PNG finish marker stops a second finish when a finished file is edited.

## `locale`, `audit`, `export`, `favicon`, `og`, `cutout`, `finish`

- `locale --root DIR --text "request"` → `suggested`, `country`, `confidence`, `ambiguous`, `multi_locale`, `facts`, `signals`, `note`. `.env` and other dotfiles are never read.
- `audit --root DIR [--out FILE]` → the counts of each issue type:
  - `missing-alt`, `no-dimensions`, `placeholder-url`, `stock/placeholder`
  - `heavy`, `oversized`, `broken-ref?`, `unreferenced`

  Plus the `locale` block. `srcset` counts as a reference. Generated masters (with `.meta.json`), their candidates and `-vN` re-run attempts are skipped.
- `export --src FILES|DIRS --out DIR [--widths 480,768 --formats avif,webp,jpg --quality 80 --alt TEXT --alt-json FILE --sizes "(max-width: 900px) 100vw, 560px" --eager --url-prefix /images]`. Widths are never upscaled. `assets.json` holds relative paths only. Pass `--url-prefix` when the folder is not under `public/`, `static/` or `www/`.
- `favicon --src logo-mark.svg|png --out DIR --name "Brand" --theme "#hex" [--bg "#hex"]`. SVG needs `rsvg-convert`, `cairosvg` or macOS Quick Look; otherwise pass a 1024 px PNG.
- `og --bg IMG --title "…" [--subtitle "…" --logo SVG|PNG --out public/og.png --font BOLD.ttf --font-regular REG.ttf --color "#fff" --accent "#hex" --size 1200x630]`. Latin script only; render other scripts from HTML (codex-design's `og-image` preset). Use the absolute `https://<domain>/og.png` in `og:image`.
- `audit --root` and `locale --root` must be an existing folder; a wrong path stops with a one-line error.
- Any command that meets a missing file or a bad value (for example `--widths 480px`) stops with one `ERROR:` line, not a traceback.
- `cutout --src FILES --out DIR [--key "#ffffff" --tolerance 12 --feather 0.6]`. The border-connected background is removed; the interior is kept.
- `finish --src FILE [--profile natural|portrait|phone|film|clean --out-dir DIR --warm --wb 0-1 --grain N --vignette 0-0.3]`.

## Environment

| Variable | Purpose |
|---|---|
| `CODEX_BIN` | Codex binary |
| `CODEX_HOME` | Codex home (`~/.codex`) |
| `CODEX_IMAGEGEN_MODE` | `fast` or `agent` |
| `CODEX_IMAGEGEN_EFFORT` | Agent effort |
| `CODEX_IMAGEGEN_FALLBACK_MODEL` | Agent mode and judge retry model (`gpt-5.5`) |
| `CODEX_IMAGEGEN_TZ` | Timezone for Codex sessions: `UTC` (default) or `system` |
| `CODEX_IMAGEGEN_KEEP_TMP=1` | Keep the run's temp folders for debugging |
| `CODEX_IMAGEGEN_FULL_FEATURES` | Do not switch off Codex memories and apps |
| `CODEX_IMAGEGEN_REASONING_SUMMARY` | Reasoning summaries: `none` or `detailed` |
| `CODEX_IMAGEGEN_WAIT_FOR_REPLY=1` | Wait for the image session's closing message instead of taking the batch result from its rollout the moment the call returns |
| `CODEX_IMAGEGEN_EXTRA_FLAGS` | Extra `codex exec` flags for every automated session, e.g. `-c mcp_servers.<name>.enabled=false`; A/B with `doctor --image-smoke` |
| `OPENAI_API_KEY` | API engine key (or macOS Keychain item `OPENAI_API_KEY`) |
| `OPENAI_BASE_URL` | API engine base URL |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `requires a newer version of Codex` | Agent mode and the judge retry with `-m gpt-5.5`; fast-mode image sessions do not. Run `codex update`, then `doctor --image-smoke` |
| Not logged in / no image tool | `codex login` (ChatGPT, not an API key; the Free plan has no image tool); `codex features list` → `image_generation stable true` |
| `no result from the Codex session` / another session error | A quick failure was already retried once. Read the events file the error names (`(events: …)`), fix the cause, then rerun with `--only <name>` |
| `timed out after 480s` | The session hung: real image sessions finish in 1 to 4 minutes, so a longer `--timeout` only means a longer wait. It is not retried. Rerun `--only <name>`; if it keeps hanging, run `doctor --image-smoke` |
| Exit code 3, `stopped: …usage limit…` or a login error | The whole run stopped at once: every later session would fail the same way. Wait until the plan's limit resets (the message says when), or run `codex login`. Then rerun the same batch with `--resume` |
| A job FAILs every time | Read `defects` and `remaining_fix` in `batch-report.md` → Next steps. The usual causes: a text-bearing object in a no-text brief, sneakers or sportswear with maker marks, a colour-matched or over-styled set, or a model limit. Simplify, then `--only` |
| `model_limit: [...]` | Simplify exactly that element (tilted liquid, upside-down object, tool on a fastener, string through a hand, three+ text strings) |
| Verdict `ERROR` | The judge failed twice or timed out; the image is kept unjudged and unexported and is listed under Next steps → ERROR. Judge it again with `batch --jobs … --only <name> --rejudge --out-dir <out>` (add `--export-dir` to export it when it passes). No new image is made |
| A batch was cut short (Ctrl-C, a killed task, a crash) | `batch-report.md` lists the unfinished jobs; finished jobs have their `.meta.json`. Rerun the same command with `--resume` |
| `style file not found` | A style value ending in `.json`, `.txt`, `.md` or `.yaml` is a file. Fix the path (relative paths: next to the jobs file, then `--workdir`), or write the style as text |
| `size must be WIDTHxHEIGHT …` | Write sizes like `1200x630`: a lowercase `x`, no spaces |
| `the brief is empty` / `brief file not found` | `--prompt-file` needs an existing, non-empty file (or `-` with text on stdin). To pass the brief as text, use `--prompt` |
| `this command needs Pillow` / `Pillow missing, no finish` | `doctor --setup` (needed for finish, transparent cleanup, grey-view judging, export/favicon/og/cutout/audit, `--size` on Linux) |
| `cannot rasterize SVG here` | Install librsvg (`brew install librsvg` / `apt install librsvg2-bin`) or pass a 1024 px PNG |
| `unknown aspect` / `invalid job name` | Use an aspect from the list above; names are letters, digits and `.-_` |
| `image budget (--max-images) exhausted` | Raise `--max-images` or rerun the rest with `--only` |
| `at most 5 input images` / `reference image not found` | The edit target plus references ≤ 5, and every file must exist (checked before any session) |
| Wrong dimensions | Choose the aspect of the slot; `--size WxH` centre-crops (`-raw.png` kept) |
| `compare` / `--engine api` says the key is missing | Store the key yourself: `security add-generic-password -a "$USER" -s OPENAI_API_KEY -w` (macOS) or export `OPENAI_API_KEY`. Never paste it into chat |
| Claude Code asks permission for every run | Add `"Bash(python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py:*)"` to `permissions.allow` |
