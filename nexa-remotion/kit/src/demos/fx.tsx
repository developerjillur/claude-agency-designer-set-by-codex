// fx demos: effect presets, looks, glitch, masks, keying, light and transitions. DemoFxSampleArt draws the
// picture the other demos use (rendered once to public/fx/landscape.jpg with `nrk.py still`).
import React from 'react';
import {AbsoluteFill, Img, Sequence, Solid, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {SafeArea, ThemeProvider, rand, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {
	BlendVideo,
	ChromaKey,
	CrtLook,
	DreamyLook,
	FilmLook,
	GlitchLook,
	GradientMask,
	LEAK_HUES,
	LightLeak,
	NewsprintLook,
	NoirLook,
	Scenes,
	ShapeMask,
	Shine,
	Starburst,
	StopMotionLook,
	TextMask,
	VhsLook,
	WipeMask,
	fx,
	lookEffects,
	makeCubeLut,
	scenesLength,
	tr,
	useLutFile,
	type Fx,
	type FxTransition,
	type LookEngine,
	type SceneSpec,
} from '../kit/fx';

const ridge = (seed: string, base: number, amp: number, step: number, jag: number): string => {
	const pts: string[] = [];
	for (let x = -40; x <= 1960; x += step) {
		const s = Math.sin(x / 310 + rand(`${seed}-a`) * 6) * 0.55 + Math.sin(x / 127 + rand(`${seed}-b`) * 6) * 0.3;
		const y = base - amp * (0.5 + 0.5 * s) - rand(`${seed}-${x}`) * jag;
		pts.push(`${x},${y.toFixed(1)}`);
	}
	return `M-40,1100 L${pts.join(' L')} L1960,1100 Z`;
};

// A conifer silhouette: branch tiers zigzag up both sides to the tip.
const pine = (x: number, baseY: number, h: number, w: number): string => {
	const tiers = 7;
	const left: string[] = [];
	const right: string[] = [];
	for (let i = 0; i < tiers; i++) {
		const t0 = i / tiers;
		const y0 = baseY - h * t0;
		const y1 = baseY - h * (t0 + 0.6 / tiers);
		const half = (w / 2) * (1 - t0 * 0.9);
		left.push(`${x - half},${y0}`, `${x - half * 0.35},${y1}`);
		right.unshift(`${x + half * 0.35},${y1}`, `${x + half},${y0}`);
	}
	return `M${x - 6},${baseY + 40} L${left.join(' L')} L${x},${baseY - h} L${right.join(' L')} L${x + 6},${baseY + 40} Z`;
};

export const SampleArt: React.FC = () => {
	const stars = Array.from({length: 110}).map((_, i) => ({
		x: rand(`sx${i}`) * 1920,
		y: Math.pow(rand(`sy${i}`), 1.6) * 470,
		r: 0.8 + rand(`sr${i}`) * 1.6,
		o: 0.3 + rand(`so${i}`) * 0.6,
	}));
	const pinesLeft = [
		{x: 70, h: 560, w: 190},
		{x: 190, h: 470, w: 170},
		{x: 300, h: 380, w: 140},
		{x: 20, h: 420, w: 150},
		{x: 390, h: 300, w: 110},
	];
	const pinesRight = [
		{x: 1850, h: 590, w: 200},
		{x: 1740, h: 470, w: 170},
		{x: 1650, h: 360, w: 130},
		{x: 1920, h: 450, w: 160},
	];
	return (
		<AbsoluteFill style={{background: '#0e1733'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
				<defs>
					<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#0d1532" />
						<stop offset="0.3" stopColor="#2e2658" />
						<stop offset="0.52" stopColor="#853d6c" />
						<stop offset="0.66" stopColor="#d9665c" />
						<stop offset="0.75" stopColor="#f59d66" />
						<stop offset="0.82" stopColor="#ffd494" />
					</linearGradient>
					<radialGradient id="glow" cx="1180" cy="690" r="640" gradientUnits="userSpaceOnUse">
						<stop offset="0" stopColor="#ffd9a0" stopOpacity="0.9" />
						<stop offset="0.22" stopColor="#ffab70" stopOpacity="0.4" />
						<stop offset="1" stopColor="#ff8a70" stopOpacity="0" />
					</radialGradient>
					<radialGradient id="sun" cx="0.45" cy="0.4" r="0.7">
						<stop offset="0" stopColor="#fffdf4" />
						<stop offset="1" stopColor="#ffe09a" />
					</radialGradient>
					<linearGradient id="far" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#b8708a" />
						<stop offset="1" stopColor="#8f5584" />
					</linearGradient>
					<linearGradient id="mid" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#5d3c74" />
						<stop offset="1" stopColor="#40295c" />
					</linearGradient>
					<linearGradient id="near" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#2c2147" />
						<stop offset="1" stopColor="#1d1734" />
					</linearGradient>
					<linearGradient id="lake" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#f0a06c" />
						<stop offset="0.22" stopColor="#b25a6d" />
						<stop offset="0.6" stopColor="#3b2b5d" />
						<stop offset="1" stopColor="#121834" />
					</linearGradient>
					<linearGradient id="mist" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#ffc2a0" stopOpacity="0" />
						<stop offset="0.5" stopColor="#ffc2a0" stopOpacity="0.32" />
						<stop offset="1" stopColor="#ffc2a0" stopOpacity="0" />
					</linearGradient>
					<radialGradient id="window" cx="0.5" cy="0.5" r="0.5">
						<stop offset="0" stopColor="#ffd98a" stopOpacity="0.9" />
						<stop offset="1" stopColor="#ffb347" stopOpacity="0" />
					</radialGradient>
				</defs>
				<rect width="1920" height="1080" fill="url(#sky)" />
				{stars.map((s, i) => (
					<circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#fff4e2" opacity={s.o} />
				))}
				<rect width="1920" height="1080" fill="url(#glow)" />
				<circle cx="1180" cy="676" r="96" fill="url(#sun)" />
				{[0, 1, 2, 3].map((i) => (
					<path
						key={i}
						d={`M${880 + i * 38},${505 + (i % 2) * 22} q10,-9 20,0 q10,-9 20,0`}
						stroke="#2a1b38"
						strokeWidth="3"
						fill="none"
						strokeLinecap="round"
					/>
				))}
				<path d={ridge('far', 800, 150, 36, 22)} fill="url(#far)" />
				<rect y="770" width="1920" height="100" fill="url(#mist)" />
				<path d={ridge('mid', 850, 110, 28, 26)} fill="url(#mid)" />
				<path d={ridge('near', 885, 55, 22, 12)} fill="url(#near)" />
				<rect y="882" width="1920" height="198" fill="url(#lake)" />
				{Array.from({length: 16}).map((_, i) => {
					const y = 892 + i * 11.5;
					const w = 230 - i * 11 + rand(`rw${i}`) * 60;
					return <rect key={i} x={1180 - w / 2 + (rand(`rx${i}`) - 0.5) * 40} y={y} width={w} height={3.2} rx={1.6} fill="#ffe4b0" opacity={0.85 - i * 0.045} />;
				})}
				{Array.from({length: 22}).map((_, i) => (
					<rect key={i} x={rand(`lx${i}`) * 1800} y={900 + rand(`ly${i}`) * 170} width={60 + rand(`lw${i}`) * 180} height={2} fill="#ffd2b0" opacity={0.12 + rand(`lo${i}`) * 0.12} />
				))}
				<g>
					<circle cx="1492" cy="846" r="46" fill="url(#window)" />
					<path d="M1452,882 L1452,846 L1492,818 L1532,846 L1532,882 Z" fill="#1a1328" />
					<rect x="1482" y="852" width="18" height="16" fill="#ffc86b" />
					<rect x="1480" y="892" width="22" height="30" fill="#ffc86b" opacity="0.28" />
				</g>
				<path d="M-10,1080 L-10,930 Q260,900 520,960 Q700,1010 760,1080 Z" fill="#110c1d" />
				<path d="M1930,1080 L1930,925 Q1700,905 1520,955 Q1400,1000 1380,1080 Z" fill="#110c1d" />
				{pinesLeft.map((p, i) => (
					<path key={`l${i}`} d={pine(p.x, 1000, p.h, p.w)} fill="#0f0a1b" />
				))}
				{pinesRight.map((p, i) => (
					<path key={`r${i}`} d={pine(p.x, 1000, p.h, p.w)} fill="#0f0a1b" />
				))}
			</svg>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- shared pieces

const PHOTO = staticFile('fx/landscape.jpg');
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** The landscape, cover fitted. With effects it becomes a canvas (whole-number size, centred crop). */
const Photo: React.FC<{effects?: Fx[]; zoom?: number; origin?: string; position?: string}> = ({effects, zoom = 1, origin = '50% 50%', position = '50% 50%'}) => {
	const {width, height} = useStage();
	return (
		<AbsoluteFill style={{overflow: 'hidden'}}>
			<Img
				src={PHOTO}
				width={Math.round(width)}
				height={Math.round(height)}
				effects={effects}
				style={{objectFit: 'cover', objectPosition: effects ? undefined : position, scale: String(zoom), transformOrigin: origin}}
			/>
		</AbsoluteFill>
	);
};

/** A small label chip for reviewing demos. */
const Tag: React.FC<{children: React.ReactNode; at?: 'tr' | 'tl' | 'br'}> = ({children, at = 'tr'}) => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const pos: React.CSSProperties =
		at === 'tl' ? {left: safe.x, top: safe.y} : at === 'br' ? {right: safe.x, bottom: safe.y} : {right: safe.x, top: safe.y};
	return (
		<div
			style={{
				position: 'absolute',
				...pos,
				fontFamily: t.type.mono,
				fontSize: 24 * unit,
				color: '#ffffff',
				background: 'rgba(10, 12, 18, 0.66)',
				padding: `${8 * unit}px ${18 * unit}px`,
				borderRadius: 999,
				whiteSpace: 'nowrap',
			}}
		>
			{children}
		</div>
	);
};

// ---------------------------------------------------------------- DemoFxEffects: the presets on one picture

type Cell = {name: string; note: string; make: (f: number, fps: number, cube: string | null) => Fx[]; ground?: string};

const PAGE = 36;

// a LUT made in code: shadows toward teal, highlights toward orange
const TEAL_ORANGE = makeCubeLut((r, g, b) => {
	const y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
	const k = (y - 0.5) * 0.16;
	return [r + k, g + k * 0.25, b - k];
}, 17, 'teal orange');
const INK = '#1c1b19';
const PAPER = '#efe7d6';

const PAGES: {title: string; cells: Cell[]}[] = [
	{
		title: 'Grade and tone',
		cells: [
			{name: "fx.grade('cinematic')", note: 'one colorCorrection pass', make: () => [fx.grade('cinematic')]},
			{name: "fx.grade('warmFilm')", note: 'lifted blacks, warm, softer', make: () => [fx.grade('warmFilm')]},
			{name: "fx.grade('coolNight')", note: 'blue hour', make: () => [fx.grade('coolNight')]},
			{name: "fx.grade('bleach')", note: 'bleach bypass', make: () => [fx.grade('bleach')]},
			{name: 'fx.levels()', note: 'black 0.06, white 0.9, gamma 1.25', make: () => [fx.levels({black: 0.06, white: 0.9, gamma: 1.25})]},
			{name: 'fx.lut(cube)', note: 'warm-film.cube from public/, 17 points', make: (_f, _fps, cube) => (cube ? [fx.lut(cube)] : [])},
		],
	},
	{
		title: 'Print and colour maps',
		cells: [
			{name: 'fx.halftone({source: true})', note: 'dots in the picture colours', ground: PAPER, make: () => [fx.halftone({source: true, size: 9, angle: 30})]},
			{name: 'fx.halftone({ink})', note: 'newsprint dots on paper', ground: PAPER, make: () => [fx.colorCorrection({contrast: 1.2}), fx.halftone({size: 8, ink: INK})]},
			{name: 'fx.duotone()', note: 'smooth two-colour map', make: () => [fx.duotone({dark: '#16193a', light: '#ffc27a'})]},
			{name: 'fx.tritone()', note: 'three-colour map', make: () => [fx.tritone({dark: '#0f2a3f', mid: '#e0527a', light: '#fff0c4'})]},
			{name: 'fx.stencil()', note: 'hard one-bit threshold', make: () => [fx.stencil({dark: '#14213d', light: '#fca311', threshold: 0.3})]},
			{name: 'fx.posterize(4)', note: 'kit effect, 4 levels a channel', make: () => [fx.posterize(4)]},
		],
	},
	{
		title: 'Lens and light',
		cells: [
			{name: 'fx.glow()', note: 'threshold 0.7: only the sun glows', make: () => [fx.glow({threshold: 0.7, radius: 22, intensity: 1.3, color: '#ffd9a0'})]},
			{name: 'fx.chromaticAberration()', note: '8 px RGB split', make: () => [fx.chromaticAberration({amount: 8})]},
			{name: 'fx.zoomBlur()', note: 'punch-in, amount 90 to 0', make: (f) => [fx.zoomBlur({amount: interpolate(f, [0, 28], [90, 0], CLAMP), center: [0.61, 0.62]})]},
			{name: 'fx.tiltShift()', note: 'a miniature focus band', make: () => [fx.tiltShift({center: [0.5, 0.78], blur: 16})]},
			{name: 'fx.scanlines() + fx.barrel()', note: 'CRT glass on a dark ground', ground: '#050505', make: (f) => [fx.scanlines({amount: 0.35, spacing: 5, thickness: 2, offset: f}), fx.barrel(0.22), fx.vignette({amount: 0.5, radius: 0.6})]},
			{name: 'fx.focus()', note: 'spotlight on the cabin', make: () => [fx.focus({center: [0.78, 0.78], size: 0.5, start: 0.3, blur: 14})]},
		],
	},
	{
		title: 'Texture and motion',
		cells: [
			{name: 'fx.grain()', note: 're-seeded 12 times a second', make: (f, fps) => [fx.grain({frame: f, fps, amount: 0.16})]},
			{name: 'fx.paper()', note: 'fibres, crumples and folds', make: () => [fx.paper({amount: 0.85})]},
			{name: 'fx.wave()', note: 'heat haze, phase animated', make: (f) => [fx.wave({amplitude: 7, wavelength: 170, phase: f * 0.4})]},
			{name: 'fx.pixelate(18)', note: 'mosaic blocks', make: () => [fx.pixelate(18)]},
			{name: 'fx.tear()', note: 'progress 0 to 1.25', ground: '#0b0d12', make: (f) => [fx.tear({progress: interpolate(f, [4, 32], [0, 1.25], CLAMP)})]},
			{name: 'fx.lightLeak()', note: 'progress 0 to 1', make: (f) => [fx.lightLeak({progress: interpolate(f, [0, PAGE - 1], [0, 1], CLAMP), seed: 3})]},
		],
	},
	{
		title: 'Reveals and signal',
		cells: [
			{name: 'fx.shine()', note: 'a sweep across the picture', make: (f) => [fx.shine({progress: interpolate(f, [2, 32], [0, 1], CLAMP)})]},
			{name: 'fx.tvSignalOff(0.6)', note: 'colour bars blended in', make: () => [fx.tvSignalOff(0.6)]},
			{name: 'fx.slices()', note: 'kit effect: torn bands', make: (f) => [fx.slices({amount: 70, bands: 26, density: 0.4, seed: Math.floor(f / 2), split: 8})]},
			{name: 'fx.pixelDissolve()', note: 'progress 0 to 1 (gone)', ground: '#0b0d12', make: (f) => [fx.pixelDissolve({progress: interpolate(f, [2, 32], [0, 1], CLAMP)})]},
			{name: 'fx.evolve()', note: 'a soft wipe in', ground: '#0b0d12', make: (f) => [fx.evolve({progress: interpolate(f, [2, 30], [0, 1], CLAMP), feather: 0.25})]},
			{name: 'fx.staticNoise()', note: 'TV static, a new seed each frame', make: (f) => [fx.staticNoise({amount: 0.35, seed: f})]},
		],
	},
	{
		title: 'Looks on footage',
		cells: [
			{name: "lookEffects('film')", note: 'grade, 12 Hz grain, vignette', make: (f, fps) => lookEffects('film', {frame: f, fps, unit: 0.5})},
			{name: "lookEffects('vhs')", note: 'smear, split, tape noise', make: (f, fps) => lookEffects('vhs', {frame: f, fps, unit: 0.5})},
			{name: "lookEffects('crt')", note: 'glow, scanlines, curve', ground: '#030304', make: (f, fps) => lookEffects('crt', {frame: f, fps, unit: 0.5})},
			{name: "lookEffects('newsprint')", note: 'levels, halftone ink', ground: PAPER, make: (f, fps) => lookEffects('newsprint', {frame: f, fps, unit: 0.5})},
			{name: "lookEffects('noir')", note: 'black and white, grain', make: (f, fps) => lookEffects('noir', {frame: f, fps, unit: 0.5})},
			{name: 'fx.lut(makeCubeLut(fn))', note: 'a teal and orange LUT made in code', make: () => [fx.lut(TEAL_ORANGE)]},
		],
	},
];

const EffectsPage: React.FC<{page: number; cube: string | null}> = ({page, cube}) => {
	const f = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, safe} = useStage();
	const gap = 28 * unit;
	const labelH = 66 * unit;
	const headH = 72 * unit;
	const cw = Math.floor((safe.w - 2 * gap) / 3);
	const ch = Math.round((cw * 9) / 16);
	const gridH = 2 * (ch + labelH) + gap;
	const top = safe.y + headH + (safe.h - headH - gridH) / 2;
	const {title, cells} = PAGES[page];
	return (
		<AbsoluteFill>
			<div style={{position: 'absolute', left: safe.x, top: safe.y, display: 'flex', alignItems: 'baseline', gap: 18 * unit}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 46 * unit, color: t.colors.text, letterSpacing: `${t.tracking.display}em`}}>{title}</div>
				<div style={{fontFamily: t.type.mono, fontSize: 22 * unit, color: t.colors.muted}}>{`effect presets, page ${page + 1} of ${PAGES.length}`}</div>
			</div>
			{cells.map((c, i) => (
				<div key={c.name} style={{position: 'absolute', left: safe.x + (i % 3) * (cw + gap), top: top + Math.floor(i / 3) * (ch + labelH + gap), width: cw}}>
					<div style={{width: cw, height: ch, borderRadius: 14 * unit, overflow: 'hidden', background: c.ground ?? '#000000'}}>
						<Img src={PHOTO} width={cw} height={ch} style={{objectFit: 'cover', display: 'block'}} effects={c.make(f, fps, cube)} />
					</div>
					<div style={{marginTop: 12 * unit, fontFamily: t.type.mono, fontSize: 21 * unit, color: t.colors.text, whiteSpace: 'nowrap'}}>{c.name}</div>
					<div style={{marginTop: 2 * unit, fontFamily: t.type.body, fontSize: 19 * unit, color: t.colors.muted}}>{c.note}</div>
				</div>
			))}
		</AbsoluteFill>
	);
};

const EffectsDemo: React.FC = () => {
	const t = useTheme();
	const cube = useLutFile('fx/warm-film.cube');
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			{PAGES.map((p, i) => (
				// one page at a time: every effect canvas holds its own WebGL contexts
				<Sequence key={p.title} from={i * PAGE} durationInFrames={PAGE} name={p.title}>
					<EffectsPage page={i} cube={cube} />
				</Sequence>
			))}
		</AbsoluteFill>
	);
};

const DemoFxEffects: React.FC = () => (
	<ThemeProvider theme="midnight">
		<EffectsDemo />
	</ThemeProvider>
);

// ---------------------------------------------------------------- DemoFxLooks: the eight looks on one title card

/** The picture the looks are judged on: the photo with a slow push and a scrim under the title area. */
const TitlePhoto: React.FC = () => {
	const frame = useCurrentFrame();
	const {unit, safe, height, durationInFrames} = useStage();
	const push = 1 + 0.06 * interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], CLAMP);
	// darkest at the bottom of the safe area, where the title sits, in 16:9 and 9:16 alike
	const base = height - safe.y - safe.h;
	return (
		<AbsoluteFill style={{background: '#0d1532'}}>
			<Photo zoom={push} origin="61% 62%" position="61% 50%" />
			<AbsoluteFill style={{background: `linear-gradient(to top, rgba(10,8,20,0.82) 0px, rgba(10,8,20,0.82) ${base}px, rgba(10,8,20,0.4) ${base + 260 * unit}px, rgba(10,8,20,0) ${base + 560 * unit}px)`}} />
		</AbsoluteFill>
	);
};

