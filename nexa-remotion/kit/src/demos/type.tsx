import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {SafeArea, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate, PushIn} from '../kit/motion';
import {
	Annotate,
	BigStatement,
	BoxedCaptions,
	Counter,
	FitText,
	KeySounds,
	Kicker,
	KineticTitle,
	Label,
	LineStack,
	Marker,
	Quote,
	Scramble,
	SplitText,
	SubtitleFile,
	TextPlate,
	TikTokCaptions,
	Typewriter,
	WordRotator,
	toCaptions,
	typewriterSchedule,
} from '../kit/type';

// ---------------------------------------------------------------- shared pieces

const Ground: React.FC<{children?: React.ReactNode}> = ({children}) => {
	const t = useTheme();
	return <AbsoluteFill style={{background: t.colors.bg}}>{children}</AbsoluteFill>;
};

const Themed: React.FC<{theme: ThemeName; children: React.ReactNode}> = ({theme, children}) => (
	<ThemeProvider theme={theme}>
		<Ground>{children}</Ground>
	</ThemeProvider>
);

// A stand-in for video footage under captions: soft light on a dark scene, with a slow push like a held shot.
const Footage: React.FC<{warm?: boolean}> = ({warm = false}) => (
	<AbsoluteFill style={{background: '#0d1117'}}>
		<PushIn amount={0.05}>
			<AbsoluteFill
				style={{
					background: warm
						? 'radial-gradient(60% 45% at 30% 28%, rgba(255, 176, 102, 0.55), transparent 70%), radial-gradient(55% 40% at 78% 72%, rgba(90, 120, 170, 0.5), transparent 70%), linear-gradient(170deg, #2a2320 0%, #121417 100%)'
						: 'radial-gradient(55% 40% at 28% 30%, rgba(96, 150, 190, 0.55), transparent 70%), radial-gradient(50% 42% at 75% 68%, rgba(210, 140, 90, 0.42), transparent 70%), linear-gradient(170deg, #1d2833 0%, #0e1115 100%)',
				}}
			/>
			<AbsoluteFill style={{background: 'radial-gradient(90% 80% at 50% 45%, transparent 55%, rgba(0, 0, 0, 0.55) 100%)'}} />
		</PushIn>
	</AbsoluteFill>
);

// transcripts: whisper-style words in seconds, converted with toCaptions()
const EN_WORDS: [string, number, number][] = [
	['Most', 0.0, 0.22],
	['teams', 0.22, 0.56],
	['lose', 0.56, 0.82],
	['four', 0.82, 1.1],
	['hours', 1.1, 1.42],
	['a', 1.42, 1.5],
	['week', 1.5, 1.78],
	['to', 1.78, 1.88],
	['status', 1.88, 2.26],
	['meetings.', 2.26, 2.8],
	['We', 3.15, 3.3],
	['cut', 3.3, 3.52],
	['ours', 3.52, 3.8],
	['to', 3.8, 3.9],
	['fifteen', 3.9, 4.35],
	['minutes.', 4.35, 4.9],
	['Here', 5.3, 5.45],
	['is', 5.45, 5.56],
	['the', 5.56, 5.66],
	['one', 5.66, 5.9],
	['change', 5.9, 6.25],
	['that', 6.25, 6.4],
	['did', 6.4, 6.6],
	['it.', 6.6, 6.95],
];

const EN = toCaptions(
	EN_WORDS.map(([word, start, end]) => ({word, start, end})),
	{offsetMs: 250},
);

const BN_WORDS: [string, number, number][] = [
	['প্রতি', 0.0, 0.3],
	['সপ্তাহে', 0.3, 0.8],
	['চার', 0.8, 1.08],
	['ঘণ্টা', 1.08, 1.45],
	['শুধু', 1.45, 1.75],
	['মিটিংয়েই', 1.75, 2.35],
	['চলে', 2.35, 2.6],
	['যায়।', 2.6, 3.05],
	['আমরা', 3.45, 3.8],
	['সেটা', 3.8, 4.1],
	['নামিয়ে', 4.1, 4.55],
	['এনেছি', 4.55, 4.95],
	['পনেরো', 4.95, 5.4],
	['মিনিটে।', 5.4, 6.0],
];

const BN = toCaptions(
	BN_WORDS.map(([text, start, end]) => ({text, start, end})),
	{offsetMs: 250},
);

// ---------------------------------------------------------------- words and titles

