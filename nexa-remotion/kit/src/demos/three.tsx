import React from 'react';
import {AbsoluteFill, staticFile, useCurrentFrame} from 'remotion';
import {SafeArea, ThemeProvider, curves, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate, Stagger, ramp} from '../kit/motion';
import {
	Bloom,
	CameraPath,
	Card3D,
	FloatingCards,
	Floor,
	Model,
	Particles,
	Phone3D,
	ProductSpin,
	RoundedBox,
	Scene3D,
	Svg3D,
	Text3D,
	Turntable,
	mix,
} from '../kit/three';

const themed = (theme: ThemeName, C: React.FC): React.FC => {
	const Wrapped: React.FC = () => (
		<ThemeProvider theme={theme}>
			<C />
		</ThemeProvider>
	);
	return Wrapped;
};

// ---------------------------------------------------------------- 2D copy blocks

const Eyebrow: React.FC<{children: React.ReactNode}> = ({children}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 30 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: t.colors.accent}}>
			{children}
		</div>
	);
};

const Headline: React.FC<{text: string; size?: number; delay?: number}> = ({text, size = 132, delay = 0}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: size * unit, lineHeight: 1.02, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textTransform: t.caps ? 'uppercase' : 'none', ...({textWrap: 'balance'} as React.CSSProperties)}}>
			<Stagger in="mask" out="fade" inline delay={delay} each={4}>
				{text.split(' ').map((w, i) => (
					<span key={i} style={{marginRight: '0.24em'}}>
						{w}
					</span>
				))}
			</Stagger>
		</div>
	);
};

const Sub: React.FC<{children: React.ReactNode; delay?: number; width?: number}> = ({children, delay = 16, width = 620}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<Animate in="rise" out="fade" delay={delay}>
			<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 38 * unit, lineHeight: 1.35, color: t.colors.muted, maxWidth: width * unit, ...({textWrap: 'balance'} as React.CSSProperties)}}>{children}</div>
		</Animate>
	);
};

// ---------------------------------------------------------------- product

const Product: React.FC<{screen?: string; video?: string; vertical?: boolean}> = ({screen, video, vertical}) => {
	const t = useTheme();
	return (
		<AbsoluteFill>
			<Scene3D camera={vertical ? {preset: 'hero', target: [0, 0.75, 0]} : {preset: 'hero', target: [-2.1, 0, 0]}} lights={t.dark ? 'dramatic' : 'studio'}>
				<ProductSpin from={-34} to={20} delay={4} floor={vertical ? -2.75 : -2.05} shadow={vertical ? 2.6 : 2.2}>
					<Phone3D screen={screen} video={video} height={vertical ? 4.6 : 3.3} />
				</ProductSpin>
			</Scene3D>
			<SafeArea justify={vertical ? 'start' : 'center'} align="start" gap={18} style={vertical ? {paddingTop: 20} : {width: '44%'}}>
				<Animate in="fade" out="fade" delay={14}>
					<Eyebrow>New</Eyebrow>
				</Animate>
				<Headline text="Nexa One" delay={18} size={vertical ? 120 : 140} />
				<Sub delay={30} width={vertical ? 800 : 640}>
					All-day battery. A camera that sees in the dark.
				</Sub>
			</SafeArea>
		</AbsoluteFill>
	);
};

const ProductDemo: React.FC = () => <Product screen={staticFile('three/wallpaper.jpg')} />;
const ProductApp: React.FC = () => <Product />;
const ProductVertical: React.FC = () => <Product video={staticFile('three/screen.mp4')} vertical />;

// ---------------------------------------------------------------- a glTF model (generated test asset)

const ModelDemo: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill>
			<Scene3D camera={{preset: 'hero', elevation: 8, target: [-2, 1.1, 0]}} lights="dramatic" shadows>
				<Floor grid={false} y={-0.02} shadowOpacity={0.35} />
				<ProductSpin from={-20} to={25} delay={4} float={0} floor={-0.01} shadow={2.2}>
					<Model src={staticFile('three/bottle.glb')} height={2.7} offset={-1.6} loop={false} envIntensity={1.4} />
				</ProductSpin>
				<Particles kind="dust" count={260} opacity={0.6} />
			</Scene3D>
			<SafeArea justify="center" align="start" gap={18} style={{width: '46%'}}>
				<Animate in="fade" out="fade" delay={14}>
					<Eyebrow>New scent</Eyebrow>
				</Animate>
				<Headline text="Amber Hour" delay={18} size={t.caps ? 110 : 132} />
				<Sub delay={32}>Warm amber, cedar and a trace of rose.</Sub>
			</SafeArea>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- card

