import {Audio} from '@remotion/media';
import React from 'react';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {Animate, Card, Kicker, KineticTitle, ThemeProvider, curves, useStage, useTheme} from './kit';
import {Pin, Route, WorldMap, type MapKey} from './kit/maps';
import {CUE, TOTAL} from './cues';
import {PLACE, SEGMENTS} from './route';
import {Vessel} from './Vessel';
import {Canal} from './Canal';
import {WaterLabel} from './WaterLabel';

// The camera follows the voice: the Bay of Bengal, west to the Red Sea, into the canal, across the Mediterranean,
// up the coast of Europe, then the whole trip beside the closing title.
const OVERVIEW_AREA = {x: 760, y: 70, w: 1090, h: 940};
const CAMERA: MapKey[] = [
	{at: 0, bbox: [[83.5, 14.5], [98.5, 27.5]]}, // close on Chattogram: the pin and the ship are there on frame 0
	// widening at a steady rate from the first frame (an eased start held still for half a second: QA saw a freeze)
	{at: 112, bbox: [[76, 3], [99, 26]], ease: curves.linear},
	{at: 232, bbox: [[75, 2.5], [93, 17]], ease: curves.sine}, // toward Colombo as it lands on the word
	// a steady push into the port through the change of ship (a 4% push read as a frozen picture for 1.3 s)
	{at: 395, bbox: [[77, 4], [91, 15.5]], ease: curves.linear},
	{at: 470, bbox: [[28, 2], [86, 30]]}, // west over the Arabian Sea to the Red Sea
	{at: 560, bbox: [[31, 4.5], [83, 28.5]], ease: curves.sine},
	{at: 606, bbox: [[28, 24], [38, 33]]}, // into the Suez Canal
	{at: 620, bbox: [[28.6, 24.6], [37.4, 32.4]], ease: curves.sine},
	{at: 672, bbox: [[-2, 27], [38, 44]]}, // after the ship as it leaves the canal: it never leaves the frame
	{at: 745, bbox: [[-12, 26], [38, 46]], ease: curves.sine}, // the Mediterranean to Gibraltar
	{at: 830, bbox: [[-16, 33], [12, 56]]}, // up the coast of Europe
	{at: 900, bbox: [[-14.6, 34.3], [10.6, 54.7]], ease: curves.sine}, // a beat on Rotterdam before the pull-back
	{at: 950, bbox: [[-18, -1], [100, 58]], area: OVERVIEW_AREA}, // the whole trip
	{at: TOTAL - 1, bbox: [[-14, 2], [96, 55]], area: OVERVIEW_AREA, ease: curves.sine},
];

const OpenTitle: React.FC = () => {
	const {unit, safe} = useStage();
	return (
		<div style={{position: 'absolute', left: safe.x, top: safe.y + 40 * unit, width: 620 * unit}}>
			<Animate in="none" out="fade" outDuration={18}>
				<Card variant="solid" elevation={3} padding={[40, 48]}>
					<Kicker text="A typical route by sea" delay={-30} />
					<div style={{height: 14 * unit}} />
					<KineticTitle text="Chattogram to Rotterdam" size={64} maxWidth={520} in="none" />
				</Card>
			</Animate>
		</div>
	);
};

const EndTitle: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<div style={{position: 'absolute', left: safe.x, top: 300 * unit, width: 640 * unit}}>
			<Animate in="rise" distance={24}>
				<Card variant="solid" elevation={3} padding={[48, 52]}>
					<Kicker text="The whole trip" />
					<div style={{height: 16 * unit}} />
					<KineticTitle text="Chattogram to Rotterdam" size={68} maxWidth={540} />
					<div style={{height: 18 * unit}} />
					<Animate in="fade" delay={18}>
						<div style={{fontFamily: t.type.body, fontSize: 30 * unit, color: t.colors.muted}}>Through the Suez Canal</div>
					</Animate>
				</Card>
			</Animate>
		</div>
	);
};

export const Main: React.FC = () => (
	<ThemeProvider theme="data">
		<AbsoluteFill>
			{/* paper land on a clear blue sea with a drawn coast: grey land on pale sea read as washed out (1.34:1) */}
			<WorldMap camera={CAMERA} ocean="frame" colors={{ocean: '#BCD8EE', stage: '#BCD8EE', land: '#F3EFE7', border: '#DDD8CE', coast: '#9FB2C2'}}>
				<Canal color="#BCD8EE" />
				{SEGMENTS.map((s, i) => (
					<Route key={i} stops={s.stops} delay={s.delay} legDuration={s.legs} dwell={0} lift={0} ease={curves.linear} marker="none" pins={false} originPin={false} width={6} />
				))}
				{/* every sea name sits beside the route, never across it */}
				<WaterLabel at={[93.0, 15.0]} text="Bay of Bengal" delay={CUE.bay - 4} outAt={900} />
				<WaterLabel at={[63.5, 15.2]} text="Arabian Sea" delay={CUE.arabian - 4} outAt={900} />
				<WaterLabel at={[40.2, 19.2]} text="Red Sea" delay={CUE.redSea - 4} size={26} along={[[32.5, 30.0], [43.4, 12.6]]} outAt={900} />
				<WaterLabel at={[29.0, 34.4]} text="Mediterranean Sea" delay={CUE.med - 4} outAt={900} />
				<Pin at={PLACE.chattogram} label="Chattogram" sub="Bangladesh" delay={-30} side="left" labelSize={34} />
				<Pin at={PLACE.colombo} label="Colombo" sub="Sri Lanka" delay={CUE.colombo - 4} side="top" labelSize={34} pulse="none" out outAt={905} />
				{/* over the sea west of the port, clear of its name and of the island; up from "There", gone as the ship
				    sails on "Then" */}
				<Sequence from={CUE.there - 4} durationInFrames={CUE.then + 12 - (CUE.there - 4)} layout="none">
					<Pin at={PLACE.colombo} kind="ring" label="Moves to a bigger ship" side="left" labelSize={32} out />
				</Sequence>
				<Pin at={PLACE.suez} label="Suez Canal" sub="Egypt" delay={CUE.suez - 4} side="right" labelSize={34} />
				{/* under the strait: on the left its box hid the turn off Portugal and touched the end card */}
				<Pin at={PLACE.gibraltar} label="Gibraltar" delay={CUE.gibraltar - 4} side="bottom" labelSize={34} />
				<Pin at={PLACE.rotterdam} label="Rotterdam" sub="Netherlands" delay={CUE.rotterdam - 4} side="right" labelSize={34} />
				<Vessel />
			</WorldMap>
			<Sequence durationInFrames={CUE.crosses - 10}>
				<OpenTitle />
			</Sequence>
			<Sequence from={918}>
				<EndTitle />
			</Sequence>
		</AbsoluteFill>
		<Audio src={staticFile('audio/mix.wav')} />
	</ThemeProvider>
);
