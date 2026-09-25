// Controls that react on cue: anything that depresses when clicked (Pressable), a themed button that can swap to a
// done state, a switch, a search bar and a form field that type themselves, and key caps for shortcuts. Sizes
// are px at 1080; frames are local to the enclosing Sequence.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp, springAt} from '../motion';
import {UiIcon, type UiIconName} from './Icon';
import {blend, fade, pressDepth, uiPalette, useUiTyping, type UiMode} from './shared';

// ------------------------------------------------------------------ Pressable

export type PressState = {
	press: number; // 0 up, 1 fully down
	after: boolean; // at or after the first press (swap labels, states)
	count: number; // presses so far
	since: number; // frames since the first press (negative before it)
	hover: number; // 0 to 1 once the pointer arrives (when hoverAt is given)
};

export type PressableProps = {
	at?: number | readonly number[]; // press frames: the bottom of each press (cursor clicks, taps)
	hoverAt?: number; // the pointer arrives: a slight lift
	depth?: number; // scale at the bottom of a press (default 0.94)
	darken?: number; // brightness dip while pressed (default 0.08)
	inline?: boolean;
	style?: React.CSSProperties;
	children?: React.ReactNode | ((s: PressState) => React.ReactNode);
};

const pressFrames = (at: PressableProps['at']): number[] => (at === undefined ? [] : typeof at === 'number' ? [at] : [...at].sort((a, b) => a - b));

/** The press state of a control at `frame` (for controls that draw their own pressed look). */
export const pressStateAt = (frame: number, fps: number, at: PressableProps['at'], hoverAt?: number): PressState => {
	const list = pressFrames(at);
	let press = 0;
	for (const p of list) {
		const d = pressDepth(frame, p, fps);
		press = Math.abs(d) > Math.abs(press) ? d : press;
	}
	const count = list.filter((p) => frame >= p).length;
	return {
		press,
		after: count > 0,
		count,
		since: list.length ? frame - list[0] : -Infinity,
		hover: hoverAt === undefined ? 0 : ramp(frame, hoverAt, at30(5, fps), curves.out),
	};
};

/** Wraps anything that should react to a click or a tap: it depresses about 6% and springs back. */
export const Pressable: React.FC<PressableProps> = ({at, hoverAt, depth = 0.94, darken = 0.08, inline = false, style, children}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const s = pressStateAt(frame, fps, at, hoverAt);
	const lift = s.hover * (1 - Math.max(0, s.press));
	return (
		<div
			style={{
				display: inline ? 'inline-block' : 'block',
				scale: `${1 - (1 - depth) * s.press}`,
				translate: lift > 0.001 ? `0px ${-2 * unit * lift}px` : undefined,
				filter: Math.abs(s.press) > 0.001 ? `brightness(${1 - darken * Math.max(0, s.press)})` : undefined,
				...style,
			}}
		>
			{typeof children === 'function' ? children(s) : children}
		</div>
	);
};

// ------------------------------------------------------------------ Button

export type UiButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'dark';

export type UiButtonProps = {
	label: string;
	variant?: UiButtonVariant;
	size?: 'sm' | 'md' | 'lg';
	icon?: UiIconName;
	iconRight?: UiIconName;
	pressAt?: number | readonly number[];
	hoverAt?: number;
	doneLabel?: string; // after the first press the label swaps to this (with a short roll)
	doneIcon?: UiIconName;
	doneVariant?: UiButtonVariant;
	width?: number; // px at 1080 (default: fits the label)
	radius?: number; // px at 1080 (default: from the theme)
	color?: string; // background override for primary
	mode?: UiMode;
	style?: React.CSSProperties;
};

const SIZES = {
	sm: {h: 44, font: 18, pad: 18, icon: 18, gap: 8},
	md: {h: 56, font: 22, pad: 24, icon: 22, gap: 10},
	lg: {h: 72, font: 28, pad: 34, icon: 26, gap: 12},
};

