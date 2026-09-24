# R6 — Rendering, font, asset, image and PDF tooling for the design skill (macOS)

Research date: **2026-09-23**. Machine: Mac Studio, macOS 26.6.1 (25G76).
Scope: headless Chrome rendering to exact-size PNG/JPG and print PDF; font/icon/QR sourcing and caching;
QA hooks (overflow, safe zone, contrast, min size, upscaled images); image ops with Apple Vision; PDF post-processing
without Ghostscript. No rendering prototypes were run (only version checks, `ls`, metadata reads and read-only HTTP
fetches of docs, source code, package registries and font files).

**Evidence tags used below**

- **[V]** verified today: read in source code or official docs at the cited URL, or checked with a command on this Mac.
- **[D]** stated in vendor docs (cited), not exercised here.
- **[U]** unverified: inference, rule of thumb, or behaviour that needs the Chrome prototype to confirm.

---

## 0. TL;DR

1. **Chrome's CLI is usable but blind.** `--screenshot`, `--print-to-pdf` and `--dump-dom` run from one harness after the
   `load` event (plus an optional virtual-time budget). The CLI cannot wait on a JS "ready" signal, cannot
   pick the JPEG quality (it is fixed at 80), and returns a meaningless exit code. It is fine for a fallback or a
   smoke test. For the main path, drive the installed Chrome over CDP (`--remote-debugging-pipe`). That needs
   no dependencies (Python stdlib, or Node 26's built-in WebSocket), and the codex-design skill already does this. [V]
2. **Always pass** `--force-color-profile=srgb`, `--hide-scrollbars`, `--use-mock-keychain`, `--password-store=basic`,
   an explicit `--force-device-scale-factor` (CLI) or `Emulation.setDeviceMetricsOverride` (CDP), and a
   throwaway `--user-data-dir`. With `--print-to-pdf`, also pass `--no-pdf-header-footer`, because the header and footer are on by default. [V]
3. **PDF font gotcha.** Skia, Chrome's PDF backend, embeds a font as Type 3 glyph procedures instead of a real
   TrueType font in five cases: the font is variable; it is CFF/OTF-outlined; its fsType is "restricted" or
   bitmap-only; the text has a blur mask filter (for example a blurred text-shadow); or the glyph path was
   synthesised (fake bold). For print PDFs, use **static TrueType instances**, such as Fontsource static
   `.ttf`/`.woff2` files, or the per-weight static TTFs that Google Fonts serves to non-browser user agents.
   Also set `font-synthesis: none`. [V source]
4. **Chrome has no `bleed`/`marks`.** To add bleed, make `@page size` = trim + 2×bleed. Then write TrimBox and BleedBox
   with pypdf or pikepdf, and draw crop marks yourself if the printer wants them. WeasyPrint and Paged.js implement
   `bleed` and `marks` natively. [V]
5. **Bengali shaping:** Chrome (HarfBuzz) is correct. Pillow is correct only with raqm. Raqm can be switched on
   here with no install: `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` loads Homebrew's FriBiDi, after which
   Pillow reports raqm 0.10.1 active. Satori gained HarfBuzz shaping on 2026-08-20, but it is untested for Bengali. [V]
6. **Hyphenation on macOS Chrome uses CoreFoundation.** `hyphens: auto` works for en, de, fr, es, it, pt, nl, sv,
   da, nb, fi, ru, pl, cs, hu, uk, el, ca, hr, sk and ro. It does **not** work for bn, hi, ar, tr, id or vi. [V]
7. **Fonts:** the Fontsource API and its jsDelivr CDN need no key, are documented and can be version-pinned. The
   Google Fonts Developer API needs a key (a request without one returns 403). The google/fonts GitHub repo gives
   raw variable TTFs. [V]
8. **Vision:** Swift 6.3.3 ships with the Command Line Tools (SDK 26.5 with Vision.framework). Face rectangles need
   macOS 10.13; attention and objectness saliency need 10.15; subject lift needs 14; the new Swift API needs 15. [V]
9. **CMYK without Ghostscript** comes down to three honest options, in this order of preference:
   (a) deliver an sRGB vector PDF and let the printer's RIP convert it;
   (b) a raster CMYK PDF through Pillow and LittleCMS 2.17, which is present;
   (c) WeasyPrint ≥ 67 with `device-cmyk()`, which needs Python ≥ 3.10.
   macOS's built-in "Create Generic PDFX-3" Quartz filter flattens transparency at 72 dpi, so avoid it. [V]
10. **Python 3.9 is past end of life.** Several key libraries have dropped it: WeasyPrint ≥ 67, pikepdf ≥ 10, Playwright ≥ 1.61, rembg ≥ 2.0.62 and numpy ≥ 2.1. Homebrew
    python@3.12/3.14 and `uv` are already installed if you decide to move (your call). [V]

---

## 0.1 Environment facts (verified 2026-09-23)

| Item | Value | How checked |
|---|---|---|
| macOS | 26.6.1 (25G76) | `sw_vers` |
| Google Chrome | **153.0.8010.53** | `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version` |
| Chrome stable channel | 154.0.8037.57/58 released 2026-09-22 (Mac) — auto-update imminent | chromiumdash `fetch_releases` |
| Cached test browsers | Chrome for Testing 152.0.7977.54 and chrome-headless-shell 152.0.7977.54 in `~/.cache/puppeteer/…`; Playwright chromium + chromium_headless_shell builds 1223–1243 in `~/Library/Caches/ms-playwright/` | `ls`, `--version` |
| Swift | Apple Swift 6.3.3, target arm64-apple-macosx26.0; **Command Line Tools only** (`/Library/Developer/CommandLineTools`), SDK 26.5; `Vision.framework` (with `.swiftinterface`), CoreImage, ImageIO, PDFKit, Quartz present in the SDK | `swift --version`, `xcode-select -p`, `ls` SDK |
| Node / Deno | Node v26.7.0 (global `WebSocket` and `fetch` present); Deno 2.9.1 (`WebSocket` present) | `node -e`, `deno eval` |
| Python | `/usr/bin/python3` 3.9.6 (CLT). Venvs: `~/.claude/skills/codex-imagegen/.venv` (Pillow 11.3.0) and `~/.claude/skills/codex-design/.venv` (Pillow 11.3.0, fontTools 4.60.2, pypdf 6.19.0, segno 1.6.6, uharfbuzz 0.51.7) | `ls site-packages` |
| Pillow features | raqm **False** by default; littlecms2 2.17, freetype 2.13.3, webp 1.5.0, avif 1.3.0, libtiff 4.7.0: all True | `PIL.features.check` |
| Pillow + raqm | With `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` → raqm **True** 0.10.1, fribidi 1.0.16, harfbuzz 11.2.1 | same, env var set |
| Homebrew libs/tools | pango 1.57.1, cairo, harfbuzz, fribidi, little-cms2, fontconfig, freetype, **poppler 26.04.0** (`pdfinfo`, `pdffonts`, `pdftoppm`, `pdftotext`), python@3.12, python@3.14, `uv` | `ls /opt/homebrew/opt`, `command -v` |
| Absent | gs, ImageMagick (`magick`/`convert`), rsvg-convert, qpdf, mutool, weasyprint | `command -v` |
| ICC profiles | `/System/Library/ColorSync/Profiles/`: sRGB Profile, Display P3, AdobeRGB1998, **Generic CMYK Profile** (55 KB), Generic Gray/Lab/XYZ, ITU-709/2020, ROMM, ACEScg | `ls` |
| Quartz filters | `/System/Library/Filters/Create Generic PDFX-3 Document.qfilter` (see §7.4) | `plutil -p` |

---

## 1. Headless Chrome from the command line (current "new headless")

### 1.1 Modes and binaries

- Since **Chrome 132**, the Chrome binary has contained only the new headless mode. `--headless` and `--headless=new`
  are the same; `--headless=old` prints an error. The old implementation lives on as a separate binary,
  **chrome-headless-shell**, built for every release since Chrome 120 and downloadable from Chrome for Testing
  (`npx @puppeteer/browsers install chrome-headless-shell@stable`). [D: developer.chrome.com "Removing
  --headless=old from Chrome", 2024-10-23; "Chrome Headless mode" page, updated 2024-10-21]. A 152 build is
  already cached locally (§0.1).
- New headless is the real Chrome browser: same Blink, Skia, fonts and printing. On macOS, since late 2025, it turns
  itself into a background-only process, so there is no Dock icon or menu bar (`TransformProcessType`). [V:
  `chrome/browser/headless/headless_mode_platform_mac.mm`, commit "Improve headless mode Chrome dock/menu hiding
  on Mac", 2025-11-17]
- Headless start-up automatically adds `--no-first-run` and `--no-error-dialogs`. If no `--user-data-dir` is given,
  it also runs **incognito** in a **unique temporary profile** under `~/Library/Application Support/Google/Chrome-headless/<random>`,
  which is deleted on a clean exit. Parallel runs are therefore safe even without a profile flag.
  [V: `chrome/browser/headless/headless_mode_init.cc`, main, 2026]
- Virtual screen: the default is **800×600 at DPR 1.0**. `--screen-info={0,0 1600x1200 devicePixelRatio=2}`
  configures it (Chrome ≥ 142). [V: `components/headless/screen_info/README.md`; D: developer.chrome.com
  "Configure virtual screens in Headless mode", updated 2026-01-13]

### 1.2 What the CLI actually does (read from Chromium source)

The whole CLI command path is a small CDP script: `components/headless/command_handler/headless_command.js`,
driven by `headless_command_handler.cc` (main as of 2026-09-23). The sequence is:

1. Create a target at `about:blank` → `Page.navigate(url)` → wait for the **`load` lifecycle event** of that frame.
   `--timeout=ms` races this; on timeout it calls `Page.stopLoading()`. [V]
2. If `--default-background-color` is set, call `Emulation.setDefaultBackgroundColorOverride`. This happens *after* load. [V]
3. If `--virtual-time-budget=ms` is set, call `Emulation.setVirtualTimePolicy({policy: 'pauseIfNetworkFetchesPending', budget,
   maxVirtualTimeTaskStarvationCount: 9999})` and wait for `virtualTimeBudgetExpired`. Virtual time does not advance
   while network fetches are pending; after that, timers are fast-forwarded. [V]
4. Run the commands in a fixed order: **`--dump-dom` → `--print-to-pdf` → `--screenshot`**. All three can be combined in
   one launch. [V]
   - dump-dom evaluates `XMLSerializer(doctype) + document.documentElement.outerHTML` and prints it to **stdout**.
   - printToPDF uses `{displayHeaderFooter: !--no-pdf-header-footer, generateTaggedPDF: !--disable-pdf-tagging,
     generateDocumentOutline: --generate-pdf-document-outline, printBackground: true, preferCSSPageSize: true}`.
   - screenshot calls `Page.captureScreenshot({format, clip:{0,0,W,H,scale:1}})`. The format comes from the file
     extension. When `--window-size` is present, it first calls `Browser.setContentsSize(W,H)`.
5. Output files are written, and a line "`<n> bytes written to file <path>`" goes to **stderr**.

Behaviour history that matters (version found with chromiumdash `fetch_commits`) [V]:

| Change | Commit date | First Chrome |
|---|---|---|
| `--print-to-pdf-no-header` removed; use `--no-pdf-header-footer` | 2023-10-03 | 120 |
| `--generate-pdf-document-outline` added | 2023-11-17 | 121 |
| Screenshot forced to `--window-size`. Before this, the new-headless screenshot came out shorter, because the tab strip and omnibox took space inside the window. | 2024-03-05 | 124 |
| `Browser.setContentsSize` makes the layout viewport exactly W×H. It is not clamped to the 800×600 virtual screen (`browser_handler.cc` resizes the window bounds directly). | 2026-03-10 | **148** |
| Page-load error handling: before this, a failed navigation or a download **hung forever**. | 2026-08-19 | **154** (installed 153 lacks it) |

**The exit code carries no information.** Chrome's startup code calls `CloseAllBrowsersAndQuit()` whatever the
handler's result was (`startup_browser_creator_impl.cc`). [V] Validate the results yourself: the file exists, its
size is non-zero, the PNG dimensions are right, and stderr contains no "Page load failed"/"Page load timed out".

### 1.3 Flag reference

| Flag | Meaning (source) | Use in our tool |
|---|---|---|
| `--headless` | New headless; the only mode in Chrome ≥ 132 [D] | always |
| `--screenshot[=/abs/out.png]` | Extension picks the format: `.png`, `.jpg`/`.jpeg`, `.webp`; anything else is an error. Default output is `./screenshot.png`. JPEG/WebP use CDP's default quality **80** (`kDefaultScreenshotQuality`), and the CLI has no quality option [V] | Write PNG, then encode JPEG/WebP with Pillow |
| `--window-size=W,H` (`,` or `x`) | With `--screenshot`: clip W×H CSS px plus exact contents size (≥ 148) [V] | Always pass it |
| `--force-device-scale-factor=N` | ui/display switch that overrides the DSF for the browser UI and contents [V `ui/display/display_switches.cc`]. Chrome's own screenshot test pins it to 1 and expects exactly 2345×1234 for `--window-size=2345,1234` [V `headless_mode_command_browsertest.cc`] | Pass 1 explicitly. With 2, expect 2W×2H output **[U]** — verify in the prototype |
| `--screen-info={…}` | Virtual screen (origin, size, `devicePixelRatio`, `colorDepth`, `workArea*`, `isInternal`, `label`, `rotation`) [V] | Only if a design reads `screen.*` |
| `--hide-scrollbars` | Prevents scrollbars on web content, for consistent screenshots [V `content_switches.cc`] | always |
| `--default-background-color=RRGGBB[AA]` | Background used only where the page paints none. `00000000` = transparent. Applied after load [V] | Transparent PNG/WebP. Keep `html,body{background:transparent}` |
| `--virtual-time-budget=ms` | See §1.2 step 3 [V] | 5000–10000 for font/image settling |
| `--timeout=ms` | Stops a hung load. Commands still run if DOMContentLoaded fired [V] | 30000–60000 |
| `--dump-dom` | Serialized DOM to stdout [V] | QA results channel (§1.7) |
| `--print-to-pdf[=/abs/out.pdf]` | Default output `./output.pdf`. `printBackground` and `preferCSSPageSize` are **true** [V] | PDFs |
| `--no-pdf-header-footer` | Without it, Chrome prints date, title, URL and page number [V] | **Always** with PDFs |
| `--disable-pdf-tagging` | Skips the tagged-PDF structure tree (smaller file) [V] | Optional |
| `--generate-pdf-document-outline` | Bookmarks built from headings [V] | Brand-guideline PDFs |
| `--user-data-dir=DIR` | Profile location. If omitted, a unique temporary incognito profile is created (§1.1) [V]. Required, and must be non-default, for `--remote-debugging-*` since **Chrome 136** [D: blog "Changes to remote debugging switches", 2025-03-17] | `mktemp -d` per process; `rm -r` it after |
| `--force-color-profile=srgb` | Treats every display as sRGB (`ui/display/display_switches.cc`) [V]. Puppeteer and Playwright both pass it by default [V source] | **Always**, for colour-accurate PNGs |
| `--use-mock-keychain`, `--password-store=basic` | Avoid macOS Keychain prompts [D: chrome-launcher `chrome-flags-for-tools.md`] | always |
| `--run-all-compositor-stages-before-draw` | viz switch: waits for each compositor stage before completing a frame. Part of headless-shell `--deterministic-mode` [V `components/viz/common/switches.cc`] | Optional, harmless |
| `--disable-checker-imaging` | cc switch: never defer image decodes [V `cc/base/switches.cc`] | Optional for large photos |
| `--allow-file-access-from-files` | file:// pages may make CORS-mode requests (web fonts, module scripts, `fetch`) to other file:// URLs. Without it, `FileURLLoaderFactory` rejects CORS requests with `kCorsDisabledScheme` [V source] | Needed if fonts load from relative `file://` URLs. **Only render trusted HTML** |
| `--remote-debugging-pipe` | CDP over **fd 3 (Chrome reads)** and **fd 4 (Chrome writes)**, NUL-terminated JSON, or CBOR with `=cbor` [V `devtools_pipe_handler.cc`, Puppeteer `BrowserLauncher.ts`] | Driver mode (§2.1) |
| `--disable-extensions`, `--disable-background-networking`, `--disable-component-update`, `--disable-sync`, `--no-default-browser-check`, `--mute-audio` | Noise and network reduction (Puppeteer and Playwright defaults) [V] | yes |
| `--font-render-hinting=…` | Defined only in `//headless`, i.e. **chrome-headless-shell**. It has **no effect** in Google Chrome [V: the only definitions are `headless/public/switches.h` and `headless/lib/browser/command_line_handler.cc`] | Drop it; it is harmless but inert |
| `--disable-lazy-loading` | The CLI command processor adds it automatically [V `headless_command_processor.cc`] | n/a (CDP path: don't use `loading="lazy"`) |
| `--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1"` | Blocks all DNS except localhost, so an accidental CDN reference fails loudly **[U]** (a long-standing flag; not re-verified today) | Optional determinism guard |

### 1.4 Copy-paste commands

```sh
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/cd-chrome.XXXXXX")"
COMMON=(--headless --user-data-dir="$PROFILE" --force-color-profile=srgb --hide-scrollbars
        --use-mock-keychain --password-store=basic --no-default-browser-check
        --disable-extensions --disable-background-networking --disable-component-update --disable-sync
        --allow-file-access-from-files --run-all-compositor-stages-before-draw
        --virtual-time-budget=8000 --timeout=45000)

# 1) Exact-size PNG, 1080x1350 @1x (Instagram portrait)
"$CHROME" "${COMMON[@]}" --force-device-scale-factor=1 --window-size=1080,1350 \
  --screenshot="$PWD/out/post.png" "file://$PWD/job/post.html" 2> out/chrome.log

# 2) @2x raster (expected 2160x2700 — verify)
"$CHROME" "${COMMON[@]}" --force-device-scale-factor=2 --window-size=1080,1350 \
  --screenshot="$PWD/out/post@2x.png" "file://$PWD/job/post.html"

# 3) Transparent PNG (page must not paint html/body backgrounds)
"$CHROME" "${COMMON[@]}" --force-device-scale-factor=1 --window-size=1200,1200 \
  --default-background-color=00000000 --screenshot="$PWD/out/mark.png" "file://$PWD/job/mark.html"

# 4) Print PDF — size comes from CSS @page (preferCSSPageSize is on in the CLI)
"$CHROME" "${COMMON[@]}" --no-pdf-header-footer --generate-pdf-document-outline \
  --print-to-pdf="$PWD/out/flyer.pdf" "file://$PWD/job/flyer.html"

# 5) One launch: QA DOM to stdout + PNG (dump-dom runs first, then the screenshot, same page state)
"$CHROME" "${COMMON[@]}" --force-device-scale-factor=1 --window-size=1080,1080 \
  --dump-dom --screenshot="$PWD/out/card.png" "file://$PWD/job/card.html" > out/card.dom.html 2> out/card.log

rm -rf -- "$PROFILE"   # the path was printed/created above; never glob here
```

Python wrapper essentials: `subprocess.run(cmd, capture_output=True, text=True, timeout=120)`, which is required
because Chrome 153 can hang on a failed navigation. Then verify with Pillow that `Image.open(png).size == (W*N, H*N)`,
that stderr has no `Page load failed`/`Page load timed out`, and that the QA marker in the dumped DOM says `done`.

### 1.5 Waiting for web fonts and images

- **The CLI waits only for `load` and then the virtual-time budget.** Anything the page starts later, such as fonts first
  requested by a later layout or JS-inserted images, is covered only by the budget. Virtual time pauses while
  fetches are pending, so file:// and localhost loads are waited for. [V source] Whether `document.fonts.ready`
  chains always settle inside the budget is **[U]**: make the page write a completion marker, and treat a
  missing marker as failure. Retry with a larger budget.
- **In the page:** `document.fonts.ready` resolves as soon as no font loads are *pending*, so it can resolve before any face was
  requested. Force layout (`document.body.offsetHeight`) and explicitly `await document.fonts.load('700 48px "Noto Sans
  Bengali"', 'বাংলা')` for every face/weight/script the design uses. Then `await Promise.all([...document.images].map(i =>
  i.decode().catch(()=>null)))`, and preload CSS background images with `new Image()` + `decode()`. [D: CSS Font Loading
  spec semantics; the codex-design `SETTLE_JS` already does the fonts.ready + decode part]
- **Local fonts.** Web-font fetches are CORS-mode. From a `file://` page they need `--allow-file-access-from-files`,
  a localhost HTTP server, or `data:` URIs. [V source analysis; exact console error **[U]**] Use `font-display: block`
  so a late face never paints a fallback.
- **Detecting fallback:** with CDP, `CSS.getPlatformFontsForNode(nodeId)` returns `{familyName, postScriptName,
  isCustomFont, glyphCount}` per text node. That is exact evidence that a system font drew some glyphs. [V protocol
  JSON] CLI-only alternative: check code-point coverage in Python against the font's `cmap` (fontTools
  `getBestCmap()`), or the width-probe trick with the OFL zero-width font **Adobe Blank 2**
  (`https://raw.githubusercontent.com/adobe-fonts/adobe-blank-2/master/AdobeBlank2.ttf`, 2.3 KB). **[U]** technique

### 1.6 `--print-to-pdf` with CSS `@page` (custom sizes, bleed)

- **Page size:** the CLI sets `preferCSSPageSize: true`, so `@page { size: 216mm 303mm }` wins. Without CSS it falls back
  to Letter. [V] Chrome now computes page sizes as floats (`ConvertUnitFloat`), so fractional point sizes are
  expected. Check with `pdfinfo -box`. [V source; output **[U]**]
- **Margins:** printToPDF defaults to 1 cm custom margins, but CSS `@page` margins are honoured: the headless
  `PrintWithParams` path never sets `ignore_css_margins`. **Always declare `@page { margin: 0 }`** for full-bleed
  designs. [V source reasoning; confirm once in the prototype]
- **Supported page CSS:** `size` (Chrome 15), `page-orientation` (85), named pages via `page:` (85), all 16 margin boxes
  such as `@bottom-right { content: counter(page) " / " counter(pages) }` (**131**). `bleed` and `marks` are **not
  implemented**: absent from MDN BCD and from Blink's `css_properties.json5`. `string-set` and `target-counter()` are
  also absent. [V]
- **Bleed recipe for Chrome:**

```css
/* A4 trim 210×297 mm + 3 mm bleed on every side */
@page { size: 216mm 303mm; margin: 0; }
html, body { margin: 0; }
.sheet { position: relative; width: 216mm; height: 303mm; overflow: hidden; break-after: page; }
.sheet:last-child { break-after: auto; }          /* avoids a trailing blank page [U] */
.trim  { position: absolute; inset: 3mm; }          /* finished size */
.safe  { position: absolute; inset: 8mm; }          /* 3 mm bleed + 5 mm safe margin */
/* backgrounds and photos extend to .sheet edges; text stays inside .safe */
```

```python
# After Chrome: mark trim/bleed boxes so imposition software and preflight know them (pypdf ≥ 3; 6.19 installed)
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
PT = 72 / 25.4; BLEED = 3 * PT                      # 3 mm = 8.504 pt
r, w = PdfReader("flyer.pdf"), PdfWriter()
for p in r.pages:
    mb = p.mediabox
    p.bleedbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
    p.trimbox  = RectangleObject((mb.left + BLEED, mb.bottom + BLEED, mb.right - BLEED, mb.top - BLEED))
    w.add_page(p)
w.add_metadata({"/Title": "Autumn flyer", "/Author": "Client name"})
w.write("flyer.print.pdf")
```

  Crop marks: most online printers want bleed and *no* marks **[U]**. If marks are required, enlarge the page by a
  slug (e.g. +10 mm per side) and draw 0.25 pt hairlines outside the bleed in HTML/SVG. Registration colour does not
  exist in RGB, so use black.
- **What Chrome's PDF contains** (Skia PDF backend; Chrome's `MakePdfDocument`) [V source]:
  - `fRasterDPI = 300`. Anything Skia cannot express in PDF is rasterised at 300 dpi: CSS `filter`, `backdrop-filter`,
    SVG filters such as `feTurbulence` grain, and colour filters ("PDF does not support image filters, so render them on
    CPU" — `SkPDFDevice.cpp`).
  - macOS only, **Chrome ≥ 151**: `fRasterizeAlphaGradientsForPrinting = true`. Gradients with transparency, for example
    a scrim fading to transparent, become 300-dpi images, while opaque gradients stay vector. This works around macOS
    PostScript print failures (commit 2026-06-24).
  - Blend modes (`mix-blend-mode`) map to native PDF `/BM` modes and stay vector. XOR-like modes fall back to normal.
  - **Font embedding (`SkPDFFont::FontType`)**: Skia falls back to Type 3 when the typeface is variable (has variation
    axes), is CFF-flavoured (OTF with `CFF ` outlines), has fsType Restricted (0x0002) or Bitmap-only (0x0200), has a
    mask filter (blurred shadow), or has a modified path (fake bold/italic, stroke). Otherwise it embeds subsetted
    TrueType with ToUnicode. Type 3 text still prints as vectors, but preflight tools flag it, it is larger, and text
    extraction is weaker. `pdffonts` lists Type 3 fonts as "emb yes", so check the **type** column.
  - Tagged PDF is on by default in the CLI. `--generate-pdf-document-outline` builds bookmarks from `h1…h6`.
- **Verify locally** (Homebrew poppler present): `pdfinfo -box out.pdf` (Media/Crop/Bleed/Trim/Art boxes),
  `pdffonts out.pdf` (look for `Type 3`), and `pdftoppm -r 150 -png out.pdf out/preview` for visual diff.

### 1.7 `--dump-dom` as a QA results channel

The DOM is serialized after load plus the budget, so a script that has finished by then can publish results.

```html
<script>
(async () => {
  const box = Object.assign(document.createElement('script'), {type: 'application/json', id: '__qa__'});
  box.textContent = '{"status":"pending"}'; document.head.append(box);
  document.body.offsetHeight;                                   // force style + layout
  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.decode().catch(() => null)));
  const over = [...document.querySelectorAll('[data-qa-box]')]
    .filter(e => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1)
    .map(e => e.dataset.qaBox);
  const r = {status: 'done', overflow: over,
             fonts: [...document.fonts].map(f => [f.family, f.weight, f.style, f.status])};
  box.textContent = JSON.stringify(r).replace(/</g, '\\u003c');  // cannot break out of <script>
})();
</script>
```

```python
import json, re
dom = proc.stdout
m = re.search(r'<script type="application/json" id="__qa__">(.*?)</script>', dom, re.S)
qa = json.loads(m.group(1)) if m else {"status": "missing"}
assert qa["status"] == "done", "raise --virtual-time-budget or switch to the CDP driver"
```

`console.log` output is not a reliable channel from the CLI. Chrome's own stderr noise varies by version, so parse
only the markers you control.

### 1.8 `--user-data-dir` isolation

- Use one throwaway directory per Chrome process, from `mktemp -d`. Two processes can never share one: the second
  would hit the profile lock and exit or attach. Never point at `~/Library/Application Support/Google/Chrome`. Chrome
  136+ refuses remote debugging on the default profile anyway. [D]
- If you omit the flag, headless creates and cleans up its own unique temp profile. It is killed only on crash or
  timeout, so sweep stale dirs under `~/Library/Application Support/Google/Chrome-headless/` only after listing them. [V]
- A fresh profile has **no components**: hyphenation dictionaries (not used on macOS, §3.8), Widevine and the like.
  None of these matter here. [V]

### 1.9 Size limits

- The only hard guard in CDP is the full-page screenshot limit of **131,072 CSS px** per side ("Page is too large").
  Its code comment refers to a 16K headless limit (`page_handler.cc`). [V] Playwright's test suite takes a 16,384-CSS-px-tall
  full-page shot at DSF 2 in Chromium without error. [V `tests/library/screenshot.spec.ts`] GPU texture limits
  (typically 16,384 px) can still cause blank or tiled regions on very large captures **[U]**. Keep each side ≤ 16,384
  **device** px, and tile with `clip` and stitch in Pillow beyond that. A0 at 300 ppi is 9,933 × 14,043, which fits.
- The CLI returns image data as a base64 string through JS. V8 caps strings at about 2^29 characters, so outputs of
  several hundred MB would fail **[U]**. The CDP path can stream PDFs (`transferMode: "ReturnAsStream"` + `IO.read`). [V protocol]
- PDF 1.x page-size implementation limit: 14,400 units, i.e. 200 in. Larger needs `UserUnit` (PDF ≥ 1.6).
  **[U]** (PDF 1.7 Annex C, not re-read today)
- Pillow's decompression-bomb guard (`Image.MAX_IMAGE_PIXELS`, about 89 MP warning / 179 MP error) must be raised for
  stitched posters. [D]

### 1.10 Pitfalls checklist

1. The exit code is always "success" → validate outputs (§1.2). [V]
2. Chrome 153 can hang on navigation errors → subprocess timeout plus `--timeout`. [V]
3. Default PDF header/footer → `--no-pdf-header-footer`. [V]
4. JPEG/WebP quality is fixed at 80 → capture PNG, encode yourself. [V]
5. Colour: missing `--force-color-profile=srgb` risks display-profile conversion **[U]** (both automation libraries force it). [V]
6. Scale: pass the DSF explicitly. Chrome's own tests do, and the default depends on the virtual/physical screen **[U]**.
7. Fonts via `file://` need `--allow-file-access-from-files` (security: only render trusted HTML), `data:` URIs or localhost. [V]
8. `document.fonts.ready` can resolve before faces are requested → `document.fonts.load()` each face. [D]
9. Variable, CFF or restricted fonts, blurred text-shadows and fake bold → Type 3 in PDF. [V]
10. Filters, backdrop-filter, SVG filters and (macOS ≥ 151) alpha gradients → 300-dpi raster islands in PDF. [V]
11. `hyphens:auto` does nothing for Bengali, Hindi or Arabic on Mac (§3.8). [V]
12. `--font-render-hinting` does nothing in Google Chrome. [V]
13. Keychain prompts → `--use-mock-keychain --password-store=basic`. [D]
14. Chrome auto-updates. Stable moved 153→154 on 2026-09-22, and branch points in 2026 are 2 weeks apart
    (chromiumdash). Record `Browser.getVersion` in every render's metadata. For bit-reproducibility, pin Chrome for
    Testing (152 is already cached). [V]
15. `--screenshot` without `--window-size` captures the default window. `--window-size` has no effect on PDF layout,
    which uses `@page`. [V]

---

## 2. Alternatives to the bare CLI

### 2.1 Comparison

| Option | Size / deps | Licence | Python 3.9? | Notes |
|---|---|---|---|---|
| **Raw CDP, Python stdlib, `--remote-debugging-pipe`** | 0 | — | yes | NUL-framed JSON on fds 3/4. Recipe: `os.pipe()` ×2, dup the child ends to ≥10 with `F_DUPFD_CLOEXEC`, then `os.dup2(r,3); os.dup2(w,4)` in `preexec_fn` with `close_fds=False`. **codex-design `scripts/design.py` already implements this.** [V file read] |
| Raw CDP, Node 26 | 0 | — | n/a | `child_process.spawn(chrome, args, {stdio:['ignore','pipe','pipe','pipe','pipe']})`: stdio[3] is Chrome's input, stdio[4] its output (same as Puppeteer). Global `WebSocket` also exists for `--remote-debugging-port=0`. [V] |
| Raw CDP, Deno 2.9 | 0 | — | n/a | `Deno.Command` has no extra fds → use `--remote-debugging-port=0`, read `DevToolsActivePort` in the profile dir, then connect with the built-in `WebSocket` **[U]** |
| **puppeteer-core 25.12.0** (2026-09-23) | 6.0 MB unpacked; ~23 packages / ~24 MB with deps (chromium-bidi 9.5 MB, devtools-protocol 3.7 MB, zod …) [V registry walk] | Apache-2.0 | n/a (Node) | `puppeteer.launch({channel:'chrome'})` or `executablePath` is required for -core. `page.pdf()` defaults: `preferCSSPageSize: false` (set true!), `waitForFonts: true`, `tagged: true`, `outline: false`, `omitBackground: false`. Default args include `--force-color-profile=srgb`, `--export-tagged-pdf`, `--generate-pdf-document-outline`, `--hide-scrollbars`, `--use-mock-keychain`. [V source] |
| **playwright-core 1.63.0** (2026-09-04) | 13.5 MB, **0 deps** | Apache-2.0 | n/a | `chromium.launch({channel:'chrome'})` uses the installed Chrome. `page.pdf({preferCSSPageSize, printBackground, tagged (default false), outline})`. `screenshot({omitBackground, scale:'css'|'device', animations:'disabled', caret:'hide'})`. Defaults include `--force-color-profile=srgb`, `--disable-component-update`, `--export-tagged-pdf`, `--enable-features=CDPScreenshotNewSurface`. [V docs/source] |
| Playwright for Python | wheel 42.9 MB (bundles a Node driver) | Apache-2.0 | **≤ 1.60.0** (1.61+ need ≥ 3.10) [V PyPI] | `p.chromium.launch(channel="chrome")`; no browser download needed |
| chrome-remote-interface 0.34.0 | ~2.2 MB (ws, commander) | MIT | n/a | Thin CDP client |

**CDP features gained over the CLI:** a JS ready gate (evaluate `await settle()` and then capture), several captures
per page load (full, background-only plate for contrast, element/clip shots, colour-blind simulations via
`Emulation.setEmulatedVisionDeficiency`), per-page DSF via `Emulation.setDeviceMetricsOverride`, one warm browser
for many jobs (saves a ~1 s cold start per render **[U]**), `CSS.getPlatformFontsForNode` for fallback detection,
`Fetch.enable` to block or serve requests offline, streamed PDFs, and console/exception capture. [V protocol JSON]

### 2.2 WeasyPrint (HTML/CSS → PDF, no JavaScript)

- **70.0**, released 2026-09-08 as a security release (CVE-2026-55073); BSD-3-Clause. **Requires Python ≥ 3.10 since 67.0.**
  66.0 (2025-07-24) is the last for 3.9 and has **no CMYK/PDF-X**. It needs Pango ≥ 1.44; Homebrew has 1.57.1 here.
  The docs recommend `brew install weasyprint` on macOS. [V changelog, PyPI, docs]
- **Print features:** `@page` size, **`bleed`, `marks: crop cross`**, the 16 margin boxes, named pages, page counters
  (with known limitations) [V docs]. **CMYK:** `device-cmyk()` colours plus `@color-profile device-cmyk { src: url(profile.icc) }`
  (since 67.0). **PDF variants:** `pdf/x-1a`, `pdf/x-3`, `pdf/x-4`, `pdf/x-5g` (from `weasyprint/pdf/pdfx.py`), plus PDF/A
  and PDF/UA; `--output-intent=srgb|device-cmyk|<profile>` since 69.0. The docs recommend PDF/X-4 when you need
  transparency. [V]
- **Limits:** no JS (charts must be pre-rendered SVG; no in-page QA); no `color-mix()` or `contrast-color()` [V docs]. The
  layout engine differs from Chrome, so designs are not portable 1:1 **[U]**. It does not convert RGB images to CMYK:
  you supply CMYK assets. Text shaping goes through Pango + HarfBuzz, so Bengali should shape **[U]** (not tested here).

### 2.3 Paged.js

- npm `pagedjs` **0.4.3 (2023-07-06)**, MIT. The repo still gets commits in 2026 (latest 2026-03-20), but there has been no
  release since 2023. `pagedjs-cli` 0.4.3 bundles an old Puppeteer. [V registry/GitHub]
- It is a polyfill that runs *inside Chrome*. It implements `bleed` and `marks` itself
  (`src/modules/paged-media/atpage.js`: 1–4 value bleed; marks with no bleed default to 6 mm) and draws the marks as DOM.
  Configure with `window.PagedConfig = {auto: true, after: () => …}`, then print with `preferCSSPageSize: true`. [V source]
- Since Chrome 131 ships margin boxes natively, Paged.js is only worth it for bleed/marks, `string-set`, running elements,
  `target-counter` cross-references, and footnotes. It is a heavy, slow-moving dependency.
- Similar engine: **Vivliostyle** (`@vivliostyle/cli` 11.3.3), which is **AGPL-3.0**, a licence caveat for tooling you distribute. [V npm]

### 2.4 Satori + resvg

- **Satori 0.33.5** (2026-09-22, MPL-2.0) added **HarfBuzz text shaping** in v0.33.0 on **2026-08-20** (`harfbuzzjs` dependency).
  Its README says complex scripts such as Arabic now shape better, but there is **no bidi**. [V README, npm]
- Layout: `display` flex/block/contents/none only (Yoga, **no grid**), no `calc`, no `z-index`, no `<style>` tags or external
  CSS, fonts must be TTF/OTF/WOFF (**no WOFF2**), no 3D transforms. [V README]
- **Bengali: untested.** HarfBuzz should form conjuncts, but line breaking and cluster handling are unproven, and the
  feature is 5 weeks old **[U]**. Not recommended as our renderer. It could serve a future server-side OG-image
  path for Latin text.
- **resvg** v0.48.1 (2026-08-02; Apache-2.0 OR MIT) shapes SVG `<text>` with rustybuzz. The npm `@resvg/resvg-js` 2.6.2 is
  from 2024-03 and MPL-2.0. Satori emits glyph paths, so resvg's shaping is not what shapes Satori's text. [V]

### 2.5 Pillow text

- Without raqm, Pillow uses its BASIC layout: code point → glyph via `cmap`, no GSUB reordering or conjuncts. Bengali,
  Devanagari and Arabic come out broken. Pillow docs: setting direction or font features is unsupported without libraqm. [V docs]
- Pillow wheels since 8.2 bundle a modified libraqm that **loads FriBiDi at runtime**. The shim tries `libfribidi.dylib`
  on the default search path, then `/usr/local/lib/…` (Intel Homebrew). Apple-Silicon Homebrew lives in `/opt/homebrew/lib`,
  hence raqm=False by default. [V source `src/thirdparty/fribidi-shim/fribidi.c`]
- **No-install enablement (verified):** `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib <venv>/bin/python …` →
  `features.check('raqm') == True`. Use `ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)`. The venv
  Python comes from `/Library/Developer/CommandLineTools`, so SIP does not strip `DYLD_*` (it would for `/usr/bin/python3`).
  Actual Bengali output was not rendered here **[U]**.
- Use Pillow text only for simple overlays (watermarks, contact-sheet labels). Chrome remains the typesetter. `uharfbuzz`
  (in the codex-design venv) can shape for measurement in Python.

---

## 3. Fonts

### 3.1 Programmatic sourcing

| Source | Pattern (verified 2026-09-23) | Key? | Notes |
|---|---|---|---|
| **Fontsource API** | `https://api.fontsource.org/v1/fonts?subsets=bengali` (list) · `https://api.fontsource.org/v1/fonts/{id}` (metadata incl. `variants[w][style][subset].url.{woff2,woff,ttf}`, `unicodeRange`, `license`, `npmVersion`) · `https://api.fontsource.org/v1/variable/{id}` (axes) | no | Documented and read-only, with a hard ceiling of about 2,500 requests per 10 s [D] |
| **Fontsource CDN (static)** | `https://cdn.jsdelivr.net/fontsource/fonts/{id}@{ver\|latest}/{subset}-{weight}-{style}.{woff2\|woff\|ttf}` e.g. `…/noto-sans-bengali@5.3.0/bengali-400-normal.ttf` (111 KB) | no | Version pin works (`@5.3.0`, `@5`). Static **TTF files are non-variable TrueType (glyf) with GSUB**, ideal for print PDFs [V] |
| **Fontsource CDN (variable)** | `https://cdn.jsdelivr.net/fontsource/fonts/{id}:vf@{ver}/{subset}-{wght\|wdth\|standard}-normal.woff2` (`standard` = all standard axes) | no | Screen only (Type 3 in PDF) [V] |
| Fontsource npm via jsDelivr | `https://cdn.jsdelivr.net/npm/@fontsource/{id}@5.3.0/files/{id}-{subset}-{w}-{style}.woff2` · variable: `@fontsource-variable/{id}` → `files/{id}-{subset}-wght-normal.woff2` | no | woff/woff2 only (no ttf in npm) [V] |
| **Google Fonts css2** | `https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;700&display=swap` (axes alphabetical `ital,wght@0,400;1,700`; ranges `wght@100..900`; `text=` subsetting) | no | UA-dependent (below). The UA behaviour is **undocumented** [D css2 docs 2024-07-23; V behaviour] |
| gstatic files | Taken from the CSS `src: url(https://fonts.gstatic.com/s/<family>/v<N>/<hash>.{ttf,woff2})` | no | Hash URLs change with font versions: cache them, don't hard-code |
| **google/fonts GitHub** | `https://raw.githubusercontent.com/google/fonts/main/ofl/notosansbengali/NotoSansBengali%5Bwdth,wght%5D.ttf` · licence `…/OFL.txt` · `…/METADATA.pb` | no | Upstream variable TTFs. The folder name gives the licence (`ofl/`, `apache/`, `ufl/`). Pin a commit SHA instead of `main` for reproducibility [V] |
| Google Fonts Developer API | `https://www.googleapis.com/webfonts/v1/webfonts?key=KEY[&family=][&subset=][&capability=VF\|WOFF2][&sort=]` | **yes** | Without a key → HTTP 403 "unregistered callers" [V]. Docs updated 2025-09-11 [D] |
| (unofficial) | `https://fonts.google.com/metadata/fonts` (2.7 MB JSON) | no | Undocumented, may change. Don't depend on it [V exists] |

**Google Fonts css2 by user agent (observed today):**
- **Non-browser UA** (curl, Python urllib): one `@font-face` per weight with `src: url(…ttf) format('truetype')`. The file is a
  full-coverage, **static-instance TTF** with no `unicode-range`. Even a range request `wght@100..900` returns nine static
  TTFs (100…900). Noto Sans Bengali 400 = 0.14 MB; Noto Sans JP 400 = 5.32 MB; Noto Color Emoji = 25.3 MB (COLR/CPAL +
  SVG tables). [V]
- **Chrome UA:** WOFF2, one `@font-face` per unicode-range subset (Bengali: 3 blocks — bengali, latin-ext, latin; Naskh
  Arabic 5; Noto Sans JP **124** slices; SC **101**). A range request returns a **variable** WOFF2 with
  `font-weight: 100 900`. [V]
- `text=` returns a tiny subset TTF that keeps GDEF/GPOS/GSUB. It was 3.7 KB for a 17-character Bengali string. Good for
  headline-only faces. Full conjunct closure is **[U]**.

### 3.2 Licensing (commercial and print)

- **OFL 1.1** (almost all Google Fonts / Fontsource families): commercial use, print, logos, and embedding in PDFs/apps
  are allowed, and the document does not become OFL. You may not sell the font by itself. Subsetting counts as
  modification, so Reserved Font Name rules can apply to *redistributed* subset font files (not to rendered
  artwork). [D: OFL-FAQ 1.1-update7, Nov 2023, openfontlicense.org]
- **Apache-2.0** (some Google families, Material Symbols): permissive; keep the NOTICE/licence with redistributed files. **UFL**
  (Ubuntu family): permissive with renaming rules for modified fonts. [D]
- Automate it: accept only `license ∈ {OFL-1.1, Apache-2.0, UFL}` from the Fontsource metadata, and copy `OFL.txt`/LICENSE
  next to cached files. Client fonts come only from the client, and are never cached into shared folders.

### 3.3 Non-Latin families and sizes

**Bengali** (Fontsource `subsets=bengali`, 11 families, all OFL) [V]:

| Family | Weights | Variable | google/fonts file (size) |
|---|---|---|---|
| Noto Sans Bengali | 100–900 | yes (wdth, wght) | `NotoSansBengali[wdth,wght].ttf` 0.46 MB |
| Noto Serif Bengali | 100–900 | yes (wdth, wght) | `NotoSerifBengali[wdth,wght].ttf` 0.98 MB |
| Hind Siliguri | 300–700 | no | 5 static TTFs ≈ 0.25–0.28 MB each |
| Anek Bangla | 100–800 | yes | `AnekBangla[wdth,wght].ttf` 1.34 MB |
| Baloo Da 2 | 400–800 | yes | `BalooDa2[wght].ttf` 0.45 MB |
| Tiro Bangla | 400 (+ italic) | no | 0.32 MB each |
| Galada | 400 | no | 0.18 MB |
| Atma | 300–700 | no | ≈ 0.21–0.22 MB each |
| Mina | 400, 700 | no | 0.15 MB each |
| Alkatra | 400–700 | yes | (display) |
| Google Sans | 400–700 | yes (GRAD, opsz, wght) | ≈ 5 MB. OFL, with a `TRADEMARKS.md` in the folder; reads as Google's brand |

**Arabic:** Noto Naskh Arabic `[wght]` 0.30 MB, Noto Sans Arabic `[wdth,wght]` 0.84 MB, Noto Kufi Arabic `[wght]` 0.43 MB,
Amiri (4 statics ≈ 0.4 MB). **Devanagari:** Noto Sans Devanagari `[wdth,wght]` 0.64 MB (plus Hind, Mukta, Tiro Devanagari
Hindi, Anek Devanagari, Alkatra). **CJK** (google/fonts variable TTF): Noto Sans JP 9.58 MB, SC 17.77 MB, TC 11.94 MB, KR 10.41 MB.
For screen, Chrome fetches only the needed unicode-range slices. For print, use the static TTF per weight via css2
(non-browser UA), e.g. JP 400 = 5.3 MB, which Chrome subsets on embed. [V]

### 3.4 macOS system fonts Chrome can reach, and their caveats

Read from the files on this Mac (name table + OS/2 fsType) [V]:

| Font (path) | Outlines | fsType | Licence signal | Chrome-PDF consequence |
|---|---|---|---|---|
| Kohinoor Bangla (`/System/Library/Fonts/KohinoorBangla.ttc`, 5 faces; Indian Type Foundry design) | **CFF** | 0x0000 (installable) | none in the file → macOS SLA | **Type 3** (CFF) |
| Bangla Sangam MN (`…/Supplemental/Bangla Sangam MN.ttc`) | glyf + GSUB/morx | 0x0000 | macOS SLA | TrueType OK |
| Bangla MN (`…/Supplemental/Bangla MN.ttc`) | glyf | 0x0004 (preview & print) | macOS SLA | TrueType OK |
| Kalpurush (`/Library/Fonts/kalpurush.ttf`, user-installed) | glyf | 0x0000 | name table says **SIL OFL** | OK |
| Siyam Rupali (`/Library/Fonts/Siyamrupali.ttf`, user-installed) | glyf | **0x0002 (restricted)** | name table says **GNU GPL** | **Type 3**, plus a GPL font-exception ambiguity → avoid |
| Kohinoor Devanagari, ITF Devanagari | CFF | 0x0000 | macOS SLA | Type 3 |
| Geeza Pro (`GeezaPro.ttc`) | glyf + AAT `morx` only (no GSUB) | 0x0000 | macOS SLA | TrueType; Arabic shaping via AAT **[U]** |
| SF Arabic (`SFArabic.ttf`) | glyf, **variable** (`fvar`) | 0x0004 | macOS SLA; Apple's SF licence restricts use | **Type 3** (variable) |
| Apple Color Emoji (192 MB, **sbix** bitmaps) | — | 0x0004 | macOS SLA; Apple artwork | Images in PDF |
| Hiragino Sans GB | CFF | 0x0008 | macOS SLA | Type 3 |

**macOS Tahoe 26 SLA §2.E (paraphrased):** the bundled fonts may be used to display and print content *while running the
Apple software*. They may be embedded in content only where the font's own embedding restrictions allow. [V: text of
`https://www.apple.com/legal/sla/docs/macOSTahoe.pdf`] Using system fonts in client deliverables is therefore a grey area.
The files also drift with OS updates (reproducibility), and other machines lack them. Kohinoor Bangla is sold
commercially by ITF **[U]**. **Rule for the skill:** client work uses OFL fonts cached in the job. System fonts must never
be reached through fallback, so treat any `isCustomFont:false` glyphs as an error.

### 3.5 Colour emoji

| Option | Licence | Fetch pattern (verified) | Notes |
|---|---|---|---|
| Noto Color Emoji (font) | OFL-1.1 (fonts); Apache-2.0 (tools and most images) | COLRv1: `https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji@v2.051/fonts/Noto-COLRv1.ttf` (5.0 MB); `main` layout moved to `2D/fonts/…`. css2 (non-browser UA) gives a 25 MB COLR+SVG TTF | Chrome renders COLRv1 since **98** (blog 2022-01-06). Order the stack as `font-family: "Noto Sans Bengali", "Noto Color Emoji"` |
| Noto emoji SVGs | Apache-2.0 | `https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji@v2.051/svg/emoji_u1f600.svg` (codepoints joined by `_`) | Vector in PDF |
| Twemoji (jdecked fork, v17.0.3, 2026-06-01) | graphics **CC-BY 4.0** (attribution), code MIT | `https://cdn.jsdelivr.net/gh/jdecked/twemoji@v17.0.3/assets/svg/1f600.svg` | Attribution in a credits file |
| OpenMoji 17.0.0 | **CC BY-SA 4.0** | `https://cdn.jsdelivr.net/npm/openmoji@17.0.0/color/svg/1F600.svg` | Share-alike can reach the adapted artwork → avoid for client work |
| Fluent Emoji (Microsoft) | MIT | `https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grinning%20face/Flat/grinning_face_flat.svg` | Name-based paths |
| Apple Color Emoji | Apple (SLA) | system | Don't ship it in client work |

How COLRv1 glyphs come out in Chrome PDFs is **[U]**. For print, insert emoji as SVG `<img>` elements, which are
deterministic vectors.

### 3.6 Variable fonts and `font-variation-settings`

- On screen, prefer the high-level properties: `font-weight: 650`, `font-stretch: 87.5%` (wdth),
  `font-optical-sizing: auto` (opsz, Chrome 79). Use `font-variation-settings: "GRAD" 50` only for custom axes: it
  overrides the high-level values and does not cascade per axis. `@font-face { font-weight: 100 900; font-stretch: 62.5% 100%; }`
  declares the ranges. [D MDN; BCD versions §4]
- **For print PDFs, use static instances.** Variable faces become Type 3 (§1.6). Sources: Fontsource static files, css2 static TTF,
  or `fontTools.varLib.instancer` (fontTools 4.60.2 is already in the codex-design venv):
  `fonttools varLib.instancer NotoSansBengali[wdth,wght].ttf wght=700 wdth=100 -o NotoSansBengali-Bold.ttf`. [D fontTools CLI; **[U]** not run]
- Set `font-synthesis: none` (Chrome 97). A missing bold then shows as a visible QA failure instead of silently
  fake-bolded Type 3 text. [V BCD]

### 3.7 Bengali-specific typesetting notes

- Chrome shapes all scripts with HarfBuzz (`third_party/blink/renderer/platform/fonts/shaping/harfbuzz_shaper.cc`), so
  conjuncts, reph, and pre-base vowel reordering are correct *if the font has the GSUB features*. [V README]
- Always set `lang="bn"` (hyphenation, locale-specific glyphs, and QA script detection).
- `text-box: trim-both cap alphabetic` (Chrome 133) trims to the Latin cap height and alphabetic baseline. Bengali's matra
  (headline) and lower vowel signs don't match those metrics, so check trimmed Bengali visually or only trim Latin
  lines. `text-box-edge` has no hanging-baseline keyword. **[U]**
- Keep `letter-spacing: 0` on Bengali/Arabic runs, because tracking disrupts joined forms **[U]** (codex-design's kit already zeroes it).
- Copy/paste from PDFs of complex scripts often yields wrong character order (a ToUnicode limitation). This is not visual,
  but tell clients who need searchable PDFs **[U]**.

### 3.8 Hyphenation on macOS Chrome

- The Blink build flag `use_minikin_hyphenation = !is_apple` [V `third_party/blink/public/public_features.gni`]. On Mac, Chrome uses
  `text/apple/hyphenation_apple.cc`, which calls `CFStringIsHyphenationAvailableForLocale` and
  `CFStringGetHyphenationLocationBeforeIndex`. No dictionary download is needed, so it works in fresh headless profiles. [V]
- Locales available on this Mac (queried through CoreFoundation today): **en, en_GB, de, fr, es, it, pt, nl, sv, da, nb, fi, ru, pl,
  cs, hu, uk, el, ca, hr, sk, ro**. **Not available: tr, id, ms, vi, bn, bn_BD, bn_IN, hi, mr, ta, te, gu, pa, ar, fa, ur, he, th,
  ja, zh, ko.** [V] On Linux/Windows Chrome, the Minikin dictionaries do include `und-Beng → bn` [V source]. That does not help on Mac.
- For Bengali, rely on `text-wrap: pretty/balance`, manual `&shy;`/`<wbr>` in long compounds, and copy edits.

---

## 4. Chrome typography and graphics CSS support

Chrome version where support began, from MDN browser-compat-data (main, fetched 2026-09-23). The installed
Chrome is 153, so everything listed with a version is available. [V]

| Feature | Chrome | Notes |
|---|---|---|
| `text-wrap: balance` / `pretty` | 114 / 117 | `text-wrap-style` longhand 130. Safari has `pretty` in 26; Firefox has no `pretty` |
| `text-box`, `text-box-trim`, `text-box-edge` | 133 | Latin-metric based (see §3.7) |
| `font-feature-settings` | 48 | Stylistic sets and `tnum`; don't disable script shaping features |
| `font-variant-alternates` | 111 | — |
| `font-variation-settings` / `font-optical-sizing` | 62 / 79 | — |
| `font-palette`, `@font-palette-values` | 101 | Recolour COLR fonts |
| `font-size-adjust` | 127 | Useful for mixed-script fallback |
| `font-synthesis` | 97 | Set it to `none` (§3.6) |
| `initial-letter` | 110 | Unprefixed in Chrome; Safari needs `-webkit-` |
| `hyphens` / `hyphens: auto` | 55 / 88 | On Mac, CoreFoundation locales only (§3.8). `hyphenate-limit-chars` 109 |
| `hanging-punctuation` | **not shipped** | Blink property exists behind runtime flag `CSSHangingPunctuation`, status "test" [V `runtime_enabled_features.json5`]. Safari only |
| `text-autospace` / `text-spacing-trim` | 140 / 123 | CJK spacing |
| `line-clamp` | only `-webkit-line-clamp` | — |
| `text-decoration-skip-ink: all` | 148 | — |
| `mix-blend-mode` | 41 | PDF: native `/BM` modes, vector |
| `mask` (unprefixed) / `clip-path` / `path()` / `shape()` | 120 / 55 / 88 / **135** | — |
| `backdrop-filter` | 76 | Rasterised in PDFs |
| `color-mix()` / `oklch()` | 111 / 111 | Relative colour syntax: 119 (lab/lch/color), 122 (oklch/oklab/rgb), 125 (hsl/hwb) |
| `light-dark()` / `contrast-color()` | 123 / **147** | — |
| `corner-shape` | 139 | Marked experimental in BCD |
| `object-view-box` | 104 | Crop an `<img>` to a Vision-computed box without re-encoding (Chrome-only) |
| `print-color-adjust` (unprefixed) | 136 | Irrelevant with `printBackground: true` |
| `@page` `size` / `page-orientation` / named pages (`page:`) | 15 / 85 / 85 | — |
| `@page` margin boxes (16 of them) | **131** | Page counters in running footers |
| `@page` `bleed`, `marks`; `string-set`; `target-counter()` | **none** | Only WeasyPrint and Paged.js implement bleed and marks |
| SVG filters (`feTurbulence`, `feColorMatrix` …) | long supported | Rasterised at 300 dpi in PDFs |

**Grain / noise (SVG `feTurbulence`)**, deterministic through a fixed `seed`:

```html
<svg class="grain" viewBox="0 0 1080 1350" preserveAspectRatio="none" aria-hidden="true">
  <filter id="g" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="7" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#g)"/>
</svg>
<style>.grain{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:soft-light;opacity:.22;pointer-events:none}</style>
```

`baseFrequency` is in user units, so the grain scales with the artwork, and 1× and 2× renders look alike. In PDFs the
filter becomes a 300-dpi image [V Skia]. For huge posters, a pre-rendered noise PNG tile (`background-repeat`) is lighter **[U]**.

---

## 5. Assets

### 5.1 Icon sets: licence and one-SVG-by-name URLs (all returned HTTP 200 today)

| Set (latest) | Licence | URL pattern |
|---|---|---|
| **Lucide** `lucide-static@1.47.0` (2026-09-17) | ISC; icons derived from Feather are MIT (listed in LICENSE) | `https://cdn.jsdelivr.net/npm/lucide-static@1.47.0/icons/{name}.svg` · `https://unpkg.com/lucide-static@1.47.0/icons/{name}.svg` |
| **Tabler** `@tabler/icons@3.48.0` (2026-09-22) | MIT | `https://cdn.jsdelivr.net/npm/@tabler/icons@3.48.0/icons/outline/{name}.svg` · `…/icons/filled/{name}.svg` |
| **Phosphor** `@phosphor-icons/core@2.1.1` (2024-03) | MIT | `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/regular/{name}.svg` · other weights `assets/{thin\|light\|bold\|fill\|duotone}/{name}-{weight}.svg` |
| **Iconoir** `iconoir@7.12.1` (2026-08-12) | MIT | `https://cdn.jsdelivr.net/npm/iconoir@7.12.1/icons/regular/{name}.svg` · `…/icons/solid/{name}.svg` |
| **Material Symbols** `@material-symbols/svg-400@0.47.5` (2026-09-22; community repackage by marella/material-symbols of Google's set) | Apache-2.0 (Google repo and the repackage) | `https://cdn.jsdelivr.net/npm/@material-symbols/svg-400@0.47.5/{outlined\|rounded\|sharp}/{name}.svg` (filled: `{name}-fill.svg`) · Google static (undocumented): `https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{name}/default/24px.svg` |
| Simple Icons `simple-icons@16.32.0` | CC0 (brand marks remain trademarks) | `https://cdn.jsdelivr.net/npm/simple-icons@16.32.0/icons/{slug}.svg` |
| Iconify API (third-party service) | per set | `https://api.iconify.design/{prefix}/{name}.svg`. Convenient, but a runtime dependency on a third party |

Practice: pin versions, cache SVGs locally with a `LICENSES.md` line per set, and inline SVGs into the HTML with
`stroke="currentColor"` (Lucide/Tabler/Iconoir are stroke icons; normalise `stroke-width` per design). ISC/MIT ask to keep
the notice with copies of the software. Rendered artwork is normally fine, but keep the notice in project files
(interpretation, not legal advice).

### 5.2 QR codes

| | **segno 1.6.6** (2025-03-12) | qrcode (python-qrcode) 8.2 (2025-05-01) |
|---|---|---|
| Licence | BSD-3-Clause | BSD |
| Python | ≥ 3.5 (**installed** in the codex-design venv) | ≥ 3.9 |
| Deps | none (PNG without Pillow) | pypng; Pillow for `[pil]` |
| SVG | `qr.save('q.svg', scale=10, border=4, dark='#111', light=None, unit='mm', xmldecl=False, svgclass=…, title=…)`, `qr.svg_inline(scale=…)`, `qr.svg_data_uri()`; also `png_data_uri()`, `symbol_size(scale, border)` [V source] | `qrcode.image.svg.SvgPathImage` (path), `SvgImage` (rects), `SvgFragmentImage`; CLI `qr --factory=svg-path "text" > q.svg` [V README] |
| Error correction | `error='L'|'M'|'Q'|'H'` (7/15/25/30 %); `boost_error=True` by default raises the level when it fits in the same version [D] | `ERROR_CORRECT_L/M/Q/H` (M default) |
| Extras | Micro QR, structured append, `segno.helpers` (WiFi, vCard, geo) | — |

**Sizing rules:**
- The quiet zone is **4 modules** on every side (DENSO WAVE).
- Use at least **4 printer dots per module**. DENSO's examples: 0.17 mm at 600 dpi laser, 0.33 mm at 300 dpi, 0.5 mm at 200 dpi. [D qrcode.com]
- Computed with segno today [V]:
  - 21-character URL: version 2 at EC M, which is 25 modules + quiet zone = 33 → **16.5 mm at 0.5 mm/module**.
  - 75-character UTM URL: version 5 at M = 37 (+8) → 22.5 mm; at EC H, version 8 → 28.5 mm.
- Practical defaults **[U]**:
  - Keep URLs short (use a redirect).
  - Use EC **M**; use **Q/H** only if a logo covers the centre.
  - Module ≥ 0.4–0.5 mm for offset/digital print.
  - Make the symbol ≥ distance ÷ 10 for posters.
  - Dark on light, and no inverted codes unless test-scanned.
- For raster (social) outputs, use an integer number of device pixels per module and `shape-rendering="crispEdges"`.
- Verify the final render: Vision `VNDetectBarcodesRequest` (macOS 10.13) decodes QR from the exported PNG/PDF raster. Assert that the payload equals the intended URL. [V availability]

### 5.3 Charts for infographics

- **Hand-written SVG** (Claude writes the paths): exact typography, no dependencies, right for ≤ 20 data points (bars, donuts,
  simple lines). Put shared tick/label text in HTML so it uses the job's web fonts.
- **Vega-Lite inside the same Chrome page** (recommended for data-driven charts). Cache the UMD builds locally:
  `https://cdn.jsdelivr.net/npm/vega@6.4.0/build/vega.min.js` (521 KB),
  `https://cdn.jsdelivr.net/npm/vega-lite@6.4.3/build/vega-lite.min.js` (251 KB),
  `https://cdn.jsdelivr.net/npm/vega-embed@7.2.0/build/vega-embed.min.js` (60 KB). All BSD-3. [V]
  `vegaEmbed('#c', spec, {renderer:'svg', actions:false})`. Text is measured with Chrome's canvas using the real web fonts,
  including Bengali labels.
- **CLI `vl2svg`** (bins in `vega-lite`: `vl2vg`, `vl2svg`, `vl2png`, `vl2pdf`; in `vega-cli`: `vg2svg`…). Example:
  `npx -p vega@6.4.0 -p vega-lite@6.4.3 vl2svg spec.vl.json chart.svg`, which downloads into the npm cache and so needs approval.
  **Caveat:** without `node-canvas`, Vega *estimates* text width as `0.8 × text.length × fontSize`
  (`vega-scenegraph/src/util/text.js`) [V]. Layout of legends and labels then drifts, badly so for Bengali, where UTF-16
  length ≠ visual width. `vega-cli` hard-depends on `canvas@^3.2.3` (N-API prebuilds via `prebuild-install -r napi`), which
  works on Node 26 **[U]**.
- Also viable in-page: Observable Plot 0.6.17 (ISC, `…/@observablehq/plot@0.6.17/dist/plot.umd.min.js`) and d3 7.9.0 (ISC).
- Deno can import `npm:vega-lite@6.4.3` directly (cached in Deno's store; network on first run) **[U]**. There is no advantage
  over the in-page approach.

---

## 6. Image operations on macOS

### 6.1 Apple Vision via Swift (no Xcode project)

- The toolchain is present: `swift` and `swiftc` 6.3.3 from the CLT, and SDK 26.5 contains `Vision.framework` with Swift
  interfaces. `import Vision` auto-links. [V]
- Run as a script with `swift vision.swift analyze photo.jpg`. This recompiles on every run (seconds) **[U]**.
- Better to compile once and cache: `swiftc -O vision.swift -o ~/.cache/cd/cd-vision`, rebuilding when the source hash
  changes (codex-design already does this). If Swift 6 strict-concurrency complains about top-level async code, add
  `-swift-version 5` **[U]**.

| Capability | Legacy VN API (macOS) | New Swift API (macOS 15+) |
|---|---|---|
| Face rectangles | `VNDetectFaceRectanglesRequest` **10.13** | `DetectFaceRectanglesRequest` → `[FaceObservation]` (`boundingBox`, roll/yaw/pitch, `captureQuality`) |
| Attention saliency (heat map + `salientObjects`) | `VNGenerateAttentionBasedSaliencyImageRequest` **10.15** | `GenerateAttentionBasedSaliencyImageRequest` → `SaliencyImageObservation` |
| Objectness saliency | `VNGenerateObjectnessBasedSaliencyImageRequest` **10.15** | `GenerateObjectnessBasedSaliencyImageRequest` |
| Subject lift / background removal | `VNGenerateForegroundInstanceMaskRequest` **14.0**; `VNInstanceMaskObservation.generateMaskedImage(ofInstances:from:croppedToInstancesExtent:)` **14.0** | `GenerateForegroundInstanceMaskRequest` → `InstanceMaskObservation` (`allInstances`, `generateMask(for:)`, `generateMaskedImage(for:imageFrom:croppedToInstancesExtent:)`, `generateScaledMask`, `instanceAtPoint`) |
| People matte | `VNGeneratePersonSegmentationRequest` **12.0** | `GeneratePersonInstanceMaskRequest` |
| Photo quality ranking | — | `CalculateImageAestheticsScoresRequest` **15.0** (`overallScore`, `isUtility`) |
| QR/barcode verify | `VNDetectBarcodesRequest` **10.13** | `DetectBarcodesRequest` 15.0 |
| OCR (spot-check text inside AI images) | `VNRecognizeTextRequest` **10.15** | `RecognizeTextRequest` (Bengali in `supportedRecognitionLanguages` **[U]**) |
| Horizon (auto-straighten) | `VNDetectHorizonRequest` **10.13** | `DetectHorizonRequest` |

Availability comes from the Apple docs JSON (`developer.apple.com/tutorials/data/documentation/vision/<symbol>.json`), and
signatures from the SDK's `Vision.swiftinterface`. [V]

```swift
// cd-vision (sketch, macOS 15 API; not compiled here). Coordinates: Vision normalises with origin bottom-left.
import Foundation
import Vision
import CoreImage
import ImageIO
let url = URL(fileURLWithPath: CommandLine.arguments[2])
let src = CGImageSourceCreateWithURL(url as CFURL, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any]
let orient = CGImagePropertyOrientation(rawValue: (props?[kCGImagePropertyOrientation] as? UInt32) ?? 1) ?? .up
let handler = ImageRequestHandler(url, orientation: orient)          // pass EXIF orientation!
let (faces, attention, objects) = try await handler.perform(
    DetectFaceRectanglesRequest(), GenerateAttentionBasedSaliencyImageRequest(),
    GenerateObjectnessBasedSaliencyImageRequest())
// … emit JSON of faces.map(\.boundingBox), attention.salientObjects, objects.salientObjects
if CommandLine.arguments[1] == "cutout",
   let obs = try await handler.perform(GenerateForegroundInstanceMaskRequest()) {
    let buf = try obs.generateMaskedImage(for: obs.allInstances, imageFrom: handler, croppedToInstancesExtent: false)
    try CIContext().writePNGRepresentation(of: CIImage(cvPixelBuffer: buf),
        to: URL(fileURLWithPath: CommandLine.arguments[3]), format: .RGBA8,
        colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
}
```

**Pitfalls:**
- `VNImageRequestHandler(cgImage:)` on pixels from `CGImageSourceCreateImageAtIndex` ignores EXIF orientation. Phone
  photos then produce rotated boxes. Pass `orientation:`, or normalise first with Pillow `ImageOps.exif_transpose`. **[U]**
  for the exact failure, but a documented Vision parameter.
- iPhone photos are Display P3. Convert to sRGB deliberately (Pillow `ImageCms`, or CoreImage with an explicit colour space),
  so cutouts don't shift colour. **[U]**
- Instance masks are soft (alpha matte). Inspect hair and edges, and add a 1–2 px feather or decontaminate when compositing
  on a very different background. **[U]**

**Smart crop:**
1. Score each candidate crop of the target aspect by the fraction of the saliency heat-map mass inside it, requiring face
   boxes to be fully inside, with ≥ 8 % headroom above the eyes line **[U]** heuristic.
2. Clamp the crop to the image.
3. Apply it without re-encoding using CSS `object-view-box: xywh(x y w h)` (Chrome 104). Alternatively use
   `object-fit: cover; object-position: <cx>% <cy>%`, or pre-crop with Pillow.
4. The upscaling QA must use the *crop* size (§6.4).

### 6.2 Alternatives to Vision

| Tool | Licence | Python 3.9 | Notes |
|---|---|---|---|
| OpenCV `opencv-python-headless` 5.0.0.93 (2026-07-02) | Apache-2.0 (also contrib) | yes (abi3 cp37 wheels, macOS 13 arm64), needs numpy ≤ 2.0.2 on 3.9 | Face: `cv2.FaceDetectorYN` + YuNet ONNX (opencv_zoo, **MIT**; `face_detection_yunet_2023mar.onnx`, 2026may variant exists). Saliency: `opencv-contrib` `saliency` module (spectral residual, fine-grained) [V repo] |
| **rembg** 2.0.85 (2026-09-20) | MIT (code) | **no** (≥ 3.11; 2.0.61 last for 3.9) | Default model is now **`bria-rmbg` (RMBG-2.0)**: BRIA licence, **paid agreement needed for commercial use** [V README, HF card]. Commercial-safe choices: `birefnet-general`/`-portrait` (BiRefNet, **MIT**), `isnet-general-use` (DIS, **Apache-2.0**), `u2net` (**Apache-2.0**), `sam` (Apache-2.0). Needs onnxruntime. Models download to `~/.rembg`. Its `withoutbg` backend uploads images to a third-party API, so don't use it |
| Core Image | Apple | — | `CIKMeans` (palette), `CIAreaAverage` (region mean; builtins accessor macOS 11) [V headers] |

**Default recommendation:** Vision first (local, fast, no model licensing). Use rembg with `-m birefnet-general` only as
an opt-in fallback in a separate Python ≥ 3.11 venv.

### 6.3 Dominant colours

```python
from PIL import Image
im = Image.open(p).convert("RGB"); im.thumbnail((256, 256))
q = im.quantize(colors=6, method=Image.Quantize.MEDIANCUT, kmeans=2)     # RGB only for MEDIANCUT
pal = q.getpalette()[:18]; counts = sorted(q.getcolors(), reverse=True)  # [(count, index), …]
swatches = [("#%02x%02x%02x" % tuple(pal[i*3:i*3+3]), c) for c, i in counts]
```

Then convert to OKLCH (a small formula, no library) to assign roles (dark base, accent, light). Ignore swatches under
3 % coverage, and ignore near-greys when choosing an accent **[U]** heuristic. The Swift alternative is `CIKMeans` in the same Vision helper.

### 6.4 Text-over-image contrast and upscaled-image checks

- **Two-pass render** (CDP): capture the final image; then add a class that sets
  `color: transparent !important; -webkit-text-stroke-color: transparent !important` on text. Shadows and scrims stay
  painted **[U]**. Capture the **background plate**, then take each text item's line boxes from
  `Range.getClientRects()` × DSF. codex-design already captures a `bg` plate. [V file read]
- For each text box:
  - Downsample the plate crop (≤ 256 px on the long side).
  - Compute WCAG relative luminance per pixel: sRGB channel c/255 → `c ≤ 0.04045 ? c/12.92 : ((c+0.055)/1.055)^2.4`;
    `L = 0.2126R + 0.7152G + 0.0722B`.
  - Contrast = `(Lmax+0.05)/(Lmin+0.05)` against the text colour, with opacity composited.
  - Report the **10th-percentile** contrast and the % of pixels below threshold, not just the mean.
  - Thresholds: WCAG 4.5:1 body, 3:1 large text [D W3C WCAG 2.2]. For social canvases, judge "large" at the
    *display* scale: a 1080-px canvas is shown ~390 pt wide on phones (~0.36×). **[U]**
- **APCA** (`apca-w3`): its "Limited W3 License" restricts use to web content for WCAG purposes, with patents pending.
  Don't embed it in a print/social tool. [V licence file]
- **Upscaling:** for every `<img>` and CSS background image, compare `naturalWidth/Height` with the rendered box × DSF.
  Use the crop rect for `object-view-box`, and the `cover` scale for `object-fit: cover`.
  - Raster outputs: flag scale > 1.0 (warn above 1.0, error above 1.5 **[U]**).
  - Print: effective ppi = natural px ÷ printed inches. Warn below 300 and error below 200 **[U]** (common prepress practice).

---

## 7. PDF post-processing without Ghostscript

### 7.1 Libraries

| | **pypdf** | **pikepdf** |
|---|---|---|
| Latest | 6.19.0 (2026-09-16), **supports Python ≥ 3.9**. Installed in the codex-design venv | 10.13.0 (2026-09-05), Python ≥ 3.10; **9.11.0** is last for 3.9 |
| Licence | BSD-3-Clause, pure Python | **MPL-2.0** (file-level copyleft only; fine to use unmodified); bundles qpdf (Apache-2.0) |
| Merge | `PdfWriter().append("a.pdf")` | `pdf.pages.extend(other.pages)` |
| Boxes | `page.trimbox/bleedbox/cropbox/artbox = RectangleObject(…)` [V docs] | `page.TrimBox = [x0, y0, x1, y1]` |
| Info metadata | `writer.add_metadata({...})` | `pdf.docinfo` |
| XMP | `pypdf.xmp.XmpInformation.create()` + `writer.xmp_metadata = xmp` (**since 6.1.0**, 2025-09-21) [V changelog] | `with pdf.open_metadata() as m: m['dc:title'] = …` (keeps Info and XMP in sync) [V docs] |
| OutputIntent | No high-level API; build the dict yourself [V code search] | Same (low-level objects) |
| Other | Encryption, forms, annotations | Linearization, object-level repair, fast |

Both are fine. Use pypdf, already installed and 3.9-compatible, for boxes and metadata. Use pikepdf for heavy
structural edits (after a Python upgrade, or pin 9.11.0).

```python
# OutputIntent + PDF/X hints (sketch; does NOT by itself make a compliant PDF/X)
import pikepdf
pdf = pikepdf.open("flyer.print.pdf")
icc = pdf.make_stream(open("/System/Library/ColorSync/Profiles/sRGB Profile.icc", "rb").read()); icc.N = 3
pdf.Root.OutputIntents = pikepdf.Array([pikepdf.Dictionary(
    Type=pikepdf.Name.OutputIntent, S=pikepdf.Name.GTS_PDFX,
    OutputConditionIdentifier="sRGB IEC61966-2.1", RegistryName="http://www.color.org", DestOutputProfile=icc)])
with pdf.open_metadata() as m:
    m["dc:title"] = "Autumn flyer"
pdf.save("flyer.x.pdf")
```

### 7.2 What "PDF/X" honestly means here

- PDF/X needs these *and* compliant content: an OutputIntent, TrimBox/BleedBox, the `GTS_PDFXVersion` Info/XMP identification,
  all fonts embedded, and colour spaces allowed by the chosen level (X-1a: CMYK/spot only, no transparency; X-3: plus ICC-based
  colour; X-4: plus live transparency). Chrome writes **DeviceRGB** colour, transparency groups and possibly Type 3 fonts.
  Stamping identifiers onto a Chrome PDF therefore produces a PDF that *claims* PDF/X without being checked. **[U]** for the exact
  level-by-level rules; confirm with the print vendor.
- No free validator covers PDF/X (veraPDF targets PDF/A and PDF/UA). Validation needs Acrobat Pro Preflight, callas pdfToolbox or
  Enfocus PitStop, all commercial. **[U]**
- Recommendation: add Trim/Bleed boxes and clean metadata, and label the file "print-ready RGB PDF". Don't claim PDF/X unless
  it was produced by WeasyPrint's PDF/X mode (with CMYK content) or verified by the printer.

### 7.3 CMYK conversion options

| Route | How | Keeps vectors/text? | Limitations |
|---|---|---|---|
| **A. RGB PDF → printer's RIP** (default) | Deliver sRGB vector PDF (+ Trim/Bleed). Many digital and online printers accept RGB **[U]** | yes | Colour conversion is out of our control. Warn about saturated RGB (neon, pure blue/green) shifting |
| **B. Raster CMYK PDF** (in-house, no install) | Render the page with Chrome at 300 ppi (DSF 3.125; 600 ppi for fine text), then Pillow `ImageCms` (LittleCMS 2.17) sRGB → press profile, then `Image.save('x.pdf', resolution=300)` (Pillow writes DeviceCMYK DCT images [V `PdfImagePlugin.py`]), then add boxes + OutputIntent | **no**, everything is a raster | Black text becomes 4-colour rich black (registration risk under ~9 pt); no K-only text; large files; JPEG in PDF (use q ≥ 95) |
| **C. WeasyPrint vector CMYK** | Author in `device-cmyk()` plus a CMYK ICC `@color-profile`; pre-convert photos to CMYK with Pillow; `weasyprint in.html out.pdf --pdf-variant=pdf/x-4` | yes | Python ≥ 3.10 + Pango; separate CSS dialect; no JS |
| D. macOS Quartz "Create Generic PDFX-3 Document" filter | Preview export or Quartz API | partly | **Flattens transparency at 72×72 dpi**, uses a generic SWOP condition ("CGATS TR 001"), adds bleed/trim boxes [V: `plutil` of the `.qfilter`] → **unsuitable** |
| E. Ghostscript / MuPDF (AGPL) / Acrobat / callas | — | yes | Excluded, or licence/cost bound |

```python
from PIL import Image, ImageCms
rgb = Image.open("flyer_300ppi.png").convert("RGB")
srgb = ImageCms.createProfile("sRGB")
press = ImageCms.getOpenProfile("PSOcoated_v3.icc")       # FOGRA51 from eci.org (download manually; check terms)
xf = ImageCms.buildTransform(srgb, press, "RGB", "CMYK",
        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
cmyk = ImageCms.applyTransform(rgb, xf)
cmyk.save("flyer_cmyk.tif", compression="tiff_lzw", dpi=(300, 300), icc_profile=press.tobytes())
cmyk.save("flyer_cmyk.pdf", resolution=300, quality=95)   # then add Trim/Bleed + OutputIntent (N=4 profile)
```

(API names checked against Pillow 11.3.0 `ImageCms.py`: `Intent`, `Flags.BLACKPOINTCOMPENSATION`, `buildTransform`,
`applyTransform`, `getOpenProfile`, `tobytes` [V]. Whether `quality` reaches the PDF's JPEG encoder is **[U]**.)

Profiles: Apple's `Generic CMYK Profile.icc` is on disk, but it is **not** a press standard. Use the ECI sets (PSO Coated v3 /
FOGRA51, PSO Uncoated v3 / FOGRA52, ISO Coated v2 / FOGRA39) or GRACoL 2013 as the printer specifies. The ECI downloads page
lists them but states no licence terms, so check before redistributing. [V page read]

---

## 8. Recommendations for our skill

### 8.1 Chosen stack

1. **Renderer: installed Google Chrome, driven over CDP by `--remote-debugging-pipe`** (the Python stdlib client already in
   codex-design). Use one warm browser per batch, a new target per job, and a throwaway `--user-data-dir` per process.
   - Launch flags: `--headless --remote-debugging-pipe --user-data-dir=<mkdtemp> --force-color-profile=srgb --hide-scrollbars
     --use-mock-keychain --password-store=basic --no-first-run --no-default-browser-check --disable-extensions --disable-sync
     --disable-background-networking --disable-component-update --mute-audio --allow-file-access-from-files`,
     plus `--run-all-compositor-stages-before-draw` optionally.
   - Per job: `Emulation.setDeviceMetricsOverride(W, H, DSF)`, then `Page.navigate`, then an in-page settle: explicit
     `document.fonts.load()` for each face and text sample, `fonts.ready`, and `img.decode()`.
   - Then run the QA script via `Runtime.evaluate(awaitPromise)` and `CSS.getPlatformFontsForNode` on text nodes.
   - Capture: final PNG (clip W×H), the background plate for contrast, and a PDF with
     `{printBackground:true, preferCSSPageSize:true, displayHeaderFooter:false}`.
   - Encode JPEG/WebP/AVIF in Pillow with an embedded sRGB ICC profile and dpi metadata.
2. **Print PDFs:** size with CSS `@page` (trim + bleed) and `margin: 0`; use static TrueType fonts only; set
   `font-synthesis: none`; no blurred text-shadows on print text. Then use pypdf to set TrimBox/BleedBox and Info/XMP
   metadata. QA with `pdfinfo -box`, with `pdffonts` (fail print jobs on **Type 3**, warn on screen PDFs), and with
   `pdftoppm -r 150` for a visual diff against the PNG. Label the output "print-ready RGB PDF".
3. **Fonts:** Fontsource API + jsDelivr, pinned (`@{npmVersion}`), cached per job with licence files. Download **static** files
   for print. WOFF2 subsets are fine for screen, and variable (`:vf`) files are for screen only. Use the google/fonts raw repo (pinned SHA)
   for families Fontsource lacks. Never use system fonts; any glyph drawn by a non-custom font is an error.
4. **Assets:** icons are pinned jsDelivr SVGs (Lucide/Tabler/Phosphor/Iconoir/Material Symbols), inlined. QR codes come from
   segno inline SVG: EC M (H with a logo), 4-module quiet zone, module ≥ 0.5 mm in print. After export, verify by decoding
   with Vision. Charts are hand SVG for small data and Vega-Lite rendered in-page (cached UMD builds) for real data. Emoji are
   Noto/Twemoji SVG images. Grain is `feTurbulence` with a fixed seed.
5. **Image ops:** the compiled Swift Vision helper. Pass EXIF orientation. Use faces + attention/objectness for smart crop
   (applied through `object-view-box` or a Pillow crop), subject lift on macOS 14+, aesthetics scoring on 15+ to rank
   candidate photos, and barcode decoding for QR QA. Pillow `quantize` handles palettes; WCAG math on the background plate handles contrast.
6. **CMYK:** default to RGB PDF plus printer conversion. Offer the "raster CMYK PDF" (route B) on request, with its
   limitations stated. Add route C (WeasyPrint PDF/X-4) only if a client requires true vector CMYK and a Python ≥ 3.10
   venv is approved.

### 8.2 Fallbacks

- **CDP fails** → the bare CLI: `--screenshot` / `--print-to-pdf` / `--dump-dom` with `--window-size`,
  `--force-device-scale-factor`, `--virtual-time-budget=8000`, `--timeout`, a subprocess timeout, and output validation
  (§1.4). In-page QA publishes through the `__qa__` JSON block.
- **Chrome missing or broken after an auto-update** → the cached Chrome for Testing 152 or chrome-headless-shell 152
  (same CLI flags; `--font-render-hinting` works there).
- **Background removal quality issue** → rembg `birefnet-general` (MIT) in a separate venv (needs Python ≥ 3.11 and approval).
- **Pillow must draw Bengali** (e.g. a label on a contact sheet) → run with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`
  and `layout_engine=RAQM`; otherwise route it through Chrome.
- **Paged.js** only if a multi-page document needs `string-set`, running elements or cross-references. Chrome ≥ 131 margin
  boxes cover page numbers.

### 8.3 Gap check against the current codex-design files (read-only review, 2026-09-23)

- **Add `--force-color-profile=srgb`** to the launch args in `scripts/design.py` (both Puppeteer and Playwright force it).
- **`--font-render-hinting=none` is inert** in Google Chrome (headless-shell only). Keep or drop it, but don't rely on it.
- **PDF font check:** `pdffonts` reports Type 3 as embedded, so also parse the *type* column and flag `Type 3` for print jobs
  (variable/CFF/restricted fonts, synthetic bold, blurred shadows). `install_fonts` downloads static per-weight WOFF2, which is good.
  Keep variable files out of print jobs.
- **`scripts/vision.swift`** builds `VNImageRequestHandler(cgImage:options:)` without an orientation. Pass
  `orientation: CGImagePropertyOrientation(from EXIF)`, or normalise the image first.
- **Hyphenation expectations:** macOS Chrome cannot hyphenate bn, hi or ar. Don't count `hyphens:auto` as a remedy for Bengali.
- **Record Chrome's version** (`Browser.getVersion`) in each render's JSON, because stable is now on a ~2-week cadence (154 shipped on 2026-09-22).
- **Security:** `--allow-file-access-from-files` lets any rendered page read local files. Keep rendering Claude-authored HTML
  only, and consider `Fetch.enable` to block non-local requests during renders.

---

## 9. Sources (accessed 2026-09-23 unless stated)

Chromium / Chrome (source at `main` on 2026-09-23 via raw.githubusercontent.com/chromium/chromium):
- `components/headless/command_handler/headless_command_switches.cc`, `headless_command_handler.cc`, `headless_command.js`
- `chrome/browser/headless/headless_mode_init.cc`, `headless_mode_platform_mac.mm`, `headless_command_processor.cc`, `test/headless_mode_command_browsertest.cc`
- `chrome/browser/ui/startup/startup_browser_creator_impl.cc` (exit behaviour); `chrome/browser/devtools/protocol/browser_handler.cc` (`SetContentsSize`)
- `components/headless/screen_info/README.md`; `ui/display/display_switches.cc`; `ui/gfx/switches.cc`; `content/public/common/content_switches.cc`; `cc/base/switches.cc`; `components/viz/common/switches.cc`; `headless/public/switches.h`, `headless/lib/browser/command_line_handler.cc`
- `content/browser/devtools/protocol/page_handler.cc` (JPEG default 80; 128K guard); `content/browser/devtools/devtools_pipe_handler.cc`; `content/browser/loader/file_url_loader_factory.cc` (file:// CORS)
- `components/printing/browser/print_to_pdf/pdf_print_utils.cc` (1 cm default margins); `components/printing/renderer/print_render_frame_helper.cc`; `printing/common/metafile_utils.cc` (`fRasterDPI=300`; macOS alpha-gradient rasterisation, commit 67832c51d5ba, 2026-06-24, Chrome 151)
- `third_party/blink/public/public_features.gni`; `third_party/blink/renderer/platform/text/apple/hyphenation_apple.cc`; `…/text/hyphenation/hyphenation_minikin.cc`; `third_party/blink/renderer/core/css/css_properties.json5`; `…/platform/runtime_enabled_features.json5`; `…/platform/fonts/README.md`
- Commit history via GitHub API (`repos/chromium/chromium/commits?path=…`) and milestones via https://chromiumdash.appspot.com/fetch_commits and `fetch_releases` / `fetch_milestone_schedule`
- https://developer.chrome.com/docs/chromium/headless (updated 2024-10-21) · https://developer.chrome.com/blog/removing-headless-old-from-chrome (2024-10-23) · https://developer.chrome.com/blog/chrome-headless-shell · https://developer.chrome.com/docs/automation-and-testing/headless-screen-config (updated 2026-01-13) · https://developer.chrome.com/blog/remote-debugging-port (2025-03-17) · https://developer.chrome.com/blog/colrv1-fonts (2022-01-06)
- https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md (last commit 2025-09-25)
- DevTools protocol JSON: https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json (HEAD 2026-09-22)

Skia (main, last commit to `SkPDFFont.cpp` 2026-09-10): `src/pdf/SkPDFFont.cpp` (`FontType`), `src/ports/SkTypeface_mac_ct.cpp`, `src/sfnt/SkOTUtils.cpp`, `src/pdf/SkPDFGraphicState.cpp`, `src/pdf/SkPDFDevice.cpp`, `src/pdf/SkPDFSubsetFont.cpp`.

Automation libraries: Puppeteer `packages/puppeteer-core/src/node/ChromeLauncher.ts`, `BrowserLauncher.ts`, `PipeTransport.ts`, `src/common/PDFOptions.ts` (main) · Playwright `packages/playwright-core/src/server/chromium/chromiumSwitches.ts`, `docs/src/api/class-page.md`, `docs/src/api/params.md`, `tests/library/screenshot.spec.ts` (main) · npm registry `registry.npmjs.org/<pkg>` · PyPI JSON `pypi.org/pypi/<pkg>/json`.

Print engines: WeasyPrint docs (`docs/api_reference.rst`, `docs/common_use_cases.rst`, `docs/first_steps.rst`, `docs/changelog.rst`, `weasyprint/pdf/pdfx.py`, main) · Paged.js `src/modules/paged-media/atpage.js`, `src/polyfill/polyfill.js` (main) · Satori README (main, 2026-08-20 commits) · resvg README (linebender/resvg, v0.48.1).

Text: Pillow docs `docs/installation/building-from-source.rst`, source `src/thirdparty/fribidi-shim/fribidi.c`, `src/PIL/ImageCms.py` and `PdfImagePlugin.py` at tag 11.3.0.

Fonts: https://developers.google.com/fonts/docs/css2 (updated 2024-07-23) · https://developers.google.com/fonts/docs/developer_api (updated 2025-09-11) · https://fontsource.org/docs/api/introduction · https://api.fontsource.org/v1/fonts · https://github.com/google/fonts · https://openfontlicense.org/ofl-faq/ (1.1-update7, Nov 2023) · https://www.apple.com/legal/sla/docs/macOSTahoe.pdf (§2.E) · https://github.com/googlefonts/noto-emoji (README, release v2.051) · https://github.com/jdecked/twemoji (v17.0.3) · https://github.com/adobe-fonts/adobe-blank-2.

CSS support: MDN browser-compat-data via https://cdn.jsdelivr.net/gh/mdn/browser-compat-data@main/ (css/properties/*, css/types/*, css/at-rules/page.json).

Assets: lucide-icons/lucide LICENSE · tabler/tabler-icons · phosphor-icons/core · iconoir-icons/iconoir · google/material-design-icons · simple-icons · heuer/segno (`segno/__init__.py`, `writers.py`; docs https://segno.readthedocs.io/en/latest/make.html and /serializers.html) · lincolnloop/python-qrcode README · https://www.qrcode.com/en/howto/cell.html and /code.html (DENSO WAVE) · vega/vega `packages/vega-scenegraph/src/util/text.js`.

Vision: Apple docs JSON `https://developer.apple.com/tutorials/data/documentation/vision/{vngenerateforegroundinstancemaskrequest, vngenerateattentionbasedsaliencyimagerequest, vngenerateobjectnessbasedsaliencyimagerequest, vndetectfacerectanglesrequest, vngeneratepersonsegmentationrequest, vndetectbarcodesrequest, vnrecognizetextrequest, generateforegroundinstancemaskrequest, calculateimageaestheticsscoresrequest}.json` · local SDK `Vision.swiftinterface`, `CIFilterBuiltins.h`.

Image-op alternatives: danielgatis/rembg README · Hugging Face model cards briaai/RMBG-2.0 and RMBG-1.4 (licence "other", BRIA) · xuebinqin/U-2-Net & DIS (Apache-2.0) · ZhengPeng7/BiRefNet (MIT) · facebookresearch/segment-anything (Apache-2.0) · opencv/opencv, opencv_contrib (Apache-2.0) · opencv/opencv_zoo `models/face_detection_yunet/README.md` (MIT) · Myndex/apca-w3 LICENSE.md.

PDF: py-pdf/pypdf docs (`docs/user/metadata.md`, `cropping-and-transforming.md`, `pdfa-compliance.md`) and CHANGELOG (6.1.0) · pikepdf docs `docs/topics/metadata.md` · qpdf LICENSE (Apache-2.0) · ECI downloads https://www.eci.org/en/downloads · local `/System/Library/Filters/Create Generic PDFX-3 Document.qfilter`.
