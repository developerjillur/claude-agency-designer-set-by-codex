# Print formulas

Verified 2026-09-24. Every constant below is tagged with where it came from. "Official" means the platform's own help page, guide or calculator. "Derived" means arithmetic on official numbers, with the working shown. Nothing here is a guess unless it says "estimate".

Units used throughout: 1 in = 25.4 mm. 1 pt = 1/72 in = 0.3528 mm. Raster px = inches x ppi (round up so the bleed is fully covered). For a PDF, set the CSS page to the full bleed size in physical units (for example `@page { size: 12.85in 9.25in; margin: 0 }`) and never to px.

---

## 1. Amazon KDP paperback: full wrap cover

Sources (official):
- Create a Paperback Cover, https://kdp.amazon.com/en_US/help/topic/G201953020 (no page date shown; read 2026-09-24).
- KDP cover calculator, https://kdp.amazon.com/cover-calculator (its results table was queried directly for the numbers marked "calculator").
- Barcodes, https://kdp.amazon.com/en_US/help/topic/G5HDYGP4BXLX4RUW
- Print Options (trim sizes, paper, page counts), https://kdp.amazon.com/en_US/help/topic/G201834180

### Formula

```
spine_in     = page_count x caliper_in
cover_w_in   = 0.125 + trim_w + spine_in + trim_w + 0.125
cover_h_in   = 0.125 + trim_h + 0.125
```

| Interior and paper | caliper per page | source |
|---|---|---|
| Black ink, white paper | 0.002252 in (0.0572 mm) | help page |
| Black ink, cream paper | 0.0025 in (0.0635 mm) | help page |
| Standard colour, white paper | 0.002252 in (0.0572 mm) | help page |
| Premium colour, white paper | 0.002347 in (0.0596 mm) | help page |
| Black ink, groundwood paper (new in 2026) | 0.00235 in (0.0597 mm) | calculator (240 pages gave 0.564 in); not yet on the help page |

There is no added constant. Some third-party calculators add "+0.06 in"; that is Lulu's formula, not KDP's. The official calculator returns exactly page_count x caliper (240 cream pages = 0.600 in).

### Zones

| Item | Value | Source |
|---|---|---|
| Bleed | 0.125 in (3.2 mm; the calculator shows 3.17 mm) on top, bottom and both outside edges | help page, calculator |
| Text safe margin from trim | 0.125 in (3.2 mm) inside every trim line | help page, calculator |
| Spine text margin | 0.0625 in (1.6 mm) from each spine fold | help page, calculator ("0.062") |
| Spine text allowed | from 79 pages (the page says "at least 79" twice and "more than 79" once); Cover Creator needs 80 | help page |
| Borders | not recommended; if used, keep them at least 0.25 in (6.4 mm) inside trim | help page |
| Barcode box | 2 x 1.2 in (50.8 x 30.5 mm) white box, lower right of the back cover, 0.25 in (6.3 mm) from the spine fold and from the bottom trim. Minimum if you supply your own: 1.4 x 0.8 in (35.56 x 20.3 mm). Solid white background. Right-to-left books: lower left. | Barcodes page, calculator ("Barcode Margin 0.25") |
| Resolution | 300 dpi minimum | help page |
| Colour | CMYK images recommended; profiles are stripped; no spot colours | help page |
| File | one PDF (back, spine, front), 650 MB max, 40 MB or less recommended; remove crop marks and template text | help page |
| Page count | 24 to 828 (5 x 8 in, white); cream max 776; groundwood max 812; standard colour 72 to 600 | Print Options |
| Custom trim | width 4 to 8.5 in, height 6 to 11.69 in | Print Options |

Known inconsistency on the help page: it says spine shift of "0.0125 in (3.2 mm)". Those two numbers disagree (3.2 mm is 0.125 in). Treat the spine as able to move 0.0625 in either way, which is what the same page says elsewhere, and keep hard colour edges off the spine folds.

### Worked example: 6 x 9 in, 240 pages, cream

```
spine   = 240 x 0.0025            = 0.600 in  (15.24 mm)
width   = 0.125 + 6 + 0.6 + 6 + 0.125 = 12.850 in (326.39 mm)
height  = 0.125 + 9 + 0.125       = 9.250 in  (234.95 mm)
raster  = 3855 x 2775 px at 300 ppi
```
The official calculator returned exactly "Full Cover 12.85 x 9.25 in", "Spine 0.6", "Spine Safe Area 0.475 x 8.75".

Panel x positions, measured from the left edge of the file (back cover is on the left for left-to-right books):

| Panel | from | to |
|---|---|---|
| Left bleed | 0 | 0.125 in |
| Back cover | 0.125 | 6.125 in |
| Spine | 6.125 | 6.725 in |
| Front cover | 6.725 | 12.725 in |
| Right bleed | 12.725 | 12.850 in |
| Spine text box | 6.1875 | 6.6625 in (0.475 in wide) |
| Barcode box | x 3.875 to 5.875 in, y 7.675 to 8.875 in (from top-left of the file) | |

For comparison, white paper at 240 pages gives a 0.540 in spine and a 12.79 in wide file; premium colour gives 0.563 in and 12.813 in; groundwood gives 0.564 in and 12.814 in (all read from the calculator).

---

## 2. Amazon KDP hardcover (case laminate)

Sources (official):
- Create a Hardcover Cover, https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6
- Hardcover Print Elements, https://kdp.amazon.com/en_US/help/topic/GKZVNAAFYWVKZWL8
- KDP cover calculator, binding "CASE_LAMINATE" (queried directly).

### Formula

```
board_w   = trim_w + 0.197 in (5 mm)
board_h   = trim_h + 0.236 in (6 mm)
spine_in  = page_count x caliper_in + 0.189 in (4.8 mm)
wrap      = 0.591 in (15 mm) on all four outside edges
cover_w   = wrap + board_w + spine + board_w + wrap
cover_h   = wrap + board_h + wrap
hinge     = 0.394 in (10 mm) band on the front and on the back board, next to the spine: no text, no barcode
```

How the constants were fixed: the calculator was queried at 76, 100, 120, 200, 240, 300, 400 and 550 pages (white), 76, 240 and 300 (cream), 76 and 240 (premium colour). Every result fits page_count x caliper + 0.189 in within the calculator's 3-decimal rounding (in mm the fit is exact: 240 cream = 15.24 + 4.8 = 20.04 mm). The board, wrap and hinge values are printed by the calculator itself ("Front Cover 6.197 x 9.236", "Wrap 0.591", "Hinge 0.394" for a 6 x 9 in book; "Wrap 15", "Hinge 10", "Front Cover 157.4 x 234.6" in mm). The 0.189 in spine allowance is derived, not printed.