/** The title block: kicker, headline and a Bangla line. */
const TitleText: React.FC<{color?: string}> = ({color = '#ffffff'}) => {
	const t = useTheme();
	const {unit, safe, vertical} = useStage();
	return (
		<SafeArea justify="end" gap={12}>
			<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 24 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: color === '#ffffff' ? '#ffd494' : color}}>
				Northbound film club · 14 November
			</div>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: (vertical ? 108 : 118) * unit, lineHeight: 1, letterSpacing: `${t.tracking.display}em`, color, maxWidth: safe.w, textWrap: 'balance'}}>
				Evenings by the lake
			</div>
			<div style={{fontFamily: t.type.bangla, fontWeight: t.weights.body, fontSize: 46 * unit, lineHeight: 1.3, color, opacity: 0.88}}>লেকের ধারে এক সন্ধ্যা</div>
		</SafeArea>
	);
};

const TitleCard: React.FC = () => (
	<AbsoluteFill>
		<TitlePhoto />
		<TitleText />
	</AbsoluteFill>
);

type LookDef = {name: string; render: (engine: LookEngine) => React.ReactNode};

const LOOKS: LookDef[] = [
	{name: 'FilmLook', render: (e) => <FilmLook engine={e}><TitleCard /></FilmLook>},
	{name: 'VhsLook', render: (e) => <VhsLook engine={e} osd="PLAY ▶" date="NOV 14 1997"><TitleCard /></VhsLook>},
	{name: 'CrtLook', render: (e) => <CrtLook engine={e}><TitleCard /></CrtLook>},
	// type printed solid over the screened picture: small type breaks up inside halftone dots
	{name: 'NewsprintLook', render: (e) => <NewsprintLook engine={e} overlay={<TitleText color="#f4efe4" />}><TitlePhoto /></NewsprintLook>},
	{name: 'NoirLook', render: (e) => <NoirLook engine={e} blinds={0.45}><TitleCard /></NoirLook>},
	{name: 'DreamyLook', render: (e) => <DreamyLook engine={e}><TitleCard /></DreamyLook>},
	{name: 'GlitchLook', render: (e) => <GlitchLook engine={e} bursts={[{at: 8, frames: 6}, {at: 26, frames: 5}]}><TitleCard /></GlitchLook>},
	{name: 'StopMotionLook', render: (e) => <StopMotionLook engine={e} step={3} levels={8}><TitleCard /></StopMotionLook>},
];

