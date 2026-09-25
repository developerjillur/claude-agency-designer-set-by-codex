// Grounds: what every scene stands on. A ground is a lit surface (a light with a source, a falloff, a band or a
// floor), never a flat vacuum behind small floating content. Each ground can wrap the scene: it draws under its
// children and puts the theme's finish (vignette and grain) over them.
import {noise2D} from '@remotion/noise';
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp, curves, useStage, useTheme, type Theme} from '../core';
import {ramp} from '../motion';
import {darken, lighten, mix, rgbaToOklab, parseColor, withAlpha} from './color';
import {Grain} from './grain';
import {Vignette} from './texture';

// ---------------------------------------------------------------- finish

export type FinishProps = {
	grain?: number | false; // default the theme's texture.grain (moving, 12 plates a second)
	vignette?: number | false; // default the theme's texture.vignette
	dither?: number; // a still, faint noise that stops smooth light from banding in 8-bit video (0 to switch off)
};

/** The theme's vignette and grain as the top layers of a scene. Grounds add it for you; use it on custom scenes. */
export const Finish: React.FC<FinishProps> = ({grain, vignette, dither = 0}) => {
	const t = useTheme();
	const g = grain === false ? 0 : grain ?? t.texture.grain;
	const v = vignette === false ? 0 : vignette ?? t.texture.vignette;
	return (
		<>
			{v > 0 ? <Vignette amount={v} /> : null}
			{g > 0 ? <Grain amount={g} /> : dither > 0 ? <Grain amount={dither} rate={0} seed="dither" /> : null}
		</>
	);
};

const lightnessOf = (c: string) => rgbaToOklab(parseColor(c)).l;

// smooth multi-stop ramps: a two- or three-stop CSS gradient shows its stops as rings on a large ground
const ease = (k: number) => k * k * (3 - 2 * k);
const rampStops = (from: string, mid: string, to: string, midAt: number, n = 9): string =>
	Array.from({length: n}, (_, i) => {
		const p = i / (n - 1);
		const c = p <= midAt ? mix(from, mid, ease(p / midAt)) : mix(mid, to, ease((p - midAt) / (1 - midAt)));
		return `${c} ${(p * 100).toFixed(1)}%`;
	}).join(', ');

/** The light colour of a ground: white light on light themes, a cool lift tinted by the text and accent on dark ones. */
const lightFor = (t: Theme, base: string, k: number) =>
	t.dark ? mix(base, mix(t.colors.text, t.colors.accent, 0.3), 0.1 * k) : mix(base, '#FFFFFF', Math.min(1, 0.65 * k));

/** A second ground that is really visible against the first (the theme's bg2 when it is, else a step off). */
const bandFor = (t: Theme, base: string) => {
	const b2 = t.colors.bg2;
	if (Math.abs(lightnessOf(b2) - lightnessOf(base)) >= 0.035) {
		return b2;
	}
	return t.dark ? lighten(base, 0.045) : darken(base, 0.05);
};

// ---------------------------------------------------------------- ground

export type GroundKind = 'lit' | 'spot' | 'band' | 'solid';

