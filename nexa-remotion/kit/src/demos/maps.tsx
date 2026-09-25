import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, SafeArea, Stage, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate, ramp} from '../kit/motion';
import {
	Choropleth,
	CountryLabel,
	CountryLabels,
	CountryShape,
	GeoLayer,
	Globe,
	MapZoom,
	Pin,
	Route,
	WorldMap,
	allCountries,
	circleKm,
	countryAnchor,
	distanceKm,
	followCamera,
	legSchedule,
	mapPalette,
	parallelLine,
	routeProgress,
	useMap,
	type LonLat,
	type ProjectionName,
	type RouteStop,
} from '../kit/maps';

// Places (world-atlas has countries only, so cities are given as [longitude, latitude])
const DHAKA: LonLat = [90.4125, 23.8103];
const CHATTOGRAM: LonLat = [91.7832, 22.3569];
const KHULNA: LonLat = [89.5403, 22.8456];
const RAJSHAHI: LonLat = [88.6042, 24.3745];
const SYLHET: LonLat = [91.8687, 24.8949];
const LONDON: LonLat = [-0.1276, 51.5072];
const NEW_YORK: LonLat = [-74.006, 40.7128];
const DUBAI: LonLat = [55.2708, 25.2048];
const SINGAPORE: LonLat = [103.8198, 1.3521];
const TOKYO: LonLat = [139.6917, 35.6895];

const Title: React.FC<{text: string; sub?: string; delay?: number; size?: number; out?: boolean; outAt?: number}> = ({text, sub, delay = 0, size = 72, out = true, outAt}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div>
			<Animate in="rise" out={out ? 'fade' : 'none'} delay={delay} outAt={outAt}>
				<div
					style={{
						fontFamily: t.type.display,
						fontWeight: t.weights.display,
						fontSize: size * unit,
						lineHeight: 1.05,
						letterSpacing: `${t.tracking.display}em`,
						textTransform: t.caps ? 'uppercase' : 'none',
						color: t.colors.text,
					}}
				>
					{text}
				</div>
			</Animate>
			{sub ? (
				<Animate in="rise" out={out ? 'fade' : 'none'} delay={delay + 6} outAt={outAt}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: size * 0.42 * unit, lineHeight: 1.35, color: t.colors.muted, marginTop: 12 * unit}}>{sub}</div>
				</Animate>
			) : null}
		</div>
	);
};

// 1. The world, drawn in west to east, with every name that fits
const WorldInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap graticule intro="sweep" introDuration={40} delay={4} camera={[{at: 0, fit: 'world', area: {x: 0, y: 175, w: 1920, h: 885}, padding: 0.01}]}>
				<CountryLabels delay={40} stagger={1} />
			</WorldMap>
			<SafeArea justify="start">
				<Title text="240 countries and territories" sub="Natural Earth 1:50m, natural earth projection" size={56} />
			</SafeArea>
		</AbsoluteFill>
	);
};

const World: React.FC = () => (
	<ThemeProvider theme="studio">
		<WorldInner />
	</ThemeProvider>
);

// 2. The four flat projections side by side
const PROJECTIONS: {name: ProjectionName; label: string}[] = [
	{name: 'naturalEarth1', label: 'naturalEarth1'},
	{name: 'equalEarth', label: 'equalEarth'},
	{name: 'mercator', label: 'mercator'},
	{name: 'equirectangular', label: 'equirectangular'},
];

const ProjectionsInner: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const cw = 860;
	const ch = 420;
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			{PROJECTIONS.map((p, i) => {
				const left = 96 + (i % 2) * (cw + 8);
				const top = 70 + Math.floor(i / 2) * (ch + 64);
				return (
					<React.Fragment key={p.name}>
						<WorldMap
							projection={p.name}
							width={cw}
							height={ch}
							padding={18}
							graticule
							highlight={[{country: 'Bangladesh', delay: 6 + i * 4, draw: 20}]}
							style={{left: left * unit, top: top * unit, borderRadius: 16 * unit}}
						/>
						<div style={{position: 'absolute', left: left * unit, top: (top + ch + 8) * unit, fontFamily: t.type.mono, fontSize: 24 * unit, color: t.colors.muted}}>{p.label}</div>
					</React.Fragment>
				);
			})}
		</AbsoluteFill>
	);
};

