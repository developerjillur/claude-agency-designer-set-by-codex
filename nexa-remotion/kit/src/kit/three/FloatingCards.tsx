// <FloatingCards>: UI cards (stat cards drawn in the theme's fonts, images, or plain colour panels) floating at
// different depths. Depth gives real parallax when the camera moves (CameraPath) and when the cards drift.
import React, {useEffect, useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {drawStatCard, drawingFonts, statCardText, type StatCardContent} from './drawings';
import {roundedPlaneGeometry} from './RoundedBox';
import {useScene3D} from './Scene3D';
import {themeFontRefs} from './hooks';
import {roundRectPath, useCanvasTexture, useImageTexture} from './textures';
import {deg, noise} from './util';

export type FloatingCard = StatCardContent & {
	/** An image for the whole card (cover). */
	src?: string;
	/** Card fill; default the theme's surface. */
	color?: string;
	/** Size in px at 1080. */
	width?: number;
	height?: number;
	/** Screen position in px at 1080 from the frame centre (x right, y down), and depth in world units. */
	x?: number;
	y?: number;
	z?: number;
	/** Turn about Y, degrees. */
	turn?: number;
};

export type FloatingCardsProps = {
	cards?: FloatingCard[];
	layout?: 'scatter' | 'row' | 'fan';
	enter?: 'fly' | 'rise' | 'none';
	out?: 'fly' | 'none';
	delay?: number;
	/** Frames between cards. */
	stagger?: number;
	enterDuration?: number;
	outDuration?: number;
	/** Idle drift in px at 1080. */
	float?: number;
	/** Corner radius in px at 1080; default the theme's radius (at least 16). */
	radius?: number;
	shadow?: boolean;
	seed?: string;
};

export const SAMPLE_CARDS: FloatingCard[] = [
	{title: 'Monthly revenue', value: '$48.2k', caption: '+12.4% this month', chart: [12, 14, 13, 17, 16, 21, 24]},
	{title: 'Active users', value: '12,480', caption: '+8.1% vs June', chart: [30, 31, 35, 34, 38, 41, 44]},
	{title: 'Conversion', value: '4.6%', caption: '+0.9 pts', chart: [3.1, 3.4, 3.3, 3.9, 4.1, 4.3, 4.6]},
	{title: 'Orders today', value: '1,284', caption: '+214 since 9 AM', chart: [2, 5, 9, 12, 17, 21, 26]},
	{title: 'Churn', value: '1.8%', caption: '-0.4 pts', up: true, chart: [2.6, 2.5, 2.3, 2.2, 2.0, 1.9, 1.8]},
	{title: 'NPS', value: '72', caption: '+6 this quarter', chart: [61, 63, 64, 66, 69, 70, 72]},
];

// normalised slots: x, y in the safe area's half-sizes (y down), z in world units
const SCATTER: [number, number, number, number][] = [
	[0.02, 0.04, 0.9, -4],
	[-0.66, -0.42, -0.9, 9],
	[0.68, -0.36, -1.8, -10],
	[-0.6, 0.52, -2.2, 7],
	[0.62, 0.56, -0.2, -7],
	[-0.04, -0.78, -3.4, 3],
];

// the same idea for portrait frames: a loose column that stays inside the narrow safe area
const SCATTER_TALL: [number, number, number, number][] = [
	[0.0, 0.0, 0.9, -4],
	[-0.42, -0.62, -1.2, 8],
	[0.45, -0.34, -2.0, -9],
	[-0.4, 0.4, -1.6, 7],
	[0.42, 0.64, -0.4, -6],
	[0.0, -0.9, -3.4, 3],
];

let shadowCache = new Map<string, THREE.CanvasTexture>();
const shadowTexture = (aspect: number): THREE.CanvasTexture => {
	const key = aspect.toFixed(2);
	const hit = shadowCache.get(key);
	if (hit) {
		return hit;
	}
	const c = document.createElement('canvas');
	const W = 256;
	const H = Math.round(W / aspect);
	c.width = W;
	c.height = H;
	const ctx = c.getContext('2d') as CanvasRenderingContext2D;
	ctx.filter = `blur(${Math.round(W * 0.06)}px)`;
	ctx.fillStyle = 'rgba(0,0,0,1)';
	roundRectPath(ctx, W * 0.14, H * 0.14, W * 0.72, H * 0.72, W * 0.08);
	ctx.fill();
	const tex = new THREE.CanvasTexture(c);
	if (shadowCache.size > 16) {
		shadowCache = new Map();
	}
	shadowCache.set(key, tex);
	return tex;
};

const CardFace: React.FC<{card: FloatingCard; w: number; h: number; wPx: number; hPx: number; radius: number; opacity: number}> = ({
	card,
	w,
	h,
	wPx,
	hPx,
	radius,
	opacity,
}) => {
	const t = useTheme();
	const {unit} = useStage();
	const fill = card.color ?? (t.dark ? t.colors.surface : '#ffffff');
	// twice the card's pixel size (and more at 4K), capped at 2048
	const res = Math.min(2048 / Math.max(wPx, hPx), 2 * Math.max(1, unit));
	const geo = useMemo(() => roundedPlaneGeometry(w, h, radius, 16), [w, h, radius]);
	useEffect(() => () => geo.dispose(), [geo]);
	const image = useImageTexture(card.src ?? null, w / h);
	const hasText = Boolean(card.title || card.value || card.caption || card.chart);
	const drawn = useCanvasTexture({
		width: Math.round(wPx * res),
		height: Math.round(hPx * res),
		draw: (ctx, W, H) => drawStatCard(ctx, W, H, t, card, fill),
		key: JSON.stringify(card) + fill + t.name,
		fonts: card.src || !hasText ? [] : drawingFonts(t),
		text: card.src ? '' : statCardText(card),
		kit: card.src || !hasText ? [] : themeFontRefs(t, ['display', 'body']),
	});
	const map = card.src ? image : hasText ? drawn : null;
	return (
		<mesh geometry={geo}>
			<meshBasicMaterial key={map ? 'm' : 'c'} map={map} color={map ? '#ffffff' : fill} transparent opacity={opacity} toneMapped={false} depthWrite={opacity > 0.98} />
		</mesh>
	);
};

export const FloatingCards: React.FC<FloatingCardsProps> = ({
	cards = SAMPLE_CARDS.slice(0, 5),
	layout = 'scatter',
	enter = 'fly',
	out = 'none',
	delay = 0,
	stagger,
	enterDuration,
	outDuration,
	float = 14,
	radius,
	shadow = true,
	seed = 'cards',
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, durationInFrames} = useStage();
	const s = useScene3D();
	const step = stagger ?? at30(6, fps);
	const eDur = enterDuration ?? at30(30, fps);
	const oDur = outDuration ?? at30(18, fps);
	const camZ = s.pose.position[2];
	const r = s.px(radius ?? Math.max(16, t.radius));
	const tSec = frame / fps;
	const n = cards.length;

	return (
		<>
			{cards.map((card, i) => {
				const wPx = card.width ?? 420;
				const hPx = card.height ?? 300;
				const w = s.px(wPx);
				const h = s.px(hPx);
				let nx: number;
				let ny: number;
				let z: number;
				let turn: number;
				if (layout === 'row') {
					const u = n > 1 ? i / (n - 1) - 0.5 : 0;
					nx = u * 1.7;
					ny = 0;
					z = i % 2 ? -0.5 : 0.2;
					turn = -u * 16;
				} else if (layout === 'fan') {
					const u = n > 1 ? i / (n - 1) - 0.5 : 0;
					nx = u * 1.25;
					ny = Math.abs(u) * 0.35;
					z = -Math.abs(u) * 1.6;
					turn = -u * 34;
				} else {
					const slots = s.height > s.width ? SCATTER_TALL : SCATTER;
					const slot = slots[i % slots.length];
					nx = slot[0];
					ny = slot[1];
					z = slot[2] - Math.floor(i / slots.length) * 2.5;
					turn = slot[3];
				}
				z = card.z ?? z;
				turn = card.turn ?? turn;
				// keep the intended screen position whatever the depth
				const persp = (camZ - z) / camZ;
				const x = card.x !== undefined ? s.px(card.x) * persp : nx * (s.safe.w / 2) * persp;
				const y = card.y !== undefined ? -s.px(card.y) * persp : -ny * (s.safe.h / 2) * persp;

				const d0 = delay + i * step;
				const k = enter === 'none' ? 1 : ramp(frame, d0, eDur, curves.out);
				const fadeIn = enter === 'none' ? 1 : ramp(frame, d0, Math.round(eDur * 0.55), curves.outCubic);
				const q = out === 'none' || !Number.isFinite(durationInFrames) ? 0 : ramp(frame, durationInFrames - 1 - oDur - (n - 1 - i) * Math.round(step / 2), oDur, curves.in);
				const env = ramp(frame, d0, fps, curves.sine);
				const fx = noise(seed, tSec * 0.22 + i * 1.7, 1) * s.px(float) * env;
				const fy = noise(seed, tSec * 0.22 + i * 1.7, 2) * s.px(float) * env;
				const rx = noise(seed, tSec * 0.18 + i * 2.3, 3) * 3 * env;
				const ry = noise(seed, tSec * 0.18 + i * 2.3, 4) * 4 * env;
				let dz = 0;
				let dy = 0;
				if (enter === 'fly') {
					dz -= (1 - k) * 5;
					dy -= (1 - k) * h * 0.4;
				} else if (enter === 'rise') {
					dy -= (1 - k) * h * 1.2;
				}
				dz += q * 6;
				const opacity = Math.max(0, Math.min(1, fadeIn) * (1 - q));
				// stays mounted while hidden, so its texture is not rebuilt when frames render out of order
				return (
					<group
						key={i}
						visible={opacity > 0.001}
						position={[x + fx, y + fy + dy, z + dz]}
						rotation={[deg(rx), deg(turn * (0.4 + 0.6 * k) + ry), 0]}
					>
						{shadow ? (
							<mesh position={[0, -h * 0.08, -0.03]} scale={[w * 1.28, h * 1.34, 1]}>
								<planeGeometry args={[1, 1]} />
								<meshBasicMaterial map={shadowTexture(w / h)} color="#000000" transparent opacity={(s.dark ? 0.55 : 0.22) * opacity} depthWrite={false} toneMapped={false} />
							</mesh>
						) : null}
						<CardFace card={card} w={w} h={h} wPx={wPx} hPx={hPx} radius={r} opacity={opacity} />
					</group>
				);
			})}
		</>
	);
};
