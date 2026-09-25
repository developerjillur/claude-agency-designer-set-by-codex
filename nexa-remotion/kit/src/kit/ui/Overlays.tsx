// Overlays for talking-head and tutorial videos: lower thirds in four looks, a subscribe nudge with a real click, a
// chapter progress bar, a countdown, a focus ring that dims everything but one control, and a tooltip. Every one
// enters on cue, stays inside the safe area and leaves by the last frame of its Sequence.
import React from 'react';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp, springAt, track} from '../motion';
import {Cursor, type CursorKey} from './Cursor';
import {UiIcon} from './Icon';
import {blend, fade, initialsOf, inkOn, pressDepth, shadowFor, uiPalette, useUiLife, type UiMode} from './shared';

// ------------------------------------------------------------------ LowerThird

export type LowerThirdVariant = 'bar' | 'split' | 'minimal' | 'card';

export type LowerThirdProps = {
	name: string;
	role?: string;
	variant?: LowerThirdVariant;
	side?: 'left' | 'right';
	delay?: number;
	exit?: number | false; // exit frames (default 14 at 30 fps); the exit ends on the Sequence's last frame
	exitAt?: number;
	accent?: string;
	scrim?: boolean; // a soft dark gradient behind it and light text, for busy footage (split and minimal)
	size?: number; // 1 = a 46 px name at 1080
	y?: number; // px at 1080 above the bottom of the safe area
	inline?: boolean; // render in flow instead of placing it in the safe area
	style?: React.CSSProperties;
};