const LOOK_LEN = 40;

const LooksReel: React.FC<{engine: LookEngine; only?: string[]}> = ({engine, only}) => {
	const list = only ? LOOKS.filter((l) => only.includes(l.name)) : LOOKS;
	return (
		<AbsoluteFill style={{background: '#000000'}}>
			{list.map((l, i) => (
				<Sequence key={l.name} from={i * LOOK_LEN} durationInFrames={LOOK_LEN} name={l.name}>
					{l.render(engine)}
					<Tag>{`<${l.name}> ${engine === 'css' ? 'css' : 'canvas'}`}</Tag>
				</Sequence>
			))}
		</AbsoluteFill>
	);
};

const DemoFxLooks: React.FC = () => (
	<ThemeProvider theme="midnight">
		<LooksReel engine="auto" />
	</ThemeProvider>
);

const DemoFxLooksCss: React.FC = () => (
	<ThemeProvider theme="editorial">
		<LooksReel engine="css" />
	</ThemeProvider>
);

const VERTICAL_LOOKS = ['FilmLook', 'VhsLook', 'NewsprintLook', 'GlitchLook'];

const DemoFxLooksVertical: React.FC = () => (
	<ThemeProvider theme="midnight">
		<LooksReel engine="auto" only={VERTICAL_LOOKS} />
	</ThemeProvider>
);

