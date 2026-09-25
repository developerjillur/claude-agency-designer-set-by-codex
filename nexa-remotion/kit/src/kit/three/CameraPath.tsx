// <CameraPath>: keyframed camera moves inside a Scene3D. Keys give a position (or an orbit around the target),
// the target, the field of view and a roll; missing values carry over from the key before. 'keys' mode eases
// each segment (the camera settles on every key); 'glide' runs one eased pass through a smooth spline.
import {useThree} from '@react-three/fiber';
import React, {useLayoutEffect} from 'react';
import {useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {curves, useStage, type Ease} from '../core';
import {ramp, track} from '../motion';
import {applyCameraPose, useScene3D, type CameraPose} from './Scene3D';
import {noise, orbitPoint, type Vec3} from './util';

export type CameraOrbit = {azimuth?: number; elevation?: number; distance?: number};

export type CameraKey3D = {
	/** Frame (local to the Sequence). */
	at: number;
	/** World position of the camera. */
	position?: Vec3;
	/** Or a place on a sphere around the target: degrees, degrees, world units. */
	orbit?: CameraOrbit;
	target?: Vec3;
	/** Vertical field of view, degrees. */
	fov?: number;
	/** Roll, degrees. */
	roll?: number;
	/** Orbit distance as a multiple of the scene's base distance (format-independent; 0.9 = 10% closer). */
	dolly?: number;
	/** Slide camera and target together in the image plane, world units [right, up] (a truck or pedestal). */
	shift?: [number, number];
};

export type CameraPathProps = {
	keys: CameraKey3D[];
	/** One curve for every segment or one per segment ('keys' mode); one curve for the whole pass ('glide'). */
	ease?: Ease | Ease[];
	mode?: 'keys' | 'glide';
	/** Handheld drift in px at 1080 (0 for a locked-off camera; 4 to 10 feels alive). */
	handheld?: number;
	handheldFreq?: number;
	seed?: string;
};

type Full = {at: number; target: Vec3; fov: number; roll: number; position: Vec3; orbit: Required<CameraOrbit> | null; shift: [number, number]};

const toOrbit = (pos: Vec3, target: Vec3): Required<CameraOrbit> => {
	const d = new THREE.Vector3(pos[0] - target[0], pos[1] - target[1], pos[2] - target[2]);
	const distance = d.length() || 1;
	return {
		azimuth: (Math.atan2(d.x, d.z) * 180) / Math.PI,
		elevation: (Math.asin(Math.max(-1, Math.min(1, d.y / distance))) * 180) / Math.PI,
		distance,
	};
};

/** Slides camera and target together along the image plane's right and up axes. */
const withShift = (pose: CameraPose, [sx, sy]: [number, number]): CameraPose => {
	if (!sx && !sy) {
		return pose;
	}
	const pos = new THREE.Vector3(...pose.position);
	const tgt = new THREE.Vector3(...pose.target);
	const fwd = tgt.clone().sub(pos).normalize();
	const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
	const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
	const d = right.multiplyScalar(sx).add(up.multiplyScalar(sy));
	return {...pose, position: [pos.x + d.x, pos.y + d.y, pos.z + d.z], target: [tgt.x + d.x, tgt.y + d.y, tgt.z + d.z]};
};

/** The camera pose at `frame` for a list of keys (exported for layouts that need to know where the camera is). */
export const cameraPathPose = (
	frame: number,
	keys: CameraKey3D[],
	base: CameraPose,
	opts: {ease?: Ease | Ease[]; mode?: 'keys' | 'glide'; baseDistance?: number} = {},
): CameraPose => {
	const {ease = curves.inOut, mode = 'keys'} = opts;
	const baseDistance = opts.baseDistance ?? toOrbit(base.position, base.target).distance;
	const sorted = [...keys].sort((a, b) => a.at - b.at);
	const allOrbit = sorted.every((k) => (k.orbit || k.dolly !== undefined) && !k.position);
	const full: Full[] = [];
	for (const k of sorted) {
		const prev: Full = full[full.length - 1] ?? {
			at: 0,
			target: base.target,
			fov: base.fov,
			roll: base.roll,
			position: base.position,
			orbit: toOrbit(base.position, base.target),
			shift: [0, 0],
		};
		const target = k.target ?? prev.target;
		const prevOrbit = prev.orbit ?? toOrbit(prev.position, prev.target);
		const orbit =
			k.orbit || k.dolly !== undefined
				? {
						azimuth: k.orbit?.azimuth ?? prevOrbit.azimuth,
						elevation: k.orbit?.elevation ?? prevOrbit.elevation,
						distance: k.orbit?.distance ?? (k.dolly !== undefined ? baseDistance * k.dolly : prevOrbit.distance),
					}
				: null;
		const position = k.position ?? (orbit ? orbitPoint(target, orbit.azimuth, orbit.elevation, orbit.distance) : prev.position);
		const entry: Full = {at: k.at, target, fov: k.fov ?? prev.fov, roll: k.roll ?? prev.roll, position, orbit: orbit ?? toOrbit(position, target), shift: k.shift ?? prev.shift};
		// two keys on one frame: the later wins (interpolate needs strictly increasing frames)
		if (full.length && full[full.length - 1].at === k.at) {
			full[full.length - 1] = entry;
		} else {
			full.push(entry);
		}
	}
	if (full.length === 0) {
		return base;
	}
	if (full.length === 1) {
		const f = full[0];
		return withShift({position: f.position, target: f.target, fov: f.fov, roll: f.roll}, f.shift);
	}
	const times = full.map((k) => k.at);
	if (mode === 'glide') {
		const one = Array.isArray(ease) ? curves.inOut : ease;
		const t0 = times[0];
		const tn = times[times.length - 1];
		const tau = t0 + (tn - t0) * ramp(frame, t0, tn - t0, one);
		let i = 0;
		while (i < times.length - 2 && tau > times[i + 1]) {
			i++;
		}
		const local = times[i + 1] > times[i] ? Math.max(0, Math.min(1, (tau - times[i]) / (times[i + 1] - times[i]))) : 1;
		const p = (i + local) / (full.length - 1);
		const lin = (pick: (f: Full) => number) => pick(full[i]) + (pick(full[i + 1]) - pick(full[i])) * local;
		const spline = (pts: Vec3[]) => new THREE.CatmullRomCurve3(pts.map((v) => new THREE.Vector3(...v)), false, 'centripetal').getPoint(p);
		const target = spline(full.map((f) => f.target));
		let position: Vec3;
		if (allOrbit) {
			const o = spline(full.map((f) => [f.orbit?.azimuth ?? 0, f.orbit?.elevation ?? 0, f.orbit?.distance ?? 1]));
			position = orbitPoint([target.x, target.y, target.z], o.x, o.y, o.z);
		} else {
			const q = spline(full.map((f) => f.position));
			position = [q.x, q.y, q.z];
		}
		return withShift({position, target: [target.x, target.y, target.z], fov: lin((f) => f.fov), roll: lin((f) => f.roll)}, [
			lin((f) => f.shift[0]),
			lin((f) => f.shift[1]),
		]);
	}
	const val = (pick: (f: Full) => number) => track(frame, times, full.map(pick), ease);
	const target: Vec3 = [val((f) => f.target[0]), val((f) => f.target[1]), val((f) => f.target[2])];
	const position: Vec3 = allOrbit
		? orbitPoint(target, val((f) => f.orbit?.azimuth ?? 0), val((f) => f.orbit?.elevation ?? 0), val((f) => f.orbit?.distance ?? 1))
		: [val((f) => f.position[0]), val((f) => f.position[1]), val((f) => f.position[2])];
	return withShift({position, target, fov: val((f) => f.fov), roll: val((f) => f.roll)}, [val((f) => f.shift[0]), val((f) => f.shift[1])]);
};

/**
 * Moves the scene's camera along keys. Place it inside a Scene3D (anywhere among the children). Orbit keys swing
 * around the target in an arc; position keys travel in straight lines ('keys') or through a spline ('glide').
 */
export const CameraPath: React.FC<CameraPathProps> = ({keys, ease, mode = 'keys', handheld = 0, handheldFreq = 0.35, seed = 'camera'}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const s = useScene3D();
	const camera = useThree((st) => st.camera);
	const pose = cameraPathPose(frame, keys, s.pose, {ease, mode, baseDistance: s.distance});
	if (handheld > 0) {
		const a = s.px(handheld);
		const tt = (frame / fps) * handheldFreq;
		pose.position = [
			pose.position[0] + noise(seed, tt, 1) * a,
			pose.position[1] + noise(seed, tt, 2) * a,
			pose.position[2] + noise(seed, tt, 3) * a * 0.5,
		];
		pose.target = [pose.target[0] + noise(seed, tt, 4) * a * 0.5, pose.target[1] + noise(seed, tt, 5) * a * 0.5, pose.target[2]];
	}
	const [x, y, z] = pose.position;
	const [tx, ty, tz] = pose.target;
	// layout effect: the camera must be in place before ThreeCanvas draws this frame
	useLayoutEffect(() => {
		applyCameraPose(camera, {position: [x, y, z], target: [tx, ty, tz], fov: pose.fov, roll: pose.roll});
	}, [camera, x, y, z, tx, ty, tz, pose.fov, pose.roll]);
	return null;
};
