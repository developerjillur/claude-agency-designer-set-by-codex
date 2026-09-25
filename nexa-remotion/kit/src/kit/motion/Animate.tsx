// <Animate>: an entrance and an optional exit for anything. The exit plays at the end of the enclosing
// <Sequence> (or at `outAt`), so a temporary element placed in a Sequence arrives and leaves on its own.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from './helpers';

export type Reveal =
	| 'none'
	| 'fade'
	| 'rise' // in from below; out upwards
	| 'drop' // in from above; out downwards
	| 'left' // in from the left; out to the left
	| 'right'
	| 'pop' // small scale-up with overshoot
	| 'grow'
	| 'zoom' // settles from slightly bigger
	| 'blur' // blur and fade with a small rise
	| 'mask' // slides up inside its own box (titles): no fade
	| 'maskDown'
	| 'wipe' // clip from the left edge to the right
	| 'wipeLeft'
	| 'wipeUp'
	| 'wipeDown'
	| 'iris' // a circle opening from the centre
	| 'flip' // folds down around its top edge
	| 'swing';

type Pose = {opacity: number; x: number; y: number; scale: number; rotate: number; blur: number; clip?: string; innerY?: number; flip: number};

const REST: Pose = {opacity: 1, x: 0, y: 0, scale: 1, rotate: 0, blur: 0, flip: 0};

// t = 0 at rest, 1 fully hidden. Exits keep travelling the way things move (a rise leaves upwards).
const pose = (kind: Reveal, t: number, d: number, exit: boolean): Pose => {
	if (t <= 0 || kind === 'none') {
		return REST;
	}
	const s = exit ? -1 : 1;
	const p = 100 * t;
	switch (kind) {
		case 'fade':
			return {...REST, opacity: 1 - t};
		case 'rise':
			return {...REST, opacity: 1 - t, y: s * d * t};
		case 'drop':
			return {...REST, opacity: 1 - t, y: -s * d * t};
		case 'left':
			return {...REST, opacity: 1 - t, x: -d * t};
		case 'right':
			return {...REST, opacity: 1 - t, x: d * t};
		case 'pop':
			return {...REST, opacity: Math.max(0, 1 - t * 1.6), scale: 1 - 0.14 * t};
		case 'grow':
			return {...REST, opacity: 1 - t, scale: 1 - 0.4 * t};
		case 'zoom':
			return {...REST, opacity: 1 - t, scale: 1 + 0.18 * t};
		case 'blur':
			return {...REST, opacity: 1 - t, blur: 14 * t, scale: 1 + 0.03 * t, y: s * d * 0.5 * t};
		case 'mask':
			return {...REST, innerY: s * t};
		case 'maskDown':
			return {...REST, innerY: -s * t};
		case 'wipe':
			return {...REST, clip: exit ? `inset(0 0 0 ${p}%)` : `inset(0 ${p}% 0 0)`};
		case 'wipeLeft':
			return {...REST, clip: exit ? `inset(0 ${p}% 0 0)` : `inset(0 0 0 ${p}%)`};
		case 'wipeDown':
			return {...REST, clip: exit ? `inset(${p}% 0 0 0)` : `inset(0 0 ${p}% 0)`};
		case 'wipeUp':
			return {...REST, clip: exit ? `inset(0 0 ${p}% 0)` : `inset(${p}% 0 0 0)`};
		case 'iris':
			return {...REST, clip: `circle(${(1 - t) * 75}% at 50% 50%)`};
		case 'flip':
			return {...REST, opacity: 1 - t, flip: s * 90 * t};
		case 'swing':
			return {...REST, opacity: 1 - t, rotate: -8 * s * t, y: s * d * 0.6 * t};
		default:
			return REST;
	}
};

const isWipe = (k: Reveal) => k.startsWith('wipe') || k === 'iris';
const MASK_TOP = '0.16em';
const MASK_BOTTOM = '0.26em';
const isMask = (k: Reveal) => k === 'mask' || k === 'maskDown';

