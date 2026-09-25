// A camera over a world larger than the frame, parallax layers, a slow push-in and a shake. Put the movement on
// the camera or the ground, not on text that is being read.
import React, {createContext, useContext} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {curves, useStage, type Ease} from '../core';
import {pulse, ramp, track, wiggle} from './helpers';

export type CameraKey = {at: number; x?: number; y?: number; zoom?: number; rotate?: number};

type CameraState = {x: number; y: number; zoom: number; rotate: number; x0: number; y0: number};

const CameraContext = createContext<CameraState | null>(null);

/** The camera's current focus and zoom, for layers that react to it. */
export const useCamera = () => useContext(CameraContext);

/**
 * Children are laid out in world coordinates (px); the camera puts the world point (x, y) in the middle of the
 * frame at `zoom`, moving between keys (ease in-out by default, one curve or one per segment). A key may leave
 * values out: they carry over from the key before. Repeat a key on a later frame to hold.
 */
export const Camera: React.FC<{
	keys: CameraKey[];
	ease?: Ease | Ease[];
	world?: {width: number; height: number};
	children: React.ReactNode;
	style?: React.CSSProperties;
}> = ({keys, ease = curves.inOut, world, children, style}) => {
	const frame = useCurrentFrame();
	const {width, height} = useStage();
	const W = world?.width ?? width;
	const H = world?.height ?? height;
	const filled: Required<CameraKey>[] = [];
	for (const k of [...keys].sort((a, b) => a.at - b.at)) {
		const prev = filled[filled.length - 1] ?? {at: 0, x: W / 2, y: H / 2, zoom: 1, rotate: 0};
		filled.push({at: k.at, x: k.x ?? prev.x, y: k.y ?? prev.y, zoom: k.zoom ?? prev.zoom, rotate: k.rotate ?? prev.rotate});
	}
	const frames = filled.map((k) => k.at);
	const val = (pick: (k: Required<CameraKey>) => number) =>
		filled.length === 1 ? pick(filled[0]) : track(frame, frames, filled.map(pick), ease);
	const x = val((k) => k.x);
	const y = val((k) => k.y);
	const zoom = val((k) => k.zoom);
	const rotate = val((k) => k.rotate);
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<div
				style={{
					position: 'absolute',
					left: 0,
					top: 0,
					width: W,
					height: H,
					transformOrigin: `${x}px ${y}px`,
					transform: `translate(${width / 2 - x}px, ${height / 2 - y}px) rotate(${rotate}deg) scale(${zoom})`,
				}}
			>
				<CameraContext.Provider value={{x, y, zoom, rotate, x0: filled[0]?.x ?? W / 2, y0: filled[0]?.y ?? H / 2}}>
					{children}
				</CameraContext.Provider>
			</div>
		</AbsoluteFill>
	);
};

/** A layer inside a Camera that moves at `depth` times the camera's speed: under 1 is farther, over 1 nearer. */
export const Parallax: React.FC<{depth: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
	depth,
	children,
	style,
}) => {
	const cam = useCamera();
	const dx = cam ? (cam.x - cam.x0) * (1 - depth) : 0;
	const dy = cam ? (cam.y - cam.y0) * (1 - depth) : 0;
	return <div style={{position: 'absolute', inset: 0, translate: `${dx}px ${dy}px`, ...style}}>{children}</div>;
};

/** A slow push over the whole Sequence (scale 1 to 1 + amount, and an optional lift): the life of a held shot. */
export const PushIn: React.FC<{
	amount?: number;
	lift?: number; // px at 1080
	origin?: string;
	ease?: Ease;
	children: React.ReactNode;
}> = ({amount = 0.035, lift = 0, origin = '50% 50%', ease = curves.sine, children}) => {
	const frame = useCurrentFrame();
	const {durationInFrames, unit} = useStage();
	const t = Number.isFinite(durationInFrames) ? ramp(frame, 0, durationInFrames, ease) : 0;
	return (
		<AbsoluteFill style={{scale: `${1 + amount * t}`, translate: `0px ${-lift * unit * t}px`, transformOrigin: origin}}>
			{children}
		</AbsoluteFill>
	);
};

/** A camera shake over [from, from + duration] that eases in and out: impacts, drops, bass hits. */
export const Shake: React.FC<{
	from?: number;
	duration?: number;
	amp?: number; // px at 1080
	rotate?: number; // degrees
	freq?: number; // Hz
	children: React.ReactNode;
}> = ({from = 0, duration = 12, amp = 14, rotate = 0.8, freq = 9, children}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const env = pulse(frame, from, duration);
	return (
		<AbsoluteFill
			style={{
				translate: `${wiggle(frame, fps, freq, 11) * amp * unit * env}px ${wiggle(frame, fps, freq, 12) * amp * unit * env}px`,
				rotate: `${wiggle(frame, fps, freq, 13) * rotate * env}deg`,
			}}
		>
			{children}
		</AbsoluteFill>
	);
};

/**
 * A zoom about a fixed point: the point (x, y) in px stays exactly where it is while everything scales around it
 * (a UI punch-in on the button being clicked). Scale goes `from` to `to` over [at, at + duration], and back when
 * `backAt` is set.
 */
export const ZoomAt: React.FC<{
	x: number;
	y: number;
	from?: number;
	to?: number;
	at?: number;
	duration?: number;
	backAt?: number;
	ease?: Ease;
	children: React.ReactNode;
}> = ({x, y, from = 1, to = 1.6, at = 0, duration = 18, backAt, ease = curves.inOut, children}) => {
	const frame = useCurrentFrame();
	const t = ramp(frame, at, duration, ease) - (backAt === undefined ? 0 : ramp(frame, backAt, duration, ease));
	return (
		<AbsoluteFill style={{transformOrigin: `${x}px ${y}px`, scale: `${from + (to - from) * t}`}}>{children}</AbsoluteFill>
	);
};
