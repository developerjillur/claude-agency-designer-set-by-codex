// Render-safety hooks for things inside a <ThreeCanvas>.
//
// While rendering, @remotion/three sets frameloop to 'never' and draws each frame once, in a passive effect that
// runs BEFORE the passive effects of your components. So:
// - per-frame imperative changes (instance matrices, attributes, the camera) go in useLayoutEffect, never
//   useEffect (a useEffect change lands one frame late in the render);
// - anything async (images, fonts, traced text) holds the render with delayRender and, once its result is on
//   screen, redraws with advance(): invalidate() does nothing when frameloop is 'never'.
import {useThree} from '@react-three/fiber';
import {useCallback, useEffect, useRef, useState} from 'react';
import {useDelayRender, useRemotionEnvironment} from 'remotion';
import {FONTS, type FontKey, type Theme} from '../core';

/** Draws the scene again now: synchronously while rendering, on the next frame in the Studio. */
export const useRedraw = (): (() => void) => {
	const advance = useThree((s) => s.advance);
	const invalidate = useThree((s) => s.invalidate);
	const {isRendering} = useRemotionEnvironment();
	return useCallback(() => {
		if (isRendering) {
			advance(performance.now());
		} else {
			invalidate();
		}
	}, [advance, invalidate, isRendering]);
};

/**
 * Holds the render from mount until `ready` is true, then redraws (so the frame shows the loaded state) and lets
 * the render continue. Released on unmount too, so a Sequence that ends early never hangs the render.
 */
export const useHoldUntil = (ready: boolean, label: string): void => {
	const {delayRender, continueRender} = useDelayRender();
	const [handle] = useState(() => delayRender(label, {timeoutInMilliseconds: 60000}));
	const released = useRef(false);
	const redraw = useRedraw();
	useEffect(() => {
		if (ready && !released.current) {
			released.current = true;
			redraw();
			continueRender(handle);
		}
	}, [ready, redraw, continueRender, handle]);
	useEffect(
		() => () => {
			if (!released.current) {
				released.current = true;
				continueRender(handle);
			}
		},
		[continueRender, handle],
	);
};

/** A kit font (core's FONTS key) and the weights a stack asked for. */
export type KitFontRef = {key: FontKey; weights: readonly number[]; italic?: boolean};

/**
 * Resolves when a kit font's faces are really in document.fonts. On 4.0.528 @remotion/google-fonts fetches the
 * file first and adds the FontFace only after it has loaded, so until then document.fonts.load() finds no face
 * and resolves at once, and a canvas draws the fallback. Asking the same loader again with the same weights and
 * subsets reuses the requests already in flight (no extra download) and gives us their waitUntilDone().
 */
export const waitForKitFont = ({key, weights, italic = false}: KitFontRef): Promise<void> => {
	const spec = FONTS[key];
	const nearest = (w: number) => spec.weights.reduce((a, b) => (Math.abs(b - w) < Math.abs(a - w) ? b : a));
	const use = [...new Set(weights.map(nearest))].sort((a, b) => a - b);
	const loaded = spec.load(italic && spec.italic ? 'italic' : 'normal', {
		weights: use.map(String),
		subsets: [...spec.subsets],
		ignoreTooManyRequestsWarning: true,
	}) as {waitUntilDone?: () => Promise<void>};
	return loaded.waitUntilDone ? loaded.waitUntilDone() : Promise.resolve();
};

/** The kit fonts behind the theme's stacks (with the Bangla fallback each stack carries). */
export const themeFontRefs = (t: Theme, which: readonly ('display' | 'body' | 'mono')[] = ['display', 'body']): KitFontRef[] => {
	const refs: KitFontRef[] = [];
	const add = (key: FontKey, weights: number[]) => {
		refs.push({key, weights});
		if (!FONTS[key].bangla) {
			refs.push({key: t.fonts.bangla, weights});
		}
	};
	if (which.includes('display')) {
		add(t.fonts.display, [t.weights.display]);
	}
	if (which.includes('body')) {
		add(t.fonts.body, [t.weights.body, t.weights.strong]);
	}
	if (which.includes('mono')) {
		add(t.fonts.mono, [400, 600]);
	}
	return refs;
};

const SYSTEM_FAMILIES = new Set(
	['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-monospace', 'ui-sans-serif', 'ui-serif', '-apple-system', 'blinkmacsystemfont', 'helvetica neue', 'helvetica', 'arial', 'georgia', 'times new roman', 'menlo', 'consolas', 'comic sans ms'],
);

/** The web-font families named in a CSS font shorthand ('800 100px "Inter", "Anek Bangla", sans-serif'). */
const webFamilies = (font: string): string[] => {
	const m = font.match(/\d+(?:\.\d+)?px\s+(.*)$/);
	return (m ? m[1] : font)
		.split(',')
		.map((f) => f.trim().replace(/^["']|["']$/g, ''))
		.filter((f) => f && !SYSTEM_FAMILIES.has(f.toLowerCase()));
};

const familyPresent = (family: string): boolean => {
	let found = false;
	document.fonts.forEach((f) => {
		if (!found && f.family.replace(/^["']|["']$/g, '') === family && f.status === 'loaded') {
			found = true;
		}
	});
	return found;
};

/**
 * True once the faces these CSS font shorthands need for `text` are loaded. Canvas drawing and text tracing use
 * whatever is loaded at that moment, so wait for this first. Pass `kit` (from themeFontRefs) for theme fonts:
 * that waits on the kit's own loaders. Other named families are polled for up to 10 s (a readiness wait under
 * delayRender, not animation), then the browser's document.fonts.load() settles the faces for the text.
 */
export const useFontsReady = (fonts: readonly string[], text: string, kit: readonly KitFontRef[] = []): boolean => {
	const key = fonts.join('\n') + '\u0000' + text + '\u0000' + kit.map((k) => `${k.key}:${k.weights.join(',')}:${k.italic ? 'i' : ''}`).join('|');
	const [readyKey, setReadyKey] = useState<string | null>(null);
	useEffect(() => {
		let alive = true;
		if (typeof document === 'undefined' || !document.fonts) {
			setReadyKey(key);
			return;
		}
		const sample = text.trim() || 'Aa';
		const families = [...new Set(fonts.flatMap(webFamilies))];
		const poll = async () => {
			const start = performance.now();
			while (alive && performance.now() - start < 10000 && !families.every(familyPresent)) {
				await new Promise((r) => setTimeout(r, 40));
			}
		};
		Promise.all(kit.map((k) => waitForKitFont(k).catch(() => undefined)))
			.then(poll)
			.then(() => Promise.all(fonts.map((f) => document.fonts.load(f, sample).catch(() => []))))
			.catch(() => undefined)
			.then(() => {
				if (alive) {
					setReadyKey(key);
				}
			});
		return () => {
			alive = false;
		};
		// the key carries every input
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [key]);
	return readyKey === key;
};
