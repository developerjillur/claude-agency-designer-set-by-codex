import React from 'react';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {Ground, ThemeProvider, TikTokCaptions, toCaptions, useTheme} from './kit';
import {CUT} from './cues';
import {WORDS} from './data/words';
import {EndCard} from './scenes/EndCard';
import {Notebook} from './scenes/Notebook';
import {PhoneStage, StepBadge} from './scenes/Phone';

// captions from the second sentence on: the hook's question is the big title on frame 0
const CAPTIONS = toCaptions(WORDS.filter((w) => w.start >= 3));

const BottomFade: React.FC = () => {
	const t = useTheme();
	return <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(14, 59, 46, 0) 0%, rgba(14, 59, 46, 0) 64.5%, ${t.colors.bg} 79%, ${t.colors.bg} 100%)`}} />;
};

export const Main: React.FC = () => (
	<ThemeProvider theme="dhaka">
		<Ground kind="lit">
			<Sequence name="Notebook" durationInFrames={CUT.phone + 12}>
				<Notebook />
			</Sequence>
			<Sequence name="Phone" from={CUT.phone} durationInFrames={CUT.end + 22 - CUT.phone} premountFor={30}>
				<PhoneStage />
			</Sequence>
			<Sequence name="Step 1" from={CUT.rule1} durationInFrames={CUT.rule2 - CUT.rule1}>
				<StepBadge n="১" />
			</Sequence>
			<Sequence name="Step 2" from={CUT.rule2} durationInFrames={CUT.rule3 - CUT.rule2}>
				<StepBadge n="২" />
			</Sequence>
			<Sequence name="Step 3" from={CUT.rule3} durationInFrames={CUT.phoneOut + 10 - CUT.rule3}>
				<StepBadge n="৩" />
			</Sequence>
			{/* the platform's caption and username sit over the phone's lower screen: it fades into the ground there */}
			<Sequence name="Fade" from={CUT.phone} durationInFrames={CUT.end + 22 - CUT.phone}>
				<BottomFade />
			</Sequence>
			{/* a whole sentence per page, the spoken number with its rule ("এক, প্রতিটা ..."), two lines at most above the
			    phone, never broken inside a phrase; gone with the phone */}
			<Sequence name="Captions" durationInFrames={CUT.phoneOut + 16}>
				<TikTokCaptions captions={CAPTIONS} highlight="pill" position={0.115} size={64} tone="theme" sentenceMs={3800} silenceMs={1200} />
			</Sequence>
			<Sequence name="End" from={CUT.end} durationInFrames={CUT.total - CUT.end}>
				<EndCard />
			</Sequence>
		</Ground>
		{/* voice, music bed (ducked) and effects, mixed and mastered to -14 LUFS by nexa-sound */}
		<Audio src={staticFile('audio/mix.wav')} />
	</ThemeProvider>
);
