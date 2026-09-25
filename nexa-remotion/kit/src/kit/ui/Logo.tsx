// Logo reveals: a mark (SVG paths, so it can be drawn), a wordmark and a tagline, brought in five ways: rising
// through a mask, outlines that draw and then fill, a scale settle with one soft pulse, two halves that meet and
// open the wordmark, and a block wipe. The sample marks are invented, neutral shapes.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp, springAt} from '../motion';
import {UiBackdrop} from './Frames';
import {splitGraphemes, useUiLife} from './shared';

/** One path of a mark. Colours may be CSS colours or theme roles: 'accent', 'accent2', 'text', 'bg', 'onAccent'. */
export type LogoPart = {d: string; fill?: string; stroke?: string; strokeWidth?: number};
export type LogoMark = {viewBox: string; parts: LogoPart[]};

/** Invented marks for demos and drafts (never a real brand). */
export const UI_MARKS = {
	note: {
		viewBox: '0 0 120 120',
		parts: [
			{d: 'M28 12H92a16 16 0 0 1 16 16V76L76 108H28a16 16 0 0 1-16-16V28a16 16 0 0 1 16-16Z', fill: 'accent'},
			{d: 'M108 76H88a12 12 0 0 0-12 12v20Z', fill: 'accent2'},
			{d: 'M34 50c8-9 16-9 24 0s16 9 24 0', stroke: 'onAccent', strokeWidth: 8},
			{d: 'M34 74c8-9 16-9 24 0', stroke: 'onAccent', strokeWidth: 8},
		],
	},
	orbit: {
		viewBox: '0 0 120 120',
		parts: [
			{d: 'M60 16a44 44 0 1 1 0 88a44 44 0 1 1 0-88Z', stroke: 'accent', strokeWidth: 10},
			{d: 'M60 42a18 18 0 1 1 0 36a18 18 0 1 1 0-36Z', fill: 'accent'},
			{d: 'M96 18a10 10 0 1 1 0 20a10 10 0 1 1 0-20Z', fill: 'accent2'},
		],
	},
	peak: {
		viewBox: '0 0 120 120',
		parts: [
			{d: 'M8 102L46 34L68 72L80 52L112 102Z', fill: 'accent'},
			{d: 'M88 12a12 12 0 1 1 0 24a12 12 0 1 1 0-24Z', fill: 'accent2'},
		],
	},
	coin: {
		viewBox: '0 0 120 120',
		parts: [
			{d: 'M60 8a52 52 0 1 1 0 104a52 52 0 1 1 0-104Z', fill: 'accent'},
			{d: 'M79 41a27 27 0 1 0 0 38', stroke: 'onAccent', strokeWidth: 11},
		],
	},
} satisfies Record<string, LogoMark>;

export type LogoRevealVariant = 'mask' | 'stroke' | 'scale' | 'split' | 'wipe';

export type LogoRevealProps = {
	mark?: LogoMark;
	name?: string; // the wordmark ('' for a mark only)
	tagline?: string;
	variant?: LogoRevealVariant;
	size?: number; // mark height, px at 1080 (default 170)
	layout?: 'row' | 'stack';
	color?: string; // replaces the 'accent' role in the mark
	delay?: number;
	exit?: number | false; // default false (hold); a number fades and settles it out at the end
	exitAt?: number;
	background?: 'theme' | 'none' | string;
	push?: number; // slow push-in over the Sequence (default 0.03)
	style?: React.CSSProperties;
};

type Resolve = (c: string | undefined) => string | undefined;

const MarkSvg: React.FC<{mark: LogoMark; px: number; resolve: Resolve; draw?: number; fill?: number; outline?: string; stagger?: number}> = ({mark, px, resolve, draw = 1, fill = 1, outline, stagger = 0.12}) => {
	const [, , vw, vh] = mark.viewBox.split(/\s+/).map(Number);
	const n = mark.parts.length;
	return (
		<svg width={(px * vw) / vh} height={px} viewBox={mark.viewBox} style={{display: 'block', overflow: 'visible'}}>
			{mark.parts.map((p, i) => {
				// each part draws over its own slice of the draw progress
				const span = 1 - stagger * (n - 1);
				const local = Math.min(1, Math.max(0, (draw - i * stagger) / Math.max(0.2, span)));
				const hasFill = p.fill !== undefined;
				const strokeColor = resolve(p.stroke) ?? outline ?? resolve(p.fill);
				const sw = p.strokeWidth ?? 3;
				const drawing = draw < 1 || fill < 1;
				return (
					<g key={i}>
						{hasFill ? <path d={p.d} fill={resolve(p.fill)} opacity={fill} /> : null}
						{p.stroke ? (
							<path d={p.d} fill="none" stroke={strokeColor} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - local} />
						) : drawing && hasFill ? (
							<path d={p.d} fill="none" stroke={strokeColor} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - local} opacity={1 - fill} />
						) : null}
					</g>
				);
			})}
		</svg>
	);
};