const Projections: React.FC = () => (
	<ThemeProvider theme="midnight">
		<ProjectionsInner />
	</ThemeProvider>
);

// 3. Bangladesh highlighted in its region, with the neighbours named quietly
const HighlightInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap
				camera={[
					{at: 0, bbox: [[66, 8], [104, 33]], padding: 0.02},
					{at: 149, bbox: [[68, 9], [102, 32]], padding: 0.02, ease: curves.sine},
				]}
				highlight={[{country: 'Bangladesh', delay: 12, label: 'বাংলাদেশ', sub: 'Bangladesh', labelMode: 'callout', labelSide: 'right'}]}
			>
				<CountryLabels countries={['India', 'Myanmar', 'Nepal', 'Bhutan', 'China', 'Pakistan']} lang="bn" size={22} delay={4} stagger={3} />
			</WorldMap>
		</AbsoluteFill>
	);
};

const Highlight: React.FC = () => (
	<ThemeProvider theme="studio">
		<HighlightInner />
	</ThemeProvider>
);

// 4. From the world down to Bangladesh, then its two biggest cities
const ZoomInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap
				camera={[
					{at: 0, fit: 'world', area: {x: 0, y: 150, w: 1920, h: 930}},
					{at: 26, fit: 'world', area: {x: 0, y: 150, w: 1920, h: 930}},
					{at: 116, fit: 'Bangladesh', padding: 0.12},
					{at: 239, fit: 'Bangladesh', padding: 0.09, ease: curves.sine},
				]}
				highlight={[{country: 'Bangladesh', delay: 84, label: true, labelMode: 'inside', sub: 'বাংলাদেশ', labelStyle: 'title'}]}
			>
				<CountryLabel country="India" delay={120} />
				<CountryLabel country="Myanmar" delay={124} />
				<Pin at={DHAKA} label="Dhaka" sub="ঢাকা" delay={140} side="right" />
				<Pin at={CHATTOGRAM} label="Chattogram" sub="চট্টগ্রাম" delay={152} side="right" />
			</WorldMap>
			<SafeArea justify="start">
				<Title text="Where is Bangladesh?" size={64} outAt={22} />
			</SafeArea>
		</AbsoluteFill>
	);
};

const Zoom: React.FC = () => (
	<ThemeProvider theme="midnight">
		<ZoomInner />
	</ThemeProvider>
);

// 4b. The one-line zoom: MapZoom to an archipelago in a capitals serif theme
const ZoomToInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<MapZoom to="Japan" delay={15} duration={75} padding={0.14} highlightTarget={{label: true, labelStyle: 'title', sub: 'Honshu, Hokkaido, Kyushu, Shikoku'}} />
		</AbsoluteFill>
	);
};

const ZoomTo: React.FC = () => (
	<ThemeProvider theme="luxury">
		<ZoomToInner />
	</ThemeProvider>
);

// 5. Dhaka to London to New York, the camera following each leg, a live distance counter
const TRIP: RouteStop[] = [
	{at: DHAKA, label: 'Dhaka', sub: 'Bangladesh'},
	{at: LONDON, label: 'London', sub: 'United Kingdom'},
	{at: NEW_YORK, label: 'New York', sub: 'United States', side: 'left'},
];

