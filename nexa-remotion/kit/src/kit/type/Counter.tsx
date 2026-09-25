// <Counter>: a number that counts (or rolls like an odometer) from one value to another, formatted with Intl
// (plain, currency, percent, compact), in Latin or Bangla digits, in fixed-width digit slots so it never jiggles,
// with a small settle when it lands. formatCount() is the same formatting as a pure function.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme, type Ease} from '../core';
import {pulse, ramp} from '../motion';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {baselineRatio, measureTextWidth, typeCss} from './layout';
import {toBanglaDigits} from './text';

export type CounterFormat = 'plain' | 'decimal' | 'currency' | 'percent' | 'compact';

export type CounterFormatOptions = {
	format?: CounterFormat | Intl.NumberFormatOptions; // default 'plain'
	locale?: string; // default 'en-US', or 'bn-BD' with Bangla digits (lakh grouping: ১২,৩৪,৫৬৭)
	currency?: string; // ISO code for 'currency' (default 'USD'; 'BDT' gives ৳)
	decimals?: number; // fraction digits (default 0; 1 for compact)
	digits?: 'latin' | 'bangla';
};

const formatters = new Map<string, Intl.NumberFormat>();

const formatter = (o: CounterFormatOptions): {nf: Intl.NumberFormat; scale: number} => {
	const f = o.format ?? 'plain';
	const bangla = o.digits === 'bangla';
	const locale = o.locale ?? (bangla ? 'bn-BD' : 'en-US');
	let opts: Intl.NumberFormatOptions;
	let scale = 1;
	if (typeof f === 'object') {
		opts = f;
	} else {
		const d = o.decimals ?? (f === 'compact' ? 1 : 0);
		const fixed = {minimumFractionDigits: f === 'compact' ? 0 : d, maximumFractionDigits: d};
		opts =
			f === 'currency'
				? {style: 'currency', currency: o.currency ?? 'USD', ...fixed}
				: f === 'percent'
					? {style: 'percent', ...fixed}
					: f === 'compact'
						? {notation: 'compact', compactDisplay: locale.startsWith('bn') ? 'long' : 'short', ...fixed}
						: fixed;
		// percent takes 42 for 42 %, not 0.42
		scale = f === 'percent' ? 0.01 : 1;
	}
	const id = `${locale}|${JSON.stringify(opts)}`;
	let nf = formatters.get(id);
	if (!nf) {
		nf = new Intl.NumberFormat(locale, opts);
		formatters.set(id, nf);
	}
	return {nf, scale};
};

/** A number formatted for the screen: Intl formats, Bangla digits on request. Pure and deterministic. */
export const formatCount = (value: number, o: CounterFormatOptions = {}): string => {
	const {nf, scale} = formatter(o);
	const s = nf.format(value * scale);
	return o.digits === 'bangla' ? toBanglaDigits(s) : s;
};

const LATIN = '0123456789';
const BANGLA = '০১২৩৪৫৬৭৮৯';
const isDigit = (c: string) => LATIN.includes(c) || BANGLA.includes(c);

export type CounterProps = TypeProps &
	CounterFormatOptions & {
		to: number;
		from?: number; // default 0
		delay?: number;
		duration?: number; // frames of the count (default 45 at 30 fps)
		ease?: Ease; // default: a strong ease-out, fast then settling
		mode?: 'count' | 'roll'; // roll: every digit is a wheel, like an odometer
		prefix?: string;
		suffix?: string;
		affixScale?: number; // size of prefix and suffix relative to the digits (default 1; 0.5 for a small %)
		settle?: boolean; // a small scale settle on landing (default true)
		enter?: 'rise' | 'fade' | 'none'; // how the number appears at `delay` (default 'rise'; 'none' shows `from` before)
		align?: 'left' | 'center' | 'right'; // digits inside the final width (default 'right': digits never move)
		style?: React.CSSProperties;
	};

/** The value shown at `frame` (unrounded). */
export const counterValue = (frame: number, from: number, to: number, delay: number, duration: number, ease: Ease = curves.outQuart): number =>
	from + (to - from) * ramp(frame, delay, duration, ease);

