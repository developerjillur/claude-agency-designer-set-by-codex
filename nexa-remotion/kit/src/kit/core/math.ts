import {random} from 'remotion';

export const clamp = (v: number, lo = 0, hi = 1): number => Math.min(hi, Math.max(lo, v));
export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;
export const invLerp = (a: number, b: number, v: number): number => (b === a ? 0 : (v - a) / (b - a));
export const remap = (v: number, a0: number, a1: number, b0: number, b1: number): number =>
	lerp(b0, b1, invLerp(a0, a1, v));

/** A seeded number in [0, 1): the same seed gives the same number in every frame and every render tab. */
export const rand = (seed: string | number): number => random(seed);

/** A seeded number in [lo, hi). */
export const randBetween = (seed: string | number, lo: number, hi: number): number => lerp(lo, hi, random(seed));

/** A seeded shuffle (Fisher-Yates) that is the same in every frame. */
export const shuffle = <T>(items: readonly T[], seed: string | number): T[] => {
	const out = [...items];
	for (let i = out.length - 1; i > 0; i--) {
		const j = Math.floor(random(`${seed}-${i}`) * (i + 1));
		[out[i], out[j]] = [out[j], out[i]];
	}
	return out;
};
