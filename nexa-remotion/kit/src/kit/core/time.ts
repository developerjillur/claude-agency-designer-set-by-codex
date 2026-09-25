// Timing helpers: seconds to frames, beat grids, reading time.

export const toFrames = (seconds: number, fps: number): number => Math.round(seconds * fps);

/** Frames of the beats of a track at `bpm` from `offset` seconds (the first downbeat) up to `durationInFrames`. */
export const beatGrid = (bpm: number, fps: number, durationInFrames: number, offset = 0): number[] => {
	const out: number[] = [];
	// each beat from its own index, so rounding never accumulates into drift
	for (let k = 0; ; k++) {
		const f = Math.round((offset + (k * 60) / bpm) * fps);
		if (f >= durationInFrames) {
			break;
		}
		out.push(f);
	}
	return out;
};

/** The beat nearest to `frame` when it is within `window` frames, else the frame itself. */
export const snapToBeat = (frame: number, grid: readonly number[], window = 6): number => {
	let best = frame;
	let dist = window + 1;
	for (const b of grid) {
		const d = Math.abs(b - frame);
		if (d < dist) {
			best = b;
			dist = d;
		}
	}
	return dist <= window ? best : frame;
};

/**
 * Frames a viewer needs to read `text`: about 0.33 s a word plus 0.3 s, never under 1.2 s, and longer for
 * numbers. Hold text at least this long once it has settled.
 */
export const readingFrames = (text: string, fps: number): number => {
	const words = text.trim().split(/\s+/).filter(Boolean);
	const digits = (text.match(/\d/g) ?? []).length;
	const seconds = Math.max(1.2, 0.3 + words.length * 0.33 + digits * 0.08);
	return Math.round(seconds * fps);
};

/** Theme and kit timings are written for 30 fps; this scales a frame count to the composition's rate. */
export const at30 = (frames: number, fps: number): number => Math.max(1, Math.round((frames * fps) / 30));
