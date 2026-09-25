# Bangla (and other complex scripts) on screen

Bangla text breaks in three ways that Latin text does not: splitting it into characters destroys conjuncts and vowel
signs, letter spacing breaks the headline stroke (matra) and the conjunct shapes, and tight leading or shallow masks
cut the vowel signs above and the forms below. The kit handles all three; this file says how and why, for anything
written by hand.

## 1. Fonts

Every kit font stack ends in a Bangla font, so Bengali letters in a Latin title still render in a real Bangla face.

| Font (kit key) | Kind | Weights | Good for |
|---|---|---|---|
| AnekBangla | sans, the kit default | 100 to 800 | titles, captions, UI; clean and wide |
| HindSiliguri | sans | 300 to 700 | words only: it draws the digit ১ as a small hook that reads as ৲, so never prices, dates or counts |
| NotoSansBengali | sans | 100 to 900 | body, dense text, the most complete coverage |
| NotoSerifBengali | serif | 100 to 900 | editorial, data journalism |
| TiroBangla | serif | 400 (italic) | literary, luxury, trailers |
| BalooDa2 | rounded | 400 to 800 | playful, kids, friendly brands |
| Galada | display script | 400 | festive headlines only |
| Atma | handwritten | 300 to 700 | whiteboard, notes |

The `dhaka` theme is Bangla first (Anek Bangla display, Noto Sans Bengali body). Every Bangla font above was rendered
with ০ to ৯: only Hind Siliguri got one wrong ("তেল, ১ লিটার ৳১৯০" read as ৳৯০ in a review). Load weights through core
(`loadKitFont('AnekBangla', [700, 800])`); with raw `@remotion/google-fonts` pass `subsets: ['bengali', 'latin']`.

## 2. Clusters and conjuncts

- A visible "letter" in Bangla is a grapheme cluster: a consonant with its vowel sign (কি, কো), a conjunct of two or
  three consonants joined by the virama (হসন্ত, U+09CD): ক্ষ, স্ব, প্র, ন্ট, র্ম (reph), র‍্য (ya-phala with a zero
  width joiner). Pre-base vowel signs (ি, ে, ৈ) are stored after the consonant but drawn before it; the shaper does
  that inside the cluster.
- `Intl.Segmenter` with `granularity: 'grapheme'` gives clusters; newer ICU versions (Unicode 15.1, rule GB9c) also keep
  virama conjuncts together, older ones split `ক্` from `ষ`. The kit's `graphemes()` merges any cluster ending in a
  virama (optionally followed by a joiner) with the next one, so the result is the same everywhere: `ক্ষমা` gives
  `ক্ষ`, `মা`; `প্রতি` gives `প্র`, `তি`; `ঘণ্টা` gives `ঘ`, `ণ্টা`.
- Never `text.split('')` or `[...text]` for animation: vowel signs detach and show dotted circles, conjuncts fall apart.
  Animate by word (the default everywhere) or by `graphemes()` for short words.
- Rendering pieces in separate inline elements is safe at cluster boundaries (the kit's typewriter and scramble do it);
  inline-blocks cost kerning, which Bangla rarely uses.

## 3. Spacing, case, leading, masks

- **Letter spacing 0**, always: any tracking opens gaps in the matra and can break conjunct shaping. The kit's
  `trackingFor()` returns 0 for any complex script.
- **No uppercase**: Bangla has no case; `textTransform: uppercase` does nothing to Bangla but still changes the Latin
  words mixed in. Kinetic caps themes keep Bangla lines as they are.
- **Leading**: display at least 1.28, body 1.5, captions 1.4 (vowel signs rise above the matra; ু, ূ, ৃ and below-base
  forms hang under the baseline).
- **Masks**: deeper padding (0.34 em top, 0.3 em bottom in the kit) and travel that clears the box and both paddings.
- Bangla reads smaller than Latin at the same px size: captions about 10 % larger, outlines thinner (0.1 of the size
  instead of 0.14).

## 4. Numbers

- Bengali digits ০১২৩৪৫৬৭৮৯: `toBanglaDigits('12,450')` or Intl with `bn-BD`, which also uses the lakh grouping of
  Bangladesh: `১২,৩৪,৫৬৭` (not 1,234,567). Compact long form: `১২.৪ লাখ`, `২৪ হাজার`, `১.২ কোটি`. Currency BDT: `৳`
  (`২৪,৮১৩৳` in the `bn-BD` pattern; write `৳ ২৪,৮১৩` by hand when a brand prefers the symbol first).
- The kit's `Counter digits="bangla"` does all of this and sets digits in fixed-width slots (many Bangla fonts have
  proportional digits, which jiggle while counting).
- Mixed text: a Latin number inside Bangla text is fine in a campaign that writes numbers that way; be consistent in
  one video.

## 5. Punctuation and line breaks

- Sentence end: the dari `।` (U+0964), double dari `॥` (U+0965) in verse. The kit's `endsSentence()` knows them, so
  caption pages and subtitle cues break after them.
- Words are separated by spaces, so measuring, wrapping and `fitTextOnNLines` work by word. Never break inside a word.
- Quotes: “ ” and ‘ ’ as in English.

## 6. Captions and transcription

- Transcribe Bangla with a multilingual model of at least `medium` (or `large-v3-turbo`) and `language: 'bn'`;
  `.en` models return garbage. Check sub-word tokens without leading spaces are glued into words (the kit's
  `toCaptions` keeps a token-level transcript's spacing; `captionWords` glues).
- Pages of 2 to 4 words work as in English; Bangla words are longer, so a page is often one line.
- Subtitles: count characters by grapheme when judging line length by eye (a conjunct is one visual letter); the 42
  character rule counts code points and is conservative for Bangla.

## 7. Writing Bangla copy

Use the `natural-copy` skill (Bangladeshi register, casual everyday words, no sadhu or bookish style) and lint every
on-screen line (`copylint --copy onscreen.json --locale BD`). Short natural lines read best in motion:
"মিটিং কম, কাজ বেশি", "চলুন, শুরু করা যাক।", "আসল কাজটা হয় ক্যামেরার পেছনে".

## 8. Checklist

1. The font is a Bangla font (look at the letterforms in a full-size still; a fallback is thinner and wider).
2. No dotted circles, no broken conjuncts, vowel signs in place (check ি before its consonant).
3. Nothing cut at the top or bottom by masks or line boxes.
4. Digits and grouping as the audience writes them.
5. Captions: pages break after `।`, size about 10 % up, outline thinner.
