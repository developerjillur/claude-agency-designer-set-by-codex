import React from 'react';
import {AbsoluteFill, Img, Sequence, Series, staticFile} from 'remotion';
import {SafeArea, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName, type ThemeSpec} from '../kit/core';
import {Animate, Stagger} from '../kit/motion';
import {
	Badge,
	Blob,
	BlobMask,
	Border,
	Card,
	Cell,
	Center,
	EffectGround,
	Frame,
	FullBleed,
	Gradient,
	Grain,
	Grid,
	Ground,
	LightSweep,
	Mesh,
	Panel,
	Paper,
	Pattern,
	Pill,
	Ring,
	Scrim,
	Sparkle,
	Split,
	Squiggle,
	Stack,
	StatSplit,
	Spotlight,
	Vignette,
	brandTheme,
	contrast,
	ensureContrast,
	mix,
	readableOn,
	useLayout,
	withAlpha,
	type GrainBlend,
} from '../kit/design';

// ---------------------------------------------------------------- demo scaffolding

type TileSpec = {theme: ThemeName | ThemeSpec; label: string; node: React.ReactNode; vw?: number; vh?: number};

/**
 * A grid of tiles, each a full virtual stage (a Sequence with its own width and height, so useStage() inside sees a
 * real 1920x1080 or 1080x1920 frame) scaled down into its cell, with its own theme and a label.
 */
const Tiles: React.FC<{cols: number; rows: number; tiles: TileSpec[]; gap?: number; bg?: string}> = ({cols, rows, tiles, gap = 14, bg = '#16171a'}) => {
	const {width, height, durationInFrames} = useStage();
	const vw0 = tiles[0]?.vw ?? 1920;
	const vh0 = tiles[0]?.vh ?? 1080;
	const cellW = Math.min((width - gap * (cols + 1)) / cols, ((height - gap * (rows + 1)) / rows) * (vw0 / vh0));
	const cellH = cellW * (vh0 / vw0);
	const ox = (width - (cols * cellW + (cols - 1) * gap)) / 2;
	const oy = (height - (rows * cellH + (rows - 1) * gap)) / 2;
	return (
		<AbsoluteFill style={{background: bg}}>
			{tiles.map((tile, i) => {
				const vw = tile.vw ?? vw0;
				const vh = tile.vh ?? vh0;
				const s = Math.min(cellW / vw, cellH / vh);
				const x = ox + (i % cols) * (cellW + gap) + (cellW - vw * s) / 2;
				const y = oy + Math.floor(i / cols) * (cellH + gap) + (cellH - vh * s) / 2;
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y, width: vw * s, height: vh * s, overflow: 'hidden'}}>
						<Sequence width={vw} height={vh} durationInFrames={durationInFrames} style={{scale: String(s), transformOrigin: '0 0'}}>
							<ThemeProvider theme={tile.theme}>{tile.node}</ThemeProvider>
						</Sequence>
						<div style={{position: 'absolute', left: 8, top: 8, padding: '3px 9px', borderRadius: 6, background: 'rgba(0,0,0,0.72)', color: '#fff', fontFamily: 'ui-monospace, Menlo, monospace', fontSize: 17}}>
							{tile.label}
						</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

const display = (t: ReturnType<typeof useTheme>, size: number, unit: number): React.CSSProperties => ({
	fontFamily: t.type.display,
	fontWeight: t.weights.display,
	fontSize: size * unit,
	lineHeight: 1.02,
	letterSpacing: `${t.tracking.display}em`,
	textTransform: t.caps ? 'uppercase' : 'none',
});

const body = (t: ReturnType<typeof useTheme>, size: number, unit: number): React.CSSProperties => ({
	fontFamily: t.type.body,
	fontWeight: t.weights.body,
	fontSize: size * unit,
	lineHeight: 1.3,
});

/** A headline and a line of body copy in the theme's type, inside the safe area. */
const Copy: React.FC<{title: string; line?: string; align?: 'start' | 'center'; justify?: 'start' | 'center' | 'end'; delay?: number; size?: number}> = ({title, line, align = 'start', justify = 'center', delay = 0, size = 104}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<SafeArea justify={justify} align={align} gap={26}>
			<Animate in="rise" delay={delay}>
				<div style={{...display(t, size, unit), color: t.colors.text, maxWidth: 1300 * unit, textAlign: align === 'center' ? 'center' : 'left', textWrap: 'balance'}}>{title}</div>
			</Animate>
			{line ? (
				<Animate in="rise" delay={delay + 6}>
					<div style={{...body(t, 42, unit), color: t.colors.muted, maxWidth: 1100 * unit, textAlign: align === 'center' ? 'center' : 'left'}}>{line}</div>
				</Animate>
			) : null}
		</SafeArea>
	);
};

/** The safe area outlined faintly, to check layouts against it on the contact sheets. */
const SafeOutline: React.FC = () => {
	const {safe, unit} = useStage();
	return <div style={{position: 'absolute', left: safe.x, top: safe.y, width: safe.w, height: safe.h, outline: `${2 * unit}px dashed rgba(255, 0, 90, 0.35)`, pointerEvents: 'none'}} />;
};

// ---------------------------------------------------------------- grounds

const Grounds: React.FC = () => (
	<Tiles
		cols={3}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'studio: lit', node: <Ground><Copy title="Every frame stands on light" line="One source above the frame, a soft falloff." /></Ground>},
			{theme: 'midnight', label: 'midnight: spot', node: <Ground kind="spot"><Copy title="Ship it tonight" line="A pool of light behind the subject." align="center" /></Ground>},
			{theme: 'vox', label: 'vox: band', node: <Ground kind="band" split={0.7}><Copy title="The price of rice, 2016 to 2026" line="A floor band gives the frame a horizon." /></Ground>},
			{theme: 'luxury', label: 'luxury: lit', node: <Ground><Copy title="Maison Aurele" line="Autumn collection, Paris" align="center" /></Ground>},
			{theme: 'dhaka', label: 'dhaka: band vertical', node: <Ground kind="band" direction="vertical" split={0.62}><Copy title="ঢাকার বাজারে নতুন দাম" line="চাল, ডাল আর তেলের দাম এক নজরে" /></Ground>},
			{theme: 'swiss', label: 'swiss: solid', node: <Ground kind="solid"><Copy title="Form follows function" line="Flat is a choice: the grid carries the page." /></Ground>},
		]}
	/>
);

