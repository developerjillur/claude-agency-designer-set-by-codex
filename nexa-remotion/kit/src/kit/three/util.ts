// Small shared helpers for the 3D module: world units, colour maths, vectors and seeded values.
import {noise2D} from '@remotion/noise';

export type Vec3 = [number, number, number];

/**
 * One world unit is 200 px at a 1080 px short side. Scene3D places its camera so the frame's short side is
 * 5.4 units at the target, in every format, so sizes written in "px at 1080" (the kit's unit) convert with
 * `px / PX_PER_UNIT` when the camera sits at its base distance.
 */
export const PX_PER_UNIT = 200;
export const SHORT_SIDE_UNITS = 1080 / PX_PER_UNIT;

export const DEG = Math.PI / 180;
export const deg = (d: number): number => d * DEG;

type RGB = [number, number, number];

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** '#abc', '#aabbcc' or 'rgb(r, g, b)' to [r, g, b] in 0..255. Unknown strings give mid grey. */
export const parseColor = (c: string): RGB => {
	const s = c.trim();
	if (s.startsWith('#')) {
		const h = s.slice(1);
		const full = h.length === 3 ? h.split('').map((x) => x + x).join('') : h.slice(0, 6);
		const n = parseInt(full, 16);
		if (Number.isFinite(n)) {
			return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
		}
	}
	const m = s.match(/rgba?\(([^)]+)\)/i);
	if (m) {
		const [r, g, b] = m[1].split(',').map((x) => parseFloat(x));
		return [r || 0, g || 0, b || 0];
	}
	return [128, 128, 128];
};

const toHex = ([r, g, b]: RGB): string =>
	'#' + [r, g, b].map((v) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, '0')).join('');

/** a to b by t (0..1), in sRGB. */
export const mix = (a: string, b: string, t: number): string => {
	const x = parseColor(a);
	const y = parseColor(b);
	const k = clamp01(t);
	return toHex([x[0] + (y[0] - x[0]) * k, x[1] + (y[1] - x[1]) * k, x[2] + (y[2] - x[2]) * k]);
};

/** Multiplies the brightness: 0.7 darker, 1.2 lighter (towards white above 1). */
export const shade = (c: string, k: number): string => (k <= 1 ? mix('#000000', c, k) : mix(c, '#ffffff', k - 1));

export const withAlpha = (c: string, a: number): string => {
	const [r, g, b] = parseColor(c);
	return `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${clamp01(a)})`;
};

/** Relative luminance (0 black .. 1 white), for picking readable colours. */
export const luminance = (c: string): number => {
	const lin = parseColor(c).map((v) => {
		const s = v / 255;
		return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
	});
	return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
};

/** sRGB colour as 0..1 floats (for shaders that write sRGB straight to the canvas). */
export const rgb01 = (c: string): RGB => parseColor(c).map((v) => v / 255) as RGB;

export const lerp3 = (a: Vec3, b: Vec3, t: number): Vec3 => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];

/** A point on a sphere around `target`: azimuth turns right (degrees), elevation lifts (degrees). */
export const orbitPoint = (target: Vec3, azimuth: number, elevation: number, distance: number): Vec3 => {
	const a = deg(azimuth);
	const e = deg(elevation);
	return [
		target[0] + distance * Math.sin(a) * Math.cos(e),
		target[1] + distance * Math.sin(e),
		target[2] + distance * Math.cos(a) * Math.cos(e),
	];
};

/** Seeded smooth noise in about [-1, 1] for a lane: the same value in every tab for the same time. */
export const noise = (seed: string, t: number, lane: number): number => noise2D(seed, t, lane * 7.31);
