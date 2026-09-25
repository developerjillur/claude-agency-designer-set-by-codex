// <SplitText>: text that arrives by word (the default), by character (short words only) or by line, with any of
// the motion module's reveals. Characters are grapheme clusters, so Bangla never breaks apart. Lines come from the
// `lines` prop, from `\n` in the text, or are measured (maxWidth) after the fonts load.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, shuffle, useStage, useTheme} from '../core';
import {Animate, ramp, type Reveal} from '../motion';
import {maskPad, typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {layoutText, typeCss, type TypeStyle} from './layout';
import {graphemes, splitWords} from './text';

export type SplitBy = 'auto' | 'word' | 'char' | 'line';
export type SplitOrder = 'forward' | 'reverse' | 'center' | 'random';

/** Timing shared by everything that reveals text unit by unit (frames). */
export type RevealTiming = {
	in?: Reveal; // default: the theme's entrance
	out?: Reveal; // default: none
	delay?: number;
	each?: number; // frames between units
	duration?: number; // entrance frames of one unit
	outDuration?: number;
	outEach?: number; // frames between exits (0: all leave together at the end of the Sequence)
	order?: SplitOrder;
	seed?: string;
	distance?: number; // px at 1080 for rises and slides
};

/** The rank of unit `i` of `n` in a stagger order (0 arrives first). */
export const staggerRank = (i: number, n: number, order: SplitOrder = 'forward', seed = 'split'): number => {
	if (order === 'reverse') {
		return n - 1 - i;
	}
	if (order === 'center') {
		return Math.abs(i - (n - 1) / 2);
	}
	if (order === 'random') {
		return shuffle(
			Array.from({length: n}, (_, k) => k),
			seed,
		).indexOf(i);
	}
	return i;
};

export const isMaskReveal = (k: Reveal | undefined): boolean => k === 'mask' || k === 'maskDown';

type MaskKind = 'mask' | 'maskDown' | null;

/**
 * A mask reveal for type: the unit slides inside its own clipping box, padded for the script (accents, descenders,
 * Bangla vowel signs), and travels the full box height plus both paddings, so no ascender or descender ever peeks
 * through the mask before the entrance or after the exit.
 */
export const MaskUnit: React.FC<{
	text: string;
	enter: MaskKind;
	exit: MaskKind;
	delay: number;
	duration: number;
	outDuration?: number;
	outAt?: number;
	lineHeight?: number;
	innerStyle?: React.CSSProperties;
	children?: React.ReactNode;
}> = ({text, enter, exit, delay, duration, outDuration, outAt, lineHeight = 1.1, innerStyle, children}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, durationInFrames} = useStage();
	const pad = maskPad(text);
	const travel = lineHeight + pad.top + pad.bottom + 0.04;
	const p = enter ? ramp(frame, delay, duration, curves[t.motion.curve]) : 1;
	const outDur = outDuration ?? at30(t.motion.exitFrames, fps);
	const exitStart = outAt ?? durationInFrames - 1 - outDur;
	const q = exit && Number.isFinite(exitStart) ? ramp(frame, exitStart, outDur, curves.in) : 0;
	const y = (enter === 'maskDown' ? -1 : 1) * (1 - p) * travel + (exit === 'maskDown' ? 1 : -1) * q * travel;
	return (
		<span
			style={{
				display: 'inline-block',
				position: 'relative',
				overflow: 'hidden',
				verticalAlign: 'top',
				paddingTop: `${pad.top}em`,
				paddingBottom: `${pad.bottom}em`,
				marginTop: `${-pad.top}em`,
				marginBottom: `${-pad.bottom}em`,
			}}
		>
			<span style={{display: 'inline-block', translate: `0 ${y}em`, ...innerStyle}}>{children ?? text}</span>
		</span>
	);
};

/**
 * One revealed unit (a word, a grapheme or a line). Mask reveals use MaskUnit (script-aware padding and full
 * travel); every other reveal is the motion module's Animate.
 */
