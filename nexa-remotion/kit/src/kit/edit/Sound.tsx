// Sound: a voice, a music bed that ducks under it, and sound effects that land on a frame. All three are the
// @remotion/media <Audio> (mixed at 48 kHz in renders) with gains that are pure functions of the frame.
import {Audio} from '@remotion/media';
import {mouseClick, pageTurn, shutterModern, shutterOld, uiSwitch, whip, whoosh} from '@remotion/sfx';
import React, {useCallback, useMemo} from 'react';
import {useVideoConfig} from 'remotion';
import {fadeGain, musicGain, safeGain, type DuckOptions, type TimeWindow} from './gain';

/**
 * The seven CC0 sounds in @remotion/sfx (safe for client work, no credit needed). They are remote URLs on
 * remotion.media: for offline or Lambda renders copy the files into public/sfx/ and use staticFile(). The other
 * @remotion/sfx exports are internet meme sounds with no stated licence: never in client work.
 */
export const SFX = {whoosh, whip, uiSwitch, mouseClick, pageTurn, shutterModern, shutterOld} as const;
export type SfxName = keyof typeof SFX;

/** Seconds from the start of each built-in file to its hit, so `at` lands the hit, not the file start. */
export const SFX_HIT: Record<SfxName, number> = {
	whoosh: 0.07,
	whip: 0.03,
	uiSwitch: 0,
	mouseClick: 0,
	pageTurn: 0.05,
	shutterModern: 0,
	shutterOld: 0,
};

export type VoiceProps = {
	src: string;
	from?: number;
	trimBefore?: number;
	trimAfter?: number;
	/** 1 = as recorded. Level voices with loudnorm before editing rather than here. */
	volume?: number;
	fadeIn?: number;
	fadeOut?: number;
	playbackRate?: number;
	name?: string;
};

/** A narration or dialogue track. The loudest layer of the mix. */
export const Voice: React.FC<VoiceProps> = ({src, from = 0, trimBefore, trimAfter, volume = 1, fadeIn = 0, fadeOut = 0, playbackRate = 1, name}) => {
	const {durationInFrames} = useVideoConfig();
	const natural = trimAfter === undefined ? Infinity : (trimAfter - (trimBefore ?? 0)) / playbackRate;
	const length = Math.min(natural, durationInFrames - from);
	const vol = useCallback((f: number) => safeGain(volume * fadeGain(f, length, fadeIn, fadeOut)), [volume, length, fadeIn, fadeOut]);
	return (
		<Audio
			src={src}
			from={from}
			trimBefore={trimBefore}
			trimAfter={trimAfter}
			playbackRate={playbackRate}
			volume={fadeIn > 0 || fadeOut > 0 ? vol : safeGain(volume)}
			name={name ?? 'Voice'}
		/>
	);
};

export type MusicProps = DuckOptions & {
	src: string;
	/** Frame on the parent timeline where the music starts. */
	from?: number;
	/** Frames it plays (default: to the end of the enclosing Sequence). The fade-out ends there. */
	durationInFrames?: number;
	trimBefore?: number;
	/** Voice windows on the parent timeline (the same timeline as `from`), in frames. speechWindows() makes them. */
	duck?: readonly TimeWindow[];
	/** Frames of fade at the start and the end. */
	fadeIn?: number;
	fadeOut?: number;
	/** Repeat the track until the end (default true); the gain curve keeps counting across repeats. */
	loop?: boolean;
	name?: string;
};

/**
 * A music bed: fades in, sits at `level`, ducks to `duckTo` under every voice window (the ramp down ends as the
 * voice starts, the ramp up waits `hold` frames after it; pauses shorter than `bridge` stay down), and fades out on
 * its last frame.
 */
export const Music: React.FC<MusicProps> = ({
	src,
	from = 0,
	durationInFrames,
	trimBefore,
	duck = [],
	fadeIn = 30,
	fadeOut = 60,
	loop = true,
	name,
	level = 0.5,
	duckTo = 0.06,
	attack = 30,
	release = 30,
	hold = 8,
	bridge,
}) => {
	const {durationInFrames: parentLength} = useVideoConfig();
	const length = Math.max(0, Math.min(durationInFrames ?? Infinity, parentLength - from));
	// compared by content, so an inline array does not make a new curve every render
	const key = JSON.stringify(duck);
	const windows = useMemo(() => (JSON.parse(key) as [number, number][]).map(([s, e]) => [s - from, e - from] as const), [key, from]);
	const vol = useCallback(
		(f: number) => musicGain(f, {length, fadeIn, fadeOut, windows, level, duckTo, attack, release, hold, bridge}),
		[windows, length, fadeIn, fadeOut, level, duckTo, attack, release, hold, bridge],
	);
	if (!(length > 0)) {
		return null;
	}
	return (
		<Audio
			src={src}
			from={from}
			durationInFrames={Number.isFinite(length) ? length : undefined}
			trimBefore={trimBefore}
			loop={loop}
			loopVolumeCurveBehavior="extend"
			volume={vol}
			name={name ?? 'Music'}
		/>
	);
};

export type SfxProps = {
	/** A file (staticFile or URL) or one of the seven CC0 names in SFX. */
	src: string;
	/** Frame the hit lands on (the cut, the impact, the word). */
	at: number;
	/** Frames from the file's start to its hit (default: known for the built-ins, else 0). */
	hit?: number;
	/** 0.1 to 0.3 under a voice; sweeteners, not headlines. */
	volume?: number;
	playbackRate?: number;
	name?: string;
};

/** One sound effect whose hit lands on frame `at`. A hit before frame 0 starts the file part-way. */
export const Sfx: React.FC<SfxProps> = ({src, at, hit, volume = 0.25, playbackRate = 1, name}) => {
	const {fps} = useVideoConfig();
	const builtIn = (Object.keys(SFX) as SfxName[]).includes(src as SfxName) ? (src as SfxName) : null;
	const url = builtIn ? SFX[builtIn] : src;
	const lead = hit ?? (builtIn ? Math.round(SFX_HIT[builtIn] * fps) : 0);
	const start = Math.round(at - lead);
	return (
		<Audio
			src={url}
			from={Math.max(0, start)}
			trimBefore={start < 0 ? -start : undefined}
			volume={safeGain(volume)}
			playbackRate={playbackRate}
			name={name ?? `Sfx ${builtIn ?? ''}`.trim()}
		/>
	);
};
