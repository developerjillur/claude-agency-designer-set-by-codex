// <Stagger>: its children arrive one after another. Stagger in reading order; keep the whole run short
// ((n - 1) * each + duration under about 0.8 s for siblings of one gesture).
import React from 'react';
import {at30, shuffle, useStage, useTheme} from '../core';
import {Animate, type AnimateProps} from './Animate';

export type StaggerProps = Omit<AnimateProps, 'children' | 'delay' | 'outAt'> & {
	each?: number; // frames between items (default: the theme's stagger)
	delay?: number; // frames before the first
	order?: 'forward' | 'reverse' | 'center' | 'random';
	outEach?: number; // frames between exits (0: all leave together)
	seed?: string;
	children: React.ReactNode;
};

export const Stagger: React.FC<StaggerProps> = ({
	each,
	delay = 0,
	order = 'forward',
	outEach = 0,
	seed = 'stagger',
	children,
	...rest
}) => {
	const theme = useTheme();
	const {fps, durationInFrames} = useStage();
	const step = each ?? at30(theme.motion.stagger, fps);
	const items = React.Children.toArray(children);
	const n = items.length;
	const randomRank = shuffle(
		items.map((_, i) => i),
		seed,
	);
	const rank = (i: number) =>
		order === 'reverse' ? n - 1 - i : order === 'center' ? Math.abs(i - (n - 1) / 2) : order === 'random' ? randomRank.indexOf(i) : i;
	const outDur = rest.outDuration ?? at30(theme.motion.exitFrames, fps);
	return (
		<>
			{items.map((child, i) => (
				<Animate
					key={i}
					delay={delay + Math.round(rank(i) * step)}
					outAt={outEach > 0 ? durationInFrames - 1 - outDur - (n - 1 - rank(i)) * outEach : undefined}
					{...rest}
				>
					{child}
				</Animate>
			))}
		</>
	);
};
