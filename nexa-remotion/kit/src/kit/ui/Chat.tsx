// A chat thread: messages arrive one after another from two sides, the other side shows typing dots first, older
// messages are pushed up (each row grows to its natural height, so nothing is measured), and 'me' messages can be
// typed into a composer and sent. Sizes px at 1080; frames local to the enclosing Sequence.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, readingFrames, useStage, useTheme} from '../core';
import {ramp, springAt} from '../motion';
import {UiIcon} from './Icon';
import {avatarColor, blend, fade, inkOn, initialsOf, pressDepth, shadowFor, typedCount, uiPalette, uiTypeSchedule, type UiMode} from './shared';

export type ChatMessage = {
	from: 'me' | 'them';
	text: string;
	at?: number; // the frame it lands (default: a reading beat after the previous one)
	name?: string; // the sender (group chats): shown above their first bubble in a run, with an avatar
	typing?: number | false; // frames of typing dots before a 'them' message (default 26 at 30 fps)
	react?: {at: number; icon?: 'heartFilled' | 'thumbUp'}; // a reaction pops onto the bubble
};

export type ChatSlot = {land: number; dots?: number; compose?: number};

/** When every message lands (and when its typing dots or composer typing start). */
export const chatTimeline = (messages: readonly ChatMessage[], fps: number, startAt = 0, composer = false, cps = 20): ChatSlot[] => {
	const slots: ChatSlot[] = [];
	let t = startAt;
	messages.forEach((m, i) => {
		const typing = m.from === 'them' && m.typing !== false ? (m.typing ?? at30(26, fps)) : 0;
		const compose = m.from === 'me' && composer ? uiTypeSchedule(m.text, fps, {cps, seed: `chat-${i}`}).total + at30(8, fps) : 0;
		const land = m.at ?? (i === 0 ? t + typing + compose : t + typing + compose);
		slots.push({land, dots: typing ? land - typing : undefined, compose: compose ? land - compose : undefined});
		t = land + at30(10, fps) + Math.round(readingFrames(m.text, fps) * 0.5);
	});
	return slots;
};

export type ChatThreadProps = {
	messages: ChatMessage[];
	startAt?: number;
	width?: number; // px at 1080 (default 720)
	height?: number; // default 900
	header?: {name: string; status?: string} | false;
	composer?: boolean; // an input bar; 'me' messages are typed into it and sent
	cps?: number; // composer typing speed (default 20)
	receipt?: string; // small text under the last 'me' message, e.g. 'Read 10:24'
	fontSize?: number; // default 30
	meColor?: string; // default: the theme accent
	themColor?: string;
	panel?: boolean; // draw the panel background and shadow (default true)
	radius?: number;
	mode?: UiMode;
	style?: React.CSSProperties;
};

/** Three dots that rise and fall in turn inside a bubble. */
export const TypingDots: React.FC<{color?: string; bg?: string; size?: number}> = ({color, bg, size = 30}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t);
	const period = fps * 0.9;
	const c = color ?? P.muted;
	return (
		<div style={{display: 'inline-flex', alignItems: 'center', gap: size * 0.22 * unit, padding: `${size * 0.52 * unit}px ${size * 0.62 * unit}px`, borderRadius: size * 0.8 * unit, background: bg ?? blend(P.page, P.text, 0.07)}}>
			{[0, 1, 2].map((i) => {
				const ph = (((frame / period - i * 0.16) % 1) + 1) % 1;
				const lift = Math.max(0, Math.sin(ph * 2 * Math.PI));
				return <div key={i} style={{width: size * 0.3 * unit, height: size * 0.3 * unit, borderRadius: '50%', background: c, opacity: 0.45 + 0.55 * lift, translate: `0px ${-size * 0.14 * lift * unit}px`}} />;
			})}
		</div>
	);
};

