// Transitions between scenes: presets over @remotion/transitions (CSS and the shader presentations that render on
// 4.0.528 with --gl=angle), the kit's own CSS presentations, overlays that sit on a cut, and <Scenes>, which builds
// the TransitionSeries from a list and checks its timing.
import {Audio} from '@remotion/media';
import {
	linearTiming,
	springTiming,
	TransitionSeries,
	type TransitionPresentation,
	type TransitionPresentationComponentProps,
	type TransitionTiming,
} from '@remotion/transitions';
import {blurSlide} from '@remotion/transitions/blur-slide';
import {bookFlip, type BookFlipDirection} from '@remotion/transitions/book-flip';
import {clockWipe} from '@remotion/transitions/clock-wipe';
import {crossZoom} from '@remotion/transitions/cross-zoom';
import {crosswarp} from '@remotion/transitions/crosswarp';
import {dissolve} from '@remotion/transitions/dissolve';
import {dreamyZoom} from '@remotion/transitions/dreamy-zoom';
import {fade} from '@remotion/transitions/fade';
import {filmBurn} from '@remotion/transitions/film-burn';
import {flip, type FlipDirection} from '@remotion/transitions/flip';
import {iris} from '@remotion/transitions/iris';
import {linearBlur} from '@remotion/transitions/linear-blur';
import {none} from '@remotion/transitions/none';
import {pushCut} from '@remotion/transitions/push-cut';
import {ripple} from '@remotion/transitions/ripple';
import {slide, type SlideDirection} from '@remotion/transitions/slide';
import {swap} from '@remotion/transitions/swap';
import {wipe, type WipeDirection} from '@remotion/transitions/wipe';
import {zoomBlur} from '@remotion/transitions/zoom-blur';
import {zoomInOut} from '@remotion/transitions/zoom-in-out';
import React from 'react';
import {AbsoluteFill, Easing, Sequence, Solid, useCurrentFrame, useVideoConfig} from 'remotion';
import {at30, curves, useTheme, type Ease, type Theme} from '../core';
import {ramp} from '../motion';
import {RgbSplit, SlicesCss, makeSlices} from './css';
import {fx} from './effects';
import {LEAK_HUES, LightLeak, type LeakHue} from './light';
import {coverSize, shapePath, type MaskShape} from './masks';
import {FxNestContext, hex6, r01, useFxNest, useSafeId} from './util';

export {useTransitionProgress} from '@remotion/transitions';

type AnyPresentation = TransitionPresentation<Record<string, unknown>>;

const asAny = <P extends Record<string, unknown>>(p: TransitionPresentation<P>): AnyPresentation => p as unknown as AnyPresentation;

export type TransitionContext = {width: number; height: number; fps: number; unit: number; theme: Theme};

export type TransitionSound = {
	src: string;
	volume?: number;
	/** Frames the sound starts before the cut (default: at the start of the transition; 0 for a hard cut). */
	lead?: number;
};

export type TransitionEngine = 'css' | 'shader' | 'overlay' | 'cut';

/**
 * A transition recipe for <Scenes>. `frames` is written for 30 fps and scaled to the composition's rate. The
 * recipe is turned into a presentation and a timing inside <Scenes>, where the frame size and theme are known.
 */
export type FxTransition = {
	name: string;
	/** css: any browser. shader: HTML-in-canvas + WebGL2 (render with --gl=angle). overlay: sits on a cut
	 * without shortening the edit. cut: a hard cut (only useful to carry a sound). */
	engine: TransitionEngine;
	frames: number;
	/** Hard-cut styles hide the incoming scene until this share of the transition; <Scenes> delays that scene's
	 * content by the hidden frames and lengthens it by the same, so its own frame 0 is the first one you see. */
	cutAt?: number;
	sound?: TransitionSound;
	make: (ctx: TransitionContext) => {presentation?: AnyPresentation; timing?: TransitionTiming; overlay?: React.ReactNode};
};

const lin = (frames: number, easing?: Ease): TransitionTiming => linearTiming({durationInFrames: Math.max(1, frames), easing});
// damping 200 = no overshoot; the default rest threshold (0.005) snaps visibly at the end
const spr = (frames: number): TransitionTiming =>
	springTiming({config: {damping: 200}, durationInFrames: Math.max(1, frames), durationRestThreshold: 0.001});

type Base = {frames?: number; sound?: TransitionSound};

// ---------------------------------------------------------------- the kit's own presentations

type ZoomThroughProps = {depth: number; blur: number; unit: number};

