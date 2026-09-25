// Notifications: a phone banner that drops from the top, a desktop toast that slides in from the side with actions
// and a timer line, and a small status pill; plus a stack where new ones push older ones down. Each enters on
// cue and leaves by the end of its Sequence.
import React from 'react';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp, springAt} from '../motion';
import {useInsidePhone} from './Frames';
import {UiIcon, type UiIconName} from './Icon';
import {fade, inkOn, shadowFor, uiPalette, useUiLife, type UiMode} from './shared';

export type NotificationPlace = 'inline' | 'top' | 'top-right' | 'top-left' | 'bottom' | 'bottom-right' | 'bottom-left';

export type NotificationProps = {
	variant?: 'phone' | 'desktop' | 'pill';
	app?: string; // app name (phone and desktop)
	title: string;
	body?: string;
	time?: string; // default 'now'
	icon?: UiIconName; // glyph on the app tile (default 'bell'; pill: 'check')
	iconColor?: string; // tile colour (default: the accent)
	actions?: string[]; // desktop buttons, e.g. ['Open', 'Later']
	delay?: number; // frames before it arrives
	exit?: number | false; // exit frames; false keeps it
	exitAt?: number;
	place?: NotificationPlace; // default: 'top' for phone, 'top-right' for desktop, 'bottom' for pill
	area?: 'parent' | 'safe'; // position inside the parent box or the frame's safe area (default: phone parent, others safe)
	inset?: number; // margin from the placed edges, px at 1080 (default 20)
	width?: number; // px at 1080
	timer?: boolean; // desktop: a thin line that runs down until the exit (default true)
	mode?: UiMode;
	style?: React.CSSProperties;
};

const placeStyle = (place: NotificationPlace, inset: number, area: {x: number; y: number; w: number; h: number} | null): React.CSSProperties => {
	if (place === 'inline') {
		return {position: 'relative'};
	}
	const box = area ? {left: area.x + inset, top: area.y + inset, right: `calc(100% - ${area.x + area.w - inset}px)`, bottom: `calc(100% - ${area.y + area.h - inset}px)`} : {left: inset, top: inset, right: inset, bottom: inset};
	const s: React.CSSProperties = {position: 'absolute', display: 'flex'};
	const vertical = place.startsWith('top') ? 'top' : 'bottom';
	s[vertical] = box[vertical];
	if (place.endsWith('right')) {
		s.right = box.right;
	} else if (place.endsWith('left')) {
		s.left = box.left;
	} else {
		s.left = box.left;
		s.right = box.right;
		s.justifyContent = 'center';
	}
	return s;
};

