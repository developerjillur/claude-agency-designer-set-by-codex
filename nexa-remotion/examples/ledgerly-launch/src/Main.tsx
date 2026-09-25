import {Audio} from '@remotion/media';
import React from 'react';
import {staticFile} from 'remotion';
import {ThemeProvider} from './kit';
import {Scenes, tr, type SceneSpec} from './kit/fx';
import {DURATION} from './cues';
import {Cta} from './scenes/Cta';
import {Currencies} from './scenes/Currencies';
import {Hook} from './scenes/Hook';
import {Receipt} from './scenes/Receipt';
import {Reminders} from './scenes/Reminders';

const SCENES: SceneSpec[] = [
	{name: 'Hook', node: <Hook />, duration: DURATION[0], transition: tr.whipPan({direction: 'left', frames: 12})},
	{name: 'Receipt', node: <Receipt />, duration: DURATION[1], transition: tr.whipPan({direction: 'left', frames: 12})},
	{name: 'Reminders', node: <Reminders />, duration: DURATION[2], transition: tr.whipPan({direction: 'left', frames: 12})},
	{name: 'Currencies', node: <Currencies />, duration: DURATION[3], transition: tr.zoomThrough({frames: 12})},
	{name: 'CTA', node: <Cta />, duration: DURATION[4]},
];

export const Main: React.FC = () => (
	<ThemeProvider theme="midnight">
		<Scenes scenes={SCENES} />
		<Audio src={staticFile('audio/mix.wav')} />
	</ThemeProvider>
);
