// Full-frame cards: a title card with words rising through masks, a chapter card, and an end card with a call to
// action, a handle, a logo slot and optional end-screen slots. They sit inside the safe area, push in slowly while
// they hold (a still card reads as frozen) and can leave on the Sequence's last frame.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp, springAt} from '../motion';
import {UiButton} from './Controls';
import {Cursor, type CursorKey} from './Cursor';
import {UiIcon} from './Icon';
import {UiBackdrop} from './Frames';
import {fade, inkOn, useUiLife} from './shared';

const BANGLA = /[ঀ-৿]/;

type HeadlineProps = {
	text: string; // '\n' for explicit line breaks
	start: number; // local frame the first word starts rising
	each: number; // frames between words
	dur: number; // rise frames per word
	exitStart: number;
	outDur: number;
	align: 'left' | 'center';
	accentWord?: string;
	accent: string;
	style: React.CSSProperties;
};

/** Words rising through masks, line by line; one word may take the accent colour. Returns the landing frame too. */
const Headline: React.FC<HeadlineProps> = ({text, start, each, dur, exitStart, outDur, align, accentWord, accent, style}) => {
	const frame = useCurrentFrame();
	const bangla = BANGLA.test(text);
	const lines = text.split('\n').map((l) => l.split(/\s+/).filter(Boolean));
	let index = 0;
	const total = lines.reduce((n, l) => n + l.length, 0);
	const padT = bangla ? 0.2 : 0.1;
	const padB = bangla ? 0.3 : 0.2;
	// the exit runs last word first and every word is gone by exitStart + outDur (the Sequence's last frame)
	const stepOut = total > 1 ? Math.max(0, Math.min(Math.max(1, Math.round(each / 2)), Math.floor((outDur - 4) / (total - 1)))) : 0;
	const wordOut = Math.max(3, outDur - (total - 1) * stepOut);
	return (
		<div style={{...style, textAlign: align, lineHeight: bangla ? 1.34 : style.lineHeight}}>
			{lines.map((words, li) => (
				<div key={li} style={{display: 'block', whiteSpace: 'nowrap'}}>
					{words.map((w, wi) => {
						const i = index++;
						const p = ramp(frame, start + i * each, dur, curves.out);
						const q = Number.isFinite(exitStart) ? ramp(frame, exitStart + (total - 1 - i) * stepOut, wordOut, curves.in) : 0;
						const isAccent = accentWord !== undefined && w.replace(/[.,!?:;]/g, '') === accentWord;
						return (
							<span key={wi} style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'top', padding: `${padT}em 0.02em ${padB}em`, margin: `-${padT}em ${wi === words.length - 1 ? 0 : 0.24}em -${padB}em 0`}}>
								<span style={{display: 'inline-block', translate: `0px ${(1 - p) * 112 - q * 112}%`, color: isAccent ? accent : undefined}}>{w}</span>
							</span>
						);
					})}
				</div>
			))}
		</div>
	);
};

const wordCount = (s: string) => s.split(/\s+/).filter(Boolean).length;

const usePush = (amount: number) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useStage();
	return Number.isFinite(durationInFrames) && amount ? 1 + amount * ramp(frame, 0, durationInFrames, curves.sine) : 1;
};

// ------------------------------------------------------------------ TitleCard

export type TitleCardProps = {
	title: string; // '\n' breaks lines where you want them (balance two-line titles by hand)
	kicker?: string; // a small label above
	subtitle?: string;
	align?: 'left' | 'center'; // default: left in landscape, centre in portrait
	size?: number; // title px at 1080 (default 124 landscape, 92 portrait)
	accentWord?: string; // one word in the accent colour
	rule?: boolean; // a short accent rule under the title
	delay?: number;
	exit?: number | false; // default false: cut on a settled frame
	exitAt?: number;
	background?: 'theme' | 'none' | string;
	push?: number; // slow push-in over the Sequence (default 0.03)
	style?: React.CSSProperties;
};

