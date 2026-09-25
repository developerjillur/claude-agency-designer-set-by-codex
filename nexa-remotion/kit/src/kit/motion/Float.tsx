// <Float>: idle drift for pictures and objects once they have landed. Never on text that is being read: text
// holds perfectly still while it is read.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {curves, useStage} from '../core';
import {ramp, wiggle} from './helpers';

export const Float: React.FC<{
	amp?: number; // px at 1080
	rotate?: number; // degrees
	freq?: number; // Hz; 0.3 to 0.6 reads alive
	delay?: number; // frames before the drift starts (it eases in over a second, never jumps)
	lane?: number; // a different lane per element so they do not move in step
	children: React.ReactNode;
	style?: React.CSSProperties;
}> = ({amp = 6, rotate = 0.6, freq = 0.4, delay = 0, lane = 0, children, style}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const env = ramp(frame, delay, fps, curves.sine);
	const x = wiggle(frame, fps, freq, lane * 3) * amp * unit * env;
	const y = wiggle(frame, fps, freq, lane * 3 + 1) * amp * unit * env;
	const r = wiggle(frame, fps, freq * 0.7, lane * 3 + 2) * rotate * env;
	return <div style={{translate: `${x}px ${y}px`, rotate: `${r}deg`, ...style}}>{children}</div>;
};