const Gradients: React.FC = () => (
	<Tiles
		cols={3}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'studio: linear', node: <Gradient><Copy title="A tinted wash" line="Accent to ground to accent2, in OKLab." /></Gradient>},
			{theme: 'fresh', label: 'fresh: radial', node: <Gradient kind="radial"><Copy title="Fresh start" line="A radial pool from the accent." align="center" /></Gradient>},
			{theme: 'neon', label: 'neon: conic, drift 12/s', node: <Gradient kind="conic" drift={12}><Copy title="Night mode" line="A fan of colour rising from below." align="center" /></Gradient>},
			{theme: 'keynote', label: 'keynote: linear, drift 6/s', node: <Gradient drift={6}><Copy title="Quiet power" line="The angle drifts six degrees a second." /></Gradient>},
			{theme: 'studio', label: 'coral to blue, sRGB (grey dip)', node: <Gradient colors={['#FF6B6B', '#2E86AB']} angle={90} space="srgb"><div /></Gradient>},
			{theme: 'studio', label: 'coral to blue, OKLab', node: <Gradient colors={['#FF6B6B', '#2E86AB']} angle={90}><div /></Gradient>},
		]}
	/>
);

const MeshDemo: React.FC = () => (
	<Tiles
		cols={2}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'studio', node: <Mesh><Copy title="Soft colour, slow drift" line="Five blobs on seeded noise." /></Mesh>},
			{theme: 'midnight', label: 'midnight + glass card', node: (
				<Mesh>
					<Center>
						<Card variant="glass" padding={[40, 56]}>
							<div style={{fontFamily: 'Inter', fontSize: 30, opacity: 0.7}}>Launch week</div>
							<div style={{fontSize: 72, fontWeight: 800, letterSpacing: '-0.03em'}}>Version 4.0</div>
						</Card>
					</Center>
				</Mesh>
			)},
			{theme: 'fresh', label: 'fresh, speed 2', node: <Mesh speed={2}><Copy title="Fresh greens" line="Twice the drift speed." /></Mesh>},
			{theme: 'neon', label: 'neon', node: <Mesh><Copy title="Afterglow" line="Cyan and magenta, softened into the ground." align="center" /></Mesh>},
		]}
	/>
);

const Effects: React.FC = () => (
	<Tiles
		cols={3}
		rows={2}
		tiles={[
			{theme: 'corporate', label: 'corporate: blueprint', node: <EffectGround kind="blueprint"><Copy title="System architecture" line="Two grids, fine and coarse, panning slowly." /></EffectGround>},
			{theme: 'fresh', label: 'fresh: liquid, loop', node: <EffectGround kind="liquid" loop><Copy title="Flow state" line="Liquid contour bands that loop." align="center" /></EffectGround>},
			{theme: 'playful', label: 'playful: waves, loop', node: <EffectGround kind="waves" loop><Copy title="Summer camp 2026" line="Waves drawn at double density." /></EffectGround>},
			{theme: 'retro', label: 'retro: starburst', node: <EffectGround kind="starburst" contrast={0.3}><Copy title="Grand opening" line="Rays turning four degrees a second." align="center" /></EffectGround>},
			{theme: 'data', label: 'data: contours', node: <EffectGround kind="contours"><Copy title="Where the rain falls" line="Topographic lines drifting east." /></EffectGround>},
			{theme: 'neon', label: 'neon: floor', node: <EffectGround kind="floor"><Copy title="Night drive" align="center" justify="start" size={120} /></EffectGround>},
		]}
	/>
);

// ---------------------------------------------------------------- textures

const SpotBoxes: React.FC = () => {
	const t = useTheme();
	const {safe, unit} = useStage();
	const w = 460 * unit;
	const h = 180 * unit;
	const pad = 26 * unit;
	const y = safe.y + (safe.h - h) / 2;
	const xs = [safe.x, safe.x + (safe.w - w) / 2, safe.x + safe.w - w];
	const box = (i: number) => ({x: xs[i] - pad, y: y - pad, w: w + 2 * pad, h: h + 2 * pad});
	return (
		<Ground>
			<SafeArea row justify="space-between" align="center">
				{['Draft', 'Review', 'Publish'].map((s, i) => (
					<Card key={s} width={460} height={180} padding={40}>
						<div style={{...body(t, 26, unit), color: t.colors.muted}}>Step {i + 1}</div>
						<div style={{...display(t, 56, unit), textTransform: 'none'}}>{s}</div>
					</Card>
				))}
			</SafeArea>
			<Spotlight rect={box(0)} toRect={box(1)} moveAt={36} corner={t.radius + 12} />
		</Ground>
	);
};

