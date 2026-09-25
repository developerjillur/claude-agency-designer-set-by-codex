// Effect presets: small wrappers around @remotion/effects with designed defaults and clamped parameters, so an
// animated value can never push an effect outside its valid range (an invalid value fails the render). Every
// effect is imported from its own subpath: the package root only exports 11 of the 74.
//
// Pixel parameters (radius, amount in px, dot size, spacing) are canvas pixels of the host: a 1920 x 1080 Img or
// HtmlInCanvas at pixelDensity 1. Multiply them by `unit` (useStage) at 4K or by pixelDensity when it is above 1.
import {barrelDistortion} from '@remotion/effects/barrel-distortion';
import {blur as blurFx} from '@remotion/effects/blur';
import {chromaticAberration} from '@remotion/effects/chromatic-aberration';
import {colorCorrection, type ColorCorrectionParams} from '@remotion/effects/color-correction';
import {colorKey} from '@remotion/effects/color-key';
import {dropShadow} from '@remotion/effects/drop-shadow';
import {duotone as duotoneFx} from '@remotion/effects/duotone';
import {evolve} from '@remotion/effects/evolve';
import {exposure} from '@remotion/effects/exposure';
import {glow} from '@remotion/effects/glow';
import {grayscale} from '@remotion/effects/grayscale';
import {halftone} from '@remotion/effects/halftone';
import {hue} from '@remotion/effects/hue';
import {levels} from '@remotion/effects/levels';
import {lightLeak} from '@remotion/effects/light-leak';
import {lut} from '@remotion/effects/lut';
import {noise} from '@remotion/effects/noise';
import {outline} from '@remotion/effects/outline';
import {paper} from '@remotion/effects/paper';
import {pixelDissolve} from '@remotion/effects/pixel-dissolve';
import {pixelate} from '@remotion/effects/pixelate';
import {radialProgressiveBlur} from '@remotion/effects/radial-progressive-blur';
import {saturation} from '@remotion/effects/saturation';
import {scanlines} from '@remotion/effects/scanlines';
import {shine} from '@remotion/effects/shine';
import {speckle} from '@remotion/effects/speckle';
import {starburst} from '@remotion/effects/starburst';
import {tear} from '@remotion/effects/tear';
import {thermalVision} from '@remotion/effects/thermal-vision';
import {xyTranslate} from '@remotion/effects/translate';
import {tvSignalOff} from '@remotion/effects/tv-signal-off';
import {vignette} from '@remotion/effects/vignette';
import {wave} from '@remotion/effects/wave';
import {whiteNoise} from '@remotion/effects/white-noise';
import {zoomBlur} from '@remotion/effects/zoom-blur';
import type {EffectDescriptor} from 'remotion';
import {posterize, sliceShift} from './custom-effects';
import {clampTo, finite, nonNegative, stepSeed, unit01, uv01, wrap360, type Uv} from './util';

export type Fx = EffectDescriptor<unknown>;

const off = (disabled: boolean | undefined) => (disabled ? {disabled: true} : {});

// ---------------------------------------------------------------- grades (colorCorrection parameter sets)

/** Named colorCorrection settings for footage and photos: pass one to fx.colorCorrection, then tweak. */
export const grades = {
	/** Clean, a little contrast and warmth: the safe default for stock footage. */
	natural: {contrast: 1.06, shadows: 0.05, highlights: -0.08, temperature: 0.04, vibrance: 0.1},
	/** Teal shadows feel, warm skin, deeper blacks: trailers and brand films. */
	cinematic: {contrast: 1.12, shadows: 0.12, highlights: -0.18, blacks: -0.05, temperature: 0.12, saturation: 0.92, vibrance: 0.15},
	/** Faded print: lifted blacks, softer contrast, warm, less saturated. */
	warmFilm: {contrast: 0.92, blacks: 0.22, highlights: -0.1, temperature: 0.22, tint: 0.04, saturation: 0.82},
	/** Blue hour: cool, crisp, slightly darker. */
	coolNight: {exposure: -0.15, contrast: 1.08, temperature: -0.28, tint: -0.03, saturation: 0.9, vibrance: 0.1},
	/** Bleach bypass: silvery, high contrast, desaturated. */
	bleach: {contrast: 1.28, highlights: -0.12, blacks: -0.08, saturation: 0.45},
	/** Bright social look: punchy colour, open shadows. */
	punchy: {exposure: 0.08, contrast: 1.1, shadows: 0.15, saturation: 1.12, vibrance: 0.3},
	/** Black and white with body. */
	mono: {contrast: 1.2, saturation: 0, shadows: 0.06, highlights: -0.1},
} satisfies Record<string, ColorCorrectionParams>;

