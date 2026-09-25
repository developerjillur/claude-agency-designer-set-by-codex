// Light rigs and a procedural studio environment. No HDR download: the reflections come from three's
// RoomEnvironment, pre-filtered once per tab with PMREM, so every tab lights the scene the same way.
import {useThree} from '@react-three/fiber';
import React, {useEffect, useLayoutEffect, useMemo} from 'react';
import * as THREE from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {useTheme} from '../core';
import {mix} from './util';

export type LightRigName = 'studio' | 'soft' | 'dramatic' | 'flat';

/** The environment (reflection) intensity each rig is tuned with; Scene3D uses it unless told otherwise. */
export const RIG_ENVIRONMENT: Record<LightRigName, number> = {
	studio: 0.8,
	soft: 1,
	dramatic: 0.28,
	flat: 0.55,
};

/**
 * Reflections and soft fill from a procedural photo studio (a lit room). Metals and glossy plastics need it:
 * without an environment a metal renders black.
 */
export const StudioEnvironment: React.FC<{intensity?: number; rotation?: number}> = ({intensity = 1, rotation = 0}) => {
	const gl = useThree((s) => s.gl);
	const scene = useThree((s) => s.scene);
	const target = useMemo(() => {
		const pmrem = new THREE.PMREMGenerator(gl);
		const room = new RoomEnvironment();
		const rt = pmrem.fromScene(room, 0.04);
		room.dispose();
		pmrem.dispose();
		return rt;
	}, [gl]);
	useLayoutEffect(() => {
		const prev = scene.environment;
		scene.environment = target.texture;
		scene.environmentIntensity = intensity;
		scene.environmentRotation.set(0, rotation, 0);
		return () => {
			scene.environment = prev;
		};
	}, [scene, target, intensity, rotation]);
	useEffect(() => () => target.dispose(), [target]);
	return null;
};

type KeyProps = {position: [number, number, number]; intensity: number; color: string; castShadow?: boolean};

const Key: React.FC<KeyProps> = ({position, intensity, color, castShadow}) => (
	<directionalLight
		position={position}
		intensity={intensity}
		color={color}
		castShadow={castShadow}
		shadow-mapSize={[2048, 2048]}
		shadow-camera-left={-11}
		shadow-camera-right={11}
		shadow-camera-top={11}
		shadow-camera-bottom={-11}
		shadow-camera-near={0.5}
		shadow-camera-far={60}
		shadow-bias={-0.0004}
		shadow-normalBias={0.02}
	/>
);

/**
 * Three looks for products, type and scenes, coloured from the theme:
 * - studio: warm key from the upper left, soft fill, a clean rim from behind (the default);
 * - soft: low contrast, wraps everything (UI cards, playful scenes);
 * - dramatic: a hard side key, little fill, an accent-tinted rim (dark themes, trailers, launches);
 * - flat: even light, nearly no shading (diagrams, charts).
 */
export const LightRig: React.FC<{rig?: LightRigName; intensity?: number; accent?: string; shadows?: boolean}> = ({
	rig = 'studio',
	intensity = 1,
	accent,
	shadows = false,
}) => {
	const t = useTheme();
	const c = t.colors;
	const k = intensity;
	const ground = mix(c.bg, '#000000', t.dark ? 0.6 : 0.35);
	const rimColor = accent ?? (t.dark ? mix('#ffffff', c.accent, 0.55) : '#ffffff');
	if (rig === 'soft') {
		return (
			<>
				<hemisphereLight args={['#ffffff', mix(c.bg, '#ffffff', 0.3), 1.0 * k]} />
				<Key position={[0, 6, 8]} intensity={0.9 * k} color="#ffffff" castShadow={shadows} />
				<directionalLight position={[-4, 2, -6]} intensity={0.45 * k} color={rimColor} />
			</>
		);
	}
	if (rig === 'dramatic') {
		return (
			<>
				<hemisphereLight args={['#ffffff', ground, 0.12 * k]} />
				<Key position={[-6, 6.5, 3.5]} intensity={3.4 * k} color="#fff1e0" castShadow={shadows} />
				<directionalLight position={[6, 2.5, -6]} intensity={3.2 * k} color={accent ?? mix('#ffffff', c.accent, 0.7)} />
				<directionalLight position={[0, -3, 5]} intensity={0.25 * k} color={mix(c.accent2, '#ffffff', 0.5)} />
			</>
		);
	}
	if (rig === 'flat') {
		return (
			<>
				<hemisphereLight args={['#ffffff', mix(c.bg, '#ffffff', 0.5), 1.5 * k]} />
				<directionalLight position={[0, 4, 10]} intensity={0.6 * k} color="#ffffff" />
			</>
		);
	}
	return (
		<>
			<hemisphereLight args={['#ffffff', ground, 0.55 * k]} />
			<Key position={[-5, 7, 6]} intensity={2.3 * k} color="#fff5ea" castShadow={shadows} />
			<directionalLight position={[5, 3.5, -7]} intensity={1.7 * k} color={rimColor} />
		</>
	);
};
