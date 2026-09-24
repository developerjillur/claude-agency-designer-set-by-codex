# Website, brand and app asset playbook

Use this whenever you build, redesign or improve a website, landing page, web app or brand. You own every visual asset end to end: plan it, produce it, optimize it, wire it into the code and verify it in the browser. Never ship placeholder services (via.placeholder, picsum, empty grey boxes) or unoptimized PNGs.

## 1. Routing: which tool makes which asset

| Asset | Make it with | Why |
|---|---|---|
| Hero, section, service, lifestyle, interior, product photos | `batch` (fast mode) with a shared style lock, then `--export-dir` | Photoreal raster; one batch = one consistent look |
| Illustrations, spot illustrations, 3D/clay icons | `batch` jobs whose Intent/Style line (or the style lock's `style`) names the medium ("flat vector illustration", "soft clay 3D"); `"transparent": true` on coloured sections | Raster art with native alpha; no camera line, photo rules or grain |
| Layered hero (subject over a background) | two jobs: a background plate with no subject + a transparent subject; combine in HTML/CSS | Layers stay editable; text never baked in |
| Logo | Claude writes the SVG (mark + wordmark). Optional first step: one `batch` of 3–4 `"transparent": true` concept jobs, each its own idea (monogram, abstract symbol, pictogram), then redraw the chosen one as SVG (`--explore` only varies camera angle) | Logos must be vector, crisp, editable, exact text |
| UI icons (nav, features, contact, social) | The project's icon library (lucide, heroicons, phosphor) or hand-written SVG on the same grid and stroke | Consistent, tiny, themeable with `currentColor` |
| Domain icons missing from libraries (tooth, implant, braces) | Hand-written SVG in the library's style (24×24 grid, same stroke width, round caps) | Matches the rest of the set |
| Favicons + app icons + manifest | `favicon --src brand/logo-mark.svg|png --out public` | All sizes, `.ico`, maskable, `site.webmanifest`, `<head>` tags |
| Social / OG card | `og --bg <hero> --title "…" --logo …` (1200×630) | Text is typeset, never generated |
| Backgrounds, textures | CSS gradients first; generated plates only when a photo or texture is needed (low contrast, no subject) | Performance and legibility |
| Cutout of an existing flat-background photo | `cutout --src …` | Border-connected background removal; interior kept |
| Existing site images | `audit --root .` then replace, re-export or add | Finds missing alt, placeholders, heavy, oversized and broken images |

## 2. New site: step by step

1. **Read the project.** Framework (Next.js, Vite, Astro, plain HTML), the public/static folder, the existing brand (logo, colors in CSS or Tailwind config, fonts), pages and sections. List every image slot. Decide the place (SKILL.md §4): the client's city and country from the request or the content (`locale --root . --text "<request>"`); when nothing names one, use `global`. The language the requester writes in is not the audience.
2. **Brand kit** (if the client has none): write `brand/BRAND.md`: name, voice, palette (hex + role), type pair (web fonts), logo usage (clear space, minimum size, mono and reversed versions), imagery style, icon style, do/don't; and `brand/style.json`, the style lock every image shares, including its `"locale"` (§4).
3. **Logo**: write `brand/logo.svg` (full color), `brand/logo-mono.svg` (`currentColor`) and `brand/logo-mark.svg` (square mark only). Never ship a generated raster logo as the master.
4. **Asset plan** → `brand/jobs.json`: one entry per slot with `name`, `aspect`, `brief`, `alt`, and `"eager": true` for the first (LCP) image. The top-level `"style"` points to the style lock. One hero per page, one image per section that needs one; skip decoration CSS can draw.
5. **Lint, then generate + export in one call** (all images run concurrently):
   `… batch --jobs brand/jobs.json --dry-run` (fix every lint warning), then
   `python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py batch --jobs brand/jobs.json --out-dir brand/generated --export-dir public/images`
   Only PASS and PASS_WITH_NOTES images are exported. Compare `assets.json` with the job list; `batch-report.md` → *Next steps* gives each failure's cause and the `--only` rerun command. Add `brand/generated/logs/` to `.gitignore` (Codex prompts and event streams) and commit only the masters you keep.
6. **Favicons**: `… favicon --src brand/logo-mark.svg --out public --name "<Brand>" --theme "<primary hex>"` (SVG needs `rsvg-convert`, `cairosvg` or macOS Quick Look; otherwise pass a 1024 px PNG of the mark).
7. **OG card**: `… og --bg brand/generated/<hero>.png --title "<exact headline>" --subtitle "<exact line>" --logo brand/logo.svg --accent "<primary hex>" --font <brand bold .ttf> --out public/og.png`. Latin script only (render Bangla or other scripts from HTML); use the absolute `https://<domain>/og.png` in `og:image`.
8. **Integrate** from `public/images/assets.json` (relative paths only; pass `--url-prefix /images` when the export folder is not under public/static/www): paste each `html` `<picture>` block (plain HTML, Astro, Vite), or use the framework component (Next.js `<Image src width height alt placeholder="blur" blurDataURL>`). Background photos: CSS `image-set()` with the AVIF/WebP variants. Add the favicon `<link>` tags and OG `<meta>` tags. Text always lives in HTML, never inside images.
9. **Verify in the browser**: start the dev server, check every image loads, crops work at 375 px and 1440 px, no layout shift, the hero is the LCP element, the total image weight is reasonable (hero AVIF ≲ 250 KB).
10. **Report**: assets made, verdicts (`PASS_WITH_NOTES` details), and anything that needs a real photo from the client.

## 3. Improving an existing site

1. `… audit --root . --out audit.json` → counts of missing-alt, no-dimensions, placeholder-url, stock/placeholder files, heavy, oversized, broken references and unreferenced files, plus a `locale` block (suggested place, confidence, markets).
2. For each image decide: **keep** (re-export only: `export --src …`), **replace** (same role and aspect, new image with the site's style lock), or **add** (missing visuals).
3. Derive the style lock from the existing brand (colors, fonts, current photography) so new images match; take `"locale"` from the audit's locale block (confirm with the client when it is `ambiguous`).
4. Write new files and update the references in code; fix alt text and width/height while there. Generation never overwrites, but `export`, `favicon`, `og` and `cutout` replace same-named files: write them to a new folder (`public/images-new`, `public/_icons-new`), review, then merge (merge `site.webmanifest` by hand).
5. Re-run `audit`: missing-alt, no-dimensions, placeholder-url, broken-ref and heavy counts should drop (`srcset` variants count as referenced; generated masters with `.meta.json` are skipped).

## 4. Style lock (brand DNA): `brand/style.json`

```json
{
  "palette": ["#0E7490 teal (primary)", "#F8FAFC off-white", "#FDE68A warm accent"],
  "light": "the real light of the rooms: window daylight mixed with ceiling lights, brighter near windows, darker corners",
  "mood": "calm, competent, human; an ordinary working day",
  "people": "when people appear: ages, genders and backgrounds vary across the set; busy with the task, expressions in between",
  "materials": "light oak, matte white surfaces, normal wear",
  "color_grade": "neutral white balance, true-to-life colour, not oversaturated",
  "avoid": "cinematic grading, golden-hour glow, colour-matched sets, text or logos in images, posed smiles",
  "locale": "global"
}
```
Every job of the set gets this block appended, so the judge checks it too (instruction following, brief fidelity). In photos the palette appears only as small accents (at most one small object), never as a colour-matched set. Leave `look` out: each job then gets the capture profile its intent needs (a style-lock `look` would force one profile and finish on every photo, product shots included). A `"style": "flat vector illustration"` key makes the whole set non-photo.
`locale` is `"City, Country"` when the business has a place (from the request, `locale` or `audit`) and `"global"` otherwise. The script turns it into place rules plus the country's real-world checks (traffic side, signage script, seasons). A job can override it with its own `"locale"`.

## 5. Dental and medical sites

**Typical slots:** hero (a welcoming reception, or a dentist talking with a relaxed patient), services (check-up and cleaning, whitening, implants, orthodontics/clear aligners, pediatric, emergency), technology (intraoral scanner, digital X-ray screen), clinic interior, CTA background, spot illustrations (tooth, aligner, implant; transparent), team section (real photos from the client; generated people only as clearly marked placeholders).

**Accuracy the judge checks:** gloves and a mask whenever hands are near a patient's mouth; patient bib and protective glasses during treatment; dental chair with overhead light, instrument tray and suction; correct tooth anatomy and a natural smile (no uniform "piano-key" teeth); hygienic, calm, well-lit rooms; no blood, no close-up needles, no graphic procedures.

**Ethics, hard rules:**
- No generated before/after, "results" or smile-transformation images presented as real outcomes.
- No generated faces presented as the clinic's real dentists, staff or patients (no names, titles or credentials on generated people).
- No fake testimonials, star ratings, awards, certifications or association and insurer logos.
- No treatment claims inside images; claims belong in reviewed copy.

**Example `brand/jobs.json`:**
```json
{
  "style": "brand/style.json",
  "locale": "Austin, Texas, USA",
  "jobs": [
    {"name": "home-hero", "aspect": "16:9", "eager": true,
     "alt": "Dentist showing a patient a jaw model in a treatment room",
     "brief": "Intent: website hero photo for a family dental clinic\nScene: a working treatment room mid-morning: dental chair, the overhead light swung aside, an instrument tray, a paper cup of water\nSubject: exactly one dentist (mask pulled down, gloves on, seated) shows something on a plastic model of a jaw; exactly one adult patient in the chair listens\nLight: overcast daylight from the window on the left mixing with the cooler ceiling LEDs\nConstraints: no text, logos or watermark\nOutput: calm empty space on the right third for the headline"},
    {"name": "service-cleaning", "aspect": "4:3", "alt": "Hygienist cleaning a patient's teeth",
     "brief": "Intent: service card photo\nSubject: exactly one hygienist (gloves, mask) cleaning the teeth of exactly one patient wearing a bib and protective glasses\nObject anatomy: a small dental mirror, a hand scaler, and a saliva ejector hooked over the lower lip\nGrip & load: the hand on the viewer's right holds the scaler in a pen grip; the other hand holds the mirror\nCamera: close three-quarter view\nConstraints: no blood, no text, no logos"},
    {"name": "icon-aligner", "aspect": "1:1", "transparent": true, "alt": "",
     "brief": "Intent: spot illustration for the clear aligners service\nSubject: exactly one transparent clear aligner tray, isolated\nStyle: soft clay 3D look in the brand palette\nConstraints: no text"}
  ]
}
```

## 6. Logo and brand guideline details

- **Mark**: simple geometry that survives 16 px (favicon); one or two colors.
- **Wordmark**: a real typeface (check the license; Google Fonts are safe), letter-spacing tuned, converted to paths in the master SVG.
- **Files**: `logo.svg`, `logo-mono.svg` (`fill="currentColor"`), `logo-reversed.svg` (dark backgrounds), `logo-mark.svg`, `logo-mark-1024.png` (favicons and social).
- **BRAND.md sections**: purpose and voice; logo (versions, clear space = half the mark height, minimum size, misuse); color (hex, RGB, role, contrast pairs meeting WCAG AA); typography (families, weights, scale); imagery (the style lock in words + approved sample images); iconography (library, stroke, size); UI (radius, shadows); do/don't.
- Optional brand board: one moodboard image from the style lock for presentations (never a production asset).

## 7. Performance and accessibility checklist

- AVIF + WebP + JPEG (PNG for alpha) via `export`; `width`/`height` on every `<img>`; `loading="lazy"` except the LCP image (`eager`, `fetchpriority="high"`); a real `sizes` attribute for images that are not full width.
- Meaningful `alt` that says what the image shows in context; decorative images `alt=""`.
- Keep text, prices, phone numbers and logos out of generated pixels (HTML/SVG only).
- Keep the `-raw.png` masters (the only files with the signed C2PA manifest) and ship the derivatives; finished files and exports of generated images carry the IPTC `trainedAlgorithmicMedia` tag.

## 8. Place, culture and people

- **New site:** the place comes from the request or the client's content (address, phone, currency). When nothing names a place, use `global`: neutral settings and a varied cast across the set. Never infer the place from the language the requester writes in, or from the machine's timezone.
- **Existing site:** `audit` (or `locale --root .`) reports the suggested place from schema.org address, phone codes, postcodes, currency, the site's own domain and email, `<html lang>`, `og:locale` and place names. Put it in the style lock.
- **Several markets** (hreflang or i18n locales): keep shared images global; give per-market pages their own `"locale"` jobs only where those pages differ.
- **Casting:** people are described by role, age and action. A named place's cast reflects its real present-day population, which is often diverse. In a `global` batch the script rotates the main person's background across the jobs that show people (opt out per job with `"cast": false`, per run with `--no-auto-cast`). Never use costume or cliché as shorthand for a place. Real team, doctor and patient photos come from the client.
- **Signage:** generated shop signs carry invented names, never real brands.
- **Check** the report's Place column (`global`, the locale, or `named in brief`) before delivery.
