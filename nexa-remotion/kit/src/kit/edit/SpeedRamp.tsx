// Speed that changes over time. <SpeedRamp> plays footage through <OffthreadVideo> (the @remotion/media <Video>
// cannot change speed while it plays): at every output frame the clip is re-placed at the source position found
// by summing the speed so far. <TimeRamp> does the same for any animated children through <Freeze>.
import React, {useMemo} from 'react';
import {AbsoluteFill, Freeze, OffthreadVideo, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {curves, type Ease} from '../core';
import {rampPositions, speedAt, type SpeedKey} from './speed';

export type SpeedRampProps = {
	src: string;
	/** Speed keys on the output timeline: [{at: 0, speed: 1}, {at: 40, speed: 4}, {at: 70, speed: 0.3}]. */
	keys: readonly SpeedKey[];
	ease?: Ease;
	/** Source frame shown at output frame 0. */
	trimBefore?: number;
	objectFit?: 'cover' | 'contain' | 'fill';
	/** The ramped clip's own sound is not usable (it would be chopped every frame): keep it muted, lay music. */
	muted?: boolean;
	/** Keep alpha (ProRes 4444 or WebM with alpha sources). */
	transparent?: boolean;
	style?: React.CSSProperties;
};

const withHash = (src: string) => (src.includes('#') ? src : `${src}#disable`);

const useTable = (keys: readonly SpeedKey[], start: number, ease: Ease) => {
	const {durationInFrames} = useVideoConfig();
	const frames = Number.isFinite(durationInFrames) ? durationInFrames : 36000;
	// one table per render tab; the keys array is compared by content so an inline literal does not rebuild it
	const sig = JSON.stringify(keys);
	return useMemo(() => rampPositions(JSON.parse(sig) as SpeedKey[], frames, start, ease), [sig, frames, start, ease]);
};

export const SpeedRamp: React.FC<SpeedRampProps> = ({
	src,
	keys,
	ease = curves.inOut,
	trimBefore = 0,
	objectFit = 'cover',
	muted = true,
	transparent = false,
	style,
}) => {
	const frame = useCurrentFrame();
	const table = useTable(keys, trimBefore, ease);
	const at = Math.min(table.length - 1, Math.max(0, Math.round(frame)));
	const position = Math.max(0, Math.round(table[at]));
	// playbackRate only smooths the preview between frames; renders take the position above
	const rate = Math.min(16, Math.max(0.0625, speedAt(frame, keys, ease)));
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Sequence from={frame} name="<SpeedRamp>">
				<OffthreadVideo
					src={withHash(src)}
					trimBefore={position}
					playbackRate={rate}
					muted={muted}
					transparent={transparent}
					style={{width: '100%', height: '100%', objectFit}}
				/>
			</Sequence>
		</AbsoluteFill>
	);
};

export type TimeRampProps = {
	keys: readonly SpeedKey[];
	ease?: Ease;
	/** Child frame at output frame 0. */
	start?: number;
	children: React.ReactNode;
};

/**
 * Retimes any animated children: they see the ramped frame (fractional, so slow motion stays smooth). The ramped
 * frame is clamped to the composition's length, so the ramp must not run ahead of it (speed-ups need the extra
 * frames to exist). Media inside a Freeze is muted.
 */
export const TimeRamp: React.FC<TimeRampProps> = ({keys, ease = curves.inOut, start = 0, children}) => {
	const frame = useCurrentFrame();
	const table = useTable(keys, start, ease);
	const at = Math.min(table.length - 1, Math.max(0, Math.round(frame)));
	return <Freeze frame={table[at]}>{children}</Freeze>;
};
