// Type settings from the theme (family, weight, tracking, leading per role) and a way to wait until the theme's
// fonts have really loaded before anything is measured. Core loads the fonts; measuring before they arrive gives
// fallback-font widths that @remotion/layout-utils then caches for the whole page, so every component that
// measures text waits for `useTypeFontsReady()` first.
import React, {useEffect, useState} from 'react';
import {useDelayRender} from 'remotion';
import {FONTS, useTheme, type FontKey, type Theme} from '../core';
import type {TypeStyle} from './layout';
import {isComplexScript} from './text';

export type FontRole = 'display' | 'body' | 'mono' | 'serif' | 'hand' | 'bangla';

export type FontNeed = {key: FontKey; weights: readonly number[]; style?: 'normal' | 'italic'};

type LoaderResult = {fontFamily: string; waitUntilDone?: () => Promise<void>};
type AnyLoader = (
	style?: 'normal' | 'italic',
	options?: {weights?: string[]; subsets?: string[]; ignoreTooManyRequestsWarning?: boolean},
) => LoaderResult;

const nearest = (weights: readonly number[], w: number): number =>
	weights.reduce((a, b) => (Math.abs(b - w) < Math.abs(a - w) ? b : a));

const waits = new Map<string, Promise<void>>();

/**
 * Resolves when a kit font (the same weights core's loadKitFont asks for) has loaded. The Google Fonts loader keeps
 * one request per weight and subset, so this never downloads twice; it only returns the loader's waitUntilDone().
 */
export const waitForTypeFont = (need: FontNeed): Promise<void> => {
	const spec = FONTS[need.key];
	const use = [...new Set(need.weights.map((w) => nearest(spec.weights, w)))].sort((a, b) => a - b);
	const st = need.style === 'italic' && spec.italic ? 'italic' : 'normal';
	const id = `${need.key}|${st}|${use.join(',')}`;
	const hit = waits.get(id);
	if (hit) {
		return hit;
	}
	const load = spec.load as unknown as AnyLoader;
	const res = load(st, {weights: use.map(String), subsets: [...spec.subsets], ignoreTooManyRequestsWarning: true});
	const p = res.waitUntilDone ? res.waitUntilDone() : Promise.resolve();
	waits.set(id, p);
	return p;
};

/** The fonts a theme role uses, exactly as core's resolveTheme loads them (the role's font plus the Bangla one). */
export const fontNeeds = (t: Theme, role: FontRole): FontNeed[] => {
	const {fonts, weights} = t;
	const withBangla = (key: FontKey, w: number[]): FontNeed[] =>
		FONTS[key].bangla ? [{key, weights: w}] : [{key, weights: w}, {key: fonts.bangla, weights: w}];
	switch (role) {
		case 'display':
			return withBangla(fonts.display, [weights.display]);
		case 'body':
			return withBangla(fonts.body, [weights.body, weights.strong]);
		case 'mono':
			return withBangla(fonts.mono, [400, 600]);
		case 'serif':
			return withBangla(fonts.serif ?? fonts.display, [400, 700]);
		case 'hand':
			return withBangla(fonts.hand ?? fonts.body, [400, 700]);
		case 'bangla':
		default:
			return [{key: fonts.bangla, weights: [weights.body, weights.strong, weights.display]}];
	}
};

const settled = new Set<string>();

/**
 * True once the fonts of the given roles (and any extra kit fonts) have loaded. Until then it holds the render with
 * a delayRender handle made in a useState initializer, so a frame is never captured with fallback measurements.
 */
export const useTypeFontsReady = (roles: FontRole | readonly FontRole[] = 'display', extra: readonly FontNeed[] = []): boolean => {
	const t = useTheme();
	const list = typeof roles === 'string' ? [roles] : roles;
	const needs = [...list.flatMap((r) => fontNeeds(t, r)), ...extra];
	const key = needs.map((n) => `${n.key}:${n.weights.join('.')}:${n.style ?? 'normal'}`).join('|');
	const {delayRender, continueRender, cancelRender} = useDelayRender();
	const [readyKey, setReadyKey] = useState<string | null>(() => (settled.has(key) ? key : null));
	const [handle] = useState<number | null>(() => (settled.has(key) ? null : delayRender(`Fonts for measured text (${key})`)));

	useEffect(() => {
		if (readyKey === key) {
			return;
		}
		let live = true;
		Promise.all(needs.map(waitForTypeFont))
			.then(() => (typeof document === 'undefined' ? undefined : document.fonts.ready))
			.then(() => {
				settled.add(key);
				if (live) {
					setReadyKey(key);
				}
			})
			.catch((err) => cancelRender(err));
		return () => {
			live = false;
		};
		// `needs` is derived from `key`, so `key` is the dependency
	}, [key, readyKey, cancelRender]);

	useEffect(() => {
		if (readyKey === key && handle !== null) {
			continueRender(handle);
		}
	}, [readyKey, key, handle, continueRender]);

	// release the handle if the component leaves before the fonts arrived (Studio scrubbing)
	useEffect(
		() => () => {
			if (handle !== null) {
				continueRender(handle);
			}
		},
		[handle, continueRender],
	);

	return readyKey === key;
};