// ---------------------------------------------------------------- DemoFxGlitch

const SignalCard: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<AbsoluteFill style={{background: `radial-gradient(ellipse at 30% 40%, ${t.colors.bg2} 0%, ${t.colors.bg} 70%)`}} />
			<SafeArea justify="center" gap={18}>
				<div style={{fontFamily: t.type.mono, fontSize: 26 * unit, color: t.colors.accent, letterSpacing: '0.12em'}}>CH 04 · LIVE · 21:07</div>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 250 * unit, lineHeight: 0.9, color: t.colors.text, textTransform: 'uppercase'}}>
					Signal lost
				</div>
				<div style={{width: 220 * unit, height: 10 * unit, background: t.colors.accent}} />
				<div style={{fontFamily: t.type.bangla, fontWeight: t.weights.strong, fontSize: 50 * unit, lineHeight: 1.3, color: t.colors.muted}}>সংকেত হারিয়ে গেছে, আবার চেষ্টা করুন</div>
			</SafeArea>
		</AbsoluteFill>
	);
};

const BURSTS = [
	{at: 16, frames: 6},
	{at: 40, frames: 5},
	{at: 64, frames: 7, strength: 0.7},
];

const DemoFxGlitch: React.FC = () => (
	<ThemeProvider theme="kinetic">
		<AbsoluteFill>
			<Sequence durationInFrames={96} name="canvas engine">
				<GlitchLook engine="canvas" bursts={BURSTS}>
					<SignalCard />
				</GlitchLook>
				<Tag>{'<GlitchLook> canvas · bursts at 16, 40, 64'}</Tag>
			</Sequence>
			<Sequence from={96} durationInFrames={96} name="css engine">
				<GlitchLook engine="css" bursts={BURSTS}>
					<SignalCard />
				</GlitchLook>
				<Tag>{'<GlitchLook> css · bursts at 16, 40, 64'}</Tag>
			</Sequence>
		</AbsoluteFill>
	</ThemeProvider>
);