/** A two-sided chat that plays itself: dots, bubbles, reactions, a read receipt and an optional composer. */
export const ChatThread: React.FC<ChatThreadProps> = ({
	messages,
	startAt = 0,
	width = 720,
	height = 900,
	header = {name: 'Maya Chen', status: 'online'},
	composer = false,
	cps = 20,
	receipt,
	fontSize = 30,
	meColor,
	themColor,
	panel = true,
	radius,
	mode = 'auto',
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const u = (v: number) => v * unit;
	const slots = chatTimeline(messages, fps, startAt, composer, cps);
	const me = meColor ?? P.accent;
	const meInk = meColor ? inkOn(meColor) : P.onAccent;
	const them = themColor ?? (P.dark ? blend(P.panel, '#FFFFFF', 0.07) : blend(P.page, P.text, 0.075));
	const headerH = header ? 96 : 0;
	const composerH = composer ? 100 : 0;
	const R = fontSize * 0.8;
	const group = messages.some((m) => m.from === 'them' && m.name);
	const dotsNow = messages.some((m, i) => {
		const s = slots[i];
		return s.dots !== undefined && frame >= s.dots && frame < s.land;
	});
	// composer state: which 'me' message is being typed now
	let draft = '';
	let draftCaret = 0;
	let sendPress = 0;
	if (composer) {
		messages.forEach((m, i) => {
			const s = slots[i];
			if (m.from !== 'me' || s.compose === undefined) {
				return;
			}
			if (frame >= s.compose && frame < s.land) {
				const plan = uiTypeSchedule(m.text, fps, {cps, seed: `chat-${i}`});
				const c = typedCount(frame - s.compose, plan.times);
				draft = plan.chars.slice(0, c).join('');
				draftCaret = 1;
			}
			sendPress = Math.max(sendPress, Math.max(0, pressDepth(frame, s.land - 1, fps)));
		});
	}
	const lastMe = messages.map((m) => m.from).lastIndexOf('me');
	const receiptAt = lastMe >= 0 ? slots[lastMe].land + at30(24, fps) : Infinity;
	const receiptIn = receipt ? ramp(frame, receiptAt, at30(8, fps), curves.out) : 0;
	const rows: React.ReactNode[] = [];
	messages.forEach((m, i) => {
		const s = slots[i];
		const prev = messages[i - 1];
		const next = messages[i + 1];
		const firstOfRun = !prev || prev.from !== m.from || prev.name !== m.name;
		const lastOfRun = !next || next.from !== m.from || next.name !== m.name;
		const mine = m.from === 'me';
		// typing dots before a 'them' message
		if (s.dots !== undefined && frame >= s.dots) {
			const grow = ramp(frame, s.dots, at30(8, fps), curves.out) * (1 - ramp(frame, s.land - at30(2, fps), at30(5, fps), curves.inOut));
			if (grow > 0.001) {
				rows.push(
					<div key={`dots-${i}`} style={{display: 'grid', gridTemplateRows: `minmax(0, ${grow}fr)`}}>
						<div style={{minHeight: 0, overflow: 'hidden'}}>
							<div style={{paddingTop: u(firstOfRun ? 18 : 6), paddingLeft: group ? u(48) : 0, opacity: grow}}>
								<TypingDots bg={them} size={fontSize} />
							</div>
						</div>
					</div>,
				);
			}
		}
		if (frame < s.land) {
			return;
		}
		const grow = ramp(frame, s.land, at30(8, fps), curves.out);
		const pop = springAt(frame, fps, {delay: s.land, config: 'settle'});
		const o = ramp(frame, s.land, at30(4, fps), curves.out);
		const rSide = lastOfRun ? u(6) : u(8);
		const radii = mine ? `${u(R)}px ${u(firstOfRun ? R : 8)}px ${rSide}px ${u(R)}px` : `${u(firstOfRun ? R : 8)}px ${u(R)}px ${u(R)}px ${rSide}px`;
		const reactIn = m.react ? springAt(frame, fps, {delay: m.react.at, config: 'pop'}) : 0;
		rows.push(
			<div key={`msg-${i}`} style={{display: 'grid', gridTemplateRows: `minmax(0, ${grow}fr)`}}>
				<div style={{minHeight: 0, overflow: grow < 0.999 ? 'hidden' : 'visible'}}>
					<div style={{paddingTop: u(firstOfRun ? 18 : 6), display: 'flex', flexDirection: 'column', alignItems: mine ? 'flex-end' : 'flex-start'}}>
						{!mine && group && firstOfRun && m.name ? (
							<div style={{fontSize: u(fontSize * 0.62), fontWeight: t.weights.strong, color: P.muted, margin: `0 0 ${u(6)}px ${u(48 + 14)}px`}}>{m.name}</div>
						) : null}
						<div style={{display: 'flex', alignItems: 'flex-end', gap: u(12), maxWidth: '82%', flexDirection: mine ? 'row-reverse' : 'row'}}>
							{!mine && group ? (
								<div style={{width: u(36), height: u(36), flex: '0 0 auto', borderRadius: '50%', background: m.name ? avatarColor(m.name, t) : P.faint, color: '#FFFFFF', fontSize: u(15), fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: lastOfRun ? 1 : 0}}>
									{m.name ? initialsOf(m.name) : ''}
								</div>
							) : null}
							<div
								style={{
									position: 'relative',
									padding: `${u(fontSize * 0.42)}px ${u(fontSize * 0.66)}px`,
									borderRadius: radii,
									background: mine ? me : them,
									color: mine ? meInk : P.text,
									fontSize: u(fontSize),
									lineHeight: 1.34,
									fontWeight: t.weights.body,
									opacity: o,
									scale: `${0.72 + 0.28 * pop}`,
									translate: `${mine ? 0 : (1 - o) * -10 * unit}px ${(1 - o) * 12 * unit}px`,
									transformOrigin: mine ? '100% 100%' : '0% 100%',
									textRendering: 'geometricPrecision',
									overflowWrap: 'break-word',
								}}
							>
								{m.text}
								{m.react && reactIn > 0.001 ? (
									<div
										style={{
											position: 'absolute',
											top: u(-22),
											[mine ? 'left' : 'right']: u(-26),
											width: u(36),
											height: u(36),
											borderRadius: '50%',
											background: P.raised,
											boxShadow: `0 ${u(3)}px ${u(8)}px ${fade('#000000', 0.18)}, 0 0 0 ${u(3)}px ${P.page}`,
											display: 'flex',
											alignItems: 'center',
											justifyContent: 'center',
											scale: `${Math.max(0, reactIn)}`,
										}}
									>
										<UiIcon name={m.react.icon ?? 'heartFilled'} size={20} color={(m.react.icon ?? 'heartFilled') === 'heartFilled' ? '#F0445C' : P.accent} stroke={1.6} />
									</div>
								) : null}
							</div>
						</div>
						{receipt && i === lastMe && receiptIn > 0.001 ? (
							<div style={{fontSize: u(fontSize * 0.55), color: P.muted, marginTop: u(6), opacity: receiptIn, fontWeight: t.weights.body}}>{receipt}</div>
						) : null}
					</div>
				</div>
			</div>,
		);
	});
	const avatarBg = header ? avatarColor(header.name, t) : P.faint;
	return (
		<div
			style={{
				position: 'relative',
				width: u(width),
				height: u(height),
				display: 'flex',
				flexDirection: 'column',
				borderRadius: panel ? u(radius ?? Math.min(t.radius + 8, 32)) : 0,
				overflow: 'hidden',
				background: panel ? P.page : 'transparent',
				boxShadow: panel ? shadowFor(P.dark, unit, 2) : undefined,
				fontFamily: t.type.body,
				...style,
			}}
		>
			{header ? (
				<div style={{height: u(headerH), flex: '0 0 auto', display: 'flex', alignItems: 'center', gap: u(16), padding: `0 ${u(22)}px`, borderBottom: `${unit}px solid ${P.line}`, background: P.bar}}>
					<UiIcon name="chevronLeft" size={30} color={P.accent} stroke={2.4} />
					<div style={{width: u(52), height: u(52), borderRadius: '50%', background: avatarBg, color: '#FFFFFF', fontSize: u(20), fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{initialsOf(header.name)}</div>
					<div style={{display: 'flex', flexDirection: 'column', gap: u(2)}}>
						<div style={{fontSize: u(24), fontWeight: t.weights.strong, color: P.text}}>{header.name}</div>
						<div style={{fontSize: u(18), color: dotsNow ? P.accent : P.muted}}>{dotsNow ? 'typing...' : (header.status ?? 'online')}</div>
					</div>
				</div>
			) : null}
			<div
				style={{
					flex: 1,
					minHeight: 0,
					display: 'flex',
					flexDirection: 'column',
					justifyContent: 'flex-end',
					padding: `0 ${u(26)}px ${u(22)}px`,
					overflow: 'hidden',
					WebkitMaskImage: `linear-gradient(to bottom, transparent 0, #000 ${u(60)}px)`,
					maskImage: `linear-gradient(to bottom, transparent 0, #000 ${u(60)}px)`,
				}}
			>
				{rows}
			</div>
			{composer ? (
				<div style={{height: u(composerH), flex: '0 0 auto', display: 'flex', alignItems: 'center', gap: u(14), padding: `0 ${u(20)}px`, borderTop: `${unit}px solid ${P.line}`, background: P.bar}}>
					<UiIcon name="plus" size={30} color={P.muted} />
					<div style={{flex: 1, height: u(58), borderRadius: u(29), border: `${u(1.5)}px solid ${P.line}`, background: P.page, display: 'flex', alignItems: 'center', padding: `0 ${u(22)}px`, fontSize: u(fontSize * 0.86), color: P.text, whiteSpace: 'pre', overflow: 'hidden'}}>
						{draft ? <span>{draft}</span> : <span style={{color: P.muted}}>Message</span>}
						{draftCaret ? <span style={{display: 'inline-block', width: u(2.5), height: u(fontSize), background: P.accent, marginLeft: u(2)}} /> : null}
					</div>
					<div style={{width: u(54), height: u(54), borderRadius: '50%', background: draft ? me : fade(me, 0.35), display: 'flex', alignItems: 'center', justifyContent: 'center', scale: `${1 - 0.1 * sendPress}`}}>
						<UiIcon name="arrowUp" size={28} color={meInk} stroke={2.6} />
					</div>
				</div>
			) : null}
		</div>
	);
};