export type AnimateProps = {
	in?: Reveal; // default: the theme's entrance
	out?: Reveal; // default: none (cut on a settled frame)
	delay?: number; // frames before the entrance starts
	duration?: number; // entrance frames (default: the theme's, scaled to the fps)
	outDuration?: number;
	outAt?: number; // local frame the exit starts (default: it ends on the last frame of the Sequence)
	distance?: number; // px at 1080 for rises, drops and slides
	ease?: Ease;
	outEase?: Ease;
	origin?: string; // transform-origin (pops and grows): 'center', '50% 100%' for grounded things
	inline?: boolean; // inline-block (words in a line) instead of block
	style?: React.CSSProperties; // on the outer box (position it here)
	innerStyle?: React.CSSProperties;
	children?: React.ReactNode;
};

export const Animate: React.FC<AnimateProps> = ({
	in: inKind,
	out: outKind = 'none',
	delay = 0,
	duration,
	outDuration,
	outAt,
	distance,
	ease,
	outEase,
	origin = 'center',
	inline = false,
	style,
	innerStyle,
	children,
}) => {
	const frame = useCurrentFrame();
	const theme = useTheme();
	const {fps, unit, durationInFrames} = useStage();
	const kIn: Reveal = inKind ?? theme.motion.enter;
	const inDur = duration ?? at30(theme.motion.enterFrames, fps);
	const outDur = outDuration ?? at30(theme.motion.exitFrames, fps);
	const d = (distance ?? theme.motion.distance) * unit;
	const inEase =
		ease ?? (kIn === 'pop' ? curves.outBack : isWipe(kIn) ? curves.inOut : curves[theme.motion.curve]);
	const exitEase = outEase ?? (isWipe(outKind) ? curves.inOut : curves.in);
	// the exit's fade runs on an even curve of its own: on the motion's ease-in nearly all the opacity went in the
	// last three frames, and a fade-out read as a blink
	const fadeEase = outEase ?? (isWipe(outKind) ? curves.inOut : curves.sine);

	const p = ramp(frame, delay, inDur, inEase);
	// the exit ends on the last frame of the Sequence, so nothing is left half-visible at the cut
	const exitStart = outAt ?? durationInFrames - 1 - outDur;
	const q = outKind !== 'none' && Number.isFinite(exitStart) ? ramp(frame, exitStart, outDur, exitEase) : 0;
	const qFade = outKind !== 'none' && Number.isFinite(exitStart) ? ramp(frame, exitStart, outDur, fadeEase) : 0;

	const a = pose(kIn, 1 - p, d, false);
	const b = pose(outKind, q, d, true);
	const bOpacity = pose(outKind, qFade, d, true).opacity;
	const clip = q > 0 && b.clip ? b.clip : a.clip;
	const innerY = q > 0 && b.innerY !== undefined ? b.innerY : a.innerY ?? 0;
	const masked = isMask(kIn) || isMask(outKind);
	const blur = Math.max(a.blur, b.blur) * unit;
	const flip = a.flip + b.flip;
	const Tag = inline ? 'span' : 'div';

	return (
		<Tag
			style={{
				display: inline ? 'inline-block' : 'block',
				position: 'relative',
				overflow: masked ? 'hidden' : undefined,
				clipPath: clip,
				verticalAlign: inline ? 'top' : undefined,
				// room for ascenders, descenders and Bangla vowel marks inside a mask, without moving the layout
				...(masked ? {paddingTop: MASK_TOP, paddingBottom: MASK_BOTTOM, marginTop: `-${MASK_TOP}`, marginBottom: `-${MASK_BOTTOM}`} : null),
				...style,
			}}
		>
			<Tag
				style={{
					display: inline ? 'inline-block' : 'block',
					opacity: a.opacity * bOpacity,
					// a masked element travels its own height plus both paddings, so no glyph peeks through at rest
					translate: `${a.x + b.x}px calc(${innerY} * (100% + ${MASK_TOP} + ${MASK_BOTTOM} + 0.04em) + ${a.y + b.y}px)`,
					scale: `${a.scale * b.scale}`,
					rotate: `${a.rotate + b.rotate}deg`,
					transform: flip ? `perspective(${1400 * unit}px) rotateX(${flip}deg)` : undefined,
					transformOrigin: flip ? '50% 0%' : origin,
					filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
					...innerStyle,
				}}
			>
				{children}
			</Tag>
		</Tag>
	);
};
