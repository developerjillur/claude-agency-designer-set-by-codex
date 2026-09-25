// <Callout>: a speech-bubble label whose pointer tip lands exactly on a point, built with makeCallout from
// @remotion/shapes around its measured text. It pops out of the point it names, stays inside its bounds (the
// pointer slides along the edge to keep the tip on the point) and leaves at the end of its Sequence.
import {makeCallout} from '@remotion/shapes';
import React, {useRef} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Rect} from '../core';
import {ramp} from '../motion';
import {textColorOn} from './color';
import {useMeasuredSize} from './measure';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type CalloutSide = 'top' | 'bottom' | 'left' | 'right' | 'auto';

export type CalloutProps = GraphicExitProps & {
	x: number; // the point the pointer touches, in px of the positioned parent (frame px on a full-frame layer)
	y: number;
	side?: CalloutSide; // where the bubble sits relative to the point (default 'top'; 'auto' picks the roomier side)
	title?: React.ReactNode; // a bold first line
	text?: React.ReactNode;
	children?: React.ReactNode; // instead of text
	maxWidth?: number; // px at 1080 (default 460): longer text wraps
	fontSize?: number; // px at 1080 (default 32)
	tone?: 'surface' | 'accent' | 'ink'; // bubble colour from the theme (default 'surface' on light themes, 'accent' on dark)
	fill?: string;
	color?: string; // text colour (default: readable on the fill)
	pointerLength?: number; // px at 1080 (default 26)
	pointerWidth?: number; // px at 1080 (default 34)
	radius?: number; // px at 1080 (default: the theme radius, at most 22)
	bounds?: Rect; // keep the bubble inside this box (parent px; default the safe area)
	delay?: number;
	shadow?: boolean; // default true on light themes
	align?: 'left' | 'center';
};

