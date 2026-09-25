import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';

// One composition per deliverable. Keep size, fps and length inline so Studio can edit them.
export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="Main" component={Main} width={1920} height={1080} fps={30} durationInFrames={810} />
	</>
);