// ---------------------------------------------------------------- DemoFxMasks

/** A full-frame scene shrunk into a grid cell, so frame-based components keep their coordinates. */
const Panel: React.FC<{x: number; y: number; k: number; label: string; children: React.ReactNode}> = ({x, y, k, label, children}) => {
	const t = useTheme();
	const {width, height, unit} = useStage();
	return (
		<>
			<div style={{position: 'absolute', left: x, top: y, width, height, scale: String(k), transformOrigin: '0 0', borderRadius: 28 * unit, overflow: 'hidden', background: t.colors.surface, boxShadow: '0 30px 80px rgba(17,24,39,0.14)'}}>
				<AbsoluteFill>{children}</AbsoluteFill>
			</div>
			<div style={{position: 'absolute', left: x, top: y + height * k + 12 * unit, fontFamily: t.type.mono, fontSize: 22 * unit, color: t.colors.muted}}>{label}</div>
		</>
	);
};

const PanelGrid: React.FC<{items: {label: string; node: React.ReactNode}[]}> = ({items}) => {
	const t = useTheme();
	const {width, height, safe, unit} = useStage();
	const k = 0.39;
	const gapX = safe.w - 2 * width * k;
	const labelH = 46 * unit;
	const gapY = safe.h - 2 * (height * k + labelH);
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			{items.map((it, i) => (
				<Panel key={it.label} x={safe.x + (i % 2) * (width * k + gapX)} y={safe.y + Math.floor(i / 2) * (height * k + labelH + gapY)} k={k} label={it.label}>
					{it.node}
				</Panel>
			))}
		</AbsoluteFill>
	);
};

const MaskShapes: React.FC = () => (
	<PanelGrid
		items={[
			{label: "<ShapeMask shape='circle' ring exit>", node: <ShapeMask shape="circle" at={[0.62, 0.6]} delay={6} duration={30} exit ring><Photo /></ShapeMask>},
			{label: "<ShapeMask shape='star' spin={90}>", node: <ShapeMask shape="star" inner={0.45} spin={90} delay={6} duration={34} exit><Photo /></ShapeMask>},
			{label: "<WipeMask from='topLeft' feather={160}>", node: <WipeMask from="topLeft" feather={160} delay={6} duration={30} exit><Photo /></WipeMask>},
			{label: "<WipeMask kind='blinds' slats={9}>", node: <WipeMask kind="blinds" slats={9} feather={0} delay={6} duration={30} exit><Photo /></WipeMask>},
		]}
	/>
);

const MaskMore: React.FC = () => (
	<PanelGrid
		items={[
			{label: "<WipeMask kind='split' from={0}>", node: <WipeMask kind="split" from={0} feather={60} delay={6} duration={28} exit><Photo /></WipeMask>},
			{label: "<WipeMask kind='radial' feather={140}>", node: <WipeMask kind="radial" at={[0.62, 0.62]} feather={140} delay={6} duration={30} exit><Photo /></WipeMask>},
			{label: "<ShapeMask shape='heart' size={560} ring>", node: <ShapeMask shape="heart" size={560} at={[0.5, 0.55]} delay={6} duration={26} exit ring={{width: 10}}><Photo /></ShapeMask>},
			{label: '<TextMask text="GLOW"> + a video', node: <GlowWord />},
		]}
	/>
);

const GlowWord: React.FC = () => (
	<AbsoluteFill style={{background: '#0b0d12'}}>
		<TextMask text="GLOW" fit={0.8} weight={900}>
			<BlendVideo src={staticFile('fx/leak-on-black.mp4')} mode="normal" crush={0} />
		</TextMask>
	</AbsoluteFill>
);

const MaskText: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill style={{background: '#0d1532'}}>
			<TextMask text="LAKE" src={PHOTO} fillZoom={0.12} fit={0.86} at={[0.5, 0.5]} outline={{color: 'rgba(255,255,255,0.4)', width: 2}} />
			<div style={{position: 'absolute', left: safe.x, right: safe.x, top: safe.y + safe.h * 0.86, textAlign: 'center', fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 34 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: 'rgba(255,255,255,0.8)'}}>
				Evenings by the lake · 14 November
			</div>
			<Tag at="tl">{'<TextMask text="LAKE" src={photo}>'}</Tag>
		</AbsoluteFill>
	);
};

const MaskFade: React.FC = () => {
	const t = useTheme();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<GradientMask fade="bottom" size={0.55}>
				<Photo />
			</GradientMask>
			<TextMask text="সন্ধ্যা" gradient={`linear-gradient(100deg, ${t.colors.accent} 10%, #e0527a 55%, #ffb86b 90%)`} font={t.type.bangla} weight={800} fit={0.5} at={[0.5, 0.74]} />
			<Tag at="tl">{"<GradientMask fade='bottom'> + <TextMask> Bangla, gradient"}</Tag>
		</AbsoluteFill>
	);
};

