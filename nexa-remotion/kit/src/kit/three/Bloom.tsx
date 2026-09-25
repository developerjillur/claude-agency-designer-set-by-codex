// <Bloom>: a soft glow on the brightest parts of the scene (emissive materials, metal highlights, glowing
// particles). three's EffectComposer (RenderPass, UnrealBloomPass, OutputPass) draws the frame instead of the
// renderer, from a priority-1 useFrame: inside ThreeCanvas that callback runs within advance(), and it uses no
// time or delta, so each frame depends only on the scene state (verified in renders; the canvas stays
// transparent over Scene3D's CSS background). Stateful passes (afterimage, TAA) would not be deterministic.
import {useFrame, useThree} from '@react-three/fiber';
import React, {useEffect, useMemo} from 'react';
import * as THREE from 'three';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {OutputPass} from 'three/examples/jsm/postprocessing/OutputPass.js';
import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

export type BloomProps = {
	/** Glow amount (0.3 subtle, 1 strong). */
	strength?: number;
	/** Spread of the glow, 0..1. */
	radius?: number;
	/** Brightness (0..1, linear) above which pixels glow: raise it to keep the glow on highlights only. */
	threshold?: number;
};

/**
 * Put it anywhere inside a Scene3D (or a ThreeCanvas). Note: the OutputPass tone-maps the whole frame, so
 * materials with toneMapped={false} (Text3D faces, screens, cards) are tone-mapped too while Bloom is on.
 */
export const Bloom: React.FC<BloomProps> = ({strength = 0.7, radius = 0.4, threshold = 0.8}) => {
	const gl = useThree((s) => s.gl);
	const scene = useThree((s) => s.scene);
	const camera = useThree((s) => s.camera);
	const size = useThree((s) => s.size);
	const composer = useMemo(() => {
		const c = new EffectComposer(gl);
		c.addPass(new RenderPass(scene, camera));
		c.addPass(new UnrealBloomPass(new THREE.Vector2(size.width, size.height), strength, radius, threshold));
		c.addPass(new OutputPass());
		c.setPixelRatio(gl.getPixelRatio());
		c.setSize(size.width, size.height);
		return c;
	}, [gl, scene, camera, size.width, size.height, strength, radius, threshold]);
	useEffect(() => () => composer.dispose(), [composer]);
	// priority 1 takes over rendering: R3F skips its own gl.render and this draws the frame instead
	useFrame(() => {
		composer.render();
	}, 1);
	return null;
};