const ZoomThrough: React.FC<TransitionPresentationComponentProps<ZoomThroughProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const {depth, blur, unit} = passedProps;
	if (presentationDirection === 'exiting') {
		// a dolly into the old frame: scale = 1 / distance, so the move accelerates like a real camera; mostly linear
		// distance keeps it visibly moving from the first frame
		const e = 0.3 * curves.inCubic(p) + 0.7 * p;
		const distance = 1 + (depth - 1) * e;
		const b = blur * unit * e;
		return <AbsoluteFill style={{scale: String(1 / Math.max(0.02, distance)), filter: b > 0.1 ? `blur(${b}px)` : undefined}}>{children}</AbsoluteFill>;
	}
	// the new scene waits until the camera is inside the old one, then comes forward out of the blur and lands by
	// 90 percent, so no sliver of the old scene shows around it at the end
	const k = curves.outCubic(Math.min(1, Math.max(0, (p - 0.4) / 0.5)));
	const b = blur * unit * (1 - k);
	return (
		<AbsoluteFill style={{scale: String(0.8 + 0.2 * k), opacity: ramp(p, 0.42, 0.36, curves.sine), filter: b > 0.1 ? `blur(${b}px)` : undefined}}>
			{children}
		</AbsoluteFill>
	);
};

type WhipProps = {direction: 'left' | 'right' | 'up' | 'down'; blur: number; frames: number};

const whipEase = Easing.bezier(0.72, 0, 0.28, 1);

const WhipPan: React.FC<TransitionPresentationComponentProps<WhipProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const {width, height} = useVideoConfig();
	const id = useSafeId('whip');
	const {direction, blur, frames} = passedProps;
	const horizontal = direction === 'left' || direction === 'right';
	const sign = direction === 'left' || direction === 'up' ? -1 : 1;
	const dist = horizontal ? width : height;
	const x = whipEase(Math.min(1, Math.max(0, p)));
	const offset = presentationDirection === 'exiting' ? sign * x * dist : sign * (x - 1) * dist;
	// motion blur from the speed: px per frame, half of it for a 180 degree shutter
	const dp = 0.5 / Math.max(1, frames);
	const speed = ((whipEase(Math.min(1, p + dp)) - whipEase(Math.max(0, p - dp))) / (2 * dp)) * (dist / Math.max(1, frames));
	const sd = Math.min(140, (speed * 0.5 * blur) / 2.2);
	const on = sd > 0.4;
	return (
		<AbsoluteFill>
			{on ? (
				<svg width="0" height="0" style={{position: 'absolute'}}>
					<filter id={id} x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
						<feGaussianBlur stdDeviation={horizontal ? `${sd} 0` : `0 ${sd}`} edgeMode="duplicate" />
					</filter>
				</svg>
			) : null}
			<AbsoluteFill style={{translate: horizontal ? `${offset}px 0px` : `0px ${offset}px`, filter: on ? `url(#${id})` : undefined}}>{children}</AbsoluteFill>
		</AbsoluteFill>
	);
};

type GlitchCutProps = {seed: string; intensity: number; unit: number; frames: number};

const GlitchCut: React.FC<TransitionPresentationComponentProps<GlitchCutProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const {seed, intensity, unit, frames} = passedProps;
	const step = Math.round(p * frames);
	const exiting = presentationDirection === 'exiting';
	const visible = exiting ? p < 0.5 : p >= 0.5;
	if (!visible) {
		return <AbsoluteFill style={{opacity: 0}}>{children}</AbsoluteFill>;
	}
	const i = intensity * Math.pow(1 - Math.min(1, Math.abs(p - 0.5) * 2), 0.6);
	const slices = makeSlices(`${seed}-${step}-${exiting ? 'a' : 'b'}`, 3 + Math.floor(6 * i), 90 * i * unit);
	const jitter = (r01(`${seed}-j-${step}`) - 0.5) * 40 * i * unit;
	const flash = !exiting && step === Math.round(0.5 * frames);
	return (
		<AbsoluteFill style={{translate: `${jitter}px 0px`}}>
			<RgbSplit dx={(step % 2 ? -1 : 1) * 16 * i * unit}>
				{i > 0.02 ? <SlicesCss slices={slices}>{children}</SlicesCss> : children}
			</RgbSplit>
			{flash ? <AbsoluteFill style={{background: '#ffffff', opacity: 0.12, mixBlendMode: 'screen'}} /> : null}
		</AbsoluteFill>
	);
};

type LeakCrossProps = {seed: number; hue: number; opacity: number};

const LightLeakCross: React.FC<TransitionPresentationComponentProps<LeakCrossProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const {width, height} = useVideoConfig();
	if (presentationDirection === 'exiting') {
		return <AbsoluteFill style={{filter: `brightness(${1 + 0.25 * Math.sin(Math.PI * p)})`}}>{children}</AbsoluteFill>;
	}
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{opacity: ramp(p, 0.42, 0.16, curves.sine)}}>{children}</AbsoluteFill>
			<Solid
				width={width}
				height={height}
				style={{position: 'absolute', inset: 0, mixBlendMode: 'screen', opacity: passedProps.opacity, pointerEvents: 'none'}}
				effects={[fx.lightLeak({progress: p, seed: passedProps.seed, hue: passedProps.hue})]}
			/>
		</AbsoluteFill>
	);
};

type BlurDissolveProps = {blur: number; unit: number};