const CardDemo: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill>
			<Scene3D camera={{preset: 'hero', target: [-2.2, 0, 0]}} lights={t.dark ? 'dramatic' : 'studio'}>
				<Turntable from={-24} to={336} delay={6} tilt={-8} float={10} enter="rise">
					<Card3D width={3.4} />
				</Turntable>
			</Scene3D>
			<SafeArea justify="center" align="start" gap={18} style={{width: '44%'}}>
				<Animate in="fade" out="fade" delay={14}>
					<Eyebrow>Nexa Pay</Eyebrow>
				</Animate>
				<Headline text="Pay with a tap." delay={18} />
				<Sub delay={30}>Contactless at every till, online in one click.</Sub>
			</SafeArea>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- 3D type

const TitleSub: React.FC<{text: string; delay: number; bottom?: number}> = ({text, delay, bottom = 250}) => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: Math.max(safe.y, bottom * unit)}}>
			<Animate in="rise" out="fade" delay={delay}>
				<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 40 * unit, color: t.colors.muted, letterSpacing: '0.01em'}}>{text}</div>
			</Animate>
		</AbsoluteFill>
	);
};

const TextDemo: React.FC = () => (
	<AbsoluteFill>
		<Scene3D camera={{preset: 'front', elevation: 6}}>
			<CameraPath
				keys={[
					{at: 0, orbit: {azimuth: -9, elevation: 7}},
					{at: 119, orbit: {azimuth: 9, elevation: 4}},
				]}
				ease={curves.sine}
			/>
			<Particles kind="dust" count={320} opacity={0.7} />
			<Text3D text="Launch Day" size={200} in="rise" out="sink" delay={6} position={[0, 0.35, 0]} />
		</Scene3D>
		<TitleSub text="Tuesday 14 October, 10:00 GMT" delay={34} />
	</AbsoluteFill>
);

const TextMetal: React.FC = () => (
	<AbsoluteFill>
		<Scene3D camera={{preset: 'low', elevation: -6}} lights="dramatic">
			<CameraPath keys={[{at: 0, orbit: {azimuth: 14, elevation: -5, distance: 11.2}}, {at: 119, orbit: {azimuth: -6, elevation: -3, distance: 10}}]} mode="glide" />
			<Particles kind="bokeh" count={40} opacity={0.4} />
			<Text3D text="Nexa Pro" size={230} look="metal" in="extrude" delay={4} duration={44} depth={0.3} bevel={0.03} position={[0, 0.3, 0]} />
			<Bloom strength={0.45} radius={0.35} threshold={0.82} />
		</Scene3D>
		<TitleSub text="The fastest Nexa we have ever made" delay={40} />
	</AbsoluteFill>
);

const TextBangla: React.FC = () => (
	<AbsoluteFill>
		<Scene3D camera={{preset: 'front', elevation: 8}}>
			<CameraPath keys={[{at: 0, orbit: {azimuth: 8, elevation: 9}}, {at: 119, orbit: {azimuth: -6, elevation: 5}}]} ease={curves.sine} />
			<Text3D text="নতুন শুরু" size={210} in="flip" out="sink" delay={6} stagger={10} position={[0, 0.3, 0]} />
		</Scene3D>
		<TitleSub text="পহেলা বৈশাখ ১৪৩৩" delay={34} />
	</AbsoluteFill>
);

const TextVertical: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill>
			<Scene3D camera={{preset: 'front', elevation: 6}}>
				<Particles kind="confetti" count={120} speed={0.8} fadeIn={20} />
				<Text3D text={'Summer\nSale'} size={250} in="drop" delay={4} stagger={14} sideColor={t.colors.accent2} position={[0, 0.9, 0]} />
			</Scene3D>
			<TitleSub text="Up to 40% off, this weekend only" delay={40} bottom={560} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- particles

const ParticlesDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<Scene3D camera="front" lights="none" environment={false} background="spot">
				<CameraPath keys={[{at: 0, position: [-0.5, -0.2, 11]}, {at: 149, position: [0.5, 0.25, 10.2]}]} ease={curves.sine} />
				<Particles kind="bokeh" fadeIn={24} seed="bokeh" />
				<Particles kind="dust" fadeIn={12} seed="dust" />
			</Scene3D>
			<SafeArea justify="center" align="center" gap={20}>
				<Animate in="blur" out="fade" delay={10}>
					<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 116 * unit, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textAlign: 'center', lineHeight: 1.04}}>
						{t.dark ? 'Built for the night shift' : 'Calm by design'}
					</div>
				</Animate>
				<Sub delay={26} width={900}>
					<span style={{display: 'block', textAlign: 'center'}}>
						{t.dark ? 'Dark mode everywhere, and a battery that keeps up.' : 'Fewer pings, clearer days, and focus that lasts.'}
					</span>
				</Sub>
			</SafeArea>
		</AbsoluteFill>
	);
};

const ParticleFields: React.FC = () => {
	const t = useTheme();
	const {unit, width, height} = useStage();
	const kinds = ['stars', 'embers', 'snow'] as const;
	return (
		<AbsoluteFill style={{flexDirection: 'row'}}>
			{kinds.map((k) => (
				<div key={k} style={{position: 'relative', flex: 1, overflow: 'hidden', borderRight: `${2 * unit}px solid ${t.colors.bg}`}}>
					<Scene3D width={width / 3} height={height} camera="front" lights="none" environment={false} background={k === 'snow' ? mix(t.colors.accent, '#0b1020', 0.75) : 'spot'}>
						<Particles kind={k} seed={k} />
					</Scene3D>
					<div style={{position: 'absolute', left: 40 * unit, bottom: 60 * unit, fontFamily: t.type.mono, fontSize: 30 * unit, color: '#ffffff', opacity: 0.85}}>{k}</div>
				</div>
			))}
		</AbsoluteFill>
	);
};

const Celebrate: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill>
			<Scene3D camera={{preset: 'front', elevation: 4}} lights="soft">
				<Particles kind="confetti" fadeIn={10} />
				<Text3D text="10K" size={320} in="drop" delay={6} stagger={8} sideColor={t.colors.accent2} position={[0, 0.45, 0]} />
			</Scene3D>
			<TitleSub text="followers. Thank you for being here." delay={30} bottom={210} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- floating cards

const CardsDemo: React.FC = () => (
	<Scene3D camera="front" lights="soft">
		<CameraPath
			keys={[
				{at: 0, orbit: {azimuth: -4, elevation: 2}, dolly: 1.06, shift: [-0.45, 0.18]},
				{at: 179, orbit: {azimuth: 4, elevation: -1}, dolly: 0.95, shift: [0.45, -0.1]},
			]}
			mode="glide"
		/>
		<FloatingCards delay={4} out="fly" />
	</Scene3D>
);

// ---------------------------------------------------------------- camera path over a 3D chart

const REGIONS = [
	{name: 'Dhaka', value: 4.2},
	{name: 'Lagos', value: 3.1},
	{name: 'Jakarta', value: 5.6},
	{name: 'Lima', value: 2.4},
	{name: 'Warsaw', value: 3.7},
];

const Bar: React.FC<{x: number; value: number; max: number; i: number; name: string}> = ({x, value, max, i, name}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const h = (value / max) * 3.2;
	const k = ramp(frame, 12 + i * 6, 34, curves.out);
	const top = i === 2;
	return (
		<group position={[x, 0, 0]}>
			<group scale={[1, Math.max(0.001, k), 1]}>
				<RoundedBox width={0.9} height={h} depth={0.9} radius={0.12} position={[0, h / 2, 0]} color={top ? t.colors.accent : mix(t.colors.accent, t.dark ? t.colors.surface : '#ffffff', 0.55)} />
			</group>
			<Text3D text={`$${value.toFixed(1)}M`} size={46} depth={0.12} in="rise" delay={30 + i * 6} position={[0, h * k + 0.32, 0.2]} color={t.colors.text} sideColor={t.colors.accent} maxWidth={2} />
			<Text3D text={name} size={38} depth={0.06} in="rise" delay={14 + i * 6} position={[0, 0.02, 0.95]} rotation={[-Math.PI / 2, 0, 0]} color={t.colors.muted} sideColor={t.colors.muted} maxWidth={1.4} />
		</group>
	);
};

const ChartTitle: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<SafeArea justify="start" align="start" gap={10}>
			<Animate in="fade" out="fade" delay={6}>
				<Eyebrow>2025 revenue</Eyebrow>
			</Animate>
			<Animate in="rise" out="fade" delay={10}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 64 * unit, letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>Jakarta leads the year</div>
			</Animate>
		</SafeArea>
	);
};

