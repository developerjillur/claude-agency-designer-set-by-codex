// Deterministic glitch timing: where the bursts are and how hard each frame hits. Pure functions of the frame,
// so any frame renders the same in any tab.
import {r01} from './util';

export type GlitchBurst = {at: number; frames?: number; strength?: number};

export type GlitchSchedule = {
	/** Explicit bursts (frames from the start of the Sequence). When given, no automatic bursts are made. */
	bursts?: GlitchBurst[];
	/** Automatic bursts: about one every `every` frames (default 54, 1.8 s at 30 fps). */
	every?: number;
	/** Frames per automatic burst (default 6). */
	length?: number;
	/** Chance that a window has a burst at all (default 0.85): real glitches are irregular. */
	chance?: number;
	seed?: string;
};

export type GlitchHit = {
	/** 0 outside a burst, up to 1 on the hardest frame. */
	intensity: number;
	/** Frame inside the burst (0 on its first frame), -1 outside. */
	local: number;
	/** A seed that changes every frame of the burst, for patterns. */
	seed: number;
};

const envelope = (frame: number, local: number, frames: number, seed: string, strength: number) => {
	// first frame hits hardest, then it flickers down
	const base = local === 0 ? 1 : 0.35 + 0.65 * r01(`${seed}-e-${frame}`);
	return Math.min(1, Math.max(0, base * (1 - (0.4 * local) / Math.max(1, frames)) * strength));
};

/** The glitch state at `frame`. Outside every burst the intensity is 0. */
export const glitchAt = (frame: number, o: GlitchSchedule = {}): GlitchHit => {
	const seed = o.seed ?? 'glitch';
	if (o.bursts && o.bursts.length > 0) {
		for (const b of o.bursts) {
			const frames = Math.max(1, Math.round(b.frames ?? 6));
			if (frame >= b.at && frame < b.at + frames) {
				const local = frame - b.at;
				return {intensity: envelope(frame, local, frames, seed, b.strength ?? 1), local, seed: frame * 7 + 13};
			}
		}
		return {intensity: 0, local: -1, seed: 0};
	}
	const every = Math.max(8, Math.round(o.every ?? 54));
	const length = Math.max(1, Math.min(every - 2, Math.round(o.length ?? 6)));
	const w = Math.floor(frame / every);
	if (r01(`${seed}-w-${w}`) > (o.chance ?? 0.85)) {
		return {intensity: 0, local: -1, seed: 0};
	}
	const start = w * every + Math.floor(r01(`${seed}-s-${w}`) * (every - length));
	if (frame < start || frame >= start + length) {
		return {intensity: 0, local: -1, seed: 0};
	}
	const local = frame - start;
	return {intensity: envelope(frame, local, length, seed, 1), local, seed: frame * 7 + 13};
};
