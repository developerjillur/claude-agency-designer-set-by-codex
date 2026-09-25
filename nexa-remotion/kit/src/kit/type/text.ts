// Text splitting that never breaks a script. Words split on spaces; characters split by grapheme cluster
// (Intl.Segmenter) with Indic conjuncts (consonant + virama + consonant, reph, ya-phala) kept in one piece, so
// Bangla vowel signs and yuktakkhor never come apart.

// A cluster that ends in a virama (optionally followed by a joiner) belongs with the next cluster.
const ENDS_IN_VIRAMA = /[\u094D\u09CD\u0A4D\u0ACD\u0B4D\u0BCD\u0C4D\u0CCD\u0D4D\u0DCA\u1039\u17D2][\u200C\u200D]?$/;
const STARTS_WITH_JOINER = /^[\u200C\u200D]/;
const SPACE_START = /^\s/;

let segmenter: Intl.Segmenter | null | undefined;

const getSegmenter = (): Intl.Segmenter | null => {
	if (segmenter === undefined) {
		segmenter =
			typeof Intl !== 'undefined' && 'Segmenter' in Intl ? new Intl.Segmenter(undefined, {granularity: 'grapheme'}) : null;
	}
	return segmenter;
};

// Without Intl.Segmenter: a base character and the combining marks after it.
const roughClusters = (text: string): string[] => text.match(/\P{M}\p{M}*|\p{M}+/gu) ?? [];

/** Grapheme clusters of `text`, with Indic conjuncts merged: safe units for per-character animation. */
export const graphemes = (text: string): string[] => {
	const seg = getSegmenter();
	const raw = seg ? Array.from(seg.segment(text), (s) => s.segment) : roughClusters(text);
	const out: string[] = [];
	for (const g of raw) {
		const prev = out[out.length - 1];
		if (prev !== undefined && !SPACE_START.test(g) && (ENDS_IN_VIRAMA.test(prev) || STARTS_WITH_JOINER.test(g))) {
			out[out.length - 1] = prev + g;
		} else {
			out.push(g);
		}
	}
	return out;
};

/** The words of a text (split on any whitespace, punctuation stays on its word). */
export const splitWords = (text: string): string[] => text.trim().split(/\s+/).filter(Boolean);

/** Lines given with `\n` in the text, each split into words. */
export const splitLines = (text: string): string[][] => text.split('\n').map(splitWords).filter((l) => l.length > 0);

const BANGLA_RANGE = /[\u0980-\u09FF]/;
// Brahmic scripts (Devanagari to Sinhala), Thai, Lao, Myanmar, Khmer: letter spacing and tight leading hurt them.
const COMPLEX = /[\u0900-\u0DFF\u0E00-\u0EFF\u1000-\u109F\u1780-\u17FF]/;

export const isBangla = (text: string): boolean => BANGLA_RANGE.test(text);
export const isComplexScript = (text: string): boolean => COMPLEX.test(text);

const BN_DIGITS = '০১২৩৪৫৬৭৮৯';

/** Latin digits to Bengali digits (০১২৩৪৫৬৭৮৯); everything else is kept. */
export const toBanglaDigits = (s: string): string => s.replace(/[0-9]/g, (d) => BN_DIGITS[Number(d)]);

/** Bengali digits back to Latin digits. */
export const toLatinDigits = (s: string): string => s.replace(/[০-৯]/g, (d) => String(BN_DIGITS.indexOf(d)));

/** True for a unit that is only punctuation (it glues to the word before it). */
export const isPunctuation = (s: string): boolean => /^[\p{P}\u0964\u0965]+$/u.test(s.trim());

/** True when the word ends a sentence (., !, ?, the Bangla dari and the ellipsis). */
export const endsSentence = (s: string): boolean => /[.!?\u0964\u0965\u2026]["'\u201D\u2019)]*$/.test(s.trim());

/** True when the word ends a clause (comma, colon, semicolon) or a sentence. */
export const endsClause = (s: string): boolean => endsSentence(s) || /[,;:]["'\u201D\u2019)]*$/.test(s.trim());

// Words that belong with the word after them, so a line never ends on one: English small words, and Bangla
// determiners, quantifiers, genitives and numbers ("মোট / বিক্রি" and "কোন / জিনিস" read as broken phrases).
const BINDERS = new Set([
	'a', 'an', 'the', 'to', 'of', 'and', 'or', 'in', 'on', 'for', 'with', 'at', 'by', 'is', 'my', 'our', 'your', 'this', 'no', 'not',
	'কোন', 'কোনো', 'কোনটা', 'এই', 'ওই', 'সেই', 'এ', 'ও', 'যে', 'যেকোনো', 'প্রতি', 'প্রতিটা', 'প্রতিটি', 'প্রত্যেক',
	'এক', 'একটা', 'একটি', 'দুই', 'দুটো', 'দুইটা', 'তিন', 'তিনটা', 'তিনটি', 'চার', 'পাঁচ', 'কিছু', 'সব', 'সকল', 'অনেক',
	'আরও', 'আরো', 'মোট', 'নতুন', 'পুরো', 'আজকের', 'দিনের', 'রাতের', 'মাসের', 'আমার', 'আপনার', 'তোমার', 'আমাদের', 'তাদের',
]);

/** True when a line should not end on this word (it belongs with the next). A word with closing punctuation never binds. */
export const bindsToNext = (word: string): boolean => {
	const w = word.trim().toLowerCase();
	if (/[\p{P}\u0964\u0965]$/u.test(w)) {
		return false;
	}
	return BINDERS.has(w) || /^[০-৯0-9]+$/.test(w);
};
