// Film grain: a seeded 256 px noise tile, made once per render tab, drawn onto a full-frame canvas at a new random
// offset a dozen times a second (a boil, not the electronic sizzle of per-frame noise, and far cheaper to encode).
// SVG feTurbulence cannot draw grain this fine and Chrome draws SVG filters on the CPU, so the tile is canvas.
import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {continueRender, delayRender, random, useCurrentFrame} from 'remotion';
import {useStage, useTheme} from '../core';

export const GRAIN_TILE = 256;

type TileKind = 'grey' | 'signed';
const tiles: Partial<Record<TileKind, HTMLCanvasElement>> = {};

// mulberry32: a tiny seeded generator, the same numbers in every tab and on every machine
const seeded = (seed: number) => () => {
	seed = (seed + 0x6d2b79f5) | 0;
	let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
	t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
	return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

/**
 * The shared noise tile. 'grey': mid-grey noise (the mean of three draws, so it clusters like film grain) for
 * overlay and soft-light blending. 'signed': the same noise as white or black specks with alpha, which shows on any
 * ground (overlay grain vanishes on near-black and pure white).
 */
export const grainTile = (kind: TileKind = 'grey'): HTMLCanvasElement | null => {
	const hit = tiles[kind];
	if (hit) {
		return hit;
	}
	if (typeof document === 'undefined') {
		return null;
	}
	const canvas = document.createElement('canvas');
	canvas.width = GRAIN_TILE;
	canvas.height = GRAIN_TILE;
	const ctx = canvas.getContext('2d');
	if (!ctx) {
		return null;
	}
	const img = ctx.createImageData(GRAIN_TILE, GRAIN_TILE);
	const rnd = seeded(9173);
	for (let i = 0; i < GRAIN_TILE * GRAIN_TILE; i++) {
		const v = (rnd() + rnd() + rnd()) / 3;
		if (kind === 'grey') {
			const g = Math.round(v * 255);
			img.data[i * 4] = g;
			img.data[i * 4 + 1] = g;
			img.data[i * 4 + 2] = g;
			img.data[i * 4 + 3] = 255;
		} else {
			const s = v * 2 - 1;
			const g = s > 0 ? 255 : 0;
			img.data[i * 4] = g;
			img.data[i * 4 + 1] = g;
			img.data[i * 4 + 2] = g;
			img.data[i * 4 + 3] = Math.round(Math.min(1, Math.abs(s) * 2.2) * 255);
		}
	}
	ctx.putImageData(img, 0, 0);
	tiles[kind] = canvas;
	return canvas;
};

/** A CSS url() of the tile, for backgrounds (paper cards, the CSS paper). 'none' outside the browser. */
const urls: Partial<Record<TileKind, string>> = {};
const rawUrls: Partial<Record<TileKind, string>> = {};
export const grainUrl = (kind: TileKind = 'grey'): string => {
	const hit = urls[kind];
	if (hit) {
		return hit;
	}
	const c = grainTile(kind);
	if (!c) {
		return 'none';
	}
	rawUrls[kind] = c.toDataURL('image/png');
	urls[kind] = `url(${rawUrls[kind]})`;
	return urls[kind] as string;
};

// A CSS background image is not awaited by the renderer, so the first frame could be captured before the tile is
// decoded. Decode it once per tab behind a delayRender; later mounts find it ready and do not wait.
const decoded: Partial<Record<TileKind, Promise<void>>> = {};
const ready: Partial<Record<TileKind, boolean>> = {};

/** grainUrl() for use in a component: holds the render until the tile image is decoded (once per tab). */
export const useGrainUrl = (kind: TileKind = 'grey'): string => {
	const url = grainUrl(kind);
	const [handle] = useState(() => (ready[kind] || url === 'none' ? null : delayRender(`grain tile ${kind}`)));
	useEffect(() => {
		if (handle === null) {
			return;
		}
		const src = rawUrls[kind];
		const job =
			decoded[kind] ??
			(decoded[kind] = new Promise<void>((resolve) => {
				const img = new Image();
				img.onload = () => resolve();
				img.onerror = () => resolve();
				img.src = src ?? '';
				img.decode().then(resolve, resolve);
			}));
		job.then(() => {
			ready[kind] = true;
			continueRender(handle);
		});
	}, [handle, kind]);
	return url;
};

export type GrainBlend = 'auto' | 'overlay' | 'soft-light' | 'signed';

export type GrainProps = {
	amount?: number; // 0 to 1; default the theme's texture.grain (0.16 reads as printed paper, 0.05 as a whisper)
	rate?: number; // new grain plates per second (default 12); 0 = still (a dither, cheap to encode)
	size?: number; // size of one grain in px at 1080 (default 1.25)
	blend?: GrainBlend; // default auto (= signed): visible on every tone; overlay keeps pure white and black clean
	seed?: string;
	style?: React.CSSProperties;
};

/**
 * Grain over everything under it. Put it last in a scene (over pictures and cards too) for a printed or filmed
 * look, or under the content for a textured ground only.
 */
export const Grain: React.FC<GrainProps> = ({amount, rate = 12, size = 1.25, blend = 'auto', seed = 'grain', style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, fps, unit} = useStage();
	const ref = useRef<HTMLCanvasElement>(null);
	const a = Math.max(0, Math.min(1, amount ?? t.texture.grain));
	const mode: Exclude<GrainBlend, 'auto'> = blend === 'auto' ? 'signed' : blend;
	// hold each plate a whole number of frames, so the boil is even
	const period = rate > 0 ? Math.max(1, Math.round(fps / rate)) : 0;
	const plate = period > 0 ? Math.floor(frame / period) : 0;
	const w = Math.max(1, Math.ceil(width));
	const h = Math.max(1, Math.ceil(height));
	const kind: TileKind = mode === 'signed' ? 'signed' : 'grey';

	useLayoutEffect(() => {
		const canvas = ref.current;
		const tile = grainTile(kind);
		if (!canvas || !tile) {
			return;
		}
		const ctx = canvas.getContext('2d');
		if (!ctx) {
			return;
		}
		const pattern = ctx.createPattern(tile, 'repeat');
		if (!pattern) {
			return;
		}
		const s = size * unit;
		const ox = random(`${seed}-${plate}-x`) * GRAIN_TILE;
		const oy = random(`${seed}-${plate}-y`) * GRAIN_TILE;
		const flipX = random(`${seed}-${plate}-f`) > 0.5 ? -1 : 1;
		pattern.setTransform(new DOMMatrix().scale(s * flipX, s).translate(ox, oy));
		ctx.clearRect(0, 0, w, h);
		ctx.imageSmoothingEnabled = true;
		ctx.fillStyle = pattern;
		ctx.fillRect(0, 0, w, h);
	}, [kind, plate, seed, size, unit, w, h]);

	if (a <= 0) {
		return null;
	}
	// measured: these gains give a luma spread (std) of about 40 x amount levels on a mid-grey in every mode, so
	// 0.16 reads like printed paper (about 6 levels). Signed specks show on any tone and shift the mean slightly
	// towards mid-grey (lifted blacks, about 1.2 x amount x 40 levels); overlay and soft-light fade out on
	// near-white and near-black grounds.
	const opacity = Math.min(1, a * (mode === 'signed' ? 0.7 : mode === 'soft-light' ? 3.2 : 1.55));
	return (
		<canvas
			ref={ref}
			width={w}
			height={h}
			style={{
				position: 'absolute',
				left: 0,
				top: 0,
				width,
				height,
				opacity,
				mixBlendMode: mode === 'signed' ? 'normal' : mode,
				pointerEvents: 'none',
				...style,
			}}
		/>
	);
};
