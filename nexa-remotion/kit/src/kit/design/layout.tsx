// Layout inside the safe area that adapts to the frame's shape: wide (16:9), square (1:1), portrait (4:5) and tall
// (9:16). Any prop marked Responsive takes one value or one per shape ({wide: 3, tall: 1}); a missing shape uses the
// nearest one that is given. Restack rows into columns for tall frames instead of cropping the wide layout.
import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame} from 'remotion';
import {clamp, curves, FONTS, useStage, useTheme, type Rect, type Theme} from '../core';
import {ramp} from '../motion';
import {contrast, isDark, readableOn} from './color';
import {estimateEm, useTextEm} from './measure';
import {OnTone, Scrim, type ScrimProps} from './surfaces';

export type Shape = 'wide' | 'square' | 'portrait' | 'tall';
export const SHAPES: readonly Shape[] = ['wide', 'square', 'portrait', 'tall'];
const ASPECT: Record<Shape, number> = {wide: 16 / 9, square: 1, portrait: 0.8, tall: 9 / 16};

/** The shape of a frame: wide from 1.3:1, square from 0.9:1, portrait from 0.68:1, tall below. */
export const shapeOf = (aspect: number): Shape => (aspect >= 1.3 ? 'wide' : aspect >= 0.9 ? 'square' : aspect >= 0.68 ? 'portrait' : 'tall');

export type Responsive<T> = T | Partial<Record<Shape, T>>;

const isPerShape = (v: unknown): v is Partial<Record<Shape, unknown>> =>
	typeof v === 'object' && v !== null && !Array.isArray(v) && Object.keys(v).length > 0 && Object.keys(v).every((k) => (SHAPES as readonly string[]).includes(k));

/** The value for a shape: the one given for it, else the one given for the nearest shape. */
export const pick = <T,>(v: Responsive<T>, shape: Shape): T => {
	if (!isPerShape(v)) {
		return v as T;
	}
	const o = v as Partial<Record<Shape, T>>;
	if (o[shape] !== undefined) {
		return o[shape] as T;
	}
	let best: T | undefined;
	let dist = Infinity;
	for (const s of SHAPES) {
		if (o[s] !== undefined) {
			const d = Math.abs(Math.log(ASPECT[s] / ASPECT[shape]));
			if (d < dist) {
				dist = d;
				best = o[s];
			}
		}
	}
	return best as T;
};

export type LayoutInfo = {
	shape: Shape;
	wide: boolean;
	tall: boolean; // portrait or tall: stack things vertically
	pick: <T>(v: Responsive<T>) => T;
	safe: Rect;
	width: number;
	height: number;
	unit: number;
};

/** The frame's shape and a pick() bound to it: `const {pick} = useLayout(); pick({wide: 3, tall: 1})`. */
export const useLayout = (): LayoutInfo => {
	const {aspect, safe, width, height, unit} = useStage();
	const shape = shapeOf(aspect);
	return {
		shape,
		wide: shape === 'wide',
		tall: shape === 'portrait' || shape === 'tall',
		pick: <T,>(v: Responsive<T>) => pick(v, shape),
		safe,
		width,
		height,
		unit,
	};
};

const flexOf = (a?: string) => (a === 'start' ? 'flex-start' : a === 'end' ? 'flex-end' : a === 'between' ? 'space-between' : a === 'around' ? 'space-around' : a);

const areaStyle = (area: 'safe' | 'full', safe: Rect): React.CSSProperties =>
	area === 'safe' ? {position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h} : {position: 'absolute', inset: 0};

// ---------------------------------------------------------------- grid

