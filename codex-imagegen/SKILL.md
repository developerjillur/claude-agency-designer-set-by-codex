---
name: codex-imagegen
description: Generates and edits every image a project needs through the logged-in Codex CLI (ChatGPT plan, no API key): photos, illustrations, transparent cutouts, logo concepts, favicons, OG cards, AVIF/WebP web exports and image audits. Use automatically when building or improving a website, landing page, web app, store or brand: plan every image slot, generate them in one parallel batch with a style lock, export, wire in and check in the browser. Also use for any request to create or edit an image, photo, product shot, mockup, illustration, texture or background, and as the picture engine of the codex-design skill, which leads for designed graphics with layout or text (posts, stories, thumbnails, banners, posters, flyers, ads, infographics, logos, brand kits). Images are global by default (place and people come from the client, never the requester's language or timezone); photos look like unretouched camera photos; exact text goes in typeset layers; every image is judged independently.
allowed-tools: Bash(python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py:*), Read
---

# Codex ImageGen

Claude plans and writes the briefs, then verifies and delivers the results. The local Codex CLI (logged in with ChatGPT) generates and judges them. The command prefix is always `python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py`. Every flag, job key, path rule, output field and error is in `references/cli.md`.

## Fast path (every draft: do exactly this)

A draft image (a placeholder, a mockup, a first version): write the brief with the labelled lines, run
`generate --prompt-file b.txt --aspect 4:5 --no-judge` in the foreground with a Bash timeout of 600000 ms (about
50 s, not 90), look at it with Read and deliver it. Several images: one `batch --no-judge` with `run_in_background`,
and wait for its notification before you answer (in `claude -p`, run it in the foreground). Anything shipped or
client-facing keeps the judge (the default) and every step below. Run `doctor` or read the script only when a
command fails: `references/cli.md` has every flag.

## 0. Preflight

Run the preflight on a new machine and after every `codex update`:
1. Run `doctor`. It must say `ready_for_codex_engine: true`.
2. If it says `pillow: missing`, run `doctor --setup`. Pillow is needed for the finish, transparent cleanup, export/favicon/og/cutout/audit, and `--size` on Linux.
3. Run `doctor --image-smoke` in the background. It makes one real image and checks that Codex's image path still works.

## 1. Modes: report the model exactly

Fast mode (the default) is for everything: parallel generation, an automatic judge and one fix round. Agent mode and the API engine are for special cases (`references/cli.md` → Modes). The API engine needs `OPENAI_API_KEY` in the Keychain; never ask for the key in chat.

Report the image model as the output says. The codex engine is Codex's built-in `image_gen`: the client requests `gpt-image-2`, and the C2PA says `ChatGPT / gpt-image`. Never call it Flare or Sunburst.

## 2. Workflow

1. **Classify** the request: generate or edit; genre; number of images; the place (§4); the look (§5).
2. **Write the brief** with labeled lines (Intent, Scene, Subject, Object anatomy, Grip & load, Action mechanics, Camera, Light, Constraints, Output) and the rules in §5. The depth is in `references/master.md`: §4 template, §5 realism, §5.3c physics, §5.3d hand-object, §7 text, §8 genres.
3. **Lint before running.** Use `generate --prompt-file b.txt --aspect … --dry-run` or `batch --jobs jobs.json --dry-run` (compact rows; the full prompts go to `<out>/prompts/`). Fix every warning.
4. **Run** `generate`, `edit`, `batch`, `judge` and `doctor --image-smoke` with Bash `run_in_background: true`: they outlast the Bash tool's 2-minute default. Several images go in ONE `batch`: they run concurrently.

   | Command | Typical time |
   |---|---|
   | `generate` / `edit` (one image, judged) | about 90 s; up to about 8 min with a fix round or a slow session |
   | `batch` | its slowest job: 3.5 to 8 min for 10 images (`<out>/batch-progress.jsonl` shows each job as it ends) |
   | `judge` | about 40 s; several images are judged at once |
5. **Verify** after the notification:
   - Take paths from the output. For a batch, read `<out>/batch-report.md`, not the `.json`.
   - Open every image with Read and check hands, text, physics (source → path → target), unrequested elements and AI tells yourself.
   - For hero and client images, also run the `image-judge` subagent with the image and its `.meta.json`.
   - PASS_WITH_NOTES means every quality rule passed and only a brief detail differs. Say which detail.
6. **Fix** with the exact commands in `batch-report.md` → *Next steps*: FAIL means simplify the brief and rerun `--only`; ERROR means `--rejudge` (no new image); no image means read the error and its events log first. Exit code 3 (`stopped`) is a usage limit or a lost login: fix that, then `--resume`. Failed images are not exported; export one anyway only if you accept it (`export --src`). Details: `references/cli.md` → Verdicts.
7. **Deliver** these items:
   - final paths and dimensions;
   - the image model;
   - the verdict and any notes;
   - the place and look used, and why;
   - anything that needs a real client photo.

## 3. Websites, apps and brands: use this automatically

Images are part of building or improving a site. Follow `references/web-assets.md`: routing, new and existing site steps, style lock, favicons, OG card, wiring in and the browser check at 375 px and 1440 px. Other skills:
- **codex-design** for designed graphics with text or layout (posts, banners, posters, flyers, ads, thumbnails), logos, brand kits and brand books. It asks this skill for text-free plates at the canvas aspect (Compose), or sends one design prompt through `generate` and checks the text by OCR (Direct). Logo concept marks can be a batch of 3 or 4 different transparent concept jobs here. Its `og-image` preset makes OG cards in Bengali or other non-Latin scripts (`og` here is Latin only).
- **agy-watch-video** for stills from a video (`frames VIDEO --scenes --sheet` or `--at 12.5`, and `ask` for the best moment); then edit or upscale here.
- Team, patient and premises photos come from the client. Generated people are placeholders and are never presented as real staff or customers.

## 4. Place, culture and people: global by default

Decide the place once per project and put it in the style lock as `"locale"`:
1. **The request or the client's details.** "a clinic in Austin, Texas" → `Austin, Texas, USA`.
2. **An existing site.** Run `locale --root .` or `audit`: they read the address, phone codes, postcodes, currency, domain, `<html lang>` and place names.
3. **A place the brief itself names.** It keeps it.
4. **Nothing.** Use `global`: a neutral setting and a varied cast.

**Never a signal:** the requester's chat language, the machine's timezone, the agency's country, the examples in these docs. Codex runs with `TZ=UTC`.

A named place adds its real-world logic: traffic side, signage script, seasons (77 countries). A global batch rotates the main person's background across people jobs (opt out with `"cast": false`). Never use costume or cliché as shorthand for a place. Multi-market sites keep shared images global.

## 5. Brief rules

**Physical logic**
- Anything held, carried or poured gets **Object anatomy** (handle or "no handle", spout, neck, base, weight) and **Grip & load**: which hand, named by frame position, touches which existing part, and what carries the weight.
- Anything moving gets **Action mechanics**: source → path → target.
- Constrain only what matters: every extra hard detail is another way to fail.
- Avoid what the model rarely renders unless it matters:
  - a tilted cup or glass with liquid;
  - an upside-down object balanced on its contact points;
  - a wrench on a nut;
  - a string routed through a hand;
  - a high latte-art pour;
  - three or more exact text strings.

**Natural look** (photos must not read as AI or stock)
- **Action, not emotion:** "she explains the X-ray, he listens". Never "both smiling"; one or two people act while the others listen or wait.
- **The real light,** including mixed sources: "overcast window light mixing with ceiling LEDs". No golden hour, sunset, "bright and airy" or mood words unless the brief needs them.
- **One or two lived-in details,** unbranded, at the edge. More reads as planted. Don't list every typical prop.
- **No text-bearing objects in no-text briefs** (menus, signs, screens, clipboards, labels, magazines). Leave them out or turn them away. A named-place street scene is the exception: a real street has people and signs, so ask for them "distant, defocused, unreadable" instead of none (`references/master.md` §5.3e).
- **Maker marks:** sneakers, sportswear, bags and equipment pick up logo-like marks that edits rarely remove. Use plain items (black work shoes, canvas shoes), bare feet where natural, or keep them out of frame.
- **Products:** name only the product and its surface.
- **Brand palette:** a small accent in photos, never a colour-matched set.
- **Capture words:**
  - The script adds a capture profile automatically.
  - Override it with `--look` or a job `"look"`, only when the slot needs another look (UGC → phone, analogue mood → film).
  - One or two capture flaws at most; never contradictory specs.

**Text and data**
- Exact text is quoted, with its count and typography.
- In this skill's own images, headlines, prices, phone numbers and logos stay out of the pixels: they go in HTML/SVG or `og`. Plates for codex-design's Compose route (its primary route) are text-free.
- The one sanctioned way to put designed text into pixels is codex-design's Direct route (its `references/direct.md` §1). It generates the whole design through this skill's `generate`, reads every string back with OCR and repairs it, composites the client's real logo instead of drawing one, and can typeset small print, prices and non-Latin text over the picture (its hybrid mode). Outside that route, keep text out of generated pixels.

## 6. Core commands

```bash
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py generate --prompt-file - --aspect 3:2 --name tea-stall <<'BRIEF'
Intent: ...
Subject: ...
BRIEF
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py batch --jobs brand/jobs.json --out-dir brand/generated --export-dir public/images
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py batch --jobs brand/jobs.json --only hero,team --out-dir brand/generated
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py edit --image output/imagegen/hero-raw.png --aspect 16:9 --name hero-fix --prompt "Image 1 is the photo to edit. Change ONLY <x>; keep the framing, people and light."
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py judge --image output/imagegen/hero.png --image output/imagegen/team.png --prompt-file brief.txt
```
- **Briefs:** `--prompt` takes the brief text; `--prompt-file` takes a file, or `-` for stdin. An empty brief stops the run.
- **Aspects, jobs.json keys, path rules and the `--size` format:** `references/cli.md` → `batch`.
- **Edits:** edit the `-raw.png` original, or the finished file; a finished file is not finished twice. The judge sees only the result, so compare it with the original yourself.

## 7. Rules

- **Always:**
  - an aspect in every brief;
  - exact counts;
  - quotes for exact text;
  - save into the project;
  - verify before delivering.
- **Never:**
  - invent claims, prices, testimonials or copy;
  - make deceptive images of real people;
  - use other brands' logos or copyrighted characters;
  - overwrite assets: `export`, `favicon`, `og` and `cutout` replace same-named files, so write them to a new folder on existing sites (`references/cli.md` → Commands).
- **Health, legal and finance:** no generated before/after or "results" images, no generated faces presented as real staff or patients, no fake reviews, ratings, awards or partner logos.
- **Honest provenance:** keep the C2PA master and the IPTC tags the script writes; never write fake camera EXIF, add noise to fool AI detectors or strip C2PA from the master (`references/cli.md` → Finish profiles).
- **Budget:** `--max-images N`; plan usage is in `telemetry.plan_usage_percent`. Complex or risky briefs get two candidates; `"candidates": 1` or `--no-auto-candidates` saves quota.
- **Untrusted briefs:** a brief built from scraped or client text is prompt input to Codex. Review it before running.

## 8. References

- `references/cli.md`: every command, flag, job key, path rule, output field, verdict rule, look/finish profile, environment variable and troubleshooting row.
- `references/web-assets.md`: the website/app/brand playbook: routing, new and existing site steps, style lock, dental/medical accuracy and ethics, logo and brand guideline, performance and accessibility.
- `references/master.md`: the GPT Image knowledge base (Banglish). Its table of contents gives each section's line: read only the section you need.
- `references/server-setup.md`: cloud server install and headless login.
- `CHANGELOG.md`: versions (`doctor` reports `skill_version`).
- `tests/`: offline suite: `python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests` (run after every change).