export const RevealUnit: React.FC<{
	text: string;
	kind: Reveal;
	out: Reveal;
	delay: number;
	duration: number;
	outDuration?: number;
	outAt?: number;
	distance?: number;
	origin?: string;
	lineHeight?: number;
	innerStyle?: React.CSSProperties;
	children?: React.ReactNode;
}> = ({text, kind, out, delay, duration, outDuration, outAt, distance, origin, lineHeight, innerStyle, children}) => {
	const maskIn = isMaskReveal(kind);
	const maskOut = isMaskReveal(out);
	const content = children ?? text;
	if (!maskIn && !maskOut) {
		return (
			<Animate inline in={kind} out={out} delay={delay} duration={duration} outDuration={outDuration} outAt={outAt} distance={distance} origin={origin} innerStyle={innerStyle}>
				{content}
			</Animate>
		);
	}
	const mask = (
		<MaskUnit
			text={text}
			enter={maskIn ? (kind as MaskKind) : null}
			exit={maskOut ? (out as MaskKind) : null}
			delay={delay}
			duration={duration}
			outDuration={outDuration}
			outAt={outAt}
			lineHeight={lineHeight}
			innerStyle={maskIn && maskOut ? innerStyle : undefined}
		>
			{content}
		</MaskUnit>
	);
	if (maskIn && maskOut) {
		return mask;
	}
	// one side is a mask, the other a motion reveal: nest them
	return (
		<Animate
			inline
			in={maskIn ? 'none' : kind}
			out={maskOut ? 'none' : out}
			delay={delay}
			duration={duration}
			outDuration={outDuration}
			outAt={outAt}
			distance={distance}
			origin={origin}
			innerStyle={innerStyle}
		>
			{mask}
		</Animate>
	);
};

export type SplitTextProps = TypeProps &
	RevealTiming & {
		text: string;
		by?: SplitBy; // 'auto': characters for one short word (up to 6 graphemes), words otherwise
		lines?: readonly string[]; // given lines
		maxWidth?: number; // px at 1080: measure and wrap to this width (needed for by="line" without lines)
		maxLines?: number; // with maxWidth: shrink the size until the text fits
		align?: 'left' | 'center' | 'right';
		style?: React.CSSProperties; // on the text block
	};

type Resolved = {
	mode: 'word' | 'char' | 'line';
	kind: Reveal;
	out: Reveal;
	delay: number;
	each: number;
	duration: number;
	outDuration: number;
	outEach: number;
	order: SplitOrder;
	seed: string;
	distance?: number;
	lineHeight?: number;
};

const useResolved = (p: SplitTextProps): Resolved => {
	const t = useTheme();
	const {fps} = useStage();
	const mode: Resolved['mode'] =
		p.by === 'line' || p.by === 'word' || p.by === 'char'
			? p.by
			: splitWords(p.text).length === 1 && graphemes(p.text).length <= 6
				? 'char'
				: 'word';
	const baseEach = mode === 'char' ? 2 : mode === 'line' ? 6 : 3;
	const baseDur = mode === 'char' ? 12 : t.motion.enterFrames;
	return {
		mode,
		kind: p.in ?? t.motion.enter,
		out: p.out ?? 'none',
		delay: p.delay ?? 0,
		each: p.each ?? at30(baseEach, fps),
		duration: p.duration ?? at30(baseDur, fps),
		outDuration: p.outDuration ?? at30(t.motion.exitFrames, fps),
		outEach: p.outEach ?? 0,
		order: p.order ?? 'forward',
		seed: p.seed ?? 'split',
		distance: p.distance,
	};
};

/** Delay and exit frame of unit `index` of `total`. */
const unitTiming = (r: Resolved, index: number, total: number, sequenceEnd: number) => {
	const rank = staggerRank(index, total, r.order, r.seed);
	return {
		delay: r.delay + Math.round(rank * r.each),
		outAt: r.outEach > 0 ? sequenceEnd - 1 - r.outDuration - (total - 1 - rank) * r.outEach : undefined,
	};
};