| Item | Value | Source |
|---|---|---|
| Papers | white, cream, premium colour (no groundwood, no standard colour for hardcover) | Print Options, calculator config |
| Page count | 75 to 550 (help page); the calculator's config says minimum 76 | Print Options, calculator |
| Trims | 5.5 x 8.5, 6 x 9, 6.14 x 9.21, 7 x 10, 8.25 x 11 in | Print Options |
| Text margin | 0.125 in inside the board edge (calculator "Margin 0.125") | calculator |
| Spine text margin | 0.062 in each side | calculator |
| Barcode | 2 x 1.2 in (50.8 x 30.5 mm); at least 0.76 in (19 mm) from the bottom of the cover and 0.25 in (6 mm) from the spine hinge; Amazon's own barcode goes in the lower right of the back cover. Calculator barcode margin 0.25 x 0.375 in | help page, calculator |
| Headband | added when the book has more than 120 pages | help page |
| Board | 2 mm thick case board, gloss or matte laminate | Print Elements |
| Resolution | 300 dpi | help page |

Known inconsistency on the help page: "Wrap 0.51 in (15 mm)" and "text 0.635 in (16 mm) from the edge". 15 mm is 0.591 in, which is what the calculator uses. Follow the calculator: wrap 0.591 in, text at least 0.125 in inside the board edge, so at least 0.716 in (18.2 mm) from the file edge.

### Worked example: 6 x 9 in, 240 pages, cream

```
board   = 6.197 x 9.236 in
spine   = 240 x 0.0025 + 0.189 = 0.789 in (20.04 mm)
width   = 0.591 + 6.197 + 0.789 + 6.197 + 0.591 = 14.364 in (364.84 mm)
height  = 0.591 + 9.236 + 0.591 = 10.417 in (264.6 mm)
raster  = 4310 x 3126 px at 300 ppi (rounded up)
```
The calculator returned "Full Cover 14.364 x 10.417 in" and "364.84 x 264.6 mm".

Panel x positions from the left edge: wrap 0 to 0.591; back board 0.591 to 6.787 (hinge band 6.393 to 6.787); spine 6.787 to 7.576; front board 7.576 to 13.773 (hinge band 7.576 to 7.970); wrap 13.773 to 14.364 in.

---

## 3. IngramSpark (Lightning Source)

Sources (official):
- File Creation Guide, dated 8.24.26 on its cover, https://www.ingramspark.com/hubfs/downloads/file-creation-guide.pdf
- Cover File Creation (help centre, updated 2026-09-24), https://help.ingramspark.com/hc/en-us/articles/35306346735245-Cover-File-Creation
- Trim sizes and papers (updated 2026-09-11), https://help.ingramspark.com/hc/en-us/articles/5341425168013
- Case Laminate and Digital Cloth (updated 2026-09-08), https://help.ingramspark.com/hc/en-us/articles/35304333693837
- Weight and Spine Width Calculator, https://myaccount.ingramspark.com/Portal/Tools/SpineCalculator (queried directly for the table below).

IngramSpark does not publish a per-page spine formula. The spine comes from its calculator or its Cover Template Generator. The only published paper figure is groundwood "PPI = 408" (pages per inch). The table below is what the official calculator returned for a 6 x 9 in book (spine in inches).

| Paper / binding | 24 | 48 | 100 | 150 | 200 | 240 | 300 | 400 | 500 | 600 | 800 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Paperback, creme 50# | 0.058 | 0.115 | 0.240 | 0.348 | 0.458 | 0.545 | 0.674 | 0.890 | 1.114 | 1.333 | 1.767 |
| Paperback, white 50# (same for standard colour 50#) | 0.050 | 0.099 | 0.207 | 0.321 | 0.424 | 0.505 | 0.629 | 0.821 | 1.005 | 1.213 | 1.590 |
| Paperback, groundwood 38# | 0.068 | 0.127 | 0.255 | 0.378 | 0.502 | 0.600 | 0.748 | 0.994 | 1.241 | 1.487 | 1.980 |
| Paperback, white 70# (same for standard colour 70#) | 0.065 | 0.130 | 0.272 | 0.408 | 0.543 | 0.652 | 0.815 | 1.087 | 1.359 | 1.630 | 2.174 |
| Paperback, premium colour 70# | 0.062 | 0.125 | 0.260 | 0.390 | 0.520 | 0.623 | 0.779 | 1.039 | 1.299 | 1.558 | 2.078 |
| Case laminate, creme | 0.250 | 0.250 | 0.375 | 0.500 | 0.625 | 0.688 | 0.813 | 1.000 | 1.250 | 1.500 | 1.938 |
| Case laminate, white 50# | 0.250 | 0.250 | 0.313 | 0.375 | 0.500 | 0.563 | 0.688 | 0.875 | 1.063 | 1.313 | 1.688 |
| Case laminate, groundwood | 0.250 | 0.250 | 0.375 | 0.500 | 0.625 | 0.750 | 0.875 | 1.125 | 1.375 | 1.625 | 2.125 |
| Case laminate, premium colour | 0.250 | 0.250 | 0.375 | 0.500 | 0.688 | 0.750 | 0.938 | 1.188 | 1.438 | 1.688 | 2.188 |

Reading the table: paperback spines are close to linear but not exactly (creme works out to about 0.0022 in per page at high counts, about 0.0024 in at low counts), so interpolate between columns and then confirm with the calculator. Case laminate spines are rounded to 1/16 in with a 0.25 in minimum. Page counts must be even ("mod2").

### Paperback cover

```
cover_w = 0.125 + trim_w + spine + trim_w + 0.125
cover_h = 0.125 + trim_h + 0.125
```

