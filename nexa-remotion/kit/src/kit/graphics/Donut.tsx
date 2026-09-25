// <Donut> and <Pie>: slices sweep round clockwise from 12 o'clock, each label arrives when the sweep passes its
// slice, the centre can count up a total, and one slice can be pulled out and kept in colour.
import {arc as d3arc} from 'd3-shape';
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity, textColorOn, seriesColors} from './color';
import {ChartLabel, ChartRoot, estimateLabelWidth, useChartBox, useChartType} from './chart';
import {applyFormat, countValue, decimalsFor, type ValueFormatter} from './numbers';
import {buildFrames, frameAtProgress, useGraphicExit, type GraphicExitProps} from './timing';

export type SliceDatum = {label: string; value: number; color?: string};

export type DonutProps = GraphicExitProps & {
	data: SliceDatum[];
	width?: number; // px at 1080 (default: the ChartFrame area or the safe area)
	height?: number;
	radius?: number; // outer radius in px at 1080 (default: as big as the labels allow)
	thickness?: number; // ring thickness as a share of the radius (default 0.34; 1 is a pie)
	labels?: 'outside' | 'inside' | 'none';
	show?: 'percent' | 'value' | 'both'; // what each label says after the name
	format?: ValueFormatter; // for values
	center?: {value?: number | string; label?: string; format?: ValueFormatter} | 'total' | 'none'; // default 'total' on a donut
	centerLabel?: string; // caption under the total (default 'Total')
	highlight?: number | string; // index or label: pulled out, in colour; the rest grey
	padAngle?: number; // degrees between slices (default 1.2)
	cornerRadius?: number; // px at 1080 (default 6 on a donut)
	startAngle?: number; // degrees, 0 = 12 o'clock
	delay?: number;
	duration?: number; // frames of the sweep (default 48 at 30 fps)
	ease?: Ease; // default in-out
	labelSize?: number;
	valueSize?: number;
	style?: React.CSSProperties;
};