const RouteInner: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const opts = {delay: 24, dwell: 30};
	const legs = legSchedule(TRIP, fps, opts);
	const area = {x: 0, y: 190, w: 1920, h: 890};
	const camera = followCamera(TRIP, legs, {padding: 0.16, overview: 40, area});
	const km = routeProgress(frame, legs).km;
	const total = legs.reduce((s, l) => s + l.km, 0);
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap camera={camera} ocean="frame">
				<Route stops={TRIP} {...opts} ghost />
			</WorldMap>
			<SafeArea justify="start">
				<Animate in="rise">
					<div style={{display: 'flex', alignItems: 'baseline', gap: 18 * unit, fontFamily: t.type.display, fontWeight: t.weights.display, color: t.colors.text}}>
						<span style={{fontSize: 64 * unit, fontVariantNumeric: 'tabular-nums', letterSpacing: `${t.tracking.display}em`}}>{Math.round(Math.min(km, total)).toLocaleString('en-US')}</span>
						<span style={{fontSize: 30 * unit, fontFamily: t.type.body, fontWeight: t.weights.body, color: t.colors.muted}}>km flown of {Math.round(total).toLocaleString('en-US')}</span>
					</div>
				</Animate>
			</SafeArea>
		</AbsoluteFill>
	);
};

const RouteDemo: React.FC = () => (
	<ThemeProvider theme="studio">
		<RouteInner />
	</ThemeProvider>
);

// 5b. Across the date line on a Pacific-centred Mercator, in a capitals theme, with a dashed trail
const HONOLULU: LonLat = [-157.8583, 21.3069];
const LOS_ANGELES: LonLat = [-118.2437, 34.0522];
const PACIFIC: RouteStop[] = [
	{at: TOKYO, label: 'Tokyo', sub: 'Japan', side: 'top'},
	{at: HONOLULU, label: 'Honolulu', sub: 'Hawaii', side: 'bottom'},
	{at: LOS_ANGELES, label: 'Los Angeles', sub: 'California', side: 'top'},
];

const PacificInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap projection="mercator" meridian={180} camera={[{at: 0, points: [TOKYO, HONOLULU, LOS_ANGELES], padding: 0.1, area: {x: 0, y: 220, w: 1920, h: 860}}]}>
				<Route stops={PACIFIC} delay={20} dwell={20} trail="dashed" pinKind="ring" />
			</WorldMap>
			<SafeArea justify="start">
				<Title text="Across the date line" sub="Tokyo, Honolulu, Los Angeles" size={64} out={false} />
			</SafeArea>
		</AbsoluteFill>
	);
};

const Pacific: React.FC = () => (
	<ThemeProvider theme="kinetic">
		<PacificInner />
	</ThemeProvider>
);

// 6. A globe that turns to Bangladesh, then flights rising off it (the far ones pass behind)
const GlobeInner: React.FC = () => {
	const t = useTheme();
	const dests: {at: LonLat; label: string; side?: 'left' | 'right' | 'top' | 'bottom'}[] = [
		{at: DUBAI, label: 'Dubai', side: 'left'},
		{at: LONDON, label: 'London', side: 'left'},
		{at: SINGAPORE, label: 'Singapore', side: 'right'},
		{at: TOKYO, label: 'Tokyo', side: 'right'},
		{at: NEW_YORK, label: 'New York', side: 'top'},
	];
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Globe
				keys={[
					{at: 0, center: [10, 30]},
					{at: 70, center: [72, 30], zoom: 1.05},
				]}
				spin={1.5}
				highlight={[{country: 'Bangladesh', delay: 60, draw: 20}]}
			>
				{dests.map((d, i) => (
					<Route key={d.label} stops={[DHAKA, {at: d.at, label: d.label, side: d.side}]} delay={96 + i * 10} marker="dot" legDuration={54} originPin={false} width={3.5} />
				))}
				<Pin at={DHAKA} label="Dhaka" delay={78} side="bottom" pulse="once" />
			</Globe>
		</AbsoluteFill>
	);
};

const GlobeDemo: React.FC = () => (
	<ThemeProvider theme="midnight">
		<GlobeInner />
	</ThemeProvider>
);

