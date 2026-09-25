// Editorial text blocks: <BigStatement> (one giant word plus a small note, a complete composition on its own),
// <Quote> (a quotation with a hanging mark and an attribution), <Kicker> (a small label above a title), <Label>
// (a pill tag) and <LineStack> (lines that arrive on their cues while the spent ones step back).
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, lerp, useStage, useTheme} from '../core';
import {ramp, springAt, type Reveal} from '../motion';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {measureTextWidth, typeCss} from './layout';
import {RevealUnit, SplitText} from './SplitText';
import {graphemes, isComplexScript, splitWords} from './text';

export type BigStatementProps = {
	word: string; // the giant word or number ("3x", "Tuesday", "47%")
	note?: string; // the small annotation
	notePosition?: 'below' | 'right';
	maxSize?: number; // px at 1080 (default: 58% of the safe height)
	maxWidth?: number; // px at 1080 (default: the safe width)
	align?: 'left' | 'center' | 'right';
	color?: string; // the word (default: the text colour)
	accent?: string; // the rule before the note (default: the accent)
	noteColor?: string; // default: muted
	delay?: number;
	role?: TypeProps['role'];
	style?: React.CSSProperties;
};

export const BigStatement: React.FC<BigStatementProps> = (props) => {
	const {word, note, notePosition = 'below', align = 'left', delay = 0} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps} = useStage();
	const role = props.role ?? 'display';
	const ready = useTypeFontsReady([role, 'body']);
	const maxW = (props.maxWidth ?? safe.w / unit) * unit * (notePosition === 'right' ? 0.62 : 1);
	const maxSize = (props.maxSize ?? (safe.h / unit) * 0.58) * unit;
	const base = typeStyle(t, unit, word, {role, size: maxSize / unit}, 300);
	const baseKey = JSON.stringify(base);
	const size = useMemo(() => {
		if (!ready) {
			return null;
		}
		const w = measureTextWidth(word, base, 100);
		return Math.min(maxSize, (maxW / w) * 100 * 0.98);
	}, [ready, word, baseKey, maxW, maxSize]); // base is keyed by baseKey
	if (size === null) {
		return null;
	}
	const ts = {...base, fontSize: size, lineHeight: isComplexScript(word) ? 1.2 : 0.96};
	const units = graphemes(word);
	const perChar = units.length <= 8 && !isComplexScript(word);
	const each = at30(2, fps);
	const dur = at30(18, fps);
	const landed = delay + (perChar ? (units.length - 1) * each : 0) + dur;
	const settle = springAt(frame, fps, {delay, config: 'heavy', from: 1.05, to: 1});
	const ruleP = ramp(frame, landed - at30(4, fps), at30(14, fps), curves.inOut);
	const noteSize = Math.max(30, Math.min(52, (size / unit) * 0.16));
	const accent = props.accent ?? t.colors.accent;
	const noteBlock = note ? (
		<div style={{display: 'flex', flexDirection: 'column', gap: 18 * unit, maxWidth: (notePosition === 'right' ? 600 : 760) * unit}}>
			<div style={{width: 72 * unit * ruleP, height: 5 * unit, background: accent, borderRadius: 3 * unit}} />
			<SplitText text={note} role="body" size={noteSize} color={props.noteColor ?? t.colors.muted} in="rise" delay={landed + at30(2, fps)} each={at30(2, fps)} align={align === 'right' ? 'right' : 'left'} />
		</div>
	) : null;
	return (
		<div
			style={{
				display: 'flex',
				flexDirection: notePosition === 'right' ? 'row' : 'column',
				alignItems: notePosition === 'right' ? 'flex-end' : align === 'center' ? 'center' : align === 'right' ? 'flex-end' : 'flex-start',
				gap: (notePosition === 'right' ? 48 : 20) * unit,
				...props.style,
			}}
		>
			<div style={{...typeCss(ts), color: props.color ?? t.colors.text, whiteSpace: 'pre', scale: `${settle}`, transformOrigin: '0% 100%'}}>
				{perChar
					? units.map((g, i) => (
							<RevealUnit key={i} text={g} kind="mask" out="none" delay={delay + i * each} duration={dur} lineHeight={ts.lineHeight} />
						))
					: <RevealUnit text={word} kind="mask" out="none" delay={delay} duration={dur} lineHeight={ts.lineHeight} />}
			</div>
			{noteBlock}
		</div>
	);
};