export type GradeName = keyof typeof grades;

export type ShapeKind = 'circle' | 'square' | 'line';

// ---------------------------------------------------------------- the presets

export const fx = {
	// ------------------------------------------------ colour and tone (footage grade)

	/** One-pass grade (exposure, white balance, tonal regions, contrast, saturation, vibrance). Identity by default. */
	colorCorrection: (o: ColorCorrectionParams & {disabled?: boolean} = {}): Fx =>
		colorCorrection({
			exposure: clampTo(o.exposure, -5, 5, 0),
			contrast: nonNegative(o.contrast, 1),
			pivot: unit01(o.pivot, 0.5),
			shadows: clampTo(o.shadows, -1, 1, 0),
			highlights: clampTo(o.highlights, -1, 1, 0),
			whites: clampTo(o.whites, -1, 1, 0),
			blacks: clampTo(o.blacks, -1, 1, 0),
			temperature: clampTo(o.temperature, -1, 1, 0),
			tint: clampTo(o.tint, -1, 1, 0),
			saturation: nonNegative(o.saturation, 1),
			vibrance: clampTo(o.vibrance, -1, 1, 0),
			...off(o.disabled),
		}),

	/** A named grade from `grades`, optionally scaled toward identity with `amount` (0 to 1). */
	grade: (name: GradeName, amount = 1): Fx => {
		const g: ColorCorrectionParams = grades[name];
		const k = unit01(amount, 1);
		const lerp = (v: number | undefined, id: number) => id + (finite(v, id) - id) * k;
		return fx.colorCorrection({
			exposure: lerp(g.exposure, 0),
			contrast: lerp(g.contrast, 1),
			shadows: lerp(g.shadows, 0),
			highlights: lerp(g.highlights, 0),
			whites: lerp(g.whites, 0),
			blacks: lerp(g.blacks, 0),
			temperature: lerp(g.temperature, 0),
			tint: lerp(g.tint, 0),
			saturation: lerp(g.saturation, 1),
			vibrance: lerp(g.vibrance, 0),
		});
	},

	/** Exposure in stops (-5 to 5): a natural brighten or darken that keeps tonal relationships. */
	exposure: (stops = 0): Fx => exposure({stops: clampTo(stops, -5, 5, 0)}),

	/** Levels: black point below white point (a 0.01 gap is kept), gamma above 1 lifts the midtones. */
	levels: (o: {black?: number; white?: number; gamma?: number} = {}): Fx => {
		const white = clampTo(o.white, 0.01, 1, 1);
		const black = clampTo(o.black, 0, white - 0.01, 0);
		return levels({blackPoint: black, whitePoint: white, gamma: clampTo(o.gamma, 0.01, 10, 1)});
	},

	/** A 3D .cube LUT (text). See makeCubeLut and useLutFile. */
	lut: (content: string): Fx => lut({content}),

	/** Saturation multiplier (2D canvas filter, cheap). */
	saturation: (amount = 1): Fx => saturation({amount: nonNegative(amount, 1)}),

	/** Hue rotation in degrees (2D canvas filter). */
	hue: (degrees = 0): Fx => hue({degrees: finite(degrees, 0)}),

	/** Black and white (2D canvas filter). */
	grayscale: (amount = 1): Fx => grayscale({amount: unit01(amount, 1)}),

	// ------------------------------------------------ film and texture

	/**
	 * Film grain re-rolled `hz` times a second (12 by default). Pass the frame and fps; `premultiply` keeps the
	 * blacks clean like real film. Put it last in a chain so nothing blurs or grades it.
	 */
	grain: (o: {frame?: number; fps?: number; amount?: number; hz?: number; seed?: number; premultiply?: boolean} = {}): Fx =>
		noise({
			amount: unit01(o.amount, 0.06),
			seed: finite(o.seed, 0) + (o.frame === undefined ? 0 : stepSeed(o.frame, o.fps ?? 30, o.hz ?? 12)),
			premultiply: o.premultiply ?? true,
		}),

	/** Plain noise (`noise()`), for dithering gradients: 0.02 to 0.04 hides 8-bit banding. */
	noise: (o: {amount?: number; seed?: number; premultiply?: boolean} = {}): Fx =>
		noise({amount: unit01(o.amount, 0.03), seed: finite(o.seed, 0), premultiply: o.premultiply ?? false}),

	/** TV static blended toward random grey. Change the seed every frame (it is electronic, not film). */
	staticNoise: (o: {amount?: number; seed?: number} = {}): Fx =>
		whiteNoise({amount: unit01(o.amount, 0.25), seed: finite(o.seed, 0)}),

	/** Dust: small transparent holes that show the layer behind (put a light ground behind for film dust). */
	dust: (o: {density?: number; size?: number; randomness?: number} = {}): Fx =>
		speckle({density: unit01(o.density, 0.02), size: nonNegative(o.size, 3), randomness: unit01(o.randomness, 1)}),

	/** Vignette in UV space (follows the frame's aspect). Weak is better: corners about 0.15 to 0.35 darker. */
	vignette: (o: {amount?: number; radius?: number; feather?: number; roundness?: number; color?: string; mode?: 'color' | 'alpha'; center?: Uv} = {}): Fx =>
		vignette({
			amount: unit01(o.amount, 0.35),
			radius: unit01(o.radius, 0.72),
			feather: unit01(o.feather, 0.5),
			roundness: unit01(o.roundness, 1),
			color: o.color ?? '#000000',
			mode: o.mode ?? 'color',
			center: [finite(o.center?.[0], 0.5), finite(o.center?.[1], 0.5)],
		}),

	/** Paper grain, fibres, crumples and folds over the source (heaviest single pass). Seed 0 to 1000. */
	paper: (o: {amount?: number; seed?: number; front?: string; back?: string; folds?: number; crumples?: number; roughness?: number; scale?: number} = {}): Fx =>
		paper({
			amount: unit01(o.amount, 0.6),
			seed: clampTo(o.seed, 0, 1000, 6),
			colorFront: o.front ?? '#c9bfae',
			colorBack: o.back ?? '#fbf7ee',
			folds: unit01(o.folds, 0.25),
			crumples: unit01(o.crumples, 0.2),
			roughness: unit01(o.roughness, 0.35),
			scale: clampTo(o.scale, 0.01, 4, 0.6),
		}),

	// ------------------------------------------------ light

	/** Monochrome additive halo. Raise `threshold` on footage so only highlights glow. */
	glow: (o: {radius?: number; intensity?: number; threshold?: number; color?: string} = {}): Fx =>
		glow({
			radius: nonNegative(o.radius, 18),
			intensity: nonNegative(o.intensity, 0.9),
			threshold: unit01(o.threshold, 0.55),
			color: o.color ?? '#ffffff',
		}),

	/** Light leak over the source: reveals over progress 0 to 0.5, retracts to 1. Hue is wrapped into 0 to 360. */
	lightLeak: (o: {progress: number; seed?: number; hue?: number}): Fx =>
		lightLeak({progress: unit01(o.progress, 0.5), seed: finite(o.seed, 0), hueShift: wrap360(o.hue ?? 0)}),

	/** A white sweep masked by the source alpha: progress 0 enters, 1 leaves. `width` scales the band. */
	shine: (o: {progress: number; angle?: number; width?: number; intensity?: number}): Fx => {
		const w = Math.max(0.05, finite(o.width, 1));
		const k = nonNegative(o.intensity, 1);
		return shine({
			progress: unit01(o.progress, 0.5),
			angle: finite(o.angle, 30),
			haloSigma: 200 * w,
			coreSigma: 65 * w,
			haloIntensity: unit01(0.3 * k, 0.3),
			coreIntensity: unit01(0.4 * k, 0.4),
		});
	},

	/** Rays from an origin (replaces the source: use it on a Solid). Rotation is free; smoothness anti-aliases. */
	starburst: (o: {colors: readonly string[]; rays?: number; rotation?: number; smoothness?: number; origin?: Uv}): Fx =>
		starburst({
			rays: Math.round(clampTo(o.rays, 2, 100, 24)),
			colors: o.colors.length >= 2 ? o.colors : [o.colors[0] ?? '#ffffff', o.colors[0] ?? '#ffffff'],
			rotation: finite(o.rotation, 0),
			smoothness: unit01(o.smoothness, 0.03),
			origin: uv01(o.origin),
		}),

	// ------------------------------------------------ lens and signal

	/** RGB split in px (red one way, blue the other). angle 0 is horizontal. */
	chromaticAberration: (o: {amount?: number; angle?: number; disabled?: boolean} = {}): Fx =>
		chromaticAberration({amount: nonNegative(o.amount, 3), angle: finite(o.angle, 0), ...off(o.disabled)}),

	/** Horizontal scanlines; animate `offset` to roll them. `premultiply` follows the image brightness. */
	scanlines: (o: {amount?: number; spacing?: number; thickness?: number; offset?: number; premultiply?: boolean} = {}): Fx => {
		const spacing = Math.max(0.5, finite(o.spacing, 4));
		return scanlines({
			amount: unit01(o.amount, 0.18),
			spacing,
			thickness: clampTo(o.thickness, 0, spacing, 1.5),
			offset: finite(o.offset, 0),
			premultiply: o.premultiply ?? true,
		});
	},

	/** CRT curvature (0 to 1). Corners become transparent: keep a dark layer behind. */
	barrel: (amount = 0.12): Fx => barrelDistortion({amount: unit01(amount, 0.12)}),

	/** Colour-bar test pattern blended in (0 to 1). */
	tvSignalOff: (amount = 1): Fx => tvSignalOff({amount: unit01(amount, 1)}),

	/** Mosaic blocks in px (1 = off). Blur first on moving footage or it shimmers. */
	pixelate: (blockSize = 16, disabled?: boolean): Fx =>
		pixelate({blockSize: Math.max(1, finite(blockSize, 16)), ...off(disabled)}),

	/** Sine displacement (heat haze, flag, underwater). phase is in RADIANS. Edges smear: overscan or keep it small. */
	wave: (o: {amplitude?: number; wavelength?: number; phase?: number; direction?: 'horizontal' | 'vertical'} = {}): Fx =>
		wave({
			amplitude: nonNegative(o.amplitude, 10),
			wavelength: Math.max(1, finite(o.wavelength, 260)),
			phase: finite(o.phase, 0),
			direction: o.direction ?? 'horizontal',
		}),

	/** Moves the image in px (content moved out is clipped). */
	jitter: (x = 0, y = 0, disabled?: boolean): Fx => xyTranslate({x: finite(x, 0), y: finite(y, 0), ...off(disabled)}),

	// ------------------------------------------------ blur and focus

	/** Gaussian blur in px; 0 or less costs nothing. One axis only: {horizontal: false} or {vertical: false}. */
	blur: (radius: number, o: {horizontal?: boolean; vertical?: boolean} = {}): Fx => {
		const r = nonNegative(radius, 0);
		return blurFx({radius: r, horizontal: o.horizontal ?? true, vertical: o.vertical ?? true, ...off(r <= 0.01)});
	},

	/**
	 * Radial zoom blur in px (streak length grows with the distance from the centre). `center` is top-left UV
	 * like every other effect: the preset flips it, because the raw zoomBlur() measures y from the bottom.
	 */
	zoomBlur: (o: {amount?: number; center?: Uv; samples?: number} = {}): Fx => {
		const amount = nonNegative(o.amount, 40);
		const [cx, cy] = uv01(o.center);
		return zoomBlur({
			amount,
			center: [cx, 1 - cy],
			samples: Math.round(clampTo(o.samples, 1, 64, 24)),
			...off(amount <= 0.01),
		});
	},

	/** Tilt shift: sharp horizontal band, blurred above and below. */
	tiltShift: (o: {center?: Uv; width?: number; height?: number; start?: number; blur?: number; rotation?: number} = {}): Fx =>
		radialProgressiveBlur({
			center: [finite(o.center?.[0], 0.5), finite(o.center?.[1], 0.55)],
			width: nonNegative(o.width, 2.4),
			height: nonNegative(o.height, 0.55),
			rotation: finite(o.rotation, 0),
			start: unit01(o.start, 0.35),
			startBlur: 0,
			endBlur: nonNegative(o.blur, 22),
		}),

	/** Spotlight focus: sharp inside an ellipse around `center`, soft outside. */
	focus: (o: {center?: Uv; size?: number; start?: number; blur?: number} = {}): Fx =>
		radialProgressiveBlur({
			center: [finite(o.center?.[0], 0.5), finite(o.center?.[1], 0.5)],
			width: nonNegative(o.size, 0.9),
			height: nonNegative(o.size, 0.9),
			start: unit01(o.start, 0.45),
			startBlur: 0,
			endBlur: nonNegative(o.blur, 16),
		}),

	// ------------------------------------------------ print and colour maps

	/** Halftone dots. Output is ONLY the dots (transparent between): put a paper-coloured layer behind. */
	halftone: (o: {size?: number; spacing?: number; angle?: number; shape?: ShapeKind; ink?: string; source?: boolean; invert?: boolean} = {}): Fx => {
		const size = Math.max(1, finite(o.size, 10));
		const base = {
			shape: o.shape ?? 'circle',
			dotSize: size,
			dotSpacing: Math.max(1, finite(o.spacing, size)),
			rotation: finite(o.angle, 45),
			invert: o.invert ?? false,
		} as const;
		// dotColor may only be passed in solid mode
		return o.source ? halftone({...base, colorMode: 'source'}) : halftone({...base, colorMode: 'solid', dotColor: o.ink ?? '#161616'});
	},

	/** Smooth two-colour gradient map (thermalVision with a 2-colour palette): shadows to `dark`, lights to `light`. */
	duotone: (o: {dark: string; light: string; amount?: number}): Fx =>
		thermalVision({palette: [o.dark, o.light], amount: unit01(o.amount, 1)}),

	/** Three-colour gradient map. */
	tritone: (o: {dark: string; mid: string; light: string; amount?: number}): Fx =>
		thermalVision({palette: [o.dark, o.mid, o.light], amount: unit01(o.amount, 1)}),

	/** Hard two-colour threshold (Remotion's duotone): 1-bit stencil, risograph single pass. */
	stencil: (o: {dark: string; light: string; threshold?: number}): Fx =>
		duotoneFx({darkColor: o.dark, lightColor: o.light, threshold: unit01(o.threshold, 0.5)}),

	/** Colour levels per channel (2 to 64). Kit effect. */
	posterize: (levelsPerChannel = 5, amount = 1): Fx => posterize({levels: levelsPerChannel, amount}),

	// ------------------------------------------------ keying and compositing

	/**
	 * Chroma key. Pick the key colour from the footage's own background (a real green screen is not #00ff00).
	 * similarity 0.2 to 0.45, smoothness 0.05 to 0.1, spill 0.5 to 0.9.
	 */
	colorKey: (o: {color?: string; similarity?: number; smoothness?: number; spill?: number} = {}): Fx =>
		colorKey({
			keyColor: o.color ?? '#00b140',
			similarity: unit01(o.similarity, 0.3),
			smoothness: unit01(o.smoothness, 0.08),
			spillSuppression: unit01(o.spill, 0.6),
		}),

	/** Outline around the alpha shape (sticker edge). Leave a transparent margin: it is clipped at the canvas edge. */
	outline: (o: {width?: number; color?: string; opacity?: number} = {}): Fx =>
		outline({width: nonNegative(o.width, 10), color: o.color ?? '#ffffff', opacity: unit01(o.opacity, 1)}),

	/** Shadow from the alpha shape, drawn behind. */
	dropShadow: (o: {blur?: number; x?: number; y?: number; opacity?: number; color?: string} = {}): Fx =>
		dropShadow({
			radius: nonNegative(o.blur, 18),
			offsetX: finite(o.x, 0),
			offsetY: finite(o.y, 12),
			opacity: unit01(o.opacity, 0.35),
			color: o.color ?? '#000000',
		}),

	// ------------------------------------------------ reveals and destruction

	/** Paper rip: 0 intact, 1 reaches the far edge, above 1 the halves keep separating. rotation 0 to 90. */
	tear: (o: {progress: number; angle?: number; rotation?: number; jaggedness?: number}): Fx =>
		tear({
			progress: nonNegative(o.progress, 0),
			angle: finite(o.angle, 0),
			rotation: clampTo(o.rotation, 0, 90, 18),
			jaggedness: nonNegative(o.jaggedness, 22),
		}),

	/** Soft-edged wipe reveal: progress 0 hidden, 1 revealed, from `direction`. */
	evolve: (o: {progress: number; direction?: 'left' | 'right' | 'top' | 'bottom'; feather?: number}): Fx =>
		evolve({progress: unit01(o.progress, 1), direction: o.direction ?? 'left', feather: unit01(o.feather, 0.15)}),

	/** Blocks disappear in random order: progress 0 fully visible, 1 fully GONE (the opposite of evolve). */
	pixelDissolve: (o: {progress: number; columns?: number; rows?: number; seed?: number; feather?: number}): Fx =>
		pixelDissolve({
			progress: unit01(o.progress, 0),
			columns: Math.round(Math.max(1, finite(o.columns, 16))),
			rows: Math.round(Math.max(1, finite(o.rows, 9))),
			seed: finite(o.seed, 0),
			feather: unit01(o.feather, 0.2),
		}),

	// ------------------------------------------------ glitch

	/** Random horizontal bands pushed sideways, with optional RGB split inside them. Kit effect. */
	slices: (o: {amount?: number; bands?: number; density?: number; seed?: number; split?: number; disabled?: boolean} = {}): Fx =>
		sliceShift({
			amount: nonNegative(o.amount, 60),
			bands: o.bands ?? 24,
			density: unit01(o.density, 0.35),
			seed: finite(o.seed, 0),
			split: nonNegative(o.split, 0),
			...off(o.disabled),
		}),
};
