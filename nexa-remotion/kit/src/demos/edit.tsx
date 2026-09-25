import {useAudioData} from '@remotion/media-utils';
import React from 'react';
import {AbsoluteFill, Img, Sequence, Series, staticFile, useCurrentFrame} from 'remotion';
import {at30, curves, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate, PushIn, ramp} from '../kit/motion';
import {
	Audiogram,
	AudioBars,
	AudioCircle,
	AudioWave,
	BeatPulse,
	buildEdit,
	Clip,
	editLength,
	fadeGain,
	gainToDb,
	JumpCuts,
	KenBurns,
	kenBurnsAt,
	kenBurnsPreset,
	keepRanges,
	LayoutLabel,
	LayoutSwitch,
	Letterbox,
	Music,
	musicGain,
	OnBeats,
	PictureInPicture,
	remapWords,
	Sfx,
	sourceTime,
	speechWindows,
	SpeedRamp,
	speedAt,
	SplitScreen,
	TimeRamp,
	useBeatGrid,
	Voice,
	beatAt,
	type SpeedKey,
	type TimeWindow,
} from '../kit/edit';

// ------------------------------------------------------------------ demo media (made for the kit, see README)

const media = (name: string) => staticFile(`edit/${name}`);

// Word timings of voice.m4a (and of talk.mp4, which carries the same voice), in the @remotion/captions shape.
const WORDS = [
	{text: 'Every', startMs: 620, endMs: 980},
	{text: ' edit', startMs: 1015, endMs: 1380},
	{text: ' starts', startMs: 1415, endMs: 1685},
	{text: ' with', startMs: 1720, endMs: 1880},
	{text: ' the', startMs: 1915, endMs: 2075},
	{text: ' voice.', startMs: 2110, endMs: 2510},
	{text: ' Cut', startMs: 4250, endMs: 4485},
	{text: ' the', startMs: 4520, endMs: 4680},
	{text: ' pauses,', startMs: 4715, endMs: 5150},
	{text: ' keep', startMs: 5310, endMs: 5545},
	{text: ' the', startMs: 5580, endMs: 5740},
	{text: ' rhythm,', startMs: 5775, endMs: 6165},
	{text: ' then', startMs: 8150, endMs: 8350},
	{text: ' let', startMs: 8385, endMs: 8615},
	{text: ' the', startMs: 8650, endMs: 8810},
	{text: ' music', startMs: 8845, endMs: 9275},
	{text: ' breathe', startMs: 9310, endMs: 9545},
	{text: ' underneath.', startMs: 9580, endMs: 10100},
];
type Word = (typeof WORDS)[number];

// The same timings with a Bangla line (a word per word, so the highlight follows the voice).
const BN_TEXT = ['প্রতিটা', ' এডিটের', ' শুরু', ' হয়', ' ভয়েস', ' থেকেই।', ' পজগুলো', ' কেটে', ' দিন,', ' ছন্দটা', ' ধরে', ' রাখুন,', ' তারপর', ' মিউজিকটা', ' পেছনে', ' হালকা', ' করে', ' বাজুক।'];
const BN_WORDS: Word[] = WORDS.map((w, i) => ({...w, text: BN_TEXT[i]}));

const FPS = 30;
const MUSIC_BPM = 120; // music.m4a: 120 BPM, first downbeat at 0 s, 20 s loop

// ------------------------------------------------------------------ small demo furniture

const Themed: React.FC<{theme: ThemeName; children: React.ReactNode}> = ({theme, children}) => <ThemeProvider theme={theme}>{children}</ThemeProvider>;

const Card: React.FC<{style?: React.CSSProperties; children: React.ReactNode}> = ({style, children}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div
			style={{
				position: 'absolute',
				background: t.colors.surface,
				color: t.colors.text,
				borderRadius: Math.min(t.radius, 22) * unit,
				padding: `${26 * unit}px ${30 * unit}px`,
				boxShadow: `0 ${16 * unit}px ${44 * unit}px rgba(0,0,0,${t.dark ? 0.45 : 0.18})`,
				boxSizing: 'border-box',
				...style,
			}}
		>
			{children}
		</div>
	);
};

const Kicker: React.FC<{children: React.ReactNode; color?: string}> = ({children, color}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 22 * unit, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase', color: color ?? t.colors.accent}}>
			{children}
		</div>
	);
};

const Row: React.FC<{label: string; value: string}> = ({label, value}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{display: 'flex', justifyContent: 'space-between', gap: 30 * unit, fontSize: 28 * unit, lineHeight: 1.5}}>
			<span style={{fontFamily: t.type.body, color: t.colors.muted}}>{label}</span>
			<span style={{fontFamily: t.type.mono, color: t.colors.text, fontVariantNumeric: 'tabular-nums'}}>{value}</span>
		</div>
	);
};

const tc = (frames: number, fps = FPS) => {
	const f = Math.max(0, Math.round(frames));
	return `${String(Math.floor(f / fps)).padStart(2, '0')}.${String(f % fps).padStart(2, '0')}`;
};

