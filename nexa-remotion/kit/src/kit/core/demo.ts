import type React from 'react';

/** One demo composition of a kit module: registered in src/Root.tsx and rendered by `nrk.py demos`. */
export type DemoDef = {
	id: string; // starts with "Demo" and the module name, for example DemoMotionEnter
	component: React.FC;
	durationInFrames: number;
	width?: number; // default 1920
	height?: number; // default 1080
	fps?: number; // default 30
};