const Textures: React.FC = () => (
	<Tiles
		cols={3}
		rows={3}
		gap={10}
		tiles={[
			{theme: 'vox', label: 'vox: Paper + grid 106', node: <Paper grid={106}><Copy title="Paper, fibres and a grid" line="The paper shader on a Solid." /></Paper>},
			{theme: 'whiteboard', label: 'whiteboard: Paper rules + margin', node: <Paper rules={56} margin="#E4312B" color="#FBFAF6"><Copy title="Notes from the lab" line="Ruled lines and a margin." /></Paper>},
			{theme: 'vox', label: 'vox: Paper, boil every 8 frames', node: <Paper boil={8} fibers={0.4} crumples={0.3}><Copy title="Stop-motion paper" line="A new sheet every 8 frames." /></Paper>},
			{theme: 'studio', label: 'studio: Spotlight box, moves at 36', node: <SpotBoxes />},
			{theme: 'keynote', label: 'keynote: Spotlight round, travels', node: (
				<Ground>
					<Copy title="Two ideas, one at a time" line="The veil is the ground's own colour." />
					<Spotlight at={[0.25, 0.47]} to={[0.62, 0.47]} radius={420} moveAt={40} />
				</Ground>
			)},
			{theme: 'midnight', label: 'midnight: LightSweep on a card, frame 20', node: (
				<Ground kind="spot">
					<Center>
						<LightSweep at={20} radius={20}>
							<Card padding={[56, 80]} elevation={4}>
								<div style={{fontSize: 34, opacity: 0.7}}>Annual plan</div>
								<div style={{fontSize: 110, fontWeight: 800, letterSpacing: '-0.04em'}}>$96</div>
							</Card>
						</LightSweep>
					</Center>
				</Ground>
			)},
			{theme: 'trailer', label: 'trailer: grain 0.1 + vignette 0.55', node: <Ground><Copy title="Coming this winter" align="center" /></Ground>},
			{theme: 'midnight', label: 'Vignette 0 / 0.3 / 0.6', node: (
				<AbsoluteFill style={{flexDirection: 'row'}}>
					{[0, 0.3, 0.6].map((a) => (
						<div key={a} style={{flex: 1, position: 'relative', background: '#6f7a8c'}}>
							<Vignette amount={a} color="#000" />
						</div>
					))}
				</AbsoluteFill>
			)},
			{theme: 'retro', label: 'retro: grain 0.12 at 12 plates a second', node: <Ground kind="spot"><Copy title="Late night radio" align="center" /></Ground>},
		]}
	/>
);

const PaperHalf: React.FC<{side: 'left' | 'right'; children: React.ReactNode}> = ({side, children}) => (
	<div style={{position: 'absolute', top: 0, bottom: 0, width: '50%', left: side === 'left' ? 0 : '50%', overflow: 'hidden'}}>
		<div style={{position: 'absolute', top: 0, height: '100%', width: '200%', left: side === 'left' ? 0 : '-100%'}}>{children}</div>
	</div>
);

/** Paper at true size: the shader on the left, the CSS fallback on the right. */
const PaperDemo: React.FC = () => (
	<ThemeProvider theme="vox">
		<PaperFull />
	</ThemeProvider>
);

const PaperFull: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<PaperHalf side="left">
				<Paper engine="webgl" grid={106} />
			</PaperHalf>
			<PaperHalf side="right">
				<Paper engine="css" grid={106} />
			</PaperHalf>
			<SafeArea justify="space-between" row>
				<div style={{fontFamily: t.type.display, fontWeight: 900, fontSize: 64 * unit, color: t.colors.text}}>webgl</div>
				<div style={{fontFamily: t.type.display, fontWeight: 900, fontSize: 64 * unit, color: t.colors.text}}>css</div>
			</SafeArea>
		</AbsoluteFill>
	);
};

