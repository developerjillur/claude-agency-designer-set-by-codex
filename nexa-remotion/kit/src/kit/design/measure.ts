// Measuring text for layouts that must fit a box (the big number of a StatSplit). The kit's fonts come from
// @remotion/google-fonts, which adds a font face to document.fonts only once it has loaded, so a measurement
// taken on the first render of a tab would use the fallback font. This waits for the face, measures once, caches
// the result for the tab, and holds the render meanwhile.
import {useEffect, useLayoutEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';

/** The first family of a CSS font stack ("Manrope", "Anek Bangla", sans-serif gives Manrope). */
export const firstFamily = (stack: string): string => (/^\s*"([^"]+)"/.exec(stack)?.[1] ?? stack.split(',')[0].trim()).trim();

/** Whether a face of this family has loaded into the page (false while the kit's font is still on its way). */
export const faceLoaded = (family: string): boolean => {
	if (typeof document === 'undefined' || !document.fonts) {
		return true;
	}
	let ok = false;
	document.fonts.forEach((f) => {
		if (f.family.replace(/^["']|["']$/g, '') === family && f.status === 'loaded') {
			ok = true;
		}
	});
	return ok;
};

export type TextStyleKey = {
	fontFamily: string; // a full stack is fine: the first family is the one waited for
	fontWeight: number | string;
	letterSpacing?: string; // in em, so it scales with the size
	textTransform?: 'none' | 'uppercase';
};

const cache = new Map<string, number>();

/**
 * The width of `text` in em for a style, measured in the page after its font has loaded; null until then (the
 * render is held, so no frame is captured with a guessed size). Pass null to skip.
 */
export const useTextEm = (text: string | null, style: TextStyleKey): number | null => {
	const key = text === null ? null : JSON.stringify([text, style.fontFamily, style.fontWeight, style.letterSpacing ?? '', style.textTransform ?? 'none']);
	const [em, setEm] = useState<number | null>(() => (key ? (cache.get(key) ?? null) : null));
	const [handle] = useState(() => (key !== null && em === null && typeof document !== 'undefined' ? delayRender(`measuring "${text}"`) : null));

	useLayoutEffect(() => {
		if (key === null || text === null || typeof document === 'undefined') {
			return;
		}
		const hit = cache.get(key);
		if (hit !== undefined) {
			setEm(hit);
			return;
		}
		let live = true;
		let tries = 0;
		const family = firstFamily(style.fontFamily);
		const measure = () => {
			if (!live) {
				return;
			}
			// wait for the face (up to about 10 s; after that, measure whatever is there)
			if (!faceLoaded(family) && tries++ < 200) {
				setTimeout(measure, 50);
				return;
			}
			const span = document.createElement('span');
			span.textContent = text;
			Object.assign(span.style, {
				position: 'absolute',
				left: '-99999px',
				top: '0px',
				visibility: 'hidden',
				whiteSpace: 'pre',
				fontSize: '100px',
				lineHeight: '1',
				fontFamily: style.fontFamily,
				fontWeight: String(style.fontWeight),
				letterSpacing: style.letterSpacing ?? 'normal',
				textTransform: style.textTransform ?? 'none',
				fontVariantNumeric: 'tabular-nums',
			});
			document.body.appendChild(span);
			const w = span.getBoundingClientRect().width;
			span.remove();
			const v = w / 100;
			cache.set(key, v);
			setEm(v);
		};
		measure();
		return () => {
			live = false;
		};
	}, [key, text, style.fontFamily, style.fontWeight, style.letterSpacing, style.textTransform]);

	useEffect(() => {
		if (handle !== null && em !== null) {
			continueRender(handle);
		}
	}, [handle, em]);
	// never leave the render held if the component goes away first
	useEffect(
		() => () => {
			if (handle !== null) {
				continueRender(handle);
			}
		},
		[handle],
	);
	return em;
};

/**
 * A quick estimate of a string's width in em from a digit width (for numbers before they are measured, or for
 * React values that cannot be measured): % and letters are wider than digits, punctuation narrower.
 */
export const estimateEm = (text: string, digit = 0.6): number => {
	let w = 0.04;
	for (const ch of text) {
		if (/[0-9]/.test(ch)) {
			w += digit;
		} else if (ch === '%') {
			w += digit * 1.6;
		} else if ('.,:;\'’'.includes(ch)) {
			w += digit * 0.45;
		} else if (ch === ' ') {
			w += digit * 0.45;
		} else if (/[A-Z]/.test(ch)) {
			w += digit * 1.15;
		} else {
			w += digit;
		}
	}
	return w;
};
