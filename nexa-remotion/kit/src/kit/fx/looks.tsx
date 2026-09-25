// Looks: a whole treatment applied to children (a scene, a card, footage). Two engines:
//  - canvas: the children are painted into <HtmlInCanvas> and a WebGL effect stack runs on the pixels (true
//    chromatic aberration, halftone, barrel curve, bloom). Needs --gl=angle in renders; preview needs Chrome with
//    chrome://flags/#canvas-draw-element.
//  - css: filters, blend modes and inline SVG filters. Works everywhere, including inside a scene that sits next
//    to a shader transition (where HTML-in-canvas cannot nest).
// engine "auto" (the default) takes canvas when it can run here, css otherwise.
import React from 'react';
import {AbsoluteFill, Freeze, HtmlInCanvas, Solid, isHtmlInCanvasSupported, useCurrentFrame} from 'remotion';
import {loadKitFont, useStage} from '../core';
import {onTwos, wiggle} from '../motion';
import {Bloom, DustOverlay, Grain, GrilleOverlay, PosterizeCss, RgbSplit, ScanlineOverlay, SlicesCss, VignetteOverlay, makeSlices} from './css';
import {fx, type Fx} from './effects';
import {glitchAt, type GlitchSchedule} from './glitch';
import {FxNestContext, mixHex, r01, stepSeed, useFxNest, useSafeId} from './util';

export type LookEngine = 'auto' | 'canvas' | 'css';

