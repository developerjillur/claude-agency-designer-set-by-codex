// Beat helpers on top of core's beatGrid and snapToBeat: where the beat is, a pulse that hits on it, and cut
// lists snapped to it. A grid is the list of beat frames: beatGrid(bpm, fps, durationInFrames, offsetSeconds).
import {snapToBeat} from '../core';

export type BeatInfo = {
	/** Index of the last beat at or before the frame (-1 before the first beat). */
	index: number;
	/** Frame of that beat. */
	beatFrame: number;
	/** Frames since that beat. */
	since: number;
	/** 0 to 1 through the current beat. */
	phase: number;
	/** Bar number (0-based) and beat in the bar (0-based), for `beatsPerBar` beats a bar. */
	bar: number;
	beatInBar: number;
};

/** Where `frame` sits on a beat grid. */
export const beatAt = (frame: number, grid: readonly number[], beatsPerBar = 4): BeatInfo => {
	let lo = 0;
	let hi = grid.length - 1;
	let index = -1;
	while (lo <= hi) {
		const mid = (lo + hi) >> 1;
		if (grid[mid] <= frame) {
			index = mid;
			lo = mid + 1;
		} else {
			hi = mid - 1;
		}
	}
	const beatFrame = index >= 0 ? grid[index] : grid[0] ?? 0;
	const next = grid[index + 1];
	const step = next !== undefined && index >= 0 ? next - beatFrame : grid.length > 1 ? grid[1] - grid[0] : 1;
	const since = index >= 0 ? frame - beatFrame : 0;
	return {
		index,
		beatFrame,
		since,
		phase: index >= 0 ? Math.min(1, since / Math.max(1, step)) : 0,
		bar: index >= 0 ? Math.floor(index / beatsPerBar) : -1,
		beatInBar: index >= 0 ? index % beatsPerBar : -1,
	};
};

/**
 * A hit on each beat: 1 on the beat frame, falling to 0 over `decay` frames (ease out, like a drum's envelope).
 * `every` 2 pulses on every second beat, `phase` shifts which beats (0 = the first). Pure, so any frame renders
 * the same.
 */
export const beatPulse = (
	frame: number,
	grid: readonly number[],
	o: {decay?: number; every?: number; phase?: number} = {},
): number => {
	const {decay = 8, every = 1, phase = 0} = o;
	const b = beatAt(frame, grid);
	if (b.index < 0) {
		return 0;
	}
	// the last beat that counts
	let i = b.index;
	while (i >= 0 && (i - phase) % every !== 0) {
		i--;
	}
	if (i < 0) {
		return 0;
	}
	const since = frame - grid[i];
	if (since < 0 || since >= decay) {
		return 0;
	}
	const t = since / decay;
	return (1 - t) * (1 - t);
};

/** Cut frames moved to the nearest beat when one is within `window` frames (core snapToBeat per cut). */
export const snapCuts = (cuts: readonly number[], grid: readonly number[], window = 6): number[] =>
	cuts.map((c) => snapToBeat(c, grid, window));

/** Cut frames every `every` beats starting at beat `first`: a montage that cuts on the music. */
export const beatCuts = (grid: readonly number[], every = 4, first = 0): number[] =>
	grid.filter((_, i) => i >= first && (i - first) % every === 0);