/** The words of the current phrase: spoken in the text colour, the active one in the accent, the rest faint. */
const Caption: React.FC<{words: readonly Word[]; ms: number; style?: React.CSSProperties; box?: boolean}> = ({words, ms, style, box = false}) => {
	const t = useTheme();
	const {unit} = useStage();
	const phrases: Word[][] = [];
	let cur: Word[] = [];
	for (const w of words) {
		cur.push(w);
		if (/[,.।]$/.test(w.text)) {
			phrases.push(cur);
			cur = [];
		}
	}
	if (cur.length) {
		phrases.push(cur);
	}
	let shown: Word[] | null = null;
	for (const p of phrases) {
		if (p[0].startMs - 150 <= ms) {
			shown = p;
		}
	}
	if (!shown || ms > shown[shown.length - 1].endMs + 700) {
		return null;
	}
	const body = (
		<span style={{whiteSpace: 'pre-wrap'}}>
			{shown.map((w, i) => {
				const active = ms >= w.startMs && ms < w.endMs + 60;
				const said = ms >= w.startMs;
				return (
					<span key={i} style={{color: active ? t.colors.accent : said ? t.colors.text : t.colors.muted, opacity: said ? 1 : 0.55}}>
						{i === 0 ? w.text.trimStart() : w.text}
					</span>
				);
			})}
		</span>
	);
	return box ? (
		<div
			style={{
				padding: `${14 * unit}px ${28 * unit}px`,
				borderRadius: Math.min(t.radius, 18) * unit,
				background: t.colors.surface,
				fontFamily: t.type.body,
				fontWeight: t.weights.strong,
				fontSize: 52 * unit,
				lineHeight: 1.2,
				boxShadow: `0 ${10 * unit}px ${30 * unit}px rgba(0,0,0,0.25)`,
				...style,
			}}
		>
			{body}
		</div>
	) : (
		<div style={style}>{body}</div>
	);
};

// ------------------------------------------------------------------ Clip

const CLIP_IN = 45;
const CLIP_OUT = 180;

const ClipDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, width} = useStage();
	const len = CLIP_OUT - CLIP_IN;
	const W = 440;
	const H = 90;
	const pts = Array.from({length: 46}, (_, i) => {
		const f = (i / 45) * (len - 1);
		return `${(i / 45) * W * unit},${(1 - fadeGain(f, len, 12, 18)) * H * unit}`;
	}).join(' ');
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Clip src={media('cam-a.mp4')} trimBefore={CLIP_IN} trimAfter={CLIP_OUT} fadeIn={12} fadeOut={18} volume={0.8} />
			<Animate in="rise" delay={8} style={{position: 'absolute', right: width - safe.x - safe.w, top: safe.y}}>
				<Card style={{position: 'relative', width: 520 * unit}}>
					<Kicker>Clip</Kicker>
					<div style={{height: 14 * unit}} />
					<Row label="Source" value={`${tc(CLIP_IN)} to ${tc(CLIP_OUT)}`} />
					<Row label="Showing" value={`f${String(frame + CLIP_IN).padStart(3, '0')}`} />
					<Row label="Sound" value="fade 12 in, 18 out" />
					<svg width={W * unit} height={(H + 8) * unit} style={{display: 'block', marginTop: 16 * unit, overflow: 'visible'}}>
						<polyline points={pts} fill="none" stroke={t.colors.accent} strokeWidth={4 * unit} strokeLinejoin="round" />
						<line x1={(frame / (len - 1)) * W * unit} x2={(frame / (len - 1)) * W * unit} y1={0} y2={H * unit} stroke={t.colors.text} strokeWidth={2 * unit} />
					</svg>
				</Card>
			</Animate>
		</AbsoluteFill>
	);
};

const ClipVerticalDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Clip src={media('cam-b.mp4')} trimBefore={30} objectFit="blur" dim={0.5} muted />
			<Animate in="rise" delay={6} style={{position: 'absolute', left: safe.x, top: safe.y}}>
				<LayoutLabel text="16:9 footage, blur fill" style={{position: 'relative', fontSize: 34 * unit}} />
			</Animate>
			<Animate in="rise" delay={12} style={{position: 'absolute', left: safe.x, top: safe.y + 90 * unit, width: safe.w}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 84 * unit, lineHeight: 1.02, letterSpacing: `${t.tracking.display}em`, color: t.colors.text, textWrap: 'balance'}}>
					The coast at first light
				</div>
			</Animate>
		</AbsoluteFill>
	);
};

const FreezeDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe} = useStage();
	const hold = 45;
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Series>
				<Series.Sequence durationInFrames={hold}>
					<Clip src={media('cam-b.mp4')} trimBefore={30} muted />
				</Series.Sequence>
				<Series.Sequence durationInFrames={60}>
					<PushIn amount={0.05}>
						<Clip src={media('cam-b.mp4')} trimBefore={30} freeze={hold - 1} />
					</PushIn>
					<AbsoluteFill style={{background: '#fff', opacity: Math.max(0, 0.85 - (frame - hold) / 8)}} />
					<Animate in="rise" out="fade" delay={6} style={{position: 'absolute', left: safe.x, top: safe.y + safe.h - 190 * unit}}>
						<Card style={{position: 'relative'}}>
							<Kicker>Freeze frame</Kicker>
							<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 64 * unit, letterSpacing: `${t.tracking.display}em`, marginTop: 6 * unit}}>Hold the moment</div>
						</Card>
					</Animate>
				</Series.Sequence>
				<Series.Sequence durationInFrames={45}>
					<Clip src={media('cam-b.mp4')} trimBefore={30 + hold} muted />
				</Series.Sequence>
			</Series>
			<Sfx src={media('click.wav')} at={hold} volume={0.4} />
		</AbsoluteFill>
	);
};

const EnginesDemo: React.FC = () => (
	<SplitScreen gap={10} enter="none" labels={['media engine, 1.5x', 'offthread engine, 1.5x', 'offthread loop, 1 s']} labelPosition="top">
		<Clip src={media('cam-a.mp4')} trimBefore={30} playbackRate={1.5} muted videoStyle={{objectPosition: '0% 100%'}} />
		<Clip src={media('cam-a.mp4')} trimBefore={30} playbackRate={1.5} engine="offthread" muted videoStyle={{objectPosition: '0% 100%'}} />
		<Clip src={media('cam-b.mp4')} trimBefore={60} trimAfter={90} loop engine="offthread" muted />
	</SplitScreen>
);

// ------------------------------------------------------------------ Ken Burns

const KB = {move: 'in' as const, amount: 0.34, focus: [0.62, 0.45] as const, delay: 0};

const KenBurnsDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, width, height, durationInFrames} = useStage();
	const [a, b] = kenBurnsPreset(KB.move, KB.amount, KB.focus);
	const now = kenBurnsAt(a, b, ramp(frame, KB.delay, durationInFrames - KB.delay, curves.sine));
	const mw = 400 * unit;
	const mh = mw * (height / width);
	const box = (r: {x: number; y: number; w: number}, style: React.CSSProperties) => (
		<div style={{position: 'absolute', left: r.x * mw, top: r.y * mh, width: r.w * mw, height: r.w * mh, boxSizing: 'border-box', ...style}} />
	);
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<KenBurns src={media('still.jpg')} move={KB.move} amount={KB.amount} focus={KB.focus} />
			<Animate in="rise" delay={10} style={{position: 'absolute', right: width - safe.x - safe.w, top: safe.y + safe.h - mh - 64 * unit}}>
				<Card style={{position: 'relative', padding: 14 * unit}}>
					<div style={{position: 'relative', width: mw, height: mh, borderRadius: 10 * unit, overflow: 'hidden'}}>
						<Img src={media('still.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', opacity: 0.55}} />
						{box(a, {border: `${2 * unit}px dashed rgba(255,255,255,0.8)`})}
						{box(b, {border: `${3 * unit}px solid ${t.colors.accent}`})}
						{box(now, {border: `${3 * unit}px solid #FFFFFF`, boxShadow: '0 0 0 9999px rgba(0,0,0,0.35)'})}
					</div>
					<div style={{display: 'flex', gap: 22 * unit, marginTop: 12 * unit, fontFamily: t.type.body, fontSize: 22 * unit, color: t.colors.muted}}>
						<span>dashed: start</span>
						<span style={{color: t.colors.accent}}>accent: end</span>
						<span style={{color: t.colors.text}}>white: now</span>
					</div>
				</Card>
			</Animate>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ Jump cuts

const TALK_SECONDS = 12;
const RANGES = keepRanges(WORDS, {gap: 0.45, padBefore: 0.12, padAfter: 0.2, duration: TALK_SECONDS});
const JUMP_LENGTH = editLength(RANGES, FPS);

const JumpCutsDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps} = useStage();
	const edit = React.useMemo(() => buildEdit(RANGES, fps), [fps]);
	const words = React.useMemo(() => remapWords(WORDS, edit, fps), [edit, fps]);
	const src = sourceTime(frame, edit, fps) ?? 0;
	const barW = 720 * unit;
	const secW = barW / TALK_SECONDS;
	const row = (label: string, color: string, children: React.ReactNode) => (
		<div style={{display: 'flex', alignItems: 'center', gap: 22 * unit}}>
			<div style={{width: 170 * unit, fontFamily: t.type.body, fontWeight: 700, fontSize: 24 * unit, color, fontVariantNumeric: 'tabular-nums'}}>{label}</div>
			<div style={{position: 'relative', width: barW, height: 20 * unit, borderRadius: 6 * unit, background: 'rgba(255,255,255,0.12)', overflow: 'hidden'}}>{children}</div>
		</div>
	);
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<JumpCuts src={media('talk.mp4')} ranges={RANGES} punchIn={0.08} punchOrigin="60% 38%" />
			<Animate in="rise" delay={6} style={{position: 'absolute', left: safe.x, top: safe.y}}>
				<div style={{display: 'flex', flexDirection: 'column', gap: 16 * unit, padding: `${20 * unit}px ${26 * unit}px`, borderRadius: 18 * unit, background: 'rgba(10,12,20,0.74)'}}>
					{row(
						`Source ${TALK_SECONDS.toFixed(1)} s`,
						'rgba(255,255,255,0.75)',
						<>
							{RANGES.map(([s0, e0], i) => (
								<div key={i} style={{position: 'absolute', left: s0 * secW, width: (e0 - s0) * secW, top: 0, bottom: 0, background: 'rgba(255,255,255,0.6)'}} />
							))}
							<div style={{position: 'absolute', left: src * secW - 2 * unit, width: 4 * unit, top: 0, bottom: 0, background: t.colors.accent}} />
						</>,
					)}
					{row(
						`Cut ${(JUMP_LENGTH / fps).toFixed(1)} s`,
						t.colors.accent,
						<>
							{edit.map((p) => (
								<div key={p.index} style={{position: 'absolute', left: (p.from / fps) * secW, width: (p.length / fps) * secW - 3 * unit, top: 0, bottom: 0, background: p.index % 2 ? t.colors.accent2 : t.colors.accent}} />
							))}
							<div style={{position: 'absolute', left: (frame / fps) * secW - 2 * unit, width: 4 * unit, top: 0, bottom: 0, background: '#fff'}} />
						</>,
					)}
				</div>
			</Animate>
			<div style={{position: 'absolute', left: safe.x, width: safe.w, top: safe.y + safe.h - 200 * unit, display: 'flex', justifyContent: 'center'}}>
				<Caption words={words} ms={(frame / fps) * 1000} box />
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ Speed ramp

const RAMP: SpeedKey[] = [
	{at: 0, speed: 1},
	{at: 30, speed: 1},
	{at: 55, speed: 2.8},
	{at: 80, speed: 2.8},
	{at: 105, speed: 0.25},
	{at: 140, speed: 0.25},
	{at: 179, speed: 1},
];
const GRAPHIC_RAMP: SpeedKey[] = [
	{at: 0, speed: 1},
	{at: 50, speed: 1},
	{at: 75, speed: 0.2},
	{at: 125, speed: 0.2},
	{at: 150, speed: 1},
];

const Ball: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit} = useStage();
	const x = ((frame % 120) / 120) * 420;
	return (
		<div style={{position: 'relative', width: 460 * unit, height: 60 * unit}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 28 * unit, height: 4 * unit, borderRadius: 2 * unit, background: t.colors.line}} />
			<div style={{position: 'absolute', left: x * unit, top: 10 * unit, width: 40 * unit, height: 40 * unit, borderRadius: 20 * unit, background: t.colors.accent2}} />
		</div>
	);
};

const SpeedRampDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, width, durationInFrames} = useStage();
	const speed = speedAt(frame, RAMP);
	const W = 520;
	const H = 150;
	const pts = Array.from({length: 90}, (_, i) => {
		const f = (i / 89) * (durationInFrames - 1);
		return `${(i / 89) * W * unit},${(1 - speedAt(f, RAMP) / 3) * H * unit}`;
	});
	const px = (frame / (durationInFrames - 1)) * W * unit;
	const py = (1 - speed / 3) * H * unit;
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<SpeedRamp src={media('cam-b.mp4')} keys={RAMP} />
			<Music src={media('music.m4a')} level={0.4} fadeIn={20} fadeOut={30} />
			<Animate in="rise" delay={6} style={{position: 'absolute', left: safe.x, top: safe.y + safe.h - 330 * unit}}>
				<Card style={{position: 'relative', width: (W + 60) * unit}}>
					<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
						<Kicker>Speed ramp</Kicker>
						<div style={{fontFamily: t.type.mono, fontWeight: 600, fontSize: 44 * unit, fontVariantNumeric: 'tabular-nums', color: t.colors.text}}>{speed.toFixed(2)}x</div>
					</div>
					<svg width={W * unit} height={H * unit} style={{display: 'block', marginTop: 12 * unit, overflow: 'visible'}}>
						<line x1={0} x2={W * unit} y1={(2 / 3) * H * unit} y2={(2 / 3) * H * unit} stroke={t.colors.line} strokeWidth={2 * unit} strokeDasharray={`${6 * unit} ${6 * unit}`} />
						<polyline points={pts.join(' ')} fill="none" stroke={t.colors.accent} strokeWidth={4 * unit} strokeLinejoin="round" />
						<circle cx={px} cy={py} r={9 * unit} fill={t.colors.accent} stroke={t.colors.surface} strokeWidth={3 * unit} />
					</svg>
				</Card>
			</Animate>
			<Animate in="rise" delay={12} style={{position: 'absolute', right: width - safe.x - safe.w, top: safe.y + safe.h - 190 * unit}}>
				<Card style={{position: 'relative', width: 520 * unit}}>
					<Kicker color={t.colors.accent2}>TimeRamp on graphics</Kicker>
					<div style={{height: 16 * unit}} />
					<TimeRamp keys={GRAPHIC_RAMP}>
						<Ball />
					</TimeRamp>
				</Card>
			</Animate>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ Split screens, picture in picture, layouts

