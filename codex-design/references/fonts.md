# Fonts: choosing, pairing and loading

Every family below is on Google Fonts under the OFL (or Apache) and installs with
`design.py fonts --family "Family:weights" --out brand/fonts` (Fontsource files, `unicode-range`, licence file).
OFL fonts may be used commercially and embedded in PDFs; they may not be sold on their own. Client fonts are used
only from the client's own files and never redistributed. Checked against Google Fonts metadata on 2026-09-23.

## 1. Principles

- **Fewer is better.** One family with weight and width contrast often beats two. Superfamilies and same-designer
  pairs are the safest harmony.
- **When you pair, contrast one dimension clearly** (serif vs sans, wide vs condensed, geometric vs humanist) and match
  the rest (x-height, stroke weight at the sizes used, era and mood).
- **Give each face one job** (display / text / data). Use optical sizes (`opsz`) at display sizes where they exist.
- **Same font-size is not the same visual size:** x-heights run from 0.386 em (Cormorant Garamond) to 0.546 (Inter)
  and 0.733 (Anton). Scale small-x-height serifs up 25–35 % next to Inter-class sans.
- **Reflex fonts need a reason.** Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Arial/Helvetica, Space Grotesk
  as the display voice; Playfair Display + Montserrat as "luxury"; Bebas Neue/Oswald/Anton as "sport"; Lobster,
  Pacifico, Dancing Script, Great Vibes, Amatic SC, Comfortaa as "fun/elegant/handmade". The fonts are fine; the
  default use gives the piece away. Genre conventions are allowed with a restyle (Anton on a thumbnail, recoloured and
  cropped). Rotate within a preset's font pool across a client's pieces.
- **Google Sans** is OFL since December 2025 and covers Latin, Bengali and Devanagari, but reads as Google's brand:
  avoid it for client brands unless you need its coverage.

## 2. Latin pairings by mood

Display / text, with the weights that look best.

| Mood / industry | Pairing | Weights | Watch out |
|---|---|---|---|
| Corporate, finance, consulting | Hanken Grotesk / Source Serif 4 | 700 / 400 | serif body ≥ 36 px on social |
| | IBM Plex Sans / IBM Plex Serif (+ Plex Mono for data) | 600 / 400 | recognisably IBM, can feel cold |
| | Schibsted Grotesk (one family) | 800 / 400 | none |
| | Public Sans (one family) | 700 / 400 | plain unless the layout carries it; NGO / public sector |
| Tech, SaaS, AI | Bricolage Grotesque / Figtree (+ JetBrains Mono) | 700–800 / 400 | Bricolage is quirky small; keep it for display |
| | Mona Sans (one family, width axis) | 800 expanded / 400 | none |
| | Host Grotesk or Funnel Display / Funnel Sans | 600–700 / 400 | not overused yet |
| | avoid by default: Space Grotesk + Inter, Inter-only, Geist-only | | the AI/SaaS default look |
| Luxury, fashion, beauty, hospitality | Bodoni Moda (opsz) / Jost | 500–600 / 400; caps labels +10–12 % | hairlines vanish small: ≥ 72 px on 1080, calm grounds |
| | Playfair (2023, opsz) / Albert Sans | display opsz / 400 | Playfair Display + Montserrat is the cliché |
| | Cormorant Garamond / Hanken Grotesk | 500–600 / 400 | x-height 0.386: never body text, +30 % size |
| | Gloock / Instrument Sans | 400 / 400–500 | single weight: never fake-bold |
| Editorial, media, reports | Newsreader (opsz 72) / Newsreader (opsz 12) + Libre Franklin labels | 600 / 400 | built-in line height 1.0: always set it |
| | Fraunces (opsz, SOFT, WONK 0) / Source Serif 4 or Libre Franklin | 600 / 400 | WONK 1 small looks like an error; Fraunces is a reflex font: use with a reason |
| | Instrument Serif / Instrument Sans | 400 / 400–600 | serif is 400 only |
| | Libre Caslon Display + Text / Libre Franklin | 400 / 400–600 | none |
| Playful, kids, education | Fredoka / Nunito | 600 / 400–600 | add colour or illustration to avoid the kids-template look |
| | Baloo 2 / Nunito Sans | 700–800 / 400 | sister families in Bengali, Devanagari, Arabic: good multilingual playful |
| | accent: Caveat or Kalam | 500–700 | ≤ 10 % of the text, never body |
| Bold, sport, fitness, events | Big Shoulders (opsz) / Barlow or Barlow Condensed | 800 caps / 500 | caps need +2–4 % tracking small |
| | Archivo expanded / Archivo condensed | 800 / 400 | one superfamily, width 62–125 |
| | Unbounded / Manrope | 800 / 500 | wide: short words only |
| | Anton / Inter Tight | 400 / 500 | template staple: restyle it |
| Organic, wellness, craft | Fraunces (SOFT 100, WONK 1) / Karla | 500 / 400 | none |
| | Young Serif / Work Sans | 400 / 400 | single weight |
| | Lora / Nunito Sans | 500–600 / 400 | none |
| Medical, clinical, public health | Atkinson Hyperlegible Next (one family) | 700 / 400 | plain: hierarchy by colour and space |
| | Lexend (one family) | 600 / 400 | none |
| | Source Sans 3 / Source Serif 4 | 600 / 400 | none |
| Food, café, FMCG | Shrikhand / Work Sans | 400 / 400–500 | display only, short words |
| | DM Serif Display or Gloock / DM Sans | 400 / 400 | DM is very common |
| | Bagel Fat One / Figtree | 400 / 400–600 | display only |
| | Alfa Slab One / Rokkitt | 400 / 400–600 | retro cliché if overdone |

