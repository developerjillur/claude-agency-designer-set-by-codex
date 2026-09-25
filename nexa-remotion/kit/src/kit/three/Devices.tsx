// Device mock-ups built from rounded extrusions: a phone with an image (or a drawn app) on its screen, and a
// payment card with printed faces. Sizes are world units; a 3.2-unit phone is 640 px tall at 1080.
import type {ThreeElements} from '@react-three/fiber';
import {Video} from '@remotion/media';
import React, {useEffect, useMemo} from 'react';
import * as THREE from 'three';
import {useStage, useTheme} from '../core';
import {drawAppScreen, drawCardBack, drawCardFront, drawingFonts, APP_SCREEN_TEXT, cardText, type CardDesign} from './drawings';
import {roundedBoxGeometry, roundedPlaneGeometry} from './RoundedBox';
import {themeFontRefs} from './hooks';
import {useCanvasTexture, useImageTexture} from './textures';
import {mix} from './util';
import {useVideoFrameTexture} from './VideoTexture';

export type DeviceFinish = 'titanium' | 'gloss' | 'matte';

const finishProps = (f: DeviceFinish) =>
	f === 'titanium'
		? {metalness: 0.9, roughness: 0.34, clearcoat: 0.25, clearcoatRoughness: 0.3}
		: f === 'gloss'
			? {metalness: 0, roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.05}
			: {metalness: 0, roughness: 0.72, clearcoat: 0, clearcoatRoughness: 0.5};

const useDisposed = <T extends {dispose: () => void}>(items: T[]) => {
	useEffect(() => () => items.forEach((i) => i.dispose()), [items]);
};

/** A diagonal glare for glass: white, very low alpha. Cached per tab. */
let glare: THREE.CanvasTexture | null = null;
const glareTexture = (): THREE.CanvasTexture => {
	if (glare) {
		return glare;
	}
	const c = document.createElement('canvas');
	c.width = 256;
	c.height = 512;
	const ctx = c.getContext('2d') as CanvasRenderingContext2D;
	const g = ctx.createLinearGradient(0, 0, 256, 512);
	g.addColorStop(0, 'rgba(255,255,255,0)');
	g.addColorStop(0.38, 'rgba(255,255,255,0)');
	g.addColorStop(0.46, 'rgba(255,255,255,0.55)');
	g.addColorStop(0.62, 'rgba(255,255,255,0.12)');
	g.addColorStop(1, 'rgba(255,255,255,0)');
	ctx.fillStyle = g;
	ctx.fillRect(0, 0, 256, 512);
	glare = new THREE.CanvasTexture(c);
	return glare;
};

export type Phone3DProps = Omit<ThreeElements['group'], 'children'> & {
	/** An image on the screen (staticFile() path or URL), cropped to cover. */
	screen?: string | null;
	/** A video on the screen (muted, looped), cropped to cover; wins over `screen`. */
	video?: string | null;
	/** With no image: the drawn app screen ('app') or a plain `screenColor`. */
	ui?: 'app' | 'none';
	screenColor?: string;
	/** Body colour; default graphite on light themes, silver on dark ones. */
	color?: string;
	finish?: DeviceFinish;
	/** Height in world units. */
	height?: number;
	/** A faint diagonal reflection on the glass. */
	glare?: boolean;
	children?: React.ReactNode;
};

