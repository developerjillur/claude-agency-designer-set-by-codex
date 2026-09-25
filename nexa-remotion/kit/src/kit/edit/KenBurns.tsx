// <KenBurns>: a slow push and pan over a still (or any full-frame content) from one framing rectangle to another.
// The picture is laid out to cover the frame, so rectangles are fractions of what fills the frame: no image
// metadata needed. Zoom moves exponentially (even speed to the eye) while the centre moves in a straight line.
import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame} from 'remotion';
import {curves, useStage, type Ease} from '../core';
import {ramp} from '../motion';

/** A framing: top-left corner and width as fractions of the picture (0 to 1); the height follows the frame. */
export type KenBurnsRect = {x: number; y: number; w: number};

export type KenBurnsMove = 'in' | 'out' | 'left' | 'right' | 'up' | 'down';

export type KenBurnsProps = {
	/** An image; or leave it out and pass children (a Clip, a scene) to move those instead. */
	src?: string;
	children?: React.ReactNode;
	/** A preset move when `from` and `to` are not given. */
	move?: KenBurnsMove;
	/** How much closer the tight end of a preset is: 0.15 = 15 %. Keep it between 0.08 and 0.25. */
	amount?: number;
	/** Where a preset pushes in to or pans across, as fractions of the picture: [x, y]. */
	focus?: readonly [number, number];
	from?: KenBurnsRect;
	to?: KenBurnsRect;
	/** Frames before the move starts and its length (default: the rest of the Sequence). */
	delay?: number;
	duration?: number;
	/** Default: a gentle sine in-out, so the move starts and lands without a bump. Use curves.linear across cuts. */
	ease?: Ease;
	/** Image styles (a grade, a filter). */
	imgStyle?: React.CSSProperties;
	style?: React.CSSProperties;
};

const clampRect = (r: KenBurnsRect): KenBurnsRect => {
	const w = Math.min(1, Math.max(0.05, r.w));
	return {w, x: Math.min(1 - w, Math.max(0, r.x)), y: Math.min(1 - w, Math.max(0, r.y))};
};

const centred = (cx: number, cy: number, w: number): KenBurnsRect => clampRect({x: cx - w / 2, y: cy - w / 2, w});

/** The start and end framings of a preset move. */
export const kenBurnsPreset = (
	move: KenBurnsMove,
	amount = 0.15,
	focus: readonly [number, number] = [0.5, 0.5],
): [KenBurnsRect, KenBurnsRect] => {
	const tight = 1 / (1 + Math.max(0, amount));
	const [fx, fy] = focus;
	switch (move) {
		case 'out':
			return [centred(fx, fy, tight), {x: 0, y: 0, w: 1}];
		case 'left':
			return [centred(1, fy, tight), centred(0, fy, tight)];
		case 'right':
			return [centred(0, fy, tight), centred(1, fy, tight)];
		case 'up':
			return [centred(fx, 1, tight), centred(fx, 0, tight)];
		case 'down':
			return [centred(fx, 0, tight), centred(fx, 1, tight)];
		case 'in':
		default:
			return [{x: 0, y: 0, w: 1}, centred(fx, fy, tight)];
	}
};

/** The framing at progress t (0 to 1) between two rectangles. */
export const kenBurnsAt = (a: KenBurnsRect, b: KenBurnsRect, t: number): KenBurnsRect => {
	const w = a.w * Math.pow(b.w / a.w, t);
	const cx = a.x + a.w / 2 + (b.x + b.w / 2 - a.x - a.w / 2) * t;
	const cy = a.y + a.w / 2 + (b.y + b.w / 2 - a.y - a.w / 2) * t;
	return centred(cx, cy, w);
};

export const KenBurns: React.FC<KenBurnsProps> = ({
	src,
	children,
	move = 'in',
	amount = 0.15,
	focus = [0.5, 0.5],
	from,
	to,
	delay = 0,
	duration,
	ease = curves.sine,
	imgStyle,
	style,
}) => {
	const frame = useCurrentFrame();
	const {width, height, durationInFrames} = useStage();
	const [pa, pb] = kenBurnsPreset(move, amount, focus);
	const a = clampRect(from ?? pa);
	const b = clampRect(to ?? pb);
	const len = duration ?? (Number.isFinite(durationInFrames) ? durationInFrames - delay : 150);
	const t = ramp(frame, delay, Math.max(1, len), ease);
	const r = kenBurnsAt(a, b, t);
	const s = 1 / r.w;
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<AbsoluteFill style={{transformOrigin: '0 0', scale: `${s}`, translate: `${-r.x * width * s}px ${-r.y * height * s}px`}}>
				{src ? <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover', ...imgStyle}} /> : children}
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
