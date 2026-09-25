// Masks: show children through a shape, text, gradient or a moving wipe. All synchronous CSS (clip-path paths,
// gradient mask-images, an inline SVG clipPath for text), so every frame is complete when it is captured: no
// image masks that could still be loading.
import {parsePath, reduceInstructions, serializeInstructions, getBoundingBox, scalePath, translatePath} from '@remotion/paths';
import {makeCircle, makeHeart, makePolygon, makeRect, makeStar, makeTriangle} from '@remotion/shapes';
import {Video} from '@remotion/media';
import React, {useLayoutEffect, useMemo, useState} from 'react';
import {AbsoluteFill, Img, cancelRender, continueRender, delayRender, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {inHoldOut, ramp} from '../motion';
import {finite, useSafeId} from './util';

const HIDE = 'inset(50% 50% 50% 50%)';

/** Rotates every point of a path around (cx, cy). The result has only M, L, C and Z. */
export const rotatePath = (d: string, degrees: number, cx: number, cy: number): string => {
	if (!degrees) {
		return d;
	}
	const a = (degrees * Math.PI) / 180;
	const cos = Math.cos(a);
	const sin = Math.sin(a);
	const rx = (x: number, y: number) => cx + (x - cx) * cos - (y - cy) * sin;
	const ry = (x: number, y: number) => cy + (x - cx) * sin + (y - cy) * cos;
	const out = reduceInstructions(parsePath(d)).map((ins) => {
		if (ins.type === 'M' || ins.type === 'L') {
			return {...ins, x: rx(ins.x, ins.y), y: ry(ins.x, ins.y)};
		}
		if (ins.type === 'C') {
			return {
				...ins,
				cp1x: rx(ins.cp1x, ins.cp1y),
				cp1y: ry(ins.cp1x, ins.cp1y),
				cp2x: rx(ins.cp2x, ins.cp2y),
				cp2y: ry(ins.cp2x, ins.cp2y),
				x: rx(ins.x, ins.y),
				y: ry(ins.x, ins.y),
			};
		}
		return ins;
	});
	return serializeInstructions(out);
};

export type MaskShape = 'circle' | 'rect' | 'star' | 'heart' | 'triangle' | 'polygon' | {path: string};

export type ShapePathOptions = {
	shape: MaskShape;
	/** Centre in px. */
	cx: number;
	cy: number;
	/** Size in px: circle, star and polygon diameter, rect and heart height, triangle side, custom path longest side. */
	size: number;
	aspect?: number; // rect width / height (1)
	radius?: number; // corner radius in px
	points?: number; // star (5) and polygon (6) points
	inner?: number; // star inner radius / outer radius (0.5)
	rotate?: number; // degrees
};

/** An SVG path for a mask shape centred on (cx, cy), or null when it is too small to draw. */
export const shapePath = (o: ShapePathOptions): string | null => {
	const s = Math.max(0, finite(o.size, 0));
	if (s < 0.5) {
		return null;
	}
	const r = s / 2;
	const corner = Math.max(0, finite(o.radius, 0));
	let d: string;
	if (o.shape === 'circle') {
		d = translatePath(makeCircle({radius: r}).path, o.cx - r, o.cy - r);
	} else if (o.shape === 'rect') {
		const w = s * Math.max(0.05, finite(o.aspect, 1));
		d = translatePath(makeRect({width: w, height: s, cornerRadius: Math.min(corner, s / 2, w / 2)}).path, o.cx - w / 2, o.cy - r);
	} else if (o.shape === 'star') {
		const info = makeStar({points: Math.max(3, Math.round(o.points ?? 5)), outerRadius: r, innerRadius: r * Math.min(0.95, Math.max(0.1, o.inner ?? 0.5)), cornerRadius: corner});
		d = translatePath(info.path, o.cx - info.width / 2, o.cy - info.height / 2);
	} else if (o.shape === 'polygon') {
		const info = makePolygon({points: Math.max(3, Math.round(o.points ?? 6)), radius: r, cornerRadius: corner});
		d = translatePath(info.path, o.cx - info.width / 2, o.cy - info.height / 2);
	} else if (o.shape === 'heart') {
		const info = makeHeart({height: s});
		d = translatePath(info.path, o.cx - info.width / 2, o.cy - info.height / 2);
	} else if (o.shape === 'triangle') {
		const info = makeTriangle({length: s, direction: 'up', cornerRadius: corner});
		d = translatePath(info.path, o.cx - info.width / 2, o.cy - info.height / 2);
	} else {
		const box = getBoundingBox(o.shape.path);
		const k = s / Math.max(1e-6, box.width, box.height);
		const scaled = scalePath(translatePath(o.shape.path, -box.x1, -box.y1), k, k);
		d = translatePath(scaled, o.cx - (box.width * k) / 2, o.cy - (box.height * k) / 2);
	}
	return rotatePath(d, finite(o.rotate, 0), o.cx, o.cy);
};

/** The size (as in shapePath) that makes a shape centred at (cx, cy) cover a w x h frame. */
export const coverSize = (shape: MaskShape, cx: number, cy: number, w: number, h: number, o: {aspect?: number; points?: number; inner?: number} = {}): number => {
	const dx = Math.max(cx, w - cx);
	const dy = Math.max(cy, h - cy);
	const d = Math.hypot(dx, dy);
	if (shape === 'circle') {
		return 2 * d * 1.01;
	}
	if (shape === 'rect') {
		const a = Math.max(0.05, o.aspect ?? 1);
		return 2 * Math.max(dy, dx / a) * 1.04;
	}
	if (shape === 'star') {
		return (2 * d) / Math.min(0.95, Math.max(0.1, o.inner ?? 0.5)) * 1.03;
	}
	if (shape === 'polygon') {
		return (2 * d) / Math.cos(Math.PI / Math.max(3, o.points ?? 6)) * 1.02;
	}
	if (shape === 'triangle') {
		return 4.2 * d;
	}
	return 3 * d;
};

type Timing = {
	/** 0 to 1: drive the mask yourself. When set, delay/duration/exit are ignored. */
	progress?: number;
	delay?: number;
	duration?: number; // frames of the reveal (default about 0.8 s)
	ease?: Ease;
	/** Hide again at the end of the Sequence (the exit ends on its last frame). */
	exit?: boolean;
	outDuration?: number;
};

const useMaskProgress = (t: Timing, fallbackIn: number) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useStage();
	if (t.progress !== undefined) {
		return Math.min(1, Math.max(0, finite(t.progress, 1)));
	}
	const inF = t.duration ?? at30(fallbackIn, fps);
	const outF = t.outDuration ?? Math.max(1, Math.round(inF * 0.8));
	const end = t.exit && Number.isFinite(durationInFrames) ? durationInFrames - 1 : Infinity;
	return inHoldOut(frame, t.delay ?? 0, inF, end, outF, t.ease ?? curves.inOut, t.ease ?? curves.inOut);
};

