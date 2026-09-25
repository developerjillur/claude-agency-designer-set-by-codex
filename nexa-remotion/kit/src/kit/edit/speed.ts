// Speed over time. Remotion renders frames independently, so a speed that changes cannot be a changing
// playbackRate: the source position at an output frame is the sum of every speed before it. These helpers build
// that table once (per render tab) and look it up.
import {interpolate} from 'remotion';
import {curves, type Ease} from '../core';

/** Speed at an output frame: 1 = normal, 2 = twice as fast, 0.25 = slow motion, 0 = hold. */
export type SpeedKey = {at: number; speed: number};

const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const sortKeys = (keys: readonly SpeedKey[]) => [...keys].sort((a, b) => a.at - b.at);

/** The speed at `frame`, eased between keys (in-out by default: speed changes feel like a camera operator's hand). */
export const speedAt = (frame: number, keys: readonly SpeedKey[], ease: Ease = curves.inOut): number => {
	if (keys.length === 0) {
		return 1;
	}
	const k = sortKeys(keys);
	if (k.length === 1) {
		return Math.max(0, k[0].speed);
	}
	// repeated `at` values would break interpolate(): nudge them apart
	const at = k.map((x, i) => x.at + i * 1e-6);
	return Math.max(0, interpolate(frame, at, k.map((x) => x.speed), {...CLAMP, easing: ease}));
};

/**
 * Source position (frames, fractional) at each output frame 0..`frames`: `start` plus the speed integrated up to
 * that frame (midpoint rule, so a ramp from 1 to 3 lands where the maths says).
 */
export const rampPositions = (
	keys: readonly SpeedKey[],
	frames: number,
	start = 0,
	ease: Ease = curves.inOut,
): Float64Array => {
	const n = Math.max(1, Math.ceil(frames) + 1);
	const pos = new Float64Array(n);
	let s = start;
	for (let t = 0; t < n; t++) {
		pos[t] = s;
		s += speedAt(t + 0.5, keys, ease);
	}
	return pos;
};

/** Output frames a ramp needs to play `sourceFrames` of footage (from `start`), capped at `max`. */
export const rampLength = (
	keys: readonly SpeedKey[],
	sourceFrames: number,
	start = 0,
	ease: Ease = curves.inOut,
	max = 36000,
): number => {
	let s = start;
	for (let t = 0; t < max; t++) {
		if (s >= start + sourceFrames) {
			return t;
		}
		s += speedAt(t + 0.5, keys, ease);
	}
	return max;
};
