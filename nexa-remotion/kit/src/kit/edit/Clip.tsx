// <Clip>: one piece of footage placed, trimmed, framed and mixed. The @remotion/media <Video> by default (frame
// exact, fastest); the OffthreadVideo engine for pitch-preserving speed changes and sources the media engine cannot
// decode in the browser (it also takes over automatically in server renders when decoding fails).
import {Video, type VideoObjectFit} from '@remotion/media';
import React, {useCallback, useMemo} from 'react';
import {AbsoluteFill, Freeze, Loop, OffthreadVideo, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {curves, useStage} from '../core';
import {ramp} from '../motion';
import {fadeGain, safeGain} from './gain';

/** How the picture fills its box: the media engine's values plus 'blur' (fitted over a blurred cover copy). */
export type ClipFit = VideoObjectFit | 'blur';

export type ClipProps = {
	src: string;
	/** Frame on the parent timeline where the clip starts. */
	from?: number;
	/** Cut the clip off after this many frames. */
	durationInFrames?: number;
	/** First source frame to use, counted in frames at the composition's fps. */
	trimBefore?: number;
	/** Source frame to stop at (a position in the file, not a length). With it the clip ends on its own. */
	trimAfter?: number;
	/** Constant speed. On the media engine the pitch moves with it; the offthread engine keeps the pitch. */
	playbackRate?: number;
	/** 'cover' (default) fills the box, 'contain' letterboxes, 'blur' letterboxes over a blurred copy. */
	objectFit?: ClipFit;
	/** Gain (1 = as recorded) or a curve `(f) => gain` where f counts frames since the clip started. */
	volume?: number | ((f: number) => number);
	/** Sound fades in frames at the start and the end of the clip (6 or more; steps are per frame). */
	fadeIn?: number;
	fadeOut?: number;
	/** Fade the picture too (a dip from the ground) with the same frames. */
	fadePicture?: boolean;
	muted?: boolean;
	/** Repeat the trimmed range until the clip is cut off. */
	loop?: boolean;
	/** Hold the picture at this frame of the clip (counted from its start, after trimBefore). A frozen clip is silent. */
	freeze?: number;
	engine?: 'media' | 'offthread';
	/** Offthread engine: keep an alpha channel (ProRes 4444, WebM with alpha). Slower. */
	transparent?: boolean;
	/** Frames to mount early so the preview has it buffered (default 1 s). Renders are exact without it. */
	premountFor?: number;
	/** Blur radius of the 'blur' fill, px at 1080. */
	blur?: number;
	/** Darkening of the 'blur' fill, 0 to 1 (raise it to 0.5 when text sits on the fill). */
	dim?: number;
	name?: string;
	/** The box: fills the parent unless you position it here. */
	style?: React.CSSProperties;
	/** Styles on the picture itself (a filter, a grade). */
	videoStyle?: React.CSSProperties;
};

/** Frames a clip lasts from its trims and speed (Infinity without `trimAfter`). */
export const clipLength = (o: {trimBefore?: number; trimAfter?: number; playbackRate?: number}): number =>
	o.trimAfter === undefined ? Infinity : Math.max(0, (o.trimAfter - (o.trimBefore ?? 0)) / (o.playbackRate ?? 1));

const withHash = (src: string) => (src.includes('#') ? src : `${src}#disable`);

export const Clip: React.FC<ClipProps> = ({
	src,
	from = 0,
	durationInFrames,
	trimBefore,
	trimAfter,
	playbackRate = 1,
	objectFit = 'cover',
	volume = 1,
	fadeIn = 0,
	fadeOut = 0,
	fadePicture = false,
	muted = false,
	loop = false,
	freeze,
	engine = 'media',
	transparent = false,
	premountFor,
	blur = 40,
	dim = 0.35,
	name,
	style,
	videoStyle,
}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames: parentLength} = useVideoConfig();
	const {unit} = useStage();
	const rate = playbackRate > 0 ? playbackRate : 1;
	const natural = loop ? Infinity : clipLength({trimBefore, trimAfter, playbackRate: rate});
	const length = Math.min(durationInFrames ?? Infinity, natural, Math.max(0, parentLength - from));
	const pre = premountFor ?? fps;

	const hasCurve = typeof volume === 'function' || fadeIn > 0 || fadeOut > 0;
	const volumeFn = useCallback(
		(f: number) => safeGain((typeof volume === 'function' ? volume(f) : volume) * fadeGain(f, length, fadeIn, fadeOut)),
		[volume, length, fadeIn, fadeOut],
	);
	const vol = hasCurve ? volumeFn : safeGain(volume as number);

	const local = frame - from;
	const opacity = fadePicture
		? Math.min(
				fadeIn > 0 ? ramp(local, 0, fadeIn, curves.sine) : 1,
				fadeOut > 0 && Number.isFinite(length) ? 1 - ramp(local, length - 1 - fadeOut, fadeOut, curves.sine) : 1,
			)
		: 1;

	const fill: React.CSSProperties = {position: 'absolute', left: 0, top: 0, width: '100%', height: '100%'};
	const fit: VideoObjectFit = objectFit === 'blur' ? 'contain' : objectFit;
	const timing = {
		from,
		durationInFrames: Number.isFinite(length) ? length : undefined,
		trimBefore,
		trimAfter,
		playbackRate: rate,
		loop,
		premountFor: pre,
		freeze,
	};

	const box = useMemo<React.CSSProperties>(() => ({overflow: 'hidden', opacity, ...style}), [opacity, style]);

	if (engine === 'offthread') {
		const loopLength = Number.isFinite(clipLength({trimBefore, trimAfter, playbackRate: rate}))
			? Math.max(1, Math.round(clipLength({trimBefore, trimAfter, playbackRate: rate})))
			: null;
		const tag = (bg: boolean) => (
			<OffthreadVideo
				src={withHash(src)}
				trimBefore={trimBefore}
				trimAfter={trimAfter}
				playbackRate={rate}
				muted={bg || muted}
				volume={bg ? 0 : vol}
				transparent={transparent}
				style={
					bg
						? {position: 'absolute', left: '-5%', top: '-5%', width: '110%', height: '110%', objectFit: 'cover', filter: `blur(${blur * unit}px)`}
						: {...fill, objectFit: fit, ...videoStyle}
				}
			/>
		);
		const body = (bg: boolean) => {
			const inner = loop && loopLength ? <Loop durationInFrames={loopLength}>{tag(bg)}</Loop> : tag(bg);
			return freeze === undefined ? inner : <Freeze frame={freeze}>{inner}</Freeze>;
		};
		return (
			<AbsoluteFill style={box}>
				<Sequence from={from} durationInFrames={timing.durationInFrames} premountFor={pre} name={name ?? '<Clip>'}>
					{objectFit === 'blur' ? (
						<>
							{body(true)}
							<AbsoluteFill style={{background: `rgba(0,0,0,${dim})`}} />
						</>
					) : null}
					{body(false)}
				</Sequence>
			</AbsoluteFill>
		);
	}

	return (
		<AbsoluteFill style={box}>
			{objectFit === 'blur' ? (
				<>
					<Video
						src={src}
						{...timing}
						muted
						objectFit="cover"
						name={`${name ?? '<Clip>'} fill`}
						showInTimeline={false}
						style={{position: 'absolute', left: '-5%', top: '-5%', width: '110%', height: '110%', filter: `blur(${blur * unit}px)`}}
					/>
					<AbsoluteFill style={{background: `rgba(0,0,0,${dim})`}} />
				</>
			) : null}
			<Video
				src={src}
				{...timing}
				muted={muted}
				volume={vol}
				loopVolumeCurveBehavior="extend"
				objectFit={fit}
				name={name ?? '<Clip>'}
				style={{...fill, ...videoStyle}}
			/>
		</AbsoluteFill>
	);
};
