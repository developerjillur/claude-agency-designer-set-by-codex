// <Sparkline>: a small trend line without axes (beside a stat, in a card, in a table row) that draws on, with a
// soft wash under it and a dot on the latest value.
import {area as d3area, curveMonotoneX, line as d3line} from 'd3-shape';
import React, {useId} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {useDrawProgress, type DrawTiming} from './Draw';
import {dashFor, pathLength, pointOnPath} from './paths';

export type SparklineProps = DrawTiming & {
	data: number[]; // values, evenly spaced in time
	width?: number; // px at 1080 (default 280)
	height?: number; // px at 1080 (default 80)
	color?: string; // default: accent
	area?: boolean; // wash under the line (default true)
	dot?: boolean; // a dot on the last value (default true)
	strokeWidth?: number; // px at 1080 (default 4)
	zero?: boolean; // the range includes 0 (default false: a sparkline shows shape, not size)
	style?: React.CSSProperties;
};

export const Sparkline: React.FC<SparklineProps> = ({
	data,
	width = 280,
	height = 80,
	color,
	area = true,
	dot = true,
	strokeWidth = 4,
	zero = false,
	style,
	duration,
	ease = curves.inOut,
	...timing
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const gid = `sp-${useId().replace(/:/g, '')}`;
	const p = useDrawProgress({duration: duration ?? at30(40, fps), ease, ...timing});
	const col = color ?? t.colors.accent;
	const finite = data.filter((v) => Number.isFinite(v));
	if (!finite.length) {
		return null;
	}
	const pad = strokeWidth * 2;
	const lo = Math.min(...finite, zero ? 0 : Infinity);
	const hi = Math.max(...finite, zero ? 0 : -Infinity);
	const span = hi - lo || 1;
	// a value that is not a finite number is skipped; the others keep their place in time
	const pts = data.flatMap((v, i) =>
		Number.isFinite(v)
			? [{x: pad + (i / Math.max(1, data.length - 1)) * (width - pad * 2), y: pad + (1 - (v - lo) / span) * (height - pad * 2)}]
			: [],
	);
	const d = d3line<{x: number; y: number}>().x((q) => q.x).y((q) => q.y).curve(curveMonotoneX)(pts) ?? '';
	const a = d3area<{x: number; y: number}>().x((q) => q.x).y0(height).y1((q) => q.y).curve(curveMonotoneX)(pts) ?? '';
	const len = pathLength(d);
	const tip = pointOnPath(d, len * p);
	const dsh = dashFor(len, p);
	const dotP = ramp(frame, (timing.delay ?? 0) + (duration ?? at30(40, fps)) - at30(4, fps), at30(10, fps), curves.outBack);
	return (
		<svg viewBox={`0 0 ${width} ${height}`} width={width * unit} height={height * unit} style={{display: 'block', overflow: 'visible', ...style}}>
			<defs>
				<linearGradient id={gid} x1="0" x2="0" y1="0" y2="1">
					<stop offset="0" stopColor={withOpacity(col, t.dark ? 0.32 : 0.22)} />
					<stop offset="1" stopColor={withOpacity(col, 0)} />
				</linearGradient>
				<clipPath id={`${gid}-c`}>
					<rect x={-10} y={-10} width={Math.max(0, (p >= 1 ? width : tip.x) + 10)} height={height + 20} />
				</clipPath>
			</defs>
			{area && p > 0 ? <path d={a} fill={`url(#${gid})`} clipPath={`url(#${gid}-c)`} /> : null}
			{dsh.hidden ? null : (
				<path d={d} fill="none" stroke={col} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dsh.strokeDasharray} strokeDashoffset={dsh.strokeDashoffset} />
			)}
			{dot && dotP > 0 ? <circle cx={pts[pts.length - 1]?.x} cy={pts[pts.length - 1]?.y} r={strokeWidth * 1.5 * dotP} fill={col} stroke={t.colors.bg} strokeWidth={strokeWidth * 0.6} /> : null}
		</svg>
	);
};
