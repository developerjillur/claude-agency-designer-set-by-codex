// Textures and light over a scene: vignette, paper (the @remotion/effects paper shader on a <Solid>, with a CSS
// fallback), a spotlight that dims everything but one place, and a specular sweep across a card or a title.
import {paper} from '@remotion/effects/paper';
import React from 'react';
import {AbsoluteFill, Solid, useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {darken, lighten, mix, withAlpha} from './color';
import {Grain, useGrainUrl} from './grain';

let gl2: boolean | undefined;

/**
 * Whether this browser can run the WebGL2 effects (@remotion/effects). Renders need `--gl=angle` (nrk passes it);
 * without it the effects throw and fail the render, so the kit's effect grounds fall back to CSS instead.
 */
export const hasWebGL2 = (): boolean => {
	if (gl2 !== undefined) {
		return gl2;
	}
	if (typeof document === 'undefined') {
		gl2 = false;
		return gl2;
	}
	try {
		const ctx = document.createElement('canvas').getContext('webgl2');
		gl2 = Boolean(ctx);
		// give the context back at once: Chrome keeps only about 16 alive
		ctx?.getExtension('WEBGL_lose_context')?.loseContext();
	} catch {
		gl2 = false;
	}
	return gl2;
};

// ---------------------------------------------------------------- vignette

export type VignetteProps = {
	amount?: number; // 0 to 1; default the theme's texture.vignette. Corners get half of it as darkness: weak
	color?: string; // default black on dark themes, the ground darkened (same hue) on light ones
	center?: [number, number]; // 0 to 1 of the frame; slightly above the middle by default, like a lens
	size?: number; // 1 = the clear middle reaches about 45% of the way to the corners; bigger is gentler
	style?: React.CSSProperties;
};

/** Darkened corners that hold the eye in the frame. Keep it weak: a visible vignette reads as a filter. */
export const Vignette: React.FC<VignetteProps> = ({amount, color, center = [0.5, 0.46], size = 1, style}) => {
	const t = useTheme();
	const a = clamp(amount ?? t.texture.vignette, 0, 1);
	if (a <= 0) {
		return null;
	}
	const c = color ?? (t.dark ? '#000000' : darken(t.colors.bg, 0.5));
	const corner = 0.5 * a;
	const inner = clamp(0.45 * size, 0.05, 0.95);
	// eased stops: a linear ramp shows its start as a ring
	const stops = [0, 0.15, 0.35, 0.55, 0.75, 1].map((k) => {
		const pos = inner + (1 - inner) * k;
		const alpha = corner * k * k * (3 - 2 * k);
		return `${withAlpha(c, alpha)} ${(pos * 100).toFixed(1)}%`;
	});
	return (
		<AbsoluteFill
			style={{
				pointerEvents: 'none',
				background: `radial-gradient(ellipse farthest-corner at ${center[0] * 100}% ${center[1] * 100}%, ${withAlpha(c, 0)} 0%, ${stops.join(', ')})`,
				...style,
			}}
		/>
	);
};

// ---------------------------------------------------------------- paper

export type PaperProps = {
	color?: string; // the sheet (default: the theme's ground on light themes, its surface on dark ones)
	amount?: number; // texture strength 0 to 1 (default 0.5)
	fibers?: number; // 0 to 1 (default 0.2); 0.4 and up reads as craft paper
	crumples?: number; // 0 to 1 (default 0.1)
	folds?: number; // 0 to 1 (default 0.05); above 0.3 it reads as a crumpled sheet
	roughness?: number; // fine tooth 0 to 1 (default 0.22)
	scale?: number; // size of the fibres and crumples, 0.1 to 4 (default 0.8)
	seed?: number; // 0 to 1000
	boil?: number; // re-seed every N frames for a stop-motion feel (default 0: still, cheap to encode)
	grid?: number | false; // a square grid, cell size px at 1080 (the Vox look uses about 106)
	rules?: number | false; // ruled notebook lines, spacing px at 1080
	margin?: string | false; // a notebook margin line in this colour (with rules)
	lineColor?: string; // grid and rule colour (default: the text colour at 8%)
	lineWeight?: number; // px at 1080 (default 1.7)
	engine?: 'auto' | 'webgl' | 'css'; // auto: the paper shader when WebGL2 is there, else the CSS paper
	grain?: number; // printed grain on the sheet, still (default: the theme's grain, at least 0.06)
	light?: number; // the soft falloff of a lit sheet, 0 to 1 (default 1)
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

const paperLines = (
	width: number,
	height: number,
	unit: number,
	color: string,
	weight: number,
	grid: number | false,
	rules: number | false,
): React.CSSProperties | null => {
	const line = Math.max(1, weight * unit);
	const soft = Math.max(0.6, 0.9 * unit);
	const stroke = (dir: string) =>
		`linear-gradient(${dir}, transparent 0px, ${color} ${soft}px, ${color} ${soft + line}px, transparent ${2 * soft + line}px, transparent 100%)`;
	if (grid) {
		const cell = Math.round(grid * unit);
		const ox = Math.round((width % cell) / 2);
		const oy = Math.round((height % cell) / 2);
		return {
			backgroundImage: [stroke('180deg'), stroke('90deg')].join(', '),
			backgroundSize: `${cell}px ${cell}px, ${cell}px ${cell}px`,
			backgroundPosition: `${ox}px ${oy}px, ${ox}px ${oy}px`,
		};
	}
	if (rules) {
		const gap = Math.round(rules * unit);
		return {
			backgroundImage: stroke('180deg'),
			backgroundSize: `100% ${gap}px`,
			backgroundPosition: `0px ${Math.round(gap * 0.6)}px`,
		};
	}
	return null;
};

// the CSS paper: two scales of soft mottling and a horizontal fibre streak, all from the grain tile
const CssPaper: React.FC<{amount: number; fibers: number}> = ({amount, fibers}) => {
	const {unit} = useStage();
	const mottle = useGrainUrl('grey');
	return (
		<>
			<AbsoluteFill
				style={{
					backgroundImage: `${mottle}, ${mottle}`,
					backgroundSize: `${Math.round(256 * 26 * unit)}px, ${Math.round(256 * 11 * unit)}px`,
					backgroundPosition: '13% 31%, 61% 7%',
					mixBlendMode: 'soft-light',
					opacity: 0.45 * amount,
				}}
			/>
			<AbsoluteFill
				style={{
					backgroundImage: mottle,
					backgroundSize: `${Math.round(256 * 9 * unit)}px ${Math.round(256 * 0.8 * unit)}px`,
					mixBlendMode: 'soft-light',
					opacity: 0.4 * amount * clamp(fibers / 0.2, 0, 2),
				}}
			/>
		</>
	);
};

/**
 * A sheet of paper as the ground: fibres, tooth and faint crumples from the paper shader, an optional grid or ruled
 * lines, a still printed grain and the soft falloff of a lit sheet. Static by default (one shader pass per tab).
 */
export const Paper: React.FC<PaperProps> = ({
	color,
	amount = 0.5,
	fibers = 0.2,
	crumples = 0.1,
	folds = 0.05,
	roughness = 0.22,
	scale = 0.8,
	seed = 6,
	boil = 0,
	grid = false,
	rules = false,
	margin = false,
	lineColor,
	lineWeight = 1.7,
	engine = 'auto',
	grain,
	light = 1,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, unit} = useStage();
	const base = color ?? (t.dark ? t.colors.surface : t.colors.bg);
	const a = clamp(amount, 0, 1);
	const useGl = engine === 'webgl' || (engine === 'auto' && hasWebGL2());
	const s = boil > 0 ? Math.floor(frame / boil) : 0;
	const seedNow = (Math.abs(seed) + s * 37.3) % 1000;
	const lines = lineColor ?? withAlpha(t.colors.text, t.dark ? 0.1 : 0.08);
	const ruled = paperLines(width, height, unit, lines, lineWeight, grid, rules);
	const grainAmount = grain ?? Math.max(0.06, t.texture.grain);
	return (
		<AbsoluteFill style={{backgroundColor: base, overflow: 'hidden', ...style}}>
			{useGl ? (
				<Solid
					width={width}
					height={height}
					// the shader darkens the sheet by about a fifth where it is flat: lift the source to keep the colour
					color={lighten(base, 0.14 * a)}
					effects={[
						paper({
							amount: a,
							colorFront: mix('#FFFFFF', base, 0.55),
							colorBack: '#FFFFFF',
							contrast: 0.18,
							roughness: clamp(roughness, 0, 1),
							fiber: clamp(fibers, 0, 1),
							fiberSize: 0.25,
							crumples: clamp(crumples, 0, 1),
							crumpleSize: 0.4,
							folds: clamp(folds, 0, 1),
							foldCount: 4,
							drops: 0.04,
							seed: clamp(seedNow, 0, 1000),
							scale: clamp(scale, 0.01, 4),
						}),
					]}
					style={{position: 'absolute', left: 0, top: 0, display: 'block'}}
				/>
			) : (
				<CssPaper amount={a} fibers={fibers} />
			)}
			{ruled ? <AbsoluteFill style={ruled} /> : null}
			{rules && margin ? (
				<AbsoluteFill style={{left: Math.round(width * 0.09), width: Math.max(1, 2 * unit), background: withAlpha(margin, 0.55)}} />
			) : null}
			<Grain amount={grainAmount} rate={0} seed="paper" />
			{light > 0 ? (
				<AbsoluteFill
					style={{
						background: `radial-gradient(ellipse at 50% 42%, rgba(255, 255, 255, ${0.1 * light}) 0%, rgba(255, 255, 255, 0) 55%, ${withAlpha(darken(base, 0.45), 0.12 * light)} 100%)`,
					}}
				/>
			) : null}
			{children}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- spotlight

export type SpotRect = {x: number; y: number; w: number; h: number}; // px in the frame

export type SpotlightProps = {
	at?: [number, number]; // a round spot's centre, 0 to 1 of the frame (default a little above the middle)
	to?: [number, number]; // where the round spot travels to
	radius?: number; // round spot radius, px at 1080 (default 300)
	rect?: SpotRect; // a box instead of a round spot: the element to show (px in the frame)
	toRect?: SpotRect; // the box it moves and resizes to
	corner?: number; // the box's corner radius, px at 1080 (default the theme's radius)
	moveAt?: number; // frame the move starts (default 30)
	moveFrames?: number; // default: scaled to the distance
	feather?: number; // soft edge: a share of the radius, or px at 1080 for a box (default 0.6 / 40)
	dim?: number; // how strongly the rest is veiled, 0 to 1 (default 0.62)
	color?: string; // the veil (default the theme's ground: dark themes darken the rest, light themes fade it)
	glow?: number; // light added inside a round spot, 0 to 1 (default 0.18 on dark themes, 0 on light)
	delay?: number; // frames before it fades in
	fade?: number; // fade frames (default the theme's entrance)
	exit?: boolean; // fade out by the end of the Sequence (default true)
};

/**
 * Veils everything except one place, and can travel to a second one: points the eye without an arrow. The veil
 * is the ground's own colour, so on a light theme the rest fades back instead of turning grey.
 */
export const Spotlight: React.FC<SpotlightProps> = ({
	at = [0.5, 0.45],
	to,
	radius = 300,
	rect,
	toRect,
	corner,
	moveAt = 30,
	moveFrames,
	feather,
	dim = 0.62,
	color,
	glow,
	delay = 0,
	fade,
	exit = true,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, width, height, durationInFrames} = useStage();
	const f = fade ?? at30(t.motion.enterFrames, fps);
	const veil = color ?? t.colors.bg;
	const fin = ramp(frame, delay, f, curves.out);
	const fout = exit && Number.isFinite(durationInFrames) ? 1 - ramp(frame, durationInFrames - 1 - Math.round(f * 0.8), Math.round(f * 0.8), curves.in) : 1;
	const o = Math.min(fin, fout);
	const d = clamp(dim, 0, 1);
	if (rect) {
		const b = toRect ?? rect;
		const dist = Math.hypot(b.x - rect.x, b.y - rect.y) / unit;
		const mf = moveFrames ?? Math.max(12, Math.round(18 * Math.sqrt(Math.max(1, dist) / 300)));
		const m = toRect ? ramp(frame, moveAt, mf, curves.inOut) : 0;
		const lerpN = (p: number, q: number) => p + (q - p) * m;
		const soft = (feather ?? 40) * unit;
		if (o <= 0) {
			return null;
		}
		return (
			<AbsoluteFill style={{pointerEvents: 'none', opacity: o, overflow: 'hidden'}}>
				<div
					style={{
						position: 'absolute',
						left: lerpN(rect.x, b.x),
						top: lerpN(rect.y, b.y),
						width: lerpN(rect.w, b.w),
						height: lerpN(rect.h, b.h),
						borderRadius: (corner ?? t.radius) * unit,
						// a huge spread shadow is the veil; its blur is the soft edge of the hole
						boxShadow: `0 0 ${soft}px ${Math.max(width, height) * 2}px ${withAlpha(veil, d)}`,
					}}
				/>
			</AbsoluteFill>
		);
	}
	const dist = to ? Math.hypot((to[0] - at[0]) * width, (to[1] - at[1]) * height) / unit : 0;
	const mf = moveFrames ?? Math.max(12, Math.round(18 * Math.sqrt(Math.max(1, dist) / 300)));
	const m = to ? ramp(frame, moveAt, mf, curves.inOut) : 0;
	const x = to ? at[0] + (to[0] - at[0]) * m : at[0];
	const y = to ? at[1] + (to[1] - at[1]) * m : at[1];
	if (o <= 0) {
		return null;
	}
	const r = radius * unit;
	const g = glow ?? (t.dark ? 0.18 : 0);
	const soft = clamp(feather ?? 0.6, 0, 1);
	return (
		<AbsoluteFill style={{pointerEvents: 'none', opacity: o}}>
			<AbsoluteFill
				style={{
					background: `radial-gradient(circle at ${x * width}px ${y * height}px, ${withAlpha(veil, 0)} 0px, ${withAlpha(veil, 0)} ${r * (1 - soft)}px, ${withAlpha(veil, d * 0.55)} ${r * (1 - soft * 0.35)}px, ${withAlpha(veil, d)} ${r}px)`,
				}}
			/>
			{g > 0 ? (
				<AbsoluteFill
					style={{
						background: `radial-gradient(circle at ${x * width}px ${y * height}px, ${withAlpha('#FFFFFF', 0.22 * g)} 0px, rgba(255, 255, 255, 0) ${r}px)`,
						mixBlendMode: 'screen',
					}}
				/>
			) : null}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- light sweep

export type LightSweepProps = {
	at?: number; // frame the sweep starts (default 8)
	duration?: number; // frames to cross (default 28 at 30 fps)
	angle?: number; // lean of the band in degrees (default -18)
	width?: number; // band width, a fraction of the box (default 0.3)
	intensity?: number; // 0 to 1 (default 0.6)
	color?: string; // default white
	blend?: React.CSSProperties['mixBlendMode']; // default soft-light on light themes, screen on dark
	radius?: number; // corner radius px at 1080 when it wraps children (default the theme's)
	children?: React.ReactNode; // the sweep is clipped to this box; without children it crosses the whole frame
	style?: React.CSSProperties;
};

/**
 * One specular pass of light across a card, a logo plate or the frame. A named beat, not decoration: two or three
 * in a 45 s film. The band is a straight gradient that is leaned (skewed) rather than an angled gradient, so its
 * edges stay clean.
 */
export const LightSweep: React.FC<LightSweepProps> = ({
	at = 8,
	duration,
	angle = -18,
	width = 0.3,
	intensity = 0.6,
	color = '#FFFFFF',
	blend,
	radius,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const d = duration ?? at30(28, fps);
	const p = ramp(frame, at, d, curves.sine);
	const live = frame >= at && frame <= at + d;
	const k = clamp(intensity, 0, 1);
	const band = clamp(width, 0.05, 1) * 100;
	const sweep = live ? (
		<div
			style={{
				position: 'absolute',
				top: '-20%',
				height: '140%',
				width: `${band}%`,
				left: `${-band - 20 + p * (140 + band)}%`,
				transform: `skewX(${angle}deg)`,
				background: `linear-gradient(90deg, ${withAlpha(color, 0)} 0%, ${withAlpha(color, 0.45 * k)} 38%, ${withAlpha(color, k)} 50%, ${withAlpha(color, 0.45 * k)} 62%, ${withAlpha(color, 0)} 100%)`,
				mixBlendMode: blend ?? (t.dark ? 'screen' : 'soft-light'),
				pointerEvents: 'none',
			}}
		/>
	) : null;
	if (!children) {
		return <AbsoluteFill style={{overflow: 'hidden', pointerEvents: 'none', ...style}}>{sweep}</AbsoluteFill>;
	}
	// only the band is clipped to the box (with its corners): the children keep their shadows
	return (
		<div style={{position: 'relative', isolation: 'isolate', ...style}}>
			{children}
			<div style={{position: 'absolute', inset: 0, overflow: 'hidden', borderRadius: (radius ?? t.radius) * unit, pointerEvents: 'none'}}>{sweep}</div>
		</div>
	);
};
