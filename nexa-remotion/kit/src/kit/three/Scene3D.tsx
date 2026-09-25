// <Scene3D>: a ThreeCanvas sized from the stage, with a camera preset, a light rig, a procedural studio
// environment, sRGB output with tone mapping, and a CSS background from the theme behind a transparent canvas.
// Everything inside is driven by useCurrentFrame(); never use R3F's useFrame().
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import React, {createContext, useContext, useLayoutEffect, useMemo} from 'react';
import {AbsoluteFill} from 'remotion';
import * as THREE from 'three';
import {Stage, ThemeProvider, useStage, useTheme, type Theme} from '../core';
import {LightRig, StudioEnvironment, type LightRigName, RIG_ENVIRONMENT} from './LightRig';
import {SHORT_SIDE_UNITS, deg, mix, orbitPoint, type Vec3} from './util';

export type CameraPreset = 'front' | 'hero' | 'low' | 'top' | 'side' | 'close' | 'wide';

export type CameraSpec = {
	preset?: CameraPreset;
	azimuth?: number; // degrees; positive moves the camera to the subject's right
	elevation?: number; // degrees; positive looks down from above
	zoom?: number; // distance multiplier: 1 puts the frame's short side at 5.4 units on the target
	fov?: number; // vertical field of view, degrees
	target?: Vec3;
	roll?: number; // degrees
};

export const CAMERA_PRESETS: Record<CameraPreset, {azimuth: number; elevation: number; zoom: number; fov: number}> = {
	front: {azimuth: 0, elevation: 0, zoom: 1, fov: 30},
	hero: {azimuth: 24, elevation: 12, zoom: 1, fov: 30}, // three-quarter product angle
	low: {azimuth: 14, elevation: -10, zoom: 1, fov: 34}, // looks up: heroic
	top: {azimuth: 0, elevation: 55, zoom: 1.05, fov: 30},
	side: {azimuth: 62, elevation: 6, zoom: 1, fov: 30},
	close: {azimuth: 16, elevation: 8, zoom: 0.7, fov: 28},
	wide: {azimuth: 0, elevation: 8, zoom: 1.35, fov: 45},
};

export type CameraPose = {position: Vec3; target: Vec3; fov: number; roll: number};

export type Scene3DInfo = {
	theme: Theme;
	dark: boolean;
	width: number; // px
	height: number;
	/** The base camera (before any CameraPath). */
	pose: CameraPose;
	distance: number;
	/** World size of the whole frame on the target plane, for the base camera. */
	visible: {w: number; h: number};
	/** The safe area on the target plane in world units (y up, the target at 0, 0). */
	safe: {left: number; right: number; top: number; bottom: number; w: number; h: number};
	/** px at 1080 (the kit's size unit) to world units on the target plane. */
	px: (px: number) => number;
};

const Scene3DContext = createContext<Scene3DInfo | null>(null);

const fallbackInfo = (theme: Theme): Scene3DInfo => ({
	theme,
	dark: theme.dark,
	width: 1920,
	height: 1080,
	pose: {position: [0, 0, 10], target: [0, 0, 0], fov: 30, roll: 0},
	distance: 10,
	visible: {w: 9.6, h: 5.4},
	safe: {left: -4.3, right: 4.3, top: 2.4, bottom: -2.4, w: 8.6, h: 4.8},
	px: (p) => p / 200,
});

/** The scene's layout info; sensible defaults outside a Scene3D (a raw ThreeCanvas). */
export const useScene3D = (): Scene3DInfo => {
	const ctx = useContext(Scene3DContext);
	const theme = useTheme();
	return ctx ?? fallbackInfo(theme);
};

/** A camera spec to a pose, for a frame of this size (the short side is 5.4 units at the target at zoom 1). */
export const cameraPose = (spec: CameraSpec, width: number, height: number): CameraPose & {distance: number; visH: number} => {
	const p = CAMERA_PRESETS[spec.preset ?? 'front'];
	const fov = spec.fov ?? p.fov;
	const zoom = spec.zoom ?? p.zoom;
	const visH = (SHORT_SIDE_UNITS * height) / Math.min(width, height);
	const distance = (visH / (2 * Math.tan(deg(fov) / 2))) * zoom;
	const target = spec.target ?? [0, 0, 0];
	return {
		position: orbitPoint(target, spec.azimuth ?? p.azimuth, spec.elevation ?? p.elevation, distance),
		target,
		fov,
		roll: spec.roll ?? 0,
		distance,
		visH: visH * zoom,
	};
};

