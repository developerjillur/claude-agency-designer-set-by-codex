// Small shared helpers for the fx module: number guards, colour mixing, seeded steps and unique ids.
import {createContext, useContext, useId} from 'react';
import {random} from 'remotion';

/** A finite number, or the fallback (effect factories throw on NaN and Infinity). */
export const finite = (v: number | undefined, fallback: number): number =>
	typeof v === 'number' && Number.isFinite(v) ? v : fallback;

export const clampTo = (v: number | undefined, lo: number, hi: number, fallback: number): number =>
	Math.min(hi, Math.max(lo, finite(v, fallback)));

export const unit01 = (v: number | undefined, fallback: number): number => clampTo(v, 0, 1, fallback);

export const nonNegative = (v: number | undefined, fallback: number): number => Math.max(0, finite(v, fallback));

/** Wraps an angle into [0, 360] (lightLeak's hueShift throws outside it). */
export const wrap360 = (deg: number): number => ((finite(deg, 0) % 360) + 360) % 360;

export type Uv = readonly [number, number];

export const uv01 = (p: Uv | undefined, fallback: Uv = [0.5, 0.5]): [number, number] => [
	unit01(p?.[0], fallback[0]),
	unit01(p?.[1], fallback[1]),
];

/**
 * A seed that changes `hz` times a second. Grain re-rolled on every frame reads as electronic sizzle and bloats
 * the encode; 12 Hz reads as film (and 24 Hz as a busy video camera).
 */
export const stepSeed = (frame: number, fps: number, hz = 12): number =>
	Math.floor((finite(frame, 0) * Math.max(0.1, hz)) / Math.max(1, fps));

const hex = (c: string): [number, number, number] | null => {
	const m = c.trim().match(/^#([0-9a-f]{3}|[0-9a-f]{6})([0-9a-f]{2})?$/i);
	if (!m) {
		return null;
	}
	const h = m[1].length === 3 ? m[1].split('').map((x) => x + x).join('') : m[1];
	return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
};

const toHex = (rgb: readonly number[]): string =>
	`#${rgb.map((v) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, '0')).join('')}`;

/** Mixes two hex colours (t = 0 gives a, 1 gives b). Non-hex input returns `a` unchanged. */
export const mixHex = (a: string, b: string, t: number): string => {
	const x = hex(a);
	const y = hex(b);
	if (!x || !y) {
		return a;
	}
	const k = Math.min(1, Math.max(0, t));
	return toHex(x.map((v, i) => v + (y[i] - v) * k));
};

/** `#rrggbb` for any 3 or 6 digit hex (the dissolve shader transition only accepts 6 digits). */
export const hex6 = (c: string, fallback = '#ffffff'): string => {
	const x = hex(c);
	return x ? toHex(x) : fallback;
};

/** rgba() from a hex colour and an alpha. */
export const rgba = (c: string, alpha: number): string => {
	const x = hex(c);
	const a = Math.min(1, Math.max(0, alpha));
	return x ? `rgba(${x[0]}, ${x[1]}, ${x[2]}, ${a})` : c;
};

/** Seeded number in [0, 1). */
export const r01 = (seed: string | number): number => random(seed);

/** A DOM id that is unique per instance and safe inside CSS url(#...). */
export const useSafeId = (prefix: string): string => `${prefix}-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`;

/**
 * Where a component sits, for choosing an engine: HTML-in-canvas cannot be nested, and a scene next to a shader
 * transition is already inside an HTML-in-canvas subtree. `canvas` holds the reason, or null when free.
 */
export type FxNest = {canvas: string | null};

export const FxNestContext = createContext<FxNest>({canvas: null});

export const useFxNest = (): FxNest => useContext(FxNestContext);
