// Brand kits: a full theme from one or two brand colours. The grounds and greys take a whisper of the brand's hue
// (tinted neutrals), text on the brand colour is picked for contrast, and the brand colour itself is kept exact.
import {makeTheme, type ThemeName, type ThemeSpec} from '../core';
import {oklch, readableOn, toOklch} from './color';

export type BrandOptions = {
	primary: string; // the brand colour: becomes the accent, unchanged
	secondary?: string; // a second brand colour for accent2 (default: a counterpart about 160 degrees round the wheel)
	dark?: boolean; // a dark ground (default false)
	base?: ThemeName | ThemeSpec; // fonts, weights, motion and radius come from here (default studio, or midnight when dark)
	neutral?: 'tinted' | 'pure'; // grounds and greys tinted by the brand hue (default) or plain grey
	fonts?: Partial<ThemeSpec['fonts']>;
	radius?: number;
	name?: string;
	grain?: number; // texture.grain (default the base theme's)
	vignette?: number;
};

/**
 * A ThemeSpec for a brand: `<ThemeProvider theme={brandTheme({primary: '#E4002B'})}>`. Check the result with
 * `contrast()` if the brand colour is very light (yellow, lime): it stays the accent fill, and components that put
 * accent-coloured text on the ground push it to a readable shade with `ensureContrast()`.
 */
export const brandTheme = (o: BrandOptions): ThemeSpec => {
	const dark = o.dark ?? false;
	const p = toOklch(o.primary);
	const h = p.h;
	const tint = o.neutral === 'pure' ? 0 : Math.min(dark ? 0.016 : 0.008, p.c * (dark ? 0.1 : 0.06));
	const second = o.secondary ?? oklch(Math.min(0.8, Math.max(0.55, p.l)), Math.min(0.17, Math.max(0.09, p.c * 0.9)), (h + 160) % 360);
	const s = toOklch(second);
	const colors = dark
		? {
				bg: oklch(0.17, tint, h),
				bg2: oklch(0.21, tint, h),
				surface: oklch(0.235, tint * 1.1, h),
				text: oklch(0.97, tint * 0.4, h),
				muted: oklch(0.73, tint * 1.3, h),
				faint: oklch(0.42, tint * 1.4, h),
				line: oklch(0.31, tint * 1.2, h),
				highlight: oklch(0.84, Math.min(0.15, s.c), s.h),
			}
		: {
				bg: oklch(0.975, tint, h),
				bg2: oklch(0.995, tint * 0.5, h),
				surface: '#FFFFFF',
				text: oklch(0.21, tint * 2.2, h),
				muted: oklch(0.5, tint * 2, h),
				faint: oklch(0.84, tint * 1.5, h),
				line: oklch(0.915, tint * 1.2, h),
				highlight: oklch(0.91, Math.min(0.13, s.c * 0.8), s.h),
			};
	return makeTheme(o.base ?? (dark ? 'midnight' : 'studio'), {
		name: o.name ?? 'brand',
		description: `Brand kit from ${o.primary}${o.secondary ? ` and ${o.secondary}` : ''}`,
		dark,
		radius: o.radius,
		fonts: o.fonts,
		colors: {
			...colors,
			accent: o.primary,
			accent2: second,
			onAccent: readableOn(o.primary, '#FFFFFF', colors.text),
		},
		texture: {...(o.grain !== undefined ? {grain: o.grain} : null), ...(o.vignette !== undefined ? {vignette: o.vignette} : null)},
	});
};