const Words: React.FC = () => (
	<Themed theme="studio">
		<SafeArea justify="center" gap={64}>
			<div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
				<Kicker text="By word" out />
				<SplitText text="Every frame is a pure function of time" size={84} in="rise" out="fade" outEach={2} delay={6} />
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
				<Kicker text="By character" delay={14} out />
				<SplitText text="Launch" size={150} in="pop" delay={20} out="fade" />
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
				<Kicker text="By line, measured" delay={28} out />
				<SplitText
					text="Lines are measured after the fonts load, so the reveal knows where each line breaks before the first frame."
					by="line"
					in="mask"
					out="mask"
					maxWidth={1100}
					size={52}
					role="body"
					strong
					delay={34}
				/>
			</div>
		</SafeArea>
	</Themed>
);

const Subline: React.FC<{text: string; delay: number; align?: 'left' | 'center'}> = ({text, delay, align = 'left'}) => {
	const t = useTheme();
	return <SplitText text={text} role="body" size={40} color={t.colors.muted} in="rise" delay={delay} each={2} align={align} out="fade" />;
};

const Title: React.FC = () => (
	<>
		<Sequence durationInFrames={90}>
			<Themed theme="studio">
				<SafeArea justify="center" gap={34}>
					<Kicker text="Release 4.2" out />
					<KineticTitle text="Ship the update your users actually asked for" emphasis="actually" out="mask" delay={8} />
					<Subline text="Written from 1,200 support tickets, not a roadmap meeting." delay={40} />
				</SafeArea>
			</Themed>
		</Sequence>
		<Sequence from={90} durationInFrames={90}>
			<Themed theme="midnight">
				<SafeArea justify="center" align="center" gap={34}>
					<KineticTitle text={'Faster reviews.\nFewer meetings.'} by="line" align="center" emphasis="Fewer" emphasisStyle="color" out="mask" outEach={3} />
					<Subline text="Async updates that people actually read" delay={24} align="center" />
				</SafeArea>
			</Themed>
		</Sequence>
		<Sequence from={180} durationInFrames={90}>
			<Themed theme="kinetic">
				<SafeArea justify="center">
					<KineticTitle text="Built for the teams who ship on Fridays" size={150} emphasis="Fridays" emphasisStyle="marker" out="mask" />
				</SafeArea>
			</Themed>
		</Sequence>
	</>
);

// ---------------------------------------------------------------- typewriter, scramble, rotator

const TYPE_LINES = ['Good products feel obvious.', 'Getting there never is.'];
const TYPE_TIMING = {delay: 10, cps: 16, seed: 'hello'};

const TERMINAL_LINES = ['$ nrk.py new launch-video --format shorts', 'project ready: 1080x1920, 30 fps, 20 s', '$ nrk.py stills launch-video'];
const TERMINAL_TIMING = {delay: 10, cps: 30, pauses: {line: 16}, instant: [1], seed: 'term'};

const TerminalCard: React.FC = () => {
	const t = useTheme();
	const {unit, fps} = useStage();
	const sched = typewriterSchedule(TERMINAL_LINES, fps, TERMINAL_TIMING);
	return (
		<div
			style={{
				width: 1320 * unit,
				borderRadius: 18 * unit,
				background: t.colors.surface,
				border: `${1.5 * unit}px solid ${t.colors.line}`,
				boxShadow: `0 ${30 * unit}px ${80 * unit}px rgba(0, 0, 0, 0.45)`,
				overflow: 'hidden',
			}}
		>
			<div style={{display: 'flex', gap: 10 * unit, padding: `${18 * unit}px ${22 * unit}px`, borderBottom: `${1.5 * unit}px solid ${t.colors.line}`}}>
				{['#F85149', '#D29922', '#3FB950'].map((c) => (
					<div key={c} style={{width: 14 * unit, height: 14 * unit, borderRadius: 99, background: c, opacity: 0.85}} />
				))}
			</div>
			<div style={{padding: `${34 * unit}px ${40 * unit}px ${40 * unit}px`}}>
				<Typewriter text={TERMINAL_LINES.join('\n')} size={38} role="mono" caret="block" lineHeight={1.7} {...TERMINAL_TIMING} />
			</div>
			<KeySounds frames={sched.keys} volume={0.25} />
		</div>
	);
};

const TypewriterDemo: React.FC = () => {
	const {fps} = useStage();
	const sched = typewriterSchedule(TYPE_LINES, fps, TYPE_TIMING);
	return (
		<>
			<Sequence durationInFrames={150}>
				<Themed theme="studio">
					<SafeArea justify="center" align="center">
						<Typewriter text={TYPE_LINES.join('\n')} role="display" size={88} align="center" {...TYPE_TIMING} />
					</SafeArea>
					<KeySounds frames={sched.keys} />
				</Themed>
			</Sequence>
			<Sequence from={150} durationInFrames={150}>
				<Themed theme="terminal">
					<SafeArea justify="center" align="center">
						<TerminalCard />
					</SafeArea>
				</Themed>
			</Sequence>
		</>
	);
};