/** Grain strength by tone and blend: rows are amounts, columns are tones. */
const GrainDemo: React.FC = () => {
	const tones = ['#f4f4f4', '#d9d7d1', '#8a8a8a', '#3a3a3a', '#101010'];
	const rows: [number, GrainBlend][] = [
		[0.05, 'signed'],
		[0.16, 'signed'],
		[0.3, 'signed'],
		[0.16, 'overlay'],
	];
	return (
		<AbsoluteFill style={{display: 'flex', flexDirection: 'column'}}>
			{rows.map(([a, b]) => (
				<div key={`${a}${b}`} style={{flex: 1, display: 'flex', position: 'relative'}}>
					{tones.map((tone) => (
						<div key={tone} style={{flex: 1, position: 'relative', overflow: 'hidden', background: tone}}>
							<Grain amount={a} blend={b} />
						</div>
					))}
					<div style={{position: 'absolute', left: 16, top: 16, padding: '4px 10px', background: 'rgba(0,0,0,0.7)', color: '#fff', font: '22px ui-monospace, Menlo, monospace', borderRadius: 6}}>
						{b} {a}
					</div>
				</div>
			))}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- patterns

const Patterns: React.FC = () => (
	<Tiles
		cols={3}
		rows={3}
		gap={10}
		tiles={[
			{theme: 'studio', label: 'grid, fade center', node: <Ground><Pattern kind="grid" fade="center" /><Copy title="Grid" size={90} /></Ground>},
			{theme: 'midnight', label: 'dots, fade edges, drift', node: <Ground><Pattern kind="dots" fade="edges" drift={[0, -14]} /><Copy title="Dots" align="center" size={90} /></Ground>},
			{theme: 'swiss', label: 'cross', node: <Ground kind="solid"><Pattern kind="cross" /><Copy title="Crosses" size={90} /></Ground>},
			{theme: 'brutalist', label: 'stripes, fade right', node: <Ground kind="solid"><Pattern kind="stripes" fade="right" color={withAlpha('#FF4F00', 0.22)} /><Copy title="Stripes" size={90} /></Ground>},
			{theme: 'editorial', label: 'rules', node: <Ground><Pattern kind="rules" /><Copy title="Ruled page" size={90} /></Ground>},
			{theme: 'playful', label: 'checker', node: <Ground><Pattern kind="checker" /><Copy title="Checker" size={90} /></Ground>},
			{theme: 'vox', label: 'halftone, fade bottom', node: <Paper><Pattern kind="halftone" fade="bottom" color="#FF8900" /><Copy title="Halftone" size={90} /></Paper>},
			{theme: 'retro', label: 'halftone, fade right, accent2', node: <Ground><Pattern kind="halftone" fade="right" color="#3DE0F5" opacity={0.45} /><Copy title="Night print" size={90} /></Ground>},
			{theme: 'corporate', label: 'grid 120 + dots, fade top', node: <Ground><Pattern kind="grid" size={120} fade="top" /><Pattern kind="dots" size={40} fade="bottom" /><Copy title="Layered" size={90} /></Ground>},
		]}
	/>
);

// ---------------------------------------------------------------- cards and surfaces

const CardRow: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const title = (s: string) => <div style={{...display(t, 44, unit), fontSize: 44 * unit, textTransform: 'none'}}>{s}</div>;
	const line = (s: string) => <div style={{...body(t, 27, unit), color: t.colors.muted, marginTop: 10 * unit}}>{s}</div>;
	const items: [React.ComponentProps<typeof Card>['variant'], string, string][] = [
		['solid', 'Solid', 'Surface, hairline, lift'],
		['outline', 'Outline', 'For secondary items'],
		['glass', 'Glass', 'Only over a moving ground'],
		['paper', 'Paper', 'Collage and notes'],
		['tonal', 'Tonal', 'Flat grouping'],
	];
	return (
		<SafeArea row justify="space-between" align="center">
			{items.map(([v, a, b], i) => (
				<Animate key={v} in="rise" delay={4 + i * 4}>
					<Card variant={v} width={316} height={300} tilt={v === 'paper' ? -2 : 0}>
						{title(a)}
						{line(b)}
						<div style={{position: 'absolute', left: 44 * unit, bottom: 36 * unit}}>
							<Pill size={24} variant={v === 'tonal' ? 'solid' : 'soft'}>{v}</Pill>
						</div>
					</Card>
				</Animate>
			))}
		</SafeArea>
	);
};

const Cards: React.FC = () => (
	<Tiles
		cols={1}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'studio: Card variants over a Mesh', node: <Mesh><CardRow /></Mesh>},
			{theme: 'midnight', label: 'midnight: Card variants over a Mesh', node: <Mesh><CardRow /></Mesh>},
		]}
	/>
);

const ElevationRow: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<SafeArea gap={90} justify="center">
			<div style={{display: 'flex', gap: 48 * unit}}>
				{[0, 1, 2, 3, 4, 5].map((lv) => (
					<Card key={lv} elevation={lv} width={230} height={230} padding={30}>
						<div style={{...body(t, 26, unit), color: t.colors.muted}}>elevation</div>
						<div style={{...display(t, 96, unit), textTransform: 'none'}}>{lv}</div>
					</Card>
				))}
			</div>
			<Stack dir="row" gap={22} align="center" wrap>
				<Pill variant="soft">Design</Pill>
				<Pill variant="solid" dot>Live now</Pill>
				<Pill variant="outline">Beta</Pill>
				<Pill variant="soft" color={t.colors.positive} dot>Shipped</Pill>
				<Pill variant="soft" color={t.colors.negative}>Blocked</Pill>
				<Badge>NEW</Badge>
				<Badge variant="soft" color={t.colors.positive}>+24%</Badge>
				<Badge variant="outline">4.9</Badge>
				<Pill caps variant="soft" color={t.colors.accent2}>Bangla: বাংলা</Pill>
			</Stack>
		</SafeArea>
	);
};

const Elevation: React.FC = () => (
	<Tiles
		cols={1}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'studio: elevation 0 to 5, pills, badges', node: <Ground><ElevationRow /></Ground>},
			{theme: 'midnight', label: 'midnight: elevation 0 to 5 (lighter surfaces), pills, badges', node: <Ground><ElevationRow /></Ground>},
		]}
	/>
);

const PanelContent: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const rows = [
		['Checkout redesign', 'In review', t.colors.accent2],
		['Faster search', 'Shipped', t.colors.positive],
		['Dark mode', 'In progress', t.colors.accent],
		['Offline sync', 'Blocked', t.colors.negative],
	] as const;
	return (
		<div style={{padding: `${36 * unit}px ${44 * unit}px`, display: 'flex', flexDirection: 'column', gap: 22 * unit}}>
			<div style={{...display(t, 46, unit), textTransform: 'none'}}>Roadmap, week 38</div>
			{rows.map(([name, state, c]) => (
				<div key={name} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: `${20 * unit}px 0`, borderTop: `${unit}px solid ${withAlpha(t.colors.text, 0.08)}`}}>
					<div style={{...body(t, 30, unit), fontWeight: t.weights.strong}}>{name}</div>
					<Pill size={24} color={c} dot>
						{state}
					</Pill>
				</div>
			))}
		</div>
	);
};