/** Name and role for a speaker or a place, in four looks: bar wipe, split rule, minimal, card. */
export const LowerThird: React.FC<LowerThirdProps> = ({
	name,
	role,
	variant = 'bar',
	side = 'left',
	delay = 0,
	exit,
	exitAt,
	accent,
	scrim = false,
	size = 1,
	y = 0,
	inline = false,
	style,
}) => {
	const t = useTheme();
	const {fps, unit, safe, height, width} = useStage();
	const life = useUiLife({delay, enter: at30(22, fps), exit: exit ?? at30(14, fps), exitAt});
	const a = accent ?? t.colors.accent;
	const k = unit * size;
	const right = side === 'right';
	const f = (n: number) => at30(n, fps);
	// exit sub-timings are written for a 14-frame exit and scaled to the real one, so every part is gone by the end
	const lo = (n: number) => Math.round((n / 14) * life.outFrames);
	const q = life.leave();
	if (life.frame < delay || q >= 1) {
		return null;
	}
	const place: React.CSSProperties = inline
		? {position: 'relative'}
		: {
				position: 'absolute',
				bottom: height - safe.y - safe.h + y * unit,
				[right ? 'right' : 'left']: right ? width - safe.x - safe.w : safe.x,
				maxWidth: safe.w,
			};
	const nameText = t.caps ? name.toUpperCase() : name;
	const displayType: React.CSSProperties = {fontFamily: t.type.display, fontWeight: t.weights.display, letterSpacing: `${t.tracking.display * 0.6}em`, lineHeight: 1.1, whiteSpace: 'nowrap', textRendering: 'geometricPrecision'};
	const bodyType: React.CSSProperties = {fontFamily: t.type.body, fontWeight: t.weights.body, lineHeight: 1.2, whiteSpace: 'nowrap', textRendering: 'geometricPrecision'};
	const light = scrim || t.dark;
	const ink = scrim ? '#FFFFFF' : t.colors.text;
	const sub = scrim ? 'rgba(255,255,255,0.82)' : t.colors.muted;
	const scrimLayer = scrim ? (
		<div
			style={{
				position: 'absolute',
				[right ? 'right' : 'left']: -safe.x - 40 * unit,
				bottom: -(height - safe.y - safe.h) - 20 * unit,
				width: 1100 * k,
				height: 420 * k,
				background: `radial-gradient(ellipse 60% 70% at ${right ? '80%' : '20%'} 90%, rgba(0,0,0,0.62) 0%, rgba(0,0,0,0.3) 45%, rgba(0,0,0,0) 75%)`,
				opacity: life.enter(0, f(12)) * (1 - life.leave(lo(4), lo(10))),
				pointerEvents: 'none',
			}}
		/>
	) : null;

	if (variant === 'bar') {
		const nameBg = t.colors.text;
		const nameInk = t.colors.bg;
		const block = life.enter(0, f(9)) * (1 - life.leave(lo(8), lo(6)));
		const nameClip = life.enter(f(4), f(14), curves.inOut) * (1 - life.leave(lo(3), lo(10), curves.inOut));
		const roleClip = life.enter(f(9), f(13), curves.inOut) * (1 - life.leave(0, lo(9), curves.inOut));
		const nameIn = life.enter(f(9), f(12));
		const roleIn = life.enter(f(13), f(12));
		const clip = (p: number) => (right ? `inset(0 0 0 ${(1 - p) * 100}%)` : `inset(0 ${(1 - p) * 100}% 0 0)`);
		return (
			<div style={{...place, display: 'flex', flexDirection: right ? 'row-reverse' : 'row', alignItems: 'stretch', ...style}}>
				<div style={{width: 12 * k, background: a, scale: `1 ${block}`, transformOrigin: '50% 100%', flex: '0 0 auto'}} />
				<div style={{display: 'flex', flexDirection: 'column', alignItems: right ? 'flex-end' : 'flex-start'}}>
					<div style={{background: nameBg, color: nameInk, padding: `${14 * k}px ${26 * k}px ${15 * k}px`, clipPath: clip(nameClip), boxShadow: `0 ${10 * k}px ${30 * k}px rgba(0,0,0,0.18)`}}>
						<div style={{...displayType, fontSize: 46 * k, opacity: nameIn, translate: `${(right ? 1 : -1) * (1 - nameIn) * 18 * k}px 0px`}}>{nameText}</div>
					</div>
					{role ? (
						<div style={{background: a, color: inkOn(a), padding: `${9 * k}px ${22 * k}px ${10 * k}px`, clipPath: clip(roleClip)}}>
							<div style={{...bodyType, fontSize: 25 * k, fontWeight: t.weights.strong, opacity: roleIn, translate: `${(right ? 1 : -1) * (1 - roleIn) * 14 * k}px 0px`}}>{role}</div>
						</div>
					) : null}
				</div>
			</div>
		);
	}

	if (variant === 'split') {
		const rule = life.enter(0, f(11), curves.out) * (1 - life.leave(lo(7), lo(7), curves.in));
		const nameIn = life.enter(f(6), f(17), curves.out);
		const roleIn = life.enter(f(10), f(17), curves.out);
		const nameOut = life.leave(lo(2), lo(9), curves.in);
		const roleOut = life.leave(0, lo(9), curves.in);
		const slide = (p: number, o: number) => `${(right ? 1 : -1) * ((1 - p) + o) * 105}% 0px`;
		return (
			<div style={{...place, ...style}}>
				{scrimLayer}
				<div style={{position: 'relative', display: 'flex', flexDirection: right ? 'row-reverse' : 'row', alignItems: 'stretch', gap: 22 * k}}>
					<div style={{width: 5 * k, borderRadius: 3 * k, background: a, scale: `1 ${rule}`, flex: '0 0 auto'}} />
					<div style={{display: 'flex', flexDirection: 'column', alignItems: right ? 'flex-end' : 'flex-start', gap: 6 * k, paddingTop: 4 * k, paddingBottom: 4 * k}}>
						<div style={{overflow: 'hidden', paddingRight: 8 * k}}>
							<div style={{...displayType, fontSize: 48 * k, color: ink, translate: slide(nameIn, nameOut), textShadow: light ? `0 ${2 * k}px ${12 * k}px rgba(0,0,0,0.35)` : undefined}}>{nameText}</div>
						</div>
						{role ? (
							<div style={{overflow: 'hidden', paddingRight: 8 * k}}>
								<div style={{...bodyType, fontSize: 26 * k, color: scrim ? sub : a, fontWeight: t.weights.strong, translate: slide(roleIn, roleOut)}}>{role}</div>
							</div>
						) : null}
					</div>
				</div>
			</div>
		);
	}

	if (variant === 'minimal') {
		const nameIn = life.enter(0, f(18), curves.out);
		const line = life.enter(f(8), f(14), curves.inOut) * (1 - life.leave(0, lo(8), curves.inOut));
		const roleIn = life.enter(f(11), f(16), curves.out);
		const nameOut = life.leave(lo(4), lo(10), curves.in);
		const roleOut = life.leave(lo(1), lo(10), curves.in);
		return (
			<div style={{...place, display: 'flex', flexDirection: 'column', alignItems: right ? 'flex-end' : 'flex-start', ...style}}>
				{scrimLayer}
				<div style={{position: 'relative', overflow: 'hidden', paddingBottom: '0.12em', marginBottom: '-0.12em'}}>
					<div style={{...displayType, fontSize: 56 * k, color: ink, translate: `0px ${(1 - nameIn) * 110 + nameOut * 110}%`}}>{nameText}</div>
				</div>
				<div style={{position: 'relative', height: 4 * k, width: 84 * k, margin: `${12 * k}px 0 ${14 * k}px`, background: a, borderRadius: 2 * k, scale: `${line} 1`, transformOrigin: right ? '100% 50%' : '0% 50%'}} />
				{role ? (
					<div style={{position: 'relative', overflow: 'hidden'}}>
						<div style={{...bodyType, fontSize: 22 * k, fontWeight: t.weights.strong, color: sub, textTransform: 'uppercase', letterSpacing: `${Math.max(0.08, t.tracking.caps)}em`, translate: `0px ${(1 - roleIn) * 110 + roleOut * 110}%`}}>{role}</div>
					</div>
				) : null}
			</div>
		);
	}

	// card
	const P = uiPalette(t);
	const pop = springAt(life.frame, life.fps, {delay, config: 'settle'});
	const av = springAt(life.frame, life.fps, {delay: delay + f(2), config: 'pop'});
	const textIn = life.enter(f(3), f(12));
	return (
		<div
			style={{
				...place,
				display: 'flex',
				flexDirection: right ? 'row-reverse' : 'row',
				alignItems: 'center',
				gap: 18 * k,
				padding: `${16 * k}px ${30 * k}px ${16 * k}px ${16 * k}px`,
				borderRadius: Math.min(t.radius + 12, 48) * k,
				background: fade(P.raised, 0.96),
				boxShadow: shadowFor(P.dark, unit, 2),
				opacity: Math.min(1, pop * 2) * (1 - q),
				translate: `0px ${(1 - Math.min(1, pop)) * 26 * k + q * 20 * k}px`,
				scale: `${0.96 + 0.04 * Math.min(1, pop)}`,
				transformOrigin: right ? '100% 100%' : '0% 100%',
				...style,
			}}
		>
			<div style={{width: 76 * k, height: 76 * k, borderRadius: '50%', background: a, color: inkOn(a), display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 30 * k, scale: `${Math.max(0, av)}`, flex: '0 0 auto'}}>
				{initialsOf(name)}
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 4 * k, alignItems: right ? 'flex-end' : 'flex-start', opacity: textIn, translate: `${(right ? 1 : -1) * (1 - textIn) * 10 * k}px 0px`}}>
				<div style={{...displayType, fontSize: 38 * k, color: P.text}}>{nameText}</div>
				{role ? <div style={{...bodyType, fontSize: 23 * k, color: P.muted}}>{role}</div> : null}
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ Subscribe