const SplitDemo: React.FC = () => (
	<SplitScreen gap={14} labels={['City at dusk', 'Nadia, host', 'The coast']}>
		<Clip src={media('cam-a.mp4')} trimBefore={20} muted />
		<Clip src={media('talk.mp4')} trimBefore={15} objectFit="cover" videoStyle={{objectPosition: '60% 50%'}} muted />
		<Clip src={media('cam-b.mp4')} trimBefore={40} muted />
	</SplitScreen>
);

const SplitVerticalDemo: React.FC = () => (
	<SplitScreen divider={8} labels={['রিঅ্যাকশন', 'ক্লিপটা']} labelPosition="top" enter="wipe">
		<Clip src={media('talk.mp4')} trimBefore={15} muted />
		<Clip src={media('cam-a.mp4')} trimBefore={20} muted />
	</SplitScreen>
);

const PipDemo: React.FC = () => (
	<AbsoluteFill>
		<Clip src={media('cam-a.mp4')} muted />
		<PictureInPicture shape="circle" width={320} border={6} label="Nadia Karim, host" delay={10} exit="pop" zoom={1.8} focus={[0.66, 0.4]}>
			<Clip src={media('talk.mp4')} trimBefore={15} objectFit="cover" />
		</PictureInPicture>
	</AbsoluteFill>
);

const SHOTS = [
	{at: 0, shot: 'a' as const, name: 'Host'},
	{at: 45, shot: 'b+a' as const, name: 'B-roll, host inset'},
	{at: 120, shot: 'split' as const, name: 'Split'},
	{at: 185, shot: 'a+b' as const, name: 'Host, B-roll inset'},
];

const LayoutSwitchDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const {safe} = useStage();
	const current = [...SHOTS].reverse().find((s) => s.at <= frame) ?? SHOTS[0];
	return (
		<AbsoluteFill>
			<LayoutSwitch
				keys={SHOTS}
				pip={{corner: 'bottomRight', width: 540, shape: 'round'}}
				a={<Clip src={media('talk.mp4')} trimBefore={15} objectFit="cover" videoStyle={{objectPosition: '62% 50%'}} />}
				b={<Clip src={media('cam-b.mp4')} muted />}
			/>
			<Sequence key={current.name} from={current.at} layout="none">
				<Animate in="rise" delay={current.at === 0 ? 6 : 10} style={{position: 'absolute', left: safe.x, top: safe.y}}>
					<LayoutLabel text={current.name} style={{position: 'relative'}} />
				</Animate>
			</Sequence>
		</AbsoluteFill>
	);
};

const LetterboxDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe, height, width} = useStage();
	const bar = (height - width / 2.39) / 2;
	return (
		<Letterbox aspect={2.39} delay={8}>
			<KenBurns move="right" amount={0.2} focus={[0.5, 0.3]}>
				<Clip src={media('cam-a.mp4')} muted />
			</KenBurns>
			<AbsoluteFill style={{zIndex: 2}}>
				<Animate in="blur" delay={30} style={{position: 'absolute', left: safe.x, width: safe.w, top: height - bar + (safe.y + safe.h - (height - bar)) / 2 - 26 * unit, textAlign: 'center'}}>
					<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 40 * unit, letterSpacing: `${t.tracking.caps}em`, color: t.colors.text, textTransform: 'uppercase'}}>
						Night falls on the city
					</div>
				</Animate>
			</AbsoluteFill>
		</Letterbox>
	);
};

// ------------------------------------------------------------------ Ducking: music under the voice, drawn

// Two takes of the voice: the first line, a musical breath, then two lines with a short pause between them.
const VA = {from: 12, trimAfter: 84};
const VB = {from: 160, trimBefore: 120};
const DUCK = {level: 0.5, duckTo: 0.06, attack: 30, release: 30, hold: 8};
const DUCK_WINDOWS: TimeWindow[] = [
	...speechWindows(WORDS.slice(0, 6), FPS, {offset: VA.from}),
	...speechWindows(WORDS.slice(6), FPS, {offset: VB.from - VB.trimBefore}),
];
const DUCK_LENGTH = 420;

/** Where the voice file is at composition frame f (null when neither take plays). */
const voiceFileFrame = (f: number): number | null => {
	if (f >= VA.from && f < VA.from + VA.trimAfter) {
		return f - VA.from;
	}
	if (f >= VB.from) {
		return f - VB.from + VB.trimBefore;
	}
	return null;
};

const DuckingDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps, durationInFrames} = useStage();
	const voice = useAudioData(media('voice.m4a'));
	const left = safe.x + 250 * unit;
	const W = safe.x + safe.w - left;
	const x = (f: number) => left + (f / durationInFrames) * W;
	const laneV = {top: safe.y + 200 * unit, h: 150 * unit};
	const laneM = {top: safe.y + 420 * unit, h: 400 * unit};
	const dbBottom = -36;
	const yDb = (db: number) => laneM.top + (Math.min(0, Math.max(dbBottom, db)) / dbBottom) * laneM.h;
	const opts = {length: durationInFrames, fadeIn: 30, fadeOut: 60, windows: DUCK_WINDOWS, ...DUCK};
	const curve: string[] = [];
	for (let f = 0; f <= durationInFrames; f += 2) {
		curve.push(`${x(f)},${yDb(gainToDb(musicGain(f, opts)))}`);
	}
	const bars: React.ReactNode[] = [];
	if (voice) {
		const d = voice.channelWaveforms[0];
		const n = 200;
		const step = durationInFrames / n;
		for (let i = 0; i < n; i++) {
			const f0 = i * step;
			const vf = voiceFileFrame(f0);
			let rms = 0;
			if (vf !== null) {
				const s0 = Math.floor((vf / fps) * voice.sampleRate);
				const s1 = s0 + Math.floor((step / fps) * voice.sampleRate);
				let sum = 0;
				let k = 0;
				for (let q = Math.max(0, s0); q < Math.min(d.length, s1); q += 8) {
					sum += d[q] * d[q];
					k++;
				}
				rms = k ? Math.sqrt(sum / k) : 0;
			}
			const h = Math.max(2 * unit, Math.min(1, rms * 4) * laneV.h);
			bars.push(<rect key={i} x={x(f0)} y={laneV.top + (laneV.h - h) / 2} width={(W / n) * 0.6} height={h} rx={2 * unit} fill={t.colors.accent2} opacity={f0 <= frame ? 1 : 0.35} />);
		}
	}
	const g = musicGain(frame, opts);
	const db = gainToDb(g);
	const laneLabel = (text: string, top: number, value?: string) => (
		<div style={{position: 'absolute', left: safe.x, top}}>
			<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 24 * unit, color: t.colors.muted, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase'}}>{text}</div>
			{value ? <div style={{fontFamily: t.type.mono, fontSize: 44 * unit, fontWeight: 600, color: t.colors.text, fontVariantNumeric: 'tabular-nums', marginTop: 6 * unit}}>{value}</div> : null}
		</div>
	);
	const chip = (text: string, color: string) => (
		<div style={{display: 'flex', alignItems: 'center', gap: 12 * unit, fontFamily: t.type.body, fontSize: 24 * unit, color: t.colors.muted}}>
			<div style={{width: 16 * unit, height: 16 * unit, borderRadius: 4 * unit, background: color}} />
			{text}
		</div>
	);
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Music src={media('music.m4a')} duck={DUCK_WINDOWS} {...DUCK} fadeIn={30} fadeOut={60} />
			<Voice src={media('voice.m4a')} from={VA.from} trimAfter={VA.trimAfter} />
			<Voice src={media('voice.m4a')} from={VB.from} trimBefore={VB.trimBefore} />
			<div style={{position: 'absolute', left: safe.x, top: safe.y}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 60 * unit, lineHeight: 1.1, letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>The bed ducks under the voice</div>
				<div style={{fontFamily: t.type.body, fontSize: 28 * unit, color: t.colors.muted, marginTop: 8 * unit}}>Down under each line, up in long gaps</div>
			</div>
			<svg width={safe.x + safe.w} height={laneM.top + laneM.h + 40 * unit} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				{DUCK_WINDOWS.map(([s0, e0], i) => (
					<rect key={i} x={x(s0)} y={laneV.top - 16 * unit} width={x(e0) - x(s0)} height={laneM.top + laneM.h - laneV.top + 32 * unit} fill={t.colors.accent2} opacity={0.07} rx={10 * unit} />
				))}
				{[0, -6, -12, -24, -36].map((v) => (
					<g key={v}>
						<line x1={left} x2={left + W} y1={yDb(v)} y2={yDb(v)} stroke={t.colors.line} strokeWidth={1.5 * unit} />
						<text x={left - 14 * unit} y={yDb(v) + 8 * unit} textAnchor="end" fill={t.colors.faint} style={{fontFamily: t.type.mono, fontSize: 22 * unit}}>
							{v === 0 ? '0 dB' : `${v}`}
						</text>
					</g>
				))}
				{bars}
				<polygon points={[`${left},${yDb(-99)}`, ...curve, `${x(durationInFrames)},${yDb(-99)}`].join(' ')} fill={t.colors.accent} opacity={0.16} />
				<polyline points={curve.join(' ')} fill="none" stroke={t.colors.accent} strokeWidth={4 * unit} strokeLinejoin="round" />
				<line x1={x(frame)} x2={x(frame)} y1={laneV.top - 26 * unit} y2={laneM.top + laneM.h + 8 * unit} stroke={t.colors.text} strokeWidth={3 * unit} />
				<circle cx={x(frame)} cy={yDb(db)} r={10 * unit} fill={t.colors.accent} stroke={t.colors.bg} strokeWidth={4 * unit} />
			</svg>
			{laneLabel('Voice', laneV.top + laneV.h / 2 - 14 * unit)}
			{laneLabel('Music', laneM.top, Number.isFinite(db) ? `${db.toFixed(1)} dB` : 'silent')}
			<div style={{position: 'absolute', left, top: safe.y + safe.h - 34 * unit, display: 'flex', gap: 44 * unit}}>
				{chip('bed 0.5, -6 dB', t.colors.accent)}
				{chip('under the voice 0.06, -24 dB', t.colors.accent)}
				{chip('voice windows', t.colors.accent2)}
				{chip('30-frame ramps, pauses under 2.3 s stay down', t.colors.faint)}
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ Visualisers

const VisualizerDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const music = media('music.m4a');
	const note = (text: string) => <div style={{fontFamily: t.type.mono, fontSize: 24 * unit, color: t.colors.muted, marginTop: 16 * unit}}>{text}</div>;
	return (
		<AbsoluteFill style={{background: t.colors.bg}}>
			<Music src={music} level={0.7} fadeIn={10} fadeOut={30} />
			<Animate in="fade" style={{position: 'absolute', left: safe.x, top: safe.y + 20 * unit, width: safe.w, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
				<AudioBars src={music} bars={36} mirror align="center" width={1560} height={380} color={t.colors.accent} color2={t.colors.accent2} />
				{note('AudioBars: 36 log-spaced bands, mirrored, falling like a meter')}
			</Animate>
			<Animate in="fade" delay={6} style={{position: 'absolute', left: safe.x + 60 * unit, top: safe.y + 560 * unit}}>
				<AudioWave src={music} variant="line" width={900} height={250} color={t.colors.accent} glow />
				{note('AudioWave line: the live waveform')}
			</Animate>
			<Animate in="pop" delay={10} style={{position: 'absolute', left: safe.x + safe.w - 560 * unit, top: safe.y + 480 * unit, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
				<AudioCircle src={music} size={250} length={70} bars={30} color={t.colors.accent2}>
					<div style={{width: '100%', height: '100%', background: `radial-gradient(circle at 35% 30%, ${t.colors.accent}, ${t.colors.bg2} 75%)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 56 * unit, color: t.colors.text}}>
						120
					</div>
				</AudioCircle>
				{note('AudioCircle: a ring around a cover')}
			</Animate>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ Audiogram (9:16)

const Cover: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{width: '100%', height: '100%', background: `linear-gradient(140deg, ${t.colors.accent} 0%, #7C3AED 55%, ${t.colors.accent2} 100%)`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#fff'}}>
			<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 120 * unit, lineHeight: 0.9, letterSpacing: '-0.04em'}}>TC</div>
			<div style={{fontFamily: t.type.body, fontWeight: 700, fontSize: 22 * unit, letterSpacing: '0.3em', marginTop: 10 * unit}}>THE CUT</div>
		</div>
	);
};

const AudiogramDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	return (
		<>
			<Music src={media('music.m4a')} duck={speechWindows(WORDS, fps)} level={0.35} duckTo={0.05} fadeIn={20} fadeOut={40} />
			<Audiogram
				src={media('voice.m4a')}
				title="Why every edit starts with the voice"
				show="The Cut"
				episode="EP 12"
				cover={<Cover />}
				captions={<Caption words={WORDS} ms={(frame / fps) * 1000} />}
			/>
		</>
	);
};

const CoverBn: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{width: '100%', height: '100%', background: `linear-gradient(150deg, ${t.colors.accent} 0%, ${t.colors.accent2} 100%)`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#fff'}}>
			<div style={{fontFamily: t.type.bangla, fontWeight: 800, fontSize: 104 * unit, lineHeight: 1.1}}>কাট</div>
			<div style={{fontFamily: t.type.bangla, fontWeight: 600, fontSize: 30 * unit, marginTop: 4 * unit}}>পডকাস্ট</div>
		</div>
	);
};

const AudiogramBanglaDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	return (
		<>
			<Music src={media('music.m4a')} duck={speechWindows(WORDS, fps)} level={0.35} duckTo={0.05} fadeIn={20} fadeOut={40} />
			<Audiogram
				src={media('voice.m4a')}
				title="এডিট কেন ভয়েস দিয়েই শুরু হয়"
				show="দ্য কাট"
				episode="পর্ব ১২"
				cover={<CoverBn />}
				captions={<Caption words={BN_WORDS} ms={(frame / fps) * 1000} />}
			/>
		</>
	);
};

// ------------------------------------------------------------------ Beat montage

const SHOT_WORDS = ['City', 'Coast', 'Peaks', 'Voice'];

const BeatHud: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, width} = useStage();
	const grid = useBeatGrid(MUSIC_BPM);
	const b = beatAt(frame, grid);
	return (
		<div style={{position: 'absolute', left: width / 2, top: safe.y + safe.h - 70 * unit, translate: '-50% 0', display: 'flex', alignItems: 'center', gap: 22 * unit, padding: `${16 * unit}px ${28 * unit}px`, borderRadius: 999, background: t.colors.bg}}>
			{[0, 1, 2, 3].map((i) => (
				<BeatPulse key={i} bpm={MUSIC_BPM} every={4} phase={i} amount={0.5} decay={10}>
					<div style={{width: 24 * unit, height: 24 * unit, borderRadius: 12 * unit, background: b.beatInBar === i ? t.colors.accent : t.colors.faint}} />
				</BeatPulse>
			))}
			<div style={{fontFamily: t.type.mono, fontSize: 26 * unit, color: t.colors.text, marginLeft: 8 * unit, fontVariantNumeric: 'tabular-nums'}}>
				BAR {b.bar + 1} BEAT {b.beatInBar + 1}
			</div>
		</div>
	);
};