const BlurDissolve: React.FC<TransitionPresentationComponentProps<BlurDissolveProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const B = passedProps.blur * passedProps.unit;
	if (presentationDirection === 'exiting') {
		const b = B * curves.inCubic(p);
		return <AbsoluteFill style={{filter: b > 0.1 ? `blur(${b}px)` : undefined}}>{children}</AbsoluteFill>;
	}
	const b = B * (1 - curves.outCubic(p));
	return <AbsoluteFill style={{opacity: curves.inOut(p), filter: b > 0.1 ? `blur(${b}px)` : undefined}}>{children}</AbsoluteFill>;
};

type MaskRevealProps = {shape: MaskShape | 'diagonal'; at: readonly [number, number]; feather: number; ring: string; angle: number; unit: number};

const MaskReveal: React.FC<TransitionPresentationComponentProps<MaskRevealProps>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
	const {width, height} = useVideoConfig();
	const {shape, at, feather, ring, angle, unit} = passedProps;
	if (presentationDirection === 'exiting') {
		// the old scene recedes a touch, so the new one reads as coming forward
		return <AbsoluteFill style={{filter: `brightness(${1 - 0.18 * p})`}}>{children}</AbsoluteFill>;
	}
	const e = curves.inOut(p);
	if (shape === 'diagonal') {
		const slant = height * Math.tan((Math.min(40, Math.max(0, angle)) * Math.PI) / 180);
		const bar = 26 * unit;
		const xt = -slant - bar + e * (width + 2 * slant + 2 * bar);
		const xb = xt - slant;
		const clip = `polygon(-10px -10px, ${xt}px -10px, ${xb}px ${height + 10}px, -10px ${height + 10}px)`;
		const barClip = `polygon(${xt}px -10px, ${xt + bar}px -10px, ${xb + bar}px ${height + 10}px, ${xb}px ${height + 10}px)`;
		return (
			<AbsoluteFill>
				<AbsoluteFill style={{clipPath: clip}}>{children}</AbsoluteFill>
				{ring ? <AbsoluteFill style={{clipPath: barClip, background: ring}} /> : null}
			</AbsoluteFill>
		);
	}
	const cx = at[0] * width;
	const cy = at[1] * height;
	const full = coverSize(shape, cx, cy, width, height) + feather * unit;
	const s = full * e;
	const f = feather * unit;
	if (shape === 'circle' && f > 0) {
		const r = s / 2;
		const mask = `radial-gradient(circle ${Math.max(0.01, r)}px at ${cx}px ${cy}px, #000 ${Math.max(0, r - f)}px, transparent ${Math.max(0.01, r)}px)`;
		return <AbsoluteFill style={{WebkitMaskImage: mask, maskImage: mask}}>{children}</AbsoluteFill>;
	}
	const d = shapePath({shape, cx, cy, size: s});
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{clipPath: d ? `path('${d}')` : 'inset(50% 50% 50% 50%)'}}>{children}</AbsoluteFill>
			{ring && d ? (
				<svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none'}}>
					<path d={d} fill="none" stroke={ring} strokeWidth={10 * unit} />
				</svg>
			) : null}
		</AbsoluteFill>
	);
};

/** Renders its children only before local frame `frame` (the first part of a split scene). */
const HideFrom: React.FC<{frame: number; children: React.ReactNode}> = ({frame, children}) => {
	const f = useCurrentFrame();
	return f >= frame ? null : <>{children}</>;
};

/** A flash that rises to `peak` on the cut and falls away; the overlay's own length sets its timing. */
const Flash: React.FC<{color: string; peak: number}> = ({color, peak}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const half = Math.max(1, durationInFrames / 2);
	const up = ramp(frame, 0, half, curves.in);
	const down = 1 - ramp(frame, half, half, curves.out);
	return <AbsoluteFill style={{background: color, opacity: peak * Math.min(up, down), pointerEvents: 'none'}} />;
};

// ---------------------------------------------------------------- presets