export type SubscribeProps = {
	channel?: string;
	handle?: string;
	delay?: number;
	clickAt?: number; // the Subscribe press (default: delay + 44 at 30 fps)
	bellAt?: number; // the bell press (default: 22 frames later; null for no bell click)
	exit?: number | false;
	exitAt?: number;
	color?: string; // the Subscribe button (default: a clear red)
	width?: number; // px at 1080 (default 720)
	place?: 'bottom' | 'center' | 'inline';
	cursor?: boolean; // draw the pointer (default true)
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** The frames of the Subscribe and bell presses, for sound. */
export const subscribeClicks = (p: Pick<SubscribeProps, 'delay' | 'clickAt' | 'bellAt'>, fps: number): number[] => {
	const click = p.clickAt ?? (p.delay ?? 0) + at30(44, fps);
	const bell = p.bellAt ?? click + at30(22, fps);
	return [click, bell];
};

/** A channel card whose Subscribe button gets clicked (it turns to Subscribed) and whose bell rings. */
export const Subscribe: React.FC<SubscribeProps> = ({
	channel = 'Studio Loop',
	handle = '@studioloop',
	delay = 0,
	clickAt,
	bellAt,
	exit,
	exitAt,
	color = '#E3263A',
	width = 720,
	place = 'bottom',
	cursor = true,
	mode = 'dark',
	style,
}) => {
	const t = useTheme();
	const {fps, unit, safe, height} = useStage();
	const P = uiPalette(t, mode);
	const life = useUiLife({delay, enter: at30(18, fps), exit: exit ?? at30(14, fps), exitAt});
	const frame = life.frame;
	const [click, bell] = subscribeClicks({delay, clickAt, bellAt}, fps);
	const W = Math.min(width, safe.w / unit);
	const H = 136;
	const btnW = 204;
	const btnH = 60;
	const bellD = 60;
	const btnX = W - 24 - bellD - 14 - btnW; // left edge of the button, px at 1080 in the card
	const keys: CursorKey[] = React.useMemo(
		() => [
			{x: W + 40, y: H + 70, at: click - at30(26, fps)},
			{x: btnX + btnW * 0.62, y: H / 2 + 6, at: click - at30(4, fps), click},
			{x: W - 24 - bellD / 2 + 4, y: H / 2 + 8, at: bell - at30(4, fps), click: bell},
		],
		[W, btnX, click, bell, fps],
	);
	const q = life.leave();
	if (frame < delay || q >= 1) {
		return null;
	}
	const pIn = life.enter(0, at30(18, fps), curves.inOut);
	const done = ramp(frame, click + 1, at30(6, fps), curves.out);
	const btnPress = pressDepth(frame, click, fps);
	const bellPress = pressDepth(frame, bell, fps);
	const ring = frame >= bell ? track(frame, [bell, bell + 4, bell + 8, bell + 12, bell + 16, bell + 20], [0, -18, 16, -11, 7, 0], curves.inOut) : 0;
	const bellOn = frame >= bell + 3;
	const check = ramp(frame, click + 3, at30(9, fps), curves.out);
	const u = (v: number) => v * unit;
	const wrap: React.CSSProperties =
		place === 'inline'
			? {position: 'relative'}
			: place === 'center'
				? {position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}
				: {position: 'absolute', left: 0, right: 0, bottom: height - safe.y - safe.h + u(10), display: 'flex', justifyContent: 'center'};
	return (
		<div style={{...wrap, pointerEvents: 'none', ...style}}>
			<div style={{position: 'relative', width: u(W), height: u(H), opacity: pIn * (1 - q), translate: `0px ${(1 - pIn) * u(18) + q * u(24)}px`, scale: `${0.98 + 0.02 * pIn - 0.03 * q}`}}>
				<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', gap: u(18), padding: `0 ${u(24)}px`, borderRadius: u(28), background: P.raised, boxShadow: shadowFor(P.dark, unit, 2), fontFamily: t.type.body}}>
					<div style={{width: u(84), height: u(84), borderRadius: '50%', background: `linear-gradient(135deg, ${t.colors.accent}, ${t.colors.accent2})`, color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(32), flex: '0 0 auto'}}>
						{initialsOf(channel)}
					</div>
					<div style={{flex: 1, minWidth: 0}}>
						<div style={{fontSize: u(31), fontWeight: t.weights.strong, color: P.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', lineHeight: 1.15}}>{channel}</div>
						<div style={{fontSize: u(20), color: P.muted, marginTop: u(4), whiteSpace: 'nowrap'}}>{handle}</div>
					</div>
					<div
						style={{
							position: 'relative',
							width: u(btnW),
							height: u(btnH),
							borderRadius: u(btnH / 2),
							background: blend(color, P.dark ? blend(P.raised, '#FFFFFF', 0.12) : blend(P.raised, '#000000', 0.08), done),
							color: blend('#FFFFFF', P.text, done),
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							gap: u(10),
							fontSize: u(24),
							fontWeight: t.weights.strong,
							scale: `${1 - 0.06 * btnPress}`,
							flex: '0 0 auto',
							overflow: 'hidden',
						}}
					>
						{done < 0.5 ? (
							<span style={{opacity: 1 - done * 2}}>Subscribe</span>
						) : (
							<>
								<svg width={u(24)} height={u(24)} viewBox="0 0 24 24" style={{flex: '0 0 auto'}}>
									<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - check} />
								</svg>
								<span style={{opacity: (done - 0.5) * 2}}>Subscribed</span>
							</>
						)}
					</div>
					<div style={{width: u(bellD), height: u(bellD), borderRadius: '50%', background: bellOn ? blend(P.raised, P.text, 0.14) : blend(P.raised, P.text, 0.07), display: 'flex', alignItems: 'center', justifyContent: 'center', scale: `${1 - 0.1 * bellPress}`, flex: '0 0 auto'}}>
						<div style={{rotate: `${ring}deg`, transformOrigin: '50% 20%'}}>
							<UiIcon name={bellOn ? 'bellFilled' : 'bell'} size={30} color={P.text} stroke={1.9} />
						</div>
					</div>
				</div>
				{cursor ? <Cursor keys={keys} hideAfter={at30(14, fps)} ripple={fade('#FFFFFF', 0.9)} /> : null}
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ ChapterBar

export type UiChapter = {title: string; at: number};

export type ChapterBarProps = {
	chapters: UiChapter[];
	end?: number; // the frame the last chapter ends (default: the Sequence's last frame)
	delay?: number;
	exit?: number | false;
	exitAt?: number;
	place?: 'bottom' | 'top';
	title?: boolean; // show the current chapter's name above the bar (default true)
	panel?: boolean; // sit on a rounded panel so it reads over footage (default true)
	width?: number; // px at 1080 (default: the safe width)
	style?: React.CSSProperties;
};

/** A segmented progress bar with the current chapter's name: the timeline of a tutorial on screen. */
export const ChapterBar: React.FC<ChapterBarProps> = ({chapters, end, delay = 0, exit, exitAt, place = 'bottom', title = true, panel = true, width, style}) => {
	const t = useTheme();
	const {fps, unit, safe, height, width: W, durationInFrames} = useStage();
	const life = useUiLife({delay, enter: at30(16, fps), exit: exit ?? at30(12, fps), exitAt});
	const frame = life.frame;
	const u = (v: number) => v * unit;
	const q = life.leave();
	if (frame < delay || q >= 1 || chapters.length === 0) {
		return null;
	}
	const last = end ?? (Number.isFinite(durationInFrames) ? durationInFrames - 1 : chapters[chapters.length - 1].at + fps * 10);
	const starts = chapters.map((c) => c.at);
	const bounds = [...starts, last];
	const total = Math.max(1, last - starts[0]);
	const P = uiPalette(t);
	const padX = panel ? u(26) : 0;
	const boxW = width !== undefined ? u(width) : safe.w;
	const barW = boxW - 2 * padX;
	const gap = u(6);
	let cur = 0;
	chapters.forEach((c, i) => {
		if (frame >= c.at) {
			cur = i;
		}
	});
	const pIn = life.enter(0, at30(16, fps));
	const progressX = (clamp((frame - starts[0]) / total) * (barW - gap * (chapters.length - 1))) / 1;
	const segs = chapters.map((c, i) => {
		const len = bounds[i + 1] - bounds[i];
		return {w: (len / total) * (barW - gap * (chapters.length - 1)), fill: clamp((frame - bounds[i]) / Math.max(1, len))};
	});
	let x = 0;
	const headX = (() => {
		let acc = 0;
		for (let i = 0; i < segs.length; i++) {
			if (i === cur) {
				return acc + segs[i].w * segs[i].fill;
			}
			acc += segs[i].w + gap;
		}
		return progressX;
	})();
	const change = ramp(frame, chapters[cur].at, at30(9, fps), curves.out);
	const prevTitle = cur > 0 ? chapters[cur - 1].title : '';
	const ink = panel ? P.text : t.colors.text;
	return (
		<div
			style={{
				position: 'absolute',
				left: width !== undefined ? (W - boxW) / 2 : safe.x,
				width: boxW,
				boxSizing: 'border-box',
				padding: panel ? `${u(18)}px ${padX}px ${u(24)}px` : undefined,
				borderRadius: panel ? u(Math.min(t.radius + 4, 26)) : undefined,
				background: panel ? fade(P.raised, 0.94) : undefined,
				boxShadow: panel ? shadowFor(P.dark, unit, 2) : undefined,
				[place === 'bottom' ? 'bottom' : 'top']: place === 'bottom' ? height - safe.y - safe.h : safe.y,
				opacity: pIn * (1 - q),
				translate: `0px ${(1 - pIn) * u(place === 'bottom' ? 14 : -14) + q * u(place === 'bottom' ? 10 : -10)}px`,
				...style,
			}}
		>
			{title ? (
				<div style={{display: 'flex', alignItems: 'baseline', gap: u(14), marginBottom: u(16), fontFamily: t.type.body, whiteSpace: 'nowrap'}}>
					<span style={{fontSize: u(22), fontWeight: t.weights.strong, color: t.colors.accent, fontVariantNumeric: 'tabular-nums'}}>
						{cur + 1}/{chapters.length}
					</span>
					<span style={{position: 'relative', overflow: 'hidden', display: 'inline-block', paddingBottom: '0.12em', marginBottom: '-0.12em'}}>
						<span style={{display: 'inline-block', fontSize: u(28), fontWeight: t.weights.strong, color: ink, translate: `0px ${(1 - change) * 100}%`}}>{chapters[cur].title}</span>
						{cur > 0 && change < 1 ? <span style={{position: 'absolute', left: 0, top: 0, fontSize: u(28), fontWeight: t.weights.strong, color: ink, translate: `0px ${-change * 100}%`}}>{prevTitle}</span> : null}
					</span>
				</div>
			) : null}
			<div style={{position: 'relative', height: u(8)}}>
				{segs.map((s, i) => {
					const left = x;
					x += s.w + gap;
					return (
						<div key={i} style={{position: 'absolute', left, width: s.w, top: 0, height: u(8), borderRadius: u(4), background: fade(ink, t.dark ? 0.2 : 0.14), overflow: 'hidden'}}>
							<div style={{width: `${s.fill * 100}%`, height: '100%', background: i === cur ? t.colors.accent : fade(t.colors.accent, 0.85), borderRadius: u(4)}} />
						</div>
					);
				})}
				<div style={{position: 'absolute', left: headX - u(9), top: u(-5), width: u(18), height: u(18), borderRadius: '50%', background: t.colors.accent, boxShadow: `0 0 0 ${u(3)}px ${panel ? P.raised : t.colors.bg}, 0 ${u(2)}px ${u(6)}px rgba(0,0,0,0.25)`}} />
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ Countdown

export type CountdownProps = {
	from?: number; // counts from this number down to 1 (ring, roll) (default 3)
	each?: number; // frames per number (default: one second)
	seconds?: number; // clock: the time left at the start (default 10)
	variant?: 'ring' | 'roll' | 'clock';
	go?: string; // shown after the last number (ring, roll); '' for nothing (default 'Go')
	delay?: number;
	exit?: number | false;
	exitAt?: number;
	size?: number; // px at 1080 (default 320)
	color?: string;
	plate?: boolean; // a solid disc or card behind the number so it reads over footage (default true)
	style?: React.CSSProperties;
};

/** A countdown: a number with a depleting ring, rolling numbers, or an mm:ss clock. Centred in its parent. */
export const Countdown: React.FC<CountdownProps> = ({from = 3, each, seconds = 10, variant = 'ring', go = 'Go', delay = 0, exit, exitAt, size = 320, color, plate = true, style}) => {
	const t = useTheme();
	const {fps, unit} = useStage();
	const life = useUiLife({delay, enter: at30(10, fps), exit: exit ?? at30(10, fps), exitAt});
	const frame = life.frame;
	const u = (v: number) => v * unit;
	const step = each ?? fps;
	const a = color ?? t.colors.accent;
	const q = life.leave();
	if (frame < delay || q >= 1) {
		return null;
	}
	const el = frame - delay;
	const pIn = life.enter();
	const display: React.CSSProperties = {fontFamily: t.type.display, fontWeight: t.weights.display, color: t.colors.text, lineHeight: 1, fontVariantNumeric: 'tabular-nums', textRendering: 'geometricPrecision', letterSpacing: `${t.tracking.display}em`};
	const box: React.CSSProperties = {position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: pIn * (1 - q), scale: `${0.9 + 0.1 * pIn}`, ...style};
	if (variant === 'clock') {
		const left = Math.max(0, seconds - Math.floor(el / fps));
		const next = Math.max(0, left - 1);
		const roll = left > 0 ? ramp(el % fps, fps - at30(8, fps), at30(8, fps), curves.inOut) : 0;
		const fmt = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
		const aStr = fmt(left);
		const bStr = fmt(next);
		return (
			<div style={box}>
				<div style={{display: 'flex', alignItems: 'center', gap: u(size * 0.02), padding: `${u(size * 0.08)}px ${u(size * 0.14)}px`, borderRadius: u(size * 0.12), background: fade(t.colors.surface, t.dark ? 0.9 : 1), boxShadow: shadowFor(t.dark, unit, 2)}}>
					<UiIcon name="clock" size={size * 0.22} color={a} stroke={2.2} />
					<div style={{...display, fontSize: u(size * 0.36), display: 'flex', marginLeft: u(size * 0.05)}}>
						{aStr.split('').map((ch, i) => {
							const changes = ch !== bStr[i];
							return (
								<span key={i} style={{position: 'relative', display: 'inline-block', overflow: 'hidden', width: ch === ':' ? '0.34em' : '0.62em', textAlign: 'center', height: '1.1em', lineHeight: '1.1em'}}>
									<span style={{display: 'block', translate: `0px ${changes ? -roll * 100 : 0}%`}}>{ch}</span>
									{changes ? <span style={{position: 'absolute', left: 0, right: 0, top: 0, translate: `0px ${(1 - roll) * 100}%`}}>{bStr[i]}</span> : null}
								</span>
							);
						})}
					</div>
				</div>
			</div>
		);
	}
	const idx = Math.floor(el / step); // 0 -> shows `from`
	const n = from - idx;
	const within = el - idx * step;
	const showGo = n <= 0;
	// with no 'Go' the last number fades out instead of vanishing on a cut
	const tail = showGo && !go ? ramp(within, 0, at30(8, fps), curves.in) : 0;
	if (tail >= 1 || (showGo && !go && idx > from)) {
		return null;
	}
	const endless = showGo && !go;
	const label = endless ? '1' : showGo ? go : String(n);
	box.opacity = (box.opacity as number) * (1 - tail);
	box.scale = `${(0.9 + 0.1 * pIn) * (1 - 0.06 * tail)}`;
	const popIn = springAt(within, fps, {config: 'pop'});
	if (variant === 'roll') {
		const roll = endless ? 1 : ramp(within, 0, at30(10, fps), curves.inOut);
		const prev = showGo && idx === from ? '1' : String(n + 1);
		return (
			<div style={box}>
				<div style={{position: 'relative', overflow: 'hidden', height: u(size * 0.9), width: u(size * 1.1), display: 'flex', justifyContent: 'center', borderRadius: u(size * 0.14), background: plate ? fade(t.colors.surface, t.dark ? 0.92 : 0.96) : undefined, boxShadow: plate ? shadowFor(t.dark, unit, 2) : undefined}}>
					<div style={{...display, fontSize: u(size * 0.7), lineHeight: `${u(size * 0.9)}px`, position: 'absolute', top: 0, translate: `0px ${(1 - roll) * 100}%`, color: showGo && !endless ? a : t.colors.text}}>{label}</div>
					{idx > 0 && roll < 1 ? <div style={{...display, fontSize: u(size * 0.7), lineHeight: `${u(size * 0.9)}px`, position: 'absolute', top: 0, translate: `0px ${-roll * 100}%`}}>{prev}</div> : null}
				</div>
			</div>
		);
	}
	// ring
	const R = 42;
	const deplete = endless ? 1 : showGo ? 1 : ramp(within, 0, step, curves.linear);
	return (
		<div style={box}>
			<div style={{position: 'relative', width: u(size), height: u(size)}}>
				{plate ? <div style={{position: 'absolute', inset: u(size * 0.02), borderRadius: '50%', background: fade(t.colors.surface, t.dark ? 0.92 : 0.96), boxShadow: shadowFor(t.dark, unit, 2)}} /> : null}
				<svg width={u(size)} height={u(size)} viewBox="0 0 100 100" style={{position: 'absolute', inset: 0, rotate: '-90deg'}}>
					<circle cx={50} cy={50} r={R} fill="none" stroke={fade(t.colors.text, 0.1)} strokeWidth={4} />
					<circle cx={50} cy={50} r={R} fill="none" stroke={a} strokeWidth={4} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={showGo ? 0 : deplete} opacity={showGo ? 1 - ramp(within, 0, at30(12, fps), curves.out) : 1} />
				</svg>
				<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					<div style={{...display, fontSize: u(size * (showGo && !endless ? 0.3 : 0.46)), color: showGo && !endless ? a : t.colors.text, scale: `${endless ? 1 : 0.6 + 0.4 * Math.max(0, popIn)}`, opacity: endless || !showGo ? 1 : Math.min(1, 0.35 + within / Math.max(1, at30(3, fps)))}}>{label}</div>
				</div>
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ FocusRing

export type FocusKey = {at: number; x: number; y: number; w: number; h: number; r?: number}; // px at 1080 in the parent

export type FocusRingProps = {
	keys: FocusKey[]; // the hole is on each rectangle at its frame `at`, holds, then glides to the next
	move?: number; // frames each glide takes, ending on the next key's frame (default 14 at 30 fps)
	dim?: number; // darkness outside (default 0.55)
	ring?: string | false; // an outline around the hole (default: the accent)
	pad?: number; // px at 1080 added around each rectangle (default 10)
	delay?: number;
	exit?: number | false;
	exitAt?: number;
};

/** Dims everything in its parent except one rounded hole that moves from control to control. */
export const FocusRing: React.FC<FocusRingProps> = ({keys, move, dim = 0.55, ring, pad = 10, delay, exit, exitAt}) => {
	const t = useTheme();
	const {fps, unit} = useStage();
	const ks = [...keys].sort((p, q) => p.at - q.at);
	const life = useUiLife({delay: delay ?? ks[0]?.at ?? 0, enter: at30(12, fps), exit: exit ?? at30(12, fps), exitAt});
	const frame = life.frame;
	if (ks.length === 0) {
		return null;
	}
	// hold on each rectangle, then glide to the next so that it arrives exactly on that key's frame
	const glide = move ?? at30(14, fps);
	const frames: number[] = [ks[0].at];
	const plan: FocusKey[] = [ks[0]];
	for (let i = 1; i < ks.length; i++) {
		const leave = Math.max(frames[frames.length - 1] + 1, ks[i].at - glide);
		if (leave < ks[i].at) {
			frames.push(leave);
			plan.push(ks[i - 1]);
		}
		frames.push(ks[i].at);
		plan.push(ks[i]);
	}
	const v = (pick: (k: FocusKey) => number) => (plan.length === 1 ? pick(plan[0]) : track(frame, frames, plan.map(pick), curves.inOut));
	const x = v((k) => k.x) - pad;
	const y = v((k) => k.y) - pad;
	const w = v((k) => k.w) + 2 * pad;
	const h = v((k) => k.h) + 2 * pad;
	const r = v((k) => k.r ?? 14) + pad * 0.6;
	const o = life.enter() * (1 - life.leave());
	if (o <= 0.001) {
		return null;
	}
	const rc = ring === false ? null : (ring ?? t.colors.accent);
	return (
		<div style={{position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 30}}>
			<div
				style={{
					position: 'absolute',
					left: x * unit,
					top: y * unit,
					width: w * unit,
					height: h * unit,
					borderRadius: r * unit,
					boxShadow: `0 0 0 ${4000 * unit}px rgba(6, 8, 14, ${dim * o})${rc ? `, inset 0 0 0 ${3 * unit}px ${fade(rc, o)}` : ''}`,
				}}
			/>
		</div>
	);
};

// ------------------------------------------------------------------ UiTooltip

export type UiTooltipProps = {
	x: number; // the point it points at, px at 1080 in the parent
	y: number;
	text: string;
	side?: 'top' | 'bottom' | 'left' | 'right'; // where the bubble sits (default 'top')
	at?: number; // it pops in
	exit?: number | false;
	exitAt?: number;
	size?: number; // font px at 1080 (default 22)
	mode?: UiMode;
};

/** A small dark bubble with a pointer that pops out of the point it explains. */
export const UiTooltip: React.FC<UiTooltipProps> = ({x, y, text, side = 'top', at = 0, exit, exitAt, size = 22, mode = 'auto'}) => {
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const life = useUiLife({delay: at, enter: at30(12, fps), exit: exit ?? at30(10, fps), exitAt});
	const frame = life.frame;
	const pop = springAt(frame, fps, {delay: at, config: 'pop'});
	const q = life.leave();
	if (frame < at || q >= 1) {
		return null;
	}
	const bg = P.dark ? '#F4F5F7' : '#16181D';
	const fg = P.dark ? '#16181D' : '#FFFFFF';
	const arrow = 9 * unit;
	const gap = 12 * unit;
	const pos: React.CSSProperties =
		side === 'top'
			? {left: x * unit, top: y * unit - gap, translate: '-50% -100%', transformOrigin: '50% 100%'}
			: side === 'bottom'
				? {left: x * unit, top: y * unit + gap, translate: '-50% 0%', transformOrigin: '50% 0%'}
				: side === 'left'
					? {left: x * unit - gap, top: y * unit, translate: '-100% -50%', transformOrigin: '100% 50%'}
					: {left: x * unit + gap, top: y * unit, translate: '0% -50%', transformOrigin: '0% 50%'};
	const tip: React.CSSProperties =
		side === 'top'
			? {left: '50%', bottom: -arrow + 1, marginLeft: -arrow, borderLeft: `${arrow}px solid transparent`, borderRight: `${arrow}px solid transparent`, borderTop: `${arrow}px solid ${bg}`}
			: side === 'bottom'
				? {left: '50%', top: -arrow + 1, marginLeft: -arrow, borderLeft: `${arrow}px solid transparent`, borderRight: `${arrow}px solid transparent`, borderBottom: `${arrow}px solid ${bg}`}
				: side === 'left'
					? {top: '50%', right: -arrow + 1, marginTop: -arrow, borderTop: `${arrow}px solid transparent`, borderBottom: `${arrow}px solid transparent`, borderLeft: `${arrow}px solid ${bg}`}
					: {top: '50%', left: -arrow + 1, marginTop: -arrow, borderTop: `${arrow}px solid transparent`, borderBottom: `${arrow}px solid transparent`, borderRight: `${arrow}px solid ${bg}`};
	return (
		<div style={{position: 'absolute', ...pos, zIndex: 35, pointerEvents: 'none', scale: `${(0.8 + 0.2 * Math.max(0, pop)) * (1 - 0.1 * q)}`, opacity: Math.min(1, pop * 2) * (1 - q)}}>
			<div style={{position: 'relative', background: bg, color: fg, padding: `${10 * unit}px ${16 * unit}px`, borderRadius: 12 * unit, fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: size * unit, whiteSpace: 'nowrap', boxShadow: `0 ${6 * unit}px ${18 * unit}px rgba(0,0,0,0.25)`}}>
				{text}
				<div style={{position: 'absolute', width: 0, height: 0, ...tip}} />
			</div>
		</div>
	);
};
