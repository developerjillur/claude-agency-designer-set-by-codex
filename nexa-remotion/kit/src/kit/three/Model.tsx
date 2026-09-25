// <Model>: a glTF / GLB model from public/ (staticFile) or a CORS-enabled URL, loaded under delayRender, fitted
// to a size, sat on the floor or centred, with its animation clips driven by the frame (mixer.setTime), so every
// tab poses it the same. No drei, no CDN: three's own GLTFLoader.
import type {ThreeElements} from '@react-three/fiber';
import React, {useEffect, useLayoutEffect, useMemo, useState} from 'react';
import {useCurrentFrame, useDelayRender} from 'remotion';
import * as THREE from 'three';
import {GLTFLoader, type GLTF} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {clone as cloneSkinned} from 'three/examples/jsm/utils/SkeletonUtils.js';
import {useStage} from '../core';
import {useHoldUntil} from './hooks';

/** Loads a glTF / GLB once per tab and holds the render until it is parsed (textures included). */
export const useModel = (src: string | null | undefined): GLTF | null => {
	const {cancelRender} = useDelayRender();
	const [gltf, setGltf] = useState<GLTF | null>(null);
	useEffect(() => {
		if (!src) {
			return;
		}
		let alive = true;
		new GLTFLoader().load(
			src,
			(g) => {
				if (alive) {
					setGltf(g);
				}
			},
			undefined,
			() => cancelRender(new Error(`Could not load the model ${src} (Draco-compressed files need a DRACOLoader with local decoder files)`)),
		);
		return () => {
			alive = false;
		};
	}, [src, cancelRender]);
	useHoldUntil(!src || gltf !== null, `Loading model ${src ?? ''}`);
	return src ? gltf : null;
};

export type ModelProps = Omit<ThreeElements['group'], 'children'> & {
	src: string;
	/** Scale the model so it is this tall (world units). */
	height?: number;
	/** Or so its largest side is this long. */
	size?: number;
	/** 'bottom' stands it on y = 0, 'center' centres it, 'none' keeps the file's origin. */
	anchor?: 'bottom' | 'center' | 'none';
	/** Animation clip to play: name or index; false for the rest pose. Default the first clip. */
	clip?: string | number | false;
	/** Clip time in seconds; default from the frame (frame / fps * speed + offset). */
	time?: number;
	speed?: number;
	offset?: number;
	loop?: boolean;
	castShadow?: boolean;
	receiveShadow?: boolean;
	/** Multiplies the model's reflections (envMapIntensity) on standard materials. */
	envIntensity?: number;
	children?: React.ReactNode;
};

export const Model: React.FC<ModelProps> = ({
	src,
	height,
	size,
	anchor = 'bottom',
	clip = 0,
	time,
	speed = 1,
	offset = 0,
	loop = true,
	castShadow = true,
	receiveShadow = true,
	envIntensity,
	children,
	...group
}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const gltf = useModel(src);

	// our own copy (skinned meshes need SkeletonUtils), with its rest-pose bounds
	const model = useMemo(() => {
		if (!gltf) {
			return null;
		}
		const scene = cloneSkinned(gltf.scene) as THREE.Object3D;
		scene.traverse((o) => {
			const m = o as THREE.Mesh;
			if (m.isMesh) {
				m.castShadow = castShadow;
				m.receiveShadow = receiveShadow;
				if (envIntensity !== undefined) {
					for (const mat of Array.isArray(m.material) ? m.material : [m.material]) {
						if ((mat as THREE.MeshStandardMaterial).isMeshStandardMaterial) {
							(mat as THREE.MeshStandardMaterial).envMapIntensity = envIntensity;
						}
					}
				}
			}
		});
		scene.updateMatrixWorld(true);
		const box = new THREE.Box3().setFromObject(scene);
		return {scene, box};
	}, [gltf, castShadow, receiveShadow, envIntensity]);

	const mixer = useMemo(() => {
		if (!model || !gltf || clip === false || gltf.animations.length === 0) {
			return null;
		}
		const c = typeof clip === 'number' ? gltf.animations[clip] : gltf.animations.find((a) => a.name === clip);
		if (!c) {
			return null;
		}
		const mx = new THREE.AnimationMixer(model.scene);
		const action = mx.clipAction(c);
		action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
		action.clampWhenFinished = true;
		action.play();
		return mx;
	}, [model, gltf, clip, loop]);
	useEffect(
		() => () => {
			mixer?.stopAllAction();
		},
		[mixer],
	);

	const t = time ?? (frame / fps) * speed + offset;
	// layout effect: the pose must be set before ThreeCanvas draws the frame
	useLayoutEffect(() => {
		mixer?.setTime(Math.max(0, t));
	}, [mixer, t]);

	if (!model) {
		return <group {...group}>{children}</group>;
	}
	const dims = model.box.getSize(new THREE.Vector3());
	const centre = model.box.getCenter(new THREE.Vector3());
	const k = height ? height / Math.max(1e-6, dims.y) : size ? size / Math.max(1e-6, dims.x, dims.y, dims.z) : 1;
	const oy = anchor === 'bottom' ? -model.box.min.y : anchor === 'center' ? -centre.y : 0;
	const ox = anchor === 'none' ? 0 : -centre.x;
	const oz = anchor === 'none' ? 0 : -centre.z;
	return (
		<group {...group}>
			<group scale={k} position={[ox * k, oy * k, oz * k]}>
				<primitive object={model.scene} />
			</group>
			{children}
		</group>
	);
};
