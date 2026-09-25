// <LineChart>: one or several series that draw on from left to right, with an area wash, dots that pop as the
// line reaches them, direct labels at the line ends (no legend), callouts that open when the line arrives at
// their point, and x values that may be categories, numbers or dates (uneven spacing is kept honest).
import {scaleLinear, scalePoint, scaleUtc} from 'd3-scale';
import {area as d3area, curveLinear, curveMonotoneX, curveStepAfter, line as d3line} from 'd3-shape';
import React, {useId, useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity, gridOf, neutralOf, seriesColors} from './color';
import {Callout, type CalloutSide} from './Callout';
import {ChartLabel, ChartRoot, estimateLabelWidth, useChartBox, useChartType} from './chart';
import {applyFormat, formatChartDate, tickFormat, type ValueFormatter} from './numbers';
import {dashFor, pathLength, pointOnPath} from './paths';
import {buildFrames, frameAtProgress, useGraphicExit, type GraphicExitProps} from './timing';

export type XValue = number | Date | string;
export type LinePoint = {x: XValue; y: number};
export type LineSeries = {name?: string; points: LinePoint[]; color?: string; dashed?: boolean; area?: boolean};
export type LineCallout = {series?: number; x: XValue; text?: React.ReactNode; title?: React.ReactNode; side?: CalloutSide};

export type LineChartProps = GraphicExitProps & {
	series?: LineSeries[];
	data?: LinePoint[]; // one series, shorthand
	width?: number; // px at 1080 (default: the ChartFrame area or the safe area)
	height?: number;
	curve?: 'linear' | 'smooth' | 'step';
	area?: boolean; // a wash under the line (default: on for a single series)
	dots?: 'all' | 'end' | 'none'; // default: all when there are 12 points or fewer
	zero?: boolean; // the y range includes 0 (default true; false for prices and temperatures)
	yTicks?: number;
	xTicks?: number; // for number and date x values
	format?: ValueFormatter; // y values
	xFormat?: (x: XValue) => string;
	yLabel?: string; // what the y numbers are
	xLabel?: string;
	endLabel?: 'name' | 'value' | 'both' | 'none'; // at each line's end (default: value for one series, name for several)
	callouts?: LineCallout[];
	highlight?: number; // series kept in colour, the rest grey
	delay?: number;
	duration?: number; // frames one line takes to draw (default 66 at 30 fps)
	stagger?: number; // frames between series
	ease?: Ease; // default in-out
	lineWidth?: number; // px at 1080 (default 6)
	tickSize?: number;
	labelSize?: number;
	style?: React.CSSProperties;
};

type Norm = {name: string; color: string; dashed: boolean; area: boolean; pts: {x: number; y: number; raw: LinePoint}[]; width: number; muted: boolean};

const xKind = (v: XValue | undefined): 'cat' | 'date' | 'num' => (typeof v === 'string' ? 'cat' : v instanceof Date ? 'date' : 'num');
const validX = (x: XValue): boolean => (typeof x === 'string' ? true : x instanceof Date ? Number.isFinite(x.getTime()) : Number.isFinite(x));

const lengthCache = new Map<string, number>();

/** Length along a left-to-right path where it reaches x (bisection, cached). */
const lengthAtX = (d: string, x: number): number => {
	const key = `${x.toFixed(2)}|${d}`;
	const hit = lengthCache.get(key);
	if (hit !== undefined) {
		return hit;
	}
	const total = pathLength(d);
	let lo = 0;
	let hi = total;
	for (let i = 0; i < 22; i++) {
		const mid = (lo + hi) / 2;
		if (pointOnPath(d, mid).x < x - 0.01) {
			lo = mid;
		} else {
			hi = mid;
		}
	}
	if (lengthCache.size > 2000) {
		lengthCache.clear();
	}
	lengthCache.set(key, hi);
	return hi;
};