export const Callout: React.FC<CalloutProps> = ({
	x,
	y,
	side = 'top',
	title,
	text,
	children,
	maxWidth = 460,
	fontSize = 32,
	tone,
	fill,
	color,
	pointerLength = 26,
	pointerWidth = 34,
	radius,
	bounds,
	delay = 0,
	shadow,
	align = 'left',
	exit = 'shrink',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps, safe} = useStage();
	const ref = useRef<HTMLDivElement>(null);
	const box = useMeasuredSize(ref, 'graphics: measuring a callout', {lines: true});
	const q = useGraphicExit({exit, outDuration, outAt});
	const kind = tone ?? (t.dark ? 'accent' : 'surface');
	const bg = fill ?? (kind === 'accent' ? t.colors.accent : kind === 'ink' ? t.colors.text : t.colors.surface);
	const fg = color ?? (kind === 'accent' ? t.colors.onAccent : textColorOn(bg, '#FFFFFF', t.colors.text));
	const b = bounds ?? safe;
	const pl = pointerLength * unit;
	const pb = pointerWidth * unit;
	const r = Math.min(radius ?? t.radius, 22) * unit;
	const pop = ramp(frame, delay, at30(16, fps), curves.outBack);
	const fade = ramp(frame, delay, at30(8, fps), curves.out);
	const hasShadow = shadow ?? !t.dark;

	// Wrapped text keeps its box at the maximum width, which would leave empty space in the bubble beside balanced
	// lines. The text keeps its natural layout (it is never re-flowed: balanced wrapping in a narrower box can break
	// differently) and only the bubble is drawn to the widest line.
	const padX = fontSize * 0.75 * unit;
	const textStyle: React.CSSProperties = {
		width: 'max-content',
		maxWidth: maxWidth * unit,
		padding: `${fontSize * 0.55 * unit}px ${padX}px`,
		boxSizing: 'border-box',
		fontFamily: t.type.body,
		fontWeight: t.weights.body,
		fontSize: fontSize * unit,
		lineHeight: 1.25,
		color: fg,
		textAlign: align,
		textWrap: 'balance',
		textRendering: 'geometricPrecision',
	};
	const content = (
		<div ref={ref} style={textStyle}>
			{title ? <div style={{fontWeight: t.weights.strong, marginBottom: text || children ? 4 * unit : 0}}>{title}</div> : null}
			{text ?? children}
		</div>
	);
	const natural = box?.w ?? 0;
	const tight = box?.line ? Math.min(natural, Math.ceil(box.line + 2 * padX + 2 * unit)) : undefined;
	// centred lines sit in the middle of the natural box: move the box so they sit in the middle of the bubble
	const shift = tight !== undefined && align === 'center' ? (natural - tight) / 2 : 0;

	// the same tree before and after measuring, so the measured node is never swapped out
	const w = tight ?? natural;
	const h = box?.h ?? 0;
	if (!box || w <= 0 || h <= 0) {
		return (
			<div style={{position: 'absolute', left: 0, top: 0, visibility: 'hidden'}}>
				{null}
				<div style={{position: 'absolute', left: 0, top: 0}}>{content}</div>
			</div>
		);
	}
	let s: Exclude<CalloutSide, 'auto'> = side === 'auto' ? 'top' : side;
	if (side === 'auto' || side === 'top' || side === 'bottom') {
		const roomAbove = y - b.y;
		const roomBelow = b.y + b.h - y;
		const need = h + pl + 6 * unit;
		if (side === 'auto') {
			s = roomAbove >= need || roomAbove >= roomBelow ? 'top' : 'bottom';
		} else if (s === 'top' && roomAbove < need && roomBelow > roomAbove) {
			s = 'bottom';
		} else if (s === 'bottom' && roomBelow < need && roomAbove > roomBelow) {
			s = 'top';
		}
	} else {
		const roomLeft = x - b.x;
		const roomRight = b.x + b.w - x;
		const need = w + pl + 6 * unit;
		if (s === 'left' && roomLeft < need && roomRight > roomLeft) {
			s = 'right';
		} else if (s === 'right' && roomRight < need && roomLeft > roomRight) {
			s = 'left';
		}
	}
	const vertical = s === 'top' || s === 'bottom';
	const along = vertical ? w : h;
	const minPP = Math.min(0.5, (r + pb / 2 + 2 * unit) / along);
	let pp: number;
	if (vertical) {
		// wider than its bounds: centre it on them; otherwise keep it inside
		const left = w > b.w ? b.x + (b.w - w) / 2 : Math.min(Math.max(x - w / 2, b.x), b.x + b.w - w);
		pp = (x - left) / w;
	} else {
		const top = h > b.h ? b.y + (b.h - h) / 2 : Math.min(Math.max(y - h / 2, b.y), b.y + b.h - h);
		pp = (y - top) / h;
	}
	pp = Math.min(1 - minPP, Math.max(minPP, pp));
	const dir = s === 'top' ? 'down' : s === 'bottom' ? 'up' : s === 'left' ? 'right' : 'left';
	const shape = makeCallout({
		width: w,
		height: h,
		pointerLength: pl,
		pointerBaseWidth: pb,
		pointerPosition: pp,
		pointerDirection: dir,
		cornerRadius: Math.min(r, h / 2, w / 2),
	});
	const tip =
		dir === 'down' ? {x: pp * w, y: h + pl} : dir === 'up' ? {x: pp * w, y: 0} : dir === 'right' ? {x: w + pl, y: pp * h} : {x: 0, y: pp * h};
	const bodyX = dir === 'left' ? pl : 0;
	const bodyY = dir === 'up' ? pl : 0;
	const scaleIn = 0.55 + 0.45 * pop;
	const scaleOut = exit === 'shrink' ? 1 - 0.45 * q : 1;
	const opacity = fade * (exit === 'none' ? 1 : 1 - q);
	return (
		<div
			style={{
				position: 'absolute',
				left: x - tip.x,
				top: y - tip.y,
				width: shape.width,
				height: shape.height,
				transformOrigin: `${tip.x}px ${tip.y}px`,
				scale: `${scaleIn * scaleOut}`,
				opacity,
				visibility: opacity <= 0.001 ? 'hidden' : 'visible',
				filter: hasShadow && opacity > 0.001 ? `drop-shadow(0 ${6 * unit}px ${14 * unit}px rgba(15, 23, 42, 0.16))` : undefined,
			}}
		>
			<svg width={shape.width} height={shape.height} viewBox={`0 0 ${shape.width} ${shape.height}`} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				<path d={shape.path} fill={bg} />
			</svg>
			<div style={{position: 'absolute', left: bodyX - shift, top: bodyY}}>{content}</div>
		</div>
	);
};
