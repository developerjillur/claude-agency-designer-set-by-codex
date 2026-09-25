// Shape morphs: <MorphPath> inside an <svg>, <Morph> as a sized block. Several shapes in a row, each held and
// then morphed into the next, with the fill colour moving along. The 4.0.528 stand-in for interpolatePaths.
import {getBoundingBox} from '@remotion/paths';
import React, {useMemo} from 'react';
import {interpolateColors, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {morphAt, type MorphMode} from './paths';

export type MorphTiming = {
	frames?: number[]; // the frame each shape is fully shown (strictly increasing); default from delay/hold/move
	delay?: number; // frames before the first morph starts its hold
	hold?: number; // frames each shape rests (default 18 at 30 fps)
	move?: number; // frames each morph takes (default 24 at 30 fps)
	ease?: Ease; // default in-out
};

/** Keyframe times and matching shapes (holds are repeated keys) from paths and hold/move lengths. */
export const morphSchedule = (n: number, delay: number, holdFrames: number, moveFrames: number): {frames: number[]; index: number[]} => {
	// keys must strictly increase
	const hold = Math.max(1, holdFrames);
	const move = Math.max(1, moveFrames);
	const frames: number[] = [];
	const index: number[] = [];
	let t = delay;
	for (let i = 0; i < n; i++) {
		frames.push(t);
		index.push(i);
		if (i < n - 1) {
			t += hold;
			frames.push(t);
			index.push(i);
			t += move;
		}
	}
	return {frames, index};
};

export type MorphPathProps = MorphTiming & {
	paths: string[];
	colors?: string[]; // fill per shape, interpolated in step with the shape
	fill?: string; // one fill for all (default: the theme accent)
	stroke?: string;
	strokeWidth?: number;
	mode?: MorphMode; // 'points' (default: any closed outlines) or 'native' (interpolatePath)
	style?: React.CSSProperties;
};

/** A path that morphs through `paths` over time, for use inside an <svg>. */
export const MorphPath: React.FC<MorphPathProps> = ({
	paths,
	colors,
	fill,
	stroke,
	strokeWidth = 0,
	mode = 'points',
	frames,
	delay = 0,
	hold,
	move,
	ease = curves.inOut,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps} = useStage();
	const sched = useMemo(() => {
		if (frames && frames.length === paths.length) {
			return {frames, index: paths.map((_, i) => i)};
		}
		return morphSchedule(paths.length, delay, hold ?? at30(18, fps), move ?? at30(24, fps));
	}, [frames, paths, delay, hold, move, fps]);
	const keyPaths = sched.index.map((i) => paths[i]);
	const d = morphAt(frame, sched.frames, keyPaths, ease, mode);
	const col =
		colors && colors.length === paths.length && sched.frames.length > 1
			? interpolateColors(frame, sched.frames, sched.index.map((i) => colors[i]), {easing: ease})
			: (fill ?? t.colors.accent);
	return <path d={d} fill={col} stroke={stroke} strokeWidth={strokeWidth} strokeLinejoin="round" style={style} />;
};

export type MorphProps = MorphPathProps & {
	viewBox?: string; // default: the union of every shape's bounding box
	width?: number; // px at 1080
	height?: number;
	svgStyle?: React.CSSProperties;
};

/** A self-contained morph block sized in px at 1080. */
export const Morph: React.FC<MorphProps> = ({viewBox, width, height, svgStyle, ...rest}) => {
	const {unit} = useStage();
	const box = useMemo(() => {
		if (viewBox) {
			const [x, y, w, h] = viewBox.split(/[\s,]+/).map(Number);
			return {x, y, w, h};
		}
		const bs = rest.paths.filter((p) => p.trim()).map((p) => getBoundingBox(p));
		if (bs.length === 0) {
			return {x: 0, y: 0, w: 1, h: 1};
		}
		const x1 = Math.min(...bs.map((b) => b.x1));
		const y1 = Math.min(...bs.map((b) => b.y1));
		const x2 = Math.max(...bs.map((b) => b.x2));
		const y2 = Math.max(...bs.map((b) => b.y2));
		const pad = (rest.strokeWidth ?? 0) + 2;
		return {x: x1 - pad, y: y1 - pad, w: x2 - x1 + 2 * pad, h: y2 - y1 + 2 * pad};
	}, [viewBox, rest.paths, rest.strokeWidth]);
	const w = width ?? (height ? (height * box.w) / box.h : box.w);
	const h = height ?? (width ? (width * box.h) / box.w : box.h);
	return (
		<svg viewBox={`${box.x} ${box.y} ${box.w} ${box.h}`} width={w * unit} height={h * unit} style={{display: 'block', overflow: 'visible', ...svgStyle}}>
			<MorphPath {...rest} />
		</svg>
	);
};
