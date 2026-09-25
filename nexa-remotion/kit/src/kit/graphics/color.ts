// Small colour maths for charts: mixes, opacity, readable text on a fill, and series palettes from the theme.
// Mixing happens in JS (not CSS color-mix) so SVG fills, gradients and interpolateColors all get plain rgb values.
import type {Theme} from '../core';

type RGBA = [number, number, number, number];

const parse = (c: string): RGBA | null => {
	const s = c.trim();
	if (s.startsWith('#')) {
		const h = s.slice(1);
		const full = h.length === 3 || h.length === 4 ? h.split('').map((x) => x + x).join('') : h;
		if (full.length !== 6 && full.length !== 8) {
			return null;
		}
		const n = (i: number) => parseInt(full.slice(i, i + 2), 16);
		return [n(0), n(2), n(4), full.length === 8 ? n(6) / 255 : 1];
	}
	const m = s.match(/^rgba?\(([^)]+)\)$/i);
	if (m) {
		const p = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
		if (p.length >= 3 && p.every((x) => Number.isFinite(x))) {
			return [p[0], p[1], p[2], p[3] ?? 1];
		}
	}
	return null;
};

const out = ([r, g, b, a]: RGBA): string =>
	a >= 1 ? `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})` : `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${+a.toFixed(3)})`;

/** `a` mixed toward `b` by t (0 = a, 1 = b). Unknown colour strings fall back to CSS color-mix. */
export const mixColor = (a: string, b: string, t: number): string => {
	const pa = parse(a);
	const pb = parse(b);
	const k = Math.min(1, Math.max(0, t));
	if (!pa || !pb) {
		return `color-mix(in srgb, ${a} ${Math.round((1 - k) * 100)}%, ${b})`;
	}
	return out([0, 1, 2, 3].map((i) => pa[i] + (pb[i] - pa[i]) * k) as RGBA);
};

/** The colour with an opacity. */
export const withOpacity = (c: string, a: number): string => {
	const p = parse(c);
	if (!p) {
		return `color-mix(in srgb, ${c} ${Math.round(a * 100)}%, transparent)`;
	}
	return out([p[0], p[1], p[2], p[3] * Math.min(1, Math.max(0, a))]);
};

const lum = (c: string): number => {
	const p = parse(c);
	if (!p) {
		return 0.5;
	}
	const ch = (v: number) => {
		const x = v / 255;
		return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
	};
	return 0.2126 * ch(p[0]) + 0.7152 * ch(p[1]) + 0.0722 * ch(p[2]);
};

/** WCAG contrast ratio between two colours (1 to 21). */
export const contrastRatio = (a: string, b: string): number => {
	const la = lum(a);
	const lb = lum(b);
	return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
};

/** Of `light` and `dark`, the text colour that reads better on `fill`. */
export const textColorOn = (fill: string, light = '#FFFFFF', dark = '#111111'): string =>
	contrastRatio(fill, light) >= contrastRatio(fill, dark) ? light : dark;

/**
 * Gridline colour: the theme's line colour, softened when the theme draws its rules in full ink (swiss,
 * brutalist), because gridlines sit behind the data.
 */
export const gridOf = (t: Theme): string => (contrastRatio(t.colors.line, t.colors.bg) > 2.2 ? withOpacity(t.colors.line, 0.16) : t.colors.line);

/** The grey a chart uses for everything that is not the story (the bars that are not highlighted). */
export const neutralOf = (t: Theme): string => mixColor(t.colors.faint, t.colors.muted, t.dark ? 0.2 : 0.28);

/**
 * n colours for series or slices from the theme: the two accents first, then tints of them, then greys. With a
 * highlight, the highlighted one gets the accent and the others stepped greys (colour only where the story is).
 */
export const seriesColors = (t: Theme, n: number, highlight?: number): string[] => {
	const c = t.colors;
	if (highlight !== undefined && highlight >= 0 && highlight < n) {
		const base = neutralOf(t);
		let k = 0;
		return Array.from({length: n}, (_, i) => {
			if (i === highlight) {
				return c.accent;
			}
			const step = k++;
			return mixColor(base, c.bg, Math.min(0.55, step * 0.14));
		});
	}
	const pool = [
		c.accent,
		c.accent2,
		mixColor(c.accent, c.bg, 0.45),
		mixColor(c.accent2, c.bg, 0.45),
		mixColor(c.text, c.bg, 0.3),
		mixColor(c.accent, c.text, 0.35),
		mixColor(c.text, c.bg, 0.55),
		mixColor(c.accent2, c.text, 0.35),
	];
	return Array.from({length: n}, (_, i) => (i < pool.length ? pool[i] : mixColor(neutralOf(t), c.bg, ((i - pool.length) % 4) * 0.12)));
};
