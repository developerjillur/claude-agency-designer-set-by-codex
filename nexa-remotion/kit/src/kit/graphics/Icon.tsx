// <Icon>: a kit icon that draws itself on (or sits still), and <IconBadge>: an icon in a tinted disc or tile that
// pops in and then draws its icon. Sizes are px at 1080.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {DrawnPath, type DrawTiming} from './Draw';
import {ICONS, type IconName} from './icons';
import type {DrawMode} from './paths';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type IconProps = DrawTiming &
	GraphicExitProps & {
		name: IconName;
		size?: number; // px at 1080 (default 96)
		color?: string; // default: the theme's text colour
		strokeWidth?: number; // on the 24 grid (default 2; 1.5 reads lighter, 2.5 bolder)
		draw?: boolean; // draw on (default true); false shows it whole at once
		mode?: DrawMode; // how its strokes share the draw (default 'sequence', like a pen)
		style?: React.CSSProperties;
	};

export const Icon: React.FC<IconProps> = ({
	name,
	size = 96,
	color,
	strokeWidth = 2,
	draw = true,
	mode = 'sequence',
	style,
	exit = 'none',
	outDuration,
	outAt,
	duration,
	...timing
}) => {
	const t = useTheme();
	const {unit, fps} = useStage();
	const q = useGraphicExit({exit: exit === 'undraw' ? 'none' : exit, outDuration, outAt});
	const s = size * unit;
	return (
		<svg
			viewBox="0 0 24 24"
			width={s}
			height={s}
			style={{display: 'block', overflow: 'visible', opacity: exit === 'fade' ? 1 - q : 1, scale: exit === 'shrink' ? `${1 - q}` : undefined, ...style}}
		>
			<DrawnPath
				{...timing}
				d={ICONS[name]}
				stroke={color ?? t.colors.text}
				strokeWidth={strokeWidth}
				mode={mode}
				progress={draw ? timing.progress : 1}
				duration={duration ?? at30(26, fps)}
				exit={exit === 'undraw' ? 'undraw' : 'none'}
				outDuration={outDuration}
				outAt={outAt}
			/>
		</svg>
	);
};

export type IconBadgeProps = Omit<IconProps, 'style'> & {
	shape?: 'circle' | 'tile';
	tint?: string; // the badge colour (default the theme accent): the disc is a light wash of it
	solid?: boolean; // a solid disc with the icon in the on-accent colour
	style?: React.CSSProperties;
};

/** An icon in a tinted disc or rounded tile: the disc pops in, then the icon draws. */
export const IconBadge: React.FC<IconBadgeProps> = ({
	name,
	size = 120,
	shape = 'circle',
	tint,
	solid = false,
	color,
	delay = 0,
	style,
	exit = 'none',
	outDuration,
	outAt,
	...rest
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const q = useGraphicExit({exit, outDuration, outAt});
	const tone = tint ?? t.colors.accent;
	const pop = ramp(frame, delay, at30(14, fps), curves.outBack);
	const s = size * unit;
	const radius = shape === 'circle' ? s / 2 : Math.min(t.radius * unit, s * 0.3);
	return (
		<div
			style={{
				width: s,
				height: s,
				borderRadius: radius,
				background: solid ? tone : withOpacity(tone, t.dark ? 0.18 : 0.12),
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				scale: `${Math.max(0, pop) * (exit === 'shrink' ? 1 - q : 1)}`,
				opacity: Math.min(1, pop * 1.5) * (exit === 'fade' ? 1 - q : 1),
				flexShrink: 0,
				...style,
			}}
		>
			<Icon
				name={name}
				size={size * 0.5}
				color={color ?? (solid ? t.colors.onAccent : tone)}
				delay={delay + at30(6, fps)}
				{...rest}
			/>
		</div>
	);
};