/** Renders its children only after the fonts of `roles` have loaded (for your own measuring code). */
export const WaitForFonts: React.FC<{roles?: FontRole | FontRole[]; extra?: FontNeed[]; children: React.ReactNode}> = ({
	roles = ['display', 'body'],
	extra = [],
	children,
}) => {
	const ready = useTypeFontsReady(roles, extra);
	return ready ? <>{children}</> : null;
};

/** The CSS family stack of a role (fonts loaded by core, Bangla fallback included). */
export const roleFamily = (t: Theme, role: FontRole): string => t.type[role];

/** The weight a role is set in: display weight for display, body or strong for body, 400 or 700 for the rest. */
export const roleWeight = (t: Theme, role: FontRole, strong = false): number => {
	switch (role) {
		case 'display':
			return t.weights.display;
		case 'body':
		case 'bangla':
			return strong ? t.weights.strong : t.weights.body;
		case 'mono':
			return strong ? 600 : 400;
		default:
			return strong ? 700 : 400;
	}
};

/**
 * Letter spacing in em for text of `size` px (at 1080) in a role. Big display type tightens toward the theme's
 * display tracking (never tighter than -0.05em), small caps open up, and Bangla or other complex scripts get 0:
 * any tracking breaks the matra line and the conjunct shapes.
 */
export const trackingFor = (t: Theme, size: number, text: string, role: FontRole = 'display', caps = false): number => {
	if (isComplexScript(text)) {
		return 0;
	}
	if (caps && size < 48) {
		return t.tracking.caps;
	}
	if (role !== 'display' && role !== 'serif') {
		return size >= 64 ? Math.max(-0.03, t.tracking.display * 0.6) : 0;
	}
	const base = t.tracking.display;
	const k = size <= 40 ? 0 : size >= 100 ? (size >= 200 ? 1.15 : 1) : (size - 40) / 60;
	return Math.max(-0.05, Math.min(0.2, base * k));
};

/**
 * Line height for text of `size` px (at 1080). Display type sets tight (1.0 to 1.1); Bangla needs room for vowel
 * signs above the matra and below-base forms, so it never goes under 1.25.
 */
export const leadingFor = (text: string, size: number, role: FontRole = 'display'): number => {
	const complex = isComplexScript(text);
	if (role === 'display' || role === 'serif') {
		const latin = size >= 160 ? 0.98 : size >= 100 ? 1.02 : size >= 64 ? 1.08 : 1.15;
		return complex ? Math.max(1.28, latin + 0.24) : latin;
	}
	return complex ? 1.5 : size >= 56 ? 1.2 : 1.35;
};

/** Mask padding (em) so a clipping mask never cuts accents, descenders or Bangla vowel signs. */
export const maskPad = (text: string): {top: number; bottom: number} =>
	isComplexScript(text) ? {top: 0.34, bottom: 0.3} : {top: 0.14, bottom: 0.22};

/** Type props shared by the text components (sizes in px at 1080). */
export type TypeProps = {
	role?: FontRole; // which theme family (default differs per component)
	size?: number; // px at 1080
	weight?: number;
	strong?: boolean; // the strong weight of body text
	caps?: boolean; // default: the theme's caps setting for display type
	tracking?: number; // em; default from trackingFor()
	lineHeight?: number; // default from leadingFor()
	fontFamily?: string; // a CSS stack instead of the role's (load it through core, and pass `fonts` to wait for it)
	color?: string;
};

/** A measured-and-rendered text style from the theme and TypeProps. */
export const typeStyle = (t: Theme, unit: number, text: string, p: TypeProps, fallbackSize: number, fallbackRole: FontRole = 'display'): TypeStyle => {
	const role = p.role ?? fallbackRole;
	const size = p.size ?? fallbackSize;
	const caps = p.caps ?? (role === 'display' ? t.caps : false);
	return {
		fontFamily: p.fontFamily ?? roleFamily(t, role),
		fontWeight: p.weight ?? roleWeight(t, role, p.strong),
		fontSize: size * unit,
		letterSpacing: p.tracking ?? trackingFor(t, size, text, role, caps),
		lineHeight: p.lineHeight ?? leadingFor(text, size, role),
		textTransform: caps ? 'uppercase' : 'none',
	};
};
