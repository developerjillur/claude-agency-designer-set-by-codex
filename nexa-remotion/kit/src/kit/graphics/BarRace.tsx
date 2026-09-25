// <BarRace>: the bar chart race. Values move between snapshots (years, months), the bars re-sort as they pass
// each other, and rank changes glide instead of jumping (the rank is averaged over the last few frames, which is a
// pure function of the frame). The scale always starts at zero and follows the current leader.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity, neutralOf, seriesColors} from './color';
import {ChartLabel, ChartRoot, estimateLabelWidth, useChartBox, useChartType} from './chart';
import {countValue, decimalsOf, formatValue, type ValueFormatter} from './numbers';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type RaceSnapshot = {label: string; values: Record<string, number>};

export type BarRaceProps = GraphicExitProps & {
	snapshots: RaceSnapshot[]; // in time order; a name missing from a snapshot counts as 0
	top?: number; // bars shown (default 8; keep it at 12 or fewer)
	width?: number; // px at 1080
	height?: number;
	step?: number; // frames from one snapshot to the next (default 45 at 30 fps)
	hold?: number; // frames each snapshot rests before moving on (default 10)
	delay?: number;
	ease?: Ease; // each step (default in-out)
	format?: ValueFormatter;
	colors?: Record<string, string>; // a colour per name
	highlight?: string; // one name kept in the accent, the rest grey
	periodLabel?: boolean; // the snapshot label, big in the corner (default true)
	smoothing?: number; // frames a rank change takes (default 8)
	labelSize?: number;
	style?: React.CSSProperties;
};

/** Frames a race needs: its steps plus a final hold. */
export const barRaceFrames = (snapshots: number, step = 45, hold = 10, delay = 0): number =>
	delay + Math.max(0, snapshots - 1) * step + hold + 30;

/** A race shows sizes: negative, NaN and infinite values count as 0. */
const size = (v: number | undefined): number => (v !== undefined && Number.isFinite(v) ? Math.max(0, v) : 0);