export const LineChart: React.FC<LineChartProps> = ({
	series,
	data,
	width,
	height,
	curve = 'smooth',
	area,
	dots,
	zero = true,
	yTicks = 4,
	xTicks = 6,
	format,
	xFormat,
	yLabel,
	xLabel,
	endLabel,
	callouts = [],
	highlight,
	delay,
	duration,
	stagger,
	ease = curves.inOut,
	lineWidth = 6,
	tickSize = 22,
	labelSize = 28,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const uid = useId().replace(/:/g, '');
	const box = useChartBox(width, height, delay);
	const W = box.width;
	const H = box.height;
	const type = useChartType();
	const q = useGraphicExit({exit, outDuration, outAt});
	// readings that are not finite (NaN, Infinity, an invalid date) are skipped: one bad value never breaks the chart
	const list: LineSeries[] = useMemo(
		() => (series ?? (data ? [{points: data}] : [])).map((s) => ({...s, points: s.points.filter((p) => Number.isFinite(p.y) && validX(p.x))})),
		[series, data],
	);
	const single = list.length === 1;
	const colors = seriesColors(t, list.length);
	const dur = duration ?? buildFrames('line', fps);
	const step = stagger ?? at30(16, fps);
	const axisIn = buildFrames('axis', fps);
	const fmt = (v: number) => applyFormat(v, format);
	const fmtTick = tickFormat(format);
	const kind = xKind(list.find((s) => s.points.length > 0)?.points[0]?.x);
	const mode = endLabel ?? (single ? 'value' : 'name');
	const fadeAll = exit === 'fade' || exit === 'undraw' || exit === 'shrink' ? 1 - q : 1;

	const cats = useMemo(() => {
		const out: string[] = [];
		list.forEach((s) => s.points.forEach((p) => typeof p.x === 'string' && !out.includes(p.x) && out.push(p.x)));
		return out;
	}, [list]);
	if (!list.some((s) => s.points.length > 0)) {
		return null;
	}
	const allY = list.flatMap((s) => s.points.map((p) => p.y));
	const ymin0 = Math.min(...allY);
	const ymax0 = Math.max(...allY);
	const pad = (ymax0 - ymin0) * 0.08 || Math.abs(ymax0) * 0.1 || 1;
	const yDomain: [number, number] = zero ? [Math.min(0, ymin0), Math.max(0, ymax0)] : [ymin0 - pad, ymax0 + pad];
	const yScale0 = scaleLinear().domain(yDomain[0] === yDomain[1] ? [yDomain[0], yDomain[0] + 1] : yDomain).nice(yTicks);
	const yTickVals = yScale0.ticks(yTicks);
	const yTickW = Math.max(0, ...yTickVals.map((v) => estimateLabelWidth(fmtTick(v), tickSize)));

	const endText = (s: LineSeries, i: number): {main: string; sub?: string} => {
		const last = [...s.points].sort((a, b) => toNum(a.x) - toNum(b.x))[s.points.length - 1];
		const v = last ? fmt(last.y) : '';
		const nm = s.name ?? `Series ${i + 1}`;
		return mode === 'value' ? {main: v} : mode === 'both' ? {main: v, sub: nm} : {main: nm};
	};
	const toNum = (x: XValue): number => (typeof x === 'string' ? cats.indexOf(x) : x instanceof Date ? x.getTime() : x);

	const endW = mode === 'none' ? 0 : Math.max(0, ...list.map((s, i) => estimateLabelWidth(endText(s, i).main, labelSize, true)));
	const left = yTickW + 18;
	const right = mode === 'none' ? lineWidth * 2 + 8 : endW + 34;
	const top = 20 + (yLabel ? tickSize * 1.9 : 0);
	const bottom = tickSize * 1.3 + 20 + (xLabel ? tickSize * 1.7 : 0);
	const x0 = left;
	const x1 = W - right;
	const y0 = top;
	const y1 = H - bottom;
	const ys = yScale0.copy().range([y1, y0]);

	// x scale by kind
	const numXs = list.flatMap((s) => s.points.map((p) => toNum(p.x)));
	const xmin = Math.min(...numXs);
	const xmax = Math.max(...numXs);
	const xsNum =
		kind === 'cat'
			? (v: XValue) => scalePoint<string>().domain(cats).range([x0, x1]).padding(0.02)(String(v)) ?? x0
			: kind === 'date'
				? (v: XValue) => scaleUtc().domain([new Date(xmin), new Date(xmax === xmin ? xmin + 1 : xmax)]).range([x0, x1])(v as Date)
				: (v: XValue) => scaleLinear().domain([xmin, xmax === xmin ? xmin + 1 : xmax]).range([x0, x1])(v as number);

	const norm: Norm[] = list.map((s, i) => {
		const muted = highlight !== undefined && highlight !== i;
		const hot = highlight !== undefined && highlight === i;
		return {
			name: s.name ?? `Series ${i + 1}`,
			color: muted ? neutralOf(t) : (s.color ?? (hot ? t.colors.accent : colors[i])),
			dashed: !!s.dashed,
			area: !muted && (s.area ?? area ?? single),
			width: muted ? lineWidth * 0.7 : lineWidth,
			muted,
			pts: [...s.points].sort((a, b) => toNum(a.x) - toNum(b.x)).map((p) => ({x: xsNum(p.x), y: ys(p.y), raw: p})),
		};
	});
	const curveFn = curve === 'smooth' ? curveMonotoneX : curve === 'step' ? curveStepAfter : curveLinear;
	const lineGen = d3line<{x: number; y: number}>()
		.x((p) => p.x)
		.y((p) => p.y)
		.curve(curveFn);
	const baseY = ys(Math.max(yScale0.domain()[0], Math.min(0, yScale0.domain()[1])));
	const areaGen = d3area<{x: number; y: number}>()
		.x((p) => p.x)
		.y0(baseY)
		.y1((p) => p.y)
		.curve(curveFn);

	const axisP = ramp(frame, box.delay, axisIn, curves.out) * fadeAll;
	const grid = gridOf(t);
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];

	// gridlines and y ticks
	yTickVals.forEach((v) => {
		const y = ys(v);
		const isZero = v === 0;
		svg.push(
			<line key={`g${v}`} x1={x0} x2={x0 + (x1 - x0) * (isZero ? axisP : 1)} y1={y} y2={y} stroke={isZero ? t.colors.text : grid} strokeWidth={isZero ? 3 : 2} opacity={isZero ? 0.85 * axisP : axisP} strokeLinecap="round" />,
		);
		html.push(
			<ChartLabel key={`yt${v}`} x={x0 - 14} y={y} anchor="right" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP}}>
				{fmtTick(v)}
			</ChartLabel>,
		);
	});
	if (yLabel) {
		html.push(
			<ChartLabel key="yLabel" x={0} y={0} anchor="top-left" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP}}>
				{yLabel}
			</ChartLabel>,
		);
	}
	// x ticks
	const xTickList: {x: number; text: string}[] = (() => {
		const f = (v: XValue) => (xFormat ? xFormat(v) : kind === 'date' ? formatChartDate(v as Date, xmax - xmin > 3 * 365 * 864e5 ? 'year' : xmax - xmin > 330 * 864e5 ? 'month-year' : 'month-day') : kind === 'num' ? applyFormat(v as number, {}) : String(v));
		if (kind === 'cat') {
			const spacing = cats.length > 1 ? (x1 - x0) / (cats.length - 1) : x1 - x0;
			const widest = Math.max(...cats.map((c) => estimateLabelWidth(f(c), tickSize)));
			const every = Math.max(1, Math.ceil((widest + 18) / Math.max(1, spacing)));
			return cats.filter((_, i) => i % every === 0 || i === cats.length - 1).map((c) => ({x: xsNum(c), text: f(c)}));
		}
		if (kind === 'date') {
			const s = scaleUtc().domain([new Date(xmin), new Date(xmax === xmin ? xmin + 1 : xmax)]).range([x0, x1]);
			return s.ticks(xTicks).map((d) => ({x: s(d), text: f(d)}));
		}
		const s = scaleLinear().domain([xmin, xmax === xmin ? xmin + 1 : xmax]).range([x0, x1]);
		return s.ticks(xTicks).map((v) => ({x: s(v), text: f(v)}));
	})();
	xTickList.forEach((tk, i) => {
		html.push(
			<ChartLabel key={`xt${i}`} x={tk.x} y={y1 + 16} anchor="top" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP}}>
				{tk.text}
			</ChartLabel>,
		);
	});
	if (xLabel) {
		html.push(
			<ChartLabel key="xLabel" x={x1} y={H} anchor="bottom-right" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP}}>
				{xLabel}
			</ChartLabel>,
		);
	}

	// series, the grey ones first so the coloured one sits on top
	const order = norm.map((_, i) => i).sort((a, b) => Number(norm[b].muted) - Number(norm[a].muted));
	const ends: {i: number; x: number; y: number; at: number; color: string}[] = [];
	const clipDefs: React.ReactNode[] = [];
	order.forEach((i) => {
		const s = norm[i];
		if (!s.pts.length) {
			return;
		}
		const start = box.delay + Math.round(axisIn * 0.6) + i * step;
		if (s.pts.length === 1) {
			// one reading: no line to draw, so its dot pops and the end label follows
			const pt = s.pts[0];
			const pop = ramp(frame, start, at30(10, fps), curves.outBack) * fadeAll;
			if (pop > 0 && !s.muted) {
				svg.push(<circle key={`d${i}-0`} cx={pt.x} cy={pt.y} r={Math.max(0, s.width * 1.35 * pop)} fill={t.colors.bg} stroke={s.color} strokeWidth={s.width * 0.8} />);
			}
			ends.push({i, x: pt.x, y: pt.y, at: start + at30(10, fps), color: s.color});
			return;
		}
		const d = lineGen(s.pts) ?? '';
		const L = pathLength(d);
		const p = ramp(frame, start, dur, ease);
		const undraw = exit === 'undraw' ? q : 0;
		const tipLen = L * p;
		const tip = pointOnPath(d, tipLen);
		const clipX = p >= 1 ? W + 40 : tip.x;
		const clipId = `lc-${uid}-${i}`;
		clipDefs.push(
			<clipPath key={clipId} id={clipId}>
				<rect x={-40} y={-40} width={Math.max(0, clipX + 40)} height={H + 80} />
			</clipPath>,
		);
		if (s.area && p > 0) {
			const gid = `lg-${uid}-${i}`;
			clipDefs.push(
				<linearGradient key={gid} id={gid} x1="0" x2="0" y1="0" y2="1">
					<stop offset="0" stopColor={withOpacity(s.color, t.dark ? 0.34 : 0.26)} />
					<stop offset="1" stopColor={withOpacity(s.color, 0)} />
				</linearGradient>,
			);
			svg.push(<path key={`a${i}`} d={areaGen(s.pts) ?? ''} fill={`url(#${gid})`} clipPath={`url(#${clipId})`} opacity={fadeAll} />);
		}
		if (p > 0) {
			if (s.dashed) {
				svg.push(
					<path key={`l${i}`} d={d} fill="none" stroke={s.color} strokeWidth={s.width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${s.width * 0.1} ${s.width * 2.4}`} clipPath={`url(#${clipId})`} opacity={fadeAll} />,
				);
			} else {
				const a = undraw * L;
				const b = tipLen;
				if (b - a > 0.05) {
					const dsh = a <= 0 ? dashFor(L, p) : {strokeDasharray: `${b - a} ${L * 2 + 10}`, strokeDashoffset: -a, hidden: false};
					if (!dsh.hidden) {
						svg.push(
							<path key={`l${i}`} d={d} fill="none" stroke={s.color} strokeWidth={s.width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dsh.strokeDasharray} strokeDashoffset={dsh.strokeDashoffset} opacity={exit === 'undraw' ? 1 : fadeAll} />,
						);
					}
				}
			}
		}
		// dots pop as the line reaches them
		const dotMode = dots ?? (s.pts.length <= 12 ? 'all' : 'end');
		s.pts.forEach((pt, k) => {
			const isEnd = k === s.pts.length - 1;
			if (dotMode === 'none' || (dotMode === 'end' && !isEnd) || s.muted) {
				return;
			}
			const at = frameAtProgress(lengthAtX(d, pt.x) / (L || 1), start, dur, ease);
			const pop = ramp(frame, at, at30(10, fps), curves.outBack) * fadeAll;
			if (pop <= 0) {
				return;
			}
			const r = (isEnd ? s.width * 1.35 : s.width * 1.05) * pop;
			svg.push(<circle key={`d${i}-${k}`} cx={pt.x} cy={pt.y} r={Math.max(0, r)} fill={t.colors.bg} stroke={s.color} strokeWidth={s.width * 0.8} />);
		});
		// the moving head while it draws
		if (p > 0 && p < 1 && !s.muted) {
			svg.push(<circle key={`h${i}`} cx={tip.x} cy={tip.y} r={s.width * 2.6} fill={withOpacity(s.color, 0.22)} />);
			svg.push(<circle key={`hc${i}`} cx={tip.x} cy={tip.y} r={s.width * 1.1} fill={s.color} />);
		}
		const last = s.pts[s.pts.length - 1];
		ends.push({i, x: last.x, y: last.y, at: start + dur, color: s.color});
	});

	// end labels, nudged apart vertically
	if (mode !== 'none') {
		const gap = labelSize * (mode === 'both' ? 2.3 : 1.3);
		const sorted = [...ends].sort((a, b) => a.y - b.y);
		const ys2 = sorted.map((e) => e.y);
		for (let k = 1; k < ys2.length; k++) {
			ys2[k] = Math.max(ys2[k], ys2[k - 1] + gap);
		}
		const overflow = ys2.length ? ys2[ys2.length - 1] - (H - gap / 2) : 0;
		if (overflow > 0) {
			for (let k = 0; k < ys2.length; k++) {
				ys2[k] -= overflow;
			}
		}
		sorted.forEach((e, k) => {
			const s = list[e.i];
			const txt = endText(s, e.i);
			const lp = ramp(frame, e.at - at30(4, fps), at30(12, fps), curves.out) * fadeAll;
			html.push(
				<ChartLabel key={`e${e.i}`} x={e.x + norm[e.i].width * 2 + 12 + (1 - lp) * -10} y={ys2[k]} anchor="left" style={{opacity: lp, lineHeight: 1.1}}>
					<div style={{...type.value, fontSize: labelSize * unit, color: norm[e.i].muted ? t.colors.muted : e.color}}>{txt.main}</div>
					{txt.sub ? <div style={{...type.tick, fontSize: tickSize * unit}}>{txt.sub}</div> : null}
				</ChartLabel>,
			);
		});
	}

	// callouts open when their line arrives
	callouts.forEach((c, k) => {
		const si = c.series ?? 0;
		const s = norm[si];
		// a category that is not on the axis (a typo) is skipped rather than pinned to the first point
		if (!s || s.pts.length < 2 || (kind === 'cat' && !cats.includes(String(c.x)))) {
			return;
		}
		const d = lineGen(s.pts) ?? '';
		const L = pathLength(d);
		const cx = xsNum(c.x);
		const len = lengthAtX(d, cx);
		const pt = pointOnPath(d, len);
		const start = box.delay + Math.round(axisIn * 0.6) + si * step;
		const at = frameAtProgress(len / (L || 1), start, dur, ease);
		html.push(
			<Callout
				key={`c${k}`}
				x={pt.x * unit}
				y={(pt.y - s.width * 1.6) * unit}
				side={c.side ?? 'top'}
				title={c.title}
				text={c.text}
				delay={Math.round(at + at30(2, fps))}
				bounds={{x: 0, y: 0, w: W * unit, h: H * unit}}
				fontSize={26}
				exit={exit === 'none' ? 'none' : 'shrink'}
				outDuration={outDuration}
				outAt={outAt}
			/>,
		);
	});

	return (
		<ChartRoot width={W} height={H} svg={[<defs key="defs">{clipDefs}</defs>, ...svg]} style={style}>
			{html}
		</ChartRoot>
	);
};
