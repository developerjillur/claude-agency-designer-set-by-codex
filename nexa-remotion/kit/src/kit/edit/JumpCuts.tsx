// <JumpCuts>: one source, only the parts worth keeping, back to back (pauses, ums and retakes cut out). Each piece
// is its own premounted clip in a <Series>, the pattern that plays smoothly in the preview and renders exactly.
// Alternate pieces can sit a little closer (a punch-in), the editor's trick that makes a jump cut look intended.
import React, {useMemo} from 'react';
import {AbsoluteFill, Series, useVideoConfig} from 'remotion';
import {Clip, type ClipFit} from './Clip';
import {buildEdit, type EditPiece, type KeepRange} from './edl';

export type JumpCutsProps = {
	src: string;
	/** Source ranges to keep, in seconds: [start, end] or [start, end, speed]. keepRanges() builds them from words. */
	ranges: readonly KeepRange[];
	objectFit?: ClipFit;
	volume?: number;
	muted?: boolean;
	/** Every second piece this much closer (0.06 to 0.12 reads as a second camera; 0 turns it off). */
	punchIn?: number;
	/** Where the punch-in centres, usually the face: CSS transform-origin. */
	punchOrigin?: string;
	/** Sound fade in frames at each join (0 by default: cuts sit in pauses; 2 to 3 smooths cuts inside sound). */
	declick?: number;
	/** Frames each piece is mounted early for smooth preview (default 1 s). */
	premountFor?: number;
	/** Something to draw over each piece (a label, a debug tag). */
	overlay?: (piece: EditPiece) => React.ReactNode;
	style?: React.CSSProperties;
};

export const JumpCuts: React.FC<JumpCutsProps> = ({
	src,
	ranges,
	objectFit = 'cover',
	volume = 1,
	muted = false,
	punchIn = 0,
	punchOrigin = '50% 40%',
	declick = 0,
	premountFor,
	overlay,
	style,
}) => {
	const {fps} = useVideoConfig();
	const edit = useMemo(() => buildEdit(ranges, fps), [ranges, fps]);
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Series>
				{edit.map((p) => (
					<Series.Sequence key={p.index} durationInFrames={p.length} premountFor={premountFor ?? fps} name={`Piece ${p.index + 1}`}>
						<AbsoluteFill style={{scale: p.index % 2 === 1 && punchIn > 0 ? `${1 + punchIn}` : undefined, transformOrigin: punchOrigin}}>
							<Clip
								src={src}
								trimBefore={p.trimBefore}
								playbackRate={p.rate}
								objectFit={objectFit}
								volume={volume}
								muted={muted}
								fadeIn={declick}
								fadeOut={declick}
								premountFor={0}
								name={`Piece ${p.index + 1}`}
							/>
						</AbsoluteFill>
						{overlay ? overlay(p) : null}
					</Series.Sequence>
				))}
			</Series>
		</AbsoluteFill>
	);
};
