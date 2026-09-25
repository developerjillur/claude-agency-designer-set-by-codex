// Grounds drawn by @remotion/effects on a <Solid>: a blueprint grid, liquid contour bands, waves, a sunburst,
// topographic lines and a perspective floor. All WebGL2: renders need --gl=angle (nrk passes it). Without WebGL2
// the ground falls back to CSS, so a missing flag gives a plainer frame instead of a failed render.
import {contourLines} from '@remotion/effects/contour-lines';
import {glow} from '@remotion/effects/glow';
import {gridlines} from '@remotion/effects/gridlines';
import {liquidContours} from '@remotion/effects/liquid-contours';
import {starburst} from '@remotion/effects/starburst';
import {vignette} from '@remotion/effects/vignette';
import {waves} from '@remotion/effects/waves';
import React from 'react';
import {AbsoluteFill, Solid, useCurrentFrame} from 'remotion';
import {clamp, useStage, useTheme} from '../core';
import {darken, mix, withAlpha} from './color';
import {Finish, Ground} from './grounds';
import {hasWebGL2} from './texture';

export type EffectGroundKind = 'blueprint' | 'liquid' | 'waves' | 'starburst' | 'contours' | 'floor';

export type EffectGroundProps = {
	kind?: EffectGroundKind;
	colors?: [string, string]; // the ground and the pattern colour (default: the theme's bg and a tint of its accent)
	contrast?: number; // 0 to 1: how far the pattern colour is from the ground (default depends on the kind)
	speed?: number; // 0 = still, 1 = the designed drift (default), 2 = twice as fast
	scale?: number; // pattern size multiplier (default 1)
	seed?: number;
	loop?: boolean; // liquid and waves: move a whole number of cycles over the Sequence, so it loops seamlessly
	pixelDensity?: number; // canvas pixels per CSS pixel (default 2 for waves and starburst, whose edges are hard, else 1)
	grain?: number | false;
	vignette?: number | false;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

const DEFAULT_CONTRAST: Record<EffectGroundKind, number> = {
	blueprint: 0.5,
	liquid: 0.15,
	waves: 0.14,
	starburst: 0.14,
	contours: 0.5,
	floor: 0.8,
};

let warned = false;

/** A moving pattern ground from the effects package, coloured from the theme, every parameter kept in range. */
export const EffectGround: React.FC<EffectGroundProps> = ({
	kind = 'liquid',
	colors,
	contrast,
	speed = 1,
	scale = 1,
	seed = 4,
	loop = false,
	pixelDensity,
	grain,
	vignette: vig,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, fps, unit, durationInFrames} = useStage();
	const k = clamp(contrast ?? DEFAULT_CONTRAST[kind], 0, 1);
	const c1 = colors?.[0] ?? t.colors.bg;
	const c2 = colors?.[1] ?? mix(c1, t.colors.accent, k);
	const sec = frame / fps;
	const dur = Number.isFinite(durationInFrames) ? durationInFrames : 30 * fps;
	const density = clamp(pixelDensity ?? (kind === 'waves' || kind === 'starburst' ? 2 : 1), 0.25, 3);
	const px = (v: number) => v * unit * density * Math.max(0.05, scale);
	const gl = hasWebGL2();

	if (!gl) {
		if (!warned && typeof console !== 'undefined') {
			warned = true;
			console.warn('EffectGround: no WebGL2 in this browser (render with --gl=angle); drawing a CSS ground instead.');
		}
		return (
			<Ground grain={grain} vignette={vig} style={style}>
				{children}
			</Ground>
		);
	}

	const solid = (effects: React.ComponentProps<typeof Solid>['effects'], color: string | undefined, h = height, top = 0, key?: string) => (
		<Solid
			key={key}
			width={width}
			height={h}
			color={color}
			pixelDensity={density}
			effects={effects}
			style={{position: 'absolute', left: 0, top, width, height: h, display: 'block'}}
		/>
	);

	let layers: React.ReactNode;
	if (kind === 'blueprint') {
		const fine = 24 * unit * scale;
		const pan = sec * 10 * unit * speed;
		const ox = (width % (fine * 5)) / 2 + pan;
		const oy = (height % (fine * 5)) / 2 + pan * 0.6;
		const ink = colors?.[1] ?? t.colors.text;
		layers = solid(
			[
				gridlines({gridSize: fine * density, lineWidth: 1 * unit * density, lineColor: withAlpha(ink, 0.03 + 0.08 * k), offsetX: ox * density, offsetY: oy * density}),
				gridlines({gridSize: fine * 5 * density, lineWidth: 1.6 * unit * density, lineColor: withAlpha(ink, 0.06 + 0.2 * k), offsetX: ox * density, offsetY: oy * density}),
			],
			c1,
		);
	} else if (kind === 'liquid') {
		const rate = 0.08 * speed; // band cycles a second
		const cycles = loop ? Math.max(1, Math.round((dur / fps) * rate)) : 0;
		const phase = 3.23 + (loop ? (cycles * frame) / dur : sec * rate);
		layers = solid(
			[liquidContours({firstColor: c1, secondColor: c2, spacing: px(110), scale: px(520), complexity: 0.25, smoothness: 1, seed, offsetX: 13.4, offsetY: 0, phase})],
			c1,
		);
	} else if (kind === 'waves') {
		const thick = 60 * unit * scale;
		const period = thick * 2;
		const cycles = loop ? Math.max(1, Math.round(((dur / fps) * 18 * unit * speed) / period)) : 0;
		const offset = loop ? (cycles * period * frame) / dur : sec * 18 * unit * speed;
		layers = solid(
			[
				waves({
					colors: [c1, c2],
					direction: 'horizontal',
					thickness: thick * density,
					gap: 0,
					angle: 0,
					amplitude: px(26),
					wavelength: px(240),
					phase: loop ? 0 : sec * 20 * speed,
					offset: offset * density,
				}),
			],
			c1,
		);
	} else if (kind === 'starburst') {
		layers = (
			<>
				<AbsoluteFill style={{background: c1}} />
				{solid(
					[
						starburst({rays: 24, colors: [c1, c2], rotation: sec * 4 * speed, smoothness: 0.08, origin: [0.5, 0.62]}),
						vignette({amount: 0.9, radius: 0.3, feather: 0.7, mode: 'alpha'}),
					],
					c1,
				)}
			</>
		);
	} else if (kind === 'contours') {
		const ink = colors?.[1] ?? (t.dark ? t.colors.text : t.colors.muted);
		layers = solid(
			[
				contourLines({
					lineColor: withAlpha(ink, 0.08 + 0.3 * k),
					lineWidth: 1.6 * unit * density,
					spacing: px(30),
					scale: px(300),
					complexity: 0.55,
					smoothness: 0.6,
					seed,
					offsetX: sec * 6 * unit * speed * density,
					offsetY: 0,
					opacity: 1,
				}),
			],
			c1,
		);
	} else {
		// a floor plane seen in perspective, its horizon at the top edge of the floor layer
		const horizon = 0.42;
		const floorH = height * (1 - horizon);
		const tilt = 72;
		const persp = (floorH / 2) * Math.tan((tilt * Math.PI) / 180);
		const cell = 80 * unit * scale;
		const line = colors?.[1] ?? t.colors.accent;
		const sky = mix(c1, t.colors.accent2, 0.35 * k);
		layers = (
			<>
				<AbsoluteFill style={{background: `linear-gradient(180deg, ${c1} 0%, ${c1} 35%, ${sky} ${horizon * 100}%, ${darken(c1, 0.02)} ${horizon * 100}%)`}} />
				{solid(
					[
						gridlines({
							gridSize: cell * density,
							lineWidth: 2 * unit * density,
							lineColor: withAlpha(line, 0.35 + 0.55 * k),
							rotationX: -tilt,
							perspective: persp * density,
							offsetY: ((sec * 90 * unit * speed) % cell) * density,
						}),
						glow({radius: 10 * unit * density, intensity: 0.7 * k, threshold: 0.2, color: line}),
					],
					undefined,
					floorH,
					height * horizon,
				)}
				<AbsoluteFill
					style={{
						top: height * horizon - 3 * unit,
						height: 6 * unit,
						background: `linear-gradient(90deg, ${withAlpha(line, 0)} 0%, ${withAlpha(mix(line, '#FFFFFF', 0.5), 0.9 * k)} 50%, ${withAlpha(line, 0)} 100%)`,
						filter: `blur(${2 * unit}px)`,
					}}
				/>
			</>
		);
	}

	return (
		<AbsoluteFill style={{background: c1, overflow: 'hidden', ...style}}>
			{layers}
			{children}
			<Finish grain={grain} vignette={vig} dither={0.03} />
		</AbsoluteFill>
	);
};