/** A modern phone: rounded aluminium body, black glass, a screen, the island, buttons and a camera bump. */
export const Phone3D: React.FC<Phone3DProps> = ({
	screen,
	video,
	ui = 'app',
	screenColor,
	color,
	finish = 'titanium',
	height = 3.2,
	glare: showGlare = true,
	children,
	...group
}) => {
	const t = useTheme();
	const h = height;
	const w = h * 0.486;
	const d = h * 0.058;
	const r = h * 0.078;
	const b = d * 0.38;
	const e = h * 0.014; // black border around the display
	const sw = w - 2 * b - 2 * e;
	const sh = h - 2 * b - 2 * e;
	const bump = w * 0.46;
	const body = color ?? (t.dark ? '#c7cad1' : '#363a42');

	const geo = useMemo(() => {
		const lens = new THREE.CylinderGeometry(bump * 0.17, bump * 0.17, h * 0.012, 40);
		lens.rotateX(Math.PI / 2);
		const ring = new THREE.CylinderGeometry(bump * 0.205, bump * 0.205, h * 0.008, 40);
		ring.rotateX(Math.PI / 2);
		return {
			body: roundedBoxGeometry(w, h, d, r, b, 6, 24),
			glass: roundedPlaneGeometry(w - 2 * b, h - 2 * b, r - b, 24),
			screen: roundedPlaneGeometry(sw, sh, Math.max(0.01, r - b - e), 24),
			island: roundedPlaneGeometry(h * 0.105, h * 0.03, h * 0.015, 12),
			bump: roundedBoxGeometry(bump, bump, h * 0.014, bump * 0.26, h * 0.005, 3, 16),
			button: roundedBoxGeometry(h * 0.012, 1, h * 0.03, h * 0.005, h * 0.003, 2, 6),
			lens,
			ring,
		};
	}, [w, h, d, r, b, sw, sh, bump]);
	useDisposed(useMemo(() => Object.values(geo), [geo]));

	const image = useImageTexture(screen ?? null, sw / sh);
	const {unit} = useStage();
	const uiW = Math.round(1000 * Math.min(2, Math.max(1, unit)));
	const drawn = useCanvasTexture({
		width: uiW,
		height: Math.round((uiW * sh) / sw),
		draw: (ctx, W, H) => drawAppScreen(ctx, W, H, t),
		key: `app-${t.name}-${t.colors.accent}-${ui}-${screen ? 'img' : 'drawn'}`,
		fonts: screen || ui !== 'app' ? [] : drawingFonts(t),
		text: screen || ui !== 'app' ? '' : APP_SCREEN_TEXT,
		kit: screen || ui !== 'app' ? [] : themeFontRefs(t, ['display', 'body', 'mono']),
	});
	const clip = useVideoFrameTexture(1000, Math.round((1000 * sh) / sw));
	const screenMap = video ? clip.texture : screen ? image : ui === 'app' ? drawn : null;
	const fz = d / 2;
	// thin layers on the glass: real gaps plus polygon offset, or they fight in the depth buffer
	const step = h * 0.0012;
	const layer = (n: number) => ({polygonOffset: true, polygonOffsetFactor: -n, polygonOffsetUnits: -2 * n});

	return (
		<group {...group}>
			{video ? <Video src={video} headless muted loop onVideoFrame={clip.onVideoFrame} /> : null}
			<mesh geometry={geo.body} castShadow receiveShadow>
				<meshPhysicalMaterial color={body} {...finishProps(finish)} />
			</mesh>
			<mesh geometry={geo.glass} position={[0, 0, fz + step]}>
				<meshPhysicalMaterial color="#08090b" metalness={0} roughness={0.08} clearcoat={1} clearcoatRoughness={0.04} {...layer(1)} />
			</mesh>
			<mesh geometry={geo.screen} position={[0, 0, fz + 2 * step]}>
				<meshBasicMaterial key={screenMap ? 'map' : 'flat'} map={screenMap} color={screenMap ? '#ffffff' : screenColor ?? t.colors.bg} toneMapped={false} {...layer(2)} />
			</mesh>
			<mesh geometry={geo.island} position={[0, sh / 2 - h * 0.034, fz + 3 * step]}>
				<meshBasicMaterial color="#030304" toneMapped={false} {...layer(3)} />
			</mesh>
			{showGlare ? (
				<mesh geometry={geo.glass} position={[0, 0, fz + 4 * step]} renderOrder={2}>
					<meshBasicMaterial map={glareTexture()} transparent opacity={t.dark ? 0.1 : 0.16} depthWrite={false} toneMapped={false} {...layer(4)} />
				</mesh>
			) : null}
			{/* buttons: action and volume on the left, power on the right */}
			{[
				{x: -w / 2 - h * 0.002, y: h * 0.25, len: h * 0.045},
				{x: -w / 2 - h * 0.002, y: h * 0.165, len: h * 0.08},
				{x: -w / 2 - h * 0.002, y: h * 0.065, len: h * 0.08},
				{x: w / 2 + h * 0.002, y: h * 0.13, len: h * 0.12},
			].map((btn, i) => (
				<mesh key={i} geometry={geo.button} position={[btn.x, btn.y, 0]} scale={[1, btn.len, 1]}>
					<meshPhysicalMaterial color={mix(body, '#000000', 0.08)} {...finishProps(finish)} />
				</mesh>
			))}
			{/* camera bump on the back, upper left when seen from behind */}
			<group position={[w / 2 - b - bump / 2 - h * 0.018, h / 2 - b - bump / 2 - h * 0.018, -fz - h * 0.006]}>
				<mesh geometry={geo.bump}>
					<meshPhysicalMaterial color={mix(body, '#ffffff', 0.08)} metalness={0.2} roughness={0.25} clearcoat={1} />
				</mesh>
				{[
					[-bump * 0.2, bump * 0.2],
					[-bump * 0.2, -bump * 0.2],
					[bump * 0.22, 0],
				].map(([x, y], i) => (
					<group key={i} position={[x, y, -h * 0.008]}>
						<mesh geometry={geo.ring}>
							<meshStandardMaterial color="#9a9ca3" metalness={1} roughness={0.28} />
						</mesh>
						<mesh geometry={geo.lens} position={[0, 0, -h * 0.002]}>
							<meshPhysicalMaterial color="#0b0c10" metalness={0.1} roughness={0.05} clearcoat={1} />
						</mesh>
					</group>
				))}
			</group>
			{children}
		</group>
	);
};

