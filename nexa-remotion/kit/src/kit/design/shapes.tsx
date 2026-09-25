// Decorative shapes, used with taste: one organic blob behind a subject, a ring that draws on, a sparkle on a
// payoff, a hand-drawn squiggle under a word. Never as wallpaper: one or two per frame, each with a job.
import {noise3D} from '@remotion/noise';
import {makeSpark} from '@remotion/shapes';
import React, {useId} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp, springAt, wiggle} from '../motion';
import {mix} from './color';

// ---------------------------------------------------------------- blob

export type BlobPathOptions = {
	width: number; // the box the blob fills, px
	height?: number; // default = width (a round blob); otherwise it is stretched to the box
	points?: number; // lobes around the edge (default 7; 5 is bolder, 9 is calmer)
	wobble?: number; // 0 to 0.4: how far the edge moves in and out (default 0.16)
	seed?: string;
	time?: number; // move this to morph (seconds times a speed)
};

/**
 * A closed, smooth organic path filling a box: points on a circle pushed in and out by seeded 3D noise, joined with
 * Catmull-Rom curves. Use it as an SVG path or as `clipPath: path('...')` for a blob-shaped picture.
 */
export const blobPath = ({width, height, points = 7, wobble = 0.16, seed = 'blob', time = 0}: BlobPathOptions): string => {
	const h = height ?? width;
	const n = Math.max(3, Math.round(points));
	const w = clamp(wobble, 0, 0.45);
	const pts: [number, number][] = [];
	for (let i = 0; i < n; i++) {
		const a = (i / n) * Math.PI * 2 - Math.PI / 2;
		const k = 1 + w * noise3D(seed, Math.cos(a) * 0.85, Math.sin(a) * 0.85, time);
		// divide by the largest possible radius so the blob always stays inside its box
		const rr = k / (1 + w);
		pts.push([width / 2 + (Math.cos(a) * rr * width) / 2, h / 2 + (Math.sin(a) * rr * h) / 2]);
	}
	const f = (v: number) => v.toFixed(2);
	let d = `M ${f(pts[0][0])} ${f(pts[0][1])}`;
	for (let i = 0; i < n; i++) {
		const p0 = pts[(i - 1 + n) % n];
		const p1 = pts[i];
		const p2 = pts[(i + 1) % n];
		const p3 = pts[(i + 2) % n];
		const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
		const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
		d += ` C ${f(c1[0])} ${f(c1[1])} ${f(c2[0])} ${f(c2[1])} ${f(p2[0])} ${f(p2[1])}`;
	}
	return `${d} Z`;
};

export type BlobProps = {
	size?: number; // px at 1080 (default 520)
	height?: number; // px at 1080 (default = size)
	color?: string; // default: the accent softened into the ground
	gradient?: [string, string]; // a two-colour fill, top-left to bottom-right
	outline?: number; // draw only the edge, this many px wide at 1080
	points?: number; // lobes (default 7)
	wobble?: number; // 0 to 0.45 (default 0.16)
	seed?: string;
	speed?: number; // how fast it morphs (default 0.25; 0 = still)
	delay?: number; // frames before it grows in (default 0)
	grow?: number; // frames to grow in (default the theme's entrance; 0 = already there)
	opacity?: number;
	style?: React.CSSProperties; // position it here (left, top, or inside a flex parent)
	children?: React.ReactNode; // shown centred on the blob
};