export type LookBaseProps = {
	/** 'auto' (default): canvas where HTML-in-canvas can run, css elsewhere. */
	engine?: LookEngine;
	/** Scales the whole treatment: 0 is off, 1 is the designed default, above 1 is heavier. */
	strength?: number;
	seed?: string;
	/** Size of the painted area in px (default: the frame). HtmlInCanvas needs whole numbers. */
	width?: number;
	height?: number;
	/** Layers drawn on top of the look and left untouched: captions, logos, type that must stay crisp. */
	overlay?: React.ReactNode;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

let supportCache: boolean | null = null;
const canvasSupported = (): boolean => {
	if (supportCache === null) {
		supportCache = typeof document !== 'undefined' && isHtmlInCanvasSupported();
	}
	return supportCache;
};

/** Resolves an engine request against where the component sits (see FxNestContext). */
export const useLookEngine = (requested: LookEngine | undefined, label: string): 'canvas' | 'css' => {
	const nest = useFxNest();
	const want = requested ?? 'auto';
	if (want === 'css') {
		return 'css';
	}
	if (want === 'canvas') {
		if (nest.canvas) {
			throw new Error(
				`${label}: engine="canvas" cannot run ${nest.canvas}, because HTML-in-canvas cannot be nested (the render would wait until it times out). Use engine="css" or "auto".`,
			);
		}
		return 'canvas';
	}
	return nest.canvas || !canvasSupported() ? 'css' : 'canvas';
};

type ShellProps = {
	engine: 'canvas' | 'css';
	label: string;
	width?: number;
	height?: number;
	/** Colour behind the painted layer (shows where effects leave transparency: barrel corners, halftone gaps). */
	ground?: string;
	effects: Fx[];
	cssFilter?: string;
	cssWrap?: (node: React.ReactNode) => React.ReactNode;
	cssOverlays?: React.ReactNode;
	contentStyle?: React.CSSProperties;
	under?: React.ReactNode;
	over?: React.ReactNode;
	/** The caller's untouched layers, drawn last. */
	overlay?: React.ReactNode;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** The frame every look shares: layers under, the painted content, overlays over. */
export const LookShell: React.FC<ShellProps> = (p) => {
	const {width: W, height: H} = useStage();
	const w = Math.max(1, Math.round(p.width ?? W));
	const h = Math.max(1, Math.round(p.height ?? H));
	const content = <AbsoluteFill style={p.contentStyle}>{p.children}</AbsoluteFill>;
	const root: React.CSSProperties = {background: p.ground, overflow: 'hidden', isolation: 'isolate', width: w, height: h, ...p.style};
	if (p.engine === 'canvas') {
		return (
			<AbsoluteFill style={root}>
				{p.under}
				<HtmlInCanvas width={w} height={h} effects={p.effects} name={p.label}>
					<FxNestContext.Provider value={{canvas: `inside a canvas ${p.label}`}}>
						<AbsoluteFill style={{width: w, height: h}}>{content}</AbsoluteFill>
					</FxNestContext.Provider>
				</HtmlInCanvas>
				{p.over}
				{p.overlay}
			</AbsoluteFill>
		);
	}
	const filtered = <AbsoluteFill style={{filter: p.cssFilter}}>{content}</AbsoluteFill>;
	return (
		<AbsoluteFill style={root}>
			{p.under}
			{p.cssWrap ? p.cssWrap(filtered) : filtered}
			{p.cssOverlays}
			{p.over}
			{p.overlay}
		</AbsoluteFill>
	);
};

export type LookFxOptions = {frame: number; fps: number; unit?: number; strength?: number; seed?: string};

// ---------------------------------------------------------------- film

export type FilmLookProps = LookBaseProps & {
	grain?: number; // noise amount (0.07)
	grainHz?: number; // re-seeds per second (12)
	vignette?: number; // corner darkening (0.3)
	weave?: number; // gate weave in px at 1080 (1.2)
	flicker?: number; // exposure flicker, fraction (0.025)
	warmth?: number; // -1 cool to 1 warm (0.2)
	fade?: number; // lifted blacks (0.14)
	dust?: number; // specks and hairs, 0 to 1 (0.6)
};

const filmFlicker = (frame: number, fps: number, seed: string, hz: number) =>
	r01(`${seed}-f-${stepSeed(frame, fps, hz)}`) * 2 - 1;

/** The film treatment as an effect stack, for footage (Img, Video) or any effects host. */
export const filmEffects = (o: LookFxOptions & Pick<FilmLookProps, 'grain' | 'grainHz' | 'vignette' | 'flicker' | 'warmth' | 'fade'>): Fx[] => {
	const s = Math.max(0, o.strength ?? 1);
	const seed = o.seed ?? 'film';
	const hz = o.grainHz ?? 12;
	const flick = filmFlicker(o.frame, o.fps, seed, hz) * (o.flicker ?? 0.025) * s;
	return [
		fx.colorCorrection({
			exposure: flick * 1.4,
			contrast: 1 - 0.05 * s,
			blacks: (o.fade ?? 0.14) * s,
			highlights: -0.1 * s,
			temperature: (o.warmth ?? 0.2) * s,
			saturation: 1 - 0.12 * s,
		}),
		fx.grain({frame: o.frame, fps: o.fps, hz, amount: (o.grain ?? 0.07) * s}),
		fx.vignette({amount: (o.vignette ?? 0.3) * s, radius: 0.76, feather: 0.62}),
	];
};

/** Film: 12 Hz grain, weak vignette, gate weave, exposure flicker, lifted warm blacks, a little dust. */
export const FilmLook: React.FC<FilmLookProps> = ({engine, strength = 1, seed = 'film', grain = 0.07, grainHz = 12, vignette = 0.3, weave = 1.2, flicker = 0.025, warmth = 0.2, fade = 0.14, dust = 0.6, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<FilmLook>');
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = Math.max(0, strength);
	const step = stepSeed(frame, fps, grainHz);
	const wx = (wiggle(frame, fps, 0.9, 3, seed) * 0.5 + (r01(`${seed}-wx-${step}`) - 0.5) * 0.6) * weave * unit * s;
	const wy = (wiggle(frame, fps, 0.7, 4, seed) * 0.8 + (r01(`${seed}-wy-${step}`) - 0.5) * 0.9) * weave * unit * s;
	const flick = filmFlicker(frame, fps, seed, grainHz) * flicker * s;
	return (
		<LookShell
			engine={e}
			label="FilmLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground="#0d0b09"
			contentStyle={{translate: `${wx}px ${wy}px`, scale: String(1 + (4 * weave * s) / 1080)}}
			effects={filmEffects({frame, fps, unit, strength: s, seed, grain, grainHz, vignette, flicker, warmth, fade})}
			cssFilter={`sepia(${Math.max(0, 0.9 * warmth * s)}) saturate(${1 - 0.12 * s}) contrast(${1 - 0.06 * s}) brightness(${1 + flick})`}
			cssOverlays={
				<>
					<AbsoluteFill style={{background: '#2b1e10', mixBlendMode: 'screen', opacity: Math.min(0.9, fade * s * 1.3), pointerEvents: 'none'}} />
					<Grain amount={Math.min(1, grain * s * 3.2)} hz={grainHz} />
					<VignetteOverlay strength={vignette * s} start={0.5} />
				</>
			}
			over={dust > 0 && s > 0 ? <DustOverlay amount={dust * s} seed={seed} hz={grainHz} /> : null}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- vhs

export type VhsLookProps = LookBaseProps & {
	split?: number; // RGB split in px at 1080 (3)
	smear?: number; // horizontal smear in px (1.6)
	noise?: number; // tape noise (0.07)
	tracking?: boolean; // the rolling noise band (true)
	osd?: string | false; // top-left on-screen text, for example 'PLAY ▶'
	date?: string | false; // bottom-right text, for example 'JAN 12 1997'
};

export const vhsEffects = (o: LookFxOptions & Pick<VhsLookProps, 'split' | 'smear' | 'noise'>): Fx[] => {
	const s = Math.max(0, o.strength ?? 1);
	const u = o.unit ?? 1;
	const seed = o.seed ?? 'vhs';
	const wob = r01(`${seed}-wob-${o.frame}`) - 0.5;
	return [
		fx.colorCorrection({contrast: 1 - 0.1 * s, blacks: 0.16 * s, saturation: 1 + 0.18 * s, temperature: 0.05 * s, tint: 0.04 * s}),
		fx.blur((o.smear ?? 1.6) * u * s, {vertical: false}),
		fx.chromaticAberration({amount: ((o.split ?? 3) + wob) * u * s}),
		fx.slices({amount: 7 * u * s, bands: 140, density: 0.05 * Math.min(1, s), seed: o.frame}),
		fx.scanlines({amount: 0.1 * Math.min(1, s), spacing: 3 * u, thickness: u}),
		fx.grain({frame: o.frame, fps: o.fps, hz: o.fps, amount: (o.noise ?? 0.07) * s}),
		fx.vignette({amount: 0.3 * Math.min(1, s), radius: 0.75, feather: 0.5}),
	];
};

const VhsBands: React.FC<{strength: number; tracking: boolean; seed: string}> = ({strength, tracking, seed}) => {
	const frame = useCurrentFrame();
	const {height, unit} = useStage();
	const id = useSafeId('vhs');
	const bandH = 0.07 * height;
	const y = ((frame * 3.1 * unit + r01(`${seed}-b0`) * height) % (height * 1.35)) - 0.2 * height;
	const noise = (key: string, freq: string, s: number) => (
		<filter id={`${id}-${key}`} x="0" y="0" width="100%" height="100%">
			<feTurbulence type="fractalNoise" baseFrequency={freq} numOctaves={1} seed={s} />
			<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 3.2 0 0 0 -1.9" />
		</filter>
	);
	return (
		<>
			{tracking ? (
				<svg style={{position: 'absolute', left: 0, top: y, width: '100%', height: bandH, mixBlendMode: 'screen', opacity: 0.55 * Math.min(1, strength), pointerEvents: 'none'}}>
					{noise('t', `${0.0035 / unit} ${0.55 / unit}`, frame)}
					<rect width="100%" height="100%" filter={`url(#${id}-t)`} />
				</svg>
			) : null}
			<svg style={{position: 'absolute', left: 0, bottom: 0, width: '100%', height: 0.028 * height, opacity: 0.8 * Math.min(1, strength), pointerEvents: 'none'}}>
				{noise('h', `${0.006 / unit} ${0.9 / unit}`, frame + 101)}
				<rect width="100%" height="100%" fill="rgba(0,0,0,0.55)" />
				<rect width="100%" height="100%" filter={`url(#${id}-h)`} />
			</svg>
		</>
	);
};

const VhsText: React.FC<{osd?: string | false; date?: string | false}> = ({osd, date}) => {
	const {safe, unit, width} = useStage();
	const family = loadKitFont('VT323', [400]);
	const text: React.CSSProperties = {
		position: 'absolute',
		fontFamily: `"${family}", ui-monospace, monospace`,
		fontSize: 62 * unit,
		lineHeight: 1,
		color: '#f5f5f0',
		letterSpacing: '0.04em',
		textShadow: `${2 * unit}px 0 rgba(255,40,60,0.55), ${-2 * unit}px 0 rgba(40,120,255,0.55), 0 0 ${6 * unit}px rgba(255,255,255,0.35)`,
		whiteSpace: 'pre',
	};
	return (
		<>
			{osd ? <div style={{...text, left: safe.x, top: safe.y}}>{osd}</div> : null}
			{date ? <div style={{...text, right: width - safe.x - safe.w, top: safe.y + safe.h - 62 * unit}}>{date}</div> : null}
		</>
	);
};

/** VHS tape: smeared, over-saturated colour, RGB split, line wobble, tape noise, rolling tracking band, OSD text. */
export const VhsLook: React.FC<VhsLookProps> = ({engine, strength = 1, seed = 'vhs', split = 3, smear = 1.6, noise = 0.07, tracking = true, osd, date, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<VhsLook>');
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = Math.max(0, strength);
	const wob = (r01(`${seed}-wob-${frame}`) - 0.5) * 1.5 * unit * s;
	return (
		<LookShell
			engine={e}
			label="VhsLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground="#07060a"
			contentStyle={{translate: `${wob}px 0px`}}
			effects={vhsEffects({frame, fps, unit, strength: s, seed, split, smear, noise})}
			cssFilter={`saturate(${1 + 0.2 * s}) contrast(${1 - 0.08 * s}) blur(${0.5 * unit * s}px)`}
			cssWrap={(n) => <RgbSplit dx={split * unit * s}>{n}</RgbSplit>}
			cssOverlays={
				<>
					<AbsoluteFill style={{background: '#1b1230', mixBlendMode: 'screen', opacity: 0.35 * Math.min(1, s), pointerEvents: 'none'}} />
					<ScanlineOverlay opacity={0.14 * Math.min(1, s)} spacing={3} thickness={1} />
					<Grain amount={Math.min(1, noise * s * 3)} hz={fps} size={0.8} />
					<VignetteOverlay strength={0.3 * Math.min(1, s)} />
				</>
			}
			over={
				<>
					<VhsBands strength={s} tracking={tracking} seed={seed} />
					<VhsText osd={osd} date={date} />
				</>
			}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- crt

export type CrtLookProps = LookBaseProps & {
	curve?: number; // barrel curvature 0 to 1 (0.08)
	scanlines?: number; // 0 to 1 (0.3)
	mask?: number; // aperture grille opacity (0.12)
	glow?: number; // phosphor bloom (0.45)
	flicker?: number; // brightness flicker, fraction (0.015)
};

export const crtEffects = (o: LookFxOptions & Pick<CrtLookProps, 'curve' | 'scanlines' | 'glow' | 'flicker'>): Fx[] => {
	const s = Math.max(0, o.strength ?? 1);
	const u = o.unit ?? 1;
	const flick = (r01(`${o.seed ?? 'crt'}-fl-${o.frame}`) * 2 - 1) * (o.flicker ?? 0.015) * s;
	return [
		fx.colorCorrection({exposure: flick * 1.4, contrast: 1 + 0.08 * s, saturation: 1 + 0.1 * s}),
		fx.glow({radius: 12 * u, intensity: (o.glow ?? 0.45) * s, threshold: 0.5}),
		fx.scanlines({amount: (o.scanlines ?? 0.3) * Math.min(1, s), spacing: 4 * u, thickness: 2 * u, offset: o.frame * 0.5 * u}),
		fx.chromaticAberration({amount: 1.2 * u * s}),
		fx.barrel((o.curve ?? 0.08) * Math.min(1, s)),
		fx.vignette({amount: 0.45 * Math.min(1, s), radius: 0.66, feather: 0.45, roundness: 0.55}),
	];
};

/** CRT monitor: curved glass, scanlines, aperture grille, phosphor glow, a faint reflection. */
export const CrtLook: React.FC<CrtLookProps> = ({engine, strength = 1, seed = 'crt', curve = 0.08, scanlines = 0.3, mask = 0.12, glow = 0.45, flicker = 0.015, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<CrtLook>');
	const frame = useCurrentFrame();
	const {fps, unit, width: W, height: H} = useStage();
	const s = Math.max(0, strength);
	const flick = (r01(`${seed}-fl-${frame}`) * 2 - 1) * flicker * s;
	const radius = Math.min(W, H) * 0.045;
	const glass = (
		<AbsoluteFill
			style={{
				pointerEvents: 'none',
				background: 'linear-gradient(125deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.0) 38%, rgba(255,255,255,0) 100%)',
			}}
		/>
	);
	return (
		<LookShell
			engine={e}
			label="CrtLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground="#030304"
			effects={crtEffects({frame, fps, unit, strength: s, seed, curve, scanlines, glow, flicker})}
			cssFilter={`contrast(${1 + 0.08 * s}) saturate(${1 + 0.1 * s}) brightness(${1 + flick})`}
			cssWrap={(n) => (
				<AbsoluteFill style={{borderRadius: radius, overflow: 'hidden'}}>
					<Bloom amount={glow * s} radius={18} threshold={0.55}>
						{n}
					</Bloom>
				</AbsoluteFill>
			)}
			cssOverlays={
				<>
					<ScanlineOverlay opacity={scanlines * Math.min(1, s) * 0.9} spacing={4} thickness={2} roll={0.5} />
					<AbsoluteFill style={{borderRadius: radius, boxShadow: `inset 0 0 ${90 * unit}px rgba(0,0,0,${0.75 * Math.min(1, s)})`, pointerEvents: 'none'}} />
				</>
			}
			over={
				<>
					<GrilleOverlay opacity={mask * Math.min(1, s)} />
					{glass}
				</>
			}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- newsprint

export type NewsprintLookProps = LookBaseProps & {
	ink?: string; // ('#1c1b19')
	paper?: string; // ('#efe7d6')
	dot?: number; // halftone cell in px at 1080 (6)
	angle?: number; // screen angle in degrees (45)
	texture?: number; // paper texture 0 to 1 (0.5)
	/** Brightens the picture before it is screened, 0 to 1 (0.5): dark pictures otherwise print as solid ink. */
	lift?: number;
};

export const newsprintEffects = (o: LookFxOptions & Pick<NewsprintLookProps, 'ink' | 'dot' | 'angle' | 'lift'>): Fx[] => {
	const u = o.unit ?? 1;
	const lift = Math.min(1, Math.max(0, o.lift ?? 0.5));
	return [
		fx.levels({black: 0.03, white: 1 - 0.45 * lift, gamma: 1 + 0.5 * lift}),
		fx.colorCorrection({saturation: 0, contrast: 1.12}),
		fx.halftone({size: (o.dot ?? 6) * u, angle: o.angle ?? 45, ink: o.ink ?? '#1c1b19'}),
	];
};

/**
 * Newsprint halftone: ink dots on textured paper. Canvas uses the real halftone effect; css builds the dots by
 * contrast. Type printed in the dots breaks up below about 60 px: pass headlines as `overlay` so they print solid.
 */
export const NewsprintLook: React.FC<NewsprintLookProps> = ({engine, strength = 1, seed = 'news', ink = '#1c1b19', paper = '#efe7d6', dot = 6, angle = 45, texture = 0.5, lift = 0.5, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<NewsprintLook>');
	const frame = useCurrentFrame();
	const {fps, unit, width: W, height: H} = useStage();
	const s = Math.max(0, strength);
	const w = Math.round(width ?? W);
	const h = Math.round(height ?? H);
	const cell = Math.max(3, dot * unit);
	const side = Math.hypot(w, h);
	const k = Math.min(1, Math.max(0, lift));
	const paperLayer =
		e === 'canvas' ? (
			<Solid width={w} height={h} color={paper} style={{position: 'absolute', inset: 0}} effects={[fx.paper({amount: texture * Math.min(1, s), seed: 11, front: mixHex(paper, '#7a705f', 0.45), back: paper})]} />
		) : (
			<AbsoluteFill style={{background: paper}} />
		);
	return (
		<LookShell
			engine={e}
			label="NewsprintLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground={paper}
			under={paperLayer}
			effects={newsprintEffects({frame, fps, unit, strength: s, seed, ink, dot, angle, lift})}
			cssWrap={(n) => (
				<AbsoluteFill style={{isolation: 'isolate'}}>
					{/* picture times a dot pattern, then a hard contrast: darker areas grow bigger dots */}
					<AbsoluteFill style={{background: '#ffffff', filter: 'contrast(22)'}}>
						<AbsoluteFill style={{filter: `grayscale(1) contrast(${0.6 - 0.18 * k}) brightness(${1.3 + 0.35 * k}) blur(${0.5 * unit}px)`}}>{n}</AbsoluteFill>
						<div
							style={{
								position: 'absolute',
								left: (w - side) / 2,
								top: (h - side) / 2,
								width: side,
								height: side,
								rotate: `${angle}deg`,
								mixBlendMode: 'multiply',
								backgroundImage: `radial-gradient(circle at 50% 50%, rgb(143,143,143) 0px, #ffffff ${cell * 0.72}px)`,
								backgroundSize: `${cell}px ${cell}px`,
							}}
						/>
					</AbsoluteFill>
					<AbsoluteFill style={{background: ink, mixBlendMode: 'lighten'}} />
					<AbsoluteFill style={{background: paper, mixBlendMode: 'multiply'}} />
				</AbsoluteFill>
			)}
			over={<Grain amount={0.22 * texture * Math.min(1, s)} hz={4} size={1.6} blend="multiply" />}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- noir

export type NoirLookProps = LookBaseProps & {
	contrast?: number; // (1.35)
	grain?: number; // (0.07)
	vignette?: number; // (0.5)
	blinds?: number; // venetian-blind shadows across the frame, 0 to 1 (0)
};

export const noirEffects = (o: LookFxOptions & Pick<NoirLookProps, 'contrast' | 'grain' | 'vignette'>): Fx[] => {
	const s = Math.max(0, o.strength ?? 1);
	return [
		fx.colorCorrection({saturation: 1 - Math.min(1, s), contrast: 1 + ((o.contrast ?? 1.35) - 1) * s, blacks: -0.08 * s, highlights: -0.06 * s, shadows: 0.04 * s}),
		fx.grain({frame: o.frame, fps: o.fps, amount: (o.grain ?? 0.07) * s}),
		fx.vignette({amount: (o.vignette ?? 0.5) * Math.min(1, s), radius: 0.64, feather: 0.6}),
	];
};

/** Film noir: black and white with hard contrast, heavy vignette, grain, optional blind shadows. */
export const NoirLook: React.FC<NoirLookProps> = ({engine, strength = 1, seed = 'noir', contrast = 1.35, grain = 0.07, vignette = 0.5, blinds = 0, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<NoirLook>');
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = Math.max(0, strength);
	const k = Math.min(1, s);
	return (
		<LookShell
			engine={e}
			label="NoirLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground="#050505"
			effects={noirEffects({frame, fps, unit, strength: s, seed, contrast, grain, vignette})}
			cssFilter={`grayscale(${k}) contrast(${1 + (contrast - 1) * s}) brightness(${1 - 0.06 * s})`}
			cssOverlays={
				<>
					<Grain amount={Math.min(1, grain * s * 5)} />
					<VignetteOverlay strength={vignette * k} start={0.42} />
				</>
			}
			over={
				blinds > 0 ? (
					<AbsoluteFill
						style={{
							pointerEvents: 'none',
							mixBlendMode: 'multiply',
							opacity: Math.min(1, blinds * k),
							filter: `blur(${10 * unit}px)`,
							backgroundImage: `repeating-linear-gradient(-24deg, rgba(0,0,0,0.75) 0px, rgba(0,0,0,0.75) ${34 * unit}px, rgba(0,0,0,0) ${34 * unit}px, rgba(0,0,0,0) ${82 * unit}px)`,
							scale: '1.2',
						}}
					/>
				) : null
			}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- dreamy

export type DreamyLookProps = LookBaseProps & {
	bloom?: number; // (0.75)
	haze?: number; // light veil at the edges (0.25)
	soften?: number; // edge softness 0 to 1 (0.5)
	warmth?: number; // (0.12)
};

export const dreamyEffects = (o: LookFxOptions & Pick<DreamyLookProps, 'bloom' | 'haze' | 'soften' | 'warmth'>): Fx[] => {
	const s = Math.max(0, o.strength ?? 1);
	const u = o.unit ?? 1;
	return [
		fx.colorCorrection({contrast: 1 - 0.1 * s, blacks: 0.14 * s, saturation: 1 + 0.06 * s, temperature: (o.warmth ?? 0.12) * s, tint: 0.05 * s}),
		fx.glow({radius: 34 * u, intensity: (o.bloom ?? 0.75) * s, threshold: 0.42, color: '#fff2e2'}),
		fx.focus({size: 1.3, start: 0.5, blur: 9 * u * (o.soften ?? 0.5) * s}),
		fx.vignette({amount: (o.haze ?? 0.25) * Math.min(1, s), radius: 0.7, feather: 0.8, color: '#fff4ee'}),
	];
};

/** Dreamy: soft bloom on the highlights, lifted pastel shadows, soft edges and a light haze. */
export const DreamyLook: React.FC<DreamyLookProps> = ({engine, strength = 1, seed = 'dreamy', bloom = 0.75, haze = 0.25, soften = 0.5, warmth = 0.12, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<DreamyLook>');
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = Math.max(0, strength);
	return (
		<LookShell
			engine={e}
			label="DreamyLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			ground="#f3ece6"
			effects={dreamyEffects({frame, fps, unit, strength: s, seed, bloom, haze, soften, warmth})}
			cssFilter={`contrast(${1 - 0.1 * s}) saturate(${1 + 0.06 * s}) sepia(${Math.max(0, warmth * s)}) brightness(${1 + 0.04 * s})`}
			cssWrap={(n) => (
				<Bloom amount={0.6 * bloom * s} radius={30} threshold={0.42}>
					{n}
				</Bloom>
			)}
			cssOverlays={<VignetteOverlay strength={haze * Math.min(1, s) * 1.4} start={0.45} color="#fff4ee" />}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- glitch

export type GlitchLookProps = LookBaseProps &
	GlitchSchedule & {
		/** Constant RGB split in px between bursts (0: clean between bursts). */
		idle?: number;
	};

export const glitchEffects = (o: LookFxOptions & GlitchSchedule & {idle?: number}): Fx[] => {
	const u = o.unit ?? 1;
	const seed = o.seed ?? 'glitch';
	const hit = glitchAt(o.frame, {...o, seed});
	const i = hit.intensity * Math.max(0, o.strength ?? 1);
	const idle = (o.idle ?? 0) * u;
	if (i <= 0) {
		return idle > 0 ? [fx.chromaticAberration({amount: idle})] : [];
	}
	const list: Fx[] = [
		fx.chromaticAberration({amount: idle + (2 + 24 * i) * u, angle: hit.local % 2 ? 180 : 0}),
		fx.slices({amount: 110 * i * u, bands: 10 + Math.floor(r01(`${seed}-bands-${o.frame}`) * 30), density: 0.18 + 0.45 * i, seed: hit.seed, split: 10 * i * u}),
		fx.jitter((r01(`${seed}-jx-${o.frame}`) - 0.5) * 30 * i * u, (r01(`${seed}-jy-${o.frame}`) - 0.5) * 6 * i * u),
	];
	if (r01(`${seed}-px-${o.frame}`) < 0.25 * i) {
		list.push(fx.pixelate(12 * u));
	}
	if (r01(`${seed}-st-${o.frame}`) < 0.4 * i) {
		list.push(fx.staticNoise({amount: 0.12 * i, seed: o.frame}));
	}
	return list;
};

/**
 * Digital glitch in deterministic bursts: RGB split, displaced slices, jitter, now and then blocks and static.
 * Clean between bursts unless `idle` is set. Pass `bursts` to place hits on beats.
 */
export const GlitchLook: React.FC<GlitchLookProps> = ({engine, strength = 1, seed = 'glitch', bursts, every, length, chance, idle = 0, width, height, overlay, children, style}) => {
	const e = useLookEngine(engine, '<GlitchLook>');
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = Math.max(0, strength);
	const schedule: GlitchSchedule = {bursts, every, length, chance, seed};
	const hit = glitchAt(frame, schedule);
	const i = hit.intensity * s;
	const jitter = i > 0 ? (r01(`${seed}-jx-${frame}`) - 0.5) * 30 * i * unit : 0;
	return (
		<LookShell
			engine={e}
			label="GlitchLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			effects={glitchEffects({frame, fps, unit, strength: s, seed, ...schedule, idle})}
			contentStyle={e === 'css' && i > 0 ? {translate: `${jitter}px 0px`} : undefined}
			cssWrap={(n) =>
				i > 0 ? (
					<RgbSplit dx={(idle + 14 * i) * unit * (hit.local % 2 ? -1 : 1)}>
						<SlicesCss slices={makeSlices(`${seed}-${hit.seed}`, 3 + Math.floor(5 * i), 70 * i * unit)}>{n}</SlicesCss>
					</RgbSplit>
				) : (
					<RgbSplit dx={idle * unit}>{n}</RgbSplit>
				)
			}
		>
			{children}
		</LookShell>
	);
};

// ---------------------------------------------------------------- stop motion

export type StopMotionLookProps = LookBaseProps & {
	step?: number; // hold every pose this many frames (2 = on twos)
	levels?: number; // colour levels per channel, 0 = keep colours (0)
	boil?: number; // per-pose jitter in px at 1080 (1.2)
};

/** Stop motion: poses held on twos (or threes), a little boil between poses, optional posterized colour. */
export const StopMotionLook: React.FC<StopMotionLookProps> = ({engine, strength = 1, seed = 'stop', step = 2, levels = 0, boil = 1.2, width, height, overlay, children, style}) => {
	const posterized = levels >= 2;
	const e = useLookEngine(posterized ? engine : 'css', '<StopMotionLook>');
	const frame = useCurrentFrame();
	const {unit} = useStage();
	const s = Math.max(0, strength);
	const held = onTwos(frame, Math.max(1, Math.round(step)));
	const bx = (r01(`${seed}-bx-${held}`) - 0.5) * 2 * boil * unit * s;
	const by = (r01(`${seed}-by-${held}`) - 0.5) * 2 * boil * unit * s;
	const br = (r01(`${seed}-br-${held}`) - 0.5) * 0.3 * s;
	return (
		<LookShell
			engine={e}
			label="StopMotionLook"
			width={width}
			height={height}
			style={style}
			overlay={overlay}
			contentStyle={{translate: `${bx}px ${by}px`, rotate: `${br}deg`, scale: String(1 + (3 * boil * s) / 1080)}}
			effects={posterized ? [fx.posterize(levels)] : []}
			cssWrap={posterized ? (n) => <PosterizeCss levels={levels}>{n}</PosterizeCss> : undefined}
		>
			<Freeze frame={held}>{children}</Freeze>
		</LookShell>
	);
};

// ---------------------------------------------------------------- by name

export type LookName = 'film' | 'vhs' | 'crt' | 'newsprint' | 'noir' | 'dreamy' | 'glitch' | 'stopMotion';

export const LOOK_NAMES: readonly LookName[] = ['film', 'vhs', 'crt', 'newsprint', 'noir', 'dreamy', 'glitch', 'stopMotion'];

/** Any look by name with its default settings (the named components take the look-specific props). */
export const Look: React.FC<LookBaseProps & {look: LookName}> = ({look, ...rest}) => {
	switch (look) {
		case 'film':
			return <FilmLook {...rest} />;
		case 'vhs':
			return <VhsLook {...rest} />;
		case 'crt':
			return <CrtLook {...rest} />;
		case 'newsprint':
			return <NewsprintLook {...rest} />;
		case 'noir':
			return <NoirLook {...rest} />;
		case 'dreamy':
			return <DreamyLook {...rest} />;
		case 'glitch':
			return <GlitchLook {...rest} />;
		case 'stopMotion':
			return <StopMotionLook {...rest} />;
		default:
			return <>{rest.children}</>;
	}
};

/**
 * The effect stack of a look for footage: `<Img effects={lookEffects('film', {frame, fps})} />` or a Video from
 * @remotion/media. DOM overlays (dust, OSD, grille, paper) are not included; stop motion needs a component.
 */
export const lookEffects = (look: Exclude<LookName, 'stopMotion'>, o: LookFxOptions): Fx[] => {
	switch (look) {
		case 'film':
			return filmEffects(o);
		case 'vhs':
			return vhsEffects(o);
		case 'crt':
			return crtEffects(o);
		case 'newsprint':
			return newsprintEffects(o);
		case 'noir':
			return noirEffects(o);
		case 'dreamy':
			return dreamyEffects(o);
		case 'glitch':
			return glitchEffects(o);
		default:
			return [];
	}
};