const countUnits = (lines: string[][], mode: Resolved['mode']): number =>
	mode === 'line'
		? lines.length
		: mode === 'word'
			? lines.reduce((a, l) => a + l.length, 0)
			: lines.reduce((a, l) => a + l.reduce((b, w) => b + graphemes(w).length, 0), 0);

// the units of some words, in reading order starting at `start`
const renderWords = (words: string[], r: Resolved, start: {i: number}, total: number, end: number): React.ReactNode[] => {
	const unit = (text: string, key: string) => {
		const {delay, outAt} = unitTiming(r, start.i++, total, end);
		return (
			<RevealUnit
				key={key}
				text={text}
				kind={r.kind}
				out={r.out}
				delay={delay}
				duration={r.duration}
				outDuration={r.outDuration}
				outAt={outAt}
				distance={r.distance}
				lineHeight={r.lineHeight}
			/>
		);
	};
	if (r.mode === 'line') {
		return [unit(words.join(' '), 'line')];
	}
	const out: React.ReactNode[] = [];
	words.forEach((w, wi) => {
		if (wi) {
			out.push(' ');
		}
		out.push(
			r.mode === 'char' ? (
				<span key={`w${wi}`} style={{display: 'inline-block', whiteSpace: 'nowrap'}}>
					{graphemes(w).map((g, gi) => unit(g, `g${gi}`))}
				</span>
			) : (
				unit(w, `w${wi}`)
			),
		);
	});
	return out;
};

const renderLines = (lines: string[][], r: Resolved, end: number, align: React.CSSProperties['textAlign']) => {
	const total = countUnits(lines, r.mode);
	const start = {i: 0};
	return lines.map((words, li) => (
		<div key={li} style={{whiteSpace: 'pre', textAlign: align}}>
			{renderWords(words, r, start, total, end)}
		</div>
	));
};

const SplitMeasured: React.FC<{p: SplitTextProps; r: Resolved; ts: TypeStyle}> = ({p, r, ts}) => {
	const t = useTheme();
	const {unit, safe, durationInFrames} = useStage();
	const ready = useTypeFontsReady(p.role ?? 'display');
	const maxW = (p.maxWidth ?? safe.w / unit) * unit;
	const tsKey = JSON.stringify(ts);
	const layout = useMemo(
		() => (ready ? layoutText(p.text, ts, {maxWidth: maxW, maxLines: p.maxLines, shrink: p.maxLines !== undefined}) : null),
		// ts is captured through tsKey
		[ready, p.text, tsKey, maxW, p.maxLines],
	);
	const color = p.color ?? t.colors.text;
	if (!layout) {
		return <div style={{...typeCss(ts), color, visibility: 'hidden', ...p.style}}>{p.text}</div>;
	}
	const lines = layout.lines.map((l) => l.words.map((w) => w.text));
	return (
		<div style={{...typeCss({...ts, fontSize: layout.fontSize}), color, width: maxW, ...p.style}}>
			{renderLines(lines, r, durationInFrames, p.align ?? 'left')}
		</div>
	);
};

export const SplitText: React.FC<SplitTextProps> = (props) => {
	const t = useTheme();
	const {unit, durationInFrames} = useStage();
	const ts = typeStyle(t, unit, props.text, props, 72);
	const r = {...useResolved(props), lineHeight: ts.lineHeight};
	const given = props.lines ?? (props.text.includes('\n') ? props.text.split('\n') : null);
	if (!given && (r.mode === 'line' || props.maxWidth !== undefined)) {
		return <SplitMeasured p={props} r={r} ts={ts} />;
	}
	const color = props.color ?? t.colors.text;
	const lines = (given ?? [props.text]).map(splitWords).filter((l) => l.length);
	if (given) {
		return <div style={{...typeCss(ts), color, ...props.style}}>{renderLines(lines, r, durationInFrames, props.align ?? 'left')}</div>;
	}
	// one paragraph that the browser wraps at the spaces
	const words = lines[0] ?? [];
	return (
		<div style={{...typeCss(ts), color, textAlign: props.align ?? 'left', ...props.style}}>
			{renderWords(words, r, {i: 0}, countUnits([words], r.mode), durationInFrames)}
		</div>
	);
};