const Surfaces: React.FC = () => (
	<Tiles
		cols={2}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'FullBleed + Scrim (auto, bottom-left)', node: (
				<FullBleed src={staticFile('design/landscape.jpg')} focus={[0.62, 0.55]}>
					<Pill variant="glass" size={26}>Field notes</Pill>
					<div style={{fontFamily: 'Inter', fontWeight: 800, fontSize: 96, lineHeight: 1, letterSpacing: '-0.035em'}}>Into the hills</div>
					<div style={{fontFamily: 'Inter', fontSize: 38, opacity: 0.85}}>A weekend on foot, 42 km</div>
				</FullBleed>
			)},
			{theme: 'vox', label: 'Frame: mat, polaroid, line', node: (
				<Paper grid={106}>
					<SafeArea row justify="center" align="center" gap={70}>
						<Frame variant="mat" width={420} height={300} tilt={-3}>
							<Img src={staticFile('design/landscape.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
						</Frame>
						<Frame variant="polaroid" width={360} height={360} tilt={4} caption="Rangamati, May">
							<Img src={staticFile('design/dusk.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
						</Frame>
						<Frame variant="line" width={380} height={300} radius={20}>
							<Img src={staticFile('design/landscape.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '70% 50%'}} />
						</Frame>
					</SafeArea>
				</Paper>
			)},
			{theme: 'luxury', label: 'Border: double rule + corners, drawn on', node: (
				<Ground>
					<Border kind="double" />
					<Border kind="corners" inset={80} length={70} color="#C9A45C" delay={10} />
					<Copy title="Maison Aurele" line="The winter atelier opens on 12 December" align="center" delay={14} />
				</Ground>
			)},
			{theme: 'fresh', label: 'Panel (no device) with a list', node: (
				<Ground kind="band" split={0.72}>
					<Center>
						<Animate in="rise">
							<Panel width={1180} height={640} title="Roadmap" bar="dots">
								<PanelContent />
							</Panel>
						</Animate>
					</Center>
				</Ground>
			)},
		]}
	/>
);

// ---------------------------------------------------------------- layouts (one scene per system, per frame shape)

const PlanCard: React.FC<{name: string; price: string; note: string; hero?: boolean}> = ({name, price, note, hero}) => {
	const t = useTheme();
	const {unit} = useStage();
	const {shape} = useLayout();
	const wide = shape === 'wide';
	const tall = shape === 'tall';
	return (
		<Card variant={hero ? 'solid' : 'outline'} elevation={hero ? 3 : 0} padding={tall ? [30, 40] : wide ? [52, 52] : [36, 32]} style={{height: '100%'}}>
			<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 * unit}}>
				<div style={{...body(t, wide ? 38 : 32, unit), fontWeight: t.weights.strong}}>{name}</div>
				{hero ? <Badge size={wide ? 24 : 20}>POPULAR</Badge> : null}
			</div>
			<div style={{...display(t, wide ? 140 : tall ? 92 : 96, unit), textTransform: 'none', marginTop: 16 * unit, fontVariantNumeric: 'tabular-nums'}}>{price}</div>
			<div style={{...body(t, wide ? 30 : 27, unit), color: t.colors.muted, marginTop: 10 * unit}}>{note}</div>
		</Card>
	);
};

const SceneGrid: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const {tall} = useLayout();
	return (
		<Ground>
			<SafeArea justify="center" gap={tall ? 44 : 56}>
				<Animate in="rise">
					<div style={{...display(t, tall ? 96 : 110, unit), color: t.colors.text}}>Pick a plan</div>
				</Animate>
				<Grid columns={{wide: 3, square: 3, portrait: 1, tall: 1}} gap={{wide: 36, square: 22, tall: 24}}>
					<Stagger in="rise" each={5} delay={6}>
						<PlanCard name="Starter" price="$0" note="One project, community help" />
						<PlanCard name="Team" price="$24" note="Per seat a month, billed yearly" hero />
						<PlanCard name="Studio" price="$99" note="Unlimited projects and renders" />
					</Stagger>
				</Grid>
			</SafeArea>
		</Ground>
	);
};

const SceneStat: React.FC = () => (
	<Ground kind="spot">
		<Animate in="fade" duration={12}>
			<StatSplit value="87%" label="of viewers start a video with the sound off" note="Sample figure for this demo" />
		</Animate>
	</Ground>
);

const SceneBleed: React.FC = () => {
	const {tall} = useLayout();
	return (
		<FullBleed src={staticFile('design/landscape.jpg')} focus={[0.66, 0.5]}>
			<Animate in="rise">
				<Pill variant="glass" size={26}>Field notes</Pill>
			</Animate>
			<Animate in="rise" delay={4}>
				<div style={{fontFamily: 'Inter', fontWeight: 800, fontSize: tall ? 110 : 104, lineHeight: 1, letterSpacing: '-0.035em'}}>Into the hills</div>
			</Animate>
			<Animate in="rise" delay={8}>
				<div style={{fontFamily: 'Inter', fontSize: 40, opacity: 0.88}}>A weekend on foot, 42 km over three ridges</div>
			</Animate>
		</FullBleed>
	);
};