export type QuoteProps = {
	text: string;
	author?: string;
	title?: string; // the author's role or company
	size?: number; // px at 1080 (default 76, 60 in 9:16)
	maxWidth?: number; // px at 1080
	align?: 'left' | 'center';
	role?: TypeProps['role']; // default 'serif'
	mark?: boolean; // the big opening quote mark (default true)
	delay?: number;
	reveal?: Reveal; // per word (default: the theme's entrance)
	color?: string;
	accent?: string;
	style?: React.CSSProperties;
};

export const Quote: React.FC<QuoteProps> = (props) => {
	const {text, author, title, align = 'left', mark = true, delay = 0} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps, vertical} = useStage();
	const role = props.role ?? 'serif';
	const size = props.size ?? (vertical ? 60 : 76);
	const maxWidth = props.maxWidth ?? Math.min(1450, safe.w / unit);
	const words = splitWords(text).length;
	const each = at30(2, fps);
	const textEnd = delay + (words - 1) * each + at30(t.motion.enterFrames, fps);
	const accent = props.accent ?? t.colors.accent;
	const markP = springAt(frame, fps, {delay, config: 'settle'});
	const byP = ramp(frame, textEnd + at30(4, fps), at30(16, fps));
	const ts = typeStyle(t, unit, text, {role, size}, size);
	const quoteMark = mark ? (
		<div
			style={{
				fontFamily: t.type.serif,
				fontWeight: 700,
				fontSize: size * 3.4 * unit,
				lineHeight: 0.8,
				color: accent,
				height: size * 1.25 * unit,
				opacity: Math.min(1, markP * 1.4),
				translate: `0 ${(1 - markP) * 24 * unit}px`,
				marginLeft: align === 'left' ? -0.05 * size * 3.4 * unit : 0,
			}}
		>
			{'“'}
		</div>
	) : null;
	return (
		<div style={{display: 'flex', flexDirection: 'column', alignItems: align === 'center' ? 'center' : 'flex-start', gap: 28 * unit, ...props.style}}>
			{quoteMark}
			<SplitText
				text={text}
				role={role}
				size={size}
				maxWidth={maxWidth}
				lineHeight={ts.lineHeight + 0.1}
				in={props.reveal}
				delay={delay + at30(4, fps)}
				each={each}
				color={props.color ?? t.colors.text}
				align={align}
			/>
			{author ? (
				<div
					style={{
						display: 'flex',
						alignItems: 'center',
						gap: 18 * unit,
						opacity: byP,
						translate: `0 ${(1 - byP) * 14 * unit}px`,
						fontFamily: t.type.body,
						fontSize: Math.max(28, size * 0.44) * unit,
						color: t.colors.muted,
					}}
				>
					<div style={{width: 44 * unit, height: 3 * unit, background: accent}} />
					<span>
						<span style={{color: t.colors.text, fontWeight: t.weights.strong}}>{author}</span>
						{title ? <span>{`, ${title}`}</span> : null}
					</span>
				</div>
			) : null}
		</div>
	);
};

export type KickerProps = {
	text: string;
	size?: number; // px at 1080 (default 26)
	color?: string; // default: the accent
	rule?: boolean; // a short bar before the text (default true)
	delay?: number;
	out?: boolean; // leave at the end of the Sequence (default false)
	style?: React.CSSProperties;
};

/** A small spaced-capitals label that sits above a title: a bar draws, then the words rise out of a mask. */
export const Kicker: React.FC<KickerProps> = ({text, size = 26, color, rule = true, delay = 0, out = false, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps, durationInFrames} = useStage();
	const c = color ?? t.colors.accent;
	const barP = ramp(frame, delay, at30(12, fps), curves.inOut);
	const outDur = at30(10, fps);
	const q = out ? ramp(frame, durationInFrames - 1 - outDur, outDur, curves.in) : 0;
	const complex = isComplexScript(text);
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: 16 * unit, opacity: 1 - q, ...style}}>
			{rule ? <div style={{width: 36 * unit * barP * (1 - q), height: 4 * unit, background: c, borderRadius: 2 * unit}} /> : null}
			<div
				style={{
					fontFamily: t.type.body,
					fontWeight: t.weights.strong,
					fontSize: size * unit,
					letterSpacing: complex ? 0 : `${t.tracking.caps}em`,
					textTransform: 'uppercase',
					color: c,
					lineHeight: complex ? 1.4 : 1.2,
					whiteSpace: 'pre',
				}}
			>
				<RevealUnit text={text} kind="mask" out="none" delay={delay + at30(rule ? 6 : 0, fps)} duration={at30(14, fps)} lineHeight={complex ? 1.4 : 1.2} />
			</div>
		</div>
	);
};