const ScrambleDemo: React.FC = () => (
	<Themed theme="neon">
		<SafeArea justify="center" align="center" gap={90}>
			<Scramble text="ACCESS GRANTED" role="mono" size={112} delay={6} align="center" />
			<Animate in="rise" delay={30}>
				<WordRotator prefix="Built for " words={['designers', 'developers', 'founders', 'small teams']} size={76} delay={56} hold={18} transition={12} align="center" />
			</Animate>
		</SafeArea>
	</Themed>
);

// ---------------------------------------------------------------- numbers and fitting

const Stat: React.FC<{label: string; children: React.ReactNode; delay: number}> = ({label, children, delay}) => {
	const t = useTheme();
	return (
		<div style={{display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'flex-start'}}>
			{children}
			<SplitText text={label} role="body" size={30} color={t.colors.muted} in="rise" delay={delay + 30} />
		</div>
	);
};

const CounterDemo: React.FC = () => (
	<Themed theme="data">
		<SafeArea justify="center" gap={70}>
			<Kicker text="Q3 in numbers" />
			<div style={{display: 'grid', gridTemplateColumns: 'repeat(4, auto)', justifyContent: 'space-between', width: '100%'}}>
				<Stat label="Revenue this month" delay={6}>
					<Counter to={24813} format="currency" currency="USD" size={112} delay={6} />
				</Stat>
				<Stat label="Uptime" delay={12}>
					<Counter to={99.98} decimals={2} suffix="%" affixScale={0.5} size={112} delay={12} />
				</Stat>
				<Stat label="App downloads" delay={18}>
					<Counter to={1240000} format="compact" size={112} delay={18} />
				</Stat>
				<Stat label="Orders shipped" delay={24}>
					<Counter to={12480} mode="roll" size={112} delay={24} duration={60} />
				</Stat>
			</div>
		</SafeArea>
	</Themed>
);

const FitRow: React.FC<{text: string; lines?: number; delay: number}> = ({text, lines = 1, delay}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{width: 860 * unit, borderLeft: `${4 * unit}px solid ${t.colors.accent}`, paddingLeft: 26 * unit}}>
			<FitText text={text} maxWidth={860 - 30} maxLines={lines} maxSize={260} in="mask" delay={delay} />
		</div>
	);
};

const FitDemo: React.FC = () => (
	<Themed theme="swiss">
		<SafeArea justify="center" gap={46}>
			<FitRow text="Q3" delay={4} />
			<FitRow text="Revenue up 38%" delay={12} />
			<FitRow text="Revenue grew faster than in any quarter since we launched" lines={3} delay={20} />
		</SafeArea>
	</Themed>
);

// ---------------------------------------------------------------- highlights, plates, statements

const HighlightDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const body = {fontFamily: t.type.serif, fontSize: 76 * unit, lineHeight: 1.22, color: t.colors.text, letterSpacing: '-0.01em'};
	const small = {fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 44 * unit, color: t.colors.text};
	return (
		<SafeArea justify="center" gap={70}>
			<div style={{...body, maxWidth: 1500 * unit}}>
				{'Most teams lose '}
				<Annotate kind="circle" delay={34} role="serif">
					four hours
				</Annotate>
				{' every week to '}
				<Marker delay={10} duration={36}>
					status meetings that could have been one short written update.
				</Marker>
			</div>
			<div style={{display: 'flex', gap: 70 * unit, alignItems: 'center', ...small}}>
				<Annotate kind="highlight" delay={60} role="body">
					highlight
				</Annotate>
				<Annotate kind="underline" delay={66} role="body">
					underline
				</Annotate>
				<Annotate kind="box" delay={72} role="body">
					box
				</Annotate>
				<Annotate kind="strike" delay={78} role="body">
					strike
				</Annotate>
				<Annotate kind="cross" delay={84} role="body">
					cross
				</Annotate>
				<Annotate kind="bracket" delay={90} role="body">
					bracket
				</Annotate>
			</div>
		</SafeArea>
	);
};

const HighlightThemed: React.FC = () => (
	<Themed theme="editorial">
		<HighlightDemo />
	</Themed>
);