/** A themed button that presses on cue and can change to a done state ("Save" to "Saved"). */
export const UiButton: React.FC<UiButtonProps> = ({
	label,
	variant = 'primary',
	size = 'md',
	icon,
	iconRight,
	pressAt,
	hoverAt,
	doneLabel,
	doneIcon,
	doneVariant,
	width,
	radius,
	color,
	mode = 'auto',
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const z = SIZES[size];
	const s = pressStateAt(frame, fps, pressAt, hoverAt);
	const first = pressFrames(pressAt)[0];
	const swap = doneLabel !== undefined && first !== undefined ? ramp(frame, first + 1, at30(7, fps), curves.out) : 0;
	const look = (v: UiButtonVariant) => {
		switch (v) {
			case 'primary':
				return {bg: color ?? P.accent, fg: color ? '#FFFFFF' : P.onAccent, border: 'transparent'};
			case 'danger':
				return {bg: P.negative, fg: '#FFFFFF', border: 'transparent'};
			case 'dark':
				return {bg: P.dark ? P.text : '#15171C', fg: P.dark ? P.page : '#FFFFFF', border: 'transparent'};
			case 'secondary':
				return {bg: P.raised, fg: P.text, border: P.line};
			default:
				return {bg: fade(P.accent, 0), fg: P.accent, border: 'transparent'};
		}
	};
	const a = look(variant);
	const b = look(doneVariant ?? variant);
	const bg = swap > 0 ? blend(a.bg, b.bg, swap) : a.bg;
	const fg = swap > 0 ? blend(a.fg, b.fg, swap) : a.fg;
	const r = radius ?? Math.min(Math.max(t.radius * 0.6, 0), z.h / 2);
	const content = (text: string, ic?: UiIconName, icR?: UiIconName) => (
		<span style={{display: 'inline-flex', alignItems: 'center', gap: z.gap * unit, whiteSpace: 'nowrap'}}>
			{ic ? <UiIcon name={ic} size={z.icon} color={fg} stroke={2.2} /> : null}
			<span>{text}</span>
			{icR ? <UiIcon name={icR} size={z.icon} color={fg} stroke={2.2} /> : null}
		</span>
	);
	return (
		<div
			style={{
				display: 'inline-flex',
				alignItems: 'center',
				justifyContent: 'center',
				position: 'relative',
				overflow: 'hidden',
				height: z.h * unit,
				width: width ? width * unit : undefined,
				padding: `0 ${z.pad * unit}px`,
				boxSizing: 'border-box',
				borderRadius: r * unit,
				background: bg,
				color: fg,
				border: `${unit}px solid ${swap > 0.5 ? b.border : a.border}`,
				fontFamily: t.type.body,
				fontWeight: t.weights.strong,
				fontSize: z.font * unit,
				letterSpacing: '-0.01em',
				boxShadow: variant === 'primary' || variant === 'danger' || variant === 'dark' ? `0 ${2 * unit}px ${6 * unit}px ${fade('#000000', P.dark ? 0.3 : 0.12)}` : undefined,
				scale: `${1 - 0.06 * s.press}`,
				translate: s.hover > 0.001 ? `0px ${-2 * unit * s.hover * (1 - Math.max(0, s.press))}px` : undefined,
				filter: s.press > 0.001 ? `brightness(${1 - 0.08 * s.press})` : undefined,
				textRendering: 'geometricPrecision',
				...style,
			}}
		>
			{doneLabel === undefined ? (
				content(label, icon, iconRight)
			) : (
				<>
					<span style={{visibility: 'hidden', display: 'grid'}}>
						<span style={{gridArea: '1 / 1'}}>{content(label, icon, iconRight)}</span>
						<span style={{gridArea: '1 / 1'}}>{content(doneLabel, doneIcon ?? icon, undefined)}</span>
					</span>
					<span style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', translate: `0px ${-100 * swap}%`, opacity: 1 - swap}}>
						{content(label, icon, iconRight)}
					</span>
					<span style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', translate: `0px ${100 * (1 - swap)}%`, opacity: swap}}>
						{content(doneLabel, doneIcon ?? icon, undefined)}
					</span>
				</>
			)}
		</div>
	);
};

// ------------------------------------------------------------------ Toggle

export type ToggleProps = {
	on?: boolean; // the state after `at` (before it: the opposite); without `at` it simply shows this state
	at?: number; // the frame it flips (a tap or click lands here)
	label?: string;
	size?: number; // 1 = a 64 x 38 track at 1080
	color?: string; // track colour when on (default: the theme's positive colour)
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** A switch that flips on cue: the knob stretches as it travels and the track fills with colour. */
export const Toggle: React.FC<ToggleProps> = ({on = true, at, label, size = 1, color, mode = 'auto', style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const k = unit * size;
	const W = 64 * k;
	const H = 38 * k;
	const pad = 3 * k;
	const knob = H - 2 * pad;
	const flip = at === undefined ? 1 : springAt(frame, fps, {delay: at, config: 'snappy'});
	const pos = on ? flip : 1 - flip; // 1 = on side
	const travel = at === undefined ? 0 : Math.sin(Math.PI * Math.min(1, Math.max(0, flip)));
	const offColor = P.dark ? blend(P.faint, P.text, 0.18) : blend(P.faint, '#FFFFFF', 0.25);
	const track = blend(offColor, color ?? P.positive, Math.min(1, Math.max(0, pos)));
	const stretch = knob * 0.28 * travel;
	return (
		<div style={{display: 'inline-flex', alignItems: 'center', gap: 16 * k, ...style}}>
			{label ? (
				<span style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 24 * k, color: P.text, whiteSpace: 'nowrap'}}>{label}</span>
			) : null}
			<div style={{position: 'relative', width: W, height: H, borderRadius: H / 2, background: track, flex: '0 0 auto', boxShadow: `inset 0 0 0 ${unit}px ${fade('#000000', 0.06)}`}}>
				<div
					style={{
						position: 'absolute',
						top: pad,
						left: pad + (W - 2 * pad - knob - stretch) * pos,
						width: knob + stretch,
						height: knob,
						borderRadius: knob / 2,
						background: '#FFFFFF',
						boxShadow: `0 ${2 * k}px ${5 * k}px rgba(0, 0, 0, 0.22), 0 0 0 ${0.5 * k}px rgba(0, 0, 0, 0.05)`,
					}}
				/>
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ SearchBar

export type SearchBarProps = {
	text?: string; // what gets typed
	placeholder?: string;
	typeAt?: number; // typing starts (default 12)
	cps?: number; // characters a second (default 14)
	focusAt?: number; // the focus ring appears (default: a little before typing)
	width?: number; // px at 1080 (default 720)
	height?: number; // default 68
	suggestions?: string[]; // a dropdown after typing
	suggestAt?: number; // default: 6 frames after typing ends
	pick?: number; // the suggestion that gets highlighted
	pickAt?: number;
	hint?: string; // a key cap shown while idle, e.g. 'Ctrl K'
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** A search field that focuses, types a query and can open a list of suggestions with one picked. */
export const SearchBar: React.FC<SearchBarProps> = ({
	text = 'quarterly report',
	placeholder = 'Search',
	typeAt = 12,
	cps = 14,
	focusAt,
	width = 720,
	height = 68,
	suggestions,
	suggestAt,
	pick,
	pickAt,
	hint,
	mode = 'auto',
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const typed = useUiTyping(text, typeAt, {cps, seed: `search-${text}`});
	const focus = ramp(frame, focusAt ?? typeAt - at30(8, fps), at30(6, fps), curves.out);
	const font = height * 0.36;
	const sAt = suggestAt ?? typed.endFrame + at30(6, fps);
	const rowH = height * 0.92;
	const list = suggestions ?? [];
	const open = list.length ? ramp(frame, sAt, at30(9, fps), curves.out) : 0;
	const picked = pick !== undefined && pickAt !== undefined ? ramp(frame, pickAt, at30(5, fps), curves.out) : 0;
	const query = text.toLowerCase();
	return (
		<div style={{position: 'relative', width: width * unit, ...style}}>
			<div
				style={{
					display: 'flex',
					alignItems: 'center',
					gap: height * 0.22 * unit,
					height: height * unit,
					padding: `0 ${height * 0.34 * unit}px`,
					boxSizing: 'border-box',
					borderRadius: (height / 2) * unit,
					background: P.dark ? P.field : P.raised,
					border: `${1.5 * unit}px solid ${blend(P.dark ? blend(P.line, P.muted, 0.35) : P.line, P.accent, focus)}`,
					boxShadow: `0 0 0 ${5 * unit * focus}px ${fade(P.accent, 0.22 * focus)}, 0 ${4 * unit}px ${14 * unit}px ${fade('#101828', P.dark ? 0.35 : 0.08)}`,
					fontFamily: t.type.body,
					fontWeight: t.weights.body,
					fontSize: font * unit,
					color: P.text,
				}}
			>
				<UiIcon name="search" size={font * 1.1} color={blend(P.muted, P.accent, focus)} stroke={2.2} />
				<div style={{flex: 1, minWidth: 0, whiteSpace: 'pre', overflow: 'hidden', position: 'relative'}}>
					{typed.count === 0 ? <span style={{color: P.muted}}>{placeholder}</span> : <span>{typed.shown}</span>}
					{focus > 0.5 ? (
						<span
							style={{
								display: 'inline-block',
								width: 2.5 * unit,
								height: font * 1.25 * unit,
								marginLeft: typed.count === 0 ? 0 : 2 * unit,
								verticalAlign: 'middle',
								translate: `0px ${-0.08 * font * unit}px`,
								background: P.accent,
								opacity: typed.caret,
								position: typed.count === 0 ? 'absolute' : 'relative',
								left: typed.count === 0 ? 0 : undefined,
								top: typed.count === 0 ? '50%' : undefined,
								marginTop: typed.count === 0 ? (-font * 0.625 * unit) : undefined,
							}}
						/>
					) : null}
				</div>
				{hint && typed.count === 0 ? (
					<span style={{fontSize: font * 0.72 * unit, color: P.muted, border: `${unit}px solid ${P.line}`, borderRadius: 8 * unit, padding: `${2 * unit}px ${8 * unit}px`, whiteSpace: 'nowrap'}}>{hint}</span>
				) : null}
				{typed.count > 0 ? <UiIcon name="x" size={font * 0.9} color={P.muted} /> : null}
			</div>
			{list.length && open > 0 ? (
				<div
					style={{
						position: 'absolute',
						left: 0,
						right: 0,
						top: (height + 10) * unit,
						display: 'grid',
						gridTemplateRows: `minmax(0, ${open}fr)`,
						opacity: Math.min(1, open * 2),
						translate: `0px ${(1 - open) * -8 * unit}px`,
						zIndex: 5,
					}}
				>
					<div style={{minHeight: 0, overflow: 'hidden', borderRadius: 18 * unit, background: P.raised, boxShadow: `0 0 0 ${unit}px ${P.line}, 0 ${12 * unit}px ${30 * unit}px ${fade('#101828', P.dark ? 0.45 : 0.14)}`}}>
						<div style={{padding: `${8 * unit}px 0`}}>
							{list.map((sug, i) => {
								const idx = sug.toLowerCase().indexOf(query);
								const rowIn = ramp(frame, sAt + i * at30(2, fps), at30(8, fps), curves.out);
								const hi = i === pick ? picked : 0;
								return (
									<div
										key={sug}
										style={{
											display: 'flex',
											alignItems: 'center',
											gap: 16 * unit,
											height: rowH * unit,
											margin: `0 ${8 * unit}px`,
											padding: `0 ${18 * unit}px`,
											borderRadius: 12 * unit,
											background: hi > 0 ? fade(P.accent, 0.12 * hi) : 'transparent',
											fontFamily: t.type.body,
											fontWeight: t.weights.body,
											fontSize: font * 0.92 * unit,
											color: P.text,
											opacity: rowIn,
											translate: `0px ${(1 - rowIn) * 6 * unit}px`,
											whiteSpace: 'pre',
										}}
									>
										<UiIcon name={i === pick ? 'arrowRight' : 'search'} size={font * 0.9} color={hi > 0.5 ? P.accent : P.muted} />
										{idx >= 0 && query.length ? (
											<span>
												{sug.slice(0, idx)}
												<span style={{fontWeight: t.weights.strong}}>{sug.slice(idx, idx + query.length)}</span>
												{sug.slice(idx + query.length)}
											</span>
										) : (
											<span>{sug}</span>
										)}
									</div>
								);
							})}
						</div>
					</div>
				</div>
			) : null}
		</div>
	);
};

// ------------------------------------------------------------------ FormField

export type FormFieldProps = {
	label: string;
	value: string; // what gets typed
	kind?: 'text' | 'email' | 'password' | 'amount';
	placeholder?: string;
	prefix?: string; // shown before the value, e.g. '$'
	typeAt?: number;
	cps?: number;
	focusAt?: number; // default: a little before typing
	blurAt?: number; // the focus ring goes away
	validAt?: number; // a check appears and the border turns positive
	hint?: string; // small text under the field
	width?: number; // px at 1080 (default 560)
	height?: number; // default 64
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** A labelled input that focuses, types (passwords as dots) and can confirm with a check. */
export const FormField: React.FC<FormFieldProps> = ({
	label,
	value,
	kind = 'text',
	placeholder = '',
	prefix,
	typeAt = 10,
	cps = 13,
	focusAt,
	blurAt,
	validAt,
	hint,
	width = 560,
	height = 64,
	mode = 'auto',
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const typed = useUiTyping(value, typeAt, {cps, seed: `field-${label}`});
	const focusIn = ramp(frame, focusAt ?? typeAt - at30(8, fps), at30(6, fps), curves.out);
	const focus = focusIn * (blurAt === undefined ? 1 : 1 - ramp(frame, blurAt, at30(6, fps), curves.in));
	const valid = validAt === undefined ? 0 : springAt(frame, fps, {delay: validAt, config: 'pop'});
	const font = height * 0.37;
	const rest = P.dark ? blend(P.line, P.muted, 0.35) : P.line;
	const border = valid > 0.01 ? blend(blend(rest, P.accent, focus), P.positive, Math.min(1, valid)) : blend(rest, P.accent, focus);
	const shown = kind === 'password' ? '•'.repeat(typed.count) : typed.shown;
	return (
		<div style={{width: width * unit, fontFamily: t.type.body, ...style}}>
			{/* the label grows with the field (a big field in a video kept a 20 px label nobody could read) */}
			<div style={{fontSize: 20 * (height / 64) * unit, fontWeight: t.weights.strong, color: P.muted, marginBottom: 10 * (height / 64) * unit, letterSpacing: '0.01em'}}>{label}</div>
			<div
				style={{
					display: 'flex',
					alignItems: 'center',
					gap: 10 * unit,
					height: height * unit,
					padding: `0 ${20 * unit}px`,
					boxSizing: 'border-box',
					borderRadius: Math.min(t.radius * 0.55, 16) * unit,
					background: P.dark ? P.field : P.raised,
					border: `${1.5 * unit}px solid ${border}`,
					boxShadow: `0 0 0 ${5 * unit * focus}px ${fade(valid > 0.5 ? P.positive : P.accent, 0.2 * focus)}`,
					fontSize: font * unit,
					fontWeight: t.weights.body,
					color: P.text,
				}}
			>
				{prefix ? <span style={{color: P.muted}}>{prefix}</span> : null}
				<div style={{flex: 1, minWidth: 0, whiteSpace: 'pre', overflow: 'hidden', fontVariantNumeric: kind === 'amount' ? 'tabular-nums' : undefined, letterSpacing: kind === 'password' ? '0.12em' : undefined}}>
					{typed.count === 0 && placeholder ? <span style={{color: P.muted}}>{placeholder}</span> : <span>{shown}</span>}
					{focus > 0.5 ? (
						<span style={{display: 'inline-block', width: 2.5 * unit, height: font * 1.2 * unit, marginLeft: 2 * unit, verticalAlign: 'middle', translate: `0px ${-0.08 * font * unit}px`, background: P.accent, opacity: typed.caret}} />
					) : null}
				</div>
				{valid > 0.01 ? (
					<div style={{width: 30 * unit, height: 30 * unit, borderRadius: '50%', background: P.positive, display: 'flex', alignItems: 'center', justifyContent: 'center', scale: `${valid}`}}>
						<UiIcon name="check" size={18} color="#FFFFFF" stroke={3} />
					</div>
				) : null}
			</div>
			{hint ? <div style={{fontSize: 18 * unit, color: P.muted, marginTop: 8 * unit}}>{hint}</div> : null}
		</div>
	);
};

// ------------------------------------------------------------------ KeyCombo

export type KeyComboProps = {
	keys: string[]; // labels; 'cmd', 'shift' and 'enter' draw their symbol
	at?: number; // the caps arrive (staggered)
	pressAt?: number; // all caps press together
	size?: number; // cap height, px at 1080 (default 64)
	mode?: UiMode;
	style?: React.CSSProperties;
};

const SYMBOL_KEYS: Record<string, UiIconName> = {cmd: 'cmd', shift: 'shift', enter: 'enter'};

/** Key caps for a shortcut: they pop in one after another and press together. */
export const KeyCombo: React.FC<KeyComboProps> = ({keys, at = 0, pressAt, size = 64, mode = 'auto', style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const H = size * unit;
	const depth = 5 * unit * (size / 64);
	const down = pressAt === undefined ? 0 : Math.max(0, pressDepth(frame, pressAt, fps));
	return (
		<div style={{display: 'inline-flex', alignItems: 'center', gap: size * 0.22 * unit, ...style}}>
			{keys.map((k, i) => {
				const p = springAt(frame, fps, {delay: at + i * at30(4, fps), config: 'pop'});
				const sym = SYMBOL_KEYS[k.toLowerCase()];
				const face = P.dark ? blend(P.raised, '#FFFFFF', 0.06) : '#FFFFFF';
				return (
					<div
						key={`${k}-${i}`}
						style={{
							minWidth: H,
							height: H,
							padding: `0 ${size * 0.26 * unit}px`,
							boxSizing: 'border-box',
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							borderRadius: size * 0.2 * unit,
							background: face,
							color: P.text,
							fontFamily: t.type.body,
							fontWeight: t.weights.strong,
							fontSize: size * 0.4 * unit,
							boxShadow: `0 ${depth * (1 - down)}px 0 ${blend(face, '#000000', P.dark ? 0.45 : 0.18)}, 0 ${depth * (1 - down) + 4 * unit}px ${10 * unit}px ${fade('#000000', P.dark ? 0.4 : 0.14)}, inset 0 0 0 ${unit}px ${fade(P.text, 0.08)}`,
							translate: `0px ${depth * down}px`,
							scale: `${Math.max(0, p)}`,
							opacity: Math.min(1, Math.max(0, p) * 2),
							whiteSpace: 'nowrap',
						}}
					>
						{sym ? <UiIcon name={sym} size={size * 0.42} color={P.text} stroke={2} /> : k}
					</div>
				);
			})}
		</div>
	);
};
