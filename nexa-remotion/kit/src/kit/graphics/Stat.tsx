// <Stat>: one big number that counts up (or rolls like an odometer) with its own formatting, tabular digits, a
// caption and an optional change pill. The width is reserved for the final number, so nothing shifts while it
// counts.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {ICONS} from './icons';
import {countValue, decimalsFor, formatValue, type ValueFormat} from './numbers';
import {buildFrames, useGraphicExit, type GraphicExitProps} from './timing';

export type StatProps = GraphicExitProps & {
	value: number;
	from?: number; // count from (default 0)
	format?: ValueFormat;
	prefix?: string; // shorthand for format.prefix
	suffix?: string; // shorthand for format.suffix
	label?: React.ReactNode; // caption under the number
	delta?: number; // a change shown as a pill: 12.4 -> '+12.4%' with an arrow
	deltaFormat?: ValueFormat; // default {suffix: '%', sign: 'always', decimals: 1}
	deltaLabel?: React.ReactNode; // 'vs last year'
	lowerIsBetter?: boolean; // a fall is good news (costs, churn, time)
	size?: number; // number size in px at 1080 (default 180)
	color?: string; // number colour (default text)
	align?: 'left' | 'center' | 'right';
	mode?: 'count' | 'roll' | 'none'; // count up, roll each digit like an odometer, or land still
	delay?: number;
	duration?: number; // frames of the count (default 42 at 30 fps)
	ease?: Ease; // default out-cubic: fast, then settling on the value
	style?: React.CSSProperties;
};

const DIGITS: Record<string, string> = {latin: '0123456789', bengali: '০১২৩৪৫৬৭৮৯', devanagari: '०१२३४५६७८९'};

/** Odometer digits: every digit column rolls to its place, the right-hand ones spinning more. */
const Roll: React.FC<{text: string; p: number; digits: string; speed: number}> = ({text, p, digits, speed}) => {
	const chars = [...text];
	const digitIdx = chars.map((c) => digits.indexOf(c));
	const nDigits = digitIdx.filter((d) => d >= 0).length;
	let seen = 0;
	return (
		<span style={{display: 'inline-flex', alignItems: 'flex-start'}}>
			{chars.map((c, i) => {
				const d = digitIdx[i];
				if (d < 0) {
					// separators and signs fade in as the digits settle
					return (
						<span key={i} style={{opacity: Math.min(1, Math.max(0, (p - 0.55) / 0.3))}}>
							{c}
						</span>
					);
				}
				const k = seen++;
				const spins = 1 + Math.min(3, nDigits - 1 - k);
				const target = d + 10 * spins;
				const pos = target * p;
				const blur = Math.min(0.05, Math.abs(target * speed) * 0.0035);
				return (
					<span key={i} style={{display: 'inline-block', height: '1em', overflow: 'hidden', verticalAlign: 'top'}}>
						<span style={{display: 'flex', flexDirection: 'column', translate: `0 ${-pos}em`, filter: blur > 0.004 ? `blur(${blur}em)` : undefined}}>
							{Array.from({length: target + 1}, (_, j) => (
								<span key={j} style={{height: '1em', lineHeight: 1, display: 'block'}}>
									{digits[j % 10]}
								</span>
							))}
						</span>
					</span>
				);
			})}
		</span>
	);
};

