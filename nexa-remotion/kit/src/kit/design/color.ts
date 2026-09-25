// Colour helpers: parse any CSS colour the kit uses, mix in OKLab (no muddy midpoints), measure WCAG contrast,
// pick readable text and push a colour until it is readable. Pure functions: safe in render.

export type RGBA = {r: number; g: number; b: number; a: number}; // 0 to 1 each, sRGB
export type Oklab = {l: number; a: number; b: number; alpha: number};
export type Oklch = {l: number; c: number; h: number; alpha: number}; // h in degrees

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const NAMED: Record<string, string> = {
	transparent: '#00000000',
	white: '#ffffff',
	black: '#000000',
	red: '#ff0000',
	green: '#008000',
	blue: '#0000ff',
	yellow: '#ffff00',
	orange: '#ffa500',
	gray: '#808080',
	grey: '#808080',
};

const num = (s: string, scale: number): number => {
	const t = s.trim();
	if (t.endsWith('%')) {
		return (parseFloat(t) / 100) * scale;
	}
	return parseFloat(t);
};

const hslToRgb = (h: number, s: number, l: number): [number, number, number] => {
	const k = (n: number) => (n + h / 30) % 12;
	const a = s * Math.min(l, 1 - l);
	const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
	return [f(0), f(8), f(4)];
};

// The browser's own parser, for anything the fast paths do not know (named colours, color(), lab()).
let probe: CanvasRenderingContext2D | null | undefined;
const browserParse = (c: string): RGBA | null => {
	if (typeof document === 'undefined') {
		return null;
	}
	if (probe === undefined) {
		probe = document.createElement('canvas').getContext('2d');
	}
	if (!probe) {
		return null;
	}
	probe.fillStyle = '#010203';
	probe.fillStyle = c;
	const out = String(probe.fillStyle);
	if (out === '#010203' && c.trim().toLowerCase() !== '#010203') {
		return null;
	}
	return out.startsWith('#') ? parseHex(out) : parseFunc(out);
};

const parseHex = (c: string): RGBA | null => {
	let h = c.slice(1);
	if (h.length === 3 || h.length === 4) {
		h = h
			.split('')
			.map((ch) => ch + ch)
			.join('');
	}
	if (h.length !== 6 && h.length !== 8) {
		return null;
	}
	const v = parseInt(h, 16);
	if (Number.isNaN(v)) {
		return null;
	}
	const has = h.length === 8;
	const r = parseInt(h.slice(0, 2), 16) / 255;
	const g = parseInt(h.slice(2, 4), 16) / 255;
	const b = parseInt(h.slice(4, 6), 16) / 255;
	const a = has ? parseInt(h.slice(6, 8), 16) / 255 : 1;
	return {r, g, b, a};
};

const parseFunc = (c: string): RGBA | null => {
	const m = /^([a-z]+)\(([^)]*)\)$/i.exec(c.trim());
	if (!m) {
		return null;
	}
	const fn = m[1].toLowerCase();
	const [main, alphaPart] = m[2].includes('/') ? m[2].split('/') : [m[2], undefined];
	const parts = main.split(/[\s,]+/).filter(Boolean);
	let alpha = alphaPart !== undefined ? num(alphaPart, 1) : parts.length === 4 ? num(parts[3], 1) : 1;
	if (!Number.isFinite(alpha)) {
		alpha = 1;
	}
	if (fn === 'rgb' || fn === 'rgba') {
		return {r: num(parts[0], 255) / 255, g: num(parts[1], 255) / 255, b: num(parts[2], 255) / 255, a: clamp01(alpha)};
	}
	if (fn === 'hsl' || fn === 'hsla') {
		const [r, g, b] = hslToRgb(parseFloat(parts[0]), num(parts[1], 1) / (parts[1].endsWith('%') ? 1 : 100), num(parts[2], 1) / (parts[2].endsWith('%') ? 1 : 100));
		return {r, g, b, a: clamp01(alpha)};
	}
	if (fn === 'oklch') {
		const l = parts[0].endsWith('%') ? parseFloat(parts[0]) / 100 : parseFloat(parts[0]);
		return oklchToRgba({l, c: num(parts[1], 0.4), h: parseFloat(parts[2]) || 0, alpha: clamp01(alpha)});
	}
	if (fn === 'oklab') {
		const l = parts[0].endsWith('%') ? parseFloat(parts[0]) / 100 : parseFloat(parts[0]);
		return oklabToRgba({l, a: num(parts[1], 0.4), b: num(parts[2], 0.4), alpha: clamp01(alpha)});
	}
	return null;
};

