// <Timeline>: a line that draws through time; each event arrives as the line reaches it (the dot pops, the date
// and title rise). Horizontal (events alternate above and below when they are close) or vertical (the default in
// 9:16). Positions are even, or true to time when every event has `at`.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {ArrowPath} from './Arrow';
import {ChartLabel, ChartRoot, useChartBox} from './chart';
import {frameAtProgress, useGraphicExit, type GraphicExitProps} from './timing';

export type TimelineEvent = {
	label: React.ReactNode; // the date or year
	title: React.ReactNode;
	text?: React.ReactNode; // one short line of detail
	at?: number; // a position on a number scale (a year, a day): used when every event has one
};

export type TimelineProps = GraphicExitProps & {
	events: TimelineEvent[];
	orientation?: 'horizontal' | 'vertical' | 'auto'; // auto: vertical in 9:16
	width?: number; // px at 1080
	height?: number;
	highlight?: number; // index of the event that matters most
	spacing?: 'even' | 'time'; // default: time when every event has `at`
	alternate?: boolean; // horizontal: events above and below the line (default: when they are close)
	arrow?: boolean; // the line ends in an arrow head (time goes on); default true
	delay?: number;
	duration?: number; // frames the line takes (default: 20 per event, at least 50)
	ease?: Ease; // default in-out
	lineWidth?: number; // px at 1080 (default 5)
	titleSize?: number; // px at 1080
	labelSize?: number;
	textSize?: number;
	style?: React.CSSProperties;
};