// 7. How far every country is from Dhaka (great-circle km to the middle of each country, computed here)
const FROM_DHAKA = Object.fromEntries(
	allCountries()
		.filter((c) => c.key !== '010' && c.key !== '050')
		.map((c) => {
			const a = countryAnchor(c.key);
			return [c.key, a ? distanceKm(DHAKA, a.lonlat) : NaN] as const;
		})
		.filter(([, v]) => Number.isFinite(v)),
);

const ChoroplethInner: React.FC = () => {
	const t = useTheme();
	const near = [...mapPalette(t).ramp].reverse();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Choropleth
				data={FROM_DHAKA}
				scale="threshold"
				breaks={[2000, 4000, 6000, 8000, 10000, 12000]}
				ramp={near}
				reveal="rank"
				delay={10}
				duration={75}
				highlight={[{country: 'Bangladesh', draw: 0, outline: false, fill: 0, color: t.colors.text}]}
				camera={[{at: 0, fit: 'world', area: {x: 0, y: 160, w: 1920, h: 760}}]}
				legend={{title: 'Distance from Dhaka, km', note: 'Great-circle distance to the middle of each country', position: 'bottom-left'}}
			>
				<Pin at={DHAKA} label="Dhaka" delay={6} side="bottom" size={14} />
			</Choropleth>
			<SafeArea justify="start">
				<Title text="How far is every country from Dhaka?" size={56} out={false} />
			</SafeArea>
		</AbsoluteFill>
	);
};

const ChoroplethDemo: React.FC = () => (
	<ThemeProvider theme="data">
		<ChoroplethInner />
	</ThemeProvider>
);

// 8. One country on its own, drawn at 1:10m
const CountryInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<CountryShape country="Bangladesh" detail="10m" label="বাংলাদেশ" sub="Bangladesh" neighbours delay={6} />
		</AbsoluteFill>
	);
};

const Country: React.FC = () => (
	<ThemeProvider theme="dhaka">
		<CountryInner />
	</ThemeProvider>
);

// 9. Three countries as small multiples, each in its own box
const RowInner: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const items = [
		{c: 'Nepal', bn: 'নেপাল'},
		{c: 'Bangladesh', bn: 'বাংলাদেশ'},
		{c: 'Sri Lanka', bn: 'শ্রীলঙ্কা'},
	];
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<SafeArea justify="start">
				<Title text="Three neighbours, one scale" sub="Each country drawn at 78 px per degree of latitude" size={56} out={false} />
			</SafeArea>
			{items.map((it, i) => (
				<CountryShape
					key={it.c}
					country={it.c}
					width={540}
					height={660}
					label={it.bn}
					sub={it.c}
					labelSize={52}
					scale={78}
					delay={6 + i * 10}
					style={{left: (110 + i * 580) * unit, top: 250 * unit}}
				/>
			))}
		</AbsoluteFill>
	);
};

const CountryRow: React.FC = () => (
	<ThemeProvider theme="studio">
		<RowInner />
	</ThemeProvider>
);

// 10. City pins on a close map (auto 10m detail at this zoom)
const PinsInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap
				camera={[
					{at: 0, fit: 'Bangladesh', padding: 0.07},
					{at: 149, fit: 'Bangladesh', padding: 0.04, ease: curves.sine},
				]}
				highlight={[{country: 'Bangladesh', draw: 0, fill: 0}]}
				colors={{highlight: ['#FFFFFF'], highlightLine: t.colors.muted, tagBg: t.colors.text, tagText: t.colors.bg, tagMuted: t.colors.faint}}
			>
				<CountryLabel country="India" delay={2} />
				<CountryLabel country="Myanmar" delay={4} />
				<Pin at={DHAKA} label="Dhaka" sub="Capital" kind="pin" delay={10} side="right" size={20} />
				<Pin at={RAJSHAHI} label="Rajshahi" delay={24} side="left" />
				<Pin at={KHULNA} label="Khulna" delay={32} side="left" />
				<Pin at={SYLHET} label="Sylhet" delay={40} side="right" />
				<Pin at={CHATTOGRAM} label="Chattogram" delay={48} side="right" />
			</WorldMap>
		</AbsoluteFill>
	);
};

