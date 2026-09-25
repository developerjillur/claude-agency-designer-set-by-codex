// Gain maths for sound: fades, ducking, keyframed volume curves and dB conversion. All pure functions of the
// frame, so a `volume` callback built from them is the same in every render tab.
import {interpolate} from 'remotion';
import {curves, type Ease} from '../core';

/** A time window [start, end] in frames (end exclusive), for example where the voice speaks. */
export type TimeWindow = readonly [start: number, end: number];

const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** dB to a linear gain: 0 dB = 1, -6 dB = 0.5, -20 dB = 0.1. */
export const dbToGain = (db: number): number => Math.pow(10, db / 20);

/** A linear gain to dB (-Infinity for 0). */
export const gainToDb = (gain: number): number => (gain > 0 ? 20 * Math.log10(gain) : -Infinity);

/**
 * A gain Remotion accepts: NaN and infinities become 0, negatives 0, and the top is capped (default 4, +12 dB).
 * Remotion throws on a non-finite callback result and on a gain of 100 or more.
 */
export const safeGain = (gain: number, max = 4): number => (Number.isFinite(gain) ? Math.min(max, Math.max(0, gain)) : 0);

/**
 * Fade-in over the first `fadeIn` frames and fade-out over the last `fadeOut` frames of something `length`
 * frames long, as a 0 to 1 factor. Volume is applied once per frame, so the steps are spread evenly: frame 0 is
 * already at 1 / (fadeIn + 1) and the last frame at 1 / (fadeOut + 1), never a silent frame at either end.
 */
export const fadeGain = (f: number, length: number, fadeIn = 0, fadeOut = 0): number => {
	let g = 1;
	if (fadeIn > 0) {
		g = Math.min(g, (f + 1) / (fadeIn + 1));
	}
	if (fadeOut > 0 && Number.isFinite(length)) {
		g = Math.min(g, (length - f) / (fadeOut + 1));
	}
	return Math.min(1, Math.max(0, g));
};

/**
 * A volume curve from keyframes, clamped on both sides (so it never keeps climbing after the last key) and made
 * safe: pass the result straight to `volume`. `frames` are frames since the media started. Non-finite gains count
 * as 0 and repeated frames are nudged apart (interpolate() throws on both).
 */
export const volumeCurve = (frames: readonly number[], gains: readonly number[], ease: Ease = curves.inOut) => {
	const n = Math.min(frames.length, gains.length);
	const fs = frames.slice(0, n).map((x, i) => x + i * 1e-6);
	const gs = gains.slice(0, n).map((g) => (Number.isFinite(g) ? g : 0));
	return (f: number): number => safeGain(n < 2 ? gs[0] ?? 1 : interpolate(f, fs, gs, {...CLAMP, easing: ease}));
};

export type DuckOptions = {
	/** Gain while nobody speaks. */
	level?: number;
	/** Gain under the voice. 0.04 to 0.1 for a mastered track under a normalised voice. */
	duckTo?: number;
	/** Frames of the ramp down; it ends when the voice starts, so the first word is never fighting the music. */
	attack?: number;
	/** Frames of the ramp back up after the voice (and the hold). */
	release?: number;
	/** Frames to stay down after a window ends, so the tail of the last word is clear. */
	hold?: number;
	/**
	 * Pauses shorter than this many frames keep the bed down (default attack + hold + release): a bed that swells
	 * for one second between two sentences pumps. Longer gaps get a real swell.
	 */
	bridge?: number;
};

/** Voice windows with short pauses bridged: sorted, and merged when the gap is under `bridge` frames. */
export const bridgeWindows = (windows: readonly TimeWindow[], bridge: number): TimeWindow[] => {
	const sorted = windows.filter(([s, e]) => e > s).map(([s, e]) => [s, e] as [number, number]).sort((a, b) => a[0] - b[0]);
	const out: [number, number][] = [];
	for (const w of sorted) {
		const last = out[out.length - 1];
		if (last && w[0] - last[1] < bridge) {
			last[1] = Math.max(last[1], w[1]);
		} else {
			out.push(w);
		}
	}
	return out;
};

const smooth = (t: number) => t * t * (3 - 2 * t);

/** How far down a bed is at frame `f` (0 = at `level`, 1 = at `duckTo`) for these voice windows. */
export const duckDepth = (f: number, windows: readonly TimeWindow[], o: DuckOptions = {}): number => {
	const {attack = 30, release = 30, hold = 8} = o;
	const bridge = o.bridge ?? attack + hold + release;
	let d = 0;
	for (const [s, e] of bridge > 0 ? bridgeWindows(windows, bridge) : windows) {
		if (!(e > s)) {
			continue;
		}
		let w: number;
		if (f < s - attack) {
			w = 0;
		} else if (f < s) {
			w = attack > 0 ? smooth((f - (s - attack)) / attack) : 1;
		} else if (f <= e + hold) {
			w = 1;
		} else if (f < e + hold + release) {
			w = 1 - smooth((f - e - hold) / release);
		} else {
			w = 0;
		}
		d = Math.max(d, w);
		if (d >= 1) {
			break;
		}
	}
	return d;
};

/**
 * The gain of a bed ducked under voice windows. Ramps move in dB (even to the ear), so half way down in time is
 * half way down in loudness. Pauses shorter than `bridge` keep the bed down; overlapping ramps merge smoothly.
 */
export const duckGain = (f: number, windows: readonly TimeWindow[], o: DuckOptions = {}): number => {
	const {level = 0.5, duckTo = 0.06} = o;
	const d = duckDepth(f, windows, o);
	if (d <= 0) {
		return level;
	}
	if (level > 0 && duckTo > 0) {
		return level * Math.pow(duckTo / level, d);
	}
	return level + (duckTo - level) * d;
};

export type MusicGainOptions = DuckOptions & {
	/** Frames the music plays (for the fade-out). */
	length?: number;
	fadeIn?: number;
	fadeOut?: number;
	/** Voice windows, in frames since the music started. */
	windows?: readonly TimeWindow[];
};

/** The full music-bed gain at frame `f` since the music started: fades times ducking, made safe. */
export const musicGain = (f: number, o: MusicGainOptions = {}): number => {
	const {length = Infinity, fadeIn = 30, fadeOut = 60, windows = []} = o;
	return safeGain(fadeGain(f, length, fadeIn, fadeOut) * duckGain(f, windows, o));
};

/**
 * Voice windows (frames) from word timings in milliseconds (a `Caption[]` from @remotion/captions works):
 * words closer than `gap` seconds merge into one window, each window padded by `pad` seconds, and shifted by
 * `offset` frames (where the voice starts on the timeline the windows are used on).
 */
export const speechWindows = (
	words: readonly {startMs: number; endMs: number}[],
	fps: number,
	o: {gap?: number; pad?: number; offset?: number} = {},
): TimeWindow[] => {
	const {gap = 0.5, pad = 0.05, offset = 0} = o;
	const sorted = [...words].filter((w) => w.endMs > w.startMs).sort((a, b) => a.startMs - b.startMs);
	const merged: [number, number][] = [];
	for (const w of sorted) {
		const s = w.startMs / 1000;
		const e = w.endMs / 1000;
		const last = merged[merged.length - 1];
		if (last && s - last[1] < gap) {
			last[1] = Math.max(last[1], e);
		} else {
			merged.push([s, e]);
		}
	}
	return merged.map(([s, e]) => [Math.round((s - pad) * fps) + offset, Math.round((e + pad) * fps) + offset] as const);
};