export const Timeline: React.FC<TimelineProps> = ({
	events,
	orientation = 'auto',
	width,
	height,
	highlight,
	spacing,
	alternate,
	arrow = true,
	delay,
	duration,
	ease = curves.inOut,
	lineWidth = 5,
	titleSize,
	labelSize,
	textSize,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, vertical: stageVertical} = useStage();
	const box = useChartBox(width, height, delay);
	const q = useGraphicExit({exit, outDuration, outAt});
	const W = box.width;
	const H = box.height;
	const n = events.length;
	const vert = orientation === 'vertical' || (orientation === 'auto' && stageVertical);
	const start = box.delay;
	const dur = duration ?? Math.max(at30(50, fps), at30(20, fps) * n);
	const fade = exit === 'none' ? 1 : 1 - q;
	// time spacing needs a finite `at` on every event; when every event shares one date they spread evenly instead
	const timed = events.every((e) => typeof e.at === 'number' && Number.isFinite(e.at));
	const useTime = timed && (spacing ?? 'time') === 'time';
	const ats = events.map((e, i) => (useTime ? (e.at as number) : i));
	const lo = Math.min(...ats);
	const hi = Math.max(...ats);
	const frac = (i: number) => (n === 1 ? 0.5 : useTime && hi > lo ? (ats[i] - lo) / (hi - lo) : i / (n - 1));
	// sizes read on a phone in 9:16, on a TV in 16:9
	const ts = titleSize ?? (vert ? 44 : 36);
	const ls0 = labelSize ?? (vert ? 30 : 28);
	const xs0 = textSize ?? (vert ? 30 : 26);
	if (n === 0) {
		return null;
	}
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];

	if (!vert) {
		const pad = Math.min(160, W / (n * 2));
		const x0 = 8;
		const x1 = W - 8;
		const ex0 = x0 + pad;
		const ex1 = x1 - pad - (arrow ? 20 : 0);
		const xs = events.map((_, i) => ex0 + frac(i) * (ex1 - ex0));
		const minGap = Math.min(...xs.slice(1).map((x, i) => x - xs[i]), W);
		const alt = alternate ?? minGap < 300;
		const colW = Math.max(160, Math.min(alt ? minGap * 1.8 : minGap * 0.92, 440));
		const yLine = alt ? H / 2 : H * 0.34;
		const p = ramp(frame, start, dur, ease);
		svg.push(
			<ArrowPath
				key="line"
				from={[x0, yLine]}
				to={[x1, yLine]}
				progress={p * (exit === 'undraw' ? 1 - q : 1)}
				head={arrow ? 'open' : 'none'}
				headSize={lineWidth * 4}
				strokeWidth={lineWidth}
				color={t.colors.text}
				opacity={fade * 0.9}
			/>,
		);
		events.forEach((e, i) => {
			const x = xs[i];
			const at = frameAtProgress((x - x0) / (x1 - x0), start, dur, ease);
			const pop = ramp(frame, at, at30(12, fps), curves.outBack) * fade;
			const rise = ramp(frame, at + at30(3, fps), at30(14, fps), curves.out) * fade;
			const hl = highlight === i;
			const r = hl ? 15 : 11;
			if (pop > 0) {
				if (hl) {
					svg.push(<circle key={`h${i}`} cx={x} cy={yLine} r={r * 2.1 * pop} fill={withOpacity(t.colors.accent, 0.18)} />);
				}
				svg.push(<circle key={`d${i}`} cx={x} cy={yLine} r={Math.max(0, r * pop)} fill={hl ? t.colors.accent : t.colors.bg} stroke={t.colors.accent} strokeWidth={5} />);
			}
			const above = alt && i % 2 === 1;
			const off = 38;
			html.push(
				<ChartLabel
					key={`e${i}`}
					x={x}
					y={above ? yLine - off - (1 - rise) * -14 : yLine + off + (1 - rise) * 14}
					anchor={above ? 'bottom' : 'top'}
					maxWidth={colW}
					style={{textAlign: 'center', opacity: rise, display: 'flex', flexDirection: above ? 'column-reverse' : 'column', gap: 6 * unit}}
				>
					{above ? (
						<>
							{e.text ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: xs0 * unit, lineHeight: 1.3, color: t.colors.muted}}>{e.text}</div> : null}
							<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ts * unit, lineHeight: 1.15, color: hl ? t.colors.accent : t.colors.text}}>{e.title}</div>
							<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ls0 * unit, color: t.colors.muted, fontVariantNumeric: 'tabular-nums', letterSpacing: `${t.tracking.caps * 0.5}em`}}>{e.label}</div>
						</>
					) : (
						<>
							<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ls0 * unit, color: t.colors.muted, fontVariantNumeric: 'tabular-nums', letterSpacing: `${t.tracking.caps * 0.5}em`}}>{e.label}</div>
							<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ts * unit, lineHeight: 1.15, color: hl ? t.colors.accent : t.colors.text}}>{e.title}</div>
							{e.text ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: xs0 * unit, lineHeight: 1.3, color: t.colors.muted}}>{e.text}</div> : null}
						</>
					)}
				</ChartLabel>,
			);
		});
	} else {
		const xL = 22;
		const y0 = 10;
		const y1 = H - 10;
		const pad = Math.min(90, H / (n * 2));
		const ey0 = y0 + pad * 0.6;
		const ey1 = y1 - pad - (arrow ? 22 : 0);
		const ys = events.map((_, i) => ey0 + frac(i) * (ey1 - ey0));
		const p = ramp(frame, start, dur, ease);
		svg.push(
			<ArrowPath
				key="line"
				from={[xL, y0]}
				to={[xL, y1]}
				progress={p * (exit === 'undraw' ? 1 - q : 1)}
				head={arrow ? 'open' : 'none'}
				headSize={lineWidth * 4}
				strokeWidth={lineWidth}
				color={t.colors.text}
				opacity={fade * 0.9}
			/>,
		);
		events.forEach((e, i) => {
			const y = ys[i];
			const at = frameAtProgress((y - y0) / (y1 - y0), start, dur, ease);
			const pop = ramp(frame, at, at30(12, fps), curves.outBack) * fade;
			const rise = ramp(frame, at + at30(3, fps), at30(14, fps), curves.out) * fade;
			const hl = highlight === i;
			const r = hl ? 15 : 11;
			if (pop > 0) {
				if (hl) {
					svg.push(<circle key={`h${i}`} cx={xL} cy={y} r={r * 2.1 * pop} fill={withOpacity(t.colors.accent, 0.18)} />);
				}
				svg.push(<circle key={`d${i}`} cx={xL} cy={y} r={Math.max(0, r * pop)} fill={hl ? t.colors.accent : t.colors.bg} stroke={t.colors.accent} strokeWidth={5} />);
			}
			html.push(
				<ChartLabel key={`e${i}`} x={xL + 48 + (1 - rise) * 16} y={y} anchor="left" maxWidth={W - xL - 60} style={{opacity: rise, display: 'flex', flexDirection: 'column', gap: 4 * unit}}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ls0 * unit, color: t.colors.muted, fontVariantNumeric: 'tabular-nums', letterSpacing: `${t.tracking.caps * 0.5}em`}}>{e.label}</div>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: ts * unit, lineHeight: 1.15, color: hl ? t.colors.accent : t.colors.text}}>{e.title}</div>
					{e.text ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: xs0 * unit, lineHeight: 1.3, color: t.colors.muted}}>{e.text}</div> : null}
				</ChartLabel>,
			);
		});
	}

	return (
		<ChartRoot width={W} height={H} svg={svg} style={style}>
			{html}
		</ChartRoot>
	);
};
