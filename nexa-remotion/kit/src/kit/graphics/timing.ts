// Shared timing for graphics: the exit window (it ends on the last frame of the enclosing Sequence, like
// Animate's), the frame at which an eased build reaches a given progress, and the house durations.
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';

export type GraphicExitKind = 'none' | 'fade' | 'shrink' | 'undraw';

export type GraphicExitProps = {
	exit?: GraphicExitKind;
	outDuration?: number; // frames (default: the theme's exit length)
	outAt?: number; // local frame the exit starts (default: it ends on the last frame of the Sequence)
};

/** 0 until the exit starts, 1 once it is done (ease-in, faster than the entrance). */
export const useGraphicExit = ({exit = 'none', outDuration, outAt}: GraphicExitProps): number => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, durationInFrames} = useStage();
	if (exit === 'none') {
		return 0;
	}
	const dur = outDuration ?? at30(t.motion.exitFrames, fps);
	const start = outAt ?? durationInFrames - 1 - dur;
	return Number.isFinite(start) ? ramp(frame, start, dur, curves.in) : 0;
};

/**
 * The (fractional) frame at which an eased ramp from `start` over `duration` reaches progress `target`: for timing a
 * dot or a label to the moment a drawing line gets to it. Assumes the curve rises; searched by bisection.
 */
// shared with the motion module (one implementation for the whole kit)
export {frameAtProgress} from '../motion';

/** House build lengths at 30 fps (scale with at30). */
export const GRAPHIC_TIMING = {
	axis: 14, // gridlines and baseline
	bar: 24, // one bar growing
	line: 66, // a line series drawing
	sweep: 48, // a donut sweeping round
	count: 42, // a number counting up
	pop: 12, // a dot or badge popping
	label: 12, // a label rising in
	edge: 18, // a connector drawing
	node: 14, // a node arriving
} as const;

/** A house build length for the composition's frame rate. */
export const buildFrames = (key: keyof typeof GRAPHIC_TIMING, fps: number): number => at30(GRAPHIC_TIMING[key], fps);