const cache = new Map<string, RGBA>();

/** Any CSS colour the kit meets (hex, rgb, hsl, oklch, oklab, names) as sRGB 0 to 1. Unknown input gives black. */
export const parseColor = (c: string): RGBA => {
	const key = c.trim().toLowerCase();
	const hit = cache.get(key);
	if (hit) {
		return hit;
	}
	const named = NAMED[key];
	const out = (key.startsWith('#') ? parseHex(key) : named ? parseHex(named) : parseFunc(key)) ?? browserParse(c) ?? {r: 0, g: 0, b: 0, a: 1};
	cache.set(key, out);
	return out;
};

const hex2 = (v: number) =>
	Math.round(clamp01(v) * 255)
		.toString(16)
		.padStart(2, '0');

/** #rrggbb, or #rrggbbaa when the colour is not opaque. */
export const toHex = (c: string | RGBA): string => {
	const x = typeof c === 'string' ? parseColor(c) : c;
	return `#${hex2(x.r)}${hex2(x.g)}${hex2(x.b)}${x.a < 0.999 ? hex2(x.a) : ''}`;
};

/** The colour with a new alpha (0 to 1), as rgba(). */
export const withAlpha = (c: string, alpha: number): string => {
	const x = parseColor(c);
	return `rgba(${Math.round(x.r * 255)}, ${Math.round(x.g * 255)}, ${Math.round(x.b * 255)}, ${Math.round(clamp01(alpha * x.a) * 1000) / 1000})`;
};

// ---------------------------------------------------------------- OKLab (Ottosson)

const toLinear = (v: number) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
const toGamma = (v: number) => (v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055);

export const rgbaToOklab = (x: RGBA): Oklab => {
	const r = toLinear(x.r);
	const g = toLinear(x.g);
	const b = toLinear(x.b);
	const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
	const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
	const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
	return {
		l: 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
		a: 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
		b: 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
		alpha: x.a,
	};
};

const oklabToLinear = (o: Oklab): [number, number, number] => {
	const l = (o.l + 0.3963377774 * o.a + 0.2158037573 * o.b) ** 3;
	const m = (o.l - 0.1055613458 * o.a - 0.0638541728 * o.b) ** 3;
	const s = (o.l - 0.0894841775 * o.a - 1.291485548 * o.b) ** 3;
	return [
		4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
		-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
		-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
	];
};

const inGamut = ([r, g, b]: [number, number, number]) => r >= -1e-4 && r <= 1.0001 && g >= -1e-4 && g <= 1.0001 && b >= -1e-4 && b <= 1.0001;

/** OKLab to sRGB; out-of-gamut colours keep their lightness and hue and lose chroma until they fit. */
export const oklabToRgba = (o: Oklab): RGBA => {
	let lin = oklabToLinear(o);
	if (!inGamut(lin)) {
		const c = Math.hypot(o.a, o.b);
		const h = Math.atan2(o.b, o.a);
		let lo = 0;
		let hi = c;
		for (let i = 0; i < 24; i++) {
			const mid = (lo + hi) / 2;
			if (inGamut(oklabToLinear({l: o.l, a: mid * Math.cos(h), b: mid * Math.sin(h), alpha: 1}))) {
				lo = mid;
			} else {
				hi = mid;
			}
		}
		lin = oklabToLinear({l: o.l, a: lo * Math.cos(h), b: lo * Math.sin(h), alpha: 1});
	}
	return {r: clamp01(toGamma(clamp01(lin[0]))), g: clamp01(toGamma(clamp01(lin[1]))), b: clamp01(toGamma(clamp01(lin[2]))), a: o.alpha};
};

export const toOklch = (c: string): Oklch => {
	const o = rgbaToOklab(parseColor(c));
	const h = (Math.atan2(o.b, o.a) * 180) / Math.PI;
	return {l: o.l, c: Math.hypot(o.a, o.b), h: h < 0 ? h + 360 : h, alpha: o.alpha};
};

export const oklchToRgba = (x: Oklch): RGBA => {
	const hr = (x.h * Math.PI) / 180;
	return oklabToRgba({l: x.l, a: x.c * Math.cos(hr), b: x.c * Math.sin(hr), alpha: x.alpha});
};

/** A hex colour from OKLCH (lightness 0 to 1, chroma about 0 to 0.37, hue in degrees), fitted into sRGB. */
export const oklch = (l: number, c: number, h: number, alpha = 1): string => toHex(oklchToRgba({l: clamp01(l), c: Math.max(0, c), h, alpha}));