export const tr = {
	/** A hard cut (no overlap). Only needed to hang a sound on the cut. */
	cut: (o: {sound?: TransitionSound} = {}): FxTransition => ({name: 'cut', engine: 'cut', frames: 0, sound: o.sound, make: () => ({})}),

	/**
	 * Crossfade of opaque scenes (15 frames). The incoming fades in; the outgoing stays underneath. `out: true`
	 * also fades the outgoing scene: needed for scenes with transparent parts, and for `exit` on <Scenes>.
	 */
	fade: (o: Base & {ease?: Ease; out?: boolean} = {}): FxTransition => ({
		name: 'fade',
		engine: 'css',
		frames: o.frames ?? 15,
		sound: o.sound,
		make: (c) => ({presentation: asAny(fade({shouldFadeOutExitingScene: o.out ?? false})), timing: lin(at30(o.frames ?? 15, c.fps), o.ease ?? curves.inOut)}),
	}),

	/** The incoming scene pushes the old one out (spring, no overshoot, 20 frames). */
	slide: (o: Base & {direction?: SlideDirection; spring?: boolean} = {}): FxTransition => ({
		name: 'slide',
		engine: 'css',
		frames: o.frames ?? 20,
		sound: o.sound,
		make: (c) => {
			const n = at30(o.frames ?? 20, c.fps);
			return {presentation: asAny(slide({direction: o.direction ?? 'from-right'})), timing: o.spring === false ? lin(n, curves.inOutQuart) : spr(n)};
		},
	}),

	/** A hard-edged wipe reveal (8 directions, 20 frames). */
	wipe: (o: Base & {direction?: WipeDirection; ease?: Ease} = {}): FxTransition => ({
		name: 'wipe',
		engine: 'css',
		frames: o.frames ?? 20,
		sound: o.sound,
		make: (c) => ({presentation: asAny(wipe({direction: o.direction ?? 'from-left'})), timing: lin(at30(o.frames ?? 20, c.fps), o.ease ?? curves.inOut)}),
	}),

	/** A card flip in 3D (26 frames). */
	flip: (o: Base & {direction?: FlipDirection; perspective?: number} = {}): FxTransition => ({
		name: 'flip',
		engine: 'css',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({presentation: asAny(flip({direction: o.direction ?? 'from-right', perspective: o.perspective ?? 1600 * c.unit})), timing: spr(at30(o.frames ?? 26, c.fps))}),
	}),

	/** A clock-hand sweep from 12 o'clock (26 frames). */
	clockWipe: (o: Base = {}): FxTransition => ({
		name: 'clockWipe',
		engine: 'css',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({presentation: asAny(clockWipe({width: c.width, height: c.height})), timing: lin(at30(o.frames ?? 26, c.fps), curves.inOut)}),
	}),

	/** A circle opening from the centre (24 frames). For another origin or a soft edge use maskReveal. */
	iris: (o: Base = {}): FxTransition => ({
		name: 'iris',
		engine: 'css',
		frames: o.frames ?? 24,
		sound: o.sound,
		make: (c) => ({presentation: asAny(iris({width: c.width, height: c.height})), timing: lin(at30(o.frames ?? 24, c.fps), curves.inOut)}),
	}),

	/** Editorial punch cut: the old shot pushes in, a hard cut with a faint flash, the new shot settles (11 frames). */
	pushCut: (o: Base & {flash?: string; flashOpacity?: number} = {}): FxTransition => ({
		name: 'pushCut',
		engine: 'css',
		frames: o.frames ?? 11,
		cutAt: 5 / 11,
		sound: o.sound,
		make: (c) => ({
			presentation: asAny(pushCut({flashColor: o.flash ?? '#f5f2ed', flashOpacity: Math.min(1, Math.max(0, o.flashOpacity ?? 0.2))})),
			timing: lin(at30(o.frames ?? 11, c.fps)),
		}),
	}),

	/** No visual: animate elements yourself with useTransitionProgress() in both scenes (20 frames). */
	choreo: (o: Base = {}): FxTransition => ({
		name: 'choreo',
		engine: 'css',
		frames: o.frames ?? 20,
		sound: o.sound,
		make: (c) => ({presentation: asAny(none()), timing: spr(at30(o.frames ?? 20, c.fps))}),
	}),

	// ------------------------------------------------ shader presentations (HTML-in-canvas + WebGL2)

	/** Whip pan with a real motion blur on both scenes (18 frames, linear: it eases itself). */
	blurSlide: (o: Base & {direction?: SlideDirection; blur?: number} = {}): FxTransition => ({
		name: 'blurSlide',
		engine: 'shader',
		frames: o.frames ?? 18,
		sound: o.sound,
		make: (c) => ({presentation: asAny(blurSlide({direction: o.direction ?? 'from-right', blur: Math.max(0, o.blur ?? 0.5)})), timing: lin(at30(o.frames ?? 18, c.fps))}),
	}),

	/** Zoom out with a turn, zoom in from the other angle, radial blur (22 frames). rotation in radians. */
	zoomBlur: (o: Base & {rotation?: number} = {}): FxTransition => ({
		name: 'zoomBlur',
		engine: 'shader',
		frames: o.frames ?? 22,
		sound: o.sound,
		make: (c) => ({presentation: asAny(zoomBlur({rotation: o.rotation ?? Math.PI / 6})), timing: lin(at30(o.frames ?? 22, c.fps), curves.inOut)}),
	}),

	/** Zoom across a moving centre with a weighted blur (24 frames). */
	crossZoom: (o: Base & {strength?: number} = {}): FxTransition => ({
		name: 'crossZoom',
		engine: 'shader',
		frames: o.frames ?? 24,
		sound: o.sound,
		make: (c) => ({presentation: asAny(crossZoom({strength: o.strength ?? 0.4})), timing: lin(at30(o.frames ?? 24, c.fps), curves.inOut)}),
	}),

	/** A film burn glow through white (30 frames). */
	filmBurn: (o: Base & {seed?: number} = {}): FxTransition => ({
		name: 'filmBurn',
		engine: 'shader',
		frames: o.frames ?? 30,
		sound: o.sound,
		make: (c) => ({presentation: asAny(filmBurn({seed: o.seed ?? 2.31})), timing: lin(at30(o.frames ?? 30, c.fps))}),
	}),

	/** A burning dissolve with a glowing edge (30 frames); edge colours default to the theme. */
	dissolve: (o: Base & {hot?: string; spread?: string} = {}): FxTransition => ({
		name: 'dissolve',
		engine: 'shader',
		frames: o.frames ?? 30,
		sound: o.sound,
		make: (c) => ({
			presentation: asAny(dissolve({hotColor: hex6(o.hot ?? c.theme.colors.highlight), spreadColor: hex6(o.spread ?? c.theme.colors.accent2)})),
			timing: lin(at30(o.frames ?? 30, c.fps)),
		}),
	}),

	/** A directional blur crossfade (20 frames). */
	linearBlur: (o: Base & {intensity?: number} = {}): FxTransition => ({
		name: 'linearBlur',
		engine: 'shader',
		frames: o.frames ?? 20,
		sound: o.sound,
		make: (c) => ({presentation: asAny(linearBlur({intensity: o.intensity ?? 0.1})), timing: lin(at30(o.frames ?? 20, c.fps), curves.inOut)}),
	}),

	/** Zoom and turn through a white bloom (26 frames). rotation in DEGREES. */
	dreamyZoom: (o: Base & {rotation?: number; scale?: number} = {}): FxTransition => ({
		name: 'dreamyZoom',
		engine: 'shader',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({presentation: asAny(dreamyZoom({rotation: o.rotation ?? 6, scale: o.scale ?? 1.2})), timing: lin(at30(o.frames ?? 26, c.fps), curves.inOut)}),
	}),

	/** The scenes swap places in perspective over a reflective floor (30 frames). */
	swap: (o: Base = {}): FxTransition => ({
		name: 'swap',
		engine: 'shader',
		frames: o.frames ?? 30,
		sound: o.sound,
		make: (c) => ({presentation: asAny(swap({})), timing: lin(at30(o.frames ?? 30, c.fps), curves.inOut)}),
	}),

	/** Water ripples from the centre while crossfading (30 frames). */
	ripple: (o: Base & {amplitude?: number; speed?: number} = {}): FxTransition => ({
		name: 'ripple',
		engine: 'shader',
		frames: o.frames ?? 30,
		sound: o.sound,
		make: (c) => ({presentation: asAny(ripple({amplitude: o.amplitude ?? 100, speed: o.speed ?? 50})), timing: lin(at30(o.frames ?? 30, c.fps), curves.inOut)}),
	}),

	/** The scenes warp against each other sideways (26 frames). */
	crosswarp: (o: Base = {}): FxTransition => ({
		name: 'crosswarp',
		engine: 'shader',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({presentation: asAny(crosswarp({})), timing: lin(at30(o.frames ?? 26, c.fps), curves.inOut)}),
	}),

	/** A shaded page turn (32 frames). */
	bookFlip: (o: Base & {direction?: BookFlipDirection} = {}): FxTransition => ({
		name: 'bookFlip',
		engine: 'shader',
		frames: o.frames ?? 32,
		sound: o.sound,
		make: (c) => ({presentation: asAny(bookFlip({direction: o.direction ?? 'from-right'})), timing: lin(at30(o.frames ?? 32, c.fps), curves.inOut)}),
	}),

	/** Zoom toward the viewer, crossfade, zoom back out (26 frames). */
	zoomInOut: (o: Base = {}): FxTransition => ({
		name: 'zoomInOut',
		engine: 'shader',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({presentation: asAny(zoomInOut({})), timing: lin(at30(o.frames ?? 26, c.fps), curves.inOut)}),
	}),

	// ------------------------------------------------ the kit's CSS presentations

	/** Fly through the old scene (scale = 1 / distance, blur) while the new one comes forward (22 frames). */
	zoomThrough: (o: Base & {depth?: number; blur?: number} = {}): FxTransition => ({
		name: 'zoomThrough',
		engine: 'css',
		frames: o.frames ?? 22,
		sound: o.sound,
		make: (c) => ({
			presentation: {component: ZoomThrough, props: {depth: Math.min(0.9, Math.max(0.05, o.depth ?? 0.22)), blur: o.blur ?? 14, unit: c.unit}} as unknown as AnyPresentation,
			timing: lin(at30(o.frames ?? 22, c.fps)),
		}),
	}),

	/** A fast camera whip: both scenes travel together with a directional motion blur (12 frames). */
	whipPan: (o: Base & {direction?: 'left' | 'right' | 'up' | 'down'; blur?: number} = {}): FxTransition => ({
		name: 'whipPan',
		engine: 'css',
		frames: o.frames ?? 12,
		sound: o.sound,
		make: (c) => {
			const n = at30(o.frames ?? 12, c.fps);
			return {
				presentation: {component: WhipPan, props: {direction: o.direction ?? 'left', blur: o.blur ?? 1, frames: n}} as unknown as AnyPresentation,
				timing: lin(n),
			};
		},
	}),

	/** A digital glitch around a hard cut: RGB split and torn slices peak on the cut (12 frames). */
	glitchCut: (o: Base & {seed?: string; intensity?: number} = {}): FxTransition => ({
		name: 'glitchCut',
		engine: 'css',
		frames: o.frames ?? 12,
		cutAt: 0.5,
		sound: o.sound,
		make: (c) => {
			const n = at30(o.frames ?? 12, c.fps);
			return {
				presentation: {component: GlitchCut, props: {seed: o.seed ?? 'glitchcut', intensity: o.intensity ?? 1, unit: c.unit, frames: n}} as unknown as AnyPresentation,
				timing: lin(n),
			};
		},
	}),

	/** A light leak flares over the cut and the scenes change under its peak (36 frames). */
	lightLeakCross: (o: Base & {seed?: number; hue?: number | LeakHue; opacity?: number} = {}): FxTransition => ({
		name: 'lightLeakCross',
		engine: 'css',
		frames: o.frames ?? 36,
		cutAt: 0.42,
		sound: o.sound,
		make: (c) => ({
			presentation: {
				component: LightLeakCross,
				props: {seed: o.seed ?? 3, hue: typeof o.hue === 'number' ? o.hue : LEAK_HUES[o.hue ?? 'warm'], opacity: o.opacity ?? 0.95},
			} as unknown as AnyPresentation,
			timing: lin(at30(o.frames ?? 36, c.fps)),
		}),
	}),

	/** A soft crossfade through blur (24 frames): calm, for photos and moods. */
	blurDissolve: (o: Base & {blur?: number} = {}): FxTransition => ({
		name: 'blurDissolve',
		engine: 'css',
		frames: o.frames ?? 24,
		sound: o.sound,
		make: (c) => ({
			presentation: {component: BlurDissolve, props: {blur: o.blur ?? 18, unit: c.unit}} as unknown as AnyPresentation,
			timing: lin(at30(o.frames ?? 24, c.fps)),
		}),
	}),

	/**
	 * The new scene revealed through a growing shape from a point (`at`, fractions), or a slanted 'diagonal' edge
	 * led by an accent bar. `ring` draws the edge in a colour (true: the theme accent).
	 */
	maskReveal: (o: Base & {shape?: MaskShape | 'diagonal'; at?: readonly [number, number]; feather?: number; ring?: string | boolean; angle?: number} = {}): FxTransition => ({
		name: 'maskReveal',
		engine: 'css',
		frames: o.frames ?? 26,
		sound: o.sound,
		make: (c) => ({
			presentation: {
				component: MaskReveal,
				props: {
					shape: o.shape ?? 'circle',
					at: o.at ?? [0.5, 0.5],
					feather: o.feather ?? 0,
					ring: o.ring === true ? c.theme.colors.accent : typeof o.ring === 'string' ? o.ring : o.shape === 'diagonal' && o.ring !== false ? c.theme.colors.accent : '',
					angle: o.angle ?? 14,
					unit: c.unit,
				},
			} as unknown as AnyPresentation,
			timing: lin(at30(o.frames ?? 26, c.fps)),
		}),
	}),

	// ------------------------------------------------ overlays on a cut (do not shorten the edit)

	/** A flash that peaks on the cut (10 frames). */
	flash: (o: Base & {color?: string; opacity?: number} = {}): FxTransition => ({
		name: 'flash',
		engine: 'overlay',
		frames: o.frames ?? 10,
		sound: o.sound,
		make: () => ({overlay: <Flash color={o.color ?? '#ffffff'} peak={Math.min(1, Math.max(0, o.opacity ?? 0.85))} />}),
	}),

	/** A light leak that blooms over a hard cut (40 frames). */
	leak: (o: Base & {seed?: number; hue?: number | LeakHue; opacity?: number} = {}): FxTransition => ({
		name: 'leak',
		engine: 'overlay',
		frames: o.frames ?? 40,
		sound: o.sound,
		make: () => ({overlay: <LightLeak seed={o.seed ?? 5} hue={o.hue ?? 'warm'} opacity={o.opacity ?? 0.9} />}),
	}),
};

