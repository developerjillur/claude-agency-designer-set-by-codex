// Colour helpers for maps (mixing in OKLab so ramps look even) and the map palette each theme gets.
// Core has no colour maths yet, so this lives here; it could move to core if other modules need it.
import type {Theme} from '../core';

export type RGBA = [number, number, number, number];

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** Parses #rgb, #rrggbb, #rrggbbaa, rgb() and rgba(); null for anything else (names, CSS variables). */
export const parseColor = (c: string): RGBA | null => {
	const s = c.trim();
	if (s.startsWith('#')) {
		const h = s.slice(1);
		const full =
			h.length === 3 || h.length === 4
				? h
						.split('')
						.map((x) => x + x)
						.join('')
				: h;
		if (!/^[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$/.test(full)) {
			return null;
		}
		const n = (i: number) => parseInt(full.slice(i, i + 2), 16);
		return [n(0), n(2), n(4), full.length === 8 ? n(6) / 255 : 1];
	}
	const m = s.match(/^rgba?\(([^)]+)\)$/i);
	if (m) {
		const parts = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
		if (parts.length >= 3 && parts.slice(0, 3).every(Number.isFinite)) {
			return [parts[0], parts[1], parts[2], parts.length > 3 && Number.isFinite(parts[3]) ? parts[3] : 1];
		}
	}
	return null;
};

const hex2 = (v: number) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, '0');

export const toCss = ([r, g, b, a]: RGBA): string =>
	a >= 0.999 ? `#${hex2(r)}${hex2(g)}${hex2(b)}` : `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${+a.toFixed(3)})`;

const toLinear = (v: number) => {
	const c = v / 255;
	return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};
const fromLinear = (v: number) => {
	const c = v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055;
	return clamp01(c) * 255;
};

type Lab = [number, number, number];

const rgbToOklab = ([r8, g8, b8]: RGBA): Lab => {
	const r = toLinear(r8);
	const g = toLinear(g8);
	const b = toLinear(b8);
	const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
	const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
	const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
	return [
		0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
		1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
		0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
	];
};

const oklabToRgb = ([L, A, B]: Lab, alpha: number): RGBA => {
	const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3;
	const m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3;
	const s = (L - 0.0894841775 * A - 1.291485548 * B) ** 3;
	return [
		fromLinear(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
		fromLinear(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
		fromLinear(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
		alpha,
	];
};

/** a to b by t (0 to 1), mixed in OKLab (even steps, no muddy middles). Unparseable input returns a or b. */
export const mix = (a: string, b: string, t: number): string => {
	const ca = parseColor(a);
	const cb = parseColor(b);
	if (!ca || !cb) {
		return t < 0.5 ? a : b;
	}
	const k = clamp01(t);
	const la = rgbToOklab(ca);
	const lb = rgbToOklab(cb);
	const lab: Lab = [la[0] + (lb[0] - la[0]) * k, la[1] + (lb[1] - la[1]) * k, la[2] + (lb[2] - la[2]) * k];
	return toCss(oklabToRgb(lab, ca[3] + (cb[3] - ca[3]) * k));
};

/** The colour at opacity `a` (0 to 1) as rgba(). */
export const withAlpha = (c: string, a: number): string => {
	const p = parseColor(c);
	return p ? toCss([p[0], p[1], p[2], clamp01(a) * p[3]]) : c;
};

/** Relative luminance (0 black to 1 white). */
export const luminance = (c: string): number => {
	const p = parseColor(c);
	if (!p) {
		return 0.5;
	}
	return 0.2126 * toLinear(p[0]) + 0.7152 * toLinear(p[1]) + 0.0722 * toLinear(p[2]);
};

/** WCAG contrast ratio of two colours (1 to 21). */
export const contrast = (a: string, b: string): number => {
	const la = luminance(a);
	const lb = luminance(b);
	return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
};

/** `n` colours evenly from the first stop to the last through the middle ones, mixed in OKLab. */
export const ramp = (stops: readonly string[], n: number): string[] => {
	if (n <= 1) {
		return [stops[stops.length - 1]];
	}
	const out: string[] = [];
	for (let i = 0; i < n; i++) {
		const t = (i / (n - 1)) * (stops.length - 1);
		const j = Math.min(stops.length - 2, Math.floor(t));
		out.push(mix(stops[j], stops[j + 1], t - j));
	}
	return out;
};

/** Of the candidates, the colour that reads best on `fill` (highest contrast). */
export const textOn = (fill: string, candidates: readonly string[]): string =>
	candidates.reduce((best, c) => (contrast(fill, c) > contrast(fill, best) ? c : best), candidates[0]);

/** The outline that goes with a highlight fill: lighter on dark themes, darker on light ones. */
export const lineFor = (fill: string, dark: boolean): string => (dark ? mix(fill, '#FFFFFF', 0.4) : mix(fill, '#000000', 0.3));

export type MapPalette = {
	stage: string; // the frame around the world (outside the sphere)
	ocean: string;
	land: string;
	border: string; // lines between countries
	coast: string;
	graticule: string;
	sphere: string; // outline of the world shape
	label: string; // country names on land
	labelMuted: string;
	halo: string; // outline behind label text so it reads over borders
	highlight: string[]; // highlight colours in order
	highlightLine: string; // outline of a highlighted country
	pin: string;
	pinRing: string;
	route: string;
	plane: string;
	tagBg: string; // label pills
	tagText: string;
	tagMuted: string;
	ramp: [string, string, string]; // choropleth: low, middle, high
	dark: boolean;
};

/**
 * The map colours for a theme. Land is a quiet tint of the ground, countries are cut apart by lines of the
 * ground colour, the accent is saved for what the story is about. Any value can be overridden.
 */
export const mapPalette = (t: Theme, o: Partial<MapPalette> = {}): MapPalette => {
	const c = t.colors;
	const dark = t.dark;
	const white = '#FFFFFF';
	const black = '#000000';
	const land = dark ? mix(c.bg, c.text, 0.2) : mix(c.bg, c.text, 0.17);
	const ocean = dark ? mix(c.bg, c.accent, 0.06) : mix(c.bg, white, 0.6);
	const stage = c.bg;
	const accent = c.accent;
	const highlightLine = lineFor(accent, dark);
	return {
		stage,
		ocean,
		land,
		border: dark ? mix(c.bg, black, 0.2) : mix(ocean, white, 0.6),
		coast: dark ? mix(land, c.text, 0.12) : mix(land, c.text, 0.1),
		graticule: dark ? mix(ocean, c.text, 0.07) : mix(ocean, c.text, 0.06),
		sphere: dark ? mix(ocean, c.text, 0.12) : mix(ocean, c.text, 0.1),
		label: c.text,
		labelMuted: dark ? mix(c.muted, c.text, 0.1) : mix(c.muted, c.text, 0.15),
		halo: land,
		highlight: [accent, c.accent2, mix(accent, c.accent2, 0.5), c.positive, c.negative],
		highlightLine,
		pin: c.accent2 === c.accent ? c.negative : c.accent2,
		pinRing: dark ? c.bg : white,
		route: accent,
		plane: c.text,
		tagBg: c.surface,
		tagText: c.text,
		tagMuted: c.muted,
		ramp: dark
			? [mix(land, accent, 0.22), accent, mix(accent, white, 0.5)]
			: [mix(mix(land, white, 0.4), accent, 0.14), accent, mix(accent, black, 0.3)],
		dark,
		...o,
	};
};