/** Mix two colours in OKLab: t = 0 gives a, 1 gives b. Midpoints stay clean (no grey dip as in sRGB). */
export const mix = (a: string, b: string, t: number): string => {
	const k = clamp01(t);
	const x = rgbaToOklab(parseColor(a));
	const y = rgbaToOklab(parseColor(b));
	return toHex(
		oklabToRgba({
			l: x.l + (y.l - x.l) * k,
			a: x.a + (y.a - x.a) * k,
			b: x.b + (y.b - x.b) * k,
			alpha: x.alpha + (y.alpha - x.alpha) * k,
		}),
	);
};

/** Lightness moved by `amount` (OKLab L, 0 to 1 scale; 0.05 is a visible step): hue and chroma kept. */
export const lighten = (c: string, amount: number): string => {
	const o = rgbaToOklab(parseColor(c));
	return toHex(oklabToRgba({...o, l: clamp01(o.l + amount)}));
};
export const darken = (c: string, amount: number): string => lighten(c, -amount);

/** Chroma scaled (0 greys it out, 1 keeps it, above 1 saturates within sRGB). */
export const saturate = (c: string, factor: number): string => {
	const o = rgbaToOklab(parseColor(c));
	return toHex(oklabToRgba({...o, a: o.a * factor, b: o.b * factor}));
};

// ---------------------------------------------------------------- WCAG contrast

/** WCAG relative luminance (0 black to 1 white). A translucent colour is first laid over `over` (default white). */
export const luminance = (c: string, over = '#ffffff'): number => {
	let x = parseColor(c);
	if (x.a < 0.999) {
		const u = parseColor(over);
		x = {r: x.r * x.a + u.r * (1 - x.a), g: x.g * x.a + u.g * (1 - x.a), b: x.b * x.a + u.b * (1 - x.a), a: 1};
	}
	return 0.2126 * toLinear(x.r) + 0.7152 * toLinear(x.g) + 0.0722 * toLinear(x.b);
};

/** WCAG contrast ratio of two colours, 1 to 21. A translucent foreground is laid over the background first. */
export const contrast = (fg: string, bg: string): number => {
	const lb = luminance(bg);
	const lf = luminance(fg, bg);
	const [hi, lo] = lf > lb ? [lf, lb] : [lb, lf];
	return (hi + 0.05) / (lo + 0.05);
};

/**
 * Whether text of this colour reads on that ground: AA needs 4.5 for body text and 3 for large text (about 40 px
 * and up at 1080p in video); AAA needs 7 and 4.5. Video is watched small and compressed: aim above the minimum.
 */
export const isReadable = (fg: string, bg: string, level: 'AA' | 'AAA' = 'AA', large = false): boolean =>
	contrast(fg, bg) >= (level === 'AAA' ? (large ? 4.5 : 7) : large ? 3 : 4.5);

/** The better of two text colours on a ground (default white or near-black): for labels on any fill. */
export const readableOn = (bg: string, light = '#FFFFFF', dark = '#111111'): string =>
	contrast(light, bg) >= contrast(dark, bg) ? light : dark;

/**
 * The colour moved in lightness (hue kept) until it reaches `min` contrast on the ground: the AA-safe darker
 * accent for small text on a light ground, or the lighter one on a dark ground.
 */
export const ensureContrast = (fg: string, bg: string, min = 4.5): string => {
	if (contrast(fg, bg) >= min) {
		return toHex(fg);
	}
	const o = rgbaToOklab(parseColor(fg));
	const towardsDark = luminance(bg) > 0.18;
	let lo = towardsDark ? 0 : o.l;
	let hi = towardsDark ? o.l : 1;
	const at = (l: number) => toHex(oklabToRgba({...o, l, alpha: 1}));
	// the best reachable end first: if even black or white fails, return it
	const end = at(towardsDark ? 0 : 1);
	if (contrast(end, bg) < min) {
		return end;
	}
	for (let i = 0; i < 22; i++) {
		const mid = (lo + hi) / 2;
		const ok = contrast(at(mid), bg) >= min;
		if (towardsDark) {
			if (ok) {
				lo = mid;
			} else {
				hi = mid;
			}
		} else if (ok) {
			hi = mid;
		} else {
			lo = mid;
		}
	}
	return at(towardsDark ? lo : hi);
};

/** Whether a colour reads as dark (a ground that wants light text). */
export const isDark = (c: string): boolean => luminance(c) < 0.18;

/** A shadow colour for a ground: the ground's own hue, very dark, so shadows look lit rather than grey. */
export const shadowTint = (ground: string): string => {
	const x = toOklch(ground);
	return oklch(0.18, Math.min(0.06, x.c * 1.6), x.h);
};
