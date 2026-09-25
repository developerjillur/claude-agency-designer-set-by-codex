// <Comparison>: A against B. 'bars': two big numbers with bars on one shared scale from zero (side by side, or
// stacked in 9:16); 'share': one bar split into the two parts of a whole. The winner keeps the accent.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {neutralOf} from './color';
import {useChartBox} from './chart';
import {countValue, decimalsFor, formatValue, type ValueFormat} from './numbers';
import {buildFrames, useGraphicExit, type GraphicExitProps} from './timing';

export type CompareSide = {label: React.ReactNode; value: number; color?: string; note?: React.ReactNode};

export type ComparisonProps = GraphicExitProps & {
	a: CompareSide;
	b: CompareSide;
	format?: ValueFormat;
	mode?: 'bars' | 'share';
	winner?: 'a' | 'b' | 'auto' | 'none'; // who keeps the accent (auto: the larger, or the smaller with lowerIsBetter)
	lowerIsBetter?: boolean;
	vs?: string; // the word between them (default 'vs')
	layout?: 'row' | 'column' | 'auto'; // bars side by side or stacked (auto: stacked in 9:16)
	width?: number; // px at 1080
	height?: number;
	delay?: number;
	duration?: number;
	ease?: Ease;
	numberSize?: number; // px at 1080
	style?: React.CSSProperties;
};

/** A value that is not a finite number shows as 0 rather than breaking the layout. */
const finiteSide = (s: CompareSide): CompareSide => (Number.isFinite(s.value) ? s : {...s, value: 0});