const Pins: React.FC = () => (
	<ThemeProvider theme="studio">
		<PinsInner />
	</ThemeProvider>
);

// 10b. Your own GeoJSON on the map: a line of latitude and a 100 km circle around Dhaka, plus a custom label
const TROPIC = 23.4368;
const TROPIC_LINE = parallelLine(TROPIC, 87.2, 94.6);
const AROUND_DHAKA = circleKm(DHAKA, 100);

const MapNote: React.FC<{at: LonLat; text: string; delay: number}> = ({at, text, delay}) => {
	const map = useMap();
	const t = useTheme();
	const frame = useCurrentFrame();
	const p = map.project(at);
	const k = ramp(frame, delay, 14, curves.out);
	return (
		<div style={{position: 'absolute', left: p.x, top: p.y, translate: `-100% calc(-100% - ${10 * map.unit}px)`, opacity: k, fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 22 * map.unit, letterSpacing: '0.06em', textTransform: 'uppercase', color: t.colors.accent2, whiteSpace: 'nowrap'}}>
			{text}
		</div>
	);
};

const GeoInner: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<WorldMap
				camera={[
					{at: 0, fit: 'Bangladesh', padding: 0.1, area: {x: 480, y: 0, w: 1440, h: 1080}},
					{at: 179, fit: 'Bangladesh', padding: 0.07, area: {x: 480, y: 0, w: 1440, h: 1080}, ease: curves.sine},
				]}
				ocean="frame"
			>
				<GeoLayer data={TROPIC_LINE} stroke={t.colors.accent2} dash="dashed" delay={12} draw={45} head />
				<MapNote at={[94.6, TROPIC]} text="Tropic of Cancer" delay={50} />
				<GeoLayer data={AROUND_DHAKA} stroke={t.colors.accent} fill={t.colors.accent} fillOpacity={0.18} delay={66} draw={40} />
				<Pin at={DHAKA} label="Dhaka" sub="100 km around" delay={90} side="left" />
			</WorldMap>
			<SafeArea justify="center" style={{width: 700}}>
				<Title text="The Tropic of Cancer crosses Bangladesh" sub="Your own GeoJSON on the kit's map: a line and a circle" size={60} out={false} />
			</SafeArea>
		</AbsoluteFill>
	);
};

const Geo: React.FC = () => (
	<ThemeProvider theme="corporate">
		<GeoInner />
	</ThemeProvider>
);

// 11. A vertical map story: the globe turns from Dhaka to London as the flight crosses it
const VERTICAL_TRIP: RouteStop[] = [
	{at: DHAKA, label: 'Dhaka', sub: 'ঢাকা', side: 'right'},
	{at: LONDON, label: 'London', sub: 'লন্ডন', side: 'left'},
];

