// Surfaces that hold content: cards (solid, outline, glass, paper, tonal), pills and badges, scrims over pictures,
// frames for pictures, a decorative border for the whole frame, and a plain app panel (no device around it).
import React, {createContext, useContext} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {contrast, ensureContrast, mix, readableOn, withAlpha} from './color';
import {useGrainUrl} from './grain';
import {elevation, hairline, surfaceAt, tonal} from './tokens';

const px = (v: number | string | undefined, unit: number) => (typeof v === 'number' ? v * unit : v);

// ---------------------------------------------------------------- tone of what is behind

const OnDarkContext = createContext<boolean | null>(null);

/**
 * Tells the surfaces inside that they sit on a dark (or light) backdrop that is not the theme's ground, such as
 * a photo under a dark scrim. FullBleed and the hard-seam Split set it for you.
 */
export const OnTone: React.FC<{dark: boolean; children: React.ReactNode}> = ({dark, children}) => (
	<OnDarkContext.Provider value={dark}>{children}</OnDarkContext.Provider>
);

/** Whether the backdrop here is dark: the nearest OnTone, else the theme's own. */
export const useOnDark = (): boolean => {
	const ctx = useContext(OnDarkContext);
	const t = useTheme();
	return ctx ?? t.dark;
};

// ---------------------------------------------------------------- card

export type CardVariant = 'solid' | 'outline' | 'glass' | 'paper' | 'tonal';