const PlateDemo: React.FC = () => (
	<ThemeProvider theme="studio">
		<Footage warm />
		<SafeArea justify="center" align="center" gap={60}>
			<TextPlate text="The quiet part of every launch nobody films" size={66} delay={6} />
			<TextPlate text="Watch till the end" tone="accent" size={46} delay={40} plateIn="wipe" />
		</SafeArea>
		{/* 9:16 subtitles: 32 characters a line, low in the safe area */}
		<BoxedCaptions captions={EN} />
	</ThemeProvider>
);

const StatementDemo: React.FC = () => (
	<Themed theme="studio">
		<SafeArea justify="center" gap={40}>
			<div style={{display: 'flex', gap: 16}}>
				<Label text="Case study" delay={4} />
				<Label text="Engineering" variant="outline" delay={8} />
			</div>
			<BigStatement word="3x" note="faster code reviews since the team moved to written updates" notePosition="right" delay={10} />
		</SafeArea>
	</Themed>
);

const QuoteDemo: React.FC = () => (
	<>
		<Sequence durationInFrames={150}>
			<Themed theme="editorial">
				<SafeArea justify="center">
					<Quote
						text="We stopped measuring how busy people looked and started measuring what they shipped."
						author="Maya Chen"
						title="Head of Product, Northwind"
						delay={6}
					/>
				</SafeArea>
			</Themed>
		</Sequence>
		<Sequence from={150} durationInFrames={150}>
			<Themed theme="luxury">
				<SafeArea justify="center" align="center">
					<LineStack
						lines={['Some things are made slowly.', 'By hand, in small batches.', 'For people who notice.']}
						each={36}
						delay={8}
						align="center"
						size={70}
						role="serif"
					/>
				</SafeArea>
			</Themed>
		</Sequence>
	</>
);

// ---------------------------------------------------------------- captions

const StyleTag: React.FC<{text: string}> = ({text}) => (
	<SafeArea justify="start" align="center">
		<Kicker text={text} color="#FFFFFF" />
	</SafeArea>
);

const CAPTION_SEGMENT = 228;

const CaptionsDemo: React.FC = () => (
	<ThemeProvider theme="midnight">
		<Footage />
		<Sequence durationInFrames={CAPTION_SEGMENT}>
			<StyleTag text="Gliding pill" />
			<TikTokCaptions captions={EN} highlight="pill" />
		</Sequence>
		<Sequence from={CAPTION_SEGMENT} durationInFrames={CAPTION_SEGMENT}>
			<StyleTag text="Karaoke fill" />
			<TikTokCaptions captions={EN} highlight="karaoke" />
		</Sequence>
	</ThemeProvider>
);

const CaptionsPopDemo: React.FC = () => (
	<ThemeProvider theme="fresh">
		<Footage warm />
		<Sequence durationInFrames={CAPTION_SEGMENT}>
			<StyleTag text="Word pop and scale" />
			<TikTokCaptions captions={EN} highlight="scale" reveal="word" />
		</Sequence>
		<Sequence from={CAPTION_SEGMENT} durationInFrames={CAPTION_SEGMENT}>
			<StyleTag text="Plate" />
			<TikTokCaptions captions={EN} highlight="color" plate="light" activeColor="#E5484D" position={0.62} />
		</Sequence>
	</ThemeProvider>
);

const CaptionsWideDemo: React.FC = () => (
	<ThemeProvider theme="studio">
		<Footage />
		{/* writes out/<composition>/subtitles.srt next to a render, for YouTube */}
		<SubtitleFile captions={EN} />
		<Sequence durationInFrames={CAPTION_SEGMENT}>
			<BoxedCaptions captions={EN} readAlong />
		</Sequence>
		<Sequence from={CAPTION_SEGMENT} durationInFrames={CAPTION_SEGMENT}>
			<TikTokCaptions captions={EN} highlight="color" />
		</Sequence>
	</ThemeProvider>
);

// ---------------------------------------------------------------- Bangla

const BanglaDemo: React.FC = () => {
	const t = useTheme();
	return (
		<>
			<Sequence durationInFrames={120}>
				<Ground>
					<SafeArea justify="center" gap={40}>
						<Kicker text="নতুন আপডেট" />
						<KineticTitle text="মিটিং কম, কাজ বেশি" emphasis="বেশি" size={150} out="mask" delay={6} />
						<Typewriter text="চলুন, শুরু করা যাক।" role="body" size={46} delay={40} cps={12} color={t.colors.muted} />
					</SafeArea>
				</Ground>
			</Sequence>
			<Sequence from={120} durationInFrames={105}>
				<Ground>
					<SafeArea justify="center" align="center" gap={24}>
						<Counter to={12450} digits="bangla" size={170} delay={4} align="center" />
						<SplitText text="ঘণ্টা বাঁচল এ বছর" role="body" size={48} color={t.colors.muted} in="rise" delay={30} align="center" />
					</SafeArea>
				</Ground>
			</Sequence>
			<Sequence from={225} durationInFrames={215}>
				<Footage />
				<TikTokCaptions captions={BN} highlight="pill" />
			</Sequence>
		</>
	);
};