// ---------------------------------------------------------------- Scenes

export type SceneSpec = {
	node: React.ReactNode;
	/** Frames the scene is mounted, overlaps included (as TransitionSeries.Sequence counts them). */
	duration: number;
	/** The transition into the NEXT scene (ignored on the last one; use `exit` there). */
	transition?: FxTransition;
	name?: string;
	/** Mount the scene this many frames early so media can load (passed through to the sequence). */
	premountFor?: number;
};

export type ScenePlan = {
	/** Frames of the whole series: sum of the scenes minus the overlaps. */
	total: number;
	/** Frame each scene starts (overlap included). */
	starts: number[];
	/** Each scene's frames after <Scenes> adds the hidden pre-cut frames of hard-cut transitions. */
	durations: number[];
	/** Frames the content of each scene is delayed (hard-cut transitions). */
	delays: number[];
	/** One entry per joint between scene i and i + 1. */
	joints: {index: number; name: string; engine: TransitionEngine; from: number; frames: number; cut: number}[];
	/** Broken timing rules: <Scenes> throws with these. */
	problems: string[];
	/** Legal but usually unintended (a scene that is never on screen on its own). */
	warnings: string[];
};

const overlapFrames = (t: FxTransition | undefined, fps: number) => (t && (t.engine === 'css' || t.engine === 'shader') ? at30(t.frames, fps) : 0);