export type LabelProps = {
	text: string;
	variant?: 'solid' | 'soft' | 'outline';
	dot?: boolean;
	size?: number; // px at 1080 (default 26)
	color?: string; // default: the accent
	delay?: number;
	style?: React.CSSProperties;
};

/** A pill tag ("New", "Beta", "৳ 499") that pops in. */
export const Label: React.FC<LabelProps> = ({text, variant = 'soft', dot = false, size = 26, color, delay = 0, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const c = color ?? t.colors.accent;
	const s = springAt(frame, fps, {delay, config: 'snappy'});
	const o = ramp(frame, delay, at30(6, fps));
	const bg = variant === 'solid' ? c : variant === 'soft' ? `color-mix(in srgb, ${c} 16%, transparent)` : 'transparent';
	const fg = variant === 'solid' ? (color ? '#FFFFFF' : t.colors.onAccent) : c;
	return (
		<div
			style={{
				display: 'inline-flex',
				alignItems: 'center',
				gap: 10 * unit,
				padding: `${0.36 * size * unit}px ${0.72 * size * unit}px`,
				borderRadius: 999,
				background: bg,
				border: variant === 'outline' ? `${2 * unit}px solid ${c}` : undefined,
				color: fg,
				fontFamily: t.type.body,
				fontWeight: t.weights.strong,
				fontSize: size * unit,
				lineHeight: 1.1,
				scale: `${0.86 + 0.14 * s}`,
				opacity: o,
				whiteSpace: 'pre',
				...style,
			}}
		>
			{dot ? <span style={{width: 0.38 * size * unit, height: 0.38 * size * unit, borderRadius: 999, background: variant === 'solid' ? fg : c}} /> : null}
			{text}
		</div>
	);
};

export type LineStackProps = TypeProps & {
	lines: readonly string[];
	at?: readonly number[]; // the frame each line arrives (default: every `each` frames from `delay`)
	each?: number; // default 36
	delay?: number;
	dim?: number; // opacity of spent lines (default 0.3)
	nudge?: number; // px at 1080 the stack moves up per arrival (default 10)
	align?: 'left' | 'center' | 'right';
	style?: React.CSSProperties;
};

/**
 * Lines that arrive one after another on their cues (a narration, a lyric): each rises into place, the lines already
 * read step back to `dim`, and the whole stack nudges up a little with every arrival.
 */
export const LineStack: React.FC<LineStackProps> = (props) => {
	const {lines, dim = 0.3, nudge = 10, align = 'left'} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const each = props.each ?? at30(36, fps);
	const delay = props.delay ?? 0;
	const at = props.at ?? lines.map((_, i) => delay + i * each);
	const ts = typeStyle(t, unit, lines.join(' '), props, 64);
	const move = at30(9, fps);
	const arrived = at.filter((f) => frame >= f).length;
	// the stack lifts by `nudge` with every arrival after the first, easing like the arrival itself
	const lift = at.slice(1).reduce((acc, f) => acc + nudge * unit * ramp(frame, f, move, curves.out), 0);
	return (
		<div style={{...typeCss(ts), color: props.color ?? t.colors.text, textAlign: align, translate: `0 ${-lift}px`, ...props.style}}>
			{lines.map((line, i) => {
				const p = ramp(frame, at[i], move, curves.out);
				const spent = i < arrived - 1 ? ramp(frame, at[i + 1], move, curves.inOut) : 0;
				return (
					<div
						key={i}
						style={{
							whiteSpace: 'pre',
							opacity: p * lerp(1, dim, spent),
							translate: `0 ${(1 - p) * 28 * unit}px`,
						}}
					>
						{line}
					</div>
				);
			})}
		</div>
	);
};
