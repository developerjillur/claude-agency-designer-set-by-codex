// Emphasis on words. <Marker>: a clean marker sweep behind the text that follows line wraps in reading order
// (one background on the inline box, so the sweep crosses from the end of one line to the start of the next).
// <Annotate>: hand-drawn marks from @remotion/rough-notation (highlight, underline, circle, box, strike, cross,
// bracket) with defaults that look right: a translucent highlight, the doubled pencil stroke, sizes from the frame.
import {
	Box as RoughBox,
	Bracket as RoughBracket,
	Circle as RoughCircle,
	CrossedOff as RoughCrossedOff,
	Highlight as RoughHighlight,
	StrikeThrough as RoughStrikeThrough,
	Underline as RoughUnderline,
	type Padding,
} from '@remotion/rough-notation';
import React, {useLayoutEffect, useRef, useState} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {useTypeFontsReady, type FontNeed, type FontRole} from './fonts';

/** A colour with alpha from a hex colour (#rgb or #rrggbb); other colours are returned unchanged. */
const withAlpha = (color: string, alpha: number): string => {
	const m = color.trim().match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
	if (!m) {
		return color;
	}
	const h = m[1].length === 3 ? [...m[1]].map((c) => c + c).join('') : m[1];
	const n = parseInt(h, 16);
	return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
};

export type MarkerShape = 'marker' | 'block' | 'underline' | 'strike';

const SHAPES: Record<MarkerShape, {h: number; y: number}> = {
	marker: {h: 0.5, y: 86}, // the lower half, like a highlighter pen
	block: {h: 1, y: 50}, // the whole line box, like a selection
	underline: {h: 0.085, y: 96},
	strike: {h: 0.085, y: 58},
};

export type MarkerProps = {
	children: React.ReactNode; // text (it may wrap: the sweep follows the lines)
	delay?: number;
	duration?: number; // frames of the sweep (default 18 at 30 fps)
	shape?: MarkerShape; // default 'marker'
	color?: string; // default: the theme's highlight (translucent on dark themes)
	thickness?: number; // em, overrides the shape's height
	textColor?: string; // colour of the text inside the marker
	ease?: Ease;
	out?: boolean; // wipe the marker off at the end of the Sequence (default false)
	style?: React.CSSProperties;
};

export const Marker: React.FC<MarkerProps> = ({
	children,
	delay = 0,
	duration,
	shape = 'marker',
	color,
	thickness,
	textColor,
	ease = curves.inOut,
	out = false,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, durationInFrames} = useStage();
	const d = duration ?? at30(18, fps);
	const p = ramp(frame, delay, d, ease);
	const outDur = at30(12, fps);
	const q = out ? ramp(frame, durationInFrames - 1 - outDur, outDur, curves.in) : 0;
	const c = color ?? (t.dark ? withAlpha(t.colors.highlight, 0.34) : t.colors.highlight);
	const s = SHAPES[shape];
	const h = thickness ?? s.h;
	// the sweep grows from the left; the exit wipes it away toward the end (the image then hangs from the right)
	return (
		<span
			style={{
				backgroundImage: `linear-gradient(${c}, ${c})`,
				backgroundRepeat: 'no-repeat',
				backgroundSize: `${Math.max(0, p * 100 - q * 100)}% ${h}em`,
				backgroundPosition: `${q > 0 ? 100 : 0}% ${s.y}%`,
				boxDecorationBreak: 'slice',
				WebkitBoxDecorationBreak: 'slice',
				padding: '0 0.08em',
				margin: '0 -0.08em',
				color: textColor,
				...style,
			}}
		>
			{children}
		</span>
	);
};

export type AnnotateKind = 'highlight' | 'underline' | 'circle' | 'box' | 'strike' | 'cross' | 'bracket';

export type AnnotateProps = {
	kind?: AnnotateKind; // default 'circle'
	children: React.ReactNode; // a short phrase: annotated text never wraps
	delay?: number;
	duration?: number; // frames to draw (default 22 at 30 fps; 26 for circles)
	color?: string; // default: translucent highlight, accent for marks, negative for strikes and crosses
	strokeWidth?: number; // px at 1080 (default: scaled to the text, about 0.07em)
	padding?: number | Partial<Padding>; // px at 1080 (default: scaled to the text)
	iterations?: number;
	roughness?: number;
	bowing?: number;
	seed?: number;
	multiStroke?: boolean; // the doubled pencil stroke (default true)
	boil?: boolean; // re-draw the line every 4 frames once drawn, a living cartoon line (default false)
	brackets?: {left?: boolean; right?: boolean; top?: boolean; bottom?: boolean};
	role?: FontRole; // the font of the annotated text, measured only once it has loaded (default 'display')
	fonts?: FontNeed[];
	ease?: Ease;
	style?: React.CSSProperties;
};

// defaults in em of the annotated text, so a mark fits 40 px labels and 200 px headlines alike; `room` is the
// margin a circle, box or bracket takes on each side so it never runs into the next word
const DEFAULTS: Record<AnnotateKind, {stroke: number; pad: Partial<Padding>; room: number}> = {
	highlight: {stroke: 0, pad: {left: 0.14, right: 0.14, top: 0.02, bottom: 0.02}, room: 0},
	underline: {stroke: 0.075, pad: {top: 0.02}, room: 0},
	circle: {stroke: 0.07, pad: {left: 0.32, right: 0.32, top: 0.16, bottom: 0.16}, room: 0.18},
	box: {stroke: 0.055, pad: {left: 0.16, right: 0.16, top: 0.08, bottom: 0.08}, room: 0.12},
	strike: {stroke: 0.08, pad: {}, room: 0},
	cross: {stroke: 0.07, pad: {}, room: 0},
	bracket: {stroke: 0.075, pad: {left: 0.14, right: 0.14, top: 0.06, bottom: 0.06}, room: 0.1},
};