export type Card3DProps = Omit<ThreeElements['group'], 'children'> & CardDesign & {
	/** Images for the faces (cover); without them the card is drawn from the theme and the design fields. */
	front?: string | null;
	back?: string | null;
	/** Width in world units (ISO card proportions). */
	width?: number;
	finish?: DeviceFinish;
	children?: React.ReactNode;
};

/** A payment or membership card: 85.6 x 54 mm proportions, rounded corners, printed front and back. */
export const Card3D: React.FC<Card3DProps> = ({
	front,
	back,
	width = 3.2,
	finish = 'gloss',
	brand,
	number,
	name,
	expiry,
	color,
	color2,
	children,
	...group
}) => {
	const t = useTheme();
	const w = width;
	const h = w / 1.586;
	const d = w * 0.012;
	const r = h * 0.07;
	const design: CardDesign = {brand, number, name, expiry, color, color2};
	const geo = useMemo(
		() => ({
			body: roundedBoxGeometry(w, h, d, r, d * 0.45, 3, 20),
			face: roundedPlaneGeometry(w - d * 0.9, h - d * 0.9, r - d * 0.45, 20),
		}),
		[w, h, d, r],
	);
	useDisposed(useMemo(() => Object.values(geo), [geo]));
	const key = JSON.stringify(design) + t.name + t.colors.accent;
	const fImg = useImageTexture(front ?? null, w / h);
	const bImg = useImageTexture(back ?? null, w / h);
	const fDraw = useCanvasTexture({
		width: 1000,
		height: Math.round(1000 / 1.586),
		draw: (ctx, W, H) => drawCardFront(ctx, W, H, t, design),
		key: 'front' + key + (front ? 'img' : ''),
		fonts: front ? [] : drawingFonts(t),
		text: front ? '' : cardText(design),
		kit: front ? [] : themeFontRefs(t, ['display', 'body', 'mono']),
	});
	const bDraw = useCanvasTexture({
		width: 1000,
		height: Math.round(1000 / 1.586),
		draw: (ctx, W, H) => drawCardBack(ctx, W, H, t, design),
		key: 'back' + key + (back ? 'img' : ''),
		fonts: back ? [] : drawingFonts(t),
		text: back ? '' : cardText(design),
		kit: back ? [] : themeFontRefs(t, ['display', 'body', 'mono']),
	});
	const f = front ? fImg : fDraw;
	const bk = back ? bImg : bDraw;
	const edge = mix(color ?? t.colors.accent, color2 ?? mix(color ?? t.colors.accent, '#000000', 0.55), 0.5);
	const fp = finishProps(finish);
	const gap = w * 0.0012;
	const layer = {polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -4};
	return (
		<group {...group}>
			<mesh geometry={geo.body} castShadow receiveShadow>
				<meshPhysicalMaterial color={edge} {...fp} />
			</mesh>
			<mesh geometry={geo.face} position={[0, 0, d / 2 + gap]}>
				<meshPhysicalMaterial key={f ? 'f' : 'nf'} map={f} color={f ? '#ffffff' : edge} {...fp} metalness={0} {...layer} />
			</mesh>
			<mesh geometry={geo.face} position={[0, 0, -d / 2 - gap]} rotation={[0, Math.PI, 0]}>
				<meshPhysicalMaterial key={bk ? 'b' : 'nb'} map={bk} color={bk ? '#ffffff' : edge} {...fp} metalness={0} {...layer} />
			</mesh>
			{children}
		</group>
	);
};
