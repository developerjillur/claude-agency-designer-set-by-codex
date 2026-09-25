// Measured text layout: every word is measured once (after the fonts loaded) at 100 px, then lines, widths and the
// size that fits are pure arithmetic. Tracking is in em, so widths scale linearly with the size. The result is
// rendered as explicit lines with `white-space: pre`, so the browser never re-wraps what was measured.
import {measureText} from '@remotion/layout-utils';
import type React from 'react';
import {splitWords} from './text';

export type TypeStyle = {
	fontFamily: string;
	fontWeight: number;
	fontSize: number; // px in the frame (already multiplied by unit)
	letterSpacing: number; // em
	lineHeight: number; // unitless
	textTransform?: 'none' | 'uppercase';
	fontVariantNumeric?: string;
};

/** The CSS for a TypeStyle, identical to what was measured. */
export const typeCss = (s: TypeStyle): React.CSSProperties => ({
	fontFamily: s.fontFamily,
	fontWeight: s.fontWeight,
	fontSize: s.fontSize,
	letterSpacing: `${s.letterSpacing}em`,
	lineHeight: s.lineHeight,
	textTransform: s.textTransform ?? 'none',
	fontVariantNumeric: s.fontVariantNumeric,
	textRendering: 'geometricPrecision',
	fontKerning: 'normal',
});

const REF = 100;

/** Width in px of `text` set in `s` at `size` (default: the style's size). Call only after useTypeFontsReady(). */
export const measureTextWidth = (text: string, s: TypeStyle, size = s.fontSize): number =>
	measureText({
		text,
		fontFamily: s.fontFamily,
		fontSize: size,
		fontWeight: s.fontWeight,
		letterSpacing: `${s.letterSpacing}em`,
		textTransform: s.textTransform ?? 'none',
		fontVariantNumeric: s.fontVariantNumeric,
		validateFontIsLoaded: true,
		additionalStyles: {textRendering: 'geometricPrecision'},
	}).width;

export type LaidWord = {text: string; index: number; x: number; width: number};
export type LaidLine = {words: LaidWord[]; text: string; width: number};
export type TextLayout = {
	lines: LaidLine[];
	fontSize: number; // the size that fits (px in the frame)
	space: number; // width of a space at that size
	width: number; // the widest line
	lineHeightPx: number;
	height: number; // lines * line height
	words: string[]; // every word in reading order (LaidWord.index points here)
};

type Measured = {words: string[]; w: number[]; space: number; paragraphs: number[][]};

const measureAll = (paragraphs: string[][], s: TypeStyle): Measured => {
	const words: string[] = [];
	const idx: number[][] = [];
	for (const p of paragraphs) {
		const row: number[] = [];
		for (const w of p) {
			row.push(words.length);
			words.push(w);
		}
		idx.push(row);
	}
	return {
		words,
		w: words.map((word) => measureTextWidth(word, s, REF)),
		space: measureTextWidth(' ', s, REF),
		paragraphs: idx,
	};
};

// greedy fill of one paragraph at `k` (size / REF) within `max` px
const greedy = (m: Measured, para: number[], k: number, max: number, binds?: (i: number) => boolean): number[][] => {
	const lines: number[][] = [];
	let cur: number[] = [];
	let width = 0;
	for (const i of para) {
		const w = m.w[i] * k;
		const add = cur.length ? m.space * k + w : w;
		if (cur.length && width + add > max) {
			// a word that belongs with the next moves down with it
			const carry: number[] = [];
			while (binds && cur.length > 1 && binds(cur[cur.length - 1])) {
				carry.unshift(cur.pop() as number);
			}
			lines.push(cur);
			cur = [...carry, i];
			width = lineWidth(m, cur, k);
		} else {
			cur.push(i);
			width += add;
		}
	}
	if (cur.length) {
		lines.push(cur);
	}
	return lines;
};

const lineWidth = (m: Measured, line: number[], k: number): number =>
	line.reduce((acc, i, j) => acc + m.w[i] * k + (j ? m.space * k : 0), 0);

// the narrowest width that keeps the same number of lines: even lines instead of one long and one orphan
const balanced = (m: Measured, para: number[], k: number, max: number, binds?: (i: number) => boolean): number[][] => {
	const first = greedy(m, para, k, max, binds);
	if (first.length < 2) {
		return first;
	}
	const widest = Math.max(...para.map((i) => m.w[i] * k));
	let lo = Math.max(widest, max * 0.4);
	let hi = max;
	for (let n = 0; n < 14; n++) {
		const mid = (lo + hi) / 2;
		if (greedy(m, para, k, mid, binds).length === first.length) {
			hi = mid;
		} else {
			lo = mid;
		}
	}
	return greedy(m, para, k, hi + 0.5, binds);
};

