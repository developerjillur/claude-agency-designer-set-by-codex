// Light: light-leak overlays, a starburst ground and a shine sweep. The effect versions from @remotion/effects
// (the @remotion/light-leaks and @remotion/starburst components are deprecated and go away in 5.0).
import React from 'react';
import {AbsoluteFill, HtmlInCanvas, Solid, interpolate, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {fx} from './effects';
import {useLookEngine, type LookEngine} from './looks';
import {FxNestContext, mixHex} from './util';

/**
 * Hue shifts for lightLeak(), measured on renders: 0 is the natural yellow-orange and the hue turns toward red
 * first (30 coral, 60 rose, 90 magenta, 180 blue, 270 green). Pass a number for anything in between.
 */
export const LEAK_HUES = {warm: 0, coral: 30, rose: 60, magenta: 90, violet: 135, blue: 180, cyan: 210, teal: 240, green: 280, lime: 320} as const;

export type LeakHue = keyof typeof LEAK_HUES;

export type LightLeakProps = {
	seed?: number;
	hue?: number | LeakHue;
	/** Layer opacity (0.85). */
	opacity?: number;
	/** screen (default) adds light over the scene; normal paints the leak as it is. */
	blend?: React.CSSProperties['mixBlendMode'];
	/** Frames before the leak starts, and its length (default: the rest of the Sequence). */
	delay?: number;
	duration?: number;
	/** Play the reveal backwards (it grows from the far side). */
	reverse?: boolean;
	/**
	 * How far the leak spreads, 0 to 1. At 1 (default) it plays the effect's full course, which covers the whole
	 * frame at mid-point (the right thing over a cut). Below 1 it swells to that coverage and falls back: a
	 * flare on a title that never hides it.
	 */
	peak?: number;
	style?: React.CSSProperties;
};

/**
 * A light leak over whatever is behind it: grows over the first half of its time, retracts over the second. Put it
 * in a Sequence, over a cut (a TransitionSeries.Overlay or tr.leak) or on a title. One per cut, not on every shot.
 */
export const LightLeak: React.FC<LightLeakProps> = ({seed = 0, hue = 'warm', opacity = 0.85, blend = 'screen', delay = 0, duration, reverse = false, peak = 1, style}) => {
	const frame = useCurrentFrame();
	const {width, height, durationInFrames} = useStage();
	const len = Math.max(2, duration ?? (Number.isFinite(durationInFrames) ? durationInFrames - delay : 60));
	const t = interpolate(frame, [delay, delay + len - 1], reverse ? [1, 0] : [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	// the effect reveals over 0 to 0.5 and retracts over 0.5 to 1, always through full cover: a partial leak
	// swells to peak / 2 and falls back the way it came instead
	const k = Math.min(1, Math.max(0, peak));
	const p = k >= 1 ? t : 0.5 * k * Math.sin(Math.PI * t);
	if (frame < delay || frame >= delay + len) {
		return null;
	}
	return (
		<Solid
			width={width}
			height={height}
			style={{position: 'absolute', inset: 0, mixBlendMode: blend, opacity, pointerEvents: 'none', ...style}}
			effects={[fx.lightLeak({progress: p, seed, hue: typeof hue === 'number' ? hue : LEAK_HUES[hue]})]}
		/>
	);
};

export type StarburstProps = {
	/** Two or more ray colours (default: the theme accent and a lighter accent). */
	colors?: string[];
	rays?: number; // 2 to 100 (24)
	/** Degrees per second (6); negative turns the other way. */
	speed?: number;
	rotation?: number; // start angle
	origin?: readonly [number, number]; // UV 0 to 1 ([0.5, 0.5])
	smoothness?: number; // anti-aliasing of the ray edges (0.035)
	vignette?: number; // (0.35)
	/** Dither against banding in the encode (0.025). */
	grain?: number;
	width?: number;
	height?: number;
	style?: React.CSSProperties;
};

/** A rotating sunburst ground (retro, sale, celebration): one Solid with the starburst effect, vignette and dither. */
export const Starburst: React.FC<StarburstProps> = ({colors, rays = 24, speed = 6, rotation = 0, origin = [0.5, 0.5], smoothness = 0.035, vignette = 0.35, grain = 0.025, width, height, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width: W, height: H, fps} = useStage();
	const cols = colors && colors.length >= 2 ? colors : [t.colors.accent, mixHex(t.colors.accent, '#ffffff', 0.14)];
	return (
		<Solid
			width={Math.round(width ?? W)}
			height={Math.round(height ?? H)}
			style={{position: 'absolute', inset: 0, ...style}}
			effects={[
				fx.starburst({colors: cols, rays, rotation: (((rotation + (frame / fps) * speed) % 360) + 360) % 360, smoothness, origin}),
				fx.vignette({amount: vignette, radius: 0.62, feather: 0.65}),
				fx.noise({amount: grain}),
			]}
		/>
	);
};

export type ShineProps = {
	delay?: number;
	/** Frames for one sweep (default about 1.1 s). */
	duration?: number;
	/** Frames from one sweep to the next (0: once). */
	repeat?: number;
	angle?: number; // degrees; 0 moves right, 90 up (30)
	width?: number; // band width scale (1)
	intensity?: number; // (1)
	ease?: Ease;
	/** canvas: the shine follows the alpha of the children (logos, cut-outs). css: a band over an opaque box. */
	engine?: LookEngine;
	/** Corner radius of the box for the css engine (px at 1080). */
	radius?: number;
	/** Size of the painted area (default: the frame). */
	boxWidth?: number;
	boxHeight?: number;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** A premium light sweep across a logo, a product shot or a card. Use it on a hero beat, not everywhere. */
export const Shine: React.FC<ShineProps> = ({delay = 0, duration, repeat = 0, angle = 30, width = 1, intensity = 1, ease = curves.inOut, engine, radius = 0, boxWidth, boxHeight, children, style}) => {
	const e = useLookEngine(engine, '<Shine>');
	const frame = useCurrentFrame();
	const {width: W, height: H, fps, unit} = useStage();
	const len = duration ?? at30(34, fps);
	const local = repeat > 0 && frame >= delay ? delay + ((frame - delay) % Math.max(len + 1, repeat)) : frame;
	const p = ramp(local, delay, len, ease);
	const w = Math.round(boxWidth ?? W);
	const h = Math.round(boxHeight ?? H);
	if (e === 'canvas') {
		return (
			<HtmlInCanvas width={w} height={h} effects={[fx.shine({progress: p, angle, width, intensity})]} style={style}>
				<FxNestContext.Provider value={{canvas: 'inside a canvas <Shine>'}}>
					<AbsoluteFill style={{width: w, height: h}}>{children}</AbsoluteFill>
				</FxNestContext.Provider>
			</HtmlInCanvas>
		);
	}
	// css: a soft white band moving across, soft-light blended, clipped to the box
	const travel = Math.hypot(w, h);
	const band = 180 * width * unit;
	// from fully outside one corner to fully outside the opposite one
	const pos = (p - 0.5) * (travel + 2 * band);
	const visible = p > 0 && p < 1;
	return (
		<AbsoluteFill style={{width: w, height: h, borderRadius: radius * unit, overflow: 'hidden', ...style}}>
			<AbsoluteFill>{children}</AbsoluteFill>
			{visible ? (
				<div
					style={{
						position: 'absolute',
						left: w / 2 - travel,
						top: h / 2 - travel,
						width: travel * 2,
						height: travel * 2,
						rotate: `${-angle}deg`,
						pointerEvents: 'none',
						mixBlendMode: 'soft-light',
						opacity: Math.min(1, intensity),
						background: `linear-gradient(90deg, rgba(255,255,255,0) calc(50% + ${pos - band}px), rgba(255,255,255,0.95) calc(50% + ${pos}px), rgba(255,255,255,0) calc(50% + ${pos + band}px))`,
					}}
				/>
			) : null}
		</AbsoluteFill>
	);
};