/** A title card: kicker, a headline that rises word by word, an optional subtitle and rule. */
export const TitleCard: React.FC<TitleCardProps> = ({
	title,
	kicker,
	subtitle,
	align,
	size,
	accentWord,
	rule = false,
	delay = 0,
	exit = false,
	exitAt,
	background = 'theme',
	push = 0.03,
	style,
}) => {
	const t = useTheme();
	const {fps, unit, safe, vertical} = useStage();
	const life = useUiLife({delay, exit: exit === false ? false : exit ?? at30(14, fps), exitAt});
	const al = align ?? (vertical ? 'center' : 'left');
	const fs = (size ?? (vertical ? 92 : 124)) * unit;
	const each = at30(3, fps);
	const rise = at30(17, fps);
	const tStart = delay + (kicker ? at30(5, fps) : 0);
	const landed = tStart + (wordCount(title) - 1) * each + rise;
	const scale = usePush(push);
	const kIn = life.enter(0, at30(14, fps), curves.inOut);
	const subIn = life.enter(landed - delay - at30(6, fps), at30(16, fps));
	const ruleIn = life.enter(landed - delay - at30(8, fps), at30(14, fps), curves.inOut);
	const q = life.leave();
	return (
		<AbsoluteFill style={style}>
			{background === 'theme' ? <UiBackdrop variant="glow" /> : background !== 'none' ? <AbsoluteFill style={{background}} /> : null}
			<AbsoluteFill style={{scale: `${scale}`, transformOrigin: al === 'center' ? '50% 50%' : `${safe.x}px 50%`}}>
				<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: al === 'center' ? 'center' : 'flex-start'}}>
					{kicker ? (
						<div
							style={{
								fontFamily: t.type.body,
								fontWeight: t.weights.strong,
								fontSize: 26 * unit,
								letterSpacing: `${Math.max(0.1, t.tracking.caps)}em`,
								textTransform: 'uppercase',
								color: t.colors.accent,
								marginBottom: 26 * unit,
								clipPath: `inset(0 ${(1 - kIn) * 100}% 0 0)`,
								opacity: 1 - q,
								whiteSpace: 'nowrap',
							}}
						>
							{kicker}
						</div>
					) : null}
					<Headline
						text={t.caps ? title.toUpperCase() : title}
						start={tStart}
						each={each}
						dur={rise}
						exitStart={life.exitStart}
						outDur={life.outFrames}
						align={al}
						accentWord={accentWord === undefined ? undefined : t.caps ? accentWord.toUpperCase() : accentWord}
						accent={t.colors.accent}
						style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: fs, lineHeight: 1.04, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textRendering: 'geometricPrecision', maxWidth: safe.w}}
					/>
					{rule ? <div style={{width: 120 * unit, height: 6 * unit, borderRadius: 3 * unit, background: t.colors.accent, marginTop: 34 * unit, scale: `${ruleIn * (1 - q)} 1`, transformOrigin: al === 'center' ? '50% 50%' : '0% 50%'}} /> : null}
					{subtitle ? (
						<div
							style={{
								fontFamily: t.type.body,
								fontWeight: t.weights.body,
								fontSize: (vertical ? 36 : 40) * unit,
								lineHeight: BANGLA.test(subtitle) ? 1.4 : 1.3,
								color: t.colors.muted,
								marginTop: (rule ? 26 : 34) * unit,
								maxWidth: Math.min(safe.w, 1200 * unit),
								textAlign: al,
								textWrap: 'balance',
								opacity: subIn * (1 - q),
								translate: `0px ${(1 - subIn) * 18 * unit - q * 10 * unit}px`,
							}}
						>
							{subtitle}
						</div>
					) : null}
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ SectionTitle

export type SectionTitleProps = {
	title: string;
	index?: number; // the chapter number
	total?: number; // chapters in all (shows "2 / 5")
	label?: string; // default 'Chapter'
	variant?: 'full' | 'inline'; // full: its own ground and a big faint numeral; inline: over content
	align?: 'left' | 'center';
	size?: number; // title px at 1080 (default 96)
	delay?: number;
	exit?: number | false; // default: leaves on the Sequence's last frame
	exitAt?: number;
	push?: number;
	style?: React.CSSProperties;
};