export type GroundProps = {
	kind?: GroundKind; // lit (light from a source above the frame, default), spot (a pool behind the subject), band, solid
	color?: string; // default the theme's bg
	color2?: string; // the band's colour (default the theme's bg2, or a visible step off the ground)
	light?: [number, number]; // where the light comes from, 0 to 1 of the frame (may be outside): lit [0.3, -0.25], spot [0.5, 0.42]
	intensity?: number; // 0 to 2 (default 1)
	split?: number; // band: position of the seam, 0 to 1 (default 0.64)
	direction?: 'horizontal' | 'vertical'; // band: a floor (horizontal seam) or a column (vertical seam)
	seam?: 'hard' | 'soft';
	drift?: number; // how far the light travels over the Sequence, a fraction of the frame (default 0.05)
	grain?: number | false;
	vignette?: number | false;
	dither?: boolean; // default true when the theme has no grain
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/**
 * The theme's ground as a lit surface. `<Ground>{scene}</Ground>` is a complete stage: lit ground, the scene, then
 * the theme's vignette and grain over it.
 */
export const Ground: React.FC<GroundProps> = ({
	kind = 'lit',
	color,
	color2,
	light,
	intensity = 1,
	split = 0.64,
	direction = 'horizontal',
	seam = 'soft',
	drift = 0.05,
	grain,
	vignette,
	dither = true,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {durationInFrames, width, height, unit} = useStage();
	const base = color ?? t.colors.bg;
	const k = clamp(intensity, 0, 2);
	const hi = lightFor(t, base, k);
	const lo = t.dark ? darken(base, 0.015 * k) : darken(base, 0.055 * k);
	const p = Number.isFinite(durationInFrames) ? ramp(frame, 0, durationInFrames, curves.sine) : 0;
	const src = light ?? (kind === 'spot' ? [0.5, 0.42] : [0.3, -0.25]);
	const lx = (src[0] + drift * (p - 0.5)) * 100;
	const ly = src[1] * 100;
	const layers: React.ReactNode[] = [];

	if (kind === 'lit' || kind === 'band') {
		layers.push(
			<AbsoluteFill
				key="lit"
				style={{background: `radial-gradient(ellipse farthest-corner at ${lx.toFixed(2)}% ${ly.toFixed(2)}%, ${rampStops(hi, base, lo, 0.42)})`}}
			/>,
		);
	} else if (kind === 'spot') {
		layers.push(
			<AbsoluteFill
				key="spot"
				style={{background: `radial-gradient(ellipse 70% 78% at ${lx.toFixed(2)}% ${ly.toFixed(2)}%, ${rampStops(hi, base, lo, 0.55)})`}}
			/>,
		);
	} else {
		layers.push(<AbsoluteFill key="solid" style={{background: base}} />);
	}

	if (kind === 'band') {
		const b = color2 ?? bandFor(t, base);
		const at = clamp(split, 0.05, 0.95);
		const horizontal = direction === 'horizontal';
		const pos = horizontal ? at * height : at * width;
		const soft = seam === 'soft' ? 3 * unit : 0;
		// the band is lit from the same source: a little brighter near the light, a contact shade at the seam
		const bandHi = mix(b, hi, t.dark ? 0.35 : 0.3);
		const bandLo = t.dark ? darken(b, 0.01) : darken(b, 0.035);
		const seamShade = withAlpha(t.dark ? '#000000' : darken(b, 0.35), t.dark ? 0.35 : 0.1);
		layers.push(
			<AbsoluteFill
				key="band"
				style={
					horizontal
						? {top: pos, background: `linear-gradient(180deg, ${seamShade} 0px, ${withAlpha(bandHi, 1)} ${Math.max(soft, 1.5 * unit)}px, ${b} 45%, ${bandLo} 100%)`}
						: {left: pos, background: `linear-gradient(90deg, ${seamShade} 0px, ${bandHi} ${Math.max(soft, 1.5 * unit)}px, ${b} 50%, ${bandLo} 100%)`}
				}
			/>,
		);
	}

	const g = grain === false ? 0 : grain ?? t.texture.grain;
	return (
		<AbsoluteFill style={{background: base, overflow: 'hidden', ...style}}>
			{layers}
			{dither && g < 0.03 ? <Grain amount={0.03} rate={0} seed="dither" /> : null}
			{children}
			<Finish grain={grain} vignette={vignette} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- gradient

export type GradientProps = {
	kind?: 'linear' | 'radial' | 'conic';
	colors?: string[]; // default: a tinted wash from the theme (accent, ground, accent2)
	stops?: number[]; // positions 0 to 1 (default evenly spread)
	angle?: number; // degrees: the direction (linear) or the start (conic); default 135 / 0
	center?: [number, number]; // radial and conic centre, 0 to 1 (default: radial [0.5, 0.42]; conic [0.5, 1.1], a fan from below)
	drift?: number; // slow rotation in degrees a second (linear, conic) or an orbit of the centre (radial); default 0
	space?: 'oklab' | 'oklch' | 'srgb'; // interpolation (default oklab: no grey dip between hues)
	dither?: number; // still noise against banding (default 0.035)
	grain?: number | false;
	vignette?: number | false;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** Linear, radial or conic colour, interpolated in OKLab, dithered against banding, optionally drifting. */
export const Gradient: React.FC<GradientProps> = ({
	kind = 'linear',
	colors,
	stops,
	angle,
	center,
	drift = 0,
	space = 'oklab',
	dither = 0.035,
	grain,
	vignette,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps} = useStage();
	const c = t.colors;
	const sec = frame / fps;
	const k = t.dark ? 0.3 : 0.16;
	const cols =
		colors && colors.length >= 2
			? colors
			: kind === 'conic'
				? [c.bg, mix(c.bg, c.accent, k * 1.2), c.bg, mix(c.bg, c.accent2, k), c.bg]
				: kind === 'radial'
					? [mix(c.bg, c.accent, k * 1.1), c.bg, t.dark ? darken(c.bg, 0.02) : c.bg]
					: [mix(c.bg, c.accent, k), c.bg, mix(c.bg, c.accent2, k * 0.8)];
	const list = cols.map((col, i) => `${col} ${(((stops?.[i] ?? i / (cols.length - 1)) * 100) as number).toFixed(1)}%`).join(', ');
	const how = space === 'srgb' ? '' : ` in ${space}`;
	const ctr = center ?? (kind === 'conic' ? [0.5, 1.1] : [0.5, 0.42]);
	let bg: string;
	if (kind === 'radial') {
		const r = drift ? 0.05 : 0;
		const a = (sec * drift * Math.PI) / 180;
		const cx = (ctr[0] + r * Math.cos(a)) * 100;
		const cy = (ctr[1] + r * Math.sin(a)) * 100;
		bg = `radial-gradient(ellipse farthest-corner at ${cx.toFixed(2)}% ${cy.toFixed(2)}%${how}, ${list})`;
	} else if (kind === 'conic') {
		const a0 = (angle ?? 0) + sec * drift;
		bg = `conic-gradient(from ${a0.toFixed(2)}deg at ${ctr[0] * 100}% ${ctr[1] * 100}%${how}, ${list})`;
	} else {
		const a0 = (angle ?? 135) + sec * drift;
		bg = `linear-gradient(${a0.toFixed(2)}deg${how}, ${list})`;
	}
	return (
		<AbsoluteFill style={{background: cols[Math.floor(cols.length / 2)], overflow: 'hidden', ...style}}>
			<AbsoluteFill style={{background: bg}} />
			{dither > 0 ? <Grain amount={dither} rate={0} seed="dither" /> : null}
			{children}
			<Finish grain={grain} vignette={vignette} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- mesh

export type MeshProps = {
	colors?: string[]; // 3 to 5 blob colours (default from the theme's accents, softened into the ground)
	base?: string; // the ground under the blobs (default the theme's bg)
	speed?: number; // 0 = still, 1 = a slow drift (a full wander takes about 12 s), 2 = twice as fast
	wander?: number; // how far a blob travels, a fraction of the frame (default 0.16)
	size?: number; // blob size multiplier (default 1)
	seed?: string;
	grain?: number | false; // default: the theme's grain, at least 0.05 (grain hides banding in moving gradients)
	vignette?: number | false;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

const ANCHORS: [number, number, number][] = [
	[0.16, 0.2, 0.62],
	[0.84, 0.16, 0.56],
	[0.8, 0.84, 0.6],
	[0.2, 0.82, 0.54],
	[0.52, 0.5, 0.42],
];

/** A soft moving colour field: 3 to 5 blobs of light drifting on seeded noise, with grain against banding. */
export const Mesh: React.FC<MeshProps> = ({
	colors,
	base,
	speed = 1,
	wander = 0.16,
	size = 1,
	seed = 'mesh',
	grain,
	vignette,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, fps} = useStage();
	const c = t.colors;
	const ground = base ?? c.bg;
	const cols = (
		colors && colors.length >= 2
			? colors
			: t.dark
				? [mix(ground, c.accent, 0.55), mix(ground, c.accent2, 0.42), mix(ground, mix(c.accent, c.accent2, 0.5), 0.35), mix(ground, c.bg2, 0.9), mix(ground, c.accent, 0.3)]
				: [mix(ground, c.accent, 0.42), mix(ground, c.accent2, 0.4), mix(ground, c.highlight, 0.45), c.bg2, mix(ground, c.accent, 0.25)]
	).slice(0, 5);
	const long = Math.max(width, height);
	const time = (frame / fps) * 0.085 * speed;
	const blobs = cols.map((col, i) => {
		const [ax, ay, ar] = ANCHORS[i % ANCHORS.length];
		const x = (ax + noise2D(seed, time, i * 3.1) * wander) * width;
		const y = (ay + noise2D(seed, time + 17.3, i * 3.1 + 1.7) * wander) * height;
		const r = ar * long * size * (1 + 0.12 * noise2D(seed, time * 0.7 + 41.9, i * 3.1 + 2.3));
		// a gaussian-like falloff drawn with stops (no CSS blur filter: blurs are slow and band)
		const fall = [1, 0.9, 0.72, 0.5, 0.3, 0.14, 0.04, 0]
			.map((a, j) => `${withAlpha(col, a)} ${((j / 7) * 100).toFixed(1)}%`)
			.join(', ');
		return `radial-gradient(circle ${r.toFixed(1)}px at ${x.toFixed(1)}px ${y.toFixed(1)}px in oklab, ${fall})`;
	});
	const g = grain === false ? 0 : grain ?? Math.max(0.05, t.texture.grain);
	return (
		<AbsoluteFill style={{background: ground, overflow: 'hidden', ...style}}>
			<AbsoluteFill style={{background: [...blobs].reverse().join(', ')}} />
			{children}
			<Finish grain={g} vignette={vignette} />
		</AbsoluteFill>
	);
};
