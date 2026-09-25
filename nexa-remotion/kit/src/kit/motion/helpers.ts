// Pure motion helpers: every value is a function of the frame, so any frame renders the same in any tab.
import {noise2D} from '@remotion/noise';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {curves, springs, type Ease, type SpringName, type SpringSpec} from '../core';

const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** 0 to 1 from `start` over `duration` frames, eased and clamped at both ends. */
export const ramp = (frame: number, start: number, duration: number, ease: Ease = curves.out): number => {
	if (!Number.isFinite(start)) {
		return 0;
	}
	if (duration <= 0) {
		return frame >= start ? 1 : 0;
	}
	return interpolate(frame, [start, start + duration], [0, 1], {...CLAMP, easing: ease});
};

/**
 * A keyframe track: `values` at `frames` (strictly increasing; repeat a value on a later frame to hold), one curve
 * for every segment or one per segment, clamped at both ends.
 */
export const track = (
	frame: number,
	frames: readonly number[],
	values: readonly number[],
	ease: Ease | readonly Ease[] = curves.inOut,
): number => interpolate(frame, frames, values, {...CLAMP, easing: ease});

/** Enter, hold, exit in one value: 0 before `start`, 1 once in, back to 0 by `end`. */
export const inHoldOut = (
	frame: number,
	start: number,
	inFrames: number,
	end: number,
	outFrames: number,
	easeIn: Ease = curves.out,
	easeOut: Ease = curves.in,
): number => Math.min(ramp(frame, start, inFrames, easeIn), 1 - ramp(frame, end - outFrames, outFrames, easeOut));

/** A spring from `delay`, 0 to 1 by default (bouncy configs overshoot). */
export const springAt = (
	frame: number,
	fps: number,
	opts: {delay?: number; config?: SpringName | SpringSpec; durationInFrames?: number; from?: number; to?: number} = {},
): number => {
	const {delay = 0, config = 'calm', durationInFrames, from = 0, to = 1} = opts;
	return spring({
		frame,
		fps,
		delay,
		config: typeof config === 'string' ? springs[config] : config,
		durationInFrames,
		from,
		to,
	});
};

export const stagger = (index: number, each: number, start = 0): number => start + index * each;

/** The frame held for `step` frames: motion "on twos" (2) or threes, the hand-animated feel. */
export const onTwos = (frame: number, step = 2): number => Math.floor(frame / step) * step;

export const loop = (frame: number, period: number): number => ((frame % period) + period) % period;

/** 0 to 1 and back over 2 * `period` frames, forever. */
export const pingPong = (frame: number, period: number): number => {
	const t = loop(frame, 2 * period) / period;
	return t <= 1 ? t : 2 - t;
};

/** A bounded pulse: 0 to 1 and back to 0 over `duration` frames from `start` (half a sine), 0 outside. */
export const pulse = (frame: number, start: number, duration: number): number => {
	const t = (frame - start) / duration;
	return t <= 0 || t >= 1 ? 0 : Math.sin(Math.PI * t);
};

/**
 * Seeded smooth wobble in about [-1, 1] at `freq` cycles a second (0.3 to 0.6 reads alive, not nervous). Use one
 * seed and different lanes for different values (the noise package only caches a few seeds).
 */
export const wiggle = (frame: number, fps: number, freq = 0.5, lane = 0, seed = 'kit'): number =>
	noise2D(seed, (frame / fps) * freq, lane * 7.31);

/** A damped oscillation after `from` (an impact, a landing): `amp`, `freq` in Hz, `decay` per second. */
export const inertia = (frame: number, from: number, fps: number, amp = 1, freq = 3, decay = 6): number => {
	if (frame < from) {
		return 0;
	}
	const t = (frame - from) / fps;
	return amp * Math.sin(2 * Math.PI * freq * t) * Math.exp(-decay * t);
};

/** Frames for a move of `distance` px, scaled from a base move by the square root of the distance ratio. */
export const moveFrames = (distance: number, baseDistance = 200, baseFrames = 16): number =>
	Math.max(4, Math.round(baseFrames * Math.sqrt(Math.max(1, distance) / baseDistance)));

export type Life = {enter: number; exit: number; visible: number; frame: number; length: number};

/**
 * The life of the enclosing Sequence: `enter` goes 0 to 1 over the first `inFrames`, `exit` 0 to 1 over the last
 * `outFrames` (ending on its last frame), `visible` is enter minus exit. For components that build their own
 * entrance and exit instead of wrapping in <Animate>.
 */
export const useLife = (
	inFrames = 15,
	outFrames = 12,
	easeIn: Ease = curves.out,
	easeOut: Ease = curves.in,
): Life => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const enter = ramp(frame, 0, inFrames, easeIn);
	const exit = Number.isFinite(durationInFrames) && outFrames > 0 ? ramp(frame, durationInFrames - 1 - outFrames, outFrames, easeOut) : 0;
	return {enter, exit, visible: Math.max(0, enter - exit), frame, length: durationInFrames};
};

/**
 * The frame (fractional) at which `ramp(frame, start, duration, ease)` reaches `target` (0 to 1): time a label to the
 * moment a line or an eased move gets there. Binary search; assumes a curve that rises overall. Round it for cues.
 */
export const frameAtProgress = (target: number, start: number, duration: number, ease: Ease = curves.out): number => {
	if (target <= 0) {
		return start;
	}
	if (target >= 1 || duration <= 0) {
		return start + Math.max(0, duration);
	}
	let lo = 0;
	let hi = 1;
	for (let i = 0; i < 28; i++) {
		const mid = (lo + hi) / 2;
		if (ease(mid) < target) {
			lo = mid;
		} else {
			hi = mid;
		}
	}
	return start + hi * duration;
};
