// Keying and blending: take a subject off a green screen, or lay an element shot on black (or white) over a scene.
import {Video} from '@remotion/media';
import React from 'react';
import {AbsoluteFill, Img} from 'remotion';
import {useStage} from '../core';
import {fx, type Fx} from './effects';

export type KeyOptions = {
	/** The screen colour, sampled from the footage itself (default '#00b140', a typical chroma green). */
	color?: string;
	similarity?: number; // 0.2 to 0.45 (0.3): how close to the key a pixel must be to vanish
	smoothness?: number; // 0.05 to 0.1 (0.08): edge softness
	spill?: number; // 0.5 to 0.9 (0.6): removes the green cast on edges
	/** A sticker edge around the subject (px at 1080). */
	outline?: boolean | {width?: number; color?: string};
	/** A soft shadow under the subject. */
	shadow?: boolean | {blur?: number; x?: number; y?: number; opacity?: number; color?: string};
};

/** The keying chain in the order that works: key, then outline, then shadow (both read the new alpha). */
export const keyEffects = (o: KeyOptions = {}, unit = 1): Fx[] => {
	const list: Fx[] = [fx.colorKey({color: o.color, similarity: o.similarity, smoothness: o.smoothness, spill: o.spill})];
	if (o.outline) {
		const ol = o.outline === true ? {} : o.outline;
		list.push(fx.outline({width: (ol.width ?? 10) * unit, color: ol.color ?? '#ffffff'}));
	}
	if (o.shadow) {
		const sh = o.shadow === true ? {} : o.shadow;
		list.push(fx.dropShadow({blur: (sh.blur ?? 22) * unit, x: (sh.x ?? 0) * unit, y: (sh.y ?? 14) * unit, opacity: sh.opacity ?? 0.35, color: sh.color}));
	}
	return list;
};

export type ChromaKeyProps = KeyOptions & {
	src: string;
	/** 'video' or 'image' (default: from the file extension). */
	kind?: 'video' | 'image';
	/** Size of the keyed layer in px (default: the frame); it is centred in the frame. */
	width?: number;
	height?: number;
	fit?: 'cover' | 'contain';
	/**
	 * A garbage matte: cut away the edges of the shot (fractions of the frame), for rigs, light stands, the
	 * floor shadow or anything the key cannot remove. Needed before an outline, which draws around any residue.
	 */
	matte?: {top?: number; right?: number; bottom?: number; left?: number};
	/** On the full-frame wrapper: move it with translate/scale, clip it with clipPath. */
	style?: React.CSSProperties;
	// video only
	trimBefore?: number;
	playbackRate?: number;
	volume?: number;
	muted?: boolean;
	loop?: boolean;
};

const looksLikeVideo = (src: string) => /\.(mp4|webm|mov|m4v|mkv)(\?|#|$)/i.test(src);

/**
 * A green-screen (or blue-screen) clip or photo with its background keyed out. Place a scene behind it. The key,
 * outline and shadow run on the GPU in the media element's own canvas.
 */
export const ChromaKey: React.FC<ChromaKeyProps> = ({src, kind, width, height, fit = 'contain', matte, style, trimBefore, playbackRate, volume, muted, loop, ...key}) => {
	const {width: W, height: H, unit} = useStage();
	const w = Math.round(width ?? W);
	const h = Math.round(height ?? H);
	const effects = keyEffects(key, unit);
	const video = kind ? kind === 'video' : looksLikeVideo(src);
	const pc = (v: number | undefined) => `${Math.min(100, Math.max(0, (v ?? 0) * 100))}%`;
	const clip = matte ? `inset(${pc(matte.top)} ${pc(matte.right)} ${pc(matte.bottom)} ${pc(matte.left)})` : undefined;
	// a positioned wrapper: a plain canvas in flow would paint UNDER absolutely positioned siblings
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', clipPath: clip, ...style}}>
			{video ? (
				<Video src={src} effects={effects} objectFit={fit} style={{width: w, height: h}} trimBefore={trimBefore} playbackRate={playbackRate} volume={volume} muted={muted} loop={loop} />
			) : (
				<Img src={src} width={w} height={h} effects={effects} style={{objectFit: fit}} />
			)}
		</AbsoluteFill>
	);
};

export type BlendMode = 'normal' | 'screen' | 'plus-lighter' | 'lighten' | 'multiply' | 'darken' | 'overlay' | 'soft-light' | 'color-dodge' | 'color-burn' | 'difference';

/**
 * Any children blended onto what is behind them (mix-blend-mode). For elements shot on black (flares, sparks,
 * smoke, light leaks) use 'screen': black disappears and light adds. For elements on white (ink, paper, line art)
 * use 'multiply'. Keying black or white instead leaves dirty fringes and kills the glow.
 */
export const Blend: React.FC<{mode?: BlendMode; opacity?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
	mode = 'screen',
	opacity = 1,
	children,
	style,
}) => <AbsoluteFill style={{mixBlendMode: mode, opacity, pointerEvents: 'none', ...style}}>{children}</AbsoluteFill>;

export type BlendVideoProps = {
	src: string;
	mode?: BlendMode;
	opacity?: number;
	/**
	 * Cleans the base before blending: for screen it crushes the grey noise floor of "black" footage to true
	 * black (levels black point), for multiply it pushes off-white paper to white. 0 to 0.2 (0.06).
	 */
	crush?: number;
	/** Extra effects after the clean-up (a grade, a hue shift). */
	effects?: Fx[];
	fit?: 'cover' | 'contain';
	style?: React.CSSProperties;
	trimBefore?: number;
	playbackRate?: number;
	loop?: boolean;
	volume?: number;
};

/** A clip shot on black (or white) laid over the scene with a blend mode, its black (or white) cleaned first. */
export const BlendVideo: React.FC<BlendVideoProps> = ({src, mode = 'screen', opacity = 1, crush = 0.06, effects = [], fit = 'cover', style, trimBefore, playbackRate, loop, volume = 0}) => {
	const {width, height} = useStage();
	const c = Math.min(0.4, Math.max(0, crush));
	const lightens = mode === 'screen' || mode === 'plus-lighter' || mode === 'lighten' || mode === 'color-dodge';
	const clean = c > 0 ? [lightens ? fx.levels({black: c}) : fx.levels({white: 1 - c})] : [];
	return (
		<AbsoluteFill style={{mixBlendMode: mode, opacity, pointerEvents: 'none', ...style}}>
			<Video src={src} effects={[...clean, ...effects]} objectFit={fit} style={{width, height}} trimBefore={trimBefore} playbackRate={playbackRate} loop={loop} volume={volume} />
		</AbsoluteFill>
	);
};
