// An edit as data: the source ranges to keep, laid back to back. Everything that is timed against the source
// (captions, words, cues) is remapped through the same list, so it stays in sync after the cuts.

/** A kept part of the source in seconds: [start, end] or [start, end, speed]. */
export type KeepRange = readonly [start: number, end: number] | readonly [start: number, end: number, rate: number];

/** One piece of an edit, in frames at the composition fps. */
export type EditPiece = {
	index: number;
	/** Output frame where the piece starts. */
	from: number;
	/** Output frames the piece lasts. */
	length: number;
	/** Source frame shown at the piece's first frame. */
	trimBefore: number;
	/** Constant speed of the piece (1 = normal). */
	rate: number;
	/** The source range in seconds, as given. */
	start: number;
	end: number;
};

/**
 * Lays kept ranges back to back. Source positions are rounded to whole frames once, here, and every other helper
 * uses these pieces, so video, captions and cues agree to the frame. Empty or reversed ranges are skipped.
 */
export const buildEdit = (ranges: readonly KeepRange[], fps: number): EditPiece[] => {
	const out: EditPiece[] = [];
	let from = 0;
	ranges.forEach((r, index) => {
		const [start, end] = r;
		const rate = r.length > 2 && r[2] !== undefined && r[2] > 0 ? r[2] : 1;
		const inF = Math.round(start * fps);
		const outF = Math.round(end * fps);
		const length = Math.floor((outF - inF) / rate + 1e-6);
		if (!(length > 0)) {
			return;
		}
		out.push({index, from, length, trimBefore: inF, rate, start, end});
		from += length;
	});
	return out;
};

/** Output frames of an edit: use it for the composition's `durationInFrames`. */
export const editLength = (ranges: readonly KeepRange[], fps: number): number => {
	const e = buildEdit(ranges, fps);
	const last = e[e.length - 1];
	return last ? last.from + last.length : 0;
};

/** The piece that shows source frame `sourceFrame`, or null when that moment was cut out. */
export const pieceAtSource = (sourceFrame: number, edit: readonly EditPiece[]): EditPiece | null => {
	for (const p of edit) {
		if (sourceFrame >= p.trimBefore && sourceFrame < p.trimBefore + p.length * p.rate) {
			return p;
		}
	}
	return null;
};

/** The piece playing at output frame `frame`, or null past the end. */
export const pieceAt = (frame: number, edit: readonly EditPiece[]): EditPiece | null => {
	for (const p of edit) {
		if (frame >= p.from && frame < p.from + p.length) {
			return p;
		}
	}
	return null;
};

/** Output time (seconds) of a source time (seconds), or null when it was cut out. */
export const remapTime = (seconds: number, edit: readonly EditPiece[], fps: number): number | null => {
	const sf = seconds * fps;
	const p = pieceAtSource(sf, edit);
	return p ? (p.from + (sf - p.trimBefore) / p.rate) / fps : null;
};

/** Source time (seconds) shown at an output frame, or null past the end: the inverse of `remapTime`. */
export const sourceTime = (frame: number, edit: readonly EditPiece[], fps: number): number | null => {
	const p = pieceAt(frame, edit);
	return p ? (p.trimBefore + (frame - p.from) * p.rate) / fps : null;
};

/**
 * Word or caption timings (ms, in the source) moved into output time. A word is kept when its middle survived
 * the cuts; its start and end are clamped to its piece. Works on `Caption[]` from @remotion/captions
 * (`timestampMs` is moved too) and on any `{startMs, endMs}` objects.
 */
export const remapWords = <T extends {startMs: number; endMs: number; timestampMs?: number | null}>(
	words: readonly T[],
	edit: readonly EditPiece[],
	fps: number,
): T[] => {
	const out: T[] = [];
	for (const w of words) {
		const mid = ((w.startMs + w.endMs) / 2000) * fps;
		const p = pieceAtSource(mid, edit);
		if (!p) {
			continue;
		}
		const lo = p.trimBefore;
		const hi = p.trimBefore + p.length * p.rate;
		const map = (ms: number) => {
			const sf = Math.min(hi, Math.max(lo, (ms / 1000) * fps));
			return Math.round(((p.from + (sf - lo) / p.rate) / fps) * 1000);
		};
		const moved = {...w, startMs: map(w.startMs), endMs: map(w.endMs)} as T;
		if (typeof w.timestampMs === 'number') {
			(moved as {timestampMs?: number | null}).timestampMs = map(w.timestampMs);
		}
		out.push(moved);
	}
	return out;
};

/**
 * The ranges to keep from word timings (ms): words closer than `gap` seconds stay in one piece, each piece gets
 * `padBefore` and `padAfter` seconds of air, and pieces never run past `duration`. Feed the result to <JumpCuts>.
 * From silence detection instead (getSilentParts in @remotion/renderer), map `audibleParts` to [start, end].
 */
export const keepRanges = (
	words: readonly {startMs: number; endMs: number}[],
	o: {gap?: number; padBefore?: number; padAfter?: number; duration?: number} = {},
): [number, number][] => {
	const {gap = 0.45, padBefore = 0.12, padAfter = 0.2, duration = Infinity} = o;
	const sorted = [...words].filter((w) => w.endMs > w.startMs).sort((a, b) => a.startMs - b.startMs);
	const out: [number, number][] = [];
	let lastEnd = -Infinity;
	for (const w of sorted) {
		const s = w.startMs / 1000;
		const e = w.endMs / 1000;
		const cur = out[out.length - 1];
		if (cur && s - lastEnd < gap) {
			cur[1] = Math.min(duration, Math.max(cur[1], e + padAfter));
		} else {
			const start = Math.max(0, s - padBefore, cur ? cur[1] : 0);
			out.push([start, Math.min(duration, e + padAfter)]);
		}
		lastEnd = Math.max(lastEnd, e);
	}
	return out.filter(([s, e]) => e > s);
};
