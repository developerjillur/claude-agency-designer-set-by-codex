// Cutting and pulsing on the music. <OnBeats> lays its children back to back, each lasting a whole number of beats,
// so every cut lands on the grid. <BeatPulse> gives an element a small hit on each beat. Keep pulses on elements
// (a dot, a logo, a line), not on the whole frame: a frame that throbs on every beat tires the eye fast.
import React, {useMemo} from 'react';
import {Series, useCurrentFrame} from 'remotion';
import {beatGrid, useStage} from '../core';
import {beatPulse} from './beats';

/** The beat frames of a track from its tempo and first downbeat (seconds), over the enclosing Sequence. */
export const useBeatGrid = (bpm: number, offset = 0): number[] => {
	const {fps, durationInFrames} = useStage();
	const len = Number.isFinite(durationInFrames) ? durationInFrames : fps * 600;
	return useMemo(() => beatGrid(bpm, fps, len + Math.ceil((60 / bpm) * fps), offset), [bpm, fps, len, offset]);
};

/** Frame of beat `k` (0 = the first downbeat) for a tempo and offset. */
export const beatFrame = (k: number, bpm: number, fps: number, offset = 0): number => Math.round((offset + (k * 60) / bpm) * fps);

export type BeatPulseProps = {
	bpm: number;
	/** Seconds to the first downbeat in the track (measure it; do not guess). */
	offset?: number;
	/** Pulse on every n-th beat (2 = on beats 1 and 3, 4 = once a bar). */
	every?: number;
	/** Which beat of the cycle counts, 0 = the first. */
	phase?: number;
	/** Extra scale on the hit (0.06 = 6 %). */
	amount?: number;
	/** Frames the hit takes to settle. */
	decay?: number;
	/** Also brighten (0 to 1): a glow for accents and lights. */
	glow?: number;
	origin?: string;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

export const BeatPulse: React.FC<BeatPulseProps> = ({bpm, offset = 0, every = 1, phase = 0, amount = 0.06, decay = 9, glow = 0, origin = 'center', children, style}) => {
	const frame = useCurrentFrame();
	const grid = useBeatGrid(bpm, offset);
	const p = beatPulse(frame, grid, {decay, every, phase});
	return (
		<div style={{scale: `${1 + amount * p}`, transformOrigin: origin, filter: glow > 0 && p > 0.01 ? `brightness(${1 + glow * p})` : undefined, ...style}}>
			{children}
		</div>
	);
};

export type OnBeatsProps = {
	bpm: number;
	/** Seconds to the first downbeat; the first shot also covers the lead-in before it. */
	offset?: number;
	/** Beats each child lasts: one number for all, or one per child. */
	beats?: number | readonly number[];
	/** Frames each child is mounted early (media in them buffers in the preview). */
	premountFor?: number;
	/** One child per shot. */
	children: React.ReactNode;
};

/** Shot lengths in frames for a beat montage (what <OnBeats> uses): the sum is where the last shot ends. */
export const onBeatLengths = (count: number, beats: number | readonly number[], bpm: number, fps: number, offset = 0): number[] => {
	const out: number[] = [];
	let k = 0;
	for (let i = 0; i < count; i++) {
		const n = typeof beats === 'number' ? beats : beats[i] ?? beats[beats.length - 1] ?? 4;
		const start = i === 0 ? 0 : beatFrame(k, bpm, fps, offset);
		const end = beatFrame(k + n, bpm, fps, offset);
		out.push(Math.max(1, end - start));
		k += n;
	}
	return out;
};

/**
 * Shots cut on the beat: child i starts on a beat and lasts `beats` beats, measured on the rounded grid so a long
 * montage never drifts. Start the music on the same frame as the montage.
 */
export const OnBeats: React.FC<OnBeatsProps> = ({bpm, offset = 0, beats = 4, premountFor, children}) => {
	const {fps} = useStage();
	const items = React.Children.toArray(children);
	const lengths = onBeatLengths(items.length, beats, bpm, fps, offset);
	return (
		<Series>
			{items.map((child, i) => (
				<Series.Sequence key={i} durationInFrames={lengths[i]} premountFor={premountFor ?? fps} name={`Beat shot ${i + 1}`}>
					{child}
				</Series.Sequence>
			))}
		</Series>
	);
};
