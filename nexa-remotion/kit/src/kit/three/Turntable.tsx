// <Turntable>: turns any 3D child about Y with an eased move, bobs it gently, and gives it an entrance and an
// exit. <ProductSpin> is a Turntable tuned for a product hero shot, with a soft contact shadow under it.
import type {ThreeElements} from '@react-three/fiber';
import React from 'react';
import {useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {at30, curves, useStage, type Ease} from '../core';
import {ramp, springAt} from '../motion';
import {useScene3D} from './Scene3D';
import {blobTexture} from './textures';
import {deg, type Vec3} from './util';

export type TurntableEnter = 'rise' | 'drop' | 'pop' | 'spin' | 'none';
export type TurntableExit = 'sink' | 'lift' | 'shrink' | 'none';

export type TurntableProps = {
	children?: React.ReactNode;
	/** Y rotation at the start of the turn, degrees. */
	from?: number;
	/** Y rotation at the end of the turn, degrees. */
	to?: number;
	delay?: number;
	/** Frames of the turn; default: to the end of the Sequence. */
	duration?: number;
	/** In-out by default; curves.linear for a constant spin. */
	ease?: Ease;
	/** Forward tilt (X), degrees. */
	tilt?: number;
	/** Bob amplitude in px at 1080 (0 for none). */
	float?: number;
	/** Seconds per bob. */
	floatPeriod?: number;
	enter?: TurntableEnter;
	enterDuration?: number;
	out?: TurntableExit;
	outDuration?: number;
	position?: Vec3;
	scale?: number;
};

/** Where a Turntable's child is this frame: shared with ProductSpin's shadow. */
const useTurntableState = (p: TurntableProps) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useStage();
	const s = useScene3D();
	const {
		from = -30,
		to = 330,
		delay = 0,
		duration,
		ease = curves.inOut,
		float = 10,
		floatPeriod = 3.4,
		enter = 'rise',
		enterDuration,
		out = 'none',
		outDuration,
	} = p;
	const turnFrames = duration ?? Math.max(1, durationInFrames - delay);
	const angle = from + (to - from) * (Number.isFinite(turnFrames) ? ramp(frame, delay, turnFrames, ease) : 0);
	const eDur = enterDuration ?? at30(enter === 'pop' ? 24 : 34, fps);
	let y = 0;
	let scale = 1;
	let spin = 0;
	if (enter === 'rise') {
		const k = ramp(frame, delay, eDur, curves.out);
		y -= (1 - k) * s.visible.h * 0.9;
		spin -= (1 - k) * 50;
	} else if (enter === 'drop') {
		const k = springAt(frame, fps, {delay, config: 'settle', durationInFrames: eDur});
		y += (1 - k) * s.visible.h * 0.9;
	} else if (enter === 'pop') {
		const k = springAt(frame, fps, {delay, config: 'pop', durationInFrames: eDur});
		scale *= Math.max(0.001, k);
		spin -= (1 - Math.min(1, k)) * 90;
	} else if (enter === 'spin') {
		const k = ramp(frame, delay, eDur, curves.out);
		spin -= (1 - k) * 360;
		scale *= 0.001 + 0.999 * Math.min(1, k * 2.5);
	}
	const oDur = outDuration ?? at30(18, fps);
	const q = out === 'none' || !Number.isFinite(durationInFrames) ? 0 : ramp(frame, durationInFrames - 1 - oDur, oDur, curves.in);
	if (out === 'sink') {
		y -= q * s.visible.h * 0.9;
	} else if (out === 'lift') {
		y += q * s.visible.h * 0.9;
	} else if (out === 'shrink') {
		scale *= Math.max(0.001, 1 - q);
		spin += q * 120;
	}
	const settle = ramp(frame, delay, fps * 1.2, curves.sine);
	const bob = float ? s.px(float) * Math.sin((2 * Math.PI * frame) / (fps * floatPeriod)) * settle : 0;
	return {angle: angle + spin, y, bob, scale};
};

export const Turntable: React.FC<TurntableProps> = (props) => {
	const {children, tilt = 0, position = [0, 0, 0], scale = 1} = props;
	const st = useTurntableState(props);
	return (
		<group position={[position[0], position[1] + st.y + st.bob, position[2]]} scale={scale * st.scale}>
			<group rotation={[deg(tilt), deg(st.angle), 0]}>{children}</group>
		</group>
	);
};

export type ContactShadowProps = Omit<ThreeElements['mesh'], 'scale'> & {
	/** Width on the floor in world units. */
	width?: number;
	/** Depth on the floor; default 45% of the width. */
	depth?: number;
	opacity?: number;
	color?: string;
	/** How far the object has lifted (world units): the shadow shrinks and fades as it rises. */
	lift?: number;
};

/** A soft blob shadow on the floor (no shadow maps): grounds a product in any light. */
export const ContactShadow: React.FC<ContactShadowProps> = ({width = 2.4, depth, opacity, color = '#000000', lift = 0, ...mesh}) => {
	const s = useScene3D();
	const o = (opacity ?? (s.dark ? 0.6 : 0.34)) * Math.max(0, 1 - Math.max(0, lift) * 0.35);
	const k = 1 + Math.max(0, lift) * 0.18;
	return (
		<mesh rotation={[-Math.PI / 2, 0, 0]} scale={[width * k, (depth ?? width * 0.45) * k, 1]} renderOrder={-1} {...mesh}>
			<planeGeometry args={[1, 1]} />
			<meshBasicMaterial map={blobTexture()} color={color} transparent opacity={o} depthWrite={false} toneMapped={false} side={THREE.DoubleSide} />
		</mesh>
	);
};

export type ProductSpinProps = TurntableProps & {
	/** World y of the floor under the product; default a little below the frame's centre. */
	floor?: number;
	/** Shadow width in world units (false: no shadow). */
	shadow?: number | false;
};

/**
 * A product hero turn: a gentle eased swing (-28 to 28 degrees by default), a rise from below the frame, a slow bob
 * and a contact shadow that breathes with the bob.
 */
export const ProductSpin: React.FC<ProductSpinProps> = ({floor, shadow = 2.2, ...props}) => {
	const s = useScene3D();
	const merged: TurntableProps = {from: -28, to: 28, enter: 'rise', float: 12, ...props};
	const st = useTurntableState(merged);
	const pos = merged.position ?? [0, 0, 0];
	const floorY = floor ?? -s.visible.h * 0.36;
	const lift = st.bob + st.y;
	return (
		<>
			<Turntable {...merged} />
			{shadow === false ? null : (
				<ContactShadow position={[pos[0], floorY, pos[2]]} width={shadow * st.scale} lift={Math.max(0, lift) + Math.max(0, -st.y) * 2} />
			)}
		</>
	);
};