const CameraDemo: React.FC = () => {
	const max = Math.max(...REGIONS.map((r) => r.value));
	return (
		<AbsoluteFill>
			<Scene3D camera={{preset: 'front', target: [0, 1.2, 0]}} shadows>
				<CameraPath
					keys={[
						{at: 0, orbit: {azimuth: 0, elevation: 8, distance: 13}, target: [0, 1.2, 0]},
						{at: 70, orbit: {azimuth: 32, elevation: 24, distance: 11.5}},
						{at: 100},
						{at: 170, orbit: {azimuth: 8, elevation: 17, distance: 10.8}, target: [0.2, 0.75, 0]},
						{at: 209},
					]}
					handheld={4}
				/>
				<group position={[0, -1.2, 0]}>
					<Floor grid={0.75} fade={6.5} />
					{REGIONS.map((r, i) => (
						<Bar key={r.name} i={i} x={(i - 2) * 1.5} value={r.value} max={max} name={r.name} />
					))}
				</group>
			</Scene3D>
			<ChartTitle />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- svg 3d (no WebGL)

const BadgeFace: React.FC = () => {
	const t = useTheme();
	return (
		<text x={0} y={0} textAnchor="middle" dominantBaseline="central" fill={t.colors.onAccent} style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 64}}>
			NEW
		</text>
	);
};

const Svg3dDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Svg3D shape="star" x={-600} y={-20} size={300} depth={70} delay={4} color={t.dark ? t.colors.highlight : t.colors.accent2} />
			<Svg3D shape="badge" x={-200} y={-20} size={320} depth={50} delay={10} turnFrom={25} turnTo={-25} color={t.colors.accent}>
				<BadgeFace />
			</Svg3D>
			<Svg3D shape="heart" x={200} y={-10} size={300} depth={70} delay={16} color={t.colors.negative} />
			<Svg3D shape="hexagon" x={600} y={-20} size={300} depth={80} delay={22} turnFrom={-40} turnTo={10} color={t.colors.positive} />
			<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 150 * unit}}>
				<Animate in="rise" out="fade" delay={36}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 36 * unit, color: t.colors.muted}}>Fresh picks, every Friday</div>
				</Animate>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

export const demos: DemoDef[] = [
	{id: 'DemoThreeProduct', component: themed('studio', ProductDemo), durationInFrames: 150},
	{id: 'DemoThreeProductMidnight', component: themed('midnight', ProductApp), durationInFrames: 150},
	{id: 'DemoThreeProductVertical', component: themed('studio', ProductVertical), durationInFrames: 150, width: 1080, height: 1920},
	{id: 'DemoThreeCard', component: themed('studio', CardDemo), durationInFrames: 150},
	{id: 'DemoThreeModel', component: themed('luxury', ModelDemo), durationInFrames: 150},
	{id: 'DemoThreeText', component: themed('studio', TextDemo), durationInFrames: 120},
	{id: 'DemoThreeTextMetal', component: themed('midnight', TextMetal), durationInFrames: 120},
	{id: 'DemoThreeTextBangla', component: themed('dhaka', TextBangla), durationInFrames: 120},
	{id: 'DemoThreeTextVertical', component: themed('playful', TextVertical), durationInFrames: 120, width: 1080, height: 1920},
	{id: 'DemoThreeParticles', component: themed('midnight', ParticlesDemo), durationInFrames: 150},
	{id: 'DemoThreeParticlesLight', component: themed('studio', ParticlesDemo), durationInFrames: 150},
	{id: 'DemoThreeParticleKinds', component: themed('midnight', ParticleFields), durationInFrames: 90},
	{id: 'DemoThreeConfetti', component: themed('playful', Celebrate), durationInFrames: 120},
	{id: 'DemoThreeCards', component: themed('studio', CardsDemo), durationInFrames: 180},
	{id: 'DemoThreeCardsMidnight', component: themed('midnight', CardsDemo), durationInFrames: 180},
	{id: 'DemoThreeCardsVertical', component: themed('fresh', CardsDemo), durationInFrames: 180, width: 1080, height: 1920},
	{id: 'DemoThreeCamera', component: themed('studio', CameraDemo), durationInFrames: 210},
	{id: 'DemoThreeSvg3d', component: themed('studio', Svg3dDemo), durationInFrames: 120},
	{id: 'DemoThreeSvg3dMidnight', component: themed('midnight', Svg3dDemo), durationInFrames: 120},
];