const SceneSplit: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const {tall} = useLayout();
	const block = (k: string, big: string, s: string, delay: number) => (
		<Animate in="rise" delay={delay}>
			<div style={{...body(t, 30, unit), fontWeight: t.weights.strong, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', opacity: 0.75}}>{k}</div>
			<div style={{...display(t, tall ? 220 : 280, unit), lineHeight: 0.9, textTransform: 'none', margin: `${14 * unit}px 0`, fontVariantNumeric: 'tabular-nums'}}>{big}</div>
			<div style={{...body(t, tall ? 40 : 42, unit), maxWidth: 560 * unit, textWrap: 'balance'}}>{s}</div>
		</Animate>
	);
	return (
		<Ground>
			<Split area="full" seam="hard" ratio={0.5}>
				{block('Before', '14', 'steps to publish a video', 0)}
				{block('After', '3', 'steps, and the rest is automatic', 8)}
			</Split>
		</Ground>
	);
};

const SceneCenter: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const {tall} = useLayout();
	return (
		<Ground>
			<Center>
				<Animate in="mask">
					<div style={{...display(t, tall ? 120 : 132, unit), color: t.colors.text}}>Make the first frame worth a pause.</div>
				</Animate>
				<Animate in="fade" delay={14}>
					<div style={{...body(t, 38, unit), color: t.colors.muted}}>Centred with a readable measure, lifted to the optical middle.</div>
				</Animate>
			</Center>
		</Ground>
	);
};

const SCENES: [ThemeName, React.FC][] = [
	['studio', SceneGrid],
	['midnight', SceneStat],
	['studio', SceneBleed],
	['fresh', SceneSplit],
	['editorial', SceneCenter],
];

const Layouts: React.FC = () => (
	<Series>
		{SCENES.map(([theme, Scene], i) => (
			<Series.Sequence key={i} durationInFrames={60}>
				<ThemeProvider theme={theme}>
					<Scene />
					<SafeOutline />
				</ThemeProvider>
			</Series.Sequence>
		))}
	</Series>
);

// ---------------------------------------------------------------- shapes

const ShapesScene: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<Ground>
			<SafeArea row justify="space-between" align="center">
				<div style={{position: 'relative', width: 720 * unit, height: 780 * unit}}>
					<Ring size={170} weight={7} dashed delay={26} color={t.colors.accent2} style={{position: 'absolute', left: 30 * unit, top: 40 * unit}} />
					<Blob size={600} seed="hero" style={{position: 'absolute', left: 150 * unit, top: 150 * unit}} />
					<BlobMask width={520} height={600} seed="photo" style={{position: 'absolute', left: 80 * unit, top: 70 * unit}}>
						<Img src={staticFile('design/landscape.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '65% 50%'}} />
					</BlobMask>
					<Sparkle size={70} delay={24} style={{position: 'absolute', left: 590 * unit, top: 60 * unit}} />
					<Sparkle size={42} delay={30} rotate={20} style={{position: 'absolute', left: 660 * unit, top: 150 * unit}} />
				</div>
				<div style={{display: 'flex', flexDirection: 'column', gap: 40 * unit, width: 820 * unit}}>
					<div>
						<div style={{...display(t, 96, unit), color: t.colors.text}}>A trip worth taking</div>
						<Squiggle width={430} delay={16} style={{marginTop: 8 * unit}} />
					</div>
					<div style={{display: 'flex', alignItems: 'center', gap: 36 * unit}}>
						<Ring size={210} weight={8} delay={20}>
							<div style={{...display(t, 76, unit), color: t.colors.text, fontVariantNumeric: 'tabular-nums'}}>42</div>
						</Ring>
						<div style={{...body(t, 38, unit), color: t.colors.muted, maxWidth: 480 * unit}}>kilometres over three ridges, in two days</div>
					</div>
				</div>
			</SafeArea>
		</Ground>
	);
};

const Shapes: React.FC = () => (
	<Tiles
		cols={1}
		rows={2}
		tiles={[
			{theme: 'playful', label: 'playful: Blob, BlobMask, Sparkle, Squiggle, Ring', node: <ShapesScene />},
			{theme: 'midnight', label: 'midnight: the same scene', node: <ShapesScene />},
		]}
	/>
);

// ---------------------------------------------------------------- colour and brand

const Swatch: React.FC<{c: string; w: number; h: number; label?: string; ink?: string}> = ({c, w, h, label, ink}) => (
	<div style={{width: w, height: h, background: c, display: 'flex', alignItems: 'center', justifyContent: 'center', color: ink ?? readableOn(c), font: `600 ${Math.round(h * 0.28)}px Inter, sans-serif`}}>{label}</div>
);

const srgbMix = (a: string, b: string, k: number) => {
	const p = (s: string) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));
	const x = p(a);
	const y = p(b);
	return `rgb(${x.map((v, i) => Math.round(v + (y[i] - v) * k)).join(', ')})`;
};

