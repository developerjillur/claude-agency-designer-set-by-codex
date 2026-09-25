// Hand-drawn marks made with perfect-freehand: a scribbled circle, underlines, a strike, a check, a cross, an arrow,
// a box, a marker highlight and a scribble. The pen draws them on at a steady speed with a tapered start, a seeded
// wobble, and a short lift between strokes. <HandMark> is a sized block, <Marked> wraps words and draws around
// them, <HandStroke> draws any point list inside an <svg>.
import {noise2D} from '@remotion/noise';
import {getStroke} from 'perfect-freehand';
import React, {useMemo, useRef} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {withOpacity} from './color';
import {useDrawProgress, type DrawTiming} from './Draw';
import {useMeasuredSize} from './measure';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type HandKind =
	| 'circle'
	| 'underline'
	| 'double-underline'
	| 'strike'
	| 'check'
	| 'cross'
	| 'arrow'
	| 'box'
	| 'highlight'
	| 'scribble';

type P = [number, number];

// ---------------------------------------------------------------- geometry

const sampleCurve = (fn: (s: number) => P, step = 3): P[] => {
	// sample finely, then keep points about `step` apart along the curve (even pen speed)
	const fine: P[] = [];
	const n = 400;
	for (let i = 0; i <= n; i++) {
		fine.push(fn(i / n));
	}
	const out: P[] = [fine[0]];
	let acc = 0;
	for (let i = 1; i < fine.length; i++) {
		acc += Math.hypot(fine[i][0] - fine[i - 1][0], fine[i][1] - fine[i - 1][1]);
		if (acc >= step) {
			out.push(fine[i]);
			acc = 0;
		}
	}
	const last = fine[fine.length - 1];
	if (out[out.length - 1] !== last) {
		out.push(last);
	}
	return out;
};

const quad = (a: P, c: P, b: P) => (s: number): P => [
	(1 - s) * (1 - s) * a[0] + 2 * (1 - s) * s * c[0] + s * s * b[0],
	(1 - s) * (1 - s) * a[1] + 2 * (1 - s) * s * c[1] + s * s * b[1],
];

const line = (a: P, b: P, bow = 0) => {
	const mx = (a[0] + b[0]) / 2;
	const my = (a[1] + b[1]) / 2;
	const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
	const nx = (b[1] - a[1]) / len;
	const ny = -(b[0] - a[0]) / len;
	return quad(a, [mx + nx * bow * len, my + ny * bow * len], b);
};

const wobble = (pts: P[], amp: number, seed: number, lane: number): P[] => {
	if (amp <= 0 || pts.length < 3) {
		return pts;
	}
	let acc = 0;
	return pts.map((p, i) => {
		const a = pts[Math.max(0, i - 1)];
		const b = pts[Math.min(pts.length - 1, i + 1)];
		if (i > 0) {
			acc += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]);
		}
		const dx = b[0] - a[0];
		const dy = b[1] - a[1];
		const l = Math.hypot(dx, dy) || 1;
		// ends move less than the middle: a pen starts and lands on purpose
		const env = Math.sin(Math.PI * Math.min(1, Math.max(0, i / (pts.length - 1)))) * 0.7 + 0.3;
		const o = noise2D('kit-hand', acc / 90, seed * 3.7 + lane * 11.3) * amp * env;
		return [p[0] + (-dy / l) * o, p[1] + (dx / l) * o];
	});
};

const DIR: Record<'right' | 'left' | 'up' | 'down', (p: P, w: number, h: number) => P> = {
	right: (p) => p,
	left: (p, w) => [w - p[0], p[1]],
	up: (p, w, h) => [p[1] * (w / h), h - p[0] * (h / w)],
	down: (p, w, h) => [w - p[1] * (w / h), p[0] * (h / w)],
};

