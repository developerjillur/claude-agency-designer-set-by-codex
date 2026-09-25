import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {curves, springs, useStage, useTheme, type CurveName, type DemoDef, type SpringName} from '../kit/core';
import {
	Animate,
	Camera,
	MotionBlur,
	Parallax,
	Shake,
	Stagger,
	ramp,
	springAt,
	type Reveal,
} from '../kit/motion';

const KINDS: Reveal[] = ['fade', 'rise', 'drop', 'left', 'right', 'pop', 'grow', 'zoom', 'blur', 'mask', 'maskDown', 'wipe', 'wipeLeft', 'wipeUp', 'wipeDown', 'iris', 'flip', 'swing'];

const Enter: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg, padding: 80 * unit, boxSizing: 'border-box'}}>
			<div style={{display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gridTemplateRows: 'repeat(3, 1fr)', gap: 28 * unit, height: '100%'}}>
				{KINDS.map((k, i) => (
					<Animate key={k} in={k} out={k} delay={6 + i * 3} duration={18} outDuration={14} style={{height: '100%'}} innerStyle={{height: '100%'}}>
						<div style={{height: '100%', background: t.colors.surface, borderRadius: 20 * unit, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 ${10 * unit}px ${30 * unit}px rgba(17,24,39,0.08)`, fontFamily: t.type.display, fontWeight: 800, fontSize: 40 * unit, color: t.colors.text}}>
							{k}
						</div>
					</Animate>
				))}
			</div>
		</AbsoluteFill>
	);
};

const CURVES: CurveName[] = ['out', 'outCubic', 'outQuint', 'outBack', 'emphasized', 'snap', 'in', 'anticipate', 'inOut', 'inOutExpo', 'sine', 'linear'];

const Curves: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit} = useStage();
	const rowH = 960 / CURVES.length;
	return (
		<AbsoluteFill style={{background: t.colors.bg, padding: `${60 * unit}px ${80 * unit}px`, boxSizing: 'border-box'}}>
			{CURVES.map((name, i) => {
				const v = ramp(frame, 10, 60, curves[name]);
				return (
					<div key={name} style={{height: rowH * unit, display: 'flex', alignItems: 'center'}}>
						<div style={{width: 300 * unit, fontFamily: t.type.mono, fontSize: 30 * unit, color: t.colors.text}}>{name}</div>
						<div style={{position: 'relative', flex: 1, height: 4 * unit, background: t.colors.line, borderRadius: 2 * unit}}>
							<div style={{position: 'absolute', top: -18 * unit, left: `calc(${v * 100}% - ${20 * unit}px)`, width: 40 * unit, height: 40 * unit, borderRadius: 20 * unit, background: i % 2 ? t.colors.accent : t.colors.accent2}} />
						</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

const SPRINGS = Object.keys(springs) as SpringName[];

const Springs: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-evenly'}}>
			{SPRINGS.map((name) => {
				const s = springAt(frame, fps, {delay: 8, config: name});
				return (
					<div key={name} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 60 * unit}}>
						<div style={{width: 180 * unit, height: 180 * unit, borderRadius: 32 * unit, background: t.colors.accent, scale: `${0.2 + 0.8 * s}`}} />
						<div style={{fontFamily: t.type.mono, fontSize: 30 * unit, color: t.colors.text}}>{name}</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

const StaggerDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const words = 'Motion that reads first'.split(' ');
	const items = ['Hold text still while it is read', 'One focal move at a time', 'Arrive with ease-out', 'Leave faster with ease-in', 'Stagger in reading order'];
	return (
		<AbsoluteFill style={{background: t.colors.bg, padding: `${120 * unit}px ${160 * unit}px`, boxSizing: 'border-box', gap: 60 * unit}}>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 120 * unit, lineHeight: 1.05, letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>
				<Stagger in="mask" out="mask" each={4} inline>
					{words.map((w) => (
						<span key={w} style={{marginRight: '0.25em'}}>
							{w}
						</span>
					))}
				</Stagger>
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 22 * unit}}>
				<Stagger in="rise" out="fade" delay={20} each={6} outEach={3}>
					{items.map((s) => (
						<div key={s} style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 44 * unit, color: t.colors.muted, display: 'flex', alignItems: 'center', gap: 24 * unit}}>
							<span style={{width: 16 * unit, height: 16 * unit, borderRadius: 8 * unit, background: t.colors.accent}} />
							{s}
						</div>
					))}
				</Stagger>
			</div>
		</AbsoluteFill>
	);
};

const CARDS = [
	{x: 800, y: 600, label: 'Plan'},
	{x: 1900, y: 520, label: 'Design'},
	{x: 3000, y: 700, label: 'Animate'},
	{x: 1200, y: 1500, label: 'Render'},
	{x: 2300, y: 1650, label: 'Check'},
	{x: 3200, y: 1500, label: 'Deliver'},
];

const CameraDemo: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Camera
				world={{width: 3840, height: 2160}}
				keys={[
					{at: 0, x: 1920, y: 1080, zoom: 0.48},
					{at: 30, zoom: 0.48},
					{at: 70, x: 800, y: 600, zoom: 1.15},
					{at: 100},
					{at: 140, x: 3000, y: 1500, zoom: 1},
					{at: 179, x: 1920, y: 1080, zoom: 0.5},
				]}
			>
				<Parallax depth={0.55}>
					<svg width={3840} height={2160} style={{position: 'absolute', inset: 0}}>
						{Array.from({length: 40 * 23}).map((_, i) => (
							<circle key={i} cx={(i % 40) * 96 + 48} cy={Math.floor(i / 40) * 96 + 48} r={5} fill={t.colors.faint} />
						))}
					</svg>
				</Parallax>
				{CARDS.map((c, i) => (
					<div key={c.label} style={{position: 'absolute', left: c.x - 300, top: c.y - 200, width: 600, height: 400, borderRadius: 40, background: t.colors.surface, boxShadow: '0 30px 80px rgba(17,24,39,0.12)', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 60, boxSizing: 'border-box'}}>
						<div style={{fontFamily: t.type.mono, fontSize: 40, color: t.colors.accent}}>0{i + 1}</div>
						<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 96, color: t.colors.text}}>{c.label}</div>
					</div>
				))}
			</Camera>
		</AbsoluteFill>
	);
};

const Whip: React.FC<{y: number}> = ({y}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, width} = useStage();
	const x = ramp(frame, 8, 10, curves.inOutExpo) * (width - 500 * unit) + 100 * unit;
	return <div style={{position: 'absolute', left: x, top: y * unit, width: 300 * unit, height: 180 * unit, borderRadius: 24 * unit, background: t.colors.accent}} />;
};

const BlurShake: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const label = (text: string, top: number) => (
		<div style={{position: 'absolute', left: 100 * unit, top: top * unit, fontFamily: t.type.mono, fontSize: 32 * unit, color: t.colors.muted}}>{text}</div>
	);
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			{label('no blur', 110)}
			<Whip y={160} />
			{label('MotionBlur samples 6', 410)}
			<MotionBlur>
				<Whip y={460} />
			</MotionBlur>
			{label('Shake at frame 30', 710)}
			<Shake from={30} duration={16} amp={18}>
				<div style={{position: 'absolute', left: 100 * unit, top: 760 * unit, width: 300 * unit, height: 180 * unit, borderRadius: 24 * unit, background: t.colors.accent2}} />
			</Shake>
		</AbsoluteFill>
	);
};

export const demos: DemoDef[] = [
	{id: 'DemoMotionEnter', component: Enter, durationInFrames: 150},
	{id: 'DemoMotionCurves', component: Curves, durationInFrames: 90},
	{id: 'DemoMotionSprings', component: Springs, durationInFrames: 75},
	{id: 'DemoMotionStagger', component: StaggerDemo, durationInFrames: 120},
	{id: 'DemoMotionCamera', component: CameraDemo, durationInFrames: 180},
	{id: 'DemoMotionBlurShake', component: BlurShake, durationInFrames: 60},
];