export type GridProps = {
	columns?: Responsive<number>; // default {wide: 3, square: 2, portrait: 2, tall: 1}
	rows?: Responsive<number>; // share the height in this many rows (with fill); default: rows as tall as their content
	gap?: Responsive<number>; // gutter px at 1080 (default {wide: 32, tall: 24})
	rowGap?: Responsive<number>;
	align?: 'start' | 'center' | 'end' | 'stretch'; // cells on the cross axis (default stretch)
	fill?: boolean; // position on the area and fill it (default false: flows in its parent at full width)
	area?: 'safe' | 'full';
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

/** Columns and gutters. Tall frames get one column by default: restack, do not shrink. */
export const Grid: React.FC<GridProps> = ({columns = {wide: 3, square: 2, portrait: 2, tall: 1}, rows, gap = {wide: 32, tall: 24}, rowGap, align = 'stretch', fill = false, area = 'safe', style, children}) => {
	const {pick: p, unit, safe} = useLayout();
	const cols = Math.max(1, Math.round(p(columns)));
	const r = rows === undefined ? undefined : Math.max(1, Math.round(p(rows)));
	const g = p(gap) * unit;
	return (
		<div
			style={{
				...(fill ? areaStyle(area, safe) : {position: 'relative', width: '100%'}),
				display: 'grid',
				gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
				gridTemplateRows: r ? `repeat(${r}, minmax(0, 1fr))` : undefined,
				columnGap: g,
				rowGap: rowGap === undefined ? g : p(rowGap) * unit,
				alignItems: align,
				boxSizing: 'border-box',
				...style,
			}}
		>
			{children}
		</div>
	);
};

export type CellProps = {span?: Responsive<number>; rowSpan?: Responsive<number>; style?: React.CSSProperties; children?: React.ReactNode};

/** A grid cell that spans several columns or rows (per shape). */
export const Cell: React.FC<CellProps> = ({span = 1, rowSpan = 1, style, children}) => {
	const {pick: p} = useLayout();
	return <div style={{gridColumn: `span ${Math.max(1, Math.round(p(span)))}`, gridRow: `span ${Math.max(1, Math.round(p(rowSpan)))}`, minWidth: 0, ...style}}>{children}</div>;
};

// ---------------------------------------------------------------- stack

export type StackProps = {
	dir?: Responsive<'row' | 'column'>; // default column
	gap?: Responsive<number>; // px at 1080 (default 24)
	align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
	justify?: 'start' | 'center' | 'end' | 'between' | 'around';
	wrap?: boolean;
	fill?: boolean; // position on the area and fill it
	area?: 'safe' | 'full';
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

/** Items in a row or a column with one gap: `dir={{wide: 'row', tall: 'column'}}` restacks for vertical frames. */
export const Stack: React.FC<StackProps> = ({dir = 'column', gap = 24, align, justify, wrap = false, fill = false, area = 'safe', style, children}) => {
	const {pick: p, unit, safe} = useLayout();
	return (
		<div
			style={{
				...(fill ? areaStyle(area, safe) : {position: 'relative'}),
				display: 'flex',
				flexDirection: p(dir),
				gap: p(gap) * unit,
				alignItems: flexOf(align),
				justifyContent: flexOf(justify),
				flexWrap: wrap ? 'wrap' : 'nowrap',
				boxSizing: 'border-box',
				...style,
			}}
		>
			{children}
		</div>
	);
};

// ---------------------------------------------------------------- center

export type CenterProps = {
	area?: 'safe' | 'full';
	maxWidth?: Responsive<number>; // a fraction of the area's width (default {wide: 0.72, square: 0.86, portrait: 0.9, tall: 0.96})
	optical?: boolean; // sit a little above the geometric middle, where the eye puts the centre (default true)
	align?: 'center' | 'start'; // text alignment (default center)
	gap?: number; // px at 1080 between children (default 28)
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

/** Content centred in the safe area, with a readable measure and optical centring. */
export const Center: React.FC<CenterProps> = ({area = 'safe', maxWidth = {wide: 0.72, square: 0.86, portrait: 0.9, tall: 0.96}, optical = true, align = 'center', gap = 28, style, children}) => {
	const {pick: p, unit, safe, width, height} = useLayout();
	const box = area === 'safe' ? safe : {x: 0, y: 0, w: width, h: height};
	return (
		<div style={{...areaStyle(area, safe), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
			<div
				style={{
					width: box.w * clamp(p(maxWidth), 0.1, 1),
					display: 'flex',
					flexDirection: 'column',
					alignItems: align === 'center' ? 'center' : 'flex-start',
					textAlign: align === 'center' ? 'center' : 'left',
					gap: gap * unit,
					textWrap: 'balance',
					translate: optical ? `0px ${-box.h * 0.03}px` : undefined,
					...style,
				}}
			>
				{children}
			</div>
		</div>
	);
};

// ---------------------------------------------------------------- split

export type SplitProps = {
	ratio?: Responsive<number>; // share of the first part, 0.15 to 0.85 (default 0.5; 0.58 gives an asymmetric hero)
	dir?: Responsive<'row' | 'column'>; // default: row on wide and square, column on portrait and tall
	gap?: Responsive<number>; // px at 1080 between the parts' content (default 72)
	area?: 'safe' | 'full'; // safe: both parts inside the safe area; full: two full-bleed parts, content kept safe
	seam?: 'none' | 'line' | 'hard'; // hard: two grounds meet at the seam (needs area full)
	grounds?: [string, string]; // the two grounds for a hard seam (default: the theme's bg, then its accent)
	align?: 'start' | 'center' | 'end'; // content across the split axis (default: centred beside each other, left-aligned when stacked)
	justify?: [('start' | 'center' | 'end')?, ('start' | 'center' | 'end')?]; // each part's content along the split axis
	style?: React.CSSProperties;
	children: [React.ReactNode, React.ReactNode];
};

type Part = {x: number; y: number; w: number; h: number};

const splitRects = (safe: Rect, ratio: number, row: boolean, gap: number, full: boolean) => {
	if (full) {
		// the seam divides the safe area (not the frame), so both parts get the same room for content; on a
		// symmetric 16:9 safe area this is also the middle of the frame
		if (row) {
			const sx = safe.x + safe.w * ratio;
			const a: Part = {x: safe.x, y: safe.y, w: sx - gap / 2 - safe.x, h: safe.h};
			const b: Part = {x: sx + gap / 2, y: safe.y, w: safe.x + safe.w - sx - gap / 2, h: safe.h};
			return {a, b, seamAt: sx};
		}
		const sy = safe.y + safe.h * ratio;
		const a: Part = {x: safe.x, y: safe.y, w: safe.w, h: sy - gap / 2 - safe.y};
		const b: Part = {x: safe.x, y: sy + gap / 2, w: safe.w, h: safe.y + safe.h - sy - gap / 2};
		return {a, b, seamAt: sy};
	}
	if (row) {
		const wa = (safe.w - gap) * ratio;
		return {a: {x: safe.x, y: safe.y, w: wa, h: safe.h}, b: {x: safe.x + wa + gap, y: safe.y, w: safe.w - wa - gap, h: safe.h}, seamAt: safe.x + wa + gap / 2};
	}
	const ha = (safe.h - gap) * ratio;
	return {a: {x: safe.x, y: safe.y, w: safe.w, h: ha}, b: {x: safe.x, y: safe.y + ha + gap, w: safe.w, h: safe.h - ha - gap}, seamAt: safe.y + ha + gap / 2};
};

/** Two parts side by side (wide) or stacked (tall), optionally as two grounds meeting at a hard seam. */
export const Split: React.FC<SplitProps> = ({ratio = 0.5, dir = {wide: 'row', square: 'row', portrait: 'column', tall: 'column'}, gap = 72, area = 'safe', seam = 'none', grounds, align, justify = [], style, children}) => {
	const t = useTheme();
	const {pick: p, unit, safe} = useLayout();
	const row = p(dir) === 'row';
	const r = clamp(p(ratio), 0.15, 0.85);
	const g = p(gap) * unit;
	const full = area === 'full';
	const {a, b, seamAt} = splitRects(safe, r, row, g, full);
	const hard = seam === 'hard' && full;
	const gA = grounds?.[0] ?? t.colors.bg;
	const gB = grounds?.[1] ?? t.colors.accent;
	// the theme's onAccent is made for buttons; across a large part keep the more readable of it and the text colour
	const inkB = contrast(t.colors.onAccent, gB) >= 4.5 ? t.colors.onAccent : readableOn(gB, t.colors.onAccent, t.colors.text);
	const across = flexOf(align ?? (row ? 'center' : 'start'));
	const part = (rect: Part, child: React.ReactNode, j: 'start' | 'center' | 'end' | undefined, ink?: string, ground?: string) => (
		<div
			style={{
				position: 'absolute',
				left: rect.x,
				top: rect.y,
				width: rect.w,
				height: rect.h,
				display: 'flex',
				flexDirection: 'column',
				// a column box: justifyContent is vertical, alignItems horizontal
				justifyContent: row ? across : flexOf(j ?? 'center'),
				alignItems: row ? flexOf(j ?? 'start') : across,
				color: ink,
				boxSizing: 'border-box',
			}}
		>
			{ground ? <OnTone dark={isDark(ground)}>{child}</OnTone> : child}
		</div>
	);
	return (
		<AbsoluteFill style={style}>
			{hard ? (
				<>
					<AbsoluteFill style={row ? {width: seamAt, background: gA} : {height: seamAt, background: gA}} />
					<AbsoluteFill style={row ? {left: seamAt, background: gB} : {top: seamAt, background: gB}} />
				</>
			) : null}
			{seam === 'line' ? (
				<div
					style={{
						position: 'absolute',
						background: t.colors.line,
						...(row ? {left: seamAt - unit, top: safe.y, width: 2 * unit, height: safe.h} : {top: seamAt - unit, left: safe.x, height: 2 * unit, width: safe.w}),
					}}
				/>
			) : null}
			{part(a, children[0], justify[0], hard ? readableOn(gA, '#FFFFFF', t.colors.text) : undefined, hard ? gA : undefined)}
			{part(b, children[1], justify[1], hard ? inkB : undefined, hard ? gB : undefined)}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- stat split

// average advance of a digit, in em, for the kit's display faces (wide faces need a smaller size to fit)
const DIGIT_EM: Partial<Record<string, number>> = {
	RubikMonoOne: 0.9,
	PressStart2P: 1.0,
	Unbounded: 0.74,
	ArchivoBlack: 0.66,
	Syne: 0.64,
	Montserrat: 0.66,
	Anton: 0.46,
	BebasNeue: 0.4,
	Oswald: 0.5,
	Cinzel: 0.66,
	PermanentMarker: 0.62,
};

const digitEm = (t: Theme) => DIGIT_EM[t.fonts.display] ?? (FONTS[t.fonts.display]?.kind === 'mono' ? 0.62 : 0.6);

export type StatSplitProps = {
	value: React.ReactNode; // the number ("87%", "3.2x", "12,480") or a counter component
	sample?: string; // the widest text the value shows, for sizing (default: value when it is a string); give it for counters
	label: React.ReactNode; // what the number means: one short sentence
	note?: React.ReactNode; // a source line or small print
	color?: string; // the number's colour (default the accent)
	ratio?: Responsive<number>; // the number's share of the safe area (default {wide: 0.58, square: 0.56, portrait: 0.5, tall: 0.46})
	size?: number; // the number's font size, px at 1080 (default: as big as its box allows, measured)
	align?: 'bottom' | 'center'; // the label against the number (default bottom)
	style?: React.CSSProperties;
};

/**
 * One big number and its meaning: side by side on wide frames, number over label on tall ones. The number is
 * sized to its box by measuring the text in the loaded font, so "87%" or "$1.2M" never runs out of the frame.
 */
export const StatSplit: React.FC<StatSplitProps> = ({value, sample, label, note, color, ratio = {wide: 0.58, square: 0.56, portrait: 0.5, tall: 0.46}, size, align = 'bottom', style}) => {
	const t = useTheme();
	const {pick: p, unit, safe, tall} = useLayout();
	const r = clamp(p(ratio), 0.3, 0.75);
	const gap = (tall ? 40 : 72) * unit;
	const text = sample ?? (typeof value === 'string' || typeof value === 'number' ? String(value) : null);
	const tracking = `${Math.min(t.tracking.display, -0.02)}em`;
	const measured = useTextEm(size ? null : text, {fontFamily: t.type.display, fontWeight: t.weights.display, letterSpacing: tracking, textTransform: t.caps ? 'uppercase' : 'none'});
	const em = measured ?? estimateEm(text ?? '0000', digitEm(t));
	const boxW = tall ? safe.w : (safe.w - gap) * r;
	const boxH = tall ? (safe.h - gap) * r : safe.h * 0.8;
	const fitted = Math.min(boxH / 0.95, (boxW * 0.97) / em);
	const fs = size ? size * unit : fitted;
	const number = (
		<div
			style={{
				fontFamily: t.type.display,
				fontWeight: t.weights.display,
				fontSize: fs,
				lineHeight: 0.84,
				letterSpacing: tracking,
				fontVariantNumeric: 'tabular-nums',
				color: color ?? t.colors.accent,
				whiteSpace: 'nowrap',
				textTransform: t.caps ? 'uppercase' : 'none',
			}}
		>
			{value}
		</div>
	);
	const caption = (
		<div style={{display: 'flex', flexDirection: 'column', gap: 18 * unit, maxWidth: tall ? safe.w : 640 * unit, paddingBottom: !tall && align === 'bottom' ? fs * 0.04 : 0}}>
			<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: (tall ? 50 : 46) * unit, lineHeight: 1.18, color: t.colors.text, textWrap: 'balance'}}>{label}</div>
			{note ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 28 * unit, lineHeight: 1.3, color: t.colors.muted}}>{note}</div> : null}
		</div>
	);
	return (
		<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', ...style}}>
			<div style={{display: 'flex', flexDirection: tall ? 'column' : 'row', alignItems: tall ? 'flex-start' : align === 'bottom' ? 'flex-end' : 'center', gap}}>
				<div style={{maxWidth: boxW, flex: 'none', display: 'flex', alignItems: 'flex-end'}}>{number}</div>
				{caption}
			</div>
		</div>
	);
};

// ---------------------------------------------------------------- full bleed

export type TextPlace = 'bottom-left' | 'bottom' | 'left' | 'center' | 'top-left';

export type FullBleedProps = {
	src?: string; // a picture (staticFile() or a URL), shown with object-fit cover
	background?: React.ReactNode; // anything full-bleed instead of a picture (a video, a Mesh)
	focus?: [number, number]; // the picture's point to keep in frame, 0 to 1 (default [0.5, 0.5])
	push?: number; // a slow push-in over the Sequence (default 0.04; 0 = still)
	place?: Responsive<TextPlace>; // where the text sits (default {wide: 'bottom-left', tall: 'bottom'})
	scrim?: ScrimProps['side'] | 'auto' | false; // default auto: from the text's side
	strength?: number; // scrim darkness (default 0.72)
	maxWidth?: Responsive<number>; // the text block's width, a fraction of the safe width (default {wide: 0.56, square: 0.84, tall: 1})
	tone?: 'light' | 'dark'; // light: white text over a dark scrim (default); dark: dark text over a light scrim
	area?: 'safe' | 'box'; // safe: text inside the frame's safe area (a whole frame); box: inside the parent box (a card)
	pad?: number; // box mode: the inner margin, px at 1080 (default 44)
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/**
 * A picture edge to edge with text on a scrim: the classic editorial frame, laid out per shape. For a picture
 * inside a card or a grid cell, use area="box" so the text keeps to that box instead of the frame's safe area.
 */
export const FullBleed: React.FC<FullBleedProps> = ({
	src,
	background,
	focus = [0.5, 0.5],
	push = 0.04,
	place = {wide: 'bottom-left', square: 'bottom-left', portrait: 'bottom', tall: 'bottom'},
	scrim = 'auto',
	strength = 0.72,
	maxWidth = {wide: 0.56, square: 0.84, portrait: 0.92, tall: 1},
	tone = 'light',
	area = 'safe',
	pad = 44,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {pick: p, safe, unit} = useLayout();
	const inBox = area === 'box';
	const {durationInFrames} = useStage();
	const where = p(place);
	const k = Number.isFinite(durationInFrames) ? ramp(frame, 0, durationInFrames, curves.sine) : 0;
	const side: ScrimProps['side'] = where === 'left' ? 'left' : where === 'center' ? 'center' : where === 'top-left' ? 'top' : 'bottom';
	const scrimSide = scrim === 'auto' ? side : scrim;
	const light = tone === 'light';
	const ink = light ? '#FFFFFF' : t.colors.text;
	const box: React.CSSProperties = {
		position: 'absolute',
		...(inBox ? {inset: 0, padding: pad * unit, boxSizing: 'border-box'} : {left: safe.x, top: safe.y, width: safe.w, height: safe.h}),
		display: 'flex',
		flexDirection: 'column',
		justifyContent: where === 'top-left' ? 'flex-start' : where === 'left' || where === 'center' ? 'center' : 'flex-end',
		alignItems: where === 'center' || where === 'bottom' ? 'center' : 'flex-start',
		textAlign: where === 'center' || where === 'bottom' ? 'center' : 'left',
		textWrap: 'balance',
		color: ink,
	};
	return (
		<AbsoluteFill style={{overflow: 'hidden', background: t.colors.bg2, ...style}}>
			<AbsoluteFill style={{scale: String(1 + push * k), transformOrigin: `${focus[0] * 100}% ${focus[1] * 100}%`}}>
				{background ?? (src ? <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${focus[0] * 100}% ${focus[1] * 100}%`}} /> : null)}
			</AbsoluteFill>
			{scrimSide ? <Scrim side={scrimSide} strength={strength} color={light ? '#000000' : t.colors.bg} size={scrimSide === 'left' ? 0.72 : 0.66} /> : null}
			<div style={box}>
				<OnTone dark={light}>
					<div style={{width: inBox ? `${clamp(p(maxWidth), 0.2, 1) * 100}%` : safe.w * clamp(p(maxWidth), 0.2, 1), display: 'flex', flexDirection: 'column', gap: 22 * unit, alignItems: 'inherit'}}>{children}</div>
				</OnTone>
			</div>
		</AbsoluteFill>
	);
};
