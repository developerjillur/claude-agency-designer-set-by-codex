// <Audiogram>: a podcast or voice clip as a video: cover in an audio-reactive ring, title, a captions slot, a
// scrolling level strip and progress. Portrait (9:16), square and landscape layouts, all inside the safe area.
import {Audio} from '@remotion/media';
import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame} from 'remotion';
import {at30, useStage, useTheme} from '../core';
import {Animate} from '../motion';
import {AudioCircle, AudioWave, useAudioLevel} from './Visualizers';

export type AudiogramProps = {
	/** The audio: played (unless playAudio is false) and analysed. */
	src: string;
	/** Frame the audio starts on this timeline, and where in the file it starts. */
	from?: number;
	trimBefore?: number;
	/** Frames of audio for the progress bar (default: to the end of the Sequence). */
	length?: number;
	title: string;
	/** Show or channel name, set small above the title. */
	show?: string;
	/** A short tag on the right of the show line: 'EP 12', '03:14'. */
	episode?: string;
	/** An image src or any node (a designed cover). Shown in a circle inside the level ring. */
	cover?: string | React.ReactNode;
	/** The captions slot: a caption component, or plain text (styled here). */
	captions?: React.ReactNode;
	playAudio?: boolean;
	volume?: number;
	accent?: string;
	style?: React.CSSProperties;
};

const clock = (s: number) => {
	const t = Math.max(0, Math.floor(s));
	return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`;
};

export const Audiogram: React.FC<AudiogramProps> = ({
	src,
	from = 0,
	trimBefore = 0,
	length,
	title,
	show,
	episode,
	cover,
	captions,
	playAudio = true,
	volume = 1,
	accent,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, unit, safe, fps, durationInFrames} = useStage();
	const c = accent ?? t.colors.accent;
	const landscape = width / height > 1.2;
	const portrait = height / width > 1.2;
	const total = length ?? (Number.isFinite(durationInFrames) ? durationInFrames - from : fps * 60);
	const elapsed = Math.min(total, Math.max(0, frame - from));
	const bass = useAudioLevel({src, from, trimBefore});
	const circle = landscape ? 420 : portrait ? 340 : 300;
	const ring = landscape ? 78 : 56;
	const step = at30(4, fps);

	const coverNode =
		typeof cover === 'string' ? (
			<Img src={cover} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
		) : (
			cover ?? <div style={{width: '100%', height: '100%', background: `linear-gradient(135deg, ${c}, ${t.colors.accent2})`}} />
		);

	const label = show || episode ? (
		<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 24 * unit, fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 26 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase'}}>
			<span style={{color: c}}>{show}</span>
			<span style={{color: t.colors.muted, fontVariantNumeric: 'tabular-nums'}}>{episode}</span>
		</div>
	) : null;

	const titleNode = (
		<div
			style={{
				fontFamily: t.type.display,
				fontWeight: t.weights.display,
				fontSize: (landscape ? 66 : 60) * unit,
				lineHeight: 1.08,
				letterSpacing: `${t.tracking.display}em`,
				textTransform: t.caps ? 'uppercase' : 'none',
				color: t.colors.text,
				textWrap: 'balance',
				display: '-webkit-box',
				WebkitLineClamp: landscape ? 3 : 2,
				WebkitBoxOrient: 'vertical',
				overflow: 'hidden',
				paddingBottom: '0.06em',
			}}
		>
			{title}
		</div>
	);

	const captionBox = (
		<div
			style={{
				minHeight: (landscape ? 128 : 118) * unit,
				fontFamily: t.type.body,
				fontWeight: t.weights.strong,
				fontSize: 46 * unit,
				lineHeight: 1.25,
				color: t.colors.text,
				display: 'flex',
				alignItems: 'flex-start',
			}}
		>
			{captions}
		</div>
	);

	const waveWidth = (landscape ? safe.w - (circle + 2 * (ring + 17)) * unit - 80 * unit : safe.w) / unit;
	const progress = (
		<div style={{display: 'flex', flexDirection: 'column', gap: 14 * unit}}>
			<AudioWave src={src} from={from} trimBefore={trimBefore} variant="scroll" width={waveWidth} height={landscape ? 96 : 80} seconds={6} points={56} color={c} />
			<div style={{display: 'flex', alignItems: 'center', gap: 18 * unit, fontFamily: t.type.mono, fontSize: 24 * unit, color: t.colors.muted, fontVariantNumeric: 'tabular-nums'}}>
				<span>{clock(elapsed / fps)}</span>
				<div style={{flex: 1, height: 6 * unit, borderRadius: 3 * unit, background: t.colors.line, overflow: 'hidden'}}>
					<div style={{width: `${(elapsed / Math.max(1, total)) * 100}%`, height: '100%', background: c}} />
				</div>
				<span>{clock(total / fps)}</span>
			</div>
		</div>
	);

	const ringNode = (
		<AudioCircle src={src} from={from} trimBefore={trimBefore} size={circle} length={ring} barWidth={landscape ? 8 : 7} bars={32} color={c} spin={4} pulse={0.03}>
			{coverNode}
		</AudioCircle>
	);

	return (
		<AbsoluteFill style={{background: t.colors.bg, overflow: 'hidden', ...style}}>
			{/* a soft light behind the ring that breathes with the bass */}
			<AbsoluteFill
				style={{
					background: `radial-gradient(circle at ${landscape ? '30% 50%' : '50% 45%'}, ${c} 0%, transparent ${landscape ? 45 : 55}%)`,
					opacity: 0.12 + 0.1 * bass,
				}}
			/>
			{playAudio ? <Audio src={src} from={from} trimBefore={trimBefore || undefined} volume={volume} name="Audiogram audio" /> : null}
			{landscape ? (
				<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, display: 'flex', alignItems: 'center', gap: 80 * unit}}>
					<Animate in="pop" delay={0}>
						{ringNode}
					</Animate>
					<div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 26 * unit, minWidth: 0}}>
						<Animate delay={step}>{label}</Animate>
						<Animate delay={step * 2}>{titleNode}</Animate>
						<Animate delay={step * 3}>{captionBox}</Animate>
						<Animate delay={step * 4}>{progress}</Animate>
					</div>
				</div>
			) : (
				<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
					<div style={{display: 'flex', flexDirection: 'column', gap: 14 * unit}}>
						<Animate delay={0}>{label}</Animate>
						<Animate delay={step}>{titleNode}</Animate>
					</div>
					<Animate in="pop" delay={step * 2} style={{alignSelf: 'center'}}>
						{ringNode}
					</Animate>
					<Animate delay={step * 3}>{captionBox}</Animate>
					<Animate delay={step * 4}>{progress}</Animate>
				</div>
			)}
		</AbsoluteFill>
	);
};