export const Counter: React.FC<CounterProps> = (props) => {
	const {to, from = 0, prefix = '', suffix = '', affixScale = 1, mode = 'count', settle = true, align = 'right'} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const delay = props.delay ?? 0;
	const duration = props.duration ?? at30(45, fps);
	const ease = props.ease ?? curves.outQuart;
	const fo: CounterFormatOptions = {format: props.format, locale: props.locale, currency: props.currency, decimals: props.decimals, digits: props.digits};
	const finalText = formatCount(to, fo);
	const ts = {...typeStyle(t, unit, finalText, props, 160), fontVariantNumeric: 'tabular-nums'};
	const ready = useTypeFontsReady(props.role ?? 'display');
	const tsKey = JSON.stringify(ts);
	const digitSet = props.digits === 'bangla' ? BANGLA : LATIN;
	// the widest digit sets the slot width, so any font (and Bangla digits) counts without jiggling
	const slot = useMemo(() => (ready ? Math.max(...[...digitSet].map((d) => measureTextWidth(d, ts))) : 0), [ready, digitSet, tsKey]); // ts is keyed by tsKey
	const land = delay + duration;
	const v = counterValue(frame, from, to, delay, duration, ease);
	const shown = frame >= land ? finalText : formatCount(v, fo);
	const s = settle ? 1 + 0.045 * pulse(frame, land - at30(4, fps), at30(16, fps)) : 1;
	const enter = props.enter ?? 'rise';
	const inP = enter === 'none' ? 1 : ramp(frame, delay, at30(9, fps), curves.out);
	const base = ready ? baselineRatio(ts.fontFamily, ts.fontWeight, ts.lineHeight) : 0.8;
	const color = props.color ?? t.colors.text;

	const digitBox = (c: string, key: React.Key, extra?: React.CSSProperties) => (
		<span key={key} style={{display: 'inline-block', width: slot || undefined, textAlign: 'center', ...extra}}>
			{c}
		</span>
	);

	let body: React.ReactNode;
	if (mode === 'roll') {
		body = <Roll finalText={finalText} value={v} to={to} from={from} slot={slot} digitSet={digitSet} lineHeight={ts.lineHeight} />;
	} else {
		const chars = [...shown];
		body = chars.map((c, i) => (isDigit(c) ? digitBox(c, i) : <span key={i}>{c}</span>));
	}
	// a smaller prefix or suffix hangs from the cap height of the digits (vertical-align em is its own size)
	const affix = (text: string) =>
		text ? (
			<span style={{fontSize: `${affixScale}em`, verticalAlign: affixScale < 1 ? `${(0.72 * (1 - affixScale)) / affixScale}em` : undefined}}>{text}</span>
		) : null;

	return (
		<div style={{...typeCss(ts), color, whiteSpace: 'pre', ...props.style}}>
			<span
				style={{
					display: 'inline-block',
					scale: `${s}`,
					transformOrigin: `50% ${base * 100}%`,
					opacity: inP,
					translate: enter === 'rise' ? `0 ${(1 - inP) * 0.18}em` : undefined,
				}}
			>
				{affix(prefix)}
				{/* the final text reserves the width; the running value sits on top of it */}
				<span style={{display: 'inline-grid', verticalAlign: 'top'}}>
					<span style={{gridArea: '1 / 1', visibility: 'hidden'}}>{[...finalText].map((c, i) => (isDigit(c) ? digitBox(c, i) : <span key={i}>{c}</span>))}</span>
					<span style={{gridArea: '1 / 1', textAlign: align, justifySelf: align === 'left' ? 'start' : align === 'center' ? 'center' : 'end'}}>{body}</span>
				</span>
				{affix(suffix)}
			</span>
		</div>
	);
};

// Odometer: every digit of the final text is a wheel; a wheel turns continuously for the lowest place and carries
// into the next place only during the last unit of the place below, like a real counter. Leading places fade in
// when the value reaches them.
const Roll: React.FC<{finalText: string; value: number; to: number; from: number; slot: number; digitSet: string; lineHeight: number}> = ({
	finalText,
	value,
	to,
	slot,
	digitSet,
	lineHeight,
}) => {
	const chars = [...finalText];
	const digitIdx = chars.map((c, i) => (isDigit(c) ? i : -1)).filter((i) => i >= 0);
	// the rolled number is the final text's digits read as an integer; the value maps onto it proportionally
	const finalDigits = digitIdx.map((i) => (LATIN.includes(chars[i]) ? LATIN.indexOf(chars[i]) : BANGLA.indexOf(chars[i]))).join('');
	const target = Number(finalDigits || '0');
	const V = to === 0 ? 0 : Math.max(0, (value / to) * target);
	const places = digitIdx.length;
	return (
		<>
			{chars.map((c, i) => {
				const d = digitIdx.indexOf(i);
				if (d < 0) {
					// a separator shows once the digit to its left is showing
					const left = digitIdx.filter((j) => j < i).pop();
					const leftPlace = left === undefined ? places : places - 1 - digitIdx.indexOf(left);
					const o = left === undefined ? 1 : clamp((V - 0.6 * 10 ** leftPlace) / (0.4 * 10 ** leftPlace));
					return (
						<span key={i} style={{opacity: o}}>
							{c}
						</span>
					);
				}
				const place = places - 1 - d;
				const unitP = 10 ** place;
				const carry = clamp((V % unitP) - (unitP - 1));
				const pos = place === 0 ? V % 10 : (Math.floor(V / unitP) % 10) + carry;
				const o = place === 0 ? 1 : clamp((V - 0.6 * unitP) / (0.4 * unitP));
				return (
					<span
						key={i}
						style={{display: 'inline-block', position: 'relative', width: slot || undefined, height: `${lineHeight}em`, overflow: 'hidden', verticalAlign: 'top', opacity: o}}
					>
						<span style={{position: 'absolute', left: 0, right: 0, top: 0, translate: `0 ${-pos * lineHeight}em`, textAlign: 'center'}}>
							{[...digitSet, digitSet[0]].map((g, k) => (
								<span key={k} style={{display: 'block', height: `${lineHeight}em`}}>
									{g}
								</span>
							))}
						</span>
					</span>
				);
			})}
		</>
	);
};
