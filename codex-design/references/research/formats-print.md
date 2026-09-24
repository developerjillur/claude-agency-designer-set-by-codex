# Print, publishing, merch and signage playbook

Verified 2026-09-24. Companion files: `print.json` (the new presets) and `print-formulas.md` (spine, wrap, barcode, legibility and resolution maths). Global by default; Bangladesh notes are at the end.

## How to read print.json

- `w`, `h`: the finished (trim) size, landscape or portrait as the product is used. Pure raster targets (e-book covers, merch files, screens) are in px.
- `bleed`: per side, beyond trim. "0" means none. The PDF page is `w + 2 x bleed` by `h + 2 x bleed`.
- `safe_mm`: [top, right, bottom, left] in mm, measured inward from the trim. `null` means the source states none; then use the family default below.
- `ppi`: resolution at final size for raster content. `null` for pixel-defined targets.
- `folds_mm`: fold positions in mm from the left edge of the flat sheet (vertical folds). When `notes` contains `fold_axis=y`, the extra fold named there is horizontal and measured from the top.
- `min_text_pt`: set only where a source gives a floor.
- `confidence`: official (the platform's or printer's own page, calculator or standard), widely-cited (several independent sources agree), practice (printer convention seen at two or more shops, or one shop's own page used as a market example), estimate (a derived or chosen value; the notes say what was chosen).
- Bleed is printer-specific (see print-formulas.md section 11). Each preset uses the bleed of the printers it cites. When the printer is known, rebuild the page at that printer's exact size.
- Family defaults when a field is null: small print 3 mm (or 0.125 in) safe; large format at least 1 in (25 mm) safe (LED Sign BD 1 in; Signs.com and Banners.com 2 in); documents 12.7 to 25.4 mm margins (0.5 to 1 in, UC Berkeley; 2.5 cm, Prospects).

## Output rules that apply to every print preset

1. Render the PDF at the full bleed size in physical units (`@page { size: <w+2b> <h+2b>; margin: 0 }`), with the design's background running to the page edge and all type and logos inside the safe box.
2. Raster fallback: px = ceil(inches x ppi) for the full bleed size, then place it in a PDF at the exact physical size.
3. No crop marks unless the printer asks (Mixam and IngramSpark ask for none; IngramSpark wants its own template page).
4. Chrome PDFs are RGB with no spot colours, layers or overprint. Offset printers want CMYK: convert with the printer's profile, force small text to 100% K, cap total ink (IngramSpark 240%, FOGRA51/52 300%, GRACoL2013 320%). Merch and e-book targets stay sRGB.
5. Cut lines, dielines and white-ink layers cannot live in a Chrome PDF. Deliver them as a separate vector file or let the printer draw them.
6. Fonts: embed or outline. For Bangla, a PDF with embedded Unicode fonts avoids the Bijoy (SutonnyMJ, ASCII) versus Unicode mix-ups that still happen in Bangladeshi presses.

---

## 1. E-book covers

Anatomy: front cover only, no spine, back cover, barcode or flap (KDP checklist). Title and author must appear and match the store metadata (KDP, D2D, BookBaby, Kobo).

Sizes: one 1600 x 2560 px sRGB JPEG under 2 MB passes every verified store (KDP ideal; Apple needs 1400 px on the short side; Google Play 640 to 7200 px; B&N Press 1400 px and 2 MB; Kobo 5 MB, portrait, 3:4 preferred; D2D any tall rectangle, 1600 x 2400 suggested). BookBaby recommends a 1.5 ratio (1400 x 2100). Rokomari publishes no spec; Boitoi accepts JPG or PNG.

Copy budget (practice): title, author, and at most a short series line or one-line hook. No price, "free", other store names or 3D mockups: Apple rejects price wording, competitor promotion, upsells, "CD/Audiobook" claims, unnecessary borders and photos of the physical book.

Where text goes: title large in the top half or across the middle; author name in a clear band; nothing essential at the very edges, because store thumbnails are recompressed and some layouts crop.

Thumbnail test (required): Amazon desktop search loads covers 218 px tall at 1x (observed 2026-09-24) and recommendation strips are about 135 to 160 px tall (Derek Haines, Creative Paramita, secondary). Shrink the cover to 218 px and 150 px tall: the title must still read. At 218 px tall a 2560 px master is scaled to about 8.5%, so 200 px cap height becomes about 17 px (computed).

Common mistakes: thin serif titles, low-contrast type over busy photos, stretched small images, white covers without a border on KDP (KDP suggests a 3 to 4 px mid-grey border; Apple forbids unnecessary borders, so add it only on the KDP export).

## 2. Print book covers (full wraps)

Anatomy (left to right, left-to-right languages): bleed, back cover (blurb, author bio, barcode lower right), spine (title, author, imprint logo), front cover, bleed. Right-to-left books (Arabic, Urdu, Hebrew) mirror this: the barcode moves to the lower left (KDP).

The wrap width depends on page count and paper, so it is never a fixed preset: compute it with print-formulas.md sections 1 to 6. The front-panel presets (`book-6x9` and others) are for designing the front; the e-book cover is the same art exported RGB.

Rules that printers enforce:
- Spine text only from 79 pages at KDP (80 in Cover Creator), 48 at IngramSpark, and more than 80 at Lulu. Keep 0.0625 in (KDP, IngramSpark) or 0.125 in (Lulu) clear on each side of spine text.
- Do not stop a colour or a picture exactly at the spine fold: spines drift up to 1/16 in (KDP, IngramSpark), so wrap colour round the spine or leave a soft transition.
- No borders near the trim (KDP: at least 0.25 in inside if used; IngramSpark: an extra 0.125 in inside the safety box).
- Barcode box (KDP 2 x 1.2 in lower right; IngramSpark 1.75 x 1 in) stays empty or white.
- Hardcover (case laminate): art must extend over the wrap (KDP 0.591 in, IngramSpark 0.625 in, Lulu 0.75 in) and keep text off the hinge (KDP 0.394 in, IngramSpark 0.5 in, Lulu about 0.25 in).
- KDP rejects covers with spine text below 79 pages, text outside the safe area, remaining template guides, crop marks, or art in the barcode spot.

Copy budget for the back cover (practice): a headline or pull quote, a short blurb, a few short endorsements, an optional author photo and bio, the ISBN barcode, and a price or category line if wanted.

## 3. Magazine covers

Anatomy: masthead at the top, main image, a handful of cover lines, issue date and price, barcode. Newsstand racks overlap covers, so the masthead and the main line live in the top band (practice; no source with a measured band was found).

Sizes: US standard 8.375 x 10.875 in (Mixam lists 8.38 x 10.88), US Letter, 8 x 10 in, MagCloud 8.25 x 10.75 in, digest 5.5 x 8.5 in, UK and EU A4. Bleed 0.125 in (3 mm), quiet area 0.25 in (5 mm). Perfect-bound covers are one spread with a spine; saddle-stitched covers are single pages.

Barcodes: US: UPC-A plus 2-digit issue add-on, 1.469 in wide at 100% including quiet zones, not below about 80%. Elsewhere: ISSN EAN-13 with prefix 977 plus a 2 or 5 digit issue add-on. Placement on the cover was not verified: follow the distributor.

## 4. Report, whitepaper, proposal and annual report covers

Anatomy: title, subtitle, organisation name and logo, date or reporting period, optional hero image. Keep the title in the upper half and the logo either top or bottom, never both competing (practice).

Sizes: A4 wherever ISO paper sizes are standard (most of the world, including Bangladesh), US Letter in the US and Canada. SEC paper filings must be no larger than 8.5 x 11 in. Designed annual reports also use 210 x 280 mm, 8.25 x 10.75 in or 7 x 10 in. Bleed only when art touches the edge; screen PDFs need none. Bound edge: 12 mm perfect binding, 15 mm wiro (Mixam UK); 0.5 in or 0.6 in in the US.

## 5. Certificates

Anatomy: organisation logo and name, certificate title ("Certificate of ..."), recipient name (the biggest line after the title), reason, date, one or two signature blocks with printed names and titles, optional seal or QR code for verification.

Rules: landscape A4 (297 x 210 mm) or Letter (11 x 8.5 in). Decorative frames look uneven when trimming drifts, so keep frames well inside the safe area or use no bleed and print on A4 certificate stock. Leave a clean, uncoated line if names are handwritten. In Bangladesh certificate paper is usually 150 to 160 gsm A4, or 250 to 300 gsm metallic card (Daraz listings).

## 6. Invitations and greeting cards

Anatomy of an invitation: host line, headline (names or event), date and time, venue, RSVP, dress code or notes. For a Bangladeshi wedding card add the Bangla and English versions, both families' names, and separate cards or panels for the gaye holud, aqd and reception (bou-bhat or walima) (practice, not sourced).

Sizes: 5 x 7 in (A7 envelope), A5 and A6 (C5 and C6 envelopes), DL (DL envelope), squares 120 to 148 mm (square mail costs more in the US). Folded cards are designed on the flat sheet: A6 card = A5 sheet, A5 card = A4 sheet, 5 x 7 card = 10 x 7 sheet.

Rules: keep text away from the fold as well as the trim; inside can be left blank; state long-edge or short-edge fold. Text 8 pt or more and lines 0.5 pt or more (MOO). Common mistake: designing the front panel only and forgetting the back panel on the same side of the sheet.

## 7. Postcards and direct mail

Anatomy: front (image, headline, offer), back split into a message half (left) and an address half (right).

US postal rules (USPS DMM 101 and 202): card price only from 3.5 x 5 in to 4.25 x 6 in; larger pieces pay letter price up to 6.125 x 11.5 in; length/height outside 1.3 to 2.5 is non-machinable. Keep the bottom-right 4.75 x 0.625 in barcode clear zone empty, the address in the OCR read area, address type 8 pt or more (sans serif, capitals preferred), return address top left, postage top right. No full UV gloss on the address side (Overnight Prints). Rounded corners up to 0.125 in radius are allowed.

UK: Royal Mail letter size is at least 90 x 140 mm and at most 240 x 165 mm and 5 mm thick; address bottom left area, left aligned, stamp top right.

## 8. Letterhead, compliments slips and envelopes

Letterhead anatomy: logo and company name in the header; address, phone, email, web, registration numbers in the footer or header; leave the address window area and the body clear. DIN 5008 places the address field 32 mm (Form A) or 50 mm (Form B) from the top and the text 25 mm from the left (secondary source); a DL window sits about 18 mm from the left and 48 mm from the top (Vistaprint UK). Avoid heavy full-bleed colour on sheets that will go through office printers; textured stocks may jam.

Compliments slip: 210 x 99 mm, logo and "With compliments", contact line, space to write.

Envelopes: no bleed on standard printed envelopes; text and logos at least 0.25 in from the edges and 1/8 in clear around windows; logo and return address top left; heavy coverage needs offset. Pairing: C6 for A6, C5 for A5 or A4 folded once, C4 for flat A4, DL for A4 folded in thirds, A7 for 5 x 7 in, A2 for 4.25 x 5.5 in.

## 9. Notepads

One design repeats on every sheet; glued at the top on grey board. Put the logo and header in a top band and keep them clear of the glue strip (its depth is not published); light tints only in the writing area. Wire-bound pads need 10 mm clear on the bound edge (Solopress).

## 10. ID cards, badges and lanyards

ID card (CR80, 85.6 x 53.98 mm): photo, name (largest), role, organisation logo, ID number, expiry, barcode or QR, emergency contact on the back. The slot punch (0.125 x 0.5 in) is centred on the top edge and punched after printing: keep art clear of it. Direct-to-card printers print edge to edge at the exact card size; online printers give their own template.

Conference badges: first name very large (read at 1 to 2 m, so at least about 22 mm cap height by the UK 1% rule and its 22 mm minimum; see print-formulas.md section 9), last name and company smaller, event branding at the top, colour band for attendee type. Print both sides of hanging badges because they flip. Avery 3 x 4 in inserts have no bleed.

Lanyards: 10 to 25 mm wide; a repeating logo or name along the strap; exact print length from the supplier.

## 11. Tickets, vouchers and loyalty cards

Tickets: event name, date, time, venue, seat or tier, price, terms, serial number, stub. Stub sits 1.5 to 2 in from one end (4over) or on the last third (Instantprint). Numbering area at least 24 x 6 mm and 5 mm from the edge (Solopress), black 12 to 14 pt; knock out dark backgrounds behind numbers.

Vouchers: business name and logo, value, recipient line, expiry, terms, serial number (Vistaprint).

Loyalty cards: business-card size, uncoated so stamps and pens work; a grid of stamp circles; folded versions give more room.

## 12. Bookmarks, table tents, hang tags and door hangers

Bookmarks: long narrow panels (2 x 6 in, 52 x 148 mm): front holds the name, logo and one key message; back holds details. Keep type 3 mm or more from the long edges.

Table tents and talkers: every face must work alone and upright; ship flat, so design on the printer's die-line; the base flap is hidden.

Hang tags and swing tags: hole 3 to 6 mm, centred about 4 mm (0.15 in) from the top; keep text clear of the hole as well as the edges. A 2 x 3.5 in tag fits a logo, product name and one or two lines; the back carries price, size, care or barcode.

Door hangers: the hook hole is about 30 mm with a slit; the die cuts through art, so use the printer's template; headline under the hole, offer in the middle, contact and call to action at the bottom; tear-off coupons 2 in deep.

## 13. Stickers and labels

Anatomy: a bleed box 1/8 in outside the cut, the cut line, and a safe box 1/16 to 1/8 in inside it. Text 6 pt or more, lines 1 pt or more, fonts outlined.

Cut lines: closed vector path, 100% magenta stroke 0.5 to 1 pt, on its own layer; name the spot for the cutter (CutContour for Roland and Mimaki, PerfCutContour for perforation, Thru-cut and Kiss-cut for Summa, "die cut" at StickerApp). Raster cut lines are never read. Online printers (Sticker Mule, StickerGiant) will draw the cut line if you do not.

Clear stickers need a white ink layer; no semi-transparency or gradients to clear.

Product labels: size wrap labels with pi x diameter minus a gap; keep the height inside the straight wall. Legal copy: US net quantity in the bottom 30% of the front panel with the heights in print-formulas.md section 13; Nutrition Facts 8 pt lines; Bangladesh BSTI: everything in Bangla, net quantity heights by pack size, MRP, maker, dates. Barcode lower right of the back, never over the seam.

What printers reject or reprint: missing bleed, rasterised or wrongly named cut lines, fonts not outlined, low-resolution art (StickerGiant prints it but gives no refund), spot colours on digital presses.

## 14. Packaging dielines

What to get from the printer before designing: the exact dieline for the size and style (reverse tuck end, straight tuck end, tuck top auto bottom, roll end tuck front mailer), the board or flute (B flute is 2.4 to 3 mm and changes panel sizes), whether sizes are inside dimensions (Uline and FEFCO use internal L x W x H, measured from crease centres), inside versus outside printing (each needs its own dieline file), and the tolerance (Refine: plus or minus 1/8 in).

Dieline conventions: cut lines solid black, creases solid red, perforations dashed, bleed green (PakFactory); dieline inks in spot colours named "cut" and "crease" so they do not print; never resize, rotate or flatten the dieline; art on a separate layer. Bleed 0.125 in (PakFactory) to 0.25 in (Refine) past every cut including glue tabs; keep art 1/8 in (3 mm) to 5 mm from cuts and folds. Text 8 pt or more (10 pt reversed or on digital corrugated). Common mistake: designing the flat box as one canvas, so neighbouring panels end up at 90 degrees or upside down when folded.

## 15. Merch and print on demand

T-shirts: 4500 x 5400 px (15 x 18 in at 300 dpi) is the Merch by Amazon file and Printful's large front; Printful's standard back is 12 x 16 in; TeePublic wants 5000 x 5500 px at 150 ppi to enable every product; Redbubble counts pixels only.

Placement: top of the design about 1.5 to 3 in below the collar (front) and 3 in or more (back); left-chest logos 3 to 4 in wide; big front graphics usually 10 to 12 in wide even on a 15 in canvas.

Copy budget: one short phrase reads best; type at least about 32 pt at 300 dpi on light tees and 48 pt on hoodies (Merch by Amazon); embroidery letters at least 0.25 in tall.

Rules: transparent sRGB PNG; no semi-transparent glows (TeePublic's 40% opacity rule); dark on dark vanishes; no neon claims; no watermarks, contact details, or trademarked words (Merch by Amazon rejects them). Mugs: 9 x 3.5 in on 11 oz, keep key elements off the seam and away from the handle gap. Full-bleed products (phone cases, totes, pillows, PopSockets) need a background edge to edge; transparent areas print white.

## 16. Yard signs, A-boards, banners, roll-ups and X-banners

Yard signs (18 x 24 in class): corrugated 4 mm board, H-stake into vertical flutes along the bottom edge, one file per side (flip arrows on the back). Dark backgrounds hide show-through from the hollow board (Vistaprint). Copy: a short headline plus a phone number or URL, read from a moving car, so stay well under Clear Channel's 7-word billboard ceiling. Bleed 1/8 in (US Press, Yard Sign Ninjas) or 1/4 in (Signs.com); text at least 1/4 in in, Signs.com says 2 in. No-bleed orders get a 3/4 in white border (Yard Sign Ninjas).

A-frames and A-boards: US inserts 24 x 36 in and 22 x 28 in; UK posters A1 and A2 in snap frames (A0 boards exist). Frame lips can hide part of the edge (snap-frame profiles are 25 mm wide); keep text 25 mm in unless the maker's template says less (Instantprint's own frames: 3 mm). Headline readable across the pavement: about 42 mm cap height at 5 m (LI 10, computed).

Vinyl and PVC banners: hems 1 in (US) or 50 mm (UK), grommets or eyelets every 2 to 3 ft (Signs.com), 2 to 4 ft (Banners.com) or about 500 mm (Instantprint); pole pockets 2 to 4 in eat into the finished size; keep text 2 in from edges and 3 in from pockets. Build at full size in physical units when the page stays under 200 in on each side (Acrobat's long-standing page limit; not re-verified in this pass), otherwise build a scaled file as billboards do; raster at 100 to 150 ppi (Lamar accepts 72 ppi at size, 36 ppi over 50 sq ft). Common mistakes: text in the hem or grommet line, white hairline gaps from missing bleed, tiny type on a banner read from 10 m (use the section 9 table).

Roll-ups: brand and headline in the top third, details in the lower third where people stand close, nothing essential in the hidden top 1 in and bottom 3 in on US stands (SNJ); UK printers such as Route1Print add the cassette allowance themselves. Standard widths 800, 850, 1000, 1200 and 1500 mm by 2000 mm (UK), 33 x 81 in and 24 / 47 x 81 in (US). People glance for about 3 seconds (Instantprint).

X-banners: 60 x 160 cm (Bangladesh: "2 x 5 ft", 24 x 60 or 24 x 63 in) and 80 x 180 cm; corner eyelets; Helloprint uses 3 mm bleed and 4 mm safe, Bangladeshi shops ask 1 in bleed and 1 in content inset. Keep text away from the four corner rings.

What printers reject: RGB or spot colours on flex (converted, colour shifts), fonts not outlined, files at the wrong scale, art in hems, missing bleed, very low resolution photos.

## 17. Billboards and transit

Anatomy: one image, one message, logo. Copy: 7 words or fewer in the headline and about 10 on the whole board, at most 3 visual elements, about 5 seconds of viewing (Clear Channel); Global asks for 5 to 7 words on roadside digital and D6 screens. Bold sans serif; a thin dark stroke round light text; no white backgrounds on digital (wash out); no red with green of similar value (Clear Channel). UK paper 48-sheets: avoid all-black backgrounds (heavy ink curls the paper) and thin fonts (75Media).

Files are built at a scale, never at full size:
- UK 48-sheet (6096 x 3048 mm): Bauer 10% (609.6 x 304.8 mm) with 1 mm bleed, 300 to 450 ppi, safe area 569.6 x 274.8 mm anchored top left; Global tenth size with 5 mm bleed and a 5946 x 2948 mm display area; 75Media 25% with no bleed. The owner decides, so keep scale and bleed per owner.
- UK 96-sheet (12192 x 3048 mm): 10%, 1 mm (Bauer) or 3 mm (Global) bleed.
- UK 6-sheet (1200 x 1800 mm Adshel; Global roadside 1185 x 1750 mm): 25% scale, 2 to 3 mm bleed. 4-sheet (1016 x 1524 mm): 50% (Bauer) or 25% (Global).
- US bulletin 14 x 48 ft: 1/2 in = 1 ft at 300 ppi (Lamar, OAAA layout 7 x 24 in) or 1/4 in = 1 ft at 600 dpi (Clear Channel), both 7200 x 2100 px live, 6 in bleed at full size; vinyl 15 x 49 ft.
- US 30-sheet poster: live 10'5" x 22'8"; Lamar 1 in = 1 ft at 216 ppi with 3/4 in bleed; Clear Channel critical area 9'5" x 21'8". Junior 8-sheet 5 x 11 ft.
- US digital: master 1400 x 400 px for bulletins and 840 x 400 px for posters (Lamar, Clear Channel), RGB, black 0/0/0. UK digital 48-sheets vary by owner (864 x 432, 612 x 306, 576 x 288 and more); D6 screens are 1080 x 1920 portrait (Global rail D6 wants the file rotated minus 90 degrees). Minimum text on Bauer's digital 48-sheet: 8 px, 12 px recommended.
- Bus: US king 30 x 144 in and queen 30 x 88 in at 1/8 scale, tail 21 x 72 in at 1/4 scale, 300 dpi, copy area 1.5 to 2 in inside the trim (OAAA, archived); UK Superside (6116 x 658 mm, 10%), Streetliners (fifth size, must work at 508 and 477 mm depths), Super Rear 60 x 20 in and Standard Rear 48 x 18 in (quarter size), 3 mm bleed (Global).

Bangladesh: no published city billboard spec; shops quote 20 x 10, 30 x 15, 40 x 20, 60 x 20 ft and 48 x 14 ft unipoles, flex on steel; Dhaka South moved to LED screens. Election billboards are capped at 16 x 9 ft and must be black and white.

## 18. Trade shows and events

Step-and-repeat (8 x 8 ft and up): logos 8 to 10 in wide on 8 x 8 ft (10 to 12 in on 10 x 10 ft), one logo width apart, alternate rows in a checkerboard, clear of the 3 in pole pockets (Signs.com). Pop-up and tension fabric walls: the "10 ft" straight wall graphic is 118.5 x 89.5 in (about 7.5 ft tall), 2 in bleed and 2 in safe on fabric, 100 to 120 ppi raster, vector art CMYK and raster art RGB for dye sublimation (Orbus); keep type off panel breaks on hardware pop-ups. Table throws: 6 ft throw 126.5 x 84 in flat, 8 ft 150.5 x 84 in, tables 30 in tall (Signs.com, Orbus); the logo goes high on the front drop. Feather and teardrop flags come in 7.5, 10, 13 and 15.5 ft (Vistaprint, BuildASign); single-sided flags show a mirror image on the back; flat print files were not verified, so use the maker's template (Orbus flag bleed: 2 in left and right, 4 in top and bottom).

Window graphics: 70/30 perforated film is the retail standard, 50/50 is most see-through but washes out; no fine type on 50/50, raise contrast 10 to 20% (Contra Vision, Clear Focus). Clings and stickers inside the glass can face in or out (Instantprint). Floor decals: textured slip-resistant laminate, indoor, about 6 months (Vistaprint); read at an angle, keep them to an arrow and a very short message.

## 19. Digital signage and LED walls

Screens: 1920 x 1080 and 3840 x 2160, landscape or portrait; design at native size (bigger adds nothing, OptiSigns). No signage safe-area standard was found; TV safe areas are the practical guide: 93% action safe and 90% title safe (SMPTE ST 2046-1), or 3.5% and 5% in from each edge (EBU R 95). Menu boards are side-by-side screens: three landscape HD screens make a 5760 x 1080 canvas and three portrait a 3240 x 1920 canvas (computed, bezels excluded); keep text off the bezel lines.

LED walls: canvas px = cabinets across x px per cabinet, by cabinets down x px per cabinet. ROE 500 mm cabinets give 192 px at 2.6 mm, 256 px at 1.9 mm, 128 px at 3.9 mm, 176 px at 2.84 mm; 16 x 9 cabinets at 2.6 mm is an 8 x 4.5 m wall at 3072 x 1728 px. Viewing distance: pitch (mm) x 10 = feet (Planar), and roadside screens need about 1 mm of pitch per mph of traffic (Daktronics). LED message signs: 4 in letters read at 150 ft, 12 in at 525 ft; 4 to 6 in text for traffic at 45 mph or less (Daktronics). Stage backdrops follow the same maths; ask the rental company for the processor canvas.

## 20. Calendars

Anatomy: a picture area and a month grid per page, or a single-sheet year planner. Top binding (wiro 15 mm clear) with a hanger hole centred at the top; US drilled calendars have a hole about 5 mm across, 0.25 in from the trim. Dates at or above MOO's general 8 pt text minimum, weekend and holiday colours consistent, week starts stated. Bangladesh: Bangla, English and often Hijri dates together; demy (18 x 23 in) and crown (15 x 20 in) sheets for wall calendars; desk calendars 5 x 8.5 in (Diamu).

## 21. CVs, decks, academic posters and zines

CV: A4 (UK, EU, Asia, Bangladesh) or Letter (US, Canada); one or two pages; body 10 to 12 pt; margins 0.5 to 1 in (2.5 cm per Prospects); no bleed; keep it as live text for applicant tracking systems. In Bangladesh a "biodata" may add a photo and personal details; confirm what the recipient expects.

Decks: 16:9 is the default (existing preset); 4:3 for old projectors; true A4 landscape (297 x 210 mm) for printed decks because PowerPoint's "A4 Paper" preset is 275 x 190.5 mm.

Academic and infographic posters: A0 portrait in Europe (existing a0-poster), 40 x 36 or 56 x 36 in in the US (design at half size and print at 200% if PowerPoint is used); title readable from about 3 m; 300 to 800 words; 150 to 200 ppi at full size is enough.

Zines: 8-page mini zines from one Letter or A4 sheet; saddle-stitched zines in multiples of 4 pages; leave 1/8 to 1/4 in margins because copiers crop edges.

---

## Corrections to existing presets

| Existing id | Status | Correction or addition |
|---|---|---|
| a3-poster, a2-poster, a1-poster, a0-poster | sizes correct (ISO 216) | Bleed 3 mm is the UK norm (Instantprint, Printed.com). Resolution: Instantprint asks 300 dpi at any size, Vistaprint accepts 150 to 250 for posters seen across a room; for A1 and A0 raster art 150 ppi at full size is acceptable and keeps files manageable (A0 at 300 ppi is 9933 x 14043 px, computed). Add aliases "infographic poster", "research poster" to a0-poster and a1-poster. |
| b2-poster | size correct (500 x 707 mm) | Mixam also offers B1 707 x 1000 mm if a larger B size is ever needed. |
| a4-flyer, a5-flyer, a6-flyer | sizes correct | Bleed differs by printer: 3 mm (Instantprint, Solopress), 2 mm (MOO), 1.5 mm (Vistaprint). Keep 3 mm as the default and allow a per-printer override. A6 flyers and A6 postcards share the size; new postcard presets add the postal rules. |
| dl-flyer | size correct (99 x 210 mm) | Do not confuse with the DL envelope, which is 110 x 220 mm (new envelope-dl). |
| letter-flyer, half-letter, tabloid-poster | sizes correct | US online printers use about 1/16 in bleed on small flat items (Overnight Prints, 4over, Vistaprint US) and 1/8 in on posters; 0.125 in stays the safe default. |
| poster-18x24, poster-24x36 | sizes correct | 18 x 24 in is also the standard yard sign; 24 x 36 in is the common A-frame insert. Vistaprint: 0.125 in bleed and 0.25 in safe for posters; 150 to 240 ppi depending on viewing distance. |
| postcard-4x6 | size correct | Printer files differ: Overnight Prints 4.25 x 6.25 in (1/8 in bleed), MOO 6.16 x 4.16 in (0.08 in). 4 x 6 in qualifies for the USPS card price (max 4.25 x 6 in); add the address-side rules (barcode clear zone 4.75 x 0.625 in bottom right). |
| bc-us | size correct (3.5 x 2 in) | MOO US file 3.66 x 2.16 in (0.08 in bleed), safe 3.34 x 1.84 in. |
| bc-eu | size correct (85 x 55 mm) | Instantprint file 91 x 61 mm (3 mm). MOO's standard is 84 x 55 mm (new bc-moo). Solopress's bleed table shows "88 x 55 mm", a typo. Bangladeshi shops sell 3.4 x 2.1 in and 3.2 x 1.9 in (new visiting-card-bd). |
| bc-jp | size not re-checked in this pass (91 x 55 mm is the usual Japanese card) | No change. |
| trifold-a4, trifold-letter | flat sizes correct | Panels are printer-specific: PrintingForLess says tri-fold panels are not equal thirds (the tuck-in panel is narrower); Instantprint asks for equal panels and adjusts them itself. Do not hard-code equal thirds; use the printer's template. Exact offsets could not be verified. |
| bifold-a4 | correct (fold at 148.5 mm) | Add `folds_mm: [148.5]` if not present. |
| rollup-850 | size is one of the standard UK widths (Route1Print sells 850 x 2000 mm) | Add the hidden zones: US templates hide the top 1 in (25 mm) and bottom 3 in (76 mm), so keep critical content out of them unless the supplier's template adds the cassette allowance itself (Route1Print does). Bleed 3 mm and safe 3 mm on the sides (Route1Print). Instantprint lists 800 x 2000 mm graphics alongside '850 mm' cassettes, so check whether a supplier's '850' is the graphic or the base. 150 ppi at full size is enough; Route1Print asks 300. Bangladeshi shops sell the same stand as 85 x 200 cm or 33 x 80 in. |
| menu-a4 | correct | For restaurant menus that get wiped or handled, note lamination; table talkers and tents are new presets. |
| deck-16x9 | correct (1920 x 1080) | PowerPoint's default widescreen is 13.333 x 7.5 in. The 4:3 and A4 landscape deck ids already exist in web.json; note for them: PowerPoint's 4:3 preset is 10 x 7.5 in, no platform publishes a 4:3 pixel size (1024 x 768 and 1440 x 1080 are both conventions), and PowerPoint's 'A4 Paper' preset is 275.17 x 190.5 mm, not true A4, so printed A4 decks need a custom 297 x 210 mm page. |
| a4-doc | correct | No bleed for office printing; 12.7 to 25.4 mm margins (0.5 to 1 in); for printed booklets keep 12 mm on a perfect-bound edge (Mixam UK). |

---

## Bangladesh print market notes

Units and sizes:
- Large format is quoted in feet and priced per square foot: plain PVC flex about ৳20 to 65 per sq ft (Global Printing ৳20 with a 10 sq ft minimum, a Daraz seller ৳22, Ishatech ৳45 to 65; 2023 to 2026 pages). UV vinyl for outdoor use ৳300 to 550 per sq ft; grommets ৳25 to 50 each (Ishatech). A PVC festoon about ৳200 each.
- Offset work uses inches and named sheets: demy (ডিমাই) 18 x 23 in (older sources say 17.5 x 22.5 in), crown 15 x 20 in, royal 20 x 25 in, legal 8.5 x 14 in; double demy (ডিডি) is sold by the ream (sources conflict on its exact size). Books are about 8.5 x 5.5 in, 16 pages per forma on demy.
- Roll-ups are quoted in cm (85 x 200, 100 x 200, 120 x 200 cm); X-banners as 60 x 160 or 80 x 180 cm, or "2 x 5 ft" (actually 24 x 60 or 24 x 63 in). Shops round loosely, so render the exact figure and confirm.
- Visiting cards at one Dhaka shop are 3.4 x 2.1 in or 3.2 x 1.9 in, not 3.5 x 2 in (Diamu). ID cards are sold as "ATM card size" 86 x 54 mm.
- Wall calendars on demy (18 x 23 in) and crown (15 x 20 in); desk calendars 5 x 8.5 in (Diamu).

Files and colour:
- Shops accept JPEG, PNG and PDF for flex; AI and PSD for stands; vector PDF preferred for roll-ups; CMYK and 300 dpi are what their pages say, while LED Sign BD accepts 150 dpi or more for X-banners. 300 ppi at full size is impractical for big flex (a 10 x 4 ft banner would be 36000 x 14400 px, computed), so 100 to 150 ppi at full size is the practical target (global printer guidance; the "72 to 150 ppi" figure often quoted was not found in any Bangladeshi source).
- Bleed is not standardised: 0.25 to 0.5 in for PVC (Ishatech), 1 in for X-banners (Ishatech, a Daraz seller, with 2 in crop marks), "keep content 1 in inside the edge" (LED Sign BD). Ask the shop.
- Bangla fonts: publishing still leans on ASCII-based SutonnyMJ (Bijoy) fonts while digital work is Unicode, and conjuncts can break when files cross between them (Prothom Alo, bn.wikipedia). Send PDFs with embedded fonts; if a shop insists on editable CorelDRAW or Illustrator files, convert Bangla text to curves first (common advice, not verified on a shop page). CorelDRAW version conventions were not verified.
- 18 oz vinyl outdoors, 13 oz indoors (LED Sign BD), because of humidity.

Rules that change designs:
- Elections (2025 code for the February 2026 parliamentary election, and the 2026 local government code): no posters at all; festoons at most 18 x 24 in; banners at most 10 x 4 ft (horizontal or vertical); billboards at most 16 x 9 ft (one per union or ward, at most 20 per constituency); leaflets and handbills at most A4; black and white only; no PVC, polythene, rexine or laminated coatings; local-election festoons and handbills must carry a print date; only the candidate's own photo and symbol.
- Government event banners, festoons and billboards may not carry the Prime Minister's photo (circular reported July 2026).
- Billboards: neither DNCC nor DSCC publishes a current billboard size policy; DSCC declared billboards, banners and festoons illegal years before 2020 and moved to LED screens. Shops quote 20 x 10, 30 x 15, 40 x 20 and 60 x 20 ft structures, 48 x 14 ft unipoles, and LED screens built from P4 to P10 modules; digital billboard ads run in 10 to 20 second loops.
- Packaged goods: BSTI labelling rules (Bangla first, net quantity heights by pack size, MRP, maker, dates; see print-formulas.md section 13).

Where work happens: poster, leaflet and handbill presses cluster in Fakirapool, Bijoynagar, Paltan, Nilkhet and Banglabazar; paper wholesale is at Nayabazar and Babubazar (Prothom Alo).

Publishing: Rokomari publishes no e-book or cover specification (only a writer and publisher request form); Boitoi takes a Word manuscript and a JPG or PNG cover with no fee. Use the ebook-master preset.

Not verified for Bangladesh: wedding card sizes, commercial festoon sizes (3 x 4, 3 x 5 and 4 x 6 ft appear only in a blocked news snippet), how festoons are hung, the old poster size rule (often said to be 60 x 45 cm), LED billboard pixel sizes, any 3 mm or 0.125 in bleed convention.

---

## Research method and limits

- Seven research passes ran in parallel on 2026-09-24 and 2026-09-24. The shared web-search budget ran out early, so most pages were reached directly, through printers' sitemaps, help-centre search APIs (Zendesk, Freshdesk), archive.org copies, or the platforms' own public calculators. No bot checks were bypassed; sites behind them are listed below.
- Book spine numbers were read from the official KDP cover calculator and the IngramSpark Weight and Spine Width Calculator on 2026-09-24, and PDFs were read as text (pdftotext), not from tool summaries.

## Could not verify

Publishing: IngramSpark's per-page spine formula (none is published; the calculator table is given instead); KDP's groundwood caliper appears only in the calculator, not the help page; KDP's hardcover spine allowance (0.189 in) is derived from calculator outputs; Lulu's casewrap full-cover formula is assembled from its help text; BookBaby publishes no formula; Barnes and Noble Press's own cover page (blocked); Kobo's pixel size (only the 3:4 ratio is official); Google Play's preferred ratio; Amazon's phone thumbnail size; magazine front-cover barcode placement, the masthead "rack line", ASME guidance; magazine trims 8 x 10.875, 9 x 10.875 in and 230 x 300 mm; a stated convention that annual reports use A4 or Letter.

Stationery: tri-fold panel widths in mm; USPS postage-area size; Royal Mail clear-zone sizes; a US certificate product spec; invitation 4 x 9.25 in and 150 mm square; letterhead header and footer zones from a printer; notepad glue-strip depth; PVC ID card bleed and slot distance from the edge; lanyard print length and repeat; 4 x 6 in, A6 and A7 badge specs; door hanger hole position; 50 x 150, 50 x 210 and 45 x 180 mm bookmarks; table tent flat die-lines; the 0.25 pt line-weight floor (MOO states 0.5 pt). UPrinting, GotPrint, Zazzle, Minted, Helloprint (live site), PsPrint and Paper Source were unreachable.

Labels and packaging: OnlineLabels, Packlane, Sticker Robot and Avery UK were blocked (their numbers are snippet only and not used); whether Roland requires CutContour to be 100% magenta and overprinted (Roland's text says any colour value); metric round sticker presets; a standard wine label size; a "Dieline" spot-name convention; ECMA carton codes, grain direction and board caliper tables; the overall EAN-13 height including digits; a 2 cm QR minimum from a standards body; recycling-symbol sizes; Bangladesh Food Safety Authority labelling rules.

Merch: Printify per-provider pixel sizes (login only); Spring's current help centre (blocked; archived pages used); whether Merch by Amazon's mug file covers 15 oz; mug handle clear zone (estimate only); poster bleed on POD platforms; hoodie pocket limits; TeePublic hoodie, tote, hat and poster pixel sizes; Society6.

Signage: US bus interior card sizes; a signage-specific safe-area standard (TV safe areas used instead); visible area behind A-frame and snap-frame lips; perforated window film bleed; floor decal minimum text; flat print sizes for feather and teardrop flags; 33.5 x 80 and 36 x 92 in retractables; the EU hidden base in mm; JCDecaux UK paper specs (image-only PDF); Outfront (behind its tool); Ocean Outdoor pixel sizes; current Clear Channel Outdoor US sheets (2013 archived versions used) and Lamar's live site (2017 sheets via archive.org).

Legibility and colour: a sign-maker "best impact versus maximum distance" chart with a primary source; BS 8300 and the original Sign Design Guide (paywalled); the exact claims "20 ppi for billboards", "150 ppi at arm's length", "100 ppi at 1 to 2 m" as stated in the brief (printer tables above replace them); C50 M40 Y40 K100 as a printer's recipe; a printer rule that black text must overprint; large-format RIPs preferring RGB; TAC for ISO Coated v2 and Japan Color 2001; PDF/X preferences of Vistaprint, MOO, 4over, Printed.com and Instantprint; published pixel sizes for 4:3 decks; the 200 in PDF page limit (stated from long-standing Acrobat behaviour, not re-checked).