/** An organic shape behind a subject (a cut-out, an icon, a number) that breathes slowly. */
export const Blob: React.FC<BlobProps> = ({size = 520, height, color, gradient, outline, points, wobble, seed = 'blob', speed = 0.25, delay = 0, grow, opacity = 1, style, children}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const w = size * unit;
	const h = (height ?? size) * unit;
	const pad = outline ? outline * unit : 0;
	const d = blobPath({width: w, height: h, points, wobble, seed, time: (frame / fps) * speed * 0.35});
	const g = grow ?? at30(t.motion.enterFrames + 6, fps);
	const s = g > 0 ? ramp(frame, delay, g, curves.outBack) : 1;
	const fill = color ?? mix(t.colors.bg, t.colors.accent, t.dark ? 0.45 : 0.3);
	const gid = `blob-${useId().replace(/:/g, '')}`;
	return (
		<div style={{position: 'relative', width: w, height: h, flex: 'none', opacity, ...style}}>
			<svg width={w} height={h} viewBox={`${-pad} ${-pad} ${w + 2 * pad} ${h + 2 * pad}`} style={{position: 'absolute', inset: 0, overflow: 'visible', scale: String(s)}}>
				{gradient ? (
					<defs>
						<linearGradient id={gid} x1="0" y1="0" x2="1" y2="1">
							<stop offset="0%" stopColor={gradient[0]} />
							<stop offset="100%" stopColor={gradient[1]} />
						</linearGradient>
					</defs>
				) : null}
				<path d={d} fill={outline ? 'none' : gradient ? `url(#${gid})` : fill} stroke={outline ? (color ?? t.colors.accent) : 'none'} strokeWidth={pad} strokeLinejoin="round" />
			</svg>
			{children ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{children}</div> : null}
		</div>
	);
};

export type BlobMaskProps = {
	width?: number; // px at 1080 (default 560)
	height?: number; // px at 1080 (default 640)
	points?: number; // lobes (default 7)
	wobble?: number; // 0 to 0.45 (default 0.12: a picture needs a calmer edge)
	seed?: string;
	speed?: number; // default 0.2
	style?: React.CSSProperties;
	children?: React.ReactNode; // a picture, sized 100% with objectFit cover
};

/** Clips its children (a photo, a video) to a slowly moving blob: an organic picture frame. */
export const BlobMask: React.FC<BlobMaskProps> = ({width = 560, height = 640, points = 7, wobble = 0.12, seed = 'mask', speed = 0.2, style, children}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const w = width * unit;
	const h = height * unit;
	const d = blobPath({width: w, height: h, points, wobble, seed, time: (frame / fps) * speed * 0.35});
	return <div style={{position: 'relative', width: w, height: h, overflow: 'hidden', clipPath: `path('${d}')`, flex: 'none', ...style}}>{children}</div>;
};

// ---------------------------------------------------------------- ring

export type RingProps = {
	size?: number; // diameter px at 1080 (default 360)
	weight?: number; // px at 1080 (default 6)
	color?: string; // default the accent
	progress?: number; // 0 to 1: how much is drawn (default: drawn on over `duration` from `delay`)
	delay?: number;
	duration?: number; // default 30 at 30 fps
	start?: number; // degrees where the stroke starts (default -90: twelve o'clock)
	dashed?: boolean; // a dotted ring (round dots)
	style?: React.CSSProperties;
	children?: React.ReactNode; // centred inside
};

/** A thin circle that draws itself around something: a number, an icon, a face. */
export const Ring: React.FC<RingProps> = ({size = 360, weight = 6, color, progress, delay = 0, duration, start = -90, dashed = false, style, children}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const id = useId().replace(/:/g, '');
	const s = size * unit;
	const w = weight * unit;
	const p = progress !== undefined ? clamp(progress, 0, 1) : ramp(frame, delay, duration ?? at30(30, fps), curves.inOut);
	const r = (s - w) / 2;
	const circ = 2 * Math.PI * r;
	const ink = color ?? t.colors.accent;
	const turn = `rotate(${start} ${s / 2} ${s / 2})`;
	const drawn = {pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - p};
	// a dotted ring is revealed through a mask that draws on, so its dots stay round and evenly spaced
	const dots = Math.max(8, Math.round(circ / (w * 3.4)));
	return (
		<div style={{position: 'relative', width: s, height: s, flex: 'none', ...style}}>
			<svg width={s} height={s} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				{dashed ? (
					<>
						<defs>
							<mask id={`ring-${id}`} maskUnits="userSpaceOnUse" x={-w} y={-w} width={s + 2 * w} height={s + 2 * w}>
								<circle cx={s / 2} cy={s / 2} r={r} fill="none" stroke="#FFFFFF" strokeWidth={w * 2.4} transform={turn} {...drawn} />
							</mask>
						</defs>
						<circle cx={s / 2} cy={s / 2} r={r} fill="none" stroke={ink} strokeWidth={w} strokeLinecap="round" strokeDasharray={`0 ${circ / dots}`} transform={turn} mask={`url(#ring-${id})`} />
					</>
				) : (
					<circle cx={s / 2} cy={s / 2} r={r} fill="none" stroke={ink} strokeWidth={w} strokeLinecap="round" transform={turn} {...drawn} />
				)}
			</svg>
			{children ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{children}</div> : null}
		</div>
	);
};

