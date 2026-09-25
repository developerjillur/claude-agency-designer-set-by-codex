// <BarChart>: vertical or horizontal bars that grow from a zero baseline in reading order, labelled directly
// (values on the bars, no legend), with one highlighted bar, nice ticks and negative values. The value scale
// always contains zero: a bar's length is its value.
import {scaleBand, scaleLinear} from 'd3-scale';
import React, {useMemo} from 'react';
import {interpolateColors, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {gridOf, neutralOf, textColorOn} from './color';
import {ChartLabel, ChartRoot, breakLabelLines, estimateLabelWidth, useChartBox, useChartType} from './chart';
import {applyFormat, countValue, decimalsFor, tickFormat, type ValueFormatter} from './numbers';
import {buildFrames, useGraphicExit, type GraphicExitProps} from './timing';

export type BarDatum = {label: string; value: number; color?: string};

export type BarChartProps = GraphicExitProps & {
	data: BarDatum[];
	orientation?: 'vertical' | 'horizontal';
	width?: number; // px at 1080 (default: the ChartFrame area or the safe area)
	height?: number;
	highlight?: number | string | readonly (number | string)[]; // index or label: accent, the rest grey
	highlightAt?: number; // frame the other bars step back to grey (default: grey from the start)
	format?: ValueFormatter; // value text: {prefix: '$', compact: true}, {suffix: '%'} or a function
	axis?: boolean; // gridlines and tick labels (default: on for vertical, off for horizontal)
	ticks?: number; // about how many ticks (default 4)
	max?: number; // pin the value range (to compare several charts); zero is always included
	min?: number;
	values?: 'land' | 'count' | 'none'; // value labels appear as a bar lands, count up riding the tip, or none
	valuePosition?: 'outside' | 'inside';
	sort?: 'none' | 'desc' | 'asc';
	delay?: number;
	duration?: number; // frames one bar takes to grow (default 24 at 30 fps)
	stagger?: number; // frames between bars (default: the theme's stagger)
	ease?: Ease; // default: the theme's arrival curve
	color?: string; // bar colour (default accent)
	neutral?: string; // colour of bars that are not highlighted
	negativeColor?: string; // negative bars (default: the theme's negative colour)
	axisLabel?: string; // what the numbers are ('USD millions'), shown by the axis
	labelSize?: number; // px at 1080
	valueSize?: number;
	barRadius?: number; // px at 1080 (default from the theme, at most 12)
	gap?: number; // share of each band left empty (default 0.32)
	maxBar?: number; // thickest bar in px at 1080 (default 190 vertical, 76 horizontal)
	style?: React.CSSProperties;
};

const f = (v: number) => +v.toFixed(2);

/** A bar whose far end is rounded and whose base is square. Vertical: from yBase to yEnd at x..x+w. */
const vBar = (x: number, w: number, yBase: number, yEnd: number, r: number): string => {
	const h = Math.abs(yEnd - yBase);
	if (h < 0.05 || w <= 0) {
		return '';
	}
	const k = Math.max(0, Math.min(r, w / 2, h));
	if (yEnd < yBase) {
		return `M${f(x)} ${f(yBase)}V${f(yEnd + k)}A${f(k)} ${f(k)} 0 0 1 ${f(x + k)} ${f(yEnd)}H${f(x + w - k)}A${f(k)} ${f(k)} 0 0 1 ${f(x + w)} ${f(yEnd + k)}V${f(yBase)}Z`;
	}
	return `M${f(x)} ${f(yBase)}V${f(yEnd - k)}A${f(k)} ${f(k)} 0 0 0 ${f(x + k)} ${f(yEnd)}H${f(x + w - k)}A${f(k)} ${f(k)} 0 0 0 ${f(x + w)} ${f(yEnd - k)}V${f(yBase)}Z`;
};

/** Horizontal: from xBase to xEnd at y..y+h. */
const hBar = (y: number, h: number, xBase: number, xEnd: number, r: number): string => {
	const w = Math.abs(xEnd - xBase);
	if (w < 0.05 || h <= 0) {
		return '';
	}
	const k = Math.max(0, Math.min(r, h / 2, w));
	if (xEnd > xBase) {
		return `M${f(xBase)} ${f(y)}H${f(xEnd - k)}A${f(k)} ${f(k)} 0 0 1 ${f(xEnd)} ${f(y + k)}V${f(y + h - k)}A${f(k)} ${f(k)} 0 0 1 ${f(xEnd - k)} ${f(y + h)}H${f(xBase)}Z`;
	}
	return `M${f(xBase)} ${f(y)}H${f(xEnd + k)}A${f(k)} ${f(k)} 0 0 0 ${f(xEnd)} ${f(y + k)}V${f(y + h - k)}A${f(k)} ${f(k)} 0 0 0 ${f(xEnd + k)} ${f(y + h)}H${f(xBase)}Z`;
};

const isHighlighted = (h: BarChartProps['highlight'], i: number, label: string): boolean => {
	if (h === undefined) {
		return false;
	}
	const list = Array.isArray(h) ? h : [h];
	return list.some((x) => x === i || x === label);
};

export const BarChart: React.FC<BarChartProps> = ({
	data,
	orientation = 'vertical',
	width,
	height,
	highlight,
	highlightAt,
	format,
	axis,
	ticks = 4,
	max,
	min,
	values = 'land',
	valuePosition = 'outside',
	sort = 'none',
	delay,
	duration,
	stagger,
	ease,
	color,
	neutral,
	negativeColor,
	axisLabel,
	labelSize,
	valueSize,
	barRadius,
	gap = 0.32,
	maxBar,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const box = useChartBox(width, height, delay);
	const W = box.width;
	const H = box.height;
	const type = useChartType();
	const q = useGraphicExit({exit, outDuration, outAt});
	const vertical = orientation === 'vertical';
	const showAxis = axis ?? vertical;
	const dur = duration ?? buildFrames('bar', fps);
	const step = stagger ?? at30(Math.max(3, t.motion.stagger), fps);
	const easing = ease ?? curves[t.motion.curve];
	const start0 = box.delay;
	const axisIn = buildFrames('axis', fps);

	const rows = useMemo(() => {
		// values that are not finite numbers (NaN, Infinity) are left out: one bad value never breaks the chart
		const withIndex = data.map((d, i) => ({...d, i})).filter((d) => Number.isFinite(d.value));
		if (sort === 'desc') {
			withIndex.sort((a, b) => b.value - a.value);
		} else if (sort === 'asc') {
			withIndex.sort((a, b) => a.value - b.value);
		}
		return withIndex;
	}, [data, sort]);
	const n = rows.length;
	const hasNeg = rows.some((r) => r.value < 0);
	const dmin = Math.min(0, Number.isFinite(min) ? (min as number) : 0, ...rows.map((r) => r.value));
	const dmax = Math.max(0, Number.isFinite(max) ? (max as number) : 0, ...rows.map((r) => r.value));
	const fmt = (v: number) => applyFormat(v, format);
	const fmtTick = tickFormat(format);

	const vs = valueSize ?? (vertical ? (n <= 5 ? 44 : n <= 8 ? 36 : 28) : n <= 6 ? 36 : n <= 10 ? 30 : 26);
	const ls = labelSize ?? (vertical ? (n <= 5 ? 30 : n <= 8 ? 26 : 22) : n <= 6 ? 30 : n <= 10 ? 26 : 22);
	const tickSize = 22;
	const base = color ?? t.colors.accent;
	const grey = neutral ?? neutralOf(t);
	const grid = gridOf(t);
	const neg = negativeColor ?? t.colors.negative;
	const anyHighlight = highlight !== undefined;
	const radius = Math.min(barRadius ?? t.radius * 0.5, 12);

	// the scale: zero always inside, nice round ends
	const scale = useMemo(() => {
		const s = scaleLinear().domain([dmin, dmax === dmin ? dmin + 1 : dmax]);
		return s.nice(Math.max(1, ticks));
	}, [dmin, dmax, ticks]);
	const tickValues = scale.ticks(Math.max(1, ticks));
	const maxTickW = showAxis ? Math.max(0, ...tickValues.map((v) => estimateLabelWidth(fmtTick(v), tickSize))) : 0;

	// per bar timing
	const timing = rows.map((_, k) => {
		const s = start0 + Math.round(axisIn * 0.5) + k * step;
		return {start: s, p: ramp(frame, s, dur, easing)};
	});
	// the exit shrinks bars last-in first-out
	const shrinkQ = (k: number) => (exit === 'shrink' ? Math.min(1, Math.max(0, q * 1.6 - ((n - 1 - k) / Math.max(1, n)) * 0.6)) : 0);
	const axisP = ramp(frame, start0, axisIn, curves.out);
	const fadeAll = exit === 'fade' || exit === 'shrink' ? 1 - q : 1;

	const colorOf = (r: (typeof rows)[number]): string => {
		const own = r.color ?? (r.value < 0 && !anyHighlight ? neg : base);
		if (!anyHighlight || isHighlighted(highlight, r.i, r.label)) {
			return anyHighlight ? (r.color ?? base) : own;
		}
		if (highlightAt === undefined) {
			return grey;
		}
		return interpolateColors(frame, [highlightAt, highlightAt + at30(12, fps)], [own, grey]);
	};

	const valueText = (r: (typeof rows)[number], p: number): string => {
		if (values === 'count') {
			return fmt(countValue(0, r.value, Math.min(1, Math.max(0, p)), decimalsFor(r.value, format)));
		}
		return fmt(r.value);
	};

	if (n === 0) {
		return null;
	}
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];

	if (vertical) {
		const catLines = (() => {
			const approxStep = (W - (showAxis ? maxTickW + 18 : 0)) / Math.max(1, n);
			return Math.max(...rows.map((r) => breakLabelLines(r.label, ls, approxStep * 0.94, 2).length), 1);
		})();
		const top = vs * 1.7 + (axisLabel && showAxis ? tickSize * 1.9 : 0);
		const bottom = ls * 1.22 * catLines + 18;
		const x0 = showAxis ? maxTickW + 18 : 0;
		const x1 = W - 2;
		const y0 = top;
		const y1 = H - bottom - (hasNeg ? vs * 1.5 : 0);
		const ys = scale.copy().range([y1, y0]);
		const band = scaleBand<number>()
			.domain(rows.map((_, k) => k))
			.range([x0, x1])
			.paddingInner(gap)
			.paddingOuter(gap * 0.5);
		const bw = Math.min(band.bandwidth(), maxBar ?? 190);
		const zeroY = ys(0);
		if (showAxis) {
			tickValues.forEach((v) => {
				const y = ys(v);
				if (v !== 0) {
					svg.push(<line key={`g${v}`} x1={x0} x2={x1} y1={y} y2={y} stroke={grid} strokeWidth={2} opacity={axisP * fadeAll} />);
				}
				html.push(
					<ChartLabel key={`t${v}`} x={x0 - 14} y={y} anchor="right" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP * fadeAll}}>
						{fmtTick(v)}
					</ChartLabel>,
				);
			});
			if (axisLabel) {
				html.push(
					<ChartLabel key="axisLabel" x={0} y={y0 - tickSize * 1.9 - vs * 0.2} anchor="top-left" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP * fadeAll}}>
						{axisLabel}
					</ChartLabel>,
				);
			}
		}
		rows.forEach((r, k) => {
			const {start, p} = timing[k];
			const grow = p * (1 - shrinkQ(k));
			const cx = (band(k) ?? 0) + band.bandwidth() / 2;
			const yEnd = ys(r.value * grow);
			const col = colorOf(r);
			svg.push(<path key={`b${k}`} d={vBar(cx - bw / 2, bw, zeroY, yEnd, radius)} fill={col} />);
			// category label: arrives with its bar
			const lp = ramp(frame, start, at30(12, fps), curves.out) * fadeAll;
			const lines = breakLabelLines(r.label, ls, band.step() * 0.94, 2);
			html.push(
				<ChartLabel key={`l${k}`} x={cx} y={y1 + (hasNeg ? vs * 1.5 : 0) + 14 + (1 - lp) * 10} anchor="top" style={{...type.label, fontSize: ls * unit, lineHeight: 1.22, textAlign: 'center', opacity: lp}}>
					{lines.map((ln, j) => (
						<div key={j}>{ln}</div>
					))}
				</ChartLabel>,
			);
			if (values !== 'none') {
				const up = r.value >= 0;
				const land = values === 'land' ? ramp(frame, start + dur * 0.62, at30(12, fps), curves.out) : Math.min(1, p * 4);
				const shown = land * fadeAll * (1 - shrinkQ(k));
				const hl = anyHighlight && isHighlighted(highlight, r.i, r.label);
				const inside = valuePosition === 'inside' && Math.abs(zeroY - yEnd) > vs * 1.8;
				const yLabel = inside ? (up ? yEnd + 12 : yEnd - 12) : up ? yEnd - 12 : yEnd + 12;
				const rise = values === 'land' ? (1 - land) * (up ? 14 : -14) : 0;
				html.push(
					<ChartLabel
						key={`v${k}`}
						x={cx}
						y={yLabel + rise}
						anchor={(inside ? !up : up) ? 'bottom' : 'top'}
						style={{
							...type.value,
							fontSize: vs * unit,
							lineHeight: 1,
							color: inside ? textColorOn(col, '#FFFFFF', t.colors.text) : hl ? t.colors.accent : t.colors.text,
							opacity: shown,
						}}
					>
						{valueText(r, p)}
					</ChartLabel>,
				);
			}
		});
		// the baseline draws across first
		svg.push(
			<line
				key="base"
				x1={x0}
				x2={x0 + (x1 - x0) * axisP}
				y1={zeroY}
				y2={zeroY}
				stroke={t.colors.text}
				strokeWidth={3}
				strokeLinecap="round"
				opacity={0.85 * fadeAll}
			/>,
		);
	} else {
		const labelW = Math.min(W * 0.36, Math.max(W * 0.12, Math.max(...rows.map((r) => Math.min(estimateLabelWidth(r.label, ls), W * 0.36))) + 26));
		const valueW = values === 'none' || valuePosition === 'inside' ? 8 : Math.max(...rows.map((r) => estimateLabelWidth(fmt(r.value), vs, true))) + 24;
		const top = showAxis ? tickSize * 2.2 + (axisLabel ? tickSize * 1.6 : 0) : 4;
		const x0 = labelW + (hasNeg ? valueW : 0);
		const x1 = W - valueW;
		const xs = scale.copy().range([x0, x1]);
		const band = scaleBand<number>()
			.domain(rows.map((_, k) => k))
			.range([top, H - 4])
			.paddingInner(gap)
			.paddingOuter(gap * 0.4);
		const bh = Math.min(band.bandwidth(), maxBar ?? 76);
		const zeroX = xs(0);
		if (showAxis) {
			tickValues.forEach((v) => {
				const x = xs(v);
				if (v !== 0) {
					svg.push(<line key={`g${v}`} x1={x} x2={x} y1={top - 6} y2={H - 4} stroke={grid} strokeWidth={2} opacity={axisP * fadeAll} />);
				}
				html.push(
					<ChartLabel key={`t${v}`} x={x} y={top - 14} anchor="bottom" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP * fadeAll}}>
						{fmtTick(v)}
					</ChartLabel>,
				);
			});
			if (axisLabel) {
				html.push(
					<ChartLabel key="axisLabel" x={x1} y={0} anchor="top-right" style={{...type.tick, fontSize: tickSize * unit, opacity: axisP * fadeAll}}>
						{axisLabel}
					</ChartLabel>,
				);
			}
		}
		rows.forEach((r, k) => {
			const {start, p} = timing[k];
			const grow = p * (1 - shrinkQ(k));
			const cy = (band(k) ?? 0) + band.bandwidth() / 2;
			const xEnd = xs(r.value * grow);
			const col = colorOf(r);
			svg.push(<path key={`b${k}`} d={hBar(cy - bh / 2, bh, zeroX, xEnd, radius)} fill={col} />);
			const lp = ramp(frame, start, at30(12, fps), curves.out) * fadeAll;
			html.push(
				<ChartLabel
					key={`l${k}`}
					x={labelW - 22 - (1 - lp) * 10}
					y={cy}
					anchor="right"
					maxWidth={labelW - 26}
					style={{...type.label, fontSize: ls * unit, lineHeight: 1.15, textAlign: 'right', opacity: lp}}
				>
					{r.label}
				</ChartLabel>,
			);
			if (values !== 'none') {
				const right = r.value >= 0;
				const land = values === 'land' ? ramp(frame, start + dur * 0.62, at30(12, fps), curves.out) : Math.min(1, p * 4);
				const shown = land * fadeAll * (1 - shrinkQ(k));
				const hl = anyHighlight && isHighlighted(highlight, r.i, r.label);
				const inside = valuePosition === 'inside' && Math.abs(xEnd - zeroX) > estimateLabelWidth(fmt(r.value), vs, true) + 36;
				const xLabel = inside ? (right ? xEnd - 16 : xEnd + 16) : right ? xEnd + 16 : xEnd - 16;
				const slide = values === 'land' ? (1 - land) * (right ? -12 : 12) : 0;
				html.push(
					<ChartLabel
						key={`v${k}`}
						x={xLabel + slide}
						y={cy}
						anchor={(inside ? !right : right) ? 'left' : 'right'}
						style={{
							...type.value,
							fontSize: vs * unit,
							lineHeight: 1,
							color: inside ? textColorOn(col, '#FFFFFF', t.colors.text) : hl ? t.colors.accent : t.colors.text,
							opacity: shown,
						}}
					>
						{valueText(r, p)}
					</ChartLabel>,
				);
			}
		});
		svg.push(
			<line
				key="base"
				x1={zeroX}
				x2={zeroX}
				y1={top - 4}
				y2={top - 4 + (H - top) * axisP}
				stroke={t.colors.text}
				strokeWidth={3}
				strokeLinecap="round"
				opacity={0.85 * fadeAll}
			/>,
		);
	}

	return (
		<ChartRoot width={W} height={H} svg={svg} style={{translate: exit === 'fade' ? `0 ${10 * unit * q}px` : undefined, ...style}}>
			{html}
		</ChartRoot>
	);
};
