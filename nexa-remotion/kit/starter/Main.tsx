import React from 'react';
import {Animate, Ground, KineticTitle, SafeArea, ThemeProvider, useStage, useTheme} from './kit';

// A starting scene: replace it with the storyboard's scenes (one file each in src/scenes/, composed here with
// <Series> or the fx module's Scenes). Every part reads the theme, so changing the theme name (or a makeTheme()
// brand kit) restyles the whole video.
const Opening: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<Ground kind="lit">
			<SafeArea justify="center" gap={28}>
				<KineticTitle text="Your title goes here" emphasis="title" out="mask" />
				<Animate in="rise" out="fade" delay={16}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 44 * unit, color: t.colors.muted}}>
						One line that says what this is about
					</div>
				</Animate>
			</SafeArea>
		</Ground>
	);
};

export const Main: React.FC = () => (
	<ThemeProvider theme="studio">
		<Opening />
	</ThemeProvider>
);