export const Donut: React.FC<DonutProps> = ({
	data,
	width,
	height,
	radius,
	thickness = 0.34,
	labels = 'outside',
	show = 'percent',
	format,
	center,
	centerLabel = 'Total',
	highlight,
	padAngle = 1.2,
	cornerRadius,
	startAngle = 0,
	delay,
	duration,
	ease = curves.inOut,
	labelSize = 26,
	valueSize = 36,
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
	const dur = duration ?? buildFrames('sweep', fps);
	const start = box.delay;
	const isPie = thickness >= 0.999;
	// negative, NaN and infinite values count as 0 (no slice, no label)
	const vals = data.map((d) => (Number.isFinite(d.value) ? Math.max(0, d.value) : 0));
	const sum = vals.reduce((a, b) => a + b, 0);
	const total = sum || 1; // divisor only
	const hiRaw = highlight === undefined ? -1 : typeof highlight === 'number' ? highlight : data.findIndex((d) => d.label === highlight);
	const hi = Number.isInteger(hiRaw) && hiRaw >= 0 && hiRaw < data.length ? hiRaw : -1;
	const colors = seriesColors(t, data.length, hi >= 0 ? hi : undefined);
	const fmt = (v: number) => applyFormat(v, format);
	const pctText = (v: number) => applyFormat((v / total) * 100, {decimals: (v / total) * 100 < 10 ? 1 : 0, suffix: '%', digits: typeof format === 'object' ? format.digits : undefined});
	const valText = (v: number) => (show === 'value' ? fmt(v) : show === 'both' ? `${pctText(v)} · ${fmt(v)}` : pctText(v));

	const labelSpace =
		labels === 'outside' ? Math.max(0, ...data.map((d, i) => Math.max(estimateLabelWidth(d.label, labelSize), estimateLabelWidth(valText(vals[i]), valueSize, true)))) + 58 : 12;
	const ro = radius ?? Math.max(60, Math.min(H / 2 - 14, W / 2 - labelSpace));
	const ri = isPie ? 0 : ro * (1 - thickness);
	const cx = W / 2;
	const cy = H / 2;
	const a0 = (startAngle * Math.PI) / 180;
	const fadeAll = exit === 'none' ? 1 : 1 - q;
	const unsweep = exit === 'shrink' || exit === 'undraw' ? q : 0;
	const p = ramp(frame, start, dur, ease) * (1 - unsweep);
	const reveal = a0 + p * Math.PI * 2;
	const slices = useMemo(() => {
		let acc = 0;
		return vals.map((v, i) => {
			const s = a0 + (acc / total) * Math.PI * 2;
			acc += v;
			const e = a0 + (acc / total) * Math.PI * 2;
			return {i, s, e, mid: (s + e) / 2, v};
		});
	}, [vals, total, a0]);
	const pull = hi >= 0 ? ramp(frame, start + dur, at30(14, fps), curves.outBack) * (1 - unsweep) : 0;
	const pad = ((isPie ? padAngle * 0.6 : padAngle) * Math.PI) / 180;
	const cr = cornerRadius ?? (isPie ? 0 : Math.min(8, (ro - ri) * 0.18));

	if (!data.length) {
		return null;
	}
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];
	if (sum <= 0 && reveal > a0) {
		// nothing to share out: an empty track, so the chart still reads as a chart at zero
		const track = d3arc<unknown>().innerRadius(ri).outerRadius(ro).startAngle(a0).endAngle(reveal)(null) ?? '';
		svg.push(<path key="track" d={track} transform={`translate(${cx} ${cy})`} fill={withOpacity(t.colors.muted, t.dark ? 0.22 : 0.16)} opacity={fadeAll} />);
	}
	slices.forEach((sl) => {
		if (reveal <= sl.s + 1e-4 || sl.v <= 0) {
			return;
		}
		const end = Math.min(sl.e, reveal);
		const off = sl.i === hi ? pull * Math.min(18, ro * 0.07) : 0;
		const gen = d3arc<unknown>()
			.innerRadius(ri)
			.outerRadius(ro)
			.startAngle(sl.s)
			.endAngle(end)
			.padAngle(end - sl.s > pad * 2 ? pad : 0)
			.cornerRadius(cr);
		const d = gen(null) ?? '';
		svg.push(
			<path
				key={`s${sl.i}`}
				d={d}
				fill={data[sl.i].color ?? colors[sl.i]}
				transform={`translate(${cx + Math.sin(sl.mid) * off} ${cy - Math.cos(sl.mid) * off})`}
				opacity={fadeAll}
			/>,
		);
	});

	// labels: arrive as the sweep passes each slice's middle
	if (labels !== 'none') {
		type L = {i: number; side: 1 | -1; x: number; y: number; ax: number; ay: number; at: number};
		const items: L[] = slices
			.filter((sl) => sl.v > 0)
			.map((sl) => {
				const side: 1 | -1 = Math.sin(sl.mid) >= 0 ? 1 : -1;
				const rr = ro + 12;
				return {
					i: sl.i,
					side,
					ax: cx + Math.sin(sl.mid) * rr,
					ay: cy - Math.cos(sl.mid) * rr,
					x: cx + side * (ro + 34),
					y: cy - Math.cos(sl.mid) * (ro + 22),
					at: frameAtProgress((sl.mid - a0) / (Math.PI * 2), start, dur, ease),
				};
			});
		if (labels === 'outside') {
			// keep labels on each side from overlapping
			const gap = labelSize * 1.2 + valueSize * 1.15;
			for (const side of [1, -1] as const) {
				const group = items.filter((it) => it.side === side).sort((a, b) => a.y - b.y);
				for (let k = 1; k < group.length; k++) {
					group[k].y = Math.max(group[k].y, group[k - 1].y + gap);
				}
				const over = group.length ? group[group.length - 1].y + gap / 2 - H : 0;
				if (over > 0) {
					group.forEach((g) => (g.y -= over));
				}
				for (let k = group.length - 2; k >= 0; k--) {
					group[k].y = Math.min(group[k].y, group[k + 1].y - gap);
				}
				// never above or below the box: when a side has too many labels they may crowd, but stay inside
				group.forEach((g) => (g.y = Math.min(H - gap / 2, Math.max(gap / 2, g.y))));
			}
		}
		items.forEach((it) => {
			const lp = ramp(frame, it.at, at30(12, fps), curves.out) * fadeAll * (1 - unsweep);
			if (lp <= 0) {
				return;
			}
			const d = data[it.i];
			const col = d.color ?? colors[it.i];
			if (labels === 'inside') {
				const sl = slices[it.i];
				if (sl.e - sl.s < 0.32) {
					return;
				}
				const rm = isPie ? ro * 0.62 : (ro + ri) / 2;
				html.push(
					<ChartLabel key={`in${it.i}`} x={cx + Math.sin(sl.mid) * rm} y={cy - Math.cos(sl.mid) * rm} anchor="center" style={{...type.value, fontSize: valueSize * 0.8 * unit, color: textColorOn(col, '#FFFFFF', t.colors.text), opacity: lp}}>
						{pctText(d.value)}
					</ChartLabel>,
				);
				return;
			}
			// out along the slice's middle, then across to the label column
			const sl = slices[it.i];
			const ex = cx + Math.sin(sl.mid) * (ro + 26);
			svg.push(
				<polyline
					key={`ln${it.i}`}
					points={`${it.ax},${it.ay} ${ex},${it.y} ${it.x},${it.y}`}
					fill="none"
					stroke={withOpacity(t.colors.text, t.dark ? 0.4 : 0.32)}
					strokeWidth={2}
					strokeLinejoin="round"
					opacity={lp}
				/>,
			);
			html.push(
				<ChartLabel key={`lb${it.i}`} x={it.x + it.side * 10} y={it.y} anchor={it.side > 0 ? 'left' : 'right'} style={{opacity: lp, textAlign: it.side > 0 ? 'left' : 'right', lineHeight: 1.15}}>
					<div style={{...type.tick, fontSize: labelSize * unit, color: t.colors.muted}}>{d.label}</div>
					<div style={{...type.value, fontSize: valueSize * unit, color: it.i === hi ? t.colors.accent : t.colors.text}}>{valText(d.value)}</div>
				</ChartLabel>,
			);
		});
	}

	// the centre
	const ctr = center ?? (isPie ? 'none' : 'total');
	if (ctr !== 'none' && !isPie) {
		const cp = ramp(frame, start + dur * 0.3, dur * 0.8, curves.outCubic) * fadeAll;
		const obj = ctr === 'total' ? {value: sum, label: centerLabel, format} : ctr;
		const shown =
			typeof obj.value === 'number'
				? applyFormat(countValue(0, obj.value, cp, decimalsFor(obj.value, obj.format ?? format)), obj.format ?? format)
				: (obj.value ?? '');
		const big = Math.min(ri * 0.52, 110);
		html.push(
			<ChartLabel key="ctr" x={cx} y={cy} anchor="center" style={{textAlign: 'center', opacity: Math.min(1, cp * 3), lineHeight: 1.05}}>
				<div style={{...type.value, fontFamily: t.type.display, fontWeight: t.weights.display, letterSpacing: `${t.tracking.display}em`, fontSize: big * unit}}>{shown}</div>
				{obj.label ? <div style={{...type.tick, fontSize: Math.max(20, big * 0.3) * unit, marginTop: 6 * unit}}>{obj.label}</div> : null}
			</ChartLabel>,
		);
	}

	return (
		<ChartRoot width={W} height={H} svg={svg} style={style}>
			{html}
		</ChartRoot>
	);
};

/** A pie: a donut with no hole and no centre total. */
export const Pie: React.FC<DonutProps> = (props) => <Donut thickness={1} center="none" {...props} />;
