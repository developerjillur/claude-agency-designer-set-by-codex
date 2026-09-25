// Measuring a box whose size comes from its text (a callout body, a word to circle). The frame is held with
// delayRender until the fonts have loaded (document.fonts and Remotion's own font handles) and the measured size
// has been committed, so a render never captures a size taken with a fallback font. offsetWidth/offsetHeight are
// layout sizes: a parent's CSS scale does not change them. With `lines`, the widest line of wrapped text is
// measured too (a wrapped box keeps its maximum width, so a bubble would otherwise show empty space beside
// balanced lines).
import {waitForKitFonts} from '../core';
import {useEffect, useLayoutEffect, useRef, useState, type RefObject} from 'react';
import {useDelayRender} from 'remotion';

export type MeasuredSize = {w: number; h: number; line?: number};

const widestLine = (node: HTMLElement): number | undefined => {
	if (typeof document === 'undefined' || !document.createRange) {
		return undefined;
	}
	// line boxes of the text only (a range over whole elements would also return their full-width boxes)
	const rects: DOMRect[] = [];
	const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
	for (let n = walker.nextNode(); n; n = walker.nextNode()) {
		if (!n.textContent || !n.textContent.trim()) {
			continue;
		}
		const range = document.createRange();
		range.selectNodeContents(n);
		rects.push(...Array.from(range.getClientRects()));
	}
	if (!rects.length) {
		return undefined;
	}
	// fragments on the same line (mixed inline styles) join into one line: from its leftmost to its rightmost edge
	const lines: {top: number; bottom: number; left: number; right: number}[] = [];
	for (const r of rects) {
		const mid = (r.top + r.bottom) / 2;
		const hit = lines.find((l) => mid >= l.top && mid <= l.bottom);
		if (hit) {
			hit.left = Math.min(hit.left, r.left);
			hit.right = Math.max(hit.right, r.right);
		} else {
			lines.push({top: r.top, bottom: r.bottom, left: r.left, right: r.right});
		}
	}
	// client rects are after transforms (a pop-in scale); bring them back to layout px
	const scale = node.offsetWidth > 0 ? node.getBoundingClientRect().width / node.offsetWidth : 1;
	const k = scale > 0.01 ? scale : 1;
	return Math.max(...lines.map((l) => l.right - l.left)) / k;
};

/**
 * Resolves when every kit font requested so far has loaded (core keeps each loader's promise: document.fonts.ready
 * alone can resolve before a Google font is added). After 25 s it measures anyway and says so, below Remotion's
 * 30 s delayRender timeout.
 */
const waitForFonts = (): Promise<void> =>
	Promise.race([
		waitForKitFonts(),
		new Promise<void>((resolve) => {
			setTimeout(() => {
				console.warn('graphics: a font was still loading after 25 s; measuring anyway');
				resolve();
			}, 25000);
		}),
	]);

export const useMeasuredSize = (
	ref: RefObject<HTMLElement | null>,
	label = 'graphics: measuring a box',
	opts: {lines?: boolean} = {},
): MeasuredSize | null => {
	const [size, setSize] = useState<MeasuredSize | null>(null);
	const [fontsReady, setFontsReady] = useState(false);
	const {delayRender, continueRender} = useDelayRender();
	const [handle] = useState(() => delayRender(label));
	const released = useRef(false);
	const lines = !!opts.lines;

	const measure = useRef<() => void>(() => undefined);
	measure.current = () => {
		// read the ref at call time; skip a node that has left the document (it measures 0)
		const node = ref.current;
		if (!node || !node.isConnected) {
			return;
		}
		const w = node.offsetWidth;
		const h = node.offsetHeight;
		const line = lines ? widestLine(node) : undefined;
		const lineR = line === undefined ? undefined : Math.ceil(line);
		setSize((prev) => {
			// a changing transform adds sub-pixel noise to the line: ignore changes of 1 px or less
			const keepLine = prev?.line !== undefined && lineR !== undefined && Math.abs(prev.line - lineR) <= 1;
			const nextLine = keepLine ? prev?.line : lineR;
			return prev && prev.w === w && prev.h === h && prev.line === nextLine ? prev : {w, h, line: nextLine};
		});
	};

	// every render: a font that finished loading after the first measurement changes line widths without
	// changing the box (so no ResizeObserver event); measuring each frame keeps the size true to what is painted
	useLayoutEffect(() => {
		measure.current();
	});

	useLayoutEffect(() => {
		const el = ref.current;
		if (!el) {
			setFontsReady(true);
			return;
		}
		let alive = true;
		const run = () => alive && measure.current();
		const ro = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(run);
		ro?.observe(el);
		const fontSet = typeof document !== 'undefined' ? document.fonts : undefined;
		fontSet?.addEventListener?.('loadingdone', run);
		const fonts = fontSet ? fontSet.ready : Promise.resolve();
		Promise.all([fonts, waitForFonts()]).then(() => {
			run();
			if (alive) {
				setFontsReady(true);
			}
		});
		return () => {
			alive = false;
			ro?.disconnect();
			fontSet?.removeEventListener?.('loadingdone', run);
		};
		// set up once per mount
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	// released once the size measured after the fonts loaded is committed to the DOM
	useEffect(() => {
		if (fontsReady && !released.current) {
			released.current = true;
			continueRender(handle);
		}
	}, [fontsReady, size, continueRender, handle]);

	// unmounted before the fonts settled: never leave the render waiting
	useEffect(
		() => () => {
			if (!released.current) {
				released.current = true;
				continueRender(handle);
			}
		},
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[],
	);

	return size;
};