/** A logo sting: mark, wordmark and tagline arrive in one of five ways and hold (or leave at the end). */
export const LogoReveal: React.FC<LogoRevealProps> = ({
	mark = UI_MARKS.note,
	name = 'Driftnote',
	tagline,
	variant = 'mask',
	size = 170,
	layout = 'row',
	color,
	delay = 0,
	exit = false,
	exitAt,
	background = 'theme',
	push = 0.03,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, durationInFrames} = useStage();
	const life = useUiLife({delay, exit: exit === false ? false : exit ?? at30(16, fps), exitAt});
	const f = (n: number) => at30(n, fps);
	const u = (v: number) => v * unit;
	const resolve: Resolve = (c) => {
		switch (c) {
			case undefined:
				return undefined;
			case 'accent':
				return color ?? t.colors.accent;
			case 'accent2':
				return t.colors.accent2;
			case 'text':
				return t.colors.text;
			case 'bg':
				return t.colors.bg;
			case 'onAccent':
				return t.colors.onAccent;
			default:
				return c;
		}
	};
	const q = life.leave();
	const pushS = Number.isFinite(durationInFrames) && push ? 1 + push * ramp(frame, delay, durationInFrames - delay, curves.sine) : 1;
	const stack = layout === 'stack';
	const markPx = u(size);
	const wordSize = u(size * (stack ? 0.46 : 0.52));
	const wordStyle: React.CSSProperties = {
		fontFamily: t.type.display,
		fontWeight: t.weights.display,
		fontSize: wordSize,
		lineHeight: 1.1,
		letterSpacing: `${t.tracking.display}em`,
		color: t.colors.text,
		whiteSpace: 'nowrap',
		textRendering: 'geometricPrecision',
	};
	const word = t.caps ? name.toUpperCase() : name;
	const gap = u(size * (stack ? 0.2 : 0.22));
	// tagline timing per variant
	const tagAt = {mask: 30, stroke: 50, scale: 36, split: 40, wipe: 34}[variant];
	const tagIn = life.enter(f(tagAt), f(18));
	let markNode: React.ReactNode;
	let wordNode: React.ReactNode = null;
	let overlay: React.ReactNode = null;
	if (variant === 'mask') {
		const m = life.enter(0, f(22), curves.out);
		const w = life.enter(f(10), f(20), curves.out);
		markNode = (
			<div style={{overflow: 'hidden', padding: u(6), margin: -u(6)}}>
				<div style={{translate: `0px ${(1 - m) * 108}%`, rotate: `${(1 - m) * -8}deg`}}>
					<MarkSvg mark={mark} px={markPx} resolve={resolve} />
				</div>
			</div>
		);
		wordNode = name ? (
			<div style={{overflow: 'hidden', paddingBottom: '0.14em', marginBottom: '-0.14em'}}>
				<div style={{...wordStyle, translate: `0px ${(1 - w) * 110}%`}}>{word}</div>
			</div>
		) : null;
	} else if (variant === 'stroke') {
		const draw = life.enter(0, f(36), curves.inOut);
		const fill = life.enter(f(26), f(16), curves.out);
		const w = life.enter(f(30), f(22), curves.inOut);
		markNode = <MarkSvg mark={mark} px={markPx} resolve={resolve} draw={draw} fill={fill} />;
		wordNode = name ? <div style={{...wordStyle, clipPath: `inset(-10% ${(1 - w) * 100}% -20% 0)`}}>{word}</div> : null;
	} else if (variant === 'scale') {
		const s = springAt(frame, fps, {delay, config: 'pop'});
		const ring = ramp(frame, delay + f(4), f(26), curves.out);
		markNode = (
			<div style={{position: 'relative'}}>
				<div style={{position: 'absolute', left: '50%', top: '50%', width: markPx * 1.2, height: markPx * 1.2, marginLeft: -markPx * 0.6, marginTop: -markPx * 0.6, borderRadius: '50%', border: `${u(3)}px solid ${resolve('accent')}`, opacity: ring > 0 && ring < 1 ? 0.45 * (1 - ring) : 0, scale: `${0.7 + 0.9 * ring}`}} />
				<div style={{scale: `${0.3 + 0.7 * s}`, rotate: `${(1 - s) * -24}deg`, opacity: Math.min(1, Math.max(0, s) * 3)}}>
					<MarkSvg mark={mark} px={markPx} resolve={resolve} />
				</div>
			</div>
		);
		const g = splitGraphemes(word);
		const perLetter = g.length <= 6 && !/[ঀ-৿]/.test(word);
		const units = perLetter ? g : word.split(/(\s+)/);
		wordNode = name ? (
			<div style={{...wordStyle, display: 'flex', whiteSpace: 'pre'}}>
				{units.map((ch, i) => {
					const p = springAt(frame, fps, {delay: delay + f(12) + i * f(perLetter ? 2 : 4), config: 'settle'});
					return (
						<span key={i} style={{display: 'inline-block', opacity: Math.min(1, Math.max(0, p) * 2), translate: `0px ${(1 - p) * 0.35 * size * unit}px`, scale: `${0.7 + 0.3 * p}`}}>
							{ch}
						</span>
					);
				})}
			</div>
		) : null;
	} else if (variant === 'split') {
		const meet = life.enter(0, f(20), curves.out);
		const open = life.enter(f(16), f(22), curves.inOut);
		const half = (left: boolean) => (
			<div style={{position: left ? 'relative' : 'absolute', inset: left ? undefined : 0, clipPath: left ? 'inset(-5% 50% -5% -5%)' : 'inset(-5% -5% -5% 50%)', translate: `${(left ? -1 : 1) * (1 - meet) * u(90)}px 0px`, opacity: Math.min(1, meet * 1.6)}}>
				<MarkSvg mark={mark} px={markPx} resolve={resolve} />
			</div>
		);
		markNode = (
			<div style={{position: 'relative'}}>
				{half(true)}
				{half(false)}
			</div>
		);
		wordNode = name ? (
			<div style={{display: 'grid', gridTemplateColumns: stack ? undefined : `minmax(0, ${open}fr)`, gridTemplateRows: stack ? `minmax(0, ${open}fr)` : undefined}}>
				<div style={{minWidth: 0, minHeight: 0, overflow: 'hidden', paddingBottom: '0.14em', marginBottom: '-0.14em'}}>
					<div style={{...wordStyle, translate: stack ? `0px ${(1 - open) * -40}%` : `${(1 - open) * -45}% 0px`, opacity: open}}>{word}</div>
				</div>
			</div>
		) : null;
	} else {
		// wipe: a block covers the lockup, the lockup appears under it, the block leaves the other way
		const cover = life.enter(0, f(13), curves.inOut);
		const uncover = life.enter(f(15), f(14), curves.inOut);
		const shown = cover >= 1;
		markNode = (
			<div style={{opacity: shown ? 1 : 0}}>
				<MarkSvg mark={mark} px={markPx} resolve={resolve} />
			</div>
		);
		wordNode = name ? <div style={{...wordStyle, opacity: shown ? 1 : 0}}>{word}</div> : null;
		overlay = <div style={{position: 'absolute', inset: -u(14), background: resolve('accent'), clipPath: `inset(0 ${(1 - cover) * 100}% 0 ${uncover * 100}%)`}} />;
	}
	return (
		<AbsoluteFill style={style}>
			{background === 'theme' ? <UiBackdrop variant="glow" /> : background !== 'none' ? <AbsoluteFill style={{background}} /> : null}
			<AbsoluteFill style={{display: 'flex', alignItems: 'center', justifyContent: 'center', scale: `${pushS * (1 - 0.03 * q)}`, opacity: 1 - q, filter: q > 0.01 ? `blur(${q * 6 * unit}px)` : undefined}}>
				<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: u(size * 0.26)}}>
					<div style={{position: 'relative', display: 'flex', flexDirection: stack ? 'column' : 'row', alignItems: 'center', gap: wordNode ? gap : 0}}>
						{markNode}
						{wordNode}
						{overlay}
					</div>
					{tagline ? (
						<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: u(size * 0.19), color: t.colors.muted, letterSpacing: `${Math.max(0.04, t.tracking.caps * 0.6)}em`, opacity: tagIn, translate: `0px ${(1 - tagIn) * u(14)}px`, whiteSpace: 'nowrap'}}>{tagline}</div>
					) : null}
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

/** A logo mark drawn still (an end card's logo slot, a watermark, a favicon-like tile): theme roles become colours. */
export const LogoMarkView: React.FC<{mark: LogoMark; size?: number; color?: string; style?: React.CSSProperties}> = ({
	mark,
	size = 48,
	color,
	style,
}) => {
	const t = useTheme();
	const {unit} = useStage();
	const role = (c?: string): string | undefined => {
		switch (c) {
			case undefined:
				return undefined;
			case 'accent':
				return color ?? t.colors.accent;
			case 'accent2':
				return t.colors.accent2;
			case 'text':
				return t.colors.text;
			case 'bg':
				return t.colors.bg;
			case 'onAccent':
				return t.colors.onAccent;
			default:
				return c;
		}
	};
	return (
		<svg viewBox={mark.viewBox} width={size * unit} height={size * unit} style={{display: 'block', ...style}}>
			{mark.parts.map((p, i) => (
				<path key={i} d={p.d} fill={p.fill ? role(p.fill) : 'none'} stroke={role(p.stroke)} strokeWidth={p.strokeWidth} strokeLinecap="round" strokeLinejoin="round" />
			))}
		</svg>
	);
};