const scalePad = (p: Partial<Padding>, k: number): Partial<Padding> =>
	Object.fromEntries(Object.entries(p).map(([key, v]) => [key, (v ?? 0) * k])) as Partial<Padding>;

export const Annotate: React.FC<AnnotateProps> = ({
	kind = 'circle',
	children,
	delay = 0,
	duration,
	color,
	strokeWidth,
	padding,
	iterations,
	roughness,
	bowing,
	seed = 1,
	multiStroke = true,
	boil = false,
	brackets,
	role = 'display',
	fonts = [],
	ease = curves.outQuart,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const ready = useTypeFontsReady(role, fonts);
	// the annotated text's font size and box (read from the page), so the defaults scale with the text
	const probe = useRef<HTMLSpanElement>(null);
	const [box, setBox] = useState<{em: number; w: number; h: number} | null>(null);
	useLayoutEffect(() => {
		const el = probe.current;
		if (!el) {
			return;
		}
		const host = el.parentElement ?? el;
		const next = {em: parseFloat(getComputedStyle(el).fontSize), w: host.offsetWidth, h: host.offsetHeight};
		if (next.em > 0 && (!box || next.em !== box.em || Math.abs(next.w - box.w) > 0.5 || Math.abs(next.h - box.h) > 0.5)) {
			setBox(next);
		}
	});
	const em = box?.em ?? null;
	const d = duration ?? at30(kind === 'circle' ? 26 : 22, fps);
	const progress = ramp(frame, delay, d, ease);
	const drawn = delay + d;
	const liveSeed = boil && frame >= drawn ? seed + 1 + Math.floor((frame - drawn) / at30(4, fps)) : seed;
	const def = DEFAULTS[kind];
	const size = em ?? 60 * unit;
	// a circle is sized to enclose the words' corners (an inscribed ellipse would cut through the first and last
	// letters): a little wider than the text, then tall enough for the corners, with 5% to spare
	let circle: Partial<Padding> | null = null;
	if (kind === 'circle' && box && padding === undefined) {
		const half = box.w / 2;
		const px = Math.max(0.3 * box.em, 0.08 * box.w);
		const ratio = Math.min(0.92, (half * half) / ((half + px) * (half + px)));
		const hh = Math.min(box.h, 1.05 * box.em) / 2;
		const py = Math.max(0.1 * box.em, (hh / Math.sqrt(1 - ratio)) * 1.05 - box.h / 2);
		circle = {left: px, right: px, top: py, bottom: py};
	}
	// explicit values are px at 1080; defaults are em of the text
	const pad =
		padding !== undefined
			? scalePad(typeof padding === 'number' ? {left: padding, right: padding, top: padding, bottom: padding} : padding, unit)
			: (circle ?? scalePad(def.pad, size));
	const sw = strokeWidth === undefined ? def.stroke * size : strokeWidth * unit;
	const roomPx = kind === 'circle' && circle ? Math.max(0, (circle.left ?? 0) - 0.12 * size) : def.room * size;
	const room = roomPx > 0 ? {margin: `0 ${roomPx}px`} : {};
	const shared = {
		progress,
		seed: liveSeed,
		disableMultiStroke: !multiStroke,
		roughness,
		bowing,
		style: {...room, ...style},
	};
	const text = <span ref={probe}>{children}</span>;
	if (!ready || em === null) {
		// not measured yet: the text alone, laid out like the annotation's own span
		return <span style={{display: 'inline-block', whiteSpace: 'pre', ...room, ...style}}>{text}</span>;
	}
	switch (kind) {
		case 'highlight':
			return (
				<RoughHighlight
					{...shared}
					color={color ?? withAlpha(t.colors.highlight, t.dark ? 0.4 : 0.62)}
					padding={pad}
					iterations={iterations}
					roughness={roughness ?? 2.3}
					bowing={bowing ?? 0.4}
					maxRandomnessOffset={0.12 * size}
				>
					{text}
				</RoughHighlight>
			);
		case 'underline':
			return (
				<RoughUnderline {...shared} color={color ?? t.colors.accent} strokeWidth={sw} padding={{top: pad.top ?? 0}} iterations={iterations}>
					{text}
				</RoughUnderline>
			);
		case 'box':
			return (
				<RoughBox {...shared} color={color ?? t.colors.accent} strokeWidth={sw} padding={pad} iterations={iterations}>
					{text}
				</RoughBox>
			);
		case 'strike':
			return (
				<RoughStrikeThrough {...shared} color={color ?? t.colors.negative} strokeWidth={sw} iterations={iterations}>
					{text}
				</RoughStrikeThrough>
			);
		case 'cross':
			return (
				<RoughCrossedOff {...shared} color={color ?? t.colors.negative} strokeWidth={sw} iterations={iterations}>
					{text}
				</RoughCrossedOff>
			);
		case 'bracket':
			return (
				<RoughBracket
					{...shared}
					color={color ?? t.colors.accent}
					strokeWidth={sw}
					padding={pad}
					bracketLeft={brackets?.left ?? true}
					bracketRight={brackets?.right ?? true}
					bracketTop={brackets?.top ?? false}
					bracketBottom={brackets?.bottom ?? false}
				>
					{text}
				</RoughBracket>
			);
		case 'circle':
		default:
			return (
				<RoughCircle {...shared} color={color ?? t.colors.accent} strokeWidth={sw} padding={pad} iterations={iterations} box="inside">
					{text}
				</RoughCircle>
			);
	}
};
