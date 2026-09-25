// CSS and inline-SVG building blocks: they work everywhere (any browser, inside shader transitions, inside a
// canvas look) and need no WebGL. The looks use them as their "css" engine; they are also useful on their own.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {useStage} from '../core';
import {r01, rgba, stepSeed, useSafeId} from './util';

type Blend = React.CSSProperties['mixBlendMode'];

/**
 * Film grain from SVG turbulence, re-seeded `hz` times a second (12 reads as film). `amount` is the layer opacity
 * (0.2 to 0.5 with overlay). `size` above 1 makes coarser grain. Deterministic: the seed is a function of the frame.
 */
export const Grain: React.FC<{amount?: number; size?: number; hz?: number; seed?: number; blend?: Blend; style?: React.CSSProperties}> = ({
	amount = 0.35,
	size = 1,
	hz = 12,
	seed = 0,
	blend = 'overlay',
	style,
}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const id = useSafeId('grain');
	const s = seed + stepSeed(frame, fps, hz);
	if (amount <= 0) {
		return null;
	}
	return (
		<svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%', mixBlendMode: blend, opacity: amount, pointerEvents: 'none', ...style}}>
			<filter id={id} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
				<feTurbulence type="fractalNoise" baseFrequency={0.78 / (unit * Math.max(0.2, size))} numOctaves={2} seed={s} stitchTiles="stitch" />
				<feColorMatrix type="matrix" values="0.33 0.33 0.33 0 0 0.33 0.33 0.33 0 0 0.33 0.33 0.33 0 0 0 0 0 0 1" />
				<feComponentTransfer>
					<feFuncR type="linear" slope="2.6" intercept="-0.8" />
					<feFuncG type="linear" slope="2.6" intercept="-0.8" />
					<feFuncB type="linear" slope="2.6" intercept="-0.8" />
				</feComponentTransfer>
			</filter>
			<rect width="100%" height="100%" filter={`url(#${id})`} />
		</svg>
	);
};

/** A radial vignette overlay. `strength` is the corner opacity (about 0.15 to 0.35 reads natural). */
export const VignetteOverlay: React.FC<{strength?: number; start?: number; color?: string; blend?: Blend}> = ({
	strength = 0.3,
	start = 0.55,
	color = '#000000',
	blend = 'normal',
}) => (
	<AbsoluteFill
		style={{
			pointerEvents: 'none',
			mixBlendMode: blend,
			background: `radial-gradient(ellipse farthest-corner at 50% 50%, ${rgba(color, 0)} ${Math.round(start * 100)}%, ${rgba(color, strength)} 100%)`,
		}}
	/>
);

/** Horizontal scanlines (px at 1080); `roll` moves them down over time (px per frame). */
export const ScanlineOverlay: React.FC<{opacity?: number; spacing?: number; thickness?: number; roll?: number; color?: string; blend?: Blend}> = ({
	opacity = 0.22,
	spacing = 4,
	thickness = 1.6,
	roll = 0,
	color = '#000000',
	blend = 'multiply',
}) => {
	const frame = useCurrentFrame();
	const {unit} = useStage();
	const sp = spacing * unit;
	const th = Math.min(sp, thickness * unit);
	return (
		<AbsoluteFill
			style={{
				pointerEvents: 'none',
				mixBlendMode: blend,
				opacity,
				backgroundImage: `repeating-linear-gradient(to bottom, ${color} 0px, ${color} ${th}px, transparent ${th}px, transparent ${sp}px)`,
				backgroundPosition: `0px ${(frame * roll * unit) % sp}px`,
			}}
		/>
	);
};

/** CRT aperture grille: thin vertical red, green and blue stripes, multiplied over the picture. */
export const GrilleOverlay: React.FC<{opacity?: number; pitch?: number}> = ({opacity = 0.14, pitch = 3}) => {
	const {unit} = useStage();
	const p = (pitch * unit) / 3;
	return (
		<AbsoluteFill
			style={{
				pointerEvents: 'none',
				mixBlendMode: 'multiply',
				opacity,
				backgroundImage: `repeating-linear-gradient(to right, #ff3b3b 0px, #ff3b3b ${p}px, #3bff5a ${p}px, #3bff5a ${2 * p}px, #3b6bff ${2 * p}px, #3b6bff ${3 * p}px)`,
			}}
		/>
	);
};

/**
 * Splits the red and blue channels of its children by `dx`, `dy` px (an SVG filter, so it works on any DOM).
 * 0 renders the children untouched.
 */