/** The ideal strokes of a mark in a w x h box (design px), before wobble. */
export const handStrokes = (kind: HandKind, w: number, h: number, seed = 1, direction: keyof typeof DIR = 'right'): P[][] => {
	// -1..1, stable per seed (offsets keep the samples off the noise lattice, where it is always 0)
	const r = (k: number) => noise2D('kit-hand-shape', seed * 1.93 + 0.37, k * 5.1 + 0.61);
	switch (kind) {
		case 'circle': {
			const cx = w / 2;
			const cy = h / 2;
			const start = (-160 + r(1) * 12) * (Math.PI / 180);
			const sweep = (2 + 0.13 + r(2) * 0.04) * Math.PI;
			const tilt = (r(3) * 3 - 2) * (Math.PI / 180);
			const fn = (s: number): P => {
				const a = start + sweep * s;
				// a slight spiral: the pen starts inside and ends outside, so the ends cross instead of meeting
				const k = 0.965 + 0.07 * s;
				const x = Math.cos(a) * (w / 2) * k;
				const y = Math.sin(a) * (h / 2) * k;
				return [cx + x * Math.cos(tilt) - y * Math.sin(tilt), cy + x * Math.sin(tilt) + y * Math.cos(tilt)];
			};
			return [sampleCurve(fn)];
		}
		case 'underline':
		case 'double-underline': {
			const y = h * 0.42;
			const first = sampleCurve(line([w * 0.01, y + h * 0.1 * r(4)], [w * 0.99, y - h * 0.16], 0.02 + 0.015 * r(5)));
			if (kind === 'underline') {
				return [first];
			}
			const y2 = h * 0.82;
			return [first, sampleCurve(line([w * 0.07, y2], [w * 0.9, y2 - h * 0.1 + h * 0.06 * r(6)], 0.015))];
		}
		case 'strike':
			return [sampleCurve(line([-w * 0.02, h * 0.56], [w * 1.02, h * 0.44 + h * 0.06 * r(7)], 0.01))];
		case 'check': {
			const a: P = [w * 0.04, h * 0.56];
			const b: P = [w * 0.36, h * 0.94];
			const c: P = [w * 0.97, h * 0.04];
			const leg1 = sampleCurve(line(a, b, -0.06));
			const leg2 = sampleCurve(line(b, c, 0.05));
			return [[...leg1, ...leg2.slice(1)]];
		}
		case 'cross':
			return [
				sampleCurve(line([w * 0.08, h * 0.08], [w * 0.92, h * 0.92], 0.03 * r(8))),
				sampleCurve(line([w * 0.9, h * 0.1], [w * 0.1, h * 0.9], 0.04 * r(9))),
			];
		case 'arrow': {
			const map = (p: P) => DIR[direction](p, w, h);
			const tip: P = [w * 0.97, h * 0.34];
			const shaft = sampleCurve(quad([w * 0.02, h * 0.8], [w * 0.5, h * 0.02], tip)).map(map);
			// head: two short strokes back from the tip around the final direction
			const ang = Math.atan2(tip[1] - h * 0.02, tip[0] - w * 0.5);
			const hl = Math.min(w, h) * 0.3 + 10;
			const wing = (sgn: number): P => [tip[0] - Math.cos(ang + sgn * 0.5) * hl, tip[1] - Math.sin(ang + sgn * 0.5) * hl];
			return [shaft, sampleCurve(line(wing(1), tip, 0.02)).map(map), sampleCurve(line(tip, wing(-1), 0.02)).map(map)];
		}
		case 'box': {
			const o = Math.min(w, h) * 0.04;
			const pts: P[] = [
				[-o, o * 0.5],
				[w + o * 0.6, -o * 0.3],
				[w - o * 0.2, h + o * 0.4],
				[o * 0.3, h - o * 0.2],
				[o * 0.8, -o * 1.2],
			];
			const out: P[] = [];
			for (let i = 0; i < pts.length - 1; i++) {
				const seg = sampleCurve(line(pts[i], pts[i + 1], 0.012 * (i % 2 ? 1 : -1)));
				out.push(...(i === 0 ? seg : seg.slice(1)));
			}
			return [out];
		}
		case 'highlight':
			return [sampleCurve(line([0, h * 0.54], [w, h * 0.46 + h * 0.05 * r(10)], 0.004))];
		case 'scribble': {
			const zigs = Math.max(4, Math.round(w / Math.max(14, h * 0.22)));
			const pts: P[] = [];
			for (let i = 0; i <= zigs; i++) {
				const x = (i / zigs) * w;
				pts.push([x + r(20 + i) * w * 0.02, i % 2 === 0 ? h * (0.12 + 0.06 * r(40 + i)) : h * (0.88 + 0.06 * r(60 + i))]);
			}
			const out: P[] = [];
			for (let i = 0; i < pts.length - 1; i++) {
				const seg = sampleCurve(line(pts[i], pts[i + 1], 0.05 * (i % 2 ? 1 : -1)));
				out.push(...(i === 0 ? seg : seg.slice(1)));
			}
			return [out];
		}
		default:
			return [];
	}
};