export type ShapeMaskProps = Timing & {
	shape?: MaskShape;
	/** Final size in px at 1080 (see shapePath), or 'cover' to fill the frame from `at`. Default 'cover'. */
	size?: number | 'cover';
	/** Centre as fractions of the frame. */
	at?: readonly [number, number];
	aspect?: number;
	radius?: number; // px at 1080
	points?: number;
	inner?: number;
	rotate?: number; // degrees; add a turn during the reveal with `spin`
	spin?: number; // extra degrees turned over the reveal
	/** Soft edge in px at 1080 (circle only; other shapes are hard edged). */
	feather?: number;
	/** An outline following the mask edge: true uses the theme accent. */
	ring?: boolean | {color?: string; width?: number};
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** Children seen through a growing shape: circle, rect, star, heart, triangle, polygon or your own SVG path. */
export const ShapeMask: React.FC<ShapeMaskProps> = ({shape = 'circle', size = 'cover', at = [0.5, 0.5], aspect, radius = 0, points, inner, rotate = 0, spin = 0, feather = 0, ring = false, children, style, ...timing}) => {
	const {width, height, unit} = useStage();
	const t = useTheme();
	const p = useMaskProgress(timing, 24);
	const cx = at[0] * width;
	const cy = at[1] * height;
	const full = size === 'cover' ? coverSize(shape, cx, cy, width, height, {aspect: aspect ?? width / height, points, inner}) : size * unit;
	const s = full * p;
	const d = shapePath({shape, cx, cy, size: s, aspect: aspect ?? (shape === 'rect' && size === 'cover' ? width / height : 1), radius: radius * unit, points, inner, rotate: rotate + spin * (1 - p)});
	const f = feather * unit;
	const soft = shape === 'circle' && f > 0;
	const mask = soft
		? `radial-gradient(circle ${Math.max(0.01, s / 2 + f / 2)}px at ${cx}px ${cy}px, #000 ${Math.max(0, s / 2 - f / 2)}px, transparent ${Math.max(0.01, s / 2 + f / 2)}px)`
		: undefined;
	const ringSpec = ring === true ? {} : ring || null;
	return (
		<AbsoluteFill style={style}>
			<AbsoluteFill
				style={{
					clipPath: soft ? undefined : d ? `path('${d}')` : HIDE,
					WebkitMaskImage: mask,
					maskImage: mask,
					visibility: s <= 0.5 && !soft ? 'hidden' : undefined,
				}}
			>
				{children}
			</AbsoluteFill>
			{ringSpec && d ? (
				<svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none'}}>
					<path d={d} fill="none" stroke={ringSpec.color ?? t.colors.accent} strokeWidth={(ringSpec.width ?? 6) * unit} />
				</svg>
			) : null}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- text mask

const measureLines = (lines: string[], font: string, spacingEm: number): number[] => {
	const canvas = document.createElement('canvas');
	const ctx = canvas.getContext('2d');
	if (!ctx) {
		return lines.map(() => 1);
	}
	ctx.font = font;
	// letterSpacing on a 2D context is a Chrome feature; the measure is at 100 px
	(ctx as CanvasRenderingContext2D & {letterSpacing?: string}).letterSpacing = `${spacingEm * 100}px`;
	return lines.map((l) => Math.max(1, ctx.measureText(l).width));
};

/** True once the fonts `spec` needs for `text` are loaded; holds the render until then. */
const useFontsFor = (spec: string, text: string): boolean => {
	const [ready, setReady] = useState(false);
	const [handle] = useState(() => delayRender(`Loading fonts for a text mask (${spec})`));
	useLayoutEffect(() => {
		let done = false;
		document.fonts
			.load(spec, text)
			.then(() => document.fonts.ready)
			.then(() => {
				if (!done) {
					done = true;
					setReady(true);
					continueRender(handle);
				}
			})
			.catch((err) => cancelRender(err));
		return () => {
			if (!done) {
				done = true;
				continueRender(handle);
			}
		};
	}, [handle, spec, text]);
	return ready;
};

export type TextMaskProps = {
	/** The words; '\n' breaks lines. Bangla works (the text is shaped by the browser, never split). */
	text: string;
	/** What shows through the letters: any children (a Video, a TransitionSeries, a gradient div). */
	children?: React.ReactNode;
	/** Shorthand fill: an image or video file (by extension), cover fitted. */
	src?: string;
	/** Shorthand fill: a CSS gradient. */
	gradient?: string;
	/** CSS font-family stack (default: the theme's display stack) and weight. */
	font?: string;
	weight?: number;
	/** Font size in px at 1080. Default: fitted so the longest line fills `fit` of the safe width. */
	size?: number;
	fit?: number;
	maxSize?: number; // px at 1080 (default 420)
	lineHeight?: number; // (0.9)
	tracking?: number; // em (default: the theme's display tracking)
	caps?: boolean; // default: the theme's caps setting
	at?: readonly [number, number];
	/** A thin outline drawn around the letters (helps on busy fills). */
	outline?: {color?: string; width?: number} | boolean;
	/** Slow push of the fill inside the letters over the Sequence: 0.08 scales it from 1.08 to 1. */
	fillZoom?: number;
	/** Colour outside the letters (default transparent). */
	background?: string;
	style?: React.CSSProperties;
};

const isVideo = (src: string) => /\.(mp4|webm|mov|m4v|mkv)(\?|#|$)/i.test(src);

/** Big words filled with a picture, a video, a gradient or any animated children (an SVG clipPath of real text). */
export const TextMask: React.FC<TextMaskProps> = ({text, children, src, gradient, font, weight, size, fit = 0.9, maxSize = 420, lineHeight = 0.9, tracking, caps, at = [0.5, 0.5], outline = false, fillZoom = 0, background, style}) => {
	const t = useTheme();
	const frame = useCurrentFrame();
	const {width, height, unit, safe, durationInFrames} = useStage();
	const id = useSafeId('tmask');
	const family = font ?? t.type.display;
	const w = weight ?? t.weights.display;
	const track = tracking ?? t.tracking.display;
	const upper = caps ?? t.caps;
	const shown = upper ? text.toUpperCase() : text;
	const lines = useMemo(() => shown.split('\n'), [shown]);
	const spec = `${w} 100px ${family}`;
	const ready = useFontsFor(spec, shown);
	const fontSize = useMemo(() => {
		if (size !== undefined) {
			return size * unit;
		}
		if (!ready) {
			return 100 * unit;
		}
		const widest = Math.max(...measureLines(lines, spec, track));
		return Math.min(maxSize * unit, ((fit * safe.w) / widest) * 100);
	}, [ready, size, unit, spec, track, lines, fit, safe.w, maxSize]);
	const cx = at[0] * width;
	const cy = at[1] * height;
	const lh = fontSize * lineHeight;
	const zoom = fillZoom > 0 && Number.isFinite(durationInFrames) ? 1 + fillZoom * (1 - ramp(frame, 0, durationInFrames, curves.sine)) : 1;
	const fill =
		children ??
		(src ? (
			isVideo(src) ? (
				<Video src={src} muted objectFit="cover" style={{width, height}} />
			) : (
				<Img src={src} style={{width, height, objectFit: 'cover'}} />
			)
		) : (
			<AbsoluteFill style={{background: gradient ?? `linear-gradient(135deg, ${t.colors.accent}, ${t.colors.accent2})`}} />
		));
	const textEls = (extra: React.SVGProps<SVGTextElement>) =>
		lines.map((l, i) => (
			<text
				key={i}
				x={cx}
				y={cy + (i - (lines.length - 1) / 2) * lh}
				textAnchor="middle"
				dominantBaseline="central"
				fontFamily={family}
				fontWeight={w}
				fontSize={fontSize}
				letterSpacing={`${track}em`}
				{...extra}
			>
				{l}
			</text>
		));
	const ring = outline === true ? {} : outline || null;
	return (
		<AbsoluteFill style={{background, visibility: ready ? undefined : 'hidden', ...style}}>
			<svg width="0" height="0" style={{position: 'absolute'}}>
				<clipPath id={id}>{textEls({})}</clipPath>
			</svg>
			{ring ? (
				// drawn under the fill at twice the width: only the outer half shows, so the overlapping contours
				// inside variable-font glyphs never draw lines through the letters
				<svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none'}}>
					{textEls({fill: 'none', stroke: ring.color ?? t.colors.text, strokeWidth: 2 * (ring.width ?? 2) * unit, strokeLinejoin: 'round'})}
				</svg>
			) : null}
			<AbsoluteFill style={{clipPath: `url(#${id})`}}>
				<AbsoluteFill style={{scale: String(zoom)}}>{fill}</AbsoluteFill>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- gradient mask

export type GradientFade = 'bottom' | 'top' | 'left' | 'right' | 'edges' | 'radial';

export type GradientMaskProps = {
	/** Which side fades out ('edges' feathers all four, 'radial' keeps the centre). */
	fade?: GradientFade;
	/** Share of the box the fade covers, 0 to 1 (0.35). */
	size?: number;
	/** A custom linear angle in degrees instead of `fade` (the gradient runs toward it, opaque first). */
	angle?: number;
	/** Swap what is kept and what fades. */
	invert?: boolean;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** Fades children out toward an edge, all edges, or around the centre (mask-image gradients). */
export const GradientMask: React.FC<GradientMaskProps> = ({fade = 'bottom', size = 0.35, angle, invert = false, children, style}) => {
	const k = Math.min(1, Math.max(0.001, size)) * 100;
	const on = invert ? 'transparent' : '#000';
	const offc = invert ? '#000' : 'transparent';
	const lin = (dir: string) => `linear-gradient(${dir}, ${on} ${100 - k}%, ${offc} 100%)`;
	let mask: string;
	let composite = false;
	if (angle !== undefined) {
		mask = lin(`${angle}deg`);
	} else if (fade === 'edges') {
		const e = k / 2;
		mask = `linear-gradient(to right, ${offc} 0%, ${on} ${e}%, ${on} ${100 - e}%, ${offc} 100%), linear-gradient(to bottom, ${offc} 0%, ${on} ${e}%, ${on} ${100 - e}%, ${offc} 100%)`;
		composite = true;
	} else if (fade === 'radial') {
		mask = `radial-gradient(ellipse farthest-side at 50% 50%, ${on} ${100 - k}%, ${offc} 100%)`;
	} else {
		mask = lin(fade === 'bottom' ? 'to bottom' : fade === 'top' ? 'to top' : fade === 'left' ? 'to left' : 'to right');
	}
	return (
		<AbsoluteFill
			style={{
				WebkitMaskImage: mask,
				maskImage: mask,
				WebkitMaskComposite: composite ? (invert ? 'source-over' : 'source-in') : undefined,
				maskComposite: composite ? (invert ? 'add' : 'intersect') : undefined,
				...style,
			}}
		>
			{children}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- wipe mask

export type WipeFrom = 'left' | 'right' | 'top' | 'bottom' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';

export type WipeMaskProps = Timing & {
	/** Where the reveal starts (linear), or a gradient angle in degrees. */
	from?: WipeFrom | number;
	/** linear: one edge; radial: a circle from `at`; split: opens from the middle; blinds: slats. */
	kind?: 'linear' | 'radial' | 'split' | 'blinds';
	/** Soft edge in px at 1080 (0 = hard). */
	feather?: number;
	at?: readonly [number, number];
	slats?: number;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

const FROM_ANGLE: Record<WipeFrom, number> = {left: 90, right: 270, top: 180, bottom: 0, topLeft: 135, topRight: 225, bottomLeft: 45, bottomRight: 315};

/** A soft or hard wipe that reveals children (and hides them again with `exit`). */
export const WipeMask: React.FC<WipeMaskProps> = ({from = 'left', kind = 'linear', feather = 80, at = [0.5, 0.5], slats = 8, children, style, ...timing}) => {
	const {width, height, unit, durationInFrames, fps} = useStage();
	const frame = useCurrentFrame();
	const inF = timing.duration ?? at30(22, fps);
	const outF = timing.outDuration ?? Math.max(1, Math.round(inF * 0.8));
	const ease = timing.ease ?? curves.inOut;
	const explicit = timing.progress !== undefined;
	const pIn = explicit ? Math.min(1, Math.max(0, finite(timing.progress, 1))) : ramp(frame, timing.delay ?? 0, inF, ease);
	const pOut = !explicit && timing.exit && Number.isFinite(durationInFrames) ? ramp(frame, durationInFrames - 1 - outF, outF, ease) : 0;
	const deg = typeof from === 'number' ? from : FROM_ANGLE[from];
	const a = (deg * Math.PI) / 180;
	const L = Math.abs(width * Math.sin(a)) + Math.abs(height * Math.cos(a));
	const f = Math.max(0, feather * unit);
	const fp = (f / L) * 100;
	let mask: string;
	if (kind === 'radial') {
		const cx = at[0] * width;
		const cy = at[1] * height;
		const far = Math.hypot(Math.max(cx, width - cx), Math.max(cy, height - cy)) + f;
		const rIn = pIn * far;
		const rOut = pOut * far;
		mask =
			pOut > 0
				? `radial-gradient(circle ${far}px at ${cx}px ${cy}px, transparent ${Math.max(0, rOut - f)}px, #000 ${rOut}px)`
				: `radial-gradient(circle ${Math.max(0.01, rIn)}px at ${cx}px ${cy}px, #000 ${Math.max(0, rIn - f)}px, transparent ${Math.max(0.01, rIn)}px)`;
	} else if (kind === 'split') {
		const half = (pOut > 0 ? 1 - pOut : pIn) * (50 + fp);
		// the soft edge grows with the opening, so nothing shows at 0
		const fe = Math.min(fp, half);
		const e0 = 50 - half + fe;
		const e1 = 50 + half - fe;
		mask = `linear-gradient(${deg}deg, transparent ${e0 - fe}%, #000 ${e0}%, #000 ${e1}%, transparent ${e1 + fe}%)`;
	} else if (kind === 'blinds') {
		const slat = L / Math.max(1, slats);
		const open = (pOut > 0 ? 1 - pOut : pIn) * (slat + f);
		mask = `repeating-linear-gradient(${deg}deg, #000 0px, #000 ${Math.max(0, open - f)}px, transparent ${Math.max(0.01, open)}px, transparent ${slat}px)`;
	} else if (pOut > 0) {
		const x = -fp + pOut * (100 + fp);
		mask = `linear-gradient(${deg}deg, transparent ${x}%, #000 ${x + fp}%)`;
	} else {
		const e = -fp + pIn * (100 + fp);
		mask = `linear-gradient(${deg}deg, #000 ${e}%, transparent ${e + fp}%)`;
	}
	return (
		<AbsoluteFill style={{WebkitMaskImage: mask, maskImage: mask, ...style}}>
			{children}
		</AbsoluteFill>
	);
};