const BrandSpecimen: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const c = t.colors;
	return (
		<AbsoluteFill style={{background: c.bg, padding: 70 * unit, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
			<div style={{...display(t, 110, unit), color: c.text}}>Brand kit</div>
			<div style={{display: 'flex', gap: 24 * unit, alignItems: 'center'}}>
				<div style={{background: c.accent, color: c.onAccent, padding: `${22 * unit}px ${40 * unit}px`, borderRadius: t.radius * unit, ...body(t, 40, unit), fontWeight: 700}}>Buy now</div>
				<Pill size={40}>Soft accent</Pill>
				<Pill size={40} variant="outline">Outline</Pill>
			</div>
			<div style={{display: 'flex', gap: 10 * unit}}>
				{[c.bg, c.bg2, c.surface, c.line, c.faint, c.muted, c.text, c.accent, c.accent2, c.highlight].map((col, i) => (
					<div key={i} style={{flex: 1, height: 110 * unit, background: col, borderRadius: 10 * unit, border: `${unit}px solid ${withAlpha(c.text, 0.12)}`}} />
				))}
			</div>
		</AbsoluteFill>
	);
};

const ColorLab: React.FC = () => {
	const pairs: [string, string][] = [
		['#2563EB', '#F59E0B'],
		['#E4002B', '#00A884'],
		['#FF6B6B', '#2E86AB'],
	];
	const onColors = ['#2563EB', '#F59E0B', '#FFD60A', '#00A884', '#E4002B', '#111827', '#F5F6F7', '#7C3AED'];
	const weak = ['#F59E0B', '#FFD60A', '#3DDC97', '#5B8CFF'];
	const brands: [string, boolean][] = [
		['#E4002B', false],
		['#00A884', true],
		['#FFD60A', false],
	];
	const cell = 88;
	const label = (s: string) => <div style={{font: '600 22px Inter, sans-serif', color: '#9aa3b2', margin: '0 0 10px'}}>{s}</div>;
	return (
		<AbsoluteFill style={{background: '#101216', padding: 50, boxSizing: 'border-box', flexDirection: 'row', gap: 50}}>
			<div style={{display: 'flex', flexDirection: 'column', gap: 26, width: 1060}}>
				{label('mix() in OKLab (top) against plain sRGB (bottom)')}
				{pairs.map(([a, b]) => (
					<div key={a + b} style={{display: 'flex', flexDirection: 'column', gap: 4}}>
						<div style={{display: 'flex'}}>
							{Array.from({length: 12}, (_, i) => (
								<Swatch key={i} c={mix(a, b, i / 11)} w={cell} h={40} />
							))}
						</div>
						<div style={{display: 'flex'}}>
							{Array.from({length: 12}, (_, i) => (
								<Swatch key={i} c={srgbMix(a, b, i / 11)} w={cell} h={40} />
							))}
						</div>
					</div>
				))}
				{label('readableOn(): the better text colour, with the contrast ratio')}
				<div style={{display: 'flex', gap: 8}}>
					{onColors.map((c) => (
						<Swatch key={c} c={c} w={124} h={96} label={`${contrast(readableOn(c), c).toFixed(1)}:1`} />
					))}
				</div>
				{label('ensureContrast(): accent text on white, before and after (min 4.5)')}
				<div style={{display: 'flex', gap: 12, background: '#FFFFFF', padding: 20, borderRadius: 12}}>
					{weak.map((c) => (
						<div key={c} style={{flex: 1, font: '800 34px Inter, sans-serif', lineHeight: 1.3}}>
							<div style={{color: c}}>Aa {contrast(c, '#FFFFFF').toFixed(1)}</div>
							<div style={{color: ensureContrast(c, '#FFFFFF', 4.5)}}>Aa {contrast(ensureContrast(c, '#FFFFFF', 4.5), '#FFFFFF').toFixed(1)}</div>
						</div>
					))}
				</div>
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 16, flex: 1}}>
				{label('brandTheme() from one colour: light, dark, light')}
				{brands.map(([c, dark]) => (
					<div key={c} style={{position: 'relative', height: 300, overflow: 'hidden', borderRadius: 12}}>
						<Sequence width={1920} height={1080} style={{scale: String(300 / 1080), transformOrigin: '0 0'}}>
							<ThemeProvider theme={brandTheme({primary: c, dark})}>
								<BrandSpecimen />
							</ThemeProvider>
						</Sequence>
						<div style={{position: 'absolute', right: 10, top: 10, font: '600 18px ui-monospace, Menlo, monospace', color: '#fff', background: 'rgba(0,0,0,0.6)', padding: '2px 8px', borderRadius: 6}}>{c}</div>
					</div>
				))}
			</div>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- grounds in 9:16

const TallGrounds: React.FC = () => (
	<Tiles
		cols={5}
		rows={1}
		gap={12}
		tiles={[
			{theme: 'studio', label: 'Ground lit', vw: 1080, vh: 1920, node: <Ground><Copy title="Lit from above" line="The same ground in 9:16." size={96} /></Ground>},
			{theme: 'midnight', label: 'Mesh', vw: 1080, vh: 1920, node: <Mesh><Copy title="Launch week" line="Blobs placed by the frame." size={96} /></Mesh>},
			{theme: 'vox', label: 'Paper + grid', vw: 1080, vh: 1920, node: <Paper grid={106}><Copy title="Rice, 2016 to 2026" size={96} /></Paper>},
			{theme: 'neon', label: 'EffectGround floor', vw: 1080, vh: 1920, node: <EffectGround kind="floor"><Copy title="Night drive" justify="start" align="center" size={110} /></EffectGround>},
			{theme: 'retro', label: 'Pattern halftone', vw: 1080, vh: 1920, node: <Ground><Pattern kind="halftone" fade="bottom" color="#FF5E8A" opacity={0.55} /><Copy title="Late night radio" size={96} /></Ground>},
		]}
	/>
);

// ---------------------------------------------------------------- more variants (bento grid, scrims, placements)

const Bento: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const cell = (title: string, line: string, tone?: string) => (
		<Card variant={tone ? 'tonal' : 'solid'} color={tone} style={{height: '100%'}} padding={36}>
			<div style={{...display(t, 52, unit), textTransform: 'none'}}>{title}</div>
			<div style={{...body(t, 28, unit), color: t.colors.muted, marginTop: 8 * unit}}>{line}</div>
		</Card>
	);
	return (
		<Ground>
			<Grid fill columns={{wide: 3, tall: 1}} rows={{wide: 2, tall: 4}} gap={{wide: 28, tall: 20}}>
				<Cell span={{wide: 2, tall: 1}} rowSpan={{wide: 2, tall: 1}}>
					<Card padding={0} style={{height: '100%', overflow: 'hidden'}}>
						<FullBleed src={staticFile('design/landscape.jpg')} push={0} area="box" maxWidth={0.8}>
							<div style={{...display(t, 64, unit), color: '#FFFFFF', textTransform: 'none'}}>Offline maps</div>
						</FullBleed>
					</Card>
				</Cell>
				{cell('4.9', 'App Store rating')}
				{cell('12 GB', 'of trails, saved', t.colors.accent2)}
			</Grid>
		</Ground>
	);
};

