// The kit's fonts: Google Fonts through @remotion/google-fonts, with the weights each family really has, so a
// request for a missing weight loads the nearest one instead of failing. Every stack ends in a Bangla font for
// Bengali letters (Lambda and many machines have none) and a system fallback.
import {loadFont as anekBangla} from '@remotion/google-fonts/AnekBangla';
import {loadFont as anton} from '@remotion/google-fonts/Anton';
import {loadFont as archivo} from '@remotion/google-fonts/Archivo';
import {loadFont as archivoBlack} from '@remotion/google-fonts/ArchivoBlack';
import {loadFont as atma} from '@remotion/google-fonts/Atma';
import {loadFont as balooDa2} from '@remotion/google-fonts/BalooDa2';
import {loadFont as bangers} from '@remotion/google-fonts/Bangers';
import {loadFont as bebasNeue} from '@remotion/google-fonts/BebasNeue';
import {loadFont as caveat} from '@remotion/google-fonts/Caveat';
import {loadFont as cinzel} from '@remotion/google-fonts/Cinzel';
import {loadFont as cormorantGaramond} from '@remotion/google-fonts/CormorantGaramond';
import {loadFont as dmSerifDisplay} from '@remotion/google-fonts/DMSerifDisplay';
import {loadFont as figtree} from '@remotion/google-fonts/Figtree';
import {loadFont as fraunces} from '@remotion/google-fonts/Fraunces';
import {loadFont as galada} from '@remotion/google-fonts/Galada';
import {loadFont as hindSiliguri} from '@remotion/google-fonts/HindSiliguri';
import {loadFont as ibmPlexMono} from '@remotion/google-fonts/IBMPlexMono';
import {loadFont as ibmPlexSans} from '@remotion/google-fonts/IBMPlexSans';
import {loadFont as inconsolata} from '@remotion/google-fonts/Inconsolata';
import {loadFont as instrumentSerif} from '@remotion/google-fonts/InstrumentSerif';
import {loadFont as inter} from '@remotion/google-fonts/Inter';
import {loadFont as jetBrainsMono} from '@remotion/google-fonts/JetBrainsMono';
import {loadFont as libreBaskerville} from '@remotion/google-fonts/LibreBaskerville';
import {loadFont as manrope} from '@remotion/google-fonts/Manrope';
import {loadFont as merriweather} from '@remotion/google-fonts/Merriweather';
import {loadFont as montserrat} from '@remotion/google-fonts/Montserrat';
import {loadFont as notoSansBengali} from '@remotion/google-fonts/NotoSansBengali';
import {loadFont as notoSerifBengali} from '@remotion/google-fonts/NotoSerifBengali';
import {loadFont as nunito} from '@remotion/google-fonts/Nunito';
import {loadFont as oswald} from '@remotion/google-fonts/Oswald';
import {loadFont as outfit} from '@remotion/google-fonts/Outfit';
import {loadFont as patrickHand} from '@remotion/google-fonts/PatrickHand';
import {loadFont as permanentMarker} from '@remotion/google-fonts/PermanentMarker';
import {loadFont as playfairDisplay} from '@remotion/google-fonts/PlayfairDisplay';
import {loadFont as poppins} from '@remotion/google-fonts/Poppins';
import {loadFont as pressStart2P} from '@remotion/google-fonts/PressStart2P';
import {loadFont as rubikMonoOne} from '@remotion/google-fonts/RubikMonoOne';
import {loadFont as sora} from '@remotion/google-fonts/Sora';
import {loadFont as sourceSerif4} from '@remotion/google-fonts/SourceSerif4';
import {loadFont as spaceGrotesk} from '@remotion/google-fonts/SpaceGrotesk';
import {loadFont as specialElite} from '@remotion/google-fonts/SpecialElite';
import {loadFont as syne} from '@remotion/google-fonts/Syne';
import {loadFont as tiroBangla} from '@remotion/google-fonts/TiroBangla';
import {loadFont as unbounded} from '@remotion/google-fonts/Unbounded';
import {loadFont as vt323} from '@remotion/google-fonts/VT323';

type Loader = (
	style?: 'normal' | 'italic',
	options?: {weights?: string[]; subsets?: string[]; ignoreTooManyRequestsWarning?: boolean},
) => {fontFamily: string; waitUntilDone?: () => Promise<unknown>};

