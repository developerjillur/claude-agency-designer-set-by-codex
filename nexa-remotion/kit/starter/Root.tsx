import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';

// One composition per deliverable. Keep size, fps and length inline so Studio can edit them.
export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="Main" component={Main} width={__WIDTH__} height={__HEIGHT__} fps={__FPS__} durationInFrames={__FRAMES__} />
	</>
);