export const Stat: React.FC<StatProps> = ({
	value,
	from = 0,
	format = {},
	prefix,
	suffix,
	label,
	delta,
	deltaFormat,
	deltaLabel,
	lowerIsBetter = false,
	size = 180,
	color,
	align = 'left',
	mode = 'count',
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
	const fmt: ValueFormat = {...format, prefix: prefix ?? format.prefix, suffix: suffix ?? format.suffix};
	const dur = duration ?? buildFrames('count', fps);
	const p = mode === 'none' ? 1 : ramp(frame, delay, dur, ease);
	const speed = mode === 'roll' ? ramp(frame + 0.5, delay, dur, ease) - ramp(frame - 0.5, delay, dur, ease) : 0;
	const appear = ramp(frame, delay, at30(10, fps), curves.out);
	const finalText = formatValue(value, fmt);
	const dec = decimalsFor(value, fmt);
	const nowText = mode === 'count' ? formatValue(countValue(from, value, p, dec), fmt) : finalText;
	const fade = exit === 'none' ? 1 : 1 - q;
	const numStyle: React.CSSProperties = {
		fontFamily: t.type.display,
		fontWeight: t.weights.display,
		fontSize: size * unit,
		lineHeight: 1,
		letterSpacing: `${Math.max(t.tracking.display, -0.03)}em`,
		color: color ?? t.colors.text,
		fontVariantNumeric: 'tabular-nums',
		textRendering: 'geometricPrecision',
		whiteSpace: 'nowrap',
	};
	const good = delta === undefined ? true : lowerIsBetter ? delta <= 0 : delta >= 0;
	const deltaText = delta === undefined ? '' : formatValue(delta, {suffix: '%', sign: 'always', decimals: 1, digits: fmt.digits, ...deltaFormat});
	const dp = ramp(frame, delay + dur - at30(6, fps), at30(12, fps), curves.out) * fade;
	const deltaColor = good ? t.colors.positive : t.colors.negative;
	const justify = align === 'center' ? 'center' : align === 'right' ? 'flex-end' : 'flex-start';
	return (
		<div style={{display: 'flex', flexDirection: 'column', alignItems: justify, gap: size * 0.1 * unit, opacity: fade, scale: exit === 'shrink' ? `${1 - 0.1 * q}` : undefined, ...style}}>
			<div style={{...numStyle, display: 'inline-grid', opacity: appear, scale: `${0.97 + 0.03 * appear}`, transformOrigin: align === 'center' ? '50% 70%' : align === 'right' ? '100% 70%' : '0% 70%'}}>
				{/* the final number, invisible, holds the width */}
				<span style={{gridArea: '1 / 1', visibility: 'hidden'}}>{finalText}</span>
				<span style={{gridArea: '1 / 1', justifySelf: align === 'left' ? 'start' : 'end'}}>
					{mode === 'roll' ? <Roll text={finalText} p={p} digits={DIGITS[fmt.digits ?? 'latin']} speed={speed} /> : nowText}
				</span>
			</div>
			{label ? (
				<div
					style={{
						fontFamily: t.type.body,
						fontWeight: t.weights.body,
						fontSize: Math.max(28, size * 0.2) * unit,
						lineHeight: 1.25,
						color: t.colors.muted,
						textAlign: align,
						opacity: ramp(frame, delay + at30(6, fps), at30(12, fps), curves.out),
						maxWidth: size * 5 * unit,
					}}
				>
					{label}
				</div>
			) : null}
			{delta !== undefined ? (
				<div style={{display: 'flex', alignItems: 'center', gap: 14 * unit, opacity: dp, translate: `0 ${(1 - dp) * 10 * unit}px`}}>
					<div
						style={{
							display: 'inline-flex',
							alignItems: 'center',
							gap: 6 * unit,
							padding: `${6 * unit}px ${14 * unit}px ${6 * unit}px ${10 * unit}px`,
							borderRadius: 999,
							background: withOpacity(deltaColor, t.dark ? 0.2 : 0.13),
							color: deltaColor,
							fontFamily: t.type.body,
							fontWeight: t.weights.strong,
							fontSize: Math.max(26, size * 0.17) * unit,
							fontVariantNumeric: 'tabular-nums',
						}}
					>
						<svg viewBox="0 0 24 24" width={Math.max(26, size * 0.17) * unit} height={Math.max(26, size * 0.17) * unit} style={{display: 'block'}}>
							<path d={delta >= 0 ? ICONS['arrow-up'] : ICONS['arrow-down']} fill="none" stroke={deltaColor} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" />
						</svg>
						{deltaText}
					</div>
					{deltaLabel ? <div style={{fontFamily: t.type.body, fontSize: Math.max(22, size * 0.14) * unit, color: t.colors.muted}}>{deltaLabel}</div> : null}
				</div>
			) : null}
		</div>
	);
};