/**
 * On 4.0.528 a shader transition gets no picture of a scene that ENTERED with a CSS transition (the entering CSS
 * presentation never captures it), so it plays as a hard cut. <Scenes> splits such a scene in two sequences
 * (CSS in, then a seamless cut, then shader out), which needs the scene to hold both transitions.
 */
const needsSplit = (before: FxTransition | undefined, after: FxTransition | undefined) => before?.engine === 'css' && after?.engine === 'shader';

/** The timing of a scene list: total length, where each scene starts, where each cut is, and what is wrong. */
export const planScenes = (scenes: SceneSpec[], fps: number, o: {enter?: FxTransition; exit?: FxTransition} = {}): ScenePlan => {
	const n = scenes.length;
	const problems: string[] = [];
	const warnings: string[] = [];
	if (n === 0) {
		return {total: 0, starts: [], durations: [], delays: [], joints: [], problems: ['there are no scenes'], warnings};
	}
	const between = scenes.map((s, i) => (i < n - 1 ? s.transition : undefined));
	const L = between.map((t) => overlapFrames(t, fps));
	const delays = scenes.map((_, i) => {
		const t = i === 0 ? o.enter : between[i - 1];
		const len = i === 0 ? overlapFrames(o.enter, fps) : L[i - 1];
		return t?.cutAt ? Math.round(len * Math.min(1, Math.max(0, t.cutAt))) : 0;
	});
	const durations = scenes.map((s, i) => Math.round(s.duration) + delays[i]);
	const starts: number[] = [];
	let at = 0;
	for (let i = 0; i < n; i++) {
		starts.push(at);
		at += durations[i] - (i < n - 1 ? L[i] : 0);
	}
	const total = starts[n - 1] + durations[n - 1];
	const lenIn = (i: number) => (i === 0 ? overlapFrames(o.enter, fps) : L[i - 1]);
	const lenOut = (i: number) => (i === n - 1 ? overlapFrames(o.exit, fps) : L[i]);
	const joints: ScenePlan['joints'] = [];
	for (let i = 0; i < n; i++) {
		const label = scenes[i].name ? `scene ${i} (${scenes[i].name})` : `scene ${i}`;
		if (!(scenes[i].duration > 0)) {
			problems.push(`${label} has no length`);
		}
		if (durations[i] < lenIn(i)) {
			problems.push(`${label} is ${durations[i]} frames, shorter than the ${lenIn(i)}-frame transition before it`);
		}
		if (durations[i] < lenOut(i)) {
			problems.push(`${label} is ${durations[i]} frames, shorter than the ${lenOut(i)}-frame transition after it`);
		}
		const before = i === 0 ? o.enter : between[i - 1];
		const after = i === n - 1 ? o.exit : between[i];
		if (needsSplit(before, after) && durations[i] < lenIn(i) + lenOut(i)) {
			problems.push(
				`${label} enters with a CSS transition and leaves with a shader one, so it must hold both (${lenIn(i) + lenOut(i)} frames, it has ${durations[i]}): lengthen it, or make both transitions shader or both CSS`,
			);
		} else if (durations[i] - lenIn(i) - lenOut(i) < 0 && problems.length === 0) {
			warnings.push(`${label} is never on screen on its own (its transitions overlap)`);
		}
		const t = between[i];
		if (t && i < n - 1) {
			const len = L[i];
			const from = starts[i + 1];
			if (t.engine === 'overlay') {
				const ov = at30(t.frames, fps);
				const half = ov / 2;
				if (half > durations[i] || half > durations[i + 1]) {
					problems.push(`the ${ov}-frame ${t.name} overlay after ${label} needs ${Math.ceil(half)} frames on both sides of the cut`);
				}
				const cut = starts[i + 1];
				joints.push({index: i, name: t.name, engine: t.engine, from: cut - Math.round(half), frames: ov, cut});
			} else {
				joints.push({index: i, name: t.name, engine: t.engine, from, frames: len, cut: from + Math.round(len * (t.cutAt ?? 0.5))});
			}
		}
	}
	return {total, starts, durations, delays, joints, problems, warnings};
};