export type FontKind = 'sans' | 'serif' | 'mono' | 'display' | 'hand' | 'bangla';

export type FontSpec = {
	load: Loader;
	kind: FontKind;
	weights: readonly number[];
	subsets: readonly string[];
	italic: boolean;
	bangla: boolean;
};

const LATIN = ['latin', 'latin-ext'] as const;
const BENGALI = ['bengali', 'latin'] as const;
const ALL = [100, 200, 300, 400, 500, 600, 700, 800, 900] as const;

const font = (
	load: unknown,
	kind: FontKind,
	weights: readonly number[],
	opts: {italic?: boolean; subsets?: readonly string[]} = {},
): FontSpec => {
	const bangla = kind === 'bangla';
	return {
		load: load as Loader,
		kind,
		weights,
		subsets: opts.subsets ?? (bangla ? BENGALI : LATIN),
		italic: opts.italic ?? false,
		bangla,
	};
};

export const FONTS = {
	// sans, for text and interfaces
	Inter: font(inter, 'sans', ALL, {italic: true}),
	Manrope: font(manrope, 'sans', [200, 300, 400, 500, 600, 700, 800]),
	Figtree: font(figtree, 'sans', [300, 400, 500, 600, 700, 800, 900], {italic: true}),
	IBMPlexSans: font(ibmPlexSans, 'sans', [100, 200, 300, 400, 500, 600, 700], {italic: true}),
	SpaceGrotesk: font(spaceGrotesk, 'sans', [300, 400, 500, 600, 700]),
	Poppins: font(poppins, 'sans', ALL, {italic: true}),
	Montserrat: font(montserrat, 'sans', ALL, {italic: true}),
	Nunito: font(nunito, 'sans', [200, 300, 400, 500, 600, 700, 800, 900], {italic: true}),
	Outfit: font(outfit, 'sans', ALL),
	Sora: font(sora, 'sans', [100, 200, 300, 400, 500, 600, 700, 800]),
	Archivo: font(archivo, 'sans', ALL, {italic: true}),
	// display, for big words
	Anton: font(anton, 'display', [400]),
	BebasNeue: font(bebasNeue, 'display', [400]),
	ArchivoBlack: font(archivoBlack, 'display', [400]),
	Oswald: font(oswald, 'display', [200, 300, 400, 500, 600, 700]),
	Syne: font(syne, 'display', [400, 500, 600, 700, 800]),
	Unbounded: font(unbounded, 'display', [200, 300, 400, 500, 600, 700, 800, 900]),
	RubikMonoOne: font(rubikMonoOne, 'display', [400]),
	Cinzel: font(cinzel, 'display', [400, 500, 600, 700, 800, 900]),
	Bangers: font(bangers, 'display', [400]),
	PressStart2P: font(pressStart2P, 'display', [400]),
	// serif
	InstrumentSerif: font(instrumentSerif, 'serif', [400], {italic: true}),
	DMSerifDisplay: font(dmSerifDisplay, 'serif', [400], {italic: true}),
	PlayfairDisplay: font(playfairDisplay, 'serif', [400, 500, 600, 700, 800, 900], {italic: true}),
	CormorantGaramond: font(cormorantGaramond, 'serif', [300, 400, 500, 600, 700], {italic: true}),
	Fraunces: font(fraunces, 'serif', ALL, {italic: true}),
	Merriweather: font(merriweather, 'serif', [300, 400, 500, 600, 700, 800, 900], {italic: true}),
	SourceSerif4: font(sourceSerif4, 'serif', [200, 300, 400, 500, 600, 700, 800, 900], {italic: true}),
	LibreBaskerville: font(libreBaskerville, 'serif', [400, 500, 600, 700], {italic: true}),
	// mono
	JetBrainsMono: font(jetBrainsMono, 'mono', [100, 200, 300, 400, 500, 600, 700, 800], {italic: true}),
	IBMPlexMono: font(ibmPlexMono, 'mono', [100, 200, 300, 400, 500, 600, 700], {italic: true}),
	Inconsolata: font(inconsolata, 'mono', [200, 300, 400, 500, 600, 700, 800, 900]),
	VT323: font(vt323, 'mono', [400]),
	SpecialElite: font(specialElite, 'mono', [400]),
	// hand
	Caveat: font(caveat, 'hand', [400, 500, 600, 700]),
	PatrickHand: font(patrickHand, 'hand', [400]),
	PermanentMarker: font(permanentMarker, 'hand', [400], {subsets: ['latin']}),
	// Bangla (each also has Latin letters)
	AnekBangla: font(anekBangla, 'bangla', [100, 200, 300, 400, 500, 600, 700, 800]),
	// Hind Siliguri draws the Bengali digit one (১) as a small hook that reads as ৲: never use it for numbers
	HindSiliguri: font(hindSiliguri, 'bangla', [300, 400, 500, 600, 700]),
	NotoSansBengali: font(notoSansBengali, 'bangla', ALL),
	NotoSerifBengali: font(notoSerifBengali, 'bangla', ALL),
	TiroBangla: font(tiroBangla, 'bangla', [400], {italic: true}),
	BalooDa2: font(balooDa2, 'bangla', [400, 500, 600, 700, 800]),
	Galada: font(galada, 'bangla', [400]),
	Atma: font(atma, 'bangla', [300, 400, 500, 600, 700]),
} satisfies Record<string, FontSpec>;