/** One notification that arrives on cue and leaves by the end of its Sequence. */
export const Notification: React.FC<NotificationProps> = ({
	variant = 'phone',
	app = 'Driftnote',
	title,
	body,
	time = 'now',
	icon,
	iconColor,
	actions,
	delay = 0,
	exit,
	exitAt,
	place,
	area,
	inset = 20,
	width,
	timer = true,
	mode = 'auto',
	style,
}) => {
	const t = useTheme();
	const {fps, unit, safe} = useStage();
	const phone = useInsidePhone();
	const P = uiPalette(t, mode);
	const life = useUiLife({delay, enter: at30(18, fps), exit: exit ?? at30(12, fps), exitAt});
	const frame = life.frame;
	const u = (v: number) => v * unit;
	const where = place ?? (variant === 'phone' ? 'top' : variant === 'desktop' ? 'top-right' : 'bottom');
	const useSafe = (area ?? (variant === 'phone' ? 'parent' : 'safe')) === 'safe';
	const box = useSafe ? {x: safe.x, y: safe.y, w: safe.w, h: safe.h} : null;
	const tile = iconColor ?? P.accent;
	const glyph = icon ?? (variant === 'pill' ? 'check' : 'bell');
	const pop = springAt(frame, fps, {delay, config: 'settle'});
	const q = life.leave();
	if (frame < delay - 1 || q >= 1) {
		return null;
	}
	const fromTop = where.startsWith('top');
	let content: React.ReactNode;
	let motion: React.CSSProperties;
	if (variant === 'phone') {
		const W = width ?? (phone ? phone.w - 2 * inset : 360);
		motion = {
			translate: `0px ${(fromTop ? -1 : 1) * ((1 - pop) * u(140) + q * u(160))}px`,
			scale: `${0.94 + 0.06 * Math.min(1, pop) - 0.04 * q}`,
			opacity: Math.min(1, pop * 2.5) * (1 - q),
		};
		content = (
			<div style={{width: u(W), padding: u(W * 0.04), boxSizing: 'border-box', borderRadius: u(W * 0.075), background: fade(P.raised, P.dark ? 0.96 : 0.97), boxShadow: shadowFor(P.dark, unit, 2), display: 'flex', gap: u(W * 0.035), alignItems: 'flex-start', fontFamily: t.type.body}}>
				<div style={{width: u(W * 0.12), height: u(W * 0.12), flex: '0 0 auto', borderRadius: u(W * 0.03), background: tile, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					<UiIcon name={glyph} size={W * 0.066} color={inkOn(tile)} stroke={2.3} />
				</div>
				<div style={{flex: 1, minWidth: 0}}>
					<div style={{display: 'flex', alignItems: 'baseline', fontSize: u(W * 0.037), color: P.muted, fontWeight: t.weights.body}}>
						<span style={{textTransform: 'uppercase', letterSpacing: '0.04em'}}>{app}</span>
						<span style={{marginLeft: 'auto'}}>{time}</span>
					</div>
					<div style={{fontSize: u(W * 0.047), fontWeight: t.weights.strong, color: P.text, marginTop: u(3), lineHeight: 1.25}}>{title}</div>
					{body ? <div style={{fontSize: u(W * 0.043), color: P.text, opacity: 0.82, lineHeight: 1.3, marginTop: u(2), display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'}}>{body}</div> : null}
				</div>
			</div>
		);
	} else if (variant === 'desktop') {
		const W = width ?? 440;
		const right = !where.endsWith('left');
		const timeLeft = Number.isFinite(life.exitStart) ? 1 - ramp(frame, delay + at30(10, fps), Math.max(1, life.exitStart - delay - at30(10, fps)), curves.linear) : 1;
		motion = {
			translate: `${(right ? 1 : -1) * ((1 - pop) * u(W * 0.9) + q * u(W * 0.9))}px 0px`,
			opacity: Math.min(1, pop * 2) * (1 - q),
		};
		content = (
			<div style={{position: 'relative', width: u(W), boxSizing: 'border-box', borderRadius: u(18), background: P.raised, boxShadow: shadowFor(P.dark, unit, 3), overflow: 'hidden', fontFamily: t.type.body}}>
				<div style={{display: 'flex', gap: u(16), padding: `${u(20)}px ${u(20)}px ${u(actions?.length ? 14 : 20)}px`}}>
					<div style={{width: u(44), height: u(44), flex: '0 0 auto', borderRadius: '50%', background: fade(tile, 0.16), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
						<UiIcon name={glyph} size={24} color={tile} stroke={2.2} />
					</div>
					<div style={{flex: 1, minWidth: 0}}>
						<div style={{display: 'flex', alignItems: 'baseline', gap: u(10)}}>
							<div style={{fontSize: u(21), fontWeight: t.weights.strong, color: P.text, lineHeight: 1.25}}>{title}</div>
							<div style={{marginLeft: 'auto', fontSize: u(16), color: P.muted, whiteSpace: 'nowrap'}}>{time}</div>
						</div>
						{body ? <div style={{fontSize: u(18.5), color: P.muted, lineHeight: 1.4, marginTop: u(4)}}>{body}</div> : null}
					</div>
				</div>
				{actions?.length ? (
					<div style={{display: 'flex', gap: u(10), padding: `0 ${u(20)}px ${u(18)}px ${u(80)}px`}}>
						{actions.map((a, i) => (
							<div key={a} style={{height: u(38), padding: `0 ${u(16)}px`, borderRadius: u(10), display: 'flex', alignItems: 'center', fontSize: u(17), fontWeight: t.weights.strong, background: i === 0 ? P.accent : 'transparent', color: i === 0 ? P.onAccent : P.text, border: i === 0 ? 'none' : `${unit}px solid ${P.line}`}}>
								{a}
							</div>
						))}
					</div>
				) : null}
				{timer ? <div style={{position: 'absolute', left: 0, bottom: 0, height: u(3), width: `${timeLeft * 100}%`, background: fade(tile, 0.7)}} /> : null}
			</div>
		);
	} else {
		motion = {
			translate: `0px ${(1 - Math.min(1, life.enter())) * u(26) + q * u(14)}px`,
			scale: `${0.9 + 0.1 * pop - 0.04 * q}`,
			opacity: Math.min(1, pop * 2) * (1 - q),
		};
		content = (
			<div style={{display: 'inline-flex', alignItems: 'center', gap: u(12), height: u(64), padding: `0 ${u(26)}px 0 ${u(18)}px`, borderRadius: u(32), background: P.dark ? P.raised : '#15171C', color: P.dark ? P.text : '#FFFFFF', boxShadow: shadowFor(true, unit, 2), fontFamily: t.type.body, fontSize: u(23), fontWeight: t.weights.strong, whiteSpace: 'nowrap'}}>
				<div style={{width: u(32), height: u(32), borderRadius: '50%', background: P.positive, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					<UiIcon name={glyph} size={19} color={inkOn(P.positive)} stroke={3} />
				</div>
				{title}
			</div>
		);
	}
	// inside a phone, a top banner sits just under the status bar
	const phoneTop: React.CSSProperties = phone && variant !== 'desktop' && where.startsWith('top') && where !== 'inline' ? {top: u(phone.top)} : {};
	return (
		<div style={{...placeStyle(where, u(inset), box), ...phoneTop, pointerEvents: 'none', zIndex: 20, ...style}}>
			<div style={{...motion, transformOrigin: fromTop ? '50% 0%' : '50% 100%'}}>{content}</div>
		</div>
	);
};

export type NotificationStackItem = Omit<NotificationProps, 'delay' | 'place' | 'variant' | 'area' | 'inset' | 'exit' | 'exitAt'> & {at: number};

export type NotificationStackProps = {
	items: NotificationStackItem[];
	variant?: 'phone' | 'desktop';
	place?: NotificationPlace;
	area?: 'parent' | 'safe';
	inset?: number;
	gap?: number; // px at 1080 between cards (default 12)
	exit?: number | false;
	exitAt?: number;
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** Several notifications: each new one lands at the top and pushes the others down. */
export const NotificationStack: React.FC<NotificationStackProps> = ({items, variant = 'desktop', place, area, inset = 20, gap = 12, exit, exitAt, mode = 'auto', style}) => {
	const {fps, unit, safe} = useStage();
	const phone = useInsidePhone();
	const life = useUiLife({exit: exit ?? at30(12, fps), exitAt});
	const where = place ?? (variant === 'phone' ? 'top' : 'top-right');
	const useSafe = (area ?? (variant === 'phone' ? 'parent' : 'safe')) === 'safe';
	const box = useSafe ? {x: safe.x, y: safe.y, w: safe.w, h: safe.h} : null;
	const sorted = [...items].sort((a, b) => b.at - a.at); // newest first
	return (
		<div style={{...placeStyle(where, inset * unit, box), ...(phone && where.startsWith('top') ? {top: phone.top * unit} : {}), pointerEvents: 'none', zIndex: 20, ...style}}>
			<div style={{display: 'flex', flexDirection: 'column', alignItems: where.endsWith('left') ? 'flex-start' : where.endsWith('right') ? 'flex-end' : 'center'}}>
				{sorted.map((it, i) => {
					const grow = ramp(life.frame, it.at, at30(10, fps), curves.out);
					if (grow <= 0) {
						return null;
					}
					return (
						<div key={`${it.title}-${it.at}-${i}`} style={{display: 'grid', gridTemplateRows: `minmax(0, ${grow}fr)`}}>
							<div style={{minHeight: 0, overflow: grow < 0.999 ? 'hidden' : 'visible', paddingBottom: gap * unit * grow}}>
								<Notification {...it} variant={variant} place="inline" delay={it.at} exit={exit ?? at30(12, fps)} exitAt={exitAt} mode={mode} />
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
};