/** Frames of a scene list (use it for the Composition's durationInFrames). */
export const scenesLength = (scenes: SceneSpec[], fps: number, o: {enter?: FxTransition; exit?: FxTransition} = {}): number =>
	planScenes(scenes, fps, o).total;

export type ScenesProps = {
	scenes: SceneSpec[];
	/** A transition into the first scene (it animates in from nothing). */
	enter?: FxTransition;
	/** A transition out of the last scene. */
	exit?: FxTransition;
	name?: string;
};

/**
 * A TransitionSeries from a list: checks the timing rules first (each scene at least as long as each neighbouring
 * transition, overlays with room on both sides) and throws a readable error instead of a mid-render one. Scenes
 * next to a shader transition are marked so looks there use their css engine.
 */
export const Scenes: React.FC<ScenesProps> = ({scenes, enter, exit, name}) => {
	const {width, height, fps} = useVideoConfig();
	const theme = useTheme();
	const nest = useFxNest();
	const plan = planScenes(scenes, fps, {enter, exit});
	if (plan.problems.length > 0) {
		throw new Error(`<Scenes>: ${plan.problems.join('; ')}.`);
	}
	const n = scenes.length;
	const between = scenes.map((s, i) => (i < n - 1 ? s.transition : undefined));
	const all = [enter, ...between, exit];
	if (nest.canvas && all.some((t) => t?.engine === 'shader')) {
		throw new Error(`<Scenes>: shader transitions cannot run ${nest.canvas}, because HTML-in-canvas cannot be nested. Use CSS transitions here, or put the look inside each scene.`);
	}
	const ctx: TransitionContext = {width, height, fps, unit: Math.min(width, height) / 1080, theme};
	const children: React.ReactNode[] = [];
	const addTransition = (t: FxTransition | undefined, key: string) => {
		if (!t || t.engine === 'cut' || t.engine === 'overlay') {
			return;
		}
		const made = t.make(ctx);
		if (made.timing) {
			children.push(<TransitionSeries.Transition key={key} timing={made.timing} presentation={made.presentation} />);
		}
	};
	addTransition(enter, 'enter');
	scenes.forEach((s, i) => {
		const before = i === 0 ? enter : between[i - 1];
		const after = i === n - 1 ? exit : between[i];
		let node = s.node;
		if (plan.delays[i] > 0) {
			node = (
				<Sequence from={plan.delays[i]} name="after the cut">
					{node}
				</Sequence>
			);
		}
		if (before?.engine === 'shader' || after?.engine === 'shader') {
			node = <FxNestContext.Provider value={{canvas: 'in a scene next to a shader transition'}}>{node}</FxNestContext.Provider>;
		}
		const extra = s.premountFor ? ({premountFor: s.premountFor} as object) : {};
		if (needsSplit(before, after)) {
			// Part A plays the whole scene (so its clock and length stay true) and hides itself when part B, a
			// copy laid over its last frames, takes over; the shader transition then captures part B.
			const tail = at30((after as FxTransition).frames, fps);
			const head = plan.durations[i] - tail;
			children.push(
				<TransitionSeries.Sequence key={`s${i}a`} durationInFrames={plan.durations[i]} name={s.name} {...extra}>
					<HideFrom frame={head}>{node}</HideFrom>
				</TransitionSeries.Sequence>,
				<TransitionSeries.Sequence
					key={`s${i}b`}
					durationInFrames={tail}
					offset={-tail}
					name={s.name ? `${s.name} (shader out)` : 'shader out'}
					{...({premountFor: Math.max(s.premountFor ?? 0, Math.min(30, head))} as object)}
				>
					<Sequence from={-head} name="continued">
						{node}
					</Sequence>
				</TransitionSeries.Sequence>,
			);
		} else {
			children.push(
				<TransitionSeries.Sequence key={`s${i}`} durationInFrames={plan.durations[i]} name={s.name} {...extra}>
					{node}
				</TransitionSeries.Sequence>,
			);
		}
		const t = between[i];
		if (t && t.engine === 'overlay') {
			children.push(
				<TransitionSeries.Overlay key={`o${i}`} durationInFrames={at30(t.frames, fps)}>
					{t.make(ctx).overlay}
				</TransitionSeries.Overlay>,
			);
		} else {
			addTransition(t, `t${i}`);
		}
	});
	addTransition(exit, 'exit');
	const sounds = plan.joints
		.map((j) => ({j, t: between[j.index]}))
		.filter(({t}) => t?.sound)
		.map(({j, t}) => {
			const snd = t?.sound as TransitionSound;
			const lead = snd.lead ?? j.cut - j.from;
			return (
				<Sequence key={`snd${j.index}`} from={Math.max(0, j.cut - lead)} name={`sound: ${j.name}`}>
					<Audio src={snd.src} volume={snd.volume ?? 0.6} />
				</Sequence>
			);
		});
	return (
		<>
			<TransitionSeries name={name ?? '<Scenes>'}>{children}</TransitionSeries>
			{sounds}
		</>
	);
};