Thumbnail and poster display faces with a convention behind them: Anton, Bebas Neue, Archivo Black, Big Shoulders,
Barlow Condensed ExtraBold (restyle: colour, crop, scale, stroke).

## 3. Latin + Bengali

The Bengali headline stroke should sit at ~1.26× the partner's Latin x-height. `@N` is the `size-adjust` for the
Bengali face next to that Latin font (`fonts --family "Noto Sans Bengali:400,700@110"`). Min display line-height is
measured from the font's ink.

| Bengali family | Weights | Latin partner → @size-adjust | Min display line-height | Character | Known issues |
|---|---|---|---|---|---|
| Noto Sans Bengali | 100–900 + width | Inter / Noto Sans @110; Plus Jakarta @109 | 1.24 (1.36 at @110) | safest coverage; condensed widths fit long headlines | generic look |
| Noto Serif Bengali | 100–900 + width | Source Serif 4 @100; Lora @102; Newsreader @89 | 1.23 | editorial, literary | none |
| Anek Bangla | 100–800 + width 75–125 | Archivo @106; Inter @110; own Anek Latin @98 | 1.33 | headlines, wordmarks; bold and condensed shine | Anek Latin caps are small; deep descenders |
| Hind Siliguri | 300–700 | Hind @100; DM Sans @99; Work Sans / Figtree @98; Inter @107 | 1.23 | UI humanist, legible supporting text | **digit ১ malformed in 400–600** (google/fonts #6037): use 700 or another font for Bengali numerals |
| Baloo Da 2 | 400–800 | Baloo 2 @96; Nunito @100; Fredoka @98 | 1.34 | friendly, FMCG, kids | display personality |
| Tiro Bangla | 400 + italic | Source Serif 4 @100; Libre Caslon Text @108 | 1.23 | literary, traditional | one weight: `font-synthesis: none`, emphasise by size or colour |
| Galada | 400 | DM Serif Display @90; Fraunces @88 (never its own Latin) | 1.44 | festive display script | its Latin is derived from Lobster: do not use it |
| Mina | 400 / 700 | Sora @106; Manrope @107 | 1.29 | geometric, techy display | two weights |
| Atma | 300–700 | Figtree @101 | 1.32 | informal, fun | informal Latin |
| Alkatra | 400–700 | Archivo @109 | 1.35 | street / graffiti display | display only |

Size: Bengali text needs at least 12 px at viewing size, more than the Latin floor. The check sets the floor from
each preset's viewing width (`view_width_px` in `scripts/presets.json`): 34 px on a 1080 post or story, 77 px on a
YouTube thumbnail. The judges failed Bengali at 26 to 30 px and passed it at about 42 px on a 1080 story and 96 px for
a thumbnail subtitle, so aim there. The checks flag text below the floor.

Rules: no caps, no italics (Tiro's italic excepted), no letter-spacing; emphasis by weight, colour, size or width
(Anek); dari "।" as the full stop; one digit script per piece (০–৯ or 0–9, a brand decision); `lang="bn"` on Bengali
runs; body line-height 1.5–1.8. Legacy Bijoy-encoded fonts are never used (Unicode only).

## 4. Latin + Arabic (RTL)

Arabic alef ≈ 1.05× the Latin cap height. `dir="rtl"`, mirror the layout, no letter-spacing (kashida only sparingly),
no caps/italics/fake bold, numerals per market (0–9, ٠–٩ or ۰–۹), native review mandatory, put Arabic above Latin in
bilingual lockups.

| Family | Weights | Partner → @ | Min display LH | Character |
|---|---|---|---|---|
| IBM Plex Sans Arabic | 100–700 | IBM Plex Sans @99 (consider @105) | 1.35 | corporate, tech |
| Noto Naskh Arabic | 400–700 | Noto Serif @112; Source Serif 4 @105 | 1.30 | text Naskh, pairs with serifs |
| Noto Sans Arabic | 100–900 + width | Inter @107 | 1.32 | neutral UI (built-in LH 2.1: set it) |
| Noto Kufi Arabic | 100–900 | Inter @101 | 1.42 | geometric Kufi, large sizes only |
| Cairo | 200–1000 | Inter @107 | 1.35 | contemporary, techy (very common in the region) |
| Tajawal | 200–900 | DM Sans @114 | 1.20 | low-contrast geometric |
| Almarai | 300–800 | Inter @107 | 1.32 | clear screen UI |
| Readex Pro | 160–700 | Lexend @99 | 1.46 | accessible reading |
| Amiri | 400/700 + italic | Lora @102; EB Garamond @95 | 1.58 (body ≥ 1.8) | classical book Naskh |
| El Messiri | 400–700 | Playfair Display @113 | 1.26 | brush-Naskh display, culture |
| Reem Kufi | 400–700 | Montserrat @92 | 1.43 | early Kufic feel; strong connotations |
| Rubik | 300–900 | Inter @102 | 1.22 | soft, friendly consumer |

Religious phrases: use the client's verified calligraphy or typeset text checked by a native reader; never generate it.

## 5. Latin + Devanagari

Headline stroke ≈ 1.26× the Latin x-height, as for Bengali. No italics or caps; tracking must not break the
shirorekha; extra line spacing.

| Family | Weights | Partner → @ | Min display LH | Character |
|---|---|---|---|---|
| Hind | 300–700 | own Latin @100 | 1.23 | UI humanist |
| Mukta | 200–800 | own Latin @94; Inter @109 | 1.23 | humanist system |
| Anek Devanagari | 100–800 + width | Anek Latin @97 | 1.28 | headlines, wordmarks |
| Noto Sans / Serif Devanagari | 100–900 + width | Inter @111 / Noto Serif @108 | 1.22 / 1.23 | coverage |
| Tiro Devanagari Hindi | 400 + italic | Source Serif 4 @100 | 1.30 | literary, single weight |
| Martel | 200–900 | Lora @98 | 1.48 | long text |
| Eczar | 400–800 | Fraunces @97 | 1.39 | lively display |
| Yatra One | 400 | DM Serif Display @98 | 1.32 | railway sign-painting display |
| Rozha One | 400 | Playfair Display @116 | 1.11 | high-contrast Didone (weddings, film) |
| Baloo 2 | 400–800 | own Latin @97 | 1.25 | playful |

## 6. Latin + CJK

- Japanese: Noto Sans JP, M PLUS 1/2, Zen Kaku Gothic New, BIZ UDPGothic, IBM Plex Sans JP, LINE Seed JP (gothic ↔ sans);
  Noto Serif JP, Shippori Mincho, Zen Old Mincho (mincho ↔ serif: Cormorant, EB Garamond, Libre Caslon Text). Display:
  Dela Gothic One. Japanese 10–15 % smaller than the Latin (or the Latin larger), +10–15 % line height, 15–35
  characters per line, `word-break: auto-phrase`, `text-spacing-trim`.
- Korean: Noto Sans/Serif KR, Gothic A1, IBM Plex Sans KR, Nanum Gothic/Myeongjo, Gowun Batang/Dodum; display Black
  Han Sans, Do Hyeon, Jua. `word-break: keep-all`.
- Chinese: Noto Sans/Serif SC and TC; display ZCOOL KuaiLe, ZCOOL XiaoWei, Ma Shan Zheng (brush), LXGW WenKai TC.
- Always tag the language (`zh-Hans`, `zh-Hant`, `ja`, `ko`): pan-CJK fonts choose glyph forms from it. No italics,
  `font-synthesis: none`. Install only the subsets you need (`fonts --subsets …`); CJK files are large.

## 7. Loading and CSS

```css
/* brand.css imports fonts/fonts.css (made by `design.py brand` or `fonts`) */
:root { --font-display: 'Bricolage Grotesque', system-ui, sans-serif;
        --font-text: 'Figtree', system-ui, sans-serif;
        --font-bengali: 'Anek Bangla', system-ui, sans-serif; }  /* the Bengali face first, as `brand` writes it */
h1 { font-family: var(--font-display); font-weight: 800; line-height: 1.0; letter-spacing: -0.02em; text-wrap: balance; }
p  { font-family: var(--font-text); line-height: 1.4; text-wrap: pretty; }
[lang="bn"] { font-family: var(--font-bengali); line-height: 1.4; }  /* the kit already zeroes tracking here */
[lang="bn"] [lang="en"] { font-family: var(--font-text); }         /* a Latin word inside a Bengali line */
.pill { text-box: trim-both cap alphabetic; }
```

- `brand.json` `fonts` entries take the same spec strings, e.g. `"bengali": "Anek Bangla:500,700@106"`.
  `design.py brand` turns each role into a variable, so `bengali` becomes `--font-bengali`: the variable the kit's
  patterns and the typeset overlay use.
- **Order in a Bengali run:** the Bengali face first, then a generic family. The renderer's script check reads the
  first family, so a Latin face placed first is reported as a fallback even when the Bengali face behind it draws the
  text. The Bengali face then also draws any Latin in that run with its own Latin glyphs (Anek Latin for Anek
  Bangla). When those do not suit, as with Galada's Lobster-derived Latin, set the Latin word in its own
  `<span lang="en">` (the `[lang="bn"] [lang="en"]` rule above).
- The renderer waits for `document.fonts.ready`, checks every face actually drew its text (weight, style and script),
  and reports a fallback as an error and a missing script as a warning.
- Search: `fonts --search "*" --subset bengali` (all Bengali families), `fonts --search grotesk --category sans-serif`.

## 8. Print, system fonts and licences (`references/research/R6-rendering-tooling.md`, verified on this Mac)

- **Chrome's PDF engine embeds real TrueType only for static TrueType-outlined fonts.** Variable fonts, CFF/OTF
  outlines, restricted fonts (fsType 0x0002), blurred text-shadows and faux bold become **Type 3** glyph procedures:
  they print, but preflight flags them and text extraction suffers. The static per-weight files that `fonts`/`brand`
  download embed as CID TrueType (checked: Bricolage Grotesque, Figtree, Anek Bangla). `render` warns on Type 3 in a
  print PDF. For a variable-only family, make a static instance:
  `fonttools varLib.instancer Font[wdth,wght].ttf wght=700 wdth=100 -o Font-Bold.ttf` (fontTools is in the skill venv).
- **System fonts are not for client files.** They drift with OS updates, other machines lack them, and the macOS licence
  allows display and printing while running Apple software, not redistribution in deliverables. The script-fallback
  check warns when a system font draws a script.

| System or local font | In a PDF | Use |
|---|---|---|
| Kohinoor Bangla (macOS) | Type 3 (CFF) | no: download Noto Sans Bengali, Hind Siliguri, Anek Bangla or Tiro Bangla |
| Bangla Sangam MN / Bangla MN (macOS) | TrueType | proofing only (Apple licence) |
| Kalpurush (if installed) | TrueType | allowed: the name table says SIL OFL; ship the file with the job |
| Siyam Rupali (if installed) | Type 3 (restricted fsType) | avoid: restricted embedding and an unclear GPL font exception |
| SF Arabic, Hiragino, Kohinoor Devanagari | Type 3 (variable or CFF) | no: use Noto Naskh/Kufi Arabic, Noto Sans JP/SC, Noto Sans Devanagari |

- **Emoji in print:** insert them as SVG images (Noto emoji SVGs, Apache-2.0, or Twemoji with CC-BY credit), never
  through the Apple Color Emoji font (bitmaps, Apple licence). On screen, Noto Color Emoji (OFL) works as a web font.
- `font-synthesis: none` is on in the kit: a missing bold shows up as a check failure instead of a faked weight.