/** Puts the default camera at a pose. Layout effect: it must land before ThreeCanvas draws the frame. */
export const applyCameraPose = (camera: THREE.Camera, pose: CameraPose): void => {
	camera.position.set(pose.position[0], pose.position[1], pose.position[2]);
	camera.up.set(0, 1, 0);
	camera.lookAt(pose.target[0], pose.target[1], pose.target[2]);
	if (pose.roll) {
		camera.rotateZ(deg(pose.roll));
	}
	if (camera instanceof THREE.PerspectiveCamera) {
		// near and far follow the distance: a tiny near plane wastes depth precision and makes thin layers
		// (a screen on glass, a label on a card) fight, which tile-based GPUs show as flickering blocks
		const dist = Math.hypot(pose.position[0] - pose.target[0], pose.position[1] - pose.target[1], pose.position[2] - pose.target[2]);
		camera.fov = pose.fov;
		camera.near = Math.max(0.05, dist * 0.03);
		camera.far = Math.max(60, dist * 40);
		camera.updateProjectionMatrix();
	}
	camera.updateMatrixWorld();
};

const BaseCamera: React.FC<{pose: CameraPose}> = ({pose}) => {
	const camera = useThree((s) => s.camera);
	const [x, y, z] = pose.position;
	const [tx, ty, tz] = pose.target;
	useLayoutEffect(() => {
		applyCameraPose(camera, {position: [x, y, z], target: [tx, ty, tz], fov: pose.fov, roll: pose.roll});
	}, [camera, x, y, z, tx, ty, tz, pose.fov, pose.roll]);
	return null;
};

export type Scene3DBackground = 'studio' | 'spot' | 'theme' | 'transparent' | (string & {});

/** The CSS background behind the canvas. 'studio' is a soft radial sweep in the theme's ground colour. */
export const sceneBackground = (bg: Scene3DBackground, t: Theme): string | undefined => {
	const c = t.colors;
	if (bg === 'transparent') {
		return undefined;
	}
	if (bg === 'theme') {
		return c.bg;
	}
	if (bg === 'studio' || bg === 'spot') {
		const tight = bg === 'spot';
		const size = tight ? '58% 62%' : '80% 75%';
		if (t.dark) {
			const hi = mix(c.bg, c.surface, tight ? 1 : 0.85);
			return `radial-gradient(ellipse ${size} at 50% 42%, ${hi} 0%, ${c.bg} ${tight ? 55 : 62}%, ${mix(c.bg, '#000000', 0.5)} 100%)`;
		}
		const hi = mix(c.bg, '#ffffff', 0.9);
		return `radial-gradient(ellipse ${size} at 50% 40%, ${hi} 0%, ${c.bg} ${tight ? 52 : 60}%, ${mix(c.bg, c.text, tight ? 0.16 : 0.09)} 100%)`;
	}
	return bg;
};

const TONE: Record<ToneMappingName, THREE.ToneMapping> = {
	neutral: THREE.NeutralToneMapping, // keeps brand colours close to their hex values: the default
	aces: THREE.ACESFilmicToneMapping, // filmic, desaturates highlights
	agx: THREE.AgXToneMapping, // soft filmic roll-off for bright light
	none: THREE.NoToneMapping,
};

export type ToneMappingName = 'neutral' | 'aces' | 'agx' | 'none';