export const BarRace: React.FC<BarRaceProps> = ({
	snapshots,
	top = 8,
	width,
	height,
	step,
	hold,
	delay,
	ease = curves.inOut,
	format,
	colors,
	highlight,
	periodLabel = true,
	smoothing,
	labelSize = 28,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const box = useChartBox(width, height, delay);
	const type = useChartType();
	const q = useGraphicExit({exit, outDuration, outAt});
	const W = box.width;
	const H = box.height;
	const stepF = Math.max(1, step ?? at30(45, fps));
	const holdF = Math.min(stepF - 1, hold ?? at30(10, fps));
	const smooth = Math.max(1, smoothing ?? at30(8, fps));
	const start = box.delay;
	const fade = exit === 'none' ? 1 : 1 - q;
	// in-between values keep the decimals the snapshots have (no 42.594M while it moves)
	const dec = useMemo(() => Math.max(0, ...snapshots.flatMap((sn) => Object.values(sn.values).filter(Number.isFinite).map(decimalsOf))), [snapshots]);
	const fmt = (v: number) =>
		typeof format === 'function' ? format(v) : formatValue(countValue(0, v, 1, format?.decimals ?? dec), {...format, decimals: format?.decimals ?? dec});

	const names = useMemo(() => {
		const out: string[] = [];
		snapshots.forEach((s) => Object.keys(s.values).forEach((k) => !out.includes(k) && out.push(k)));
		return out;
	}, [snapshots]);
	const palette = useMemo(() => seriesColors(t, Math.max(8, names.length)), [t, names.length]);
	if (!snapshots.length || !names.length) {
		return null;
	}
	const colorOf = (name: string, i: number): string => {
		if (highlight !== undefined) {
			return name === highlight ? t.colors.accent : neutralOf(t);
		}
		return colors?.[name] ?? palette[i % palette.length];
	};

	// the values at a (fractional) time: hold, then ease to the next snapshot
	const valuesAt = (f: number): {vals: number[]; seg: number; u: number} => {
		const local = Math.max(0, f - start);
		const last = snapshots.length - 1;
		const seg = Math.min(last, Math.floor(local / stepF));
		if (seg >= last) {
			return {vals: names.map((n) => size(snapshots[last]?.values[n])), seg: last, u: 0};
		}
		const inSeg = local - seg * stepF;
		const u = inSeg <= holdF ? 0 : ease(Math.min(1, (inSeg - holdF) / (stepF - holdF)));
		const a = snapshots[seg].values;
		const b = snapshots[seg + 1].values;
		return {vals: names.map((n) => size(a[n]) + (size(b[n]) - size(a[n])) * u), seg, u};
	};
	const ranksAt = (f: number): number[] => {
		const {vals} = valuesAt(f);
		const order = names.map((_, i) => i).sort((x, y) => vals[y] - vals[x] || x - y);
		const r = new Array<number>(names.length);
		order.forEach((idx, k) => (r[idx] = k));
		return r;
	};
	// a rank that glides: the mean of the last `smooth` frames' ranks
	const smoothRank = names.map(() => 0);
	for (let j = 0; j < smooth; j++) {
		const r = ranksAt(frame - j);
		r.forEach((v, i) => (smoothRank[i] += v / smooth));
	}
	const {vals, seg, u} = valuesAt(frame);
	const lead = Math.max(1e-9, ...vals);
	const appear = ramp(frame, start - at30(10, fps), at30(14, fps), curves.out) * fade;

	const nameW = Math.min(W * 0.3, Math.max(...names.map((n) => estimateLabelWidth(n, labelSize))) + 24);
	const valueW = Math.max(...names.map((_, i) => estimateLabelWidth(fmt(Math.max(0, ...snapshots.map((s) => size(s.values[names[i]])))), labelSize, true))) + 20;
	const x0 = nameW;
	const x1 = W - valueW;
	const rows = Math.max(1, Math.min(top, names.length));
	const rowH = H / rows;
	const barH = Math.min(rowH * 0.72, 84);
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];
	// the bigger value is drawn last, so a bar that overtakes passes in front
	const drawOrder = names.map((_, i) => i).sort((a, b) => vals[a] - vals[b]);
	drawOrder.forEach((i) => {
		const name = names[i];
		const r = smoothRank[i];
		if (r > rows + 0.5) {
			return;
		}
		// bars leaving the top N fade as they slide out of the last row
		const vis = Math.min(1, Math.max(0, rows - r + 0.5)) * appear;
		const y = r * rowH + (rowH - barH) / 2;
		const w = Math.max(0, ((x1 - x0) * vals[i]) / (lead * 1.02));
		const col = colorOf(name, i);
		const k = Math.min(10, barH / 2);
		svg.push(
			<path
				key={`b${name}`}
				d={w <= 0.5 ? '' : `M${x0} ${y}H${x0 + w - k}A${k} ${k} 0 0 1 ${x0 + w} ${y + k}V${y + barH - k}A${k} ${k} 0 0 1 ${x0 + w - k} ${y + barH}H${x0}Z`}
				fill={col}
				opacity={vis}
			/>,
		);
		html.push(
			<ChartLabel key={`n${name}`} x={x0 - 16} y={y + barH / 2} anchor="right" style={{...type.label, fontSize: labelSize * unit, opacity: vis}}>
				{name}
			</ChartLabel>,
		);
		html.push(
			<ChartLabel key={`v${name}`} x={x0 + w + 14} y={y + barH / 2} anchor="left" style={{...type.value, fontSize: labelSize * unit, opacity: vis, color: highlight === name ? t.colors.accent : t.colors.text}}>
				{fmt(vals[i])}
			</ChartLabel>,
		);
	});
	svg.push(<line key="base" x1={x0} x2={x0} y1={0} y2={H} stroke={t.colors.text} strokeWidth={3} opacity={0.85 * appear} />);
	if (periodLabel && snapshots.length) {
		const cur = snapshots[Math.min(snapshots.length - 1, u > 0.5 ? seg + 1 : seg)].label;
		const big = Math.min(H * 0.22, 180);
		html.push(
			<ChartLabel
				key="period"
				x={W - 8}
				y={H - 8}
				anchor="bottom-right"
				style={{
					fontFamily: t.type.display,
					fontWeight: t.weights.display,
					fontSize: big * unit,
					lineHeight: 1,
					letterSpacing: `${t.tracking.display}em`,
					color: withOpacity(t.colors.text, t.dark ? 0.28 : 0.2),
					fontVariantNumeric: 'tabular-nums',
					opacity: appear,
				}}
			>
				{cur}
			</ChartLabel>,
		);
	}
	return (
		<ChartRoot width={W} height={H} svg={svg} style={style}>
			{html}
		</ChartRoot>
	);
};
