// Themes: a palette, a type system, a motion character and a texture amount. Components read the theme from
// context, so one <ThemeProvider theme="vox"> restyles a whole video. makeTheme() derives a brand kit.
import React, {createContext, useContext, useMemo} from 'react';
import type {CurveName, SpringName} from './easing';
import {fontStack, type FontKey} from './fonts';
import {THEMES, type ThemeName} from './themes';

export type Palette = {
	bg: string; // the ground
	bg2: string; // a second ground (bands, alternating scenes)
	surface: string; // cards, panels
	text: string;
	muted: string; // secondary text
	faint: string; // tertiary, gridlines, disabled
	line: string; // borders, rules
	accent: string; // the one colour with a budget (fills, bars, lines)
	accentText: string; // the accent as small text on bg: at least 4.5:1
	accent2: string; // a second accent for contrast or a second series
	highlight: string; // marker sweeps behind words
	positive: string;
	negative: string;
	onAccent: string; // text on an accent fill: at least 4.5:1
};

export type EnterStyle = 'rise' | 'pop' | 'fade' | 'mask' | 'blur' | 'left' | 'wipe';

export type ThemeSpec = {
	name: string;
	description: string;
	dark: boolean;
	colors: Palette;
	fonts: {display: FontKey; body: FontKey; mono: FontKey; bangla: FontKey; serif?: FontKey; hand?: FontKey};
	weights: {display: number; body: number; strong: number};
	tracking: {display: number; caps: number}; // em
	caps: boolean; // set display type in capitals
	radius: number; // px at 1080
	motion: {
		enter: EnterStyle;
		enterFrames: number; // at 30 fps; scaled for other rates
		exitFrames: number;
		stagger: number;
		distance: number; // px at 1080 for rises and slides
		curve: CurveName;
		spring: SpringName;
	};
	texture: {grain: number; vignette: number; grainRate: number}; // amounts 0 to 1; grainRate: new grain plates a second (file size grows fast with it)
};

export type Theme = ThemeSpec & {
	/** Resolved CSS font-family stacks (fonts loaded, Bangla fallback included). */
	type: {display: string; body: string; mono: string; serif: string; hand: string; bangla: string};
};

export const resolveTheme = (spec: ThemeSpec): Theme => {
	const {weights, fonts} = spec;
	const bangla = fonts.bangla;
	return {
		...spec,
		type: {
			display: fontStack(fonts.display, [weights.display], bangla),
			body: fontStack(fonts.body, [weights.body, weights.strong], bangla),
			mono: fontStack(fonts.mono, [400, 600], bangla),
			serif: fontStack(fonts.serif ?? fonts.display, [400, 700], bangla),
			hand: fontStack(fonts.hand ?? fonts.body, [400, 700], bangla),
			bangla: fontStack(bangla, [weights.body, weights.strong, weights.display], null),
		},
	};
};

export type ThemeOverrides = {
	name?: string;
	description?: string;
	dark?: boolean;
	colors?: Partial<Palette>;
	fonts?: Partial<ThemeSpec['fonts']>;
	weights?: Partial<ThemeSpec['weights']>;
	tracking?: Partial<ThemeSpec['tracking']>;
	caps?: boolean;
	radius?: number;
	motion?: Partial<ThemeSpec['motion']>;
	texture?: Partial<ThemeSpec['texture']>;
};

/** A theme from a named base with some parts replaced: a brand kit is usually colours and fonts. */
export const makeTheme = (base: ThemeName | ThemeSpec, o: ThemeOverrides = {}): ThemeSpec => {
	const b = typeof base === 'string' ? THEMES[base] : base;
	return {
		...b,
		name: o.name ?? b.name,
		description: o.description ?? b.description,
		dark: o.dark ?? b.dark,
		caps: o.caps ?? b.caps,
		radius: o.radius ?? b.radius,
		colors: {...b.colors, ...o.colors},
		fonts: {...b.fonts, ...o.fonts},
		weights: {...b.weights, ...o.weights},
		tracking: {...b.tracking, ...o.tracking},
		motion: {...b.motion, ...o.motion},
		texture: {...b.texture, ...o.texture},
	};
};

const ThemeContext = createContext<Theme | null>(null);

export const ThemeProvider: React.FC<{theme?: ThemeName | ThemeSpec; children: React.ReactNode}> = ({
	theme = 'studio',
	children,
}) => {
	const value = useMemo(() => resolveTheme(typeof theme === 'string' ? THEMES[theme] : theme), [theme]);
	return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

/** The current theme; the studio theme when no provider is above. */
export const useTheme = (): Theme => {
	const t = useContext(ThemeContext);
	return t ?? resolveTheme(THEMES.studio);
};