| Item | Value | Source |
|---|---|---|
| Bleed | 0.125 in (3 mm) all four sides | guide p.18, help |
| Type safety | 0.25 in (6 mm) recommended on all sides; templates allow 0.125 in (3 mm) | guide p.18 to 19, help |
| Spine type safety | 0.0625 in (2 mm) each side for spines 0.35 in and wider; 0.03125 in (1 mm) for narrower spines | guide, help |
| Spine text | not allowed below 48 pages | guide, help |
| Barcode | mandatory. 100% black on a white box. If you do not supply one, leave 1.75 x 1 in free; the template's barcode is centred on the back cover and may be moved inside the safe area but not resized | guide p.19, help |
| Resolution | 300 ppi; images under 200 ppi may be rejected | guide |
| Colour | CMYK; rich black 60C 40M 40Y 100K; total ink 240% maximum; text 24 pt and smaller in 100% K only; convert spot colours | guide p.19 |
| PDF | PDF/X-1a:2001 (or PDF/X-3:2002); fonts embedded | guide, help |
| Variance | 1/16 in (0.0625 in, 2 mm) shift allowed on every book | guide p.4 |
| Template | artwork is placed on the template page, which is larger than the bleed box and carries crop marks; the PDF must stay at the template's page size | guide p.19 to 20 |

Worked example, 6 x 9 in, 240 pages, creme 50#: spine 0.545 in (13.843 mm, calculator), cover 12.795 x 9.25 in (324.99 x 234.95 mm), 3839 x 2775 px at 300 ppi.

### Casebound (case laminate) cover

```
board_w = trim_w - 0.185 in (5 mm)
board_h = trim_h + 0.25 in (6 mm)
cover_w = 0.625 + board_w + 0.5 + spine + 0.5 + board_w + 0.625   (in)
cover_h = 0.625 + board_h + 0.625
```
0.625 in (16 mm) is the wrap that folds round the board; 0.5 in (13 mm) is the gutter or hinge on each side of the spine. Both are stated in the guide (custom trim page) and the help centre (which gives the wrap as "0.625 in / 15mm"; 0.625 in is 15.9 mm). Keep important art out of the 0.5 in hinge.

Worked example, 6 x 9 in, 240 pages, creme: spine 0.688 in (calculator), board 5.815 x 9.25 in, cover 0.625 + 5.815 + 0.5 + 0.688 + 0.5 + 5.815 + 0.625 = 14.568 in wide, 10.5 in tall (370.03 x 266.7 mm), 4371 x 3150 px at 300 ppi.

Dust jacket (guide p.26 to 27): flaps 3.25 in (82.55 mm) each, plus a 0.25 in (6 mm) wrap strip between each cover panel and its flap, 0.125 in bleed, same safety rules. A full jacket formula is not printed in the guide; use the template.

---

## 4. Lulu

Source (official): Lulu Book Creation Guide (PDF created 2026-01-22), https://assets.lulu.com/media/guides/en/lulu-book-creation-guide.pdf ; Creating Your Hardcover Casewrap Cover, https://help.lulu.com/en/support/solutions/articles/64000308572-creating-your-hardcover-casewrap-cover

### Paperback

```
spine_in = page_count / 444 + 0.06
spine_mm = page_count / 17.48 + 1.524
cover_w  = 0.125 + trim_w + spine + trim_w + 0.125
cover_h  = 0.125 + trim_h + 0.125
```
- Bleed 0.125 in (3.175 mm) on every side. Safety margin 0.5 in (12.7 mm) inside the trim edge.
- Spine text: leave 0.125 in (3.175 mm) each side; no spine text at 80 pages or fewer.
- Minimum 32 interior pages for paperback, 24 for hardcover.
- Trim tolerance 0.125 in towards front and back.
- Images 300 to 600 ppi; fonts embedded; transparency flattened; no trim or bleed lines in the file.

Worked example, 6 x 9 in, 240 pages: spine 240 / 444 + 0.06 = 0.6005 in (15.25 mm); cover 12.851 x 9.25 in; 3856 x 2775 px.

### Hardcover casewrap

Spine comes from a table, not a formula:

| Pages | Spine | Pages | Spine | Pages | Spine |
|---|---|---|---|---|---|
| 24 to 84 | 0.25 in (6 mm) | 251 to 278 | 0.875 in (22 mm) | 501 to 528 | 1.438 in (37 mm) |
| 85 to 140 | 0.5 in (13 mm) | 279 to 306 | 0.938 in (24 mm) | 529 to 556 | 1.5 in (38 mm) |
| 141 to 168 | 0.625 in (16 mm) | 307 to 334 | 1 in (25 mm) | 557 to 582 | 1.563 in (40 mm) |
| 169 to 194 | 0.688 in (17 mm) | 335 to 360 | 1.063 in (27 mm) | 583 to 610 | 1.625 in (41 mm) |
| 195 to 222 | 0.75 in (19 mm) | 361 to 388 | 1.125 in (29 mm) | 611 to 638 | 1.688 in (43 mm) |
| 223 to 250 | 0.813 in (21 mm) | 389 to 416 | 1.188 in (30 mm) | 639 to 666 | 1.75 in (44 mm) |
| | | 417 to 444 | 1.25 in (32 mm) | 667 to 694 | 1.813 in (46 mm) |
| | | 445 to 472 | 1.313 in (33 mm) | 695 to 722 | 1.875 in (48 mm) |
| | | 473 to 500 | 1.375 in (35 mm) | 723 to 750 | 1.938 in (49 mm) |
| | | | | 751 to 778 | 2 in (51 mm) |
| | | | | 779 to 799 | 2.063 in (52 mm) |
| | | | | 800 | 2.125 in (54 mm) |

Casewrap zones (help article): the cover is printed 0.75 in larger than the front cover on each outside edge (wrap); boards overhang the pages by 0.125 in on the three open sides, so the finished cover is 0.125 in wider and 0.25 in taller than the trim; the hinge fold sits about 0.25 in (6 mm) from the spine on each board; artwork can land up to 0.25 in from its designed position.

```
board_w = trim_w + 0.125        board_h = trim_h + 0.25
cover_w = 0.75 + board_w + spine + board_w + 0.75
cover_h = 0.75 + board_h + 0.75
```
This assembly is derived from the help article's wording, not printed as a formula by Lulu. Confirm against the template Lulu generates after the interior upload.

Worked example, 6 x 9 in, 240 pages: spine 0.813 in (table row 223 to 250), cover 0.75 + 6.125 + 0.813 + 6.125 + 0.75 = 14.563 in by 0.75 + 9.25 + 0.75 = 10.75 in (derived).

---

## 5. BookBaby

Source (official help centre): https://support.bookbaby.com/hc/en-us/articles/205517898 , /205517798 , /360042283214 , /219635227