export type TextLayoutOptions = {
	maxWidth: number; // px in the frame
	maxLines?: number; // default: unlimited
	balance?: boolean; // default true: even line lengths
	shrink?: boolean; // default true: reduce the size until it fits maxWidth and maxLines
	minSize?: number; // px in the frame, the floor for shrinking (default 40% of the size)
	noBreakAfter?: (word: string) => boolean; // words a line must not end on (captions pass bindsToNext)
};

/**
 * Lays out `text` (a string, `\n` for forced breaks, or an array of given lines) in `style` within `maxWidth`:
 * the words of every line with their x offsets, and the size that fits. Call only after useTypeFontsReady().
 */
export const layoutText = (text: string | readonly string[], style: TypeStyle, opts: TextLayoutOptions): TextLayout => {
	const paragraphs = (typeof text === 'string' ? text.split('\n') : [...text]).map(splitWords).filter((p) => p.length);
	const m = measureAll(paragraphs, style);
	const {maxWidth, maxLines = Infinity, balance = true, shrink = true, noBreakAfter} = opts;
	const binds = noBreakAfter ? (i: number) => noBreakAfter(m.words[i]) : undefined;
	const place = (size: number, bal: boolean): number[][] => {
		const k = size / REF;
		return m.paragraphs.flatMap((p) => (bal ? balanced(m, p, k, maxWidth, binds) : greedy(m, p, k, maxWidth, binds)));
	};
	const fits = (size: number): boolean => {
		const k = size / REF;
		if (m.w.some((w) => w * k > maxWidth + 0.5)) {
			return false;
		}
		return place(size, false).length <= maxLines;
	};
	let size = style.fontSize;
	if (shrink && !fits(size)) {
		let lo = opts.minSize ?? style.fontSize * 0.4;
		let hi = size;
		if (fits(lo)) {
			for (let n = 0; n < 18; n++) {
				const mid = (lo + hi) / 2;
				if (fits(mid)) {
					lo = mid;
				} else {
					hi = mid;
				}
			}
		}
		size = Math.floor(lo * 10) / 10;
	}
	const k = size / REF;
	const groups = place(size, balance);
	const lines: LaidLine[] = groups.map((g) => {
		let x = 0;
		const words = g.map((i, j) => {
			if (j) {
				x += m.space * k;
			}
			const lw: LaidWord = {text: m.words[i], index: i, x, width: m.w[i] * k};
			x += m.w[i] * k;
			return lw;
		});
		return {words, text: g.map((i) => m.words[i]).join(' '), width: lineWidth(m, g, k)};
	});
	const lineHeightPx = size * style.lineHeight;
	return {
		lines,
		fontSize: size,
		space: m.space * k,
		width: Math.max(0, ...lines.map((l) => l.width)),
		lineHeightPx,
		height: lines.length * lineHeightPx,
		words: m.words,
	};
};

/** The x offset of a line of `lineW` in a box of `boxW` for an alignment. */
export const textAlignOffset = (align: 'left' | 'center' | 'right', boxW: number, lineW: number): number =>
	align === 'center' ? (boxW - lineW) / 2 : align === 'right' ? boxW - lineW : 0;

type Metrics = {ascent: number; descent: number};
const metricsCache = new Map<string, Metrics>();

/**
 * Ascent and descent (as a fraction of the size) of the primary font of a family stack, from canvas TextMetrics.
 * Used to put transform origins exactly on the baseline. Call only after the fonts loaded.
 */
export const fontMetrics = (fontFamily: string, fontWeight: number): Metrics => {
	const id = `${fontFamily}|${fontWeight}`;
	const hit = metricsCache.get(id);
	if (hit) {
		return hit;
	}
	let out: Metrics = {ascent: 0.93, descent: 0.24};
	if (typeof document !== 'undefined') {
		const ctx = document.createElement('canvas').getContext('2d');
		if (ctx) {
			ctx.font = `${fontWeight} ${REF}px ${fontFamily}`;
			const tm = ctx.measureText('Hg');
			if (tm.fontBoundingBoxAscent > 0) {
				out = {ascent: tm.fontBoundingBoxAscent / REF, descent: tm.fontBoundingBoxDescent / REF};
			}
		}
	}
	metricsCache.set(id, out);
	return out;
};

/**
 * Where the baseline sits in a line box, as a fraction of the box height from the top: the value to use in
 * `transformOrigin` so scaled type grows from its baseline and does not wobble.
 */
export const baselineRatio = (fontFamily: string, fontWeight: number, lineHeight: number): number => {
	const {ascent, descent} = fontMetrics(fontFamily, fontWeight);
	const halfLeading = (lineHeight - (ascent + descent)) / 2;
	return Math.min(1, Math.max(0, (halfLeading + ascent) / lineHeight));
};