export type CardProps = {
	variant?: CardVariant;
	elevation?: number; // 0 to 5 (default: solid 2, glass 3, paper 2, outline and tonal 0)
	radius?: number; // px at 1080 (default: the theme's radius)
	padding?: number | [number, number]; // px at 1080, [vertical, horizontal] (default 44)
	width?: number | string; // a number is px at 1080
	height?: number | string;
	color?: string; // the surface (tonal: the tint)
	blur?: number; // glass: backdrop blur px at 1080 (default 28)
	tilt?: number; // degrees, for pinned paper cut-outs
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

/**
 * A surface for a group of content, from the theme. Solid for most things; tonal for flat grouping without
 * shadows; outline for secondary items; paper for collage looks; glass only over a busy, moving ground (it costs a
 * backdrop blur every frame, and glass on a flat ground is just a pale card).
 */
// the printed grain of a paper card: its own component so only paper cards load the tile
const PaperTooth: React.FC<{radius: number}> = ({radius}) => {
	const {unit} = useStage();
	const grain = useGrainUrl('grey');
	// z-index -1 inside an isolated card: under the content, over the card's own fill, and the children stay
	// direct children (so their absolute positions are relative to the card)
	return (
		<div
			style={{
				position: 'absolute',
				inset: 0,
				zIndex: -1,
				borderRadius: radius,
				backgroundImage: grain,
				backgroundSize: `${Math.round(256 * 1.25 * unit)}px`,
				mixBlendMode: 'overlay',
				opacity: 0.45,
				pointerEvents: 'none',
			}}
		/>
	);
};

export const Card: React.FC<CardProps> = ({variant = 'solid', elevation: level, radius, padding = 44, width, height, color, blur = 28, tilt = 0, style, children}) => {
	const t = useTheme();
	const {unit} = useStage();
	const lv = level ?? (variant === 'solid' || variant === 'paper' ? 2 : variant === 'glass' ? 3 : 0);
	const r = (radius ?? t.radius) * unit;
	const pad = Array.isArray(padding) ? `${padding[0] * unit}px ${padding[1] * unit}px` : `${padding * unit}px`;
	const base: React.CSSProperties = {
		position: 'relative',
		boxSizing: 'border-box',
		width: px(width, unit),
		height: px(height, unit),
		padding: pad,
		borderRadius: r,
		color: t.colors.text,
		fontFamily: t.type.body,
		rotate: tilt ? `${tilt}deg` : undefined,
	};
	let look: React.CSSProperties;
	let texture: React.ReactNode = null;
	if (variant === 'outline') {
		look = {border: `${1.5 * unit}px solid ${withAlpha(t.colors.text, t.dark ? 0.24 : 0.18)}`, boxShadow: elevation(lv, t, unit)};
	} else if (variant === 'tonal') {
		look = {background: color ? tonal(t, color) : tonal(t), boxShadow: elevation(lv, t, unit)};
	} else if (variant === 'glass') {
		const tint = t.dark ? withAlpha(mix(t.colors.surface, t.colors.text, 0.06), 0.42) : withAlpha(color ?? '#FFFFFF', 0.46);
		look = {
			background: `linear-gradient(160deg, ${withAlpha('#FFFFFF', t.dark ? 0.1 : 0.34)} 0%, ${withAlpha('#FFFFFF', 0)} 48%), ${tint}`,
			backdropFilter: `blur(${blur * unit}px) saturate(1.35)`,
			WebkitBackdropFilter: `blur(${blur * unit}px) saturate(1.35)`,
			border: `${unit}px solid ${withAlpha('#FFFFFF', t.dark ? 0.14 : 0.55)}`,
			boxShadow: `${elevation(lv, t, unit)}, inset 0 ${unit}px 0 ${withAlpha('#FFFFFF', t.dark ? 0.12 : 0.6)}`,
		};
	} else if (variant === 'paper') {
		const sheet = color ?? (t.dark ? t.colors.surface : mix(t.colors.surface, '#F7F1E6', 0.35));
		look = {background: sheet, boxShadow: `0 ${unit}px ${unit}px ${withAlpha('#000000', 0.06)}, ${elevation(lv, t, unit)}`};
		texture = <PaperTooth radius={r} />;
	} else {
		look = {
			background: color ?? surfaceAt(lv, t),
			border: `${unit}px solid ${hairline(t)}`,
			boxShadow: t.dark ? `${elevation(lv, t, unit)}, inset 0 ${unit}px 0 ${withAlpha('#FFFFFF', 0.05)}` : elevation(lv, t, unit),
		};
	}
	return (
		<div style={{...base, ...look, isolation: 'isolate', ...style}}>
			{texture}
			{children}
		</div>
	);
};

// ---------------------------------------------------------------- pill and badge

export type ChipVariant = 'solid' | 'soft' | 'outline' | 'glass';

export type PillProps = {
	variant?: ChipVariant; // default soft
	color?: string; // default the accent
	size?: number; // font size px at 1080 (default 30: the smallest size that reads on a phone)
	caps?: boolean;
	dot?: boolean | string; // a status dot, in the pill colour or the given one
	icon?: React.ReactNode;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

const chipColors = (variant: ChipVariant, color: string, bg: string, accent: string, onAccent: string, ink: string, dark: boolean) => {
	if (variant === 'solid') {
		// small text: keep the theme's onAccent only where it reaches 4.5:1 (white on coral or green does not)
		const on = color === accent ? onAccent : '#FFFFFF';
		return {background: color, text: contrast(on, color) >= 4.5 ? on : readableOn(color, on, ink), border: 'transparent'};
	}
	if (variant === 'outline') {
		return {background: 'transparent', text: ensureContrast(color, bg, 4.5), border: withAlpha(color, 0.7)};
	}
	if (variant === 'glass') {
		return {background: withAlpha('#FFFFFF', dark ? 0.16 : 0.55), text: dark ? '#FFFFFF' : '#111111', border: withAlpha('#FFFFFF', dark ? 0.26 : 0.65)};
	}
	const fill = mix(bg, color, dark ? 0.24 : 0.14);
	return {background: fill, text: ensureContrast(color, fill, 4.5), border: 'transparent'};
};

const Chip: React.FC<PillProps & {shape: 'pill' | 'badge'}> = ({variant = 'soft', color, size, caps = false, dot, icon, children, style, shape}) => {
	const t = useTheme();
	const {unit} = useStage();
	const onDark = useOnDark();
	const c = color ?? t.colors.accent;
	const fs = (size ?? (shape === 'pill' ? 30 : 28)) * unit;
	// on a backdrop other than the theme's ground, soft and outline chips measure contrast against a stand-in
	const ground = onDark === t.dark ? t.colors.bg : onDark ? '#141414' : '#F4F4F4';
	// the theme's darkest colour, for text on a bright fill
	const ink = t.dark ? t.colors.bg : t.colors.text;
	const k = chipColors(variant, c, ground, t.colors.accent, t.colors.onAccent, ink, onDark);
	const dotColor = typeof dot === 'string' ? dot : variant === 'solid' ? k.text : c;
	return (
		<div
			style={{
				display: 'inline-flex',
				alignItems: 'center',
				gap: '0.45em',
				boxSizing: 'border-box',
				fontFamily: t.type.body,
				fontWeight: shape === 'badge' ? Math.max(t.weights.strong, 700) : t.weights.strong,
				fontSize: fs,
				lineHeight: 1,
				letterSpacing: caps ? `${t.tracking.caps}em` : shape === 'badge' ? '0.01em' : '0em',
				textTransform: caps ? 'uppercase' : 'none',
				fontVariantNumeric: 'tabular-nums',
				whiteSpace: 'nowrap',
				padding: shape === 'pill' ? '0.42em 0.95em' : '0.3em 0.55em',
				borderRadius: shape === 'pill' ? 999 : Math.min(t.radius, 12) * unit,
				background: k.background,
				color: k.text,
				border: `${Math.max(1, 2 * unit)}px solid ${k.border}`,
				backdropFilter: variant === 'glass' ? `blur(${14 * unit}px)` : undefined,
				...style,
			}}
		>
			{dot ? <span style={{width: '0.5em', height: '0.5em', borderRadius: '50%', background: dotColor, flex: 'none'}} /> : null}
			{icon}
			{children}
		</div>
	);
};

/** A rounded label: a tag, a status, a category. Soft by default (tinted fill, text pushed to AA contrast). */
export const Pill: React.FC<PillProps> = (props) => <Chip {...props} shape="pill" />;

/** A compact, bolder label for numbers and flags ("NEW", "+24%", "4.9"): tabular figures, small radius. */
export const Badge: React.FC<PillProps> = ({variant = 'solid', ...rest}) => <Chip {...rest} variant={variant} shape="badge" />;

// ---------------------------------------------------------------- scrim

export type ScrimProps = {
	side?: 'bottom' | 'top' | 'left' | 'right' | 'center' | 'full';
	size?: number; // how far it reaches, a fraction of the frame (default 0.62)
	strength?: number; // darkness at the strongest point, 0 to 1 (default 0.72)
	color?: string; // default black; use the theme's bg for a light scrim under dark text
	style?: React.CSSProperties;
};

/**
 * A legibility gradient over a picture, behind text. The stops follow an eased curve, so no edge shows where the
 * scrim starts (a two-stop linear gradient leaves a visible line).
 */
export const Scrim: React.FC<ScrimProps> = ({side = 'bottom', size = 0.62, strength = 0.72, color = '#000000', style}) => {
	const s = clamp(strength, 0, 1);
	const reach = clamp(size, 0.05, 1) * 100;
	const stops = (n = 10) =>
		Array.from({length: n}, (_, i) => {
			const p = i / (n - 1);
			const a = s * (1 - p) * (1 - p) * (1 + 2 * p);
			return `${withAlpha(color, a)} ${(p * reach).toFixed(1)}%`;
		}).join(', ');
	let background: string;
	if (side === 'full') {
		background = `linear-gradient(180deg, ${withAlpha(color, s * 0.55)} 0%, ${withAlpha(color, s * 0.75)} 100%)`;
	} else if (side === 'center') {
		background = `radial-gradient(ellipse ${reach}% ${reach * 0.8}% at 50% 50%, ${stops()}, ${withAlpha(color, 0)} 100%)`;
	} else {
		const dir = {bottom: '0deg', top: '180deg', left: '90deg', right: '270deg'}[side];
		background = `linear-gradient(${dir}, ${stops()}, ${withAlpha(color, 0)} 100%)`;
	}
	return <AbsoluteFill style={{background, pointerEvents: 'none', ...style}} />;
};

// ---------------------------------------------------------------- frame (for pictures)

export type FrameProps = {
	variant?: 'mat' | 'line' | 'polaroid' | 'bare';
	width?: number; // the picture's size, px at 1080 (default 720 x 480)
	height?: number;
	mat?: number; // the border around the picture, px at 1080
	color?: string; // the mat (default white on light themes, a lifted surface on dark ones)
	radius?: number; // px at 1080
	elevation?: number; // default 3
	tilt?: number; // degrees
	caption?: React.ReactNode; // polaroid: handwritten caption under the picture
	children?: React.ReactNode; // the picture: an <Img> sized 100% with objectFit cover
	style?: React.CSSProperties;
};

/** A finished frame around a picture: a mat and a shadow, a hairline, or an instant photo with a caption. */
export const Frame: React.FC<FrameProps> = ({variant = 'mat', width = 720, height = 480, mat, color, radius, elevation: level = 3, tilt = 0, caption, children, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	const sheet = color ?? (t.dark ? mix(t.colors.surface, '#FFFFFF', 0.06) : '#FFFFFF');
	const m = (mat ?? (variant === 'polaroid' ? 22 : variant === 'mat' ? 18 : 0)) * unit;
	const bottom = variant === 'polaroid' ? Math.max(m, 92 * unit) : m;
	const r = (radius ?? (variant === 'polaroid' ? 3 : variant === 'line' ? t.radius : Math.min(t.radius, 14))) * unit;
	const innerR = Math.max(0, r - m * 0.6);
	return (
		<div
			style={{
				position: 'relative',
				boxSizing: 'content-box',
				width: width * unit,
				height: height * unit,
				padding: variant === 'bare' || variant === 'line' ? 0 : `${m}px ${m}px ${bottom}px ${m}px`,
				background: variant === 'mat' || variant === 'polaroid' ? sheet : 'transparent',
				borderRadius: r,
				boxShadow: variant === 'line' ? undefined : elevation(level, t, unit),
				rotate: tilt ? `${tilt}deg` : undefined,
				...style,
			}}
		>
			<div
				style={{
					position: 'relative',
					width: '100%',
					height: '100%',
					overflow: 'hidden',
					borderRadius: variant === 'line' ? r : innerR,
					background: t.colors.bg2,
					boxShadow: variant === 'line' ? `inset 0 0 0 ${Math.max(1, 1.5 * unit)}px ${withAlpha(t.colors.text, 0.16)}` : `inset 0 0 0 ${unit}px ${withAlpha('#000000', 0.06)}`,
				}}
			>
				{children}
				{variant === 'line' ? (
					<div style={{position: 'absolute', inset: 0, borderRadius: r, boxShadow: `inset 0 0 0 ${Math.max(1, 1.5 * unit)}px ${withAlpha(t.colors.text, 0.16)}`, pointerEvents: 'none'}} />
				) : null}
			</div>
			{variant === 'polaroid' && caption ? (
				<div
					style={{
						position: 'absolute',
						left: m,
						right: m,
						bottom: 0,
						height: bottom,
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						fontFamily: t.type.hand,
						fontSize: 40 * unit,
						color: '#2A2724',
					}}
				>
					{caption}
				</div>
			) : null}
		</div>
	);
};

// ---------------------------------------------------------------- border (the whole frame)

export type BorderProps = {
	kind?: 'rule' | 'double' | 'corners' | 'brackets';
	inset?: number | 'safe'; // px at 1080 from the frame edge, or 'safe': between the edge and the safe area
	color?: string; // default the theme's text at 55% (accent for brackets)
	weight?: number; // px at 1080 (default 2; brackets 5)
	length?: number; // corner arm length, px at 1080 (default 64)
	delay?: number; // frames before it draws on
	duration?: number; // draw-on frames (default 24 at 30 fps); 0 = already drawn
	style?: React.CSSProperties;
};

/** A decorative border for the whole frame: an inset rule, a double rule, or corner marks, drawn on. */
export const Border: React.FC<BorderProps> = ({kind = 'rule', inset = 'safe', color, weight, length = 64, delay = 0, duration, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, safe, unit, fps} = useStage();
	const d = duration ?? at30(24, fps);
	const p = d <= 0 ? 1 : ramp(frame, delay, d, curves.inOut);
	const ins = inset === 'safe' ? Math.round(Math.min(safe.x, safe.y) * 0.6) : inset * unit;
	const wgt = (weight ?? (kind === 'brackets' ? 5 : 2)) * unit;
	const ink = color ?? (kind === 'brackets' ? t.colors.accent : withAlpha(t.colors.text, 0.55));
	const x0 = ins + wgt / 2;
	const y0 = ins + wgt / 2;
	const x1 = width - ins - wgt / 2;
	const y1 = height - ins - wgt / 2;
	const rect = (o: number) => `M ${x0 + o} ${y0 + o} H ${x1 - o} V ${y1 - o} H ${x0 + o} Z`;
	const arm = length * unit;
	const corners = [
		`M ${x0} ${y0 + arm} V ${y0} H ${x0 + arm}`,
		`M ${x1 - arm} ${y0} H ${x1} V ${y0 + arm}`,
		`M ${x1} ${y1 - arm} V ${y1} H ${x1 - arm}`,
		`M ${x0 + arm} ${y1} H ${x0} V ${y1 - arm}`,
	];
	const paths = kind === 'rule' ? [rect(0)] : kind === 'double' ? [rect(0), rect(10 * unit)] : corners;
	return (
		<svg width={width} height={height} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', overflow: 'visible', ...style}}>
			{paths.map((dPath, i) => (
				<path
					key={i}
					d={dPath}
					fill="none"
					stroke={ink}
					strokeWidth={kind === 'double' && i === 1 ? wgt * 0.5 : wgt}
					strokeLinecap={kind === 'brackets' ? 'round' : 'butt'}
					strokeLinejoin={kind === 'brackets' ? 'round' : 'miter'}
					pathLength={1}
					strokeDasharray={1}
					strokeDashoffset={1 - p}
				/>
			))}
		</svg>
	);
};

// ---------------------------------------------------------------- panel

export type PanelProps = {
	width?: number; // px at 1080 (default 1100)
	height?: number; // px at 1080 (default 680)
	title?: string;
	bar?: 'dots' | 'title' | 'none'; // the top strip: window dots, a centred title, or nothing
	tone?: 'auto' | 'light' | 'dark'; // default: the theme's
	elevation?: number; // default 4
	radius?: number; // px at 1080 (default the theme's radius, at most 22)
	padding?: number; // content padding px at 1080 (default 0: screenshots fill it)
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** An app window without a device around it: a surface, a slim top strip and a clipped content area. */
export const Panel: React.FC<PanelProps> = ({width = 1100, height = 680, title, bar = 'dots', tone = 'auto', elevation: level = 4, radius, padding = 0, children, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	const dark = tone === 'auto' ? t.dark : tone === 'dark';
	const surface = tone === 'auto' ? surfaceAt(level, t) : dark ? '#17191E' : '#FFFFFF';
	const strip = dark ? mix(surface, '#FFFFFF', 0.04) : mix(surface, '#000000', 0.025);
	const ink = dark ? '#E8EAED' : '#1F2328';
	const r = (radius ?? Math.min(t.radius, 22)) * unit;
	const barH = bar === 'none' ? 0 : 58 * unit;
	return (
		<div
			style={{
				position: 'relative',
				width: width * unit,
				height: height * unit,
				borderRadius: r,
				overflow: 'hidden',
				background: surface,
				color: ink,
				fontFamily: t.type.body,
				textAlign: 'left',
				border: `${unit}px solid ${dark ? withAlpha('#FFFFFF', 0.09) : withAlpha('#000000', 0.08)}`,
				boxShadow: elevation(level, {...t, dark}, unit),
				display: 'flex',
				flexDirection: 'column',
				...style,
			}}
		>
			{bar !== 'none' ? (
				<div
					style={{
						height: barH,
						flex: 'none',
						background: strip,
						borderBottom: `${unit}px solid ${dark ? withAlpha('#FFFFFF', 0.07) : withAlpha('#000000', 0.07)}`,
						display: 'flex',
						alignItems: 'center',
						padding: `0 ${22 * unit}px`,
						position: 'relative',
					}}
				>
					{bar === 'dots'
						? ['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
								<span key={c} style={{width: 15 * unit, height: 15 * unit, borderRadius: '50%', background: c, marginRight: 10 * unit, boxShadow: `inset 0 0 0 ${unit * 0.8}px ${withAlpha('#000000', 0.12)}`}} />
							))
						: null}
					{title ? (
						<div style={{position: 'absolute', left: 0, right: 0, textAlign: 'center', fontSize: 23 * unit, fontWeight: t.weights.strong, color: withAlpha(ink, 0.62)}}>{title}</div>
					) : null}
				</div>
			) : null}
			<div style={{position: 'relative', flex: 1, padding: padding * unit, overflow: 'hidden'}}>{children}</div>
		</div>
	);
};