// ---------------------------------------------------------------- stroke rendering

const cumulative = (pts: P[]): number[] => {
	const out = [0];
	for (let i = 1; i < pts.length; i++) {
		out.push(out[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
	}
	return out;
};

/** The first `len` of a sampled stroke, with an interpolated last point so the tip moves smoothly. */
const cutPoints = (pts: P[], cum: number[], len: number): P[] => {
	const out: P[] = [];
	for (let i = 0; i < pts.length; i++) {
		if (cum[i] <= len) {
			out.push(pts[i]);
		} else {
			const a = pts[i - 1];
			const span = cum[i] - cum[i - 1] || 1;
			const k = (len - cum[i - 1]) / span;
			out.push([a[0] + (pts[i][0] - a[0]) * k, a[1] + (pts[i][1] - a[1]) * k]);
			break;
		}
	}
	return out;
};

const outlinePath = (o: number[][]): string => {
	if (o.length < 3) {
		return '';
	}
	const g = (v: number) => v.toFixed(2);
	let d = `M${g(o[0][0])} ${g(o[0][1])}`;
	for (let i = 1; i < o.length; i++) {
		const a = o[i];
		const b = o[(i + 1) % o.length];
		d += `Q${g(a[0])} ${g(a[1])} ${g((a[0] + b[0]) / 2)} ${g((a[1] + b[1]) / 2)}`;
	}
	return d + 'Z';
};

export type PenStyle = {
	size?: number; // stroke width in the SVG's units
	thinning?: number; // how much pressure changes the width (0 even, 0.6 inky)
	taper?: number; // taper length at the start and the tip, as a multiple of size (default 1.4)
	flat?: boolean; // flat ends (a marker) instead of round ones
};

const penPressure = (s: number, seed: number, lane: number): number => {
	const land = Math.min(1, s / 0.1);
	const lift = Math.min(1, (1 - s) / 0.12);
	return 0.34 + 0.26 * land * (0.75 + 0.25 * lift) + 0.08 * noise2D('kit-hand-p', s * 3, seed + lane * 2.1);
};

/**
 * SVG path data of strokes drawn up to progress p: strokes are drawn one after another at an even pen speed, with a
 * short lift between them.
 */
export const penPaths = (strokes: P[][], p: number, style: PenStyle = {}, seed = 1): string[] => {
	const size = style.size ?? 8;
	const cums = strokes.map(cumulative);
	const lens = cums.map((c) => c[c.length - 1] ?? 0);
	const total = lens.reduce((a, b) => a + b, 0);
	const lift = strokes.length > 1 ? total * 0.06 : 0;
	const along = Math.min(1, Math.max(0, p)) * (total + lift * (strokes.length - 1));
	const out: string[] = [];
	let startAt = 0;
	strokes.forEach((pts, i) => {
		const drawn = Math.min(lens[i], along - startAt);
		startAt += lens[i] + lift;
		if (drawn < 0.5 || pts.length < 2) {
			return;
		}
		const done = drawn >= lens[i] - 0.01;
		const part = done ? pts : cutPoints(pts, cums[i], drawn);
		const withP = part.map((q, k) => [q[0], q[1], penPressure(cums[i][Math.min(k, cums[i].length - 1)] / (lens[i] || 1), seed, i)]);
		const taper = (style.taper ?? 1.4) * size;
		const outline = getStroke(withP, {
			size,
			thinning: style.thinning ?? 0.45,
			smoothing: 0.6,
			streamline: 0.25,
			simulatePressure: false,
			start: {taper: style.flat ? 0 : taper, cap: !style.flat},
			end: {taper: style.flat ? 0 : taper * 0.8, cap: !style.flat},
			last: done,
		});
		out.push(outlinePath(outline));
	});
	return out;
};

// ---------------------------------------------------------------- components

export type HandStrokeProps = DrawTiming &
	PenStyle & {
		points: [number, number][]; // one stroke, in the SVG's units
		color?: string;
		rough?: number; // extra wobble in the SVG's units (default 0: the points as given)
		seed?: number;
		opacity?: number;
	};

/** Any stroke you have points for (a signature, a route sketch), drawn on with a pen inside an <svg>. */
export const HandStroke: React.FC<HandStrokeProps> = ({points, color, rough = 0, seed = 1, opacity = 1, size = 8, thinning, taper, flat, ...timing}) => {
	const t = useTheme();
	const p = useDrawProgress({...timing, ease: timing.ease ?? curves.inOut});
	const pts = useMemo(() => {
		const dense: P[] = [];
		for (let i = 0; i < points.length - 1; i++) {
			const a = points[i];
			const b = points[i + 1];
			const seg = sampleCurve((s) => [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s]);
			dense.push(...(i === 0 ? seg : seg.slice(1)));
		}
		return wobble(dense.length ? dense : (points as P[]), rough, seed, 0);
	}, [points, rough, seed]);
	const ds = penPaths([pts], p, {size, thinning, taper, flat}, seed);
	return (
		<g opacity={opacity}>
			{ds.map((d, i) => (
				<path key={i} d={d} fill={color ?? t.colors.text} />
			))}
		</g>
	);
};

const DEFAULT_SIZE: Record<HandKind, number> = {
	circle: 7,
	underline: 8,
	'double-underline': 7,
	strike: 8,
	check: 11,
	cross: 10,
	arrow: 8,
	box: 6,
	highlight: 0, // the mark's height
	scribble: 6,
};

export type HandMarkProps = DrawTiming &
	GraphicExitProps & {
		kind: HandKind;
		width?: number; // px at 1080 (default 320)
		height?: number; // px at 1080 (default: 200 for circles and boxes, 40 for lines)
		color?: string; // default: the theme's second accent (a marker colour); highlights use the highlight colour
		size?: number; // pen width in px at 1080
		rough?: number; // wobble amount (default 1; 0 is a steady hand)
		seed?: number; // a different seed draws a different hand-made variation
		boil?: number; // after it is drawn, redraw a new variation every n frames (3 to 5 gives a cartoon boil)
		direction?: 'right' | 'left' | 'up' | 'down'; // for arrows
		opacity?: number;
		style?: React.CSSProperties; // on the <svg> (position it here)
	};

/** A hand-drawn mark in a box of its own, sized in px at 1080. */
export const HandMark: React.FC<HandMarkProps> = ({
	kind,
	width = 320,
	height,
	color,
	size,
	rough = 1,
	seed = 1,
	boil = 0,
	direction = 'right',
	opacity = 1,
	style,
	exit = 'none',
	outDuration,
	outAt,
	...timing
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const h = height ?? (kind === 'circle' || kind === 'box' || kind === 'check' || kind === 'cross' || kind === 'scribble' ? 200 : kind === 'arrow' ? 160 : 40);
	const p = useDrawProgress({...timing, duration: timing.duration ?? at30(kind === 'circle' || kind === 'box' ? 24 : 16, fps), ease: timing.ease ?? curves.inOut});
	const q = useGraphicExit({exit, outDuration, outAt});
	const s = boil > 0 && p >= 1 ? seed + 1 + Math.floor(frame / boil) : seed;
	const pen = size ?? (kind === 'highlight' ? h * 0.8 : DEFAULT_SIZE[kind]);
	const strokes = useMemo(() => {
		const amp = kind === 'highlight' ? rough * 1.2 : rough * Math.min(5, 1.2 + 0.008 * Math.max(width, h));
		return handStrokes(kind, width, h, s, direction).map((st, i) => wobble(st, amp, s, i));
	}, [kind, width, h, s, direction, rough]);
	const shown = exit === 'undraw' ? p * (1 - q) : p;
	const ds = penPaths(strokes, shown, {size: pen, flat: kind === 'highlight', thinning: kind === 'highlight' ? 0.1 : undefined}, s);
	const fill = color ?? (kind === 'highlight' ? withOpacity(t.colors.highlight, 0.8) : t.colors.accent2);
	return (
		<svg
			viewBox={`0 0 ${width} ${h}`}
			width={width * unit}
			height={h * unit}
			style={{display: 'block', overflow: 'visible', opacity: opacity * (exit === 'fade' ? 1 - q : 1), ...style}}
		>
			{ds.map((d, i) => (
				<path key={i} d={d} fill={fill} />
			))}
		</svg>
	);
};

export type MarkedProps = Omit<HandMarkProps, 'width' | 'height' | 'style' | 'kind' | 'direction'> & {
	kind?: Exclude<HandKind, 'arrow' | 'check'>;
	pad?: number; // px at 1080 around the words (circles and boxes)
	children: React.ReactNode;
	style?: React.CSSProperties; // on the wrapper span
};

/**
 * Words with a hand-drawn mark around, under, through or behind them: `<Marked kind="circle">42%</Marked>`.
 * The words are measured after the fonts load. Keep it to a short phrase on one line (the box does not wrap).
 */
export const Marked: React.FC<MarkedProps> = ({kind = 'underline', pad, children, style, ...mark}) => {
	const ref = useRef<HTMLSpanElement>(null);
	const box = useMeasuredSize(ref, 'graphics: measuring a marked phrase');
	const {unit} = useStage();
	const w = box ? box.w / unit : 0;
	const h = box ? box.h / unit : 0;
	let layout: {x: number; y: number; w: number; h: number} | null = null;
	if (box && w > 0 && h > 0) {
		const pd = pad ?? (kind === 'circle' ? Math.max(14, h * 0.28) : 8);
		switch (kind) {
			case 'circle':
				layout = {x: -pd * 1.4, y: -pd, w: w + pd * 2.8, h: h + pd * 2};
				break;
			case 'box':
			case 'cross':
			case 'scribble':
				layout = {x: -pd, y: -pd * 0.6, w: w + pd * 2, h: h + pd * 1.2};
				break;
			case 'underline':
				layout = {x: -4, y: h * 0.86, w: w + 8, h: Math.max(18, h * 0.22)};
				break;
			case 'double-underline':
				layout = {x: -4, y: h * 0.84, w: w + 8, h: Math.max(26, h * 0.34)};
				break;
			case 'strike':
				layout = {x: -4, y: h * 0.38, w: w + 8, h: Math.max(14, h * 0.24)};
				break;
			case 'highlight':
				layout = {x: -8, y: h * 0.14, w: w + 16, h: h * 0.8};
				break;
			default:
				layout = null;
		}
	}
	return (
		<span ref={ref} style={{position: 'relative', display: 'inline-block', whiteSpace: 'nowrap', isolation: 'isolate', ...style}}>
			{layout ? (
				<HandMark
					kind={kind}
					width={layout.w}
					height={layout.h}
					{...mark}
					style={{position: 'absolute', left: layout.x * unit, top: layout.y * unit, zIndex: kind === 'highlight' ? -1 : 1, pointerEvents: 'none'}}
				/>
			) : null}
			{children}
		</span>
	);
};