const VerticalInner: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps} = useStage();
	const opts = {delay: 40, legDuration: 150};
	const legs = legSchedule(VERTICAL_TRIP, fps, opts);
	const km = routeProgress(frame, legs).km;
	const total = distanceKm(DHAKA, LONDON);
	const size = 1000;
	const cx = 540;
	const cy = 1230;
	const arrive = ramp(frame, legs[0].end, at30(14, fps), curves.outCubic);
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Globe
				size={size}
				x={cx}
				y={cy}
				keys={[
					{at: 0, center: [86, 14]},
					{at: 40, center: [86, 14]},
					{at: 190, center: [42, 22]},
				]}
				highlight={[{country: 'Bangladesh', delay: 8, draw: 18}, {country: 'United Kingdom', delay: 176, draw: 16}]}
			>
				<Route stops={VERTICAL_TRIP} {...opts} marker="plane" lift={0.16} />
			</Globe>
			<div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w}}>
				<Animate in="rise">
					<div style={{fontFamily: t.type.bangla, fontWeight: t.weights.display, fontSize: 88 * unit, lineHeight: 1.1, color: t.colors.text}}>ঢাকা থেকে লন্ডন</div>
				</Animate>
				<Animate in="rise" delay={6}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 34 * unit, color: t.colors.muted, marginTop: 10 * unit}}>Dhaka to London, the great-circle way</div>
				</Animate>
				<Animate in="rise" delay={14}>
					<div style={{display: 'flex', alignItems: 'baseline', gap: 14 * unit, marginTop: 28 * unit}}>
						<span style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 76 * unit, color: arrive > 0 ? t.colors.accent : t.colors.text, fontVariantNumeric: 'tabular-nums'}}>
							{Math.round(Math.min(km, total)).toLocaleString('en-US')}
						</span>
						<span style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 32 * unit, color: t.colors.muted}}>km</span>
					</div>
				</Animate>
			</div>
		</AbsoluteFill>
	);
};

const Vertical: React.FC = () => (
	<ThemeProvider theme="midnight">
		<Stage format="shorts">
			<VerticalInner />
		</Stage>
	</ThemeProvider>
);

// 12. The map palette in six themes (colours come from the theme, nothing is set by hand)
const THEMES: ThemeName[] = ['studio', 'midnight', 'vox', 'editorial', 'neon', 'dhaka'];

const ThemeCell: React.FC<{i: number}> = ({i}) => {
	const t = useTheme();
	const {unit} = useStage();
	const w = 630;
	const h = 350;
	const left = 10 + (i % 3) * (w + 5);
	const top = 130 + Math.floor(i / 3) * (h + 70);
	return (
		<div style={{position: 'absolute', left: left * unit, top: top * unit, width: w * unit, height: (h + 60) * unit, overflow: 'hidden', background: t.colors.bg}}>
			<WorldMap width={w} height={h} padding={14} highlight={[{country: 'Bangladesh', delay: 4, draw: 16}, {country: 'Brazil', delay: 8, draw: 16}]} />
			<div style={{position: 'absolute', left: 16 * unit, top: (h + 10) * unit, fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 26 * unit, color: t.colors.text}}>{t.name}</div>
		</div>
	);
};

const Themes: React.FC = () => (
	<AbsoluteFill style={{background: '#16181C'}}>
		{THEMES.map((name, i) => (
			<ThemeProvider key={name} theme={name}>
				<ThemeCell i={i} />
			</ThemeProvider>
		))}
	</AbsoluteFill>
);

export const demos: DemoDef[] = [
	{id: 'DemoMapsWorld', component: World, durationInFrames: 180},
	{id: 'DemoMapsProjections', component: Projections, durationInFrames: 60},
	{id: 'DemoMapsHighlight', component: Highlight, durationInFrames: 150},
	{id: 'DemoMapsZoom', component: Zoom, durationInFrames: 240},
	{id: 'DemoMapsZoomTo', component: ZoomTo, durationInFrames: 180},
	{id: 'DemoMapsRoute', component: RouteDemo, durationInFrames: 330},
	{id: 'DemoMapsPacific', component: Pacific, durationInFrames: 240},
	{id: 'DemoMapsGlobe', component: GlobeDemo, durationInFrames: 240},
	{id: 'DemoMapsChoropleth', component: ChoroplethDemo, durationInFrames: 150},
	{id: 'DemoMapsCountry', component: Country, durationInFrames: 120},
	{id: 'DemoMapsCountryRow', component: CountryRow, durationInFrames: 120},
	{id: 'DemoMapsPins', component: Pins, durationInFrames: 150},
	{id: 'DemoMapsGeoLayer', component: Geo, durationInFrames: 180},
	{id: 'DemoMapsVertical', component: Vertical, durationInFrames: 300, width: 1080, height: 1920},
	{id: 'DemoMapsThemes', component: Themes, durationInFrames: 45},
];