const BanglaThemed: React.FC = () => (
	<ThemeProvider theme="dhaka">
		<BanglaDemo />
	</ThemeProvider>
);

// every other component with Bangla copy: grapheme splitting, scramble, rotator, marker, annotation, plate, fit
const BanglaKitDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const cell: React.CSSProperties = {display: 'flex', flexDirection: 'column', gap: 16 * unit};
	return (
		<Ground>
			<SafeArea justify="center">
				<div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 90 * unit, rowGap: 64 * unit, width: '100%'}}>
					<div style={cell}>
						<Kicker text="By character" />
						<SplitText text="স্বাগতম" size={110} in="pop" delay={6} />
					</div>
					<div style={cell}>
						<Kicker text="Scramble" delay={6} />
						<Scramble text="তথ্য যাচাই হয়েছে" size={70} delay={10} />
					</div>
					<div style={cell}>
						<Kicker text="Rotator" delay={12} />
						<Animate in="rise" delay={16}>
							<WordRotator words={['ডিজাইনারদের', 'ডেভেলপারদের', 'ছোট টিমের']} suffix=" জন্য বানানো" size={64} delay={40} hold={24} />
						</Animate>
					</div>
					<div style={cell}>
						<Kicker text="Marker and circle" delay={18} />
						<Animate in="rise" delay={22}>
						<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 52 * unit, lineHeight: 1.5, color: t.colors.text}}>
							{'প্রতি সপ্তাহে '}
							<Annotate kind="circle" role="body" delay={40}>
								চার ঘণ্টা
							</Annotate>
							{' যায় '}
							<Marker delay={30}>শুধু মিটিংয়ে</Marker>
						</div>
						</Animate>
					</div>
					<div style={cell}>
						<Kicker text="Fit text" delay={24} />
						<FitText text="৩৮% বেশি আয়" maxWidth={700} maxSize={150} in="mask" delay={28} />
					</div>
					<div style={cell}>
						<Kicker text="Plate" delay={30} />
						<TextPlate text="আসল কাজটা হয় ক্যামেরার পেছনে" size={46} align="left" maxWidth={720} delay={34} tone="accent" out={false} />
					</div>
				</div>
			</SafeArea>
		</Ground>
	);
};

const BanglaKitThemed: React.FC = () => (
	<ThemeProvider theme="dhaka">
		<BanglaKitDemo />
	</ThemeProvider>
);

export const demos: DemoDef[] = [
	{id: 'DemoTypeWords', component: Words, durationInFrames: 120},
	{id: 'DemoTypeTitle', component: Title, durationInFrames: 270},
	{id: 'DemoTypeTypewriter', component: TypewriterDemo, durationInFrames: 300},
	{id: 'DemoTypeScramble', component: ScrambleDemo, durationInFrames: 150},
	{id: 'DemoTypeCounter', component: CounterDemo, durationInFrames: 120},
	{id: 'DemoTypeFit', component: FitDemo, durationInFrames: 75},
	{id: 'DemoTypeHighlight', component: HighlightThemed, durationInFrames: 150},
	{id: 'DemoTypePlate', component: PlateDemo, durationInFrames: 228, width: 1080, height: 1920},
	{id: 'DemoTypeStatement', component: StatementDemo, durationInFrames: 120},
	{id: 'DemoTypeQuote', component: QuoteDemo, durationInFrames: 300},
	{id: 'DemoTypeCaptions', component: CaptionsDemo, durationInFrames: CAPTION_SEGMENT * 2, width: 1080, height: 1920},
	{id: 'DemoTypeCaptionsPop', component: CaptionsPopDemo, durationInFrames: CAPTION_SEGMENT * 2, width: 1080, height: 1920},
	{id: 'DemoTypeCaptionsWide', component: CaptionsWideDemo, durationInFrames: CAPTION_SEGMENT * 2},
	{id: 'DemoTypeBangla', component: BanglaThemed, durationInFrames: 440, width: 1080, height: 1920},
	{id: 'DemoTypeBanglaKit', component: BanglaKitThemed, durationInFrames: 150},
];