- No public formula. The spine is set by the custom cover template, downloadable after saving a quote; it depends on trim, cover style, paper and page count.
- Print-ready rules: page size = trim + bleed, 0.125 in bleed, CMYK (they will convert RGB but colours can shift), true black not registration black, fonts embedded or outlined, all images 300 dpi or more.
- Their own example: a US Trade (6 x 9 in) softcover of 200 pages has a 12.73 x 9.25 in cover document, which implies a 0.48 in spine (derived: 12.73 minus 12.25). Paper stock for that example is not stated.

---

## 6. Worked example side by side (6 x 9 in, 240 pages, cream or creme)

| Platform and binding | Spine | Full cover (in) | Full cover (mm) | px at 300 ppi | status |
|---|---|---|---|---|---|
| KDP paperback | 0.600 in | 12.850 x 9.250 | 326.39 x 234.95 | 3855 x 2775 | official calculator |
| IngramSpark paperback | 0.545 in | 12.795 x 9.250 | 324.99 x 234.95 | 3839 x 2775 | official calculator |
| Lulu paperback | 0.6005 in | 12.851 x 9.250 | 326.40 x 234.95 | 3856 x 2775 | official formula |
| KDP hardcover | 0.789 in | 14.364 x 10.417 | 364.84 x 264.60 | 4310 x 3126 | official calculator |
| IngramSpark casebound | 0.688 in | 14.568 x 10.500 | 370.03 x 266.70 | 4371 x 3150 | official formula and calculator |
| Lulu casewrap | 0.813 in | 14.563 x 10.750 | 369.90 x 273.05 | 4369 x 3225 | derived, confirm with template |

The same book needs a different file for every platform. A skill must never reuse one wrap across printers.

---

## 7. Common book trim sizes