const ShotWord: React.FC<{word: string}> = ({word}) => {
	const t = useTheme();
	const {unit, safe} = useStage();
	return (
		<div style={{position: 'absolute', left: safe.x, top: safe.y}}>
			<Animate in="wipe" out="fade" duration={at30(7, FPS)} outDuration={at30(6, FPS)}>
				<div style={{background: t.colors.bg, padding: `${6 * unit}px ${26 * unit}px ${2 * unit}px`, fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 120 * unit, lineHeight: 1.05, color: t.colors.accent, textTransform: 'uppercase'}}>{word}</div>
			</Animate>
		</div>
	);
};

const BeatDemo: React.FC = () => (
	<AbsoluteFill style={{background: '#000'}}>
		<Music src={media('music.m4a')} level={0.7} fadeIn={4} fadeOut={20} />
		<OnBeats bpm={MUSIC_BPM} beats={4}>
			<AbsoluteFill>
				<Clip src={media('cam-a.mp4')} muted />
				<ShotWord word={SHOT_WORDS[0]} />
			</AbsoluteFill>
			<AbsoluteFill>
				<Clip src={media('cam-b.mp4')} trimBefore={30} muted />
				<ShotWord word={SHOT_WORDS[1]} />
			</AbsoluteFill>
			<AbsoluteFill>
				<KenBurns src={media('still.jpg')} move="in" amount={0.12} focus={[0.62, 0.5]} ease={curves.linear} />
				<ShotWord word={SHOT_WORDS[2]} />
			</AbsoluteFill>
			<AbsoluteFill>
				<Clip src={media('talk.mp4')} trimBefore={20} muted />
				<ShotWord word={SHOT_WORDS[3]} />
			</AbsoluteFill>
		</OnBeats>
		<Sfx src={media('whoosh.wav')} at={60} hit={10} volume={0.3} />
		<BeatHud />
	</AbsoluteFill>
);