const ScrimSides: React.FC = () => (
	<AbsoluteFill style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr'}}>
		{(['top', 'right', 'center', 'full'] as const).map((side) => (
			<div key={side} style={{position: 'relative', overflow: 'hidden'}}>
				<Img src={staticFile('design/landscape.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
				<Scrim side={side} />
				<div style={{position: 'absolute', left: 24, top: 20, font: '700 44px Inter, sans-serif', color: '#fff'}}>{side}</div>
			</div>
		))}
	</AbsoluteFill>
);

const ShapeBits: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<Ground>
			<SafeArea row justify="space-between" align="center">
				<Blob size={360} gradient={[t.colors.accent, t.colors.accent2]} seed="g">
					<div style={{...display(t, 96, unit), color: '#FFFFFF'}}>24</div>
				</Blob>
				<Blob size={300} outline={6} seed="o" color={t.colors.accent} />
				<Ring size={300} weight={10} progress={0.72} color={t.colors.accent2}>
					<div style={{...display(t, 80, unit), color: t.colors.text}}>72%</div>
				</Ring>
				<div style={{display: 'flex', gap: 30 * unit}}>
					<Sparkle size={90} delay={6} twinkle />
					<Sparkle size={56} delay={12} rotate={20} twinkle />
				</div>
			</SafeArea>
		</Ground>
	);
};

const More: React.FC = () => (
	<Tiles
		cols={3}
		rows={2}
		tiles={[
			{theme: 'studio', label: 'Grid fill, rows, Cell spans (bento)', node: <Bento />},
			{theme: 'studio', label: 'Scrim: top, right, center, full', node: <ScrimSides />},
			{theme: 'editorial', label: 'FullBleed tone dark, place top-left', node: (
				<FullBleed src={staticFile('design/landscape.jpg')} tone="dark" place="top-left" focus={[0.5, 0.3]}>
					<div style={{fontFamily: 'Instrument Serif', fontSize: 110, lineHeight: 1}}>The quiet season</div>
					<Pill variant="outline">Travel</Pill>
				</FullBleed>
			)},
			{theme: 'midnight', label: 'FullBleed place left, dusk', node: (
				<FullBleed src={staticFile('design/dusk.jpg')} place="left" focus={[0.3, 0.4]}>
					<Pill variant="glass">Night hikes</Pill>
					<div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 100, lineHeight: 1}}>Walk under the stars</div>
				</FullBleed>
			)},
			{theme: 'neon', label: 'Border brackets + LightSweep on the frame', node: (
				<Ground kind="spot">
					<Border kind="brackets" inset={120} length={80} />
					<Copy title="Level 12 unlocked" align="center" />
					<LightSweep at={10} duration={40} />
				</Ground>
			)},
			{theme: 'playful', label: 'Blob gradient + outline, Ring 72%, Sparkles', node: <ShapeBits />},
		]}
	/>
);

// ---------------------------------------------------------------- the list



export const demos: DemoDef[] = [
	{id: 'DemoDesignGrounds', component: Grounds, durationInFrames: 120},
	{id: 'DemoDesignGradients', component: Gradients, durationInFrames: 120},
	{id: 'DemoDesignMesh', component: MeshDemo, durationInFrames: 180},
	{id: 'DemoDesignGroundsTall', component: TallGrounds, durationInFrames: 90},
	{id: 'DemoDesignEffects', component: Effects, durationInFrames: 120},
	{id: 'DemoDesignTextures', component: Textures, durationInFrames: 90},
	{id: 'DemoDesignPaper', component: PaperDemo, durationInFrames: 30},
	{id: 'DemoDesignGrain', component: GrainDemo, durationInFrames: 30},
	{id: 'DemoDesignPatterns', component: Patterns, durationInFrames: 90},
	{id: 'DemoDesignCards', component: Cards, durationInFrames: 60},
	{id: 'DemoDesignElevation', component: Elevation, durationInFrames: 30},
	{id: 'DemoDesignSurfaces', component: Surfaces, durationInFrames: 60},
	{id: 'DemoDesignMore', component: More, durationInFrames: 60},
	{id: 'DemoDesignLayouts', component: Layouts, durationInFrames: 300},
	{id: 'DemoDesignLayoutsTall', component: Layouts, durationInFrames: 300, width: 1080, height: 1920},
	{id: 'DemoDesignLayoutsSquare', component: Layouts, durationInFrames: 300, width: 1080, height: 1080},
	{id: 'DemoDesignLayoutsFeed', component: Layouts, durationInFrames: 300, width: 1080, height: 1350},
	{id: 'DemoDesignShapes', component: Shapes, durationInFrames: 90},
	{id: 'DemoDesignColor', component: ColorLab, durationInFrames: 1},
];
