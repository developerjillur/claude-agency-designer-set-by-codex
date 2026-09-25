// An object travelling along a path (a plane on a route, a packet on a wire, a dot on a chart), turned to the
// direction of travel, with an optional trail drawn behind it. Null-safe on 4.0.528 (lengths are clamped).
import {cutPath} from '@remotion/paths';
import React from 'react';
import {curves, useTheme} from '../core';
import {useDrawProgress, type DrawTiming} from './Draw';
import {dashFor, pathLength, pathPose} from './paths';

export type PathFollowProps = DrawTiming & {
	d: string;
	rotate?: boolean; // turn with the path (default true)
	angleOffset?: number; // degrees added to the heading: 90 when the artwork points up instead of right
	trail?: 'none' | 'solid' | 'dashed';
	trailColor?: string;
	trailWidth?: number;
	trailDash?: string; // for 'dashed' (default '2 16' with round caps: a dotted route)
	scaleIn?: number; // share of the trip (0 to 0.3) over which the object grows in at the start
	scaleOut?: number; // share of the trip over which it shrinks away at the end (0: it stays at the end)
	children?: React.ReactNode; // SVG drawn around (0, 0), pointing right (+x)
};

/** For use inside an <svg> (or SvgLayer): children ride the path. */
export const PathFollow: React.FC<PathFollowProps> = ({
	d,
	rotate = true,
	angleOffset = 0,
	trail = 'none',
	trailColor,
	trailWidth = 4,
	trailDash = '2 16',
	scaleIn = 0,
	scaleOut = 0,
	children,
	ease = curves.inOut,
	...timing
}) => {
	const t = useTheme();
	const p = useDrawProgress({...timing, ease});
	if (!d.trim()) {
		return null; // nothing to ride
	}
	const pose = pathPose(d, p);
	const len = pathLength(d);
	const col = trailColor ?? t.colors.muted;
	const sIn = scaleIn > 0 ? Math.min(1, p / scaleIn) : 1;
	const sOut = scaleOut > 0 ? Math.min(1, (1 - p) / scaleOut) : 1;
	const s = curves.outCubic(Math.max(0, Math.min(sIn, sOut)));
	let trailEl: React.ReactNode = null;
	if (trail === 'dashed' && p > 0) {
		trailEl = <path d={cutPath(d, len * p)} fill="none" stroke={col} strokeWidth={trailWidth} strokeLinecap="round" strokeDasharray={trailDash} />;
	} else if (trail === 'solid') {
		const dsh = dashFor(len, p);
		trailEl = dsh.hidden ? null : (
			<path d={d} fill="none" stroke={col} strokeWidth={trailWidth} strokeLinecap="round" strokeDasharray={dsh.strokeDasharray} strokeDashoffset={dsh.strokeDashoffset} />
		);
	}
	return (
		<g>
			{trailEl}
			{s > 0.001 ? (
				<g transform={`translate(${pose.x} ${pose.y}) rotate(${rotate ? pose.angle + angleOffset : angleOffset}) scale(${s})`}>{children}</g>
			) : null}
		</g>
	);
};
