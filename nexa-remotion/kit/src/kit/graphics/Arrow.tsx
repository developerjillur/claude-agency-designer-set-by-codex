// Arrows that draw on: a straight or bent shaft, an open or filled head that rides the tip and turns with it.
// <ArrowPath> works inside any <svg>; <Arrow> is an overlay in frame pixels (for pointing at things in a scene).
import {cutPath, reversePath} from '@remotion/paths';
import React, {useMemo} from 'react';
import {at30, curves, useStage, useTheme} from '../core';
import {useDrawProgress, type DrawTiming} from './Draw';
import {bendPath, dashFor, pathLength, pathPose} from './paths';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type ArrowHead = 'open' | 'filled' | 'none';

export type ArrowPathProps = DrawTiming &
	GraphicExitProps & {
		from?: [number, number];
		to?: [number, number];
		d?: string; // any path instead of from/to (the head goes at its end)
		bend?: number; // 0 straight, 0.2 to 0.35 a friendly arc, negative bends the other way
		head?: ArrowHead;
		tail?: ArrowHead; // a head at the start too (a two-way arrow)
		headSize?: number; // length of the head (default 4.5 x the stroke)
		headAngle?: number; // half-angle of the head in degrees (default 30)
		gap?: number; // keep this far from both end points (so the arrow does not touch what it points at)
		color?: string;
		strokeWidth?: number;
		dash?: string; // a dashed shaft ('10 12')
		opacity?: number;
	};

const shorten = (d: string, start: number, end: number): string => {
	const len = pathLength(d);
	if (start + end >= len * 0.9) {
		return d;
	}
	let out = d;
	if (end > 0) {
		out = cutPath(out, len - end);
	}
	if (start > 0) {
		const rev = reversePath(out);
		out = reversePath(cutPath(rev, pathLength(rev) - start));
	}
	return out;
};

const Head: React.FC<{x: number; y: number; angle: number; size: number; half: number; kind: ArrowHead; color: string; width: number}> = ({
	x,
	y,
	angle,
	size,
	half,
	kind,
	color,
	width,
}) => {
	if (kind === 'none' || size <= 0.01) {
		return null;
	}
	const a = (half * Math.PI) / 180;
	const bx = -Math.cos(a) * size;
	const by = Math.sin(a) * size;
	const g = `translate(${x} ${y}) rotate(${angle})`;
	if (kind === 'filled') {
		// a slightly swept-back triangle: reads as designed, not as a default marker
		return (
			<path
				transform={g}
				d={`M0 0L${bx} ${-by}Q${bx * 0.72} 0 ${bx} ${by}Z`}
				fill={color}
				stroke={color}
				strokeWidth={width * 0.5}
				strokeLinejoin="round"
			/>
		);
	}
	return (
		<path
			transform={g}
			d={`M${bx} ${-by}L0 0L${bx} ${by}`}
			fill="none"
			stroke={color}
			strokeWidth={width}
			strokeLinecap="round"
			strokeLinejoin="round"
		/>
	);
};

/** An arrow for use inside an <svg>: coordinates and sizes are the SVG's own units. */
export const ArrowPath: React.FC<ArrowPathProps> = ({
	from = [0, 0],
	to = [200, 0],
	d,
	bend = 0,
	head = 'open',
	tail = 'none',
	headSize,
	headAngle = 30,
	gap = 0,
	color,
	strokeWidth = 5,
	dash,
	opacity = 1,
	exit = 'none',
	outDuration,
	outAt,
	ease = curves.outCubic,
	...timing
}) => {
	const t = useTheme();
	const {fps} = useStage();
	const p = useDrawProgress({duration: at30(22, fps), ...timing, ease});
	const q = useGraphicExit({exit, outDuration, outAt});
	const col = color ?? t.colors.text;
	const size = headSize ?? strokeWidth * 4.5;
	const [fx, fy] = from;
	const [tx, ty] = to;
	const path = useMemo(() => shorten(d ?? bendPath([fx, fy], [tx, ty], bend), gap, gap), [d, fx, fy, tx, ty, bend, gap]);
	const len = pathLength(path);
	if (p <= 0 || len <= 0) {
		return null;
	}
	// the shaft stops short of a filled head's point so its round cap never pokes through
	const tipBack = head === 'filled' ? size * 0.55 : 0;
	const tailBack = tail === 'filled' ? size * 0.55 : 0;
	const drawn = p * len;
	const shaftEnd = Math.max(0, drawn - tipBack);
	const tip = pathPose(path, p);
	const start = pathPose(path, 0);
	// heads grow in over the first stretch so the first frames do not show a head without a line
	const grow = Math.min(1, drawn / Math.max(1, size * 2.2));
	const erase = exit === 'undraw' ? q : 0;
	const fade = exit === 'fade' ? 1 - q : 1;
	let shaft: React.ReactNode = null;
	if (dash) {
		const cut = cutPath(path, Math.max(0.01, shaftEnd));
		shaft = <path d={cut} fill="none" stroke={col} strokeWidth={strokeWidth} strokeLinecap="round" strokeDasharray={dash} opacity={1 - erase} />;
	} else {
		const a = tailBack + erase * len;
		const b = shaftEnd;
		if (b - a > 0.01) {
			const dsh = a <= 0 ? dashFor(len, b / len) : {strokeDasharray: `${b - a} ${len * 2 + 10}`, strokeDashoffset: -a, hidden: false};
			shaft = dsh.hidden ? null : (
				<path d={path} fill="none" stroke={col} strokeWidth={strokeWidth} strokeLinecap="round" strokeDasharray={dsh.strokeDasharray} strokeDashoffset={dsh.strokeDashoffset} />
			);
		}
	}
	const headScale = grow * (1 - erase);
	return (
		<g opacity={opacity * fade}>
			{shaft}
			<Head x={tip.x} y={tip.y} angle={tip.angle} size={size * headScale} half={headAngle} kind={head} color={col} width={strokeWidth} />
			{tail !== 'none' ? (
				<Head x={start.x} y={start.y} angle={start.angle + 180} size={size * grow * (1 - erase)} half={headAngle} kind={tail} color={col} width={strokeWidth} />
			) : null}
		</g>
	);
};

export type ArrowProps = Omit<ArrowPathProps, 'strokeWidth' | 'headSize' | 'gap'> & {
	strokeWidth?: number; // px at 1080 (default 6)
	headSize?: number; // px at 1080
	gap?: number; // px at 1080
	style?: React.CSSProperties;
};

/**
 * An arrow over the whole frame: `from` and `to` are frame pixels (read positions from useStage: width, height,
 * safe), sizes are px at 1080. Put it last in the scene so it draws above what it points at.
 */
export const Arrow: React.FC<ArrowProps> = ({strokeWidth = 6, headSize, gap = 0, style, ...rest}) => {
	const {width, height, unit} = useStage();
	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			width={width}
			height={height}
			style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none', ...style}}
		>
			<ArrowPath strokeWidth={strokeWidth * unit} headSize={headSize === undefined ? undefined : headSize * unit} gap={gap * unit} {...rest} />
		</svg>
	);
};