| Name | Inches | mm | Offered by |
|---|---|---|---|
| 5 x 8 | 5 x 8 | 127 x 203.2 | KDP, IngramSpark (paperback, case laminate, cloth, jacket) |
| 5.25 x 8 | 5.25 x 8 | 133.4 x 203.2 | KDP, IngramSpark |
| 5.5 x 8.5 ("Demy 8vo" in IngramSpark's matrix) | 5.5 x 8.5 | 139.7 x 215.9 | KDP (paperback and hardcover), IngramSpark |
| 6 x 9 (US trade; KDP default) | 6 x 9 | 152.4 x 228.6 | KDP, IngramSpark, Lulu |
| 6.14 x 9.21 ("Royal 8vo") | 6.14 x 9.21 | 156 x 234 | KDP, IngramSpark |
| 7 x 10 | 7 x 10 | 177.8 x 254 | KDP, IngramSpark, Lulu |
| 8.5 x 11 (US letter) | 8.5 x 11 | 215.9 x 279.4 | KDP (paperback), IngramSpark |
| A5 | 5.83 x 8.27 | 148 x 210 | KDP (paperback), IngramSpark, Lulu |
| B-format (UK paperback) | 5.06 x 7.81 | 129 x 198 | KDP, IngramSpark |
| A-format (UK mass market) | 4.37 x 7 (IngramSpark) | 111 x 178 | IngramSpark (the traditional A-format is 110 x 178 mm) |
| C-format / 6.024 x 9.252 | 6.024 x 9.252 | 153 x 235 | IngramSpark |
| A4 | 8.27 x 11.69 | 210 x 297 | KDP (paperback), IngramSpark, Lulu |
| 8.5 x 8.5 square | 8.5 x 8.5 | 215.9 x 215.9 | KDP, IngramSpark |

Sources: KDP calculator configuration and Print Options page; IngramSpark trim size matrix (File Creation Guide p.40) and its public trim list; Lulu Book Creation Guide trim table.

---

## 8. Barcode areas

### Books

| Platform | Barcode box | Position | Rules | Source |
|---|---|---|---|---|
| KDP paperback | 2 x 1.2 in (50.8 x 30.5 mm); your own barcode at least 1.4 x 0.8 in (35.56 x 20.3 mm) | lower right of the back cover, 0.25 in (6.3 mm) from the spine fold and the bottom trim; lower left for right-to-left books | solid white background; raster barcodes at 300 ppi; if Amazon places the barcode, any art in that spot is covered or the cover is rejected | KDP Barcodes page G5HDYGP4BXLX4RUW, calculator |
| KDP hardcover | 2 x 1.2 in | lower right of the back board, at least 0.76 in (19 mm) from the bottom of the cover and 0.25 in (6 mm) from the hinge | same | KDP GDTKFJPNQCBTMRV6 |
| IngramSpark | leave 1.75 x 1 in free, or supply your own | template barcode is centred on the back cover; it may move anywhere inside the safe area but must not be resized | 100% black bars on a white box; unscannable barcodes are replaced without notice | File Creation Guide p.19, help centre |
| Lulu | yellow barcode area on the template | back cover | ISBN and barcode files come from the Copyright step | Lulu casewrap article |
| ISBN in general | EAN-13 (prefix 978 or 979) sized by the GS1 rules below | lower right quadrant of the back cover, near the spine | human-readable "ISBN ..." line above the bars; US and Canada add a 5-digit price add-on (90000 = no price) | isbn-international.org, ISBN Users' Manual 7th ed. |

### Retail products: GS1 EAN-13 and UPC-A (GS1 General Specifications, Release 26.0, January 2026)

```
X (module) nominal       = 0.330 mm   (100%)
allowed for retail POS   = 0.264 to 0.660 mm (80% to 200%)
symbol width incl. quiet = 113 X  -> 37.29 mm at 100%, 29.83 mm at 80%, 74.58 mm at 200%
minimum bar height       = 22.85 mm at 100% (18.28 mm at 80%, 34.28 mm at 150%, 45.70 mm at 200%)
quiet zones              = EAN-13 11X left, 7X right (3.63 / 2.31 mm at 100%); UPC-A 9X each side
```
- Do not truncate bar height below the table minimum. Never rescale finished barcode art; regenerate it at the new size (GS1 US).
- Dark bars (black, dark blue, dark green) on a light ground, in one ink. Red or brown bars do not scan.
- Placement: lower right quadrant of the back, 8 mm to 100 mm from the nearest edge; never over folds, seams, flaps, perforations or tight curves; never wrapped round a corner.
- Curved packs: picket-fence orientation (bars vertical) needs a container diameter of at least 48 mm at X 0.264 mm, 64 mm at X 0.350 mm, 91 mm at X 0.500 mm; otherwise turn the barcode to ladder orientation.
- The overall symbol height including the printed digits (about 25.9 mm at 100%) appears only in a GS1 drawing; not verified from text.

### Magazines

- US newsstand: UPC-A with a 2-digit issue add-on (5-digit for an issue date). At 100% the UPC-A is 1.469 in wide including quiet zones and its guard bars are 0.960 in tall; do not go below about 80% (1.175 in wide). Source: barcode-us.com (secondary).
- ISSN barcode (outside the US): EAN-13 with prefix 977, then the 7 ISSN digits without their check digit, 2 publisher digits (for example a price variant) and a check digit, optionally followed by a 2 or 5 digit issue add-on. Ask the national GS1 office or the press distributor about placement. Source: issn.org (official).
- Front-cover barcode position and the masthead "rack line" were not verified.

### QR codes

- Quiet zone: 4 modules on every side (DENSO WAVE, GS1).
- GS1 consumer use: module X at least 0.396 mm, target 0.495 mm, at most 0.990 mm. Total size including the quiet zone at the target X (computed): Version 1 (21 modules) 14.4 mm, Version 3 (29) 18.3 mm, Version 5 (37) 22.3 mm.
- DENSO module size by printer: 300 dpi gives 0.33 mm with 4 dots per module.
- The common "2 cm minimum" is not a standard's number; it roughly matches Version 3 to 5 at GS1's target X.

---

## 9. Text size versus viewing distance

### Core formulas

```
USSC / MUTCD:   cap height (in) = viewing distance (ft) / LI
metric:         cap height (mm) = viewing distance (m) x 83.33 / LI
LI (legibility index, ft per inch): 30 average (USSC; MUTCD 11th ed. guidance)
                                    25 moderate congestion, 20 heavy congestion (USSC x0.83, x0.67)
                                    10 for wall signs read at an angle, and the printers' conservative rule
All caps needs about 15% more height than upper and lower case (USSC).
Moving traffic: viewing distance (ft) = mph x reaction time (s) x 1.47; reaction time 8 to 11 s (USSC)
```

Converting cap height to a font size depends on the font. Estimate: cap height is about 0.7 of the point size for common sans serifs, so pt = cap height (mm) / (0.7 x 0.3528) = cap height (mm) x 4.05. Measure the real font's cap height before relying on it.

### Sources and values

| Rule | ft per inch | mm per m | Source (confidence) |
|---|---|---|---|
| USSC average | 30 | 2.78 | USSC Foundation, Best Practice Standards for On-Premise Signs, 2015 (widely-cited) |
| USSC measured range, upper and lower case | 24 to 38 | 3.47 to 2.19 | USSC Table 4 |
| USSC measured range, all caps | 20 to 32 | 4.17 to 2.60 | USSC Table 4 |
| USSC congested areas | 25 / 20 | 3.33 / 4.17 | USSC |
| USSC parallel (wall) signs | 10 | 8.33 | USSC Sign Legibility Rules of Thumb, 2006 |
| MUTCD 11th edition (2023), road signs | 30 | 2.78 | FHWA MUTCD 2A.08 (official) |
| MUTCD 2003 (superseded) | 40 | 2.08 | FHWA (official, historic) |
| LED message signs, normal vision / 20/40 vision | 40 to 45 / 20 | 2.08 to 1.85 / 4.17 | FHWA-HRT-15-027 (official) |
| Printer rule of thumb | 10 | 8.33 | Vistaprint sign and banner guides (practice) |
| Billboard operator | 25 to 40 | 3.33 to 2.08 | Whistler Billboards (practice) |
| UK pedestrian and transport signs | 1% of distance, 22 mm minimum | 10 | DfT Inclusive Mobility 2021 (official) |
| UK road signs (x-height, not cap height) | n/a | 100 mm x-height at 60 m | Traffic Signs Manual ch. 7 (official) |

URLs: https://usscfoundation.org/wp-content/uploads/2018/03/USSC-Guideline-Standards-for-On-Premise-Signs-2018.pdf ; https://mutcd.fhwa.dot.gov/pdfs/11th_Edition/Chapter2a.pdf ; https://www.fhwa.dot.gov/publications/research/safety/15027/004.cfm ; https://www.vistaprint.com/hub/best-fonts-for-signs ; https://www.whistlerbillboards.com/ad-design/billboard-readability-viewing-height-distance/ ; https://assets.publishing.service.gov.uk/media/61d32bb7d3bf7f1f72b5ffd2/inclusive-mobility-a-guide-to-best-practice-on-access-to-pedestrian-and-transport-infrastructure.pdf

### ADA 2010 Standards 703.5.5 (visual characters on signs, measured on uppercase "I")

| Baseline height above floor | Horizontal viewing distance | Minimum character height |
|---|---|---|
| 40 to 70 in (1015 to 1780 mm) | under 72 in (1830 mm) | 5/8 in (16 mm) |
| 40 to 70 in | 72 in and more | 5/8 in plus 1/8 in (3.2 mm) per foot beyond 72 in |
| over 70 to 120 in (1780 to 3050 mm) | under 180 in (4570 mm) | 2 in (51 mm) |
| over 70 to 120 in | 180 in and more | 2 in plus 1/8 in per foot beyond 180 in |
| over 120 in (3050 mm) | under 21 ft (6400 mm) | 3 in (75 mm) |
| over 120 in | 21 ft and more | 3 in plus 1/8 in per foot beyond 21 ft |

Also: stroke 10 to 30% of height; letter spacing 10 to 35%; line spacing 135 to 170%; non-glare finish; light on dark or dark on light; characters at least 40 in above the floor. Source: https://www.access-board.gov/ada/ (read directly; official).

### Quick table (computed from the formulas above)

| Distance | LI 30 (road, average) | LI 25 (busy street) | LI 10 (wall sign, conservative) | 1% rule (UK pedestrian) | pt at LI 30 / LI 10 (estimate) |
|---|---|---|---|---|---|
| 1 m | 2.8 mm | 3.3 mm | 8.3 mm | 22 mm (minimum) | 11 / 34 pt |
| 3 m | 8.3 mm | 10 mm | 25 mm | 30 mm | 34 / 101 pt |
| 5 m | 13.9 mm | 16.7 mm | 41.7 mm | 50 mm | 56 / 169 pt |
| 10 m | 27.8 mm | 33.3 mm | 83.3 mm | 100 mm | 112 / 337 pt |
| 30 m | 83 mm | 100 mm | 250 mm | 300 mm | 337 / 1012 pt |
| 50 m | 139 mm | 167 mm | 417 mm | 500 mm | 562 / 1687 pt |
| 100 m | 278 mm | 333 mm | 833 mm | 1000 mm | 1125 / 3374 pt |
| 150 m (about 500 ft) | 417 mm | 500 mm | 1250 mm | 1500 mm | n/a |

Copy load: USSC keeps copy to at most 40% of the sign panel (60% or more empty space). Billboards: about 7 words (Outfront). Research posters: key information readable from about 10 ft (NYU).

---

## 10. Resolution versus viewing distance

Physical floor (1 arcminute acuity, 20/20 vision):
```
ppi_floor = 3438 / viewing distance (in)  =  87.3 / viewing distance (m)
```
0.3 m: 291 ppi. 0.5 m: 175. 1 m: 87. 2 m: 44. 3 m: 29. 5 m: 17. 10 m: 9. This is the least the eye can resolve; printers ask for more.

What printers ask for:

| Viewing distance | ppi at final size | Source |
|---|---|---|
| In the hand (0.3 to 1 m) | 300; 400 or more for fine text or line art | Vistaprint (2025, 2026) |
| Indoor poster, 1 to 2 m | 240 | Vistaprint poster guide 2026 |
| Across a room, 2 to 3 m or more | 150 to 200 (scientific posters 200 to 240) | Vistaprint poster guide 2026 |
| Outdoor posters | 100 to 150 | Vistaprint poster guide 2026 |
| Booth backdrops | 150 to 200 | Vistaprint what-is-dpi 2025 |
| Banners, signs, billboards, 3 to 15 m | 35 to 100 | Vistaprint what-is-dpi 2025 |
| Large posters (floor) | 150 | Vistaprint print-resolution 2024 |
| Any size | 300 | Instantprint (including PVC and mesh banners), Printed.com, Mixam, PrintNinja |
| Book covers | 300; under 200 may be rejected | IngramSpark |
| Bangladesh flex and X-banners | 150 or more (LED Sign BD) to 300 (Ishatech, Daraz sellers) | Bangladeshi printer pages |

URLs: https://www.vistaprint.com/hub/what-is-dpi ; https://www.vistaprint.com/hub/poster-printing-preparation-guide ; https://www.vistaprint.com/hub/print-resolution ; https://www.instantprint.co.uk/printspiration/be-inspired/resolution-guide ; https://mixam.com/blog/education/dpi-for-printing

Pixel budgets at full size (computed): 18 x 24 in at 150 ppi = 2700 x 3600 px; 24 x 36 in at 200 ppi = 4800 x 7200 px; 3 x 6 ft at 100 ppi = 3600 x 7200 px; a 10 x 4 ft banner at 150 ppi = 18000 x 7200 px and at 300 ppi 36000 x 14400 px, which is why large-format shops accept less than 300.

---

## 11. Bleed and safe margins by printer

| Printer or platform | Bleed per side | Safe inside trim | Notes | Source |
|---|---|---|---|---|
| Instantprint (UK) | 3 mm | 3 mm | PVC and mesh banners: 25 mm bleed, 36 mm safe | instantprint.co.uk bleed guide and product pages |
| Solopress (UK) | 3 mm | 3 mm | fallback when there is no bleed: 6 mm white border | solopress.com bleed guide |
| Printed.com (UK) | at least 3 mm | per template | | printed.com FAQ text |
| Mixam UK | 3 mm | 5 mm; 12 mm perfect-bound edge, 15 mm wiro | hardcover covers 20 mm bleed | mixam.co.uk support |
| MOO (UK and US) | 2 mm (US pages give about 0.08 in) | 2 mm | text 8 pt or more, lines 0.5 pt or more | moo.com design guidelines |
| Vistaprint UK | 1.5 mm on A-sizes and DL; 3 mm on the 148 mm square | 1.5 mm | | Vistaprint help 360059888112 |
| Vistaprint US | about 0.06 in | about 0.06 in | posters: 0.125 in bleed, 0.25 in safe | vistaprint.com product pages, poster guide |
| Overnight Prints (US) | 1/16 in on most items; 1/8 in on 4 x 6 postcards and 4 x 6 / 6 x 9 flyers | 1/16 to 1/8 in | | overnightprints.com quick specs |
| 4over (US) | 1/16 in ("0.125 in bleed" means the total) | not stated | | 4over.com product pages |
| PrintingForLess (US) | 0.125 in | 0.125 in | tri-fold panels are not equal thirds | printingforless.com guides |
| Mixam US | 0.125 in | 0.25 in; 0.5 in perfect-bound edge, 0.6 in wire-O | hardcover 0.8 in bleed | mixam.com support |
| KDP, IngramSpark, Lulu, BookBaby | 0.125 in (3.2 mm) | 0.125 in (KDP), 0.25 in (IngramSpark), 0.5 in (Lulu) | see sections 1 to 5 | platform guides |
| Sticker Mule | 1/16 in minimum, 1/8 in when you supply full bleed | 0.1 in standard border, 1/16 in minimum | | stickermule.com |
| StickerGiant | 1/8 in | 1/16 in (1/8 in for stickers under 0.75 in) | | support.stickergiant.com |
| StickerApp | 2 mm | 2 mm | | stickerapp.com |
| PakFactory (boxes) | 0.125 in (3 mm) past every cut | 0.125 in from cuts and creases | | pakfactory.com |
| Refine Packaging | 0.25 in | 1/8 in from knives and scores | | refinepackaging.com |
| Bangladesh shops | not standardised: PVC 0.25 to 0.5 in (Ishatech), X-banner 1 in (Ishatech, a Daraz seller) | content 1 in inside the edge (LED Sign BD) | | Bangladeshi printer pages |

Default when the printer is unknown: 3 mm (metric jobs) or 0.125 in (inch jobs) bleed, 3 to 5 mm (0.125 to 0.25 in) safe, more for large format. Always rebuild the file at the chosen printer's exact size: several printers reject or rescale a file whose page size does not match their template.

---

## 12. Colour rules

Rich black and text:

| Printer | Rich black C/M/Y/K | Limits and text rule |
|---|---|---|
| IngramSpark | 60/40/40/100 | total ink 240% maximum; text 24 pt and smaller in 100% K only |
| Vistaprint | 60/40/40/100 (cool 60/0/0/100, warm 0/60/30/100, designer 70/50/30/100) | 100% K for text and fine lines |
| Blurb | 60/50/50/100 | reversed type on rich black at least 6 pt sans, 8 pt serif, 10 pt script |
| Mixam | 30/30/30/100 | registration black (100/100/100/100) forbidden |
| PakFactory (digital corrugated) | 30/30/30/100 | black text and barcodes 100% K |

Total ink (TAC) by ICC profile (ICC profile registry, https://registry.color.org/profile-registry/): PSO Coated v3 / FOGRA51 300%; PSO Uncoated v3 / FOGRA52 300%; GRACoL2013 CRPC6 320%; SWOP2006 Coated3 and Coated5 300%; GRACoL2013 uncoated CRPC3 280%; Japan Color 2011 Coated 350%; newsprint (SNAP 2007, ISOnewspaper26v4) 240%.

CMYK or RGB:
- CMYK PDF: offset and most digital presses. Instantprint converts everything to CMYK; Mixam wants CMYK with GRACoL2006 and PDF/X-4; IngramSpark wants CMYK with PDF/X-1a:2001 or X-3:2002 and no embedded profiles; KDP strips profiles and wants no spot colours.
- sRGB: print-on-demand merch (Printful sRGB IEC61966-2.1, Printify RGB, Merch by Amazon sRGB PNG, TeePublic RGB PNG); e-book covers (RGB only; Kindle does not support CMYK); Blurb accepts sRGB.
- Headless Chrome writes RGB PDFs with no spot colours, overprint or layers. For offset work add a conversion step (for example Ghostscript or a PDF library) that converts to the printer's CMYK profile, forces text to 100% K and caps TAC; send cut lines and white-ink layers as separate vector files.

---

## 13. Labels on round containers

```
label_width  = pi x container diameter - gap          (gap about 10 mm or 1/8 in, so nothing prints over itself)
sleeve_width = pi x diameter + 1/8 to 1/4 in overlap   (plain full-bleed sleeves only)
label_height = straight wall height - 3 mm top - 3 mm bottom
US principal display panel (cylinder) = 40% of (height x circumference)   [21 CFR 101.1]
```
Sources: Paperlust and Print and Package (practice), FDA 21 CFR 101.1 (official).

US net quantity minimum type height by PDP area (21 CFR 101.7): up to 5 sq in 1/16 in; over 5 to 25 sq in 1/8 in; over 25 to 100 sq in 3/16 in; over 100 to 400 sq in 1/4 in; over 400 sq in 1/2 in; placed in the bottom 30% of the PDP. Every other required item at least 1/16 in (101.2). Nutrition Facts: nutrient lines 8 pt, "Calories" 16 pt bold, calorie number 22 pt bold, servings 10 pt, hairline box (101.9). Note: 21 CFR 101.105 no longer exists in the current eCFR; the rules are in 101.7.

Bangladesh (BSTI Packaging of Commodities Rules 2021, amended 2025; https://bsti.gov.bd/pages/static-pages/6922df32933eb65569e2084c): all declarations in Bangla (other languages allowed beside, less prominent); any declaration at least 1 mm tall (2 mm if moulded or embossed); net quantity heights by weight or volume: up to 50 g 2 mm, over 50 to 200 g 3 mm, over 200 g to 1 kg 4 mm, over 1 to 5 kg 6 mm, over 5 kg 8 mm; clear space of one numeral above and below and two numerals left and right; MRP, maker's address, manufacture and expiry dates required.

Worked example (computed): a 3 in diameter jar with a 3 in label: circumference 9.42 in; wrap label about 9.3 in wide (minus a 1/8 in gap); US PDP = 0.4 x 3 x 9.42 = 11.3 sq in, so the net quantity must be at least 1/8 in tall.

---

## 14. Merchandise pixel sizes

```
file_px = print area (in) x dpi
```
| Product | Print area | File | Source |
|---|---|---|---|
| T-shirt, Merch by Amazon | 15 x 18 in | 4500 x 5400 px, 300 dpi, PNG, sRGB, under 25 MB | merch.amazon.com (official) |
| T-shirt, Printful large front (L and up) | 15 x 18 in | 2250 x 2700 px at 150 dpi minimum, 4500 x 5400 at 300 | Printful (official) |
| T-shirt back, Printful | 12 x 16 in | 1800 x 2400 at 150, 3600 x 4800 at 300 | Printful (official) |
| T-shirt, TeePublic | template 15 x 17 in at 150 dpi | at least 5000 x 5500 px to enable all products | TeePublic (official) |
| T-shirt, Redbubble | not published | minimum 2875 x 3900 px (premium tee) | Redbubble (official) |
| Hoodie front, Merch by Amazon | 15 x 13.5 in | 4500 x 4050 px | merch.amazon.com (official) |
| Mug 11 oz | 9 x 3.5 in | 2700 x 1050 px | Merch by Amazon, Printful (official) |
| Mug 15 oz, Printful | 9 x 3.8 in | 2700 x 1140 px (derived) | Printful (official) |
| Tote, Merch by Amazon | 16 x 16 in bag | 2925 x 2925 px | merch.amazon.com (official) |
| Phone case, Merch by Amazon | all models | 1800 x 3200 px | merch.amazon.com (official) |
| PopSockets | 1.56 in button | 485 x 485 px | merch.amazon.com (official) |
| Cap embroidery, Printful dad hat | 5.5 x 2 in | 825 x 300 at 150, 1650 x 600 at 300 | Printful (official) |

Embroidery limits (Printful and Printify): up to 6 of 15 thread colours, text at least 0.25 in tall, lines at least 0.05 in, no gradients.

---

## 15. Folds and panels

- Half fold (greeting cards, bifold brochures): flat width = 2 x panel width, fold at the centre. A6 card = A5 sheet, A5 card = A4 sheet, 5 x 7 in card = 10 x 7 in sheet.
- Tri-fold (roll or C-fold, 6 panels): printers disagree on panel widths. PrintingForLess says the panels are not equal thirds (the tuck-in panel is narrower so it folds inside). Instantprint asks for equal panels and adjusts them itself before printing. The exact offsets were not verified, so use the chosen printer's template and never assume equal thirds for a printer that asks for unequal panels.
- Keep text and key art at least the safe margin away from every fold as well as the trim (Instantprint folding guide: avoid text on or near a crease).
- Mini zine (8 pages from one sheet): panels are 1/4 of the width by 1/2 of the height (Letter: 2.75 x 4.25 in; A4: 74.25 x 105 mm); one cut along the horizontal centre across the two middle panels; top-row panels print upside down.
- Saddle-stitched booklets: page count in multiples of 4; a separate cover adds 4 pages; creep grows with page count (Mixam, PrintingForLess).
- Table tents and packaging: get the flat die-line from the printer; the flat geometry is not published.

---

## 16. Large format and billboard scale files

```
file_size   = full_size x scale
file_px     = file_size (in) x file_ppi
effective   = file_ppi x scale           (ppi on the finished print)
bleed_file  = bleed_full x scale         (unless the owner states bleed at file scale)
```

| Format | Full size | Scale and file | ppi at file scale | Effective ppi | Bleed | Source |
|---|---|---|---|---|---|---|
| UK 48-sheet (Bauer) | 6096 x 3048 mm | 10%: 609.6 x 304.8 mm | 300 min, 450 best | 30 to 45 | 1 mm on the 10% file | Bauer 48-sheet spec |
| UK 48-sheet (Global) | 6096 x 3048 mm, display 5946 x 2948 | tenth size | 300 min | 30 | 5 mm (scale not stated) | Global 48-sheet PDF (2020) |
| UK 48-sheet (75Media) | 6096 x 3048 mm | 25%: 1524 x 762 mm | 300 min, 450 recommended | 75 to 112 | none | 75Media guide (2023) |
| UK 96-sheet (Bauer) | 12192 x 3048 mm | 10%: 1219.2 x 304.8 mm | 300 to 450 | 30 to 45 | 1 mm | Bauer 96-sheet spec |
| UK 6-sheet Adshel (Bauer) | 1200 x 1800 mm | 25%: 300 x 450 mm | 300 to 450 | 75 to 112 | 2 mm | Bauer Adshel spec |
| UK 4-sheet (Bauer) | 1016 x 1524 mm | 50%: 508 x 762 mm | 300 to 450 | 150 to 225 | 2 mm | Bauer station 4-sheet spec |
| US bulletin (Lamar) | 14 x 48 ft | 1/2 in = 1 ft: 7 x 24 in | 300 | 12.5 | 6 in full size = 0.25 in at scale | Lamar bulletin sheet (3/2017) |
| US bulletin (Clear Channel) | 14 x 48 ft (vinyl 15 x 49 ft) | 1/4 in = 1 ft: 3.5 x 12 in | 600 | 12.5 | 2.5 in bleed plus 3.5 in pockets | CCO sheet (2013) |
| US 30-sheet poster (Lamar) | 10'5" x 22'8" live | 1 in = 1 ft | 216 | 18 | 3/4 in full size | Lamar poster sheet (3/2017) |
| US 30-sheet poster (Clear Channel) | 10'5" x 22'8" | 1/2 in = 1 ft | 600 | 25 | critical area 6 in inside | CCO sheet (2013) |
| US king bus | 30 x 144 in | 1/8 scale: 3.75 x 18 in | 300 | 37.5 | copy area 27 x 141 in | OAAA (archived 2016) |
| US bus tail | 21 x 72 in | 1/4 scale: 5.25 x 18 in | 300 | 75 | copy area 17 x 69 in | OAAA (archived 2016) |
| UK bus Superside (Global) | 6116 x 658 mm | 10%: 611.6 x 65.8 mm | 300 | 30 | 3 mm | Global Supersides PDF (2025) |
| Vinyl banners (Lamar) | any | 1:1 | 72 (36 over 50 sq ft) | 72 / 36 | per printer | Lamar temp-print page |

Worked example (computed): Bauer 48-sheet at 300 ppi on the 10% file = 609.6 / 25.4 x 300 = 7200 px by 3600 px; with the 1 mm bleed on each side, 7224 x 3624 px. US bulletin at Lamar scale = 24 x 300 = 7200 by 7 x 300 = 2100 px; with the 0.25 in scaled bleed, 7350 x 2250 px.

Why scale: a 14 x 48 ft board at 150 ppi would be 86400 x 25200 px, and PDF pages above 200 in per side need special handling (Acrobat's page-size limit, not re-verified here), so media owners ask for scaled files.

---

## 17. Digital signage and LED walls

```
LED canvas px   = (cabinets across x px per cabinet width) by (cabinets down x px per cabinet height)
px per cabinet  = cabinet size (mm) / pixel pitch (mm), rounded by the maker (read the spec sheet)
viewing distance (ft) ~ pitch (mm) x 10            (Planar rule of thumb)
acuity distance (mm)  = pitch (mm) x 3438          (Planar; same constant as ppi = 3438 / d_in)
roadside pitch        ~ 1 mm per mph of traffic    (Daktronics; 0.5 mm per mph for better clarity)
title safe (TV)       = 90% of width and height    (SMPTE ST 2046-1; action safe 93%)
EBU R 95              = action safe 3.5%, graphics safe 5% in from each edge
```

| Cabinet (ROE Visual) | Pitch | px per cabinet |
|---|---|---|
| Meru 500 x 500 mm | 1.56 mm | 320 x 320 |
| Meru 500 x 500 mm | 1.9 mm | 256 x 256 |
| Meru 500 x 500 mm | 2.6 mm | 192 x 192 |
| Meru 500 x 500 mm | 3.9 mm | 128 x 128 |
| Black Pearl BP2V2 500 x 500 mm | 2.84 mm | 176 x 176 |
| Carbon CB5 600 x 1200 mm | 5.77 mm | 104 x 208 |

Worked examples (computed): 16 x 9 cabinets of 500 mm at 2.6 mm = 8 x 4.5 m, 3072 x 1728 px (16:9), viewing from about 26 ft (8 m); 32 x 9 cabinets = 16 x 4.5 m, 6144 x 1728 px (32:9). Title safe on 1920 x 1080 = 1728 x 972 px; on portrait 1080 x 1920 = 972 x 1728 px; on 3840 x 2160 = 3456 x 1944 px.

Daktronics LED message signs: 4 in letters read at 150 ft, 12 in at 525 ft (about 37 to 44 ft per inch); 4 to 6 in text for traffic at 45 mph or less, 8 in or more up to 60 mph; viewers get 3 to 4 seconds.