const DemoFxMasks: React.FC = () => (
	<ThemeProvider theme="studio">
		<AbsoluteFill>
			<Sequence durationInFrames={90} name="shapes and wipes">
				<MaskShapes />
			</Sequence>
			<Sequence from={90} durationInFrames={80} name="more masks" premountFor={20}>
				<MaskMore />
			</Sequence>
			<Sequence from={170} durationInFrames={75} name="text mask">
				<MaskText />
			</Sequence>
			<Sequence from={245} durationInFrames={60} name="gradient mask">
				<MaskFade />
			</Sequence>
		</AbsoluteFill>
	</ThemeProvider>
);


// ---------------------------------------------------------------- DemoFxKey

const GREEN = '#20c44e';

const KeyOverScene: React.FC = () => (
	<AbsoluteFill>
		<Photo effects={[fx.grade('natural')]} />
		<ChromaKey src={staticFile('fx/greenscreen.mp4')} color={GREEN} similarity={0.34} smoothness={0.08} spill={0.7} shadow={{blur: 26, y: 18, opacity: 0.4}} />
		<Tag at="tl">{'<ChromaKey color="#20c44e" shadow> over the scene'}</Tag>
	</AbsoluteFill>
);

const KeySticker: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, ${t.colors.bg2}, ${t.colors.bg} 75%)`}}>
			<ChromaKey src={staticFile('fx/greenscreen.mp4')} color={GREEN} similarity={0.34} spill={0.7} matte={{bottom: 0.2}} outline={{width: 12, color: '#ffffff'}} shadow={{blur: 30, y: 20, opacity: 0.5}} />
			<div style={{position: 'absolute', left: safe.x, bottom: safe.y, fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 64 * unit, color: t.colors.text}}>Sticker cut-out</div>
			<Tag at="tl">key, garbage matte, outline, shadow</Tag>
		</AbsoluteFill>
	);
};

const KeyVsBlend: React.FC = () => {
	const t = useTheme();
	const {unit, width} = useStage();
	// the clip goes on the blended element itself: a clipped parent would isolate the blend from the photo
	return (
		<AbsoluteFill>
			<Photo effects={[fx.grade('coolNight')]} />
			<BlendVideo src={staticFile('fx/leak-on-black.mp4')} mode="screen" crush={0.06} style={{clipPath: 'inset(0 50% 0 0)'}} />
			<ChromaKey src={staticFile('fx/leak-on-black.mp4')} color="#000000" similarity={0.25} smoothness={0.05} spill={0} fit="cover" style={{clipPath: 'inset(0 0 0 50%)'}} />
			<div style={{position: 'absolute', left: width / 2 - 2 * unit, top: 0, bottom: 0, width: 4 * unit, background: t.colors.text, opacity: 0.8}} />
			<Tag at="tl">{"<BlendVideo mode='screen' crush={0.06}>"}</Tag>
			<Tag at="tr">keyed black: hard edges, lost glow</Tag>
		</AbsoluteFill>
	);
};

const DemoFxKey: React.FC = () => (
	<ThemeProvider theme="midnight">
		<AbsoluteFill>
			<Sequence durationInFrames={90} name="key over a scene" premountFor={15}>
				<KeyOverScene />
			</Sequence>
			<Sequence from={90} durationInFrames={75} name="sticker" premountFor={15}>
				<KeySticker />
			</Sequence>
			<Sequence from={165} durationInFrames={75} name="screen blend vs key" premountFor={15}>
				<KeyVsBlend />
			</Sequence>
		</AbsoluteFill>
	</ThemeProvider>
);

// ---------------------------------------------------------------- DemoFxLightLeak

const LeakTitle: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<Photo effects={[fx.grade('cinematic'), fx.vignette({amount: 0.45})]} />
			<AbsoluteFill style={{background: 'rgba(5,5,5,0.35)'}} />
			<SafeArea justify="center" align="center" gap={20}>
				<div style={{fontFamily: t.type.body, fontSize: 26 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: t.colors.accent}}>Northbound pictures presents</div>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 132 * unit, lineHeight: 1, letterSpacing: `${t.tracking.display}em`, textTransform: 'uppercase', color: t.colors.text}}>The long evening</div>
			</SafeArea>
			<LightLeak seed={3} hue="coral" delay={4} duration={64} peak={0.6} />
			<LightLeak seed={9} hue="rose" delay={62} duration={38} />
			<Tag at="br">{'<LightLeak peak={0.6}> then a full <LightLeak hue="rose">'}</Tag>
		</AbsoluteFill>
	);
};

const SaleCard: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<Starburst rays={28} speed={8} origin={[0.5, 0.52]} />
			<SafeArea justify="center" align="center" gap={26}>
				{/* the shadow sits outside the shine's canvas (a drop-shadow follows the pill, a box-shadow inside would be clipped) */}
				<div style={{filter: `drop-shadow(0 ${18 * unit}px ${30 * unit}px rgba(26,15,46,0.4))`}}>
					<Shine delay={24} duration={30} boxWidth={Math.round(520 * unit)} boxHeight={Math.round(220 * unit)} style={{position: 'relative'}}>
						<div style={{width: 520 * unit, height: 220 * unit, borderRadius: 110 * unit, background: t.colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
							<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 140 * unit, color: t.colors.highlight, lineHeight: 1}}>-40%</div>
						</div>
					</Shine>
				</div>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 92 * unit, color: t.colors.text, textTransform: 'uppercase', lineHeight: 1}}>Sale ends Sunday</div>
				<div style={{fontFamily: t.type.bangla, fontWeight: t.weights.strong, fontSize: 48 * unit, color: t.colors.text, lineHeight: 1.3}}>অফার শেষ রবিবার</div>
			</SafeArea>
			<Tag at="br">{'<Starburst> ground + <Shine> on the badge'}</Tag>
		</AbsoluteFill>
	);
};

const DemoFxLightLeak: React.FC = () => (
	<AbsoluteFill>
		<Sequence durationInFrames={100} name="light leaks">
			<ThemeProvider theme="trailer">
				<LeakTitle />
			</ThemeProvider>
		</Sequence>
		<Sequence from={100} durationInFrames={90} name="starburst and shine">
			<ThemeProvider theme="retro">
				<SaleCard />
			</ThemeProvider>
		</Sequence>
	</AbsoluteFill>
);

// ---------------------------------------------------------------- transitions: scene content

type SceneLook = {kind: 'photo'; kicker: string; title: string; grade: Parameters<typeof fx.grade>[0]; zoom?: number; origin?: string} | {kind: 'card'; bg: string; fg: string; big: string; title: string; sub?: string};

const PhotoScene: React.FC<{kicker: string; title: string; grade: Parameters<typeof fx.grade>[0]; zoom?: number; origin?: string; tag: string}> = ({kicker, title, grade, zoom = 1, origin, tag}) => {
	const t = useTheme();
	const {unit, vertical} = useStage();
	return (
		<AbsoluteFill style={{background: '#0d1532'}}>
			<Photo effects={[fx.grade(grade)]} zoom={zoom} origin={origin} />
			<AbsoluteFill style={{background: 'linear-gradient(to top, rgba(10,8,20,0.72) 0%, rgba(10,8,20,0) 50%)'}} />
			<SafeArea justify="end" gap={8}>
				<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 26 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: '#ffd494'}}>{kicker}</div>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: (vertical ? 92 : 104) * unit, lineHeight: 1.02, letterSpacing: `${t.tracking.display}em`, color: '#ffffff'}}>{title}</div>
			</SafeArea>
			<Tag>{tag}</Tag>
		</AbsoluteFill>
	);
};

const CardScene: React.FC<{bg: string; fg: string; big: string; title: string; sub?: string; tag: string}> = ({bg, fg, big, title, sub, tag}) => {
	const t = useTheme();
	const {unit, vertical} = useStage();
	return (
		<AbsoluteFill style={{background: bg}}>
			<SafeArea justify="center" gap={14}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: (vertical ? 170 : big.length > 9 ? 150 : 230) * unit, lineHeight: 0.95, letterSpacing: `${t.tracking.display}em`, color: fg}}>{big}</div>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.strong, fontSize: 58 * unit, lineHeight: 1.1, color: fg}}>{title}</div>
				{sub ? <div style={{fontFamily: sub.match(/[ঀ-৿]/) ? t.type.bangla : t.type.body, fontWeight: t.weights.body, fontSize: 36 * unit, lineHeight: 1.35, color: fg, opacity: 0.78}}>{sub}</div> : null}
			</SafeArea>
			<Tag>{tag}</Tag>
		</AbsoluteFill>
	);
};

const TRIP: SceneLook[] = [
	{kind: 'photo', kicker: 'Day 1', title: 'Arrive at the lake', grade: 'natural'},
	{kind: 'card', bg: '#2563eb', fg: '#ffffff', big: '14 km', title: 'Ridge walk, day 2', sub: 'Five lookouts and one long lunch'},
	{kind: 'photo', kicker: 'Day 3', title: 'A night in the cabin', grade: 'warmFilm', zoom: 1.7, origin: '78% 80%'},
	{kind: 'card', bg: '#0b0d12', fg: '#f3f5f9', big: '02:14', title: 'Northern lights', sub: 'রাতের আকাশে সবুজ আলো'},
	{kind: 'photo', kicker: 'Day 5', title: 'Home by the water', grade: 'coolNight'},
	{kind: 'card', bg: '#f59e0b', fg: '#111827', big: '5 days', title: 'From 890 euros', sub: 'Small groups, May to September'},
	{kind: 'card', bg: '#111827', fg: '#ffffff', big: 'northbound.travel', title: 'Book the trip'},
];

const sceneNode = (i: number, tag: string): React.ReactNode => {
	const s = TRIP[i % TRIP.length];
	return s.kind === 'photo' ? (
		<PhotoScene kicker={s.kicker} title={s.title} grade={s.grade} zoom={s.zoom} origin={s.origin} tag={tag} />
	) : (
		<CardScene bg={s.bg} fg={s.fg} big={s.big} title={s.title} sub={s.sub} tag={tag} />
	);
};

/** Scenes from a list of transitions: scene i shows which transition comes next. */
const tripScenes = (list: {t: ReturnType<typeof tr.fade>; label: string}[], len = 50): SceneSpec[] =>
	[...list, null].map((item, i) => ({
		node: sceneNode(i, item ? `next: ${item.label}` : 'end'),
		duration: len,
		transition: item?.t,
		name: item ? `before ${item.label}` : 'last',
	}));

const SCENES_BUILTIN = tripScenes([
	{t: tr.slide(), label: 'tr.slide()'},
	{t: tr.wipe({direction: 'from-left'}), label: "tr.wipe('from-left')"},
	{t: tr.iris(), label: 'tr.iris()'},
	{t: tr.pushCut(), label: 'tr.pushCut()'},
	{t: tr.fade(), label: 'tr.fade()'},
	{t: tr.flip(), label: 'tr.flip()'},
]);

const SCENES_KIT = tripScenes([
	{t: tr.zoomThrough(), label: 'tr.zoomThrough()'},
	{t: tr.whipPan({sound: {src: staticFile('fx/whoosh.m4a'), volume: 0.5}}), label: 'tr.whipPan() + sound'},
	{t: tr.glitchCut(), label: 'tr.glitchCut()'},
	{t: tr.lightLeakCross(), label: 'tr.lightLeakCross()'},
	{t: tr.blurDissolve(), label: 'tr.blurDissolve()'},
]);

const SCENES_MASK = tripScenes([
	{t: tr.maskReveal({at: [0.62, 0.62], ring: true}), label: 'tr.maskReveal() circle'},
	{t: tr.maskReveal({shape: 'diagonal'}), label: "tr.maskReveal('diagonal')"},
	{t: tr.clockWipe(), label: 'tr.clockWipe()'},
	{t: tr.flash(), label: 'tr.flash() overlay'},
	{t: tr.leak(), label: 'tr.leak() overlay'},
]);

// scene 2 wears a FilmLook: next to shader transitions it switches itself to the css engine (no nesting)
const SCENES_SHADER_A = tripScenes([
	{t: tr.blurSlide(), label: 'tr.blurSlide()'},
	{t: tr.zoomBlur(), label: 'tr.zoomBlur()'},
	{t: tr.crossZoom(), label: 'tr.crossZoom()'},
	{t: tr.filmBurn(), label: 'tr.filmBurn()'},
	{t: tr.dissolve(), label: 'tr.dissolve()'},
	{t: tr.linearBlur(), label: 'tr.linearBlur()'},
]).map((s, i) => (i === 2 ? {...s, node: <FilmLook>{s.node}</FilmLook>} : s));

const SCENES_SHADER_B = tripScenes([
	{t: tr.dreamyZoom(), label: 'tr.dreamyZoom()'},
	{t: tr.swap(), label: 'tr.swap()'},
	{t: tr.ripple(), label: 'tr.ripple()'},
	{t: tr.crosswarp(), label: 'tr.crosswarp()'},
	{t: tr.bookFlip(), label: 'tr.bookFlip()'},
	{t: tr.zoomInOut(), label: 'tr.zoomInOut()'},
]);

const SCENES_VERTICAL = tripScenes([
	{t: tr.slide({direction: 'from-bottom'}), label: "slide('from-bottom')"},
	{t: tr.maskReveal({shape: 'diagonal'}), label: "maskReveal('diagonal')"},
	{t: tr.whipPan({direction: 'up'}), label: "whipPan('up')"},
	{t: tr.blurSlide({direction: 'from-bottom'}), label: "blurSlide('from-bottom')"},
]);


// shader in then CSS out, and CSS in then shader out: <Scenes> splits the second kind (see planScenes)
const SCENES_MIXED = tripScenes([
	{t: tr.blurSlide(), label: 'blurSlide (shader)'},
	{t: tr.slide(), label: 'slide (css)'},
	{t: tr.zoomBlur(), label: 'zoomBlur (shader)'},
	{t: tr.wipe(), label: 'wipe (css)'},
]);

const withTheme = (theme: ThemeName, scenes: SceneSpec[], edges: {enter?: FxTransition; exit?: FxTransition} = {}): React.FC => {
	const C: React.FC = () => (
		<ThemeProvider theme={theme}>
			<AbsoluteFill style={{background: '#000000'}}>
				<Scenes scenes={scenes} enter={edges.enter} exit={edges.exit} />
			</AbsoluteFill>
		</ThemeProvider>
	);
	return C;
};

const KIT_EDGES = {enter: tr.fade({frames: 12}), exit: tr.fade({frames: 14, out: true})};


// ---------------------------------------------------------------- DemoFxLeakHues: the named leak colours

const LeakHues: React.FC = () => {
	const t = useTheme();
	const {width, height, unit} = useStage();
	const names = Object.keys(LEAK_HUES) as (keyof typeof LEAK_HUES)[];
	const cols = 5;
	const w = Math.floor(width / cols);
	const h = Math.floor(height / Math.ceil(names.length / cols));
	return (
		<AbsoluteFill style={{background: '#000000'}}>
			{names.map((n, i) => (
				<div key={n} style={{position: 'absolute', left: (i % cols) * w, top: Math.floor(i / cols) * h, width: w, height: h}}>
					<Solid width={w} height={h} effects={[fx.lightLeak({progress: 0.42, seed: 3, hue: LEAK_HUES[n]})]} />
					<div style={{position: 'absolute', left: 24 * unit, bottom: 24 * unit, fontFamily: t.type.mono, fontSize: 30 * unit, color: '#ffffff', background: 'rgba(0,0,0,0.55)', padding: `${6 * unit}px ${12 * unit}px`, borderRadius: 8 * unit}}>{`${n} · ${LEAK_HUES[n]}`}</div>
				</div>
			))}
		</AbsoluteFill>
	);
};


// ---------------------------------------------------------------- the list

export const demos: DemoDef[] = [
	{id: 'DemoFxSampleArt', component: SampleArt, durationInFrames: 1},
	{id: 'DemoFxEffects', component: DemoFxEffects, durationInFrames: PAGES.length * PAGE},
	{id: 'DemoFxLooks', component: DemoFxLooks, durationInFrames: LOOKS.length * LOOK_LEN},
	{id: 'DemoFxLooksCss', component: DemoFxLooksCss, durationInFrames: LOOKS.length * LOOK_LEN},
	{id: 'DemoFxLooksVertical', component: DemoFxLooksVertical, durationInFrames: VERTICAL_LOOKS.length * LOOK_LEN, width: 1080, height: 1920},
	{id: 'DemoFxGlitch', component: DemoFxGlitch, durationInFrames: 192},
	{id: 'DemoFxMasks', component: DemoFxMasks, durationInFrames: 305},
	{id: 'DemoFxKey', component: DemoFxKey, durationInFrames: 240},
	{id: 'DemoFxLightLeak', component: DemoFxLightLeak, durationInFrames: 190},
	{id: 'DemoFxLeakHues', component: LeakHues, durationInFrames: 1},
	{id: 'DemoFxTransitions', component: withTheme('studio', SCENES_BUILTIN), durationInFrames: scenesLength(SCENES_BUILTIN, 30)},
	{id: 'DemoFxTransitionsKit', component: withTheme('studio', SCENES_KIT, KIT_EDGES), durationInFrames: scenesLength(SCENES_KIT, 30, KIT_EDGES)},
	{id: 'DemoFxTransitionsMask', component: withTheme('midnight', SCENES_MASK), durationInFrames: scenesLength(SCENES_MASK, 30)},
	{id: 'DemoFxTransitionsShaderA', component: withTheme('midnight', SCENES_SHADER_A), durationInFrames: scenesLength(SCENES_SHADER_A, 30)},
	{id: 'DemoFxTransitionsShaderB', component: withTheme('midnight', SCENES_SHADER_B), durationInFrames: scenesLength(SCENES_SHADER_B, 30)},
	{id: 'DemoFxTransitionsMixed', component: withTheme('midnight', SCENES_MIXED), durationInFrames: scenesLength(SCENES_MIXED, 30)},
	{id: 'DemoFxTransitionsVertical', component: withTheme('fresh', SCENES_VERTICAL), durationInFrames: scenesLength(SCENES_VERTICAL, 30), width: 1080, height: 1920},
];
