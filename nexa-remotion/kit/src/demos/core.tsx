import React from 'react';
import {AbsoluteFill} from 'remotion';
import {
	FORMATS,
	SafeArea,
	SafeGuides,
	Stage,
	THEME_NAMES,
	ThemeProvider,
	useStage,
	useTheme,
	type DemoDef,
	type FormatName,
} from '../kit/core';

const Specimen: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const c = t.colors;
	return (
		<div
			style={{
				width: '100%',
				height: '100%',
				background: c.bg,
				color: c.text,
				padding: 22 * unit,
				boxSizing: 'border-box',
				display: 'flex',
				flexDirection: 'column',
				justifyContent: 'space-between',
				overflow: 'hidden',
			}}
		>
			<div style={{fontFamily: t.type.body, fontSize: 17 * unit, fontWeight: t.weights.strong, color: c.muted, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase'}}>
				{t.name}
			</div>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 60 * unit, lineHeight: 1, letterSpacing: `${t.tracking.display}em`, textTransform: t.caps ? 'uppercase' : 'none'}}>
				Aa Bold 24
			</div>
			<div style={{fontFamily: t.type.bangla, fontWeight: t.weights.strong, fontSize: 28 * unit, lineHeight: 1.15}}>বাংলা লেখা ১২৩</div>
			<div style={{display: 'flex', gap: 6 * unit}}>
				{[c.accent, c.accent2, c.highlight, c.surface, c.text].map((col, i) => (
					<div key={i} style={{width: 32 * unit, height: 32 * unit, borderRadius: Math.min(t.radius, 16) * unit, background: col, border: `${unit}px solid ${c.line}`}} />
				))}
			</div>
		</div>
	);
};

const Themes: React.FC = () => (
	<AbsoluteFill style={{display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gridTemplateRows: 'repeat(4, 1fr)', gap: 2, background: '#000'}}>
		{THEME_NAMES.map((name) => (
			<ThemeProvider key={name} theme={name}>
				<Specimen />
			</ThemeProvider>
		))}
	</AbsoluteFill>
);

const SafeContent: React.FC<{format: FormatName}> = ({format}) => {
	const t = useTheme();
	const {unit, width, height, safe} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<SafeArea justify="space-between">
				<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 84 * unit, lineHeight: 1, color: t.colors.text}}>{format}</div>
				<div style={{fontFamily: t.type.body, fontSize: 32 * unit, color: t.colors.muted}}>
					{width} x {height}, safe {Math.round(safe.w)} x {Math.round(safe.h)} at ({Math.round(safe.x)}, {Math.round(safe.y)})
					<br />
					{FORMATS[format].note}
				</div>
			</SafeArea>
			<SafeGuides />
		</AbsoluteFill>
	);
};

const SafeYoutube: React.FC = () => (
	<Stage format="youtube">
		<SafeContent format="youtube" />
	</Stage>
);

const SafeShorts: React.FC = () => (
	<Stage format="shorts">
		<SafeContent format="shorts" />
	</Stage>
);

export const demos: DemoDef[] = [
	{id: 'DemoCoreThemes', component: Themes, durationInFrames: 1},
	{id: 'DemoCoreSafeYoutube', component: SafeYoutube, durationInFrames: 1},
	{id: 'DemoCoreSafeShorts', component: SafeShorts, durationInFrames: 1, width: 1080, height: 1920},
];