// ---------------------------------------------------------------- sparkle

export type SparkleProps = {
	size?: number; // px at 1080 (default 64)
	color?: string; // default the theme's highlight on dark themes, the accent on light ones
	delay?: number; // frame it pops in
	rotate?: number; // degrees (default 0)
	twinkle?: boolean; // a slow, small shimmer after it lands (default false)
	style?: React.CSSProperties;
};

/** A four-point sparkle that pops in with a little overshoot: for a payoff moment, not for decoration. */
export const Sparkle: React.FC<SparkleProps> = ({size = 64, color, delay = 0, rotate = 0, twinkle = false, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const s = size * unit;
	const spark = makeSpark({width: s, height: s * 1.18, edgeRoundness: 1.6});
	const pop = springAt(frame, fps, {delay, config: 'pop'});
	const shimmer = twinkle ? 1 + 0.08 * wiggle(frame, fps, 0.6, 5, 'sparkle') * ramp(frame, delay + 10, 20) : 1;
	return (
		<svg width={spark.width} height={spark.height} style={{overflow: 'visible', flex: 'none', scale: String(Math.max(0, pop) * shimmer), rotate: `${rotate + (1 - Math.min(1, pop)) * -40}deg`, ...style}}>
			<path d={spark.path} fill={color ?? (t.dark ? t.colors.highlight : t.colors.accent)} />
		</svg>
	);
};

// ---------------------------------------------------------------- squiggle

export type SquiggleProps = {
	width?: number; // px at 1080 (default 420)
	amplitude?: number; // px at 1080 (default 12)
	waves?: number; // number of waves across (default 5)
	weight?: number; // px at 1080 (default 7)
	color?: string; // default the accent
	delay?: number;
	duration?: number; // draw-on frames (default 18 at 30 fps)
	seed?: string;
	style?: React.CSSProperties;
};

/** A hand-drawn wavy stroke that draws itself: under a word, beside a number. */
export const Squiggle: React.FC<SquiggleProps> = ({width = 420, amplitude = 12, waves = 5, weight = 7, color, delay = 0, duration, seed = 'squiggle', style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const w = width * unit;
	const a = amplitude * unit;
	const sw = weight * unit;
	const p = ramp(frame, delay, duration ?? at30(18, fps), curves.outCubic);
	const steps = Math.max(24, Math.round(waves * 16));
	let d = '';
	for (let i = 0; i <= steps; i++) {
		const u = i / steps;
		// a hand wobbles: amplitude and baseline drift a little along the stroke (seeded, still over time)
		const amp = a * (0.85 + 0.3 * noise3D(seed, u * 3, 0, 0));
		const y = a + sw / 2 + Math.sin(u * waves * Math.PI * 2) * amp + noise3D(seed, u * 2, 5, 0) * a * 0.25;
		d += `${i === 0 ? 'M' : 'L'} ${(u * w).toFixed(2)} ${y.toFixed(2)} `;
	}
	const h = 2 * a + sw + a * 0.6;
	return (
		<svg width={w} height={h} style={{overflow: 'visible', flex: 'none', ...style}}>
			<path d={d} fill="none" stroke={color ?? t.colors.accent} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
		</svg>
	);
};
