// Design tokens that go with the themes: elevation shadows (levels 0 to 5, lit from above, tinted by the ground),
// a spacing scale and surface colours for dark themes (higher surfaces are lighter, since shadows vanish on dark).
import type {Theme} from '../core';
import {lighten, mix, shadowTint, withAlpha} from './color';

export type Elevation = 0 | 1 | 2 | 3 | 4 | 5;

// [y offset, blur, alpha] for a tight key shadow and a soft ambient one, px at 1080. The light is above the frame,
// so shadows fall straight down and grow with height; blur grows faster than offset, like a real soft light.
const KEY: [number, number, number][] = [
	[0, 0, 0],
	[1, 2, 0.13],
	[2, 5, 0.12],
	[3, 8, 0.11],
	[5, 12, 0.1],
	[8, 18, 0.1],
];
const AMBIENT: [number, number, number][] = [
	[0, 0, 0],
	[3, 8, 0.08],
	[8, 20, 0.11],
	[14, 34, 0.14],
	[24, 52, 0.18],
	[38, 84, 0.24],
];

const clampLevel = (level: number): Elevation => Math.max(0, Math.min(5, Math.round(level))) as Elevation;

/**
 * A CSS box-shadow for an elevation level (0 flat to 5 floating). On light grounds the shadow takes the ground's
 * hue (warm paper gets warm shadows); on dark grounds it is black and stronger, because a soft shadow barely shows
 * there (pair it with `surfaceAt` so higher cards are also lighter).
 */
export const elevation = (level: number, t: Theme, unit = 1, color?: string): string => {
	const lv = clampLevel(level);
	if (lv === 0) {
		return 'none';
	}
	const tint = color ?? (t.dark ? '#000000' : shadowTint(t.colors.bg));
	const boost = t.dark ? 3.2 : 1;
	const [ky, kb, ka] = KEY[lv];
	const [ay, ab, aa] = AMBIENT[lv];
	const px = (v: number) => `${Math.round(v * unit * 10) / 10}px`;
	return [
		`0 ${px(ky)} ${px(kb)} ${withAlpha(tint, Math.min(0.6, ka * boost))}`,
		`0 ${px(ay)} ${px(ab)} ${px(-ay * 0.25)} ${withAlpha(tint, Math.min(0.7, aa * boost))}`,
	].join(', ');
};

/** The surface colour for an elevation: the theme's surface, a step lighter per level on dark themes. */
export const surfaceAt = (level: number, t: Theme): string =>
	t.dark ? lighten(t.colors.surface, clampLevel(level) * 0.012) : t.colors.surface;

/** A hairline border colour for a surface: text at a few percent on light, white at a few percent on dark. */
export const hairline = (t: Theme, strength = 1): string =>
	t.dark ? withAlpha('#FFFFFF', 0.09 * strength) : withAlpha(t.colors.text, 0.08 * strength);

/** Spacing steps, px at 1080. Use one step between siblings and a bigger step between groups. */
export const SPACE = {xs: 8, sm: 16, md: 24, lg: 40, xl: 64, xxl: 96, huge: 144} as const;
export type SpaceName = keyof typeof SPACE;

/** A spacing step (or a number) in px for the current frame size. */
export const space = (s: SpaceName | number, unit = 1): number => (typeof s === 'number' ? s : SPACE[s]) * unit;

/** A tonal fill: the ground tinted towards a colour (default the accent), for flat grouping without shadows. */
export const tonal = (t: Theme, color?: string, amount?: number): string =>
	mix(t.colors.bg, color ?? t.colors.accent, amount ?? (t.dark ? 0.16 : 0.1));