/** A chapter card: a rule draws across, the chapter label slides out of it and the title rises above it. */
export const SectionTitle: React.FC<SectionTitleProps> = ({title, index, total, label = 'Chapter', variant = 'full', align = 'left', size, delay = 0, exit, exitAt, push = 0.025, style}) => {
	const t = useTheme();
	const {fps, unit, safe, vertical} = useStage();
	const life = useUiLife({delay, exit: exit === false ? false : exit ?? at30(14, fps), exitAt});
	const fs = (size ?? (vertical ? 80 : 96)) * unit;
	const scale = usePush(variant === 'full' ? push : 0);
	const line = life.enter(0, at30(18, fps), curves.inOut);
	const lab = life.enter(at30(8, fps), at30(14, fps), curves.out);
	const num = life.enter(at30(4, fps), at30(30, fps), curves.out);
	const q = life.leave();
	const lineOut = life.leave(Math.round(life.outFrames * 0.3), Math.max(1, life.outFrames - Math.round(life.outFrames * 0.3)), curves.inOut);
	const labelText = `${label}${index !== undefined ? ` ${String(index).padStart(2, '0')}` : ''}${total !== undefined ? ` / ${String(total).padStart(2, '0')}` : ''}`;
	const center = align === 'center';
	return (
		<AbsoluteFill style={style}>
			{variant === 'full' ? <UiBackdrop variant="glow" color={t.colors.bg2} /> : null}
			<AbsoluteFill style={{scale: `${scale}`, transformOrigin: center ? '50% 50%' : `${safe.x + safe.w}px 50%`}}>
				{variant === 'full' && index !== undefined ? (
					<div
						style={{
							position: 'absolute',
							right: center ? undefined : safe.x,
							left: center ? 0 : undefined,
							width: center ? '100%' : undefined,
							textAlign: center ? 'center' : 'right',
							top: safe.y + safe.h * (vertical ? 0.02 : 0.02),
							fontFamily: t.type.display,
							fontWeight: t.weights.display,
							fontSize: (vertical ? 300 : 460) * unit,
							lineHeight: 1,
							color: fade(t.colors.text, t.dark ? 0.07 : 0.06),
							fontVariantNumeric: 'tabular-nums',
							letterSpacing: `${t.tracking.display}em`,
							opacity: num * (1 - q),
							translate: `${(1 - num) * 60 * unit}px 0px`,
						}}
					>
						{String(index).padStart(2, '0')}
					</div>
				) : null}
				<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: center ? 'center' : 'flex-start'}}>
					<Headline
						text={t.caps ? title.toUpperCase() : title}
						start={delay + at30(10, fps)}
						each={at30(3, fps)}
						dur={at30(16, fps)}
						exitStart={life.exitStart}
						outDur={life.outFrames}
						align={align}
						accent={t.colors.accent}
						style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: fs, lineHeight: 1.05, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textRendering: 'geometricPrecision'}}
					/>
					<div style={{width: center ? Math.min(safe.w, 900 * unit) : safe.w * 0.62, height: 3 * unit, background: t.colors.accent, margin: `${28 * unit}px 0 ${22 * unit}px`, scale: `${line * (1 - lineOut)} 1`, transformOrigin: center ? '50% 50%' : '0% 50%'}} />
					<div style={{overflow: 'hidden'}}>
						<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 26 * unit, letterSpacing: `${Math.max(0.12, t.tracking.caps)}em`, textTransform: 'uppercase', color: t.colors.muted, translate: `0px ${(1 - lab) * -110 + q * -110}%`, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap'}}>{labelText}</div>
					</div>
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ EndCard

export type EndCardProps = {
	title?: string; // the call to action headline ('\n' to break)
	subtitle?: string;
	cta?: string; // the button
	doneCta?: string; // the button after the click (default: unchanged)
	url?: string;
	handle?: string;
	name?: string; // the brand name next to the logo slot
	logo?: React.ReactNode; // the logo slot (default: a tile with the name's first letter)
	slots?: 0 | 1 | 2; // placeholders for end-screen videos on the right (landscape)
	slotLabels?: string[];
	clickAt?: number; // a pointer clicks the button at this frame (default: no pointer)
	delay?: number;
	push?: number; // slow push-in (default 0.03)
	background?: 'theme' | 'none' | string;
	style?: React.CSSProperties;
};