export const demos: DemoDef[] = [
	{id: 'DemoEditClip', component: () => <Themed theme="studio"><ClipDemo /></Themed>, durationInFrames: CLIP_OUT - CLIP_IN},
	{id: 'DemoEditClipVertical', component: () => <Themed theme="midnight"><ClipVerticalDemo /></Themed>, durationInFrames: 150, width: 1080, height: 1920},
	{id: 'DemoEditFreeze', component: () => <Themed theme="studio"><FreezeDemo /></Themed>, durationInFrames: 150},
	{id: 'DemoEditEngines', component: () => <Themed theme="studio"><EnginesDemo /></Themed>, durationInFrames: 90},
	{id: 'DemoEditKenBurns', component: () => <Themed theme="studio"><KenBurnsDemo /></Themed>, durationInFrames: 180},
	{id: 'DemoEditJumpCuts', component: () => <Themed theme="midnight"><JumpCutsDemo /></Themed>, durationInFrames: JUMP_LENGTH},
	{id: 'DemoEditSpeedRamp', component: () => <Themed theme="studio"><SpeedRampDemo /></Themed>, durationInFrames: 180},
	{id: 'DemoEditSplit', component: () => <Themed theme="studio"><SplitDemo /></Themed>, durationInFrames: 150},
	{id: 'DemoEditSplitVertical', component: () => <Themed theme="midnight"><SplitVerticalDemo /></Themed>, durationInFrames: 150, width: 1080, height: 1920},
	{id: 'DemoEditPip', component: () => <Themed theme="midnight"><PipDemo /></Themed>, durationInFrames: 150},
	{id: 'DemoEditLayoutSwitch', component: () => <Themed theme="studio"><LayoutSwitchDemo /></Themed>, durationInFrames: 240},
	{id: 'DemoEditLetterbox', component: () => <Themed theme="trailer"><LetterboxDemo /></Themed>, durationInFrames: 150},
	{id: 'DemoEditDucking', component: () => <Themed theme="midnight"><DuckingDemo /></Themed>, durationInFrames: DUCK_LENGTH},
	{id: 'DemoEditVisualizer', component: () => <Themed theme="neon"><VisualizerDemo /></Themed>, durationInFrames: 240},
	{id: 'DemoEditAudiogram', component: () => <Themed theme="studio"><AudiogramDemo /></Themed>, durationInFrames: 330, width: 1080, height: 1920},
	{id: 'DemoEditAudiogramBangla', component: () => <Themed theme="dhaka"><AudiogramBanglaDemo /></Themed>, durationInFrames: 330, width: 1080, height: 1920},
	{id: 'DemoEditBeat', component: () => <Themed theme="kinetic"><BeatDemo /></Themed>, durationInFrames: 240},
];