export const RgbSplit: React.FC<{dx?: number; dy?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({dx = 4, dy = 0, children, style}) => {
	const id = useSafeId('rgb');
	const on = Math.abs(dx) > 0.05 || Math.abs(dy) > 0.05;
	return (
		<AbsoluteFill style={{filter: on ? `url(#${id})` : undefined, ...style}}>
			{on ? (
				<svg width="0" height="0" style={{position: 'absolute'}}>
					<filter id={id} x="-2%" y="-2%" width="104%" height="104%" colorInterpolationFilters="sRGB">
						<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r" />
						<feOffset in="r" dx={-dx} dy={-dy} result="ro" />
						<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="g" />
						<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="b" />
						<feOffset in="b" dx={dx} dy={dy} result="bo" />
						<feBlend in="ro" in2="g" mode="screen" result="rg" />
						<feBlend in="rg" in2="bo" mode="screen" />
					</filter>
				</svg>
			) : null}
			{children}
		</AbsoluteFill>
	);
};

/**
 * Bloom: a second copy of the children, crushed to its highlights, blurred and screened on top. It renders the
 * children twice, so keep what is inside light.
 */
export const Bloom: React.FC<{amount?: number; radius?: number; threshold?: number; children: React.ReactNode}> = ({
	amount = 0.55,
	radius = 26,
	threshold = 0.5,
	children,
}) => {
	const {unit} = useStage();
	// contrast around mid grey works as a soft threshold; brightness then drops what is left under it
	const c = 1 + threshold * 3;
	return (
		<AbsoluteFill>
			<AbsoluteFill>{children}</AbsoluteFill>
			{amount > 0 ? (
				<AbsoluteFill style={{filter: `contrast(${c}) brightness(${1 - threshold * 0.35}) blur(${radius * unit}px)`, mixBlendMode: 'screen', opacity: amount, pointerEvents: 'none'}}>
					{children}
				</AbsoluteFill>
			) : null}
		</AbsoluteFill>
	);
};

/** Posterizes the colours of its children to `levels` per channel (SVG feComponentTransfer, exact steps). */
export const PosterizeCss: React.FC<{levels?: number; children: React.ReactNode}> = ({levels = 5, children}) => {
	const id = useSafeId('post');
	const n = Math.max(2, Math.round(levels));
	const table = Array.from({length: n}, (_, i) => (i / (n - 1)).toFixed(4)).join(' ');
	return (
		<AbsoluteFill style={{filter: `url(#${id})`}}>
			<svg width="0" height="0" style={{position: 'absolute'}}>
				<filter id={id} colorInterpolationFilters="sRGB">
					<feComponentTransfer>
						<feFuncR type="discrete" tableValues={table} />
						<feFuncG type="discrete" tableValues={table} />
						<feFuncB type="discrete" tableValues={table} />
					</feComponentTransfer>
				</filter>
			</svg>
			{children}
		</AbsoluteFill>
	);
};

/**
 * Film dust: a few seeded specks for a frame or two, and now and then a hair. `amount` 0 to 1 scales how often.
 * Everything comes from the frame, so every render tab draws the same dust.
 */
export const DustOverlay: React.FC<{amount?: number; seed?: string; hz?: number; color?: string}> = ({
	amount = 1,
	seed = 'dust',
	hz = 12,
	color = '#1a120a',
}) => {
	const frame = useCurrentFrame();
	const {fps, width, height, unit} = useStage();
	const step = stepSeed(frame, fps, hz);
	const n = r01(`${seed}-n-${step}`) < 0.55 * amount ? 1 + Math.floor(r01(`${seed}-c-${step}`) * 3) : 0;
	const hair = r01(`${seed}-h-${step}`) < 0.06 * amount;
	if (n === 0 && !hair) {
		return null;
	}
	const hx = r01(`${seed}-hx-${step}`) * width;
	const hy = r01(`${seed}-hy-${step}`) * height;
	const hs = (40 + r01(`${seed}-hs-${step}`) * 70) * unit;
	return (
		<svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none'}} viewBox={`0 0 ${width} ${height}`}>
			{Array.from({length: n}).map((_, i) => {
				const k = `${seed}-${step}-${i}`;
				const light = r01(`${k}-l`) < 0.35;
				return (
					<ellipse
						key={i}
						cx={r01(`${k}-x`) * width}
						cy={r01(`${k}-y`) * height}
						rx={(1.2 + r01(`${k}-r`) * 3) * unit}
						ry={(1 + r01(`${k}-q`) * 2.2) * unit}
						fill={light ? '#fff8e8' : color}
						opacity={0.35 + r01(`${k}-o`) * 0.4}
					/>
				);
			})}
			{hair ? (
				<path
					d={`M${hx},${hy} q${hs * 0.4},${-hs * 0.3} ${hs * 0.7},${hs * 0.1} t${hs * 0.5},${hs * 0.35}`}
					stroke={color}
					strokeWidth={1.2 * unit}
					fill="none"
					opacity={0.45}
				/>
			) : null}
		</svg>
	);
};

export type SliceSpec = {top: number; height: number; dx: number};

/** Seeded glitch bands: `count` bands with offsets up to `amount` px (for SlicesCss and glitch transitions). */
export const makeSlices = (seed: string, count: number, amount: number): SliceSpec[] =>
	Array.from({length: count}, (_, i) => {
		const h = 0.015 + r01(`${seed}-h${i}`) * 0.09;
		return {
			top: r01(`${seed}-t${i}`) * (1 - h),
			height: h,
			dx: (r01(`${seed}-d${i}`) * 2 - 1) * amount,
		};
	});

/**
 * The CSS glitch: the children once, then one clipped copy per band pushed sideways. Renders the children
 * `slices.length + 1` times: use it only on burst frames.
 */
export const SlicesCss: React.FC<{slices: SliceSpec[]; children: React.ReactNode}> = ({slices, children}) => (
	<AbsoluteFill>
		<AbsoluteFill>{children}</AbsoluteFill>
		{slices.map((s, i) => (
			<AbsoluteFill
				key={i}
				style={{
					clipPath: `inset(${(s.top * 100).toFixed(3)}% 0 ${((1 - s.top - s.height) * 100).toFixed(3)}% 0)`,
					translate: `${s.dx}px 0px`,
				}}
			>
				{children}
			</AbsoluteFill>
		))}
	</AbsoluteFill>
);
