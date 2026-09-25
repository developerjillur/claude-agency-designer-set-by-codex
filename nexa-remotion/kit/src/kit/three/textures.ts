// Textures that are safe to render: images load under delayRender and redraw with advance() once they are on
// screen; canvas textures wait for their fonts before drawing. Colour textures are tagged sRGB.
import {useThree} from '@react-three/fiber';
import {useEffect, useLayoutEffect, useMemo, useState} from 'react';
import {useDelayRender} from 'remotion';
import * as THREE from 'three';
import {useFontsReady, useHoldUntil, type KitFontRef} from './hooks';

export type TextureFit = 'cover' | 'fill';

/** Crops a texture (repeat and offset) so it covers a surface of `aspect` (width / height) without stretching. */
export const fitTexture = (tex: THREE.Texture, aspect: number, fit: TextureFit = 'cover'): THREE.Texture => {
	const img = tex.image as {width?: number; height?: number} | null;
	const ia = img?.width && img?.height ? img.width / img.height : aspect;
	tex.repeat.set(1, 1);
	tex.offset.set(0, 0);
	if (fit === 'cover' && Number.isFinite(ia) && ia > 0 && aspect > 0) {
		if (ia > aspect) {
			tex.repeat.x = aspect / ia;
			tex.offset.x = (1 - tex.repeat.x) / 2;
		} else {
			tex.repeat.y = ia / aspect;
			tex.offset.y = (1 - tex.repeat.y) / 2;
		}
	}
	return tex;
};

/**
 * An image as a texture (staticFile() path or a CORS-enabled URL), held under delayRender until it is loaded and
 * drawn. `aspect` crops it to cover a surface of that width / height. Returns null until loaded (and for no src).
 */
export const useImageTexture = (src: string | null | undefined, aspect?: number, fit: TextureFit = 'cover'): THREE.Texture | null => {
	const gl = useThree((s) => s.gl);
	const {cancelRender} = useDelayRender();
	const [tex, setTex] = useState<THREE.Texture | null>(null);
	useEffect(() => {
		if (!src) {
			return;
		}
		let alive = true;
		new THREE.TextureLoader().load(
			src,
			(t) => {
				if (!alive) {
					t.dispose();
					return;
				}
				t.colorSpace = THREE.SRGBColorSpace;
				t.anisotropy = gl.capabilities.getMaxAnisotropy();
				setTex(t);
			},
			undefined,
			() => cancelRender(new Error(`Could not load the texture ${src}`)),
		);
		return () => {
			alive = false;
		};
	}, [src, gl, cancelRender]);
	useEffect(() => () => tex?.dispose(), [tex]);
	useLayoutEffect(() => {
		if (tex && aspect) {
			fitTexture(tex, aspect, fit);
		}
	}, [tex, aspect, fit]);
	useHoldUntil(!src || tex !== null, `Loading texture ${src ?? ''}`);
	return src ? tex : null;
};

export type CanvasDraw = (ctx: CanvasRenderingContext2D, width: number, height: number) => void;

/**
 * A texture drawn with the 2D canvas API (UI screens, card faces, labels), redrawn when `key` changes. `fonts`
 * are CSS font shorthands the drawing uses ('700 40px "Inter", sans-serif'): drawing waits until they load, so
 * text never renders in a fallback face. `text` is the text drawn, so the right subsets (Bangla) load.
 */
export const useCanvasTexture = ({
	width,
	height,
	draw,
	key,
	fonts = [],
	text = '',
	kit = [],
}: {
	width: number;
	height: number;
	draw: CanvasDraw;
	key: string;
	fonts?: readonly string[];
	text?: string;
	/** Kit fonts behind `fonts` (themeFontRefs(theme)): drawing waits until they are really loaded. */
	kit?: readonly KitFontRef[];
}): THREE.CanvasTexture | null => {
	const gl = useThree((s) => s.gl);
	const ready = useFontsReady(fonts, text, kit);
	const tex = useMemo(() => {
		if (!ready || typeof document === 'undefined') {
			return null;
		}
		const canvas = document.createElement('canvas');
		canvas.width = Math.max(2, Math.round(width));
		canvas.height = Math.max(2, Math.round(height));
		const ctx = canvas.getContext('2d');
		if (!ctx) {
			return null;
		}
		draw(ctx, canvas.width, canvas.height);
		const t = new THREE.CanvasTexture(canvas);
		t.colorSpace = THREE.SRGBColorSpace;
		t.anisotropy = gl.capabilities.getMaxAnisotropy();
		return t;
		// `key` stands for the drawing's content
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [ready, key, width, height, gl]);
	useEffect(() => () => tex?.dispose(), [tex]);
	useHoldUntil(tex !== null, 'Drawing a canvas texture');
	return tex;
};

/** A rounded rectangle path on a 2D canvas (for UI drawing). */
export const roundRectPath = (ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number): void => {
	const rr = Math.max(0, Math.min(r, w / 2, h / 2));
	ctx.beginPath();
	ctx.moveTo(x + rr, y);
	ctx.arcTo(x + w, y, x + w, y + h, rr);
	ctx.arcTo(x + w, y + h, x, y + h, rr);
	ctx.arcTo(x, y + h, x, y, rr);
	ctx.arcTo(x, y, x + w, y, rr);
	ctx.closePath();
};

/** A soft round blob (white, alpha falling off to the edge) for contact shadows and glows; cached per tab. */
let blob: THREE.CanvasTexture | null = null;
export const blobTexture = (): THREE.CanvasTexture => {
	if (blob) {
		return blob;
	}
	const c = document.createElement('canvas');
	c.width = 256;
	c.height = 256;
	const ctx = c.getContext('2d') as CanvasRenderingContext2D;
	const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
	g.addColorStop(0, 'rgba(255,255,255,1)');
	g.addColorStop(0.35, 'rgba(255,255,255,0.62)');
	g.addColorStop(0.7, 'rgba(255,255,255,0.16)');
	g.addColorStop(1, 'rgba(255,255,255,0)');
	ctx.fillStyle = g;
	ctx.fillRect(0, 0, 256, 256);
	blob = new THREE.CanvasTexture(c);
	return blob;
};