export type FontKey = keyof typeof FONTS;

const FALLBACK: Record<FontKind, string> = {
	sans: 'system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif',
	display: '"Helvetica Neue", Arial, sans-serif',
	serif: 'Georgia, "Times New Roman", serif',
	mono: 'ui-monospace, Menlo, Consolas, monospace',
	hand: '"Comic Sans MS", cursive',
	bangla: 'sans-serif',
};

const loaded = new Map<string, string>();
const pending = new Map<string, Promise<unknown>>();

const nearest = (weights: readonly number[], w: number): number =>
	weights.reduce((a, b) => (Math.abs(b - w) < Math.abs(a - w) ? b : a));

/**
 * Loads weights of a kit font and returns its CSS family name (which can differ from the key: VT323 is
 * registered as "VTThreeTwoThree"). The first call starts the download and holds the render until it arrives;
 * later calls are free, so calling it during render is fine.
 */
export const loadKitFont = (
	key: FontKey,
	weights: readonly number[] = [400, 700],
	style: 'normal' | 'italic' = 'normal',
): string => {
	const spec: FontSpec = FONTS[key];
	const use = [...new Set(weights.map((w) => nearest(spec.weights, w)))].sort((a, b) => a - b);
	const st = style === 'italic' && spec.italic ? 'italic' : 'normal';
	const id = `${key}|${st}|${use.join(',')}`;
	const hit = loaded.get(id);
	if (hit) {
		return hit;
	}
	const res = spec.load(st, {
		weights: use.map(String),
		subsets: [...spec.subsets],
		ignoreTooManyRequestsWarning: true,
	});
	loaded.set(id, res.fontFamily);
	pending.set(id, res.waitUntilDone ? res.waitUntilDone() : Promise.resolve());
	return res.fontFamily;
};

/** Resolves when every kit font requested so far has loaded: await it before measuring text. */
export const waitForKitFonts = (): Promise<void> => Promise.all([...pending.values()]).then(() => undefined);

/** Loads a kit font (if needed) and resolves when it has loaded. */
export const waitForKitFont = (
	key: FontKey,
	weights: readonly number[] = [400, 700],
	style: 'normal' | 'italic' = 'normal',
): Promise<void> => {
	loadKitFont(key, weights, style);
	return waitForKitFonts();
};

/**
 * A CSS font-family value for a kit font: the font, then a Bangla font for Bengali letters (unless the font is
 * one, or `bangla` is null), then the system fallback.
 */
export const fontStack = (
	key: FontKey,
	weights: readonly number[] = [400, 700],
	bangla: FontKey | null = 'AnekBangla',
	style: 'normal' | 'italic' = 'normal',
): string => {
	const spec: FontSpec = FONTS[key];
	const parts = [`"${loadKitFont(key, weights, style)}"`];
	if (bangla && !spec.bangla) {
		parts.push(`"${loadKitFont(bangla, weights)}"`);
	}
	parts.push(FALLBACK[spec.kind]);
	return parts.join(', ');
};