export type Scene3DProps = {
	children?: React.ReactNode;
	camera?: CameraPreset | CameraSpec;
	lights?: LightRigName | 'none';
	/** Studio reflections from a procedural room (no download): intensity, or false. Default: the rig's. */
	environment?: number | boolean;
	background?: Scene3DBackground;
	toneMapping?: ToneMappingName;
	exposure?: number;
	/** Shadow maps from the key light (meshes need castShadow / receiveShadow). */
	shadows?: boolean;
	/** Depth fog in the ground colour: sells depth for particles and cards. */
	fog?: boolean | {near?: number; far?: number; color?: string};
	/** Canvas size in px for a split screen or an inset; default the whole frame. */
	width?: number;
	height?: number;
	style?: React.CSSProperties;
};

export const Scene3D: React.FC<Scene3DProps> = ({
	children,
	camera = 'front',
	lights = 'studio',
	environment,
	background = 'studio',
	toneMapping = 'neutral',
	exposure = 1,
	shadows = false,
	fog = false,
	width: w,
	height: h,
	style,
}) => {
	const theme = useTheme();
	const stage = useStage();
	const {unit} = stage;
	const width = Math.round(w ?? stage.width);
	const height = Math.round(h ?? stage.height);
	// a custom size gets its own 5% margins; the full frame keeps the platform's safe area
	const custom = width !== stage.width || height !== stage.height;
	const safe = custom ? {x: width * 0.05, y: height * 0.05, w: width * 0.9, h: height * 0.9} : stage.safe;
	const spec: CameraSpec = typeof camera === 'string' ? {preset: camera} : camera;
	const pose = cameraPose(spec, width, height);
	const wpp = pose.visH / height; // world units per frame pixel on the target plane

	const info = useMemo<Scene3DInfo>(
		() => ({
			theme,
			dark: theme.dark,
			width,
			height,
			pose: {position: pose.position, target: pose.target, fov: pose.fov, roll: pose.roll},
			distance: pose.distance,
			visible: {w: pose.visH * (width / height), h: pose.visH},
			safe: {
				left: (safe.x - width / 2) * wpp,
				right: (safe.x + safe.w - width / 2) * wpp,
				top: (height / 2 - safe.y) * wpp,
				bottom: (height / 2 - safe.y - safe.h) * wpp,
				w: safe.w * wpp,
				h: safe.h * wpp,
			},
			px: (p: number) => p * unit * wpp,
		}),
		// the pose is derived from these values
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[theme, width, height, unit, safe.x, safe.y, safe.w, safe.h, wpp, JSON.stringify(spec)],
	);

	const gl = useMemo(
		() => ({
			antialias: true,
			alpha: true,
			toneMapping: TONE[toneMapping],
			toneMappingExposure: exposure,
			outputColorSpace: THREE.SRGBColorSpace,
			localClippingEnabled: true, // Text3D's mask reveal clips with planes
		}),
		[toneMapping, exposure],
	);

	const envIntensity =
		environment === false ? 0 : typeof environment === 'number' ? environment : RIG_ENVIRONMENT[lights === 'none' ? 'studio' : lights];

	const fogSpec = fog === false ? null : fog === true ? {} : fog;

	return (
		<AbsoluteFill style={{width, height, right: undefined, bottom: undefined, background: sceneBackground(background, theme), ...style}}>
			<ThreeCanvas
				width={width}
				height={height}
				gl={gl}
				shadows={shadows ? 'soft' : false}
				camera={{fov: pose.fov, near: Math.max(0.05, pose.distance * 0.03), far: Math.max(60, pose.distance * 40), position: pose.position}}
				style={{position: 'absolute', left: 0, top: 0}}
			>
				<ThemeProvider theme={theme}>
					<Stage safe={safe}>
						<Scene3DContext.Provider value={info}>
							<BaseCamera pose={info.pose} />
							{envIntensity > 0 ? <StudioEnvironment intensity={envIntensity} /> : null}
							{lights === 'none' ? null : <LightRig rig={lights} shadows={shadows} />}
							{fogSpec ? (
								<fog
									attach="fog"
									args={[
										fogSpec.color ?? theme.colors.bg,
										fogSpec.near ?? pose.distance * 0.85,
										fogSpec.far ?? pose.distance * 2.4,
									]}
								/>
							) : null}
							{children}
						</Scene3DContext.Provider>
					</Stage>
				</ThemeProvider>
			</ThreeCanvas>
		</AbsoluteFill>
	);
};