export const Comparison: React.FC<ComparisonProps> = ({
	a: aIn,
	b: bIn,
	format = {},
	mode = 'bars',
	winner = 'auto',
	lowerIsBetter = false,
	vs = 'vs',
	layout = 'auto',
	width,
	height,
	delay,
	duration,
	ease = curves.outCubic,
	numberSize,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps, vertical} = useStage();
	const a = finiteSide(aIn);
	const b = finiteSide(bIn);
	const box = useChartBox(width, height, delay);
	const q = useGraphicExit({exit, outDuration, outAt});
	const W = box.width;
	const H = box.height;
	const start = box.delay;
	const dur = duration ?? buildFrames('count', fps);
	const fade = exit === 'none' ? 1 : 1 - q;
	const win = winner === 'auto' ? (a.value === b.value ? 'none' : (a.value > b.value) !== lowerIsBetter ? 'a' : 'b') : winner;
	const grey = neutralOf(t);
	const colA = a.color ?? (win === 'b' ? grey : t.colors.accent);
	const colB = b.color ?? (win === 'a' ? grey : win === 'none' ? t.colors.accent2 : t.colors.accent);
	const pA = ramp(frame, start, dur, ease);
	const pB = ramp(frame, start + at30(8, fps), dur, ease);
	const num = (side: CompareSide, p: number) => formatValue(countValue(0, side.value, p, decimalsFor(side.value, format)), format);
	const numStyle = (size: number, col: string): React.CSSProperties => ({
		fontFamily: t.type.display,
		fontWeight: t.weights.display,
		fontSize: size * unit,
		lineHeight: 1,
		letterSpacing: `${Math.max(t.tracking.display, -0.03)}em`,
		color: col,
		fontVariantNumeric: 'tabular-nums',
		whiteSpace: 'nowrap',
	});
	const labelStyle: React.CSSProperties = {fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 32 * unit, color: t.colors.muted, lineHeight: 1.2};
	const noteStyle: React.CSSProperties = {fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 26 * unit, color: t.colors.muted, lineHeight: 1.3};

	if (mode === 'share') {
		const sum = Math.max(0, a.value) + Math.max(0, b.value);
		const total = Math.max(1e-9, sum);
		const shareA = Math.max(0, a.value) / total;
		const barH = Math.min(120, H * 0.22);
		const wipe = ramp(frame, start, dur, curves.inOut);
		const appear = ramp(frame, start, at30(10, fps), curves.out);
		const lp = ramp(frame, start + dur * 0.6, at30(12, fps), curves.out) * fade;
		// each share counts while the wipe crosses its own part of the bar
		const pA = Math.min(1, wipe / Math.max(1e-6, shareA));
		const pB = Math.max(0, Math.min(1, (wipe - shareA) / Math.max(1e-6, 1 - shareA)));
		// nothing to share (both zero): 0% and 0%, no bar
		const pct = (s: number, p: number) => formatValue(sum > 0 ? countValue(0, s * 100, p, 0) : 0, {suffix: '%', digits: format.digits});
		const size = numberSize ?? Math.min(120, H * 0.26);
		return (
			<div style={{position: 'relative', width: W * unit, height: H * unit, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 26 * unit, opacity: fade * appear, ...style}}>
				<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
					<div style={numStyle(size, colA)}>{pct(shareA, pA)}</div>
					<div style={{...numStyle(size, colB), opacity: Math.min(1, pB * 4)}}>{pct(1 - shareA, pB)}</div>
				</div>
				<div style={{position: 'relative', height: barH * unit, borderRadius: Math.min(t.radius, barH / 2) * unit, overflow: 'hidden', background: 'transparent'}}>
					{/* one wipe from left to right reveals A, then B after a hairline gap */}
					<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${Math.min(wipe, shareA) * 100}%`, background: colA}} />
					{sum > 0 && wipe > shareA ? (
						<div
							style={{
								position: 'absolute',
								left: `calc(${shareA * 100}% + ${4 * unit}px)`,
								top: 0,
								bottom: 0,
								width: `max(0px, calc(${(wipe - shareA) * 100}% - ${4 * unit}px))`,
								background: colB,
							}}
						/>
					) : null}
				</div>
				<div style={{display: 'flex', justifyContent: 'space-between', opacity: lp}}>
					<div style={labelStyle}>{a.label}</div>
					<div style={{...labelStyle, textAlign: 'right'}}>{b.label}</div>
				</div>
			</div>
		);
	}

	const stacked = layout === 'column' || (layout === 'auto' && vertical);
	const maxV = Math.max(Math.abs(a.value), Math.abs(b.value), 1e-9);
	const size = numberSize ?? (stacked ? Math.min(150, H * 0.16) : Math.min(170, W * 0.1));
	const barH = stacked ? 44 : 40;
	const col = (side: CompareSide, c: string, p: number, key: string, isWinner: boolean) => {
		const lp = ramp(frame, start + (key === 'a' ? 0 : at30(8, fps)), at30(12, fps), curves.out) * fade;
		const appear = ramp(frame, start + (key === 'a' ? 0 : at30(8, fps)), at30(10, fps), curves.out);
		const colW = stacked ? W : (W - 150) / 2;
		const share = Math.abs(side.value) / maxV;
		return (
			<div key={key} style={{display: 'flex', flexDirection: 'column', gap: 18 * unit, width: colW * unit, opacity: appear, translate: `0 ${(1 - appear) * 16 * unit}px`}}>
				<div style={{...labelStyle, opacity: lp, color: isWinner ? t.colors.text : t.colors.muted}}>{side.label}</div>
				<div style={numStyle(size, isWinner ? t.colors.text : t.colors.muted)}>{num(side, p)}</div>
				<div style={{position: 'relative', height: barH * unit, width: colW * unit}}>
					<div style={{position: 'absolute', inset: 0, borderRadius: barH * unit, background: t.dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'}} />
					<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${share * p * 100}%`, borderRadius: barH * unit, background: c}} />
				</div>
				{side.note ? <div style={{...noteStyle, opacity: ramp(frame, start + dur, at30(12, fps), curves.out) * fade}}>{side.note}</div> : null}
			</div>
		);
	};
	const vsP = ramp(frame, start + at30(4, fps), at30(14, fps), curves.outBack) * fade;
	const vsEl = (
		<div
			style={{
				width: 96 * unit,
				height: 96 * unit,
				borderRadius: 999,
				border: `${3 * unit}px solid ${t.colors.line}`,
				background: t.colors.surface,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				fontFamily: t.type.display,
				fontWeight: t.weights.display,
				fontSize: 34 * unit,
				color: t.colors.muted,
				scale: `${Math.max(0, vsP)}`,
				flexShrink: 0,
				textTransform: t.caps ? 'uppercase' : 'none',
			}}
		>
			{vs}
		</div>
	);
	return (
		<div
			style={{
				position: 'relative',
				width: W * unit,
				height: H * unit,
				display: 'flex',
				flexDirection: stacked ? 'column' : 'row',
				alignItems: stacked ? 'flex-start' : 'center',
				justifyContent: stacked ? 'center' : 'space-between',
				gap: (stacked ? 40 : 0) * unit,
				opacity: fade,
				...style,
			}}
		>
			{col(a, colA, pA, 'a', win === 'a' || win === 'none')}
			{stacked ? null : vsEl}
			{col(b, colB, pB, 'b', win === 'b' || win === 'none')}
		</div>
	);
};
