// <ProgressRing> and <ProgressBar>: a share of something, filling from zero with the number counting in step.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {countValue, decimalsFor, formatValue, type ValueFormat} from './numbers';
import {buildFrames, useGraphicExit, type GraphicExitProps} from './timing';

export type ProgressRingProps = GraphicExitProps & {
	value: number; // 0 to 1, or a count out of `max`
	max?: number;
	size?: number; // diameter in px at 1080 (default 300)
	thickness?: number; // px at 1080 (default 9% of the size)
	color?: string;
	track?: string;
	label?: 'percent' | 'value' | 'none' | React.ReactNode; // the centre (default percent)
	sublabel?: React.ReactNode; // a caption under the centre number
	format?: ValueFormat; // for label 'value' (and digits for 'percent')
	delay?: number;
	duration?: number; // frames (default 42 at 30 fps)
	ease?: Ease;
	style?: React.CSSProperties;
};

export const ProgressRing: React.FC<ProgressRingProps> = ({
	value,
	max = 1,
	size = 300,
	thickness,
	color,
	track,
	label = 'percent',
	sublabel,
	format = {},
	delay = 0,
	duration,
	ease = curves.outCubic,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const q = useGraphicExit({exit, outDuration, outAt});
	const dur = duration ?? buildFrames('count', fps);
	const share = Math.min(1, Math.max(0, max ? value / max : 0));
	const unfill = exit === 'shrink' || exit === 'undraw' ? q : 0;
	const p = ramp(frame, delay, dur, ease) * (1 - unfill);
	const th = thickness ?? size * 0.09;
	const r = (size - th) / 2;
	const c = size / 2;
	const col = color ?? t.colors.accent;
	const shown = share * p;
	const center =
		label === 'percent'
			? formatValue(countValue(0, share * 100, p, 0), {suffix: '%', digits: format.digits})
			: label === 'value'
				? formatValue(countValue(0, value, p, decimalsFor(value, format)), format)
				: label === 'none'
					? null
					: label;
	const appear = ramp(frame, delay, at30(8, fps), curves.out);
	return (
		<div style={{position: 'relative', width: size * unit, height: size * unit, opacity: appear * (exit === 'fade' ? 1 - q : 1), flexShrink: 0, ...style}}>
			<svg viewBox={`0 0 ${size} ${size}`} width={size * unit} height={size * unit} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<circle cx={c} cy={c} r={r} fill="none" stroke={track ?? withOpacity(t.colors.text, t.dark ? 0.14 : 0.08)} strokeWidth={th} />
				{shown > 0.002 ? (
					<circle
						cx={c}
						cy={c}
						r={r}
						fill="none"
						stroke={col}
						strokeWidth={th}
						strokeLinecap="round"
						pathLength={1}
						strokeDasharray={shown >= 0.9999 ? undefined : `${shown} 2`}
						transform={`rotate(-90 ${c} ${c})`}
					/>
				) : null}
			</svg>
			{center !== null ? (
				<div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
					<div
						style={{
							fontFamily: t.type.display,
							fontWeight: t.weights.display,
							fontSize: size * 0.24 * unit,
							lineHeight: 1,
							letterSpacing: `${Math.max(t.tracking.display, -0.03)}em`,
							color: t.colors.text,
							fontVariantNumeric: 'tabular-nums',
						}}
					>
						{center}
					</div>
					{sublabel ? (
						<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: Math.max(20, size * 0.075) * unit, color: t.colors.muted, marginTop: size * 0.03 * unit, maxWidth: size * 0.62 * unit, lineHeight: 1.2}}>
							{sublabel}
						</div>
					) : null}
				</div>
			) : null}
		</div>
	);
};

export type ProgressBarProps = GraphicExitProps & {
	value: number; // 0 to 1, or a count out of `max`
	max?: number;
	width?: number; // px at 1080 (default 760)
	thickness?: number; // px at 1080 (default 22)
	label?: React.ReactNode; // above the bar on the left
	showValue?: 'percent' | 'value' | 'none'; // above the bar on the right (default percent)
	format?: ValueFormat;
	segments?: number; // split into this many blocks (steps of a process)
	color?: string;
	track?: string;
	delay?: number;
	duration?: number;
	ease?: Ease;
	style?: React.CSSProperties;
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
	value,
	max = 1,
	width = 760,
	thickness = 22,
	label,
	showValue = 'percent',
	format = {},
	segments = 0,
	color,
	track,
	delay = 0,
	duration,
	ease = curves.outCubic,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const q = useGraphicExit({exit, outDuration, outAt});
	const dur = duration ?? buildFrames('count', fps);
	const share = Math.min(1, Math.max(0, max ? value / max : 0));
	const p = ramp(frame, delay, dur, ease) * (exit === 'shrink' ? 1 - q : 1);
	const appear = ramp(frame, delay, at30(10, fps), curves.out);
	const col = color ?? t.colors.accent;
	const tr = track ?? withOpacity(t.colors.text, t.dark ? 0.14 : 0.08);
	const w = width * unit;
	const h = thickness * unit;
	const fillW = w * share * p;
	const valueText =
		showValue === 'percent'
			? formatValue(countValue(0, share * 100, p, 0), {suffix: '%', digits: format.digits})
			: showValue === 'value'
				? formatValue(countValue(0, value, p, decimalsFor(value, format)), format)
				: '';
	const gap = 8 * unit;
	const segW = segments > 0 ? (w - gap * (segments - 1)) / segments : w;
	return (
		<div style={{width: w, opacity: appear * (exit === 'fade' ? 1 - q : 1), ...style}}>
			{label || showValue !== 'none' ? (
				<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 * unit, gap: 20 * unit}}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 30 * unit, color: t.colors.text}}>{label}</div>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 30 * unit, color: t.colors.text, fontVariantNumeric: 'tabular-nums'}}>{valueText}</div>
				</div>
			) : null}
			<div style={{position: 'relative', width: w, height: h}}>
				{segments > 0 ? (
					Array.from({length: segments}, (_, i) => {
						const x = i * (segW + gap);
						const filled = Math.min(segW, Math.max(0, fillW - i * (segW + gap)));
						return (
							<div key={i} style={{position: 'absolute', left: x, top: 0, width: segW, height: h, borderRadius: h / 2, background: tr, overflow: 'hidden'}}>
								<div style={{width: filled, height: h, background: col, borderRadius: h / 2}} />
							</div>
						);
					})
				) : (
					<div style={{position: 'absolute', inset: 0, borderRadius: h / 2, background: tr, overflow: 'hidden'}}>
						<div style={{width: fillW, height: h, background: col, borderRadius: h / 2}} />
					</div>
				)}
			</div>
		</div>
	);
};