/** The last card: logo slot, a call to action with a button, the handle and address, optional video slots. */
export const EndCard: React.FC<EndCardProps> = ({
	title = 'Start writing\nwith Driftnote',
	subtitle = 'Free for your first three projects.',
	cta = 'Try it free',
	doneCta,
	url = 'driftnote.example',
	handle = '@driftnote',
	name = 'Driftnote',
	logo,
	slots = 0,
	slotLabels = ['Watch next', 'Our best tips'],
	clickAt,
	delay = 0,
	push = 0.03,
	background = 'theme',
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, safe, vertical} = useStage();
	const scale = usePush(push);
	const u = (v: number) => v * unit;
	const f = (n: number) => at30(n, fps);
	const rise = (offset: number) => {
		const p = ramp(frame, delay + offset, f(18), curves.out);
		return {opacity: p, translate: `0px ${(1 - p) * 24 * unit}px`} as React.CSSProperties;
	};
	const showSlots = !vertical && slots > 0;
	const colW = showSlots ? safe.w * 0.5 : safe.w;
	const titleSize = vertical ? 104 : showSlots ? 92 : 108;
	const titleWords = wordCount(title);
	const afterTitle = f(8) + (titleWords - 1) * f(3) + f(17);
	const btnPop = springAt(frame, fps, {delay: delay + afterTitle, config: 'settle'});
	// the button sits in normal flow, so its target comes from the layout: measure-free constants
	const btnW = 300;
	const btnH = 72;
	const logoNode = logo ?? (
		<div style={{width: u(64), height: u(64), borderRadius: u(Math.min(t.radius, 20)), background: t.colors.accent, color: inkOn(t.colors.accent), display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(34)}}>
			{name.slice(0, 1)}
		</div>
	);
	return (
		<AbsoluteFill style={style}>
			{background === 'theme' ? <UiBackdrop variant="glow" /> : background !== 'none' ? <AbsoluteFill style={{background}} /> : null}
			<AbsoluteFill style={{scale: `${scale}`, transformOrigin: vertical ? '50% 50%' : `${safe.x}px 50%`}}>
				<div
					style={{
						position: 'absolute',
						left: safe.x + (vertical ? 0 : 6 * unit),
						top: safe.y,
						width: colW - (vertical ? 0 : 6 * unit),
						height: safe.h,
						display: 'flex',
						flexDirection: 'column',
						justifyContent: 'center',
						alignItems: vertical ? 'center' : 'flex-start',
						textAlign: vertical ? 'center' : 'left',
					}}
				>
					<div style={{display: 'flex', alignItems: 'center', gap: u(18), marginBottom: u(40), ...rise(0)}}>
						{logoNode}
						<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(40), letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>{t.caps ? name.toUpperCase() : name}</div>
					</div>
					<Headline
						text={t.caps ? title.toUpperCase() : title}
						start={delay + f(8)}
						each={f(3)}
						dur={f(17)}
						exitStart={Infinity}
						outDur={1}
						align={vertical ? 'center' : 'left'}
						accent={t.colors.accent}
						style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(titleSize), lineHeight: 1.04, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textRendering: 'geometricPrecision'}}
					/>
					{subtitle ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: u(vertical ? 40 : 34), color: t.colors.muted, marginTop: u(26), ...rise(afterTitle - f(8))}}>{subtitle}</div> : null}
					<div style={{position: 'relative', marginTop: u(44), scale: `${Math.max(0, btnPop)}`, opacity: Math.min(1, btnPop * 2), transformOrigin: vertical ? '50% 50%' : '0% 50%'}}>
						<UiButton label={cta} size="lg" width={btnW} iconRight="arrowRight" pressAt={clickAt} doneLabel={doneCta} doneIcon="check" />
						{clickAt !== undefined ? (
							<Cursor
								keys={
									[
										{x: btnW + 220, y: btnH + 150, at: clickAt - f(30)},
										// on the arrow, never over the label; then the hand moves off and fades (it used to vanish in place)
										{x: btnW - btnH * 0.5, y: btnH * 0.58, at: clickAt - f(4), click: clickAt},
										{x: btnW + 150, y: btnH + 110, at: clickAt + f(22)},
									] satisfies CursorKey[]
								}
								hideAfter={f(2)}
							/>
						) : null}
					</div>
					<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: vertical ? 'center' : 'flex-start', gap: `${u(14)}px ${u(34)}px`, marginTop: u(40), fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: u(vertical ? 34 : 32), color: t.colors.text, ...rise(afterTitle + f(6))}}>
						{url ? (
							<span style={{display: 'inline-flex', alignItems: 'center', gap: u(10)}}>
								<UiIcon name="globe" size={26} color={t.colors.accent} />
								{url}
							</span>
						) : null}
						{handle ? (
							<span style={{display: 'inline-flex', alignItems: 'center', gap: u(10)}}>
								<UiIcon name="user" size={26} color={t.colors.accent} />
								{handle}
							</span>
						) : null}
					</div>
				</div>
				{showSlots ? (
					<div style={{position: 'absolute', left: safe.x + safe.w * 0.64, top: safe.y, width: safe.w * 0.36, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: u(40)}}>
						{Array.from({length: slots}).map((_, i) => {
							const p = ramp(frame, delay + f(10 + i * 6), f(20), curves.out);
							return (
								<div key={i} style={{opacity: p, translate: `${(1 - p) * 40 * unit}px 0px`}}>
									<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: u(22), color: t.colors.muted, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', marginBottom: u(12)}}>{slotLabels[i] ?? ''}</div>
									<div style={{width: '100%', aspectRatio: '16 / 9', borderRadius: u(Math.min(t.radius, 18)), border: `${u(2)}px solid ${fade(t.colors.text, 0.16)}`, background: fade(t.colors.text, t.dark ? 0.05 : 0.035), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
										<div style={{width: u(76), height: u(76), borderRadius: '50%', background: fade(t.colors.text, 0.1), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
											<UiIcon name="play" size={34} color={fade(t.colors.text, 0.5)} />
										</div>
									</div>
								</div>
							);
						})}
					</div>
				) : null}
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
