import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {at30, curves, rand, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate, Camera, Float, ramp, springAt, Stagger} from '../kit/motion';
import {
	BrowserWindow,
	ChapterBar,
	ChatThread,
	ClickSounds,
	CodeBlock,
	Countdown,
	Cursor,
	cursorPose,
	cursorTimeline,
	DeviceRise,
	EndCard,
	FocusRing,
	FormField,
	KeyCombo,
	LaptopFrame,
	LogoReveal,
	LowerThird,
	MacWindow,
	Notification,
	NotificationStack,
	PhoneFrame,
	phoneScreen,
	Pressable,
	ScrollView,
	SearchBar,
	SectionTitle,
	Subscribe,
	subscribeClicks,
	TapIndicator,
	Terminal,
	TitleCard,
	Toggle,
	UI_MARKS,
	UiBackdrop,
	UiButton,
	UiIcon,
	uiPalette,
	UiTooltip,
	useUiTyping,
	type CursorKey,
	type LogoRevealVariant,
	type TermLine,
	type UiIconName,
} from '../kit/ui';

const themed =
	(theme: ThemeName, C: React.FC): React.FC =>
	() => (
		<ThemeProvider theme={theme}>
			<C />
		</ThemeProvider>
	);

// ------------------------------------------------------------------ shared stand-ins

/** A soft interview-room plate standing in for footage: window light, bokeh, a blurred subject, a slow push. */
const Footage: React.FC<{tone?: 'warm' | 'cool'}> = ({tone = 'warm'}) => {
	const frame = useCurrentFrame();
	const {width, height} = useStage();
	const c = tone === 'warm' ? {a: '#2E211B', b: '#7A5238', light: 'rgba(255, 214, 170, 0.55)', dot: '255, 226, 190'} : {a: '#141C27', b: '#35506E', light: 'rgba(170, 205, 255, 0.45)', dot: '200, 225, 255'};
	const push = 1 + 0.05 * Math.min(1, frame / 400);
	return (
		<AbsoluteFill style={{background: `linear-gradient(155deg, ${c.b} 0%, ${c.a} 72%)`, overflow: 'hidden'}}>
			<AbsoluteFill style={{scale: `${push}`}}>
				<div style={{position: 'absolute', left: width * 0.55, top: -height * 0.25, width: width * 0.7, height: height * 1.1, background: `radial-gradient(ellipse at 45% 40%, ${c.light} 0%, rgba(0,0,0,0) 62%)`}} />
				{Array.from({length: 16}).map((_, i) => {
					const r = (22 + rand(`bk-r-${i}`) * 70) * (height / 1080);
					return (
						<div
							key={i}
							style={{
								position: 'absolute',
								left: (0.5 + rand(`bk-x-${i}`) * 0.5) * width - r,
								top: rand(`bk-y-${i}`) * height * 0.8 - r + Math.sin(frame / 60 + i) * 4,
								width: r * 2,
								height: r * 2,
								borderRadius: '50%',
								background: `radial-gradient(circle, rgba(${c.dot}, ${0.1 + rand(`bk-o-${i}`) * 0.16}) 0%, rgba(${c.dot}, 0.04) 60%, rgba(${c.dot}, 0) 72%)`,
							}}
						/>
					);
				})}
				<div style={{position: 'absolute', left: width * 0.3, top: height * 0.2, width: height * 0.36, height: height * 0.42, borderRadius: '50%', background: 'radial-gradient(ellipse at 50% 45%, rgba(20, 14, 12, 0.85) 0%, rgba(20, 14, 12, 0.55) 45%, rgba(20,14,12,0) 70%)'}} />
				<div style={{position: 'absolute', left: width * 0.16, top: height * 0.52, width: height * 0.95, height: height * 0.8, borderRadius: '45% 45% 0 0', background: 'radial-gradient(ellipse at 50% 20%, rgba(18, 13, 11, 0.9) 0%, rgba(18,13,11,0.6) 50%, rgba(18,13,11,0) 72%)'}} />
			</AbsoluteFill>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)'}} />
		</AbsoluteFill>
	);
};

const Label: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	return <div style={{fontFamily: t.type.mono, fontSize: 20 * unit, color: t.colors.muted, letterSpacing: '0.02em', ...style}}>{children}</div>;
};

// ------------------------------------------------------------------ DemoUiCursorShapes: the pointer drawings up close

const Shapes: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const half = (dark: boolean) => (
		<div style={{position: 'relative', flex: 1, background: dark ? '#14161B' : '#F3F4F6'}}>
			{(['arrow', 'hand', 'grab', 'text'] as const).map((s, i) => (
				<div key={s} style={{position: 'absolute', left: (110 + i * 200) * unit, top: 300 * unit}}>
					<Label style={{position: 'absolute', top: -120 * unit, color: dark ? '#9AA1AD' : '#667085'}}>{s}</Label>
					<Cursor keys={[{x: 0, y: 0, at: -10, shape: s}]} size={2.2} appear="none" hideAfter={Infinity} debug={i === 0} />
				</div>
			))}
			<div style={{position: 'absolute', left: 110 * unit, top: 640 * unit}}>
				<Label style={{position: 'absolute', top: -60 * unit, whiteSpace: 'nowrap', color: dark ? '#9AA1AD' : '#667085'}}>tap, long press</Label>
				<TapIndicator taps={[{x: 40, y: 60, at: 4, hold: 40}, {x: 220, y: 60, at: 4, hold: 40, long: true}]} />
			</div>
		</div>
	);
	return (
		<AbsoluteFill style={{flexDirection: 'row', fontFamily: t.type.body}}>
			{half(false)}
			{half(true)}
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiCursor: waypoints, drag, clicks, sound

const BOARD = {w: 1500, h: 700};
const COL_X = [56, 530, 1004];
const CARD = {w: 408, h: 150};
const TOGGLE = {x: 56, y: 608};
const PUBLISH = {x: 1244, y: 50, w: 200, h: 56};

const CURSOR_KEYS: CursorKey[] = [
	{x: 1380, y: 640, at: 6},
	{x: 272, y: 270, at: 36, drag: true},
	{x: 1220, y: 436, at: 70},
	{x: TOGGLE.x + 32, y: TOGGLE.y + 19, at: 104, click: true},
	{x: PUBLISH.x + 120, y: PUBLISH.y + 30, at: 146, click: true},
];

const TaskCard: React.FC<{title: string; tag: string; tagColor: string; who: string; style?: React.CSSProperties; lift?: number}> = ({title, tag, tagColor, who, style, lift = 0}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t);
	return (
		<div
			style={{
				position: 'absolute',
				width: CARD.w * unit,
				height: CARD.h * unit,
				boxSizing: 'border-box',
				padding: 22 * unit,
				borderRadius: 18 * unit,
				background: P.raised,
				boxShadow: `0 0 0 ${unit}px ${P.line}, 0 ${(4 + 18 * lift) * unit}px ${(10 + 30 * lift) * unit}px rgba(16, 24, 40, ${0.08 + 0.12 * lift})`,
				display: 'flex',
				flexDirection: 'column',
				justifyContent: 'space-between',
				fontFamily: t.type.body,
				...style,
			}}
		>
			<div style={{fontSize: 25 * unit, fontWeight: t.weights.strong, color: P.text}}>{title}</div>
			<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
				<span style={{fontSize: 17 * unit, fontWeight: t.weights.strong, color: tagColor, background: `${tagColor}1F`, padding: `${5 * unit}px ${12 * unit}px`, borderRadius: 20 * unit}}>{tag}</span>
				<span style={{width: 36 * unit, height: 36 * unit, borderRadius: '50%', background: P.panel, color: P.muted, fontSize: 14 * unit, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `inset 0 0 0 ${unit}px ${P.line}`}}>{who}</span>
			</div>
		</div>
	);
};

const CursorDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, width, height} = useStage();
	const P = uiPalette(t);
	const tl = React.useMemo(() => cursorTimeline(CURSOR_KEYS, fps), [fps]);
	const pose = cursorPose(tl, frame, fps);
	const dragKey = tl.keys[1];
	const dragging = frame >= (dragKey.press ?? 0) && frame < (dragKey.release ?? 0) + 1;
	const dropped = frame >= (dragKey.release ?? Infinity);
	const grab = {x: 200, y: 60};
	const liftIn = ramp(frame, dragKey.press ?? 0, at30(5, fps), curves.out) * (1 - ramp(frame, dragKey.release ?? Infinity, at30(8, fps), curves.out));
	const cardPos = dragging ? {x: pose.x - grab.x, y: pose.y - grab.y} : dropped ? {x: 1004 + 16, y: 376} : {x: 72, y: 210};
	const slideUp = ramp(frame, (dragKey.press ?? 0) + at30(6, fps), at30(12, fps), curves.inOut);
	const col = (i: number, title: string, count: number) => (
		<div key={title} style={{position: 'absolute', left: COL_X[i] * unit, top: 150 * unit, width: 440 * unit, height: 410 * unit, borderRadius: 22 * unit, background: P.panel, boxShadow: `inset 0 0 0 ${unit}px ${P.line}`}}>
			<div style={{display: 'flex', alignItems: 'center', gap: 10 * unit, padding: `${18 * unit}px ${20 * unit}px`, fontFamily: t.type.body, fontSize: 20 * unit, fontWeight: t.weights.strong, color: P.muted}}>
				{title}
				<span style={{fontSize: 16 * unit, background: P.page, borderRadius: 12 * unit, padding: `${2 * unit}px ${10 * unit}px`, boxShadow: `inset 0 0 0 ${unit}px ${P.line}`}}>{count}</span>
			</div>
		</div>
	);
	const clicks = tl.clicks;
	return (
		<AbsoluteFill>
			<UiBackdrop variant="dots" />
			<div style={{position: 'absolute', left: (width - BOARD.w * unit) / 2, top: (height - BOARD.h * unit) / 2, width: BOARD.w * unit, height: BOARD.h * unit, borderRadius: 30 * unit, background: P.page, boxShadow: `0 0 0 ${unit}px ${P.line}, 0 ${30 * unit}px ${80 * unit}px rgba(16,24,40,0.12)`}}>
				<div style={{position: 'absolute', left: 56 * unit, top: 52 * unit, fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 44 * unit, letterSpacing: `${t.tracking.display}em`, color: P.text}}>Launch checklist</div>
				<div style={{position: 'absolute', left: PUBLISH.x * unit, top: PUBLISH.y * unit}}>
					<UiButton label="Publish" width={PUBLISH.w} icon="sparkle" pressAt={tl.pressOf(4)} hoverAt={tl.arriveOf(4)} doneLabel="Published" doneIcon="check" doneVariant="dark" />
				</div>
				{col(0, 'To do', dropped ? 1 : 2)}
				{col(1, 'In review', 1)}
				{col(2, 'Done', dropped ? 2 : 1)}
				<TaskCard title="Record demo video" tag="Video" tagColor="#7C3AED" who="LO" style={{left: 72 * unit, top: (376 - 166 * slideUp) * unit}} />
				<TaskCard title="Pricing page copy" tag="Copy" tagColor="#D97706" who="AR" style={{left: 546 * unit, top: 210 * unit}} />
				<TaskCard title="Fix login redirect" tag="Bug" tagColor="#DC2626" who="MC" style={{left: 1020 * unit, top: 210 * unit}} />
				<TaskCard title="Write release notes" tag="Docs" tagColor="#2563EB" who="MC" lift={liftIn} style={{left: cardPos.x * unit, top: cardPos.y * unit, rotate: `${2.5 * liftIn}deg`, scale: `${1 + 0.03 * liftIn}`, zIndex: 5}} />
				<div style={{position: 'absolute', left: TOGGLE.x * unit, top: TOGGLE.y * unit, display: 'flex', alignItems: 'center', gap: 16 * unit}}>
					<Toggle on at={tl.pressOf(3)} />
					<span style={{fontFamily: t.type.body, fontSize: 24 * unit, color: P.text}}>Tell the team when it goes live</span>
				</div>
				<Cursor keys={CURSOR_KEYS} />
			</div>
			<ClickSounds frames={clicks} src={staticFile('ui/click.wav')} volume={0.5} />
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiInputs: search, form, toggle, keys (dark)

const InputsDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const P = uiPalette(t);
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: safe.x + 40 * unit, top: safe.y, height: safe.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 40 * unit}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 20 * unit}}>
					<KeyCombo keys={['cmd', 'K']} at={-6} pressAt={16} />
					<span style={{fontFamily: t.type.body, fontSize: 24 * unit, color: P.muted}}>opens search anywhere</span>
				</div>
				<SearchBar text="invoice" placeholder="Search notes, people, files" typeAt={24} cps={9} suggestions={['Invoice template', 'Invoices from March', 'Send an invoice reminder']} pick={1} pickAt={96} hint="Ctrl K" width={760} />
				<div style={{height: 230 * unit}} />
			</div>
			<div style={{position: 'absolute', right: safe.x + 40 * unit, top: safe.y + (safe.h - 700 * unit) / 2, width: 640 * unit, padding: 40 * unit, boxSizing: 'border-box', borderRadius: 28 * unit, background: P.raised, boxShadow: `0 0 0 ${unit}px ${P.line}, 0 ${24 * unit}px ${60 * unit}px rgba(0,0,0,0.4)`, display: 'flex', flexDirection: 'column', gap: 26 * unit}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 40 * unit, color: P.text, letterSpacing: `${t.tracking.display}em`}}>Create your account</div>
				<FormField label="নাম (Name)" value="আরিফ রহমান" typeAt={20} cps={6} blurAt={52} width={560} />
				<FormField label="Email" value="arif@coinlet.example" kind="email" typeAt={58} cps={16} blurAt={96} validAt={98} width={560} />
				<FormField label="Password" value="correct-horse-7" kind="password" typeAt={102} cps={14} blurAt={140} width={560} hint="At least 12 characters" />
				<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
					<span style={{fontFamily: t.type.body, fontSize: 22 * unit, color: P.text}}>Keep me signed in</span>
					<Toggle on at={146} />
				</div>
				<UiButton label="Create account" size="lg" width={560} pressAt={162} doneLabel="Account ready" doneIcon="check" />
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiBrowser: a page, a camera punch-in, a dialog

const PAGE = {w: 1440, h: 762};
const SHARE = {x: 1234, y: 50, w: 150, h: 56};
const DIALOG = {x: 420, y: 186, w: 600, h: 390};
const BROWSER_KEYS: CursorKey[] = [
	{x: 1100, y: 330, at: 84},
	{x: SHARE.x + 96, y: SHARE.y + 30, at: 110, click: true},
	{x: DIALOG.x + 64, y: DIALOG.y + 237, at: 176, click: true},
	{x: DIALOG.x + 478, y: DIALOG.y + 334, at: 204, click: true},
];

const Sidebar: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t);
	const items: [UiIconName, string][] = [
		['home', 'Home'],
		['folder', 'Projects'],
		['file', 'Launch plan'],
		['user', 'Team'],
		['sliders', 'Settings'],
	];
	return (
		<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 260 * unit, background: P.panel, borderRight: `${unit}px solid ${P.line}`, padding: `${28 * unit}px ${18 * unit}px`, boxSizing: 'border-box', fontFamily: t.type.body}}>
			<div style={{display: 'flex', alignItems: 'center', gap: 12 * unit, marginBottom: 30 * unit, paddingLeft: 8 * unit}}>
				<div style={{width: 34 * unit, height: 34 * unit, borderRadius: 9 * unit, background: P.accent, color: P.onAccent, fontWeight: 800, fontSize: 18 * unit, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>D</div>
				<span style={{fontSize: 21 * unit, fontWeight: t.weights.strong, color: P.text}}>Driftnote</span>
			</div>
			{items.map(([icon, label]) => {
				const active = label === 'Launch plan';
				return (
					<div key={label} style={{display: 'flex', alignItems: 'center', gap: 14 * unit, height: 46 * unit, padding: `0 ${12 * unit}px`, borderRadius: 10 * unit, background: active ? `${P.accent}1C` : 'transparent', color: active ? P.accent : P.muted, fontSize: 19 * unit, fontWeight: active ? t.weights.strong : t.weights.body}}>
						<UiIcon name={icon} size={20} />
						{label}
					</div>
				);
			})}
		</div>
	);
};

const WorkspacePage: React.FC<{contentAt: number; tl: ReturnType<typeof cursorTimeline>}> = ({contentAt, tl}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t);
	const u = (v: number) => v * unit;
	const sharePress = tl.pressOf(1) ?? 0;
	const dialogAt = sharePress + at30(8, fps);
	const dialog = springAt(frame, fps, {delay: dialogAt, config: 'settle'});
	const scrim = ramp(frame, dialogAt, at30(8, fps), curves.out);
	const copyAt = tl.pressOf(3) ?? 0;
	const skel = 1 - ramp(frame, contentAt, at30(10, fps), curves.out);
	const shimmer = ((frame * 18) % 1400) - 400;
	const bar = (x: number, y: number, w: number, h: number, i: number) => (
		<div key={i} style={{position: 'absolute', left: u(x), top: u(y), width: u(w), height: u(h), borderRadius: u(Math.min(10, h / 2)), background: `linear-gradient(90deg, ${P.panel} 0%, ${P.line} 50%, ${P.panel} 100%)`, backgroundSize: `${u(1400)}px 100%`, backgroundPosition: `${u(shimmer - x)}px 0px`}} />
	);
	const rows = [
		['Oct 6', 'Beta invites go out', 'Lena'],
		['Oct 13', 'Pricing page goes live', 'Arif'],
		['Oct 20', 'Public launch', 'Maya'],
	];
	return (
		<AbsoluteFill style={{fontFamily: t.type.body, background: P.page}}>
			<Sidebar />
			<div style={{position: 'absolute', left: 0, top: 0, width: PAGE.w * unit, height: PAGE.h * unit}}>
				{skel > 0.001 ? (
					<div style={{position: 'absolute', inset: 0, opacity: skel}}>
						{[
							[316, 40, 180, 16],
							[316, 70, 330, 40],
							[316, 172, 110, 22],
							[316, 214, 520, 18],
							[316, 252, 460, 18],
							[316, 290, 560, 18],
							[316, 382, 130, 22],
							[316, 424, 820, 40],
							[316, 480, 820, 40],
							[316, 536, 820, 40],
							[1180, 170, 204, 130],
							[1234, 52, 150, 56],
						].map(([x, y, w, h], i) => bar(x, y, w, h, i))}
					</div>
				) : null}
				<Stagger in="rise" delay={contentAt} each={3} distance={16}>
					<div style={{position: 'absolute', left: u(316), top: u(38), fontSize: u(18), color: P.muted}}>Projects / Q4 launch</div>
					<div style={{position: 'absolute', left: u(316), top: u(66), fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(46), letterSpacing: `${t.tracking.display}em`, color: P.text}}>Launch plan</div>
					<div style={{position: 'absolute', left: u(316), top: u(170), width: u(820)}}>
						<div style={{fontSize: u(24), fontWeight: t.weights.strong, color: P.text, marginBottom: u(12)}}>Goals</div>
						{['Ship offline mode to every workspace', 'Cut first load under one second', 'Invite 40 beta teams before launch day'].map((g) => (
							<div key={g} style={{display: 'flex', alignItems: 'center', gap: u(12), fontSize: u(21), color: P.text, height: u(40)}}>
								<span style={{width: u(8), height: u(8), borderRadius: '50%', background: P.accent}} />
								{g}
							</div>
						))}
					</div>
					<div style={{position: 'absolute', left: u(316), top: u(380), width: u(820)}}>
						<div style={{fontSize: u(24), fontWeight: t.weights.strong, color: P.text, marginBottom: u(14)}}>Timeline</div>
						{rows.map((r, i) => (
							<div key={r[1]} style={{display: 'flex', alignItems: 'center', height: u(56), borderTop: `${unit}px solid ${P.line}`, borderBottom: i === rows.length - 1 ? `${unit}px solid ${P.line}` : undefined, fontSize: u(20), color: P.text}}>
								<span style={{width: u(130), color: P.muted, fontVariantNumeric: 'tabular-nums'}}>{r[0]}</span>
								<span style={{flex: 1}}>{r[1]}</span>
								<span style={{color: P.muted}}>{r[2]}</span>
							</div>
						))}
					</div>
					<div style={{position: 'absolute', left: u(1180), top: u(170), width: u(204), padding: u(22), borderRadius: u(18), background: P.panel, boxShadow: `inset 0 0 0 ${unit}px ${P.line}`}}>
						<div style={{fontSize: u(17), color: P.muted}}>Readiness</div>
						<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(44), color: P.text, fontVariantNumeric: 'tabular-nums'}}>72%</div>
						<div style={{height: u(8), borderRadius: u(4), background: P.line, marginTop: u(8)}}>
							<div style={{width: '72%', height: '100%', borderRadius: u(4), background: P.positive}} />
						</div>
					</div>
				</Stagger>
				<Animate in="fade" delay={contentAt + 6} style={{position: 'absolute', left: u(SHARE.x - 128), top: u(SHARE.y + 10)}}>
				<div style={{display: 'flex'}}>
					{['MC', 'AR', 'LO'].map((n, i) => (
						<div key={n} style={{width: u(38), height: u(38), marginLeft: i ? u(-10) : 0, borderRadius: '50%', background: ['#2563EB', '#D97706', '#7C3AED'][i], color: '#FFFFFF', fontSize: u(14), fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 0 0 ${u(3)}px ${P.page}`}}>
							{n}
						</div>
					))}
				</div>
				</Animate>
				<Animate in="fade" delay={contentAt + 6} style={{position: 'absolute', left: u(SHARE.x), top: u(SHARE.y)}}>
					<UiButton label="Share" variant="secondary" icon="link" width={SHARE.w} pressAt={sharePress} hoverAt={tl.arriveOf(1)} />
				</Animate>
			</div>
			{frame >= dialogAt ? (
				<>
					<AbsoluteFill style={{background: `rgba(10, 14, 22, ${0.28 * scrim})`}} />
					<div style={{position: 'absolute', left: u(DIALOG.x), top: u(DIALOG.y), width: u(DIALOG.w), height: u(DIALOG.h), borderRadius: u(22), background: P.raised, boxShadow: `0 ${u(30)}px ${u(70)}px rgba(10,14,22,0.28)`, opacity: Math.min(1, dialog * 2), scale: `${0.94 + 0.06 * dialog}`}}>
						<div style={{position: 'absolute', left: u(32), top: u(28), fontSize: u(26), fontWeight: t.weights.strong, color: P.text}}>Share &ldquo;Launch plan&rdquo;</div>
						<div style={{position: 'absolute', left: u(32), top: u(84)}}>
							<FormField label="Invite by email" value="lena@studio.example" typeAt={dialogAt + at30(14, fps)} cps={16} blurAt={(tl.pressOf(2) ?? 0) - 2} width={536} height={60} />
						</div>
						<div style={{position: 'absolute', left: u(32), top: u(218), display: 'flex', alignItems: 'center', gap: u(16)}}>
							<Toggle on at={tl.pressOf(2)} />
							<span style={{fontSize: u(20), color: P.text}}>Anyone with the link can view</span>
						</div>
						<div style={{position: 'absolute', left: u(DIALOG.w - 32 - 180 - 12 - 120), top: u(306)}}>
							<UiButton label="Cancel" variant="ghost" width={120} />
						</div>
						<div style={{position: 'absolute', left: u(DIALOG.w - 32 - 180), top: u(306)}}>
							<UiButton label="Copy link" width={180} pressAt={copyAt} doneLabel="Copied" doneIcon="check" />
						</div>
					</div>
				</>
			) : null}
			<Notification variant="pill" title="Link copied" delay={copyAt + at30(6, fps)} area="parent" place="bottom" inset={36} />
			<Cursor keys={BROWSER_KEYS} />
		</AbsoluteFill>
	);
};

const BrowserDemo: React.FC = () => {
	const {fps} = useStage();
	const tl = React.useMemo(() => cursorTimeline(BROWSER_KEYS, fps), [fps]);
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<Camera
				keys={[
					{at: 0, x: 960, y: 540, zoom: 1},
					{at: 66, zoom: 1},
					{at: 94, x: 1330, y: 390, zoom: 1.3},
					{at: 124, x: 1330, y: 390, zoom: 1.3},
					{at: 152, x: 960, y: 540, zoom: 1},
				]}
			>
				<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
					<BrowserWindow width={1440} height={860} url="driftnote.example/launch-plan" typeUrlAt={6} loadAt={44} tabs={['Launch plan: Driftnote', 'Weekly sync notes', 'Inbox (3)']}>
						<WorkspacePage contentAt={48} tl={tl} />
					</BrowserWindow>
				</AbsoluteFill>
			</Camera>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiLaptop: laptop, app window, guided tour

const WIDGETS = [
	{x: 252, y: 150, w: 256, h: 230},
	{x: 532, y: 150, w: 256, h: 230},
	{x: 812, y: 150, w: 256, h: 230},
];
const TIPS = ['Points finished each sprint', 'Tasks nobody has picked up', 'Due before Friday'];

const SprintApp: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t);
	const u = (v: number) => v * unit;
	const card = (i: number, title: string, body: React.ReactNode) => (
		<div key={title} style={{position: 'absolute', left: u(WIDGETS[i].x - 220), top: u(WIDGETS[i].y - 52), width: u(WIDGETS[i].w), height: u(WIDGETS[i].h), boxSizing: 'border-box', padding: u(20), borderRadius: u(16), background: P.panel, boxShadow: `inset 0 0 0 ${unit}px ${P.line}`}}>
			<div style={{fontSize: u(17), color: P.muted, marginBottom: u(12)}}>{title}</div>
			{body}
		</div>
	);
	return (
		<MacWindow width={1100} height={687.5} title="Taskwell: Sprint 14" radius={0} shadow={false} sidebarWidth={220} sidebar={
			<div style={{padding: u(20), fontFamily: t.type.body, fontSize: u(17), color: P.muted, display: 'flex', flexDirection: 'column', gap: u(14)}}>
				{['Overview', 'Board', 'Backlog', 'Reports'].map((s, i) => (
					<div key={s} style={{color: i === 0 ? P.text : P.muted, fontWeight: i === 0 ? t.weights.strong : t.weights.body}}>{s}</div>
				))}
			</div>
		}>
			<div style={{position: 'absolute', left: u(32), top: u(28), fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(34), color: P.text}}>Sprint 14</div>
			<div style={{position: 'absolute', left: u(32), top: u(72), fontSize: u(16), color: P.muted}}>Oct 6 to Oct 17 &middot; 9 people</div>
			{card(0, 'Velocity', (
				<div style={{display: 'flex', alignItems: 'flex-end', gap: u(10), height: u(130)}}>
					{[42, 55, 48, 66, 72].map((h, i) => (
						<div key={i} style={{flex: 1, height: `${h * 1.6}%`, maxHeight: '100%', borderRadius: u(5), background: i === 4 ? P.accent : `${P.accent}55`}} />
					))}
				</div>
			))}
			{card(1, 'Open tasks', <div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(84), color: P.text, lineHeight: 1}}>18</div>)}
			<div style={{position: 'absolute', left: u(32), right: u(32), top: u(356), fontFamily: t.type.body}}>
				<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: u(10)}}>
					<span style={{fontSize: u(19), fontWeight: t.weights.strong, color: P.text}}>Up next</span>
					<span style={{fontSize: u(15), color: P.accent}}>View board</span>
				</div>
				{[
					['Checkout copy review', 'Lena', 'In review', P.accent2],
					['Offline sync for images', 'Arif', 'In progress', P.accent],
					['Invite flow on mobile', 'Maya', 'Blocked', P.negative],
					['Weekly usage email', 'Tanvir', 'In progress', P.accent],
				].map(([task, who, status, c]) => (
					<div key={task} style={{display: 'flex', alignItems: 'center', height: u(52), borderTop: `${unit}px solid ${P.line}`, fontSize: u(16), color: P.text}}>
						<span style={{flex: 1}}>{task}</span>
						<span style={{width: u(110), color: P.muted}}>{who}</span>
						<span style={{fontSize: u(13), fontWeight: t.weights.strong, color: c, background: `${c}22`, padding: `${u(4)}px ${u(10)}px`, borderRadius: u(10)}}>{status}</span>
					</div>
				))}
			</div>
			{card(2, 'Due this week', (
				<div style={{display: 'flex', flexDirection: 'column', gap: u(12), fontSize: u(16), color: P.text}}>
					{['Onboarding emails', 'Billing page QA', 'Release notes'].map((s) => (
						<div key={s} style={{display: 'flex', alignItems: 'center', gap: u(8)}}>
							<UiIcon name="clock" size={16} color={P.muted} />
							{s}
						</div>
					))}
				</div>
			))}
		</MacWindow>
	);
};

const LaptopDemo: React.FC = () => {
	const {fps} = useStage();
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingTop: 40}}>
				<DeviceRise tilt={22} distance={180} delay={-8}>
					<Float amp={4} rotate={0.2} delay={at30(26, fps)}>
						<LaptopFrame width={1100}>
							<SprintApp />
							<FocusRing keys={WIDGETS.map((w, i) => ({...w, at: 64 + i * 44}))} exitAt={186} />
							{TIPS.map((tip, i) => (
								<Sequence key={tip} from={70 + i * 44} durationInFrames={i < TIPS.length - 1 ? 22 : 40} layout="none">
									<UiTooltip x={WIDGETS[i].x + WIDGETS[i].w / 2} y={WIDGETS[i].y + WIDGETS[i].h + 12} side="bottom" text={tip} />
								</Sequence>
							))}
							<Notification variant="desktop" title="Sprint review at 3 pm" body="Room 2 or the team call link" icon="calendar" delay={206} area="parent" inset={18} width={380} actions={['Join', 'Later']} />
						</LaptopFrame>
					</Float>
				</DeviceRise>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiPhone: two phones, a notes app, a banner

const NOTES = {rows: 184, rowH: 78, scroll: 120};

const NotesScreen: React.FC<{tapAt: number}> = ({tapAt}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t, 'light');
	const u = (v: number) => v * unit;
	const notes = [
		['Launch checklist', 'Three items left before Friday', 'Today'],
		['Interview notes: Lena', 'Loves the offline mode and wants', 'Yesterday'],
		['Pricing ideas', 'Keep the free plan to three', 'Mon'],
		['Reading list', 'Two books on product writing', 'Sep 28'],
		['Offsite agenda', 'Day one is all customer calls', 'Sep 26'],
		['Hiring plan', 'One designer, one support lead', 'Sep 24'],
		['Q4 goals', 'Faster sync, calmer onboarding', 'Sep 20'],
		['Gift ideas', 'Something for the new studio', 'Sep 18'],
	];
	return (
		<ScrollView keys={[{at: 30, y: 0}, {at: 48, y: NOTES.scroll}]} mode="light">
		<AbsoluteFill style={{background: '#FFFFFF', fontFamily: t.type.body, height: u(NOTES.rows + 8 * NOTES.rowH + 40)}}>
			<div style={{position: 'absolute', left: u(24), top: u(66), fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(40), color: P.text, letterSpacing: `${t.tracking.display}em`}}>Notes</div>
			<div style={{position: 'absolute', left: u(24), right: u(24), top: u(126), height: u(44), borderRadius: u(12), background: P.field, display: 'flex', alignItems: 'center', gap: u(8), padding: `0 ${u(14)}px`, color: P.muted, fontSize: u(17)}}>
				<UiIcon name="search" size={17} />
				Search
			</div>
			{notes.map(([title, body, when], i) => (
				<div key={title} style={{position: 'absolute', left: u(20), right: u(20), top: u(NOTES.rows + i * NOTES.rowH), height: u(NOTES.rowH)}}>
					<Pressable at={i === 2 ? tapAt : undefined} style={{height: '100%'}}>
						<div style={{height: '100%', boxSizing: 'border-box', padding: `${u(13)}px ${u(8)}px`, borderBottom: `${unit}px solid ${P.line}`, borderRadius: u(10)}}>
							<div style={{fontSize: u(19), fontWeight: t.weights.strong, color: P.text}}>{title}</div>
							<div style={{fontSize: u(16), color: P.muted, marginTop: u(4), whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
								<span style={{color: P.text, opacity: 0.8}}>{when}</span>&nbsp; {body}
							</div>
						</div>
					</Pressable>
				</div>
			))}
		</AbsoluteFill>
		</ScrollView>
	);
};

const EditorScreen: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const u = (v: number) => v * unit;
	return (
		<AbsoluteFill style={{background: '#101216', fontFamily: t.type.body, padding: `${u(70)}px ${u(26)}px`, boxSizing: 'border-box', color: '#EEF0F4'}}>
			<div style={{fontSize: u(15), color: '#8B93A1'}}>Launch checklist</div>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(30), margin: `${u(8)}px 0 ${u(18)}px`}}>Before Friday</div>
			{['Record the demo', 'Send beta invites', 'Update pricing page', 'Write release notes'].map((s, i) => (
				<div key={s} style={{display: 'flex', alignItems: 'center', gap: u(12), height: u(46), fontSize: u(18)}}>
					<div style={{width: u(24), height: u(24), borderRadius: u(7), border: `${u(2)}px solid ${i < 1 ? t.colors.accent : '#4A505C'}`, background: i < 1 ? t.colors.accent : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i < 1 ? <UiIcon name="check" size={16} color="#FFFFFF" stroke={3} /> : null}</div>
					<span style={{opacity: i < 1 ? 0.5 : 1, textDecoration: i < 1 ? 'line-through' : undefined}}>{s}</span>
				</div>
			))}
		</AbsoluteFill>
	);
};

const PhoneDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe, height} = useStage();
	const W = 400;
	const S = phoneScreen(W);
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: safe.x + 30 * unit, top: safe.y, height: safe.h, width: safe.w * 0.46, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 26 * unit}}>
				<Animate in="rise" delay={-4}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 24 * unit, color: t.colors.accent, letterSpacing: `${t.tracking.caps}em`, textTransform: 'uppercase'}}>Driftnote for phone</div>
				</Animate>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 92 * unit, lineHeight: 1.02, letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>
					<Stagger in="mask" each={4} delay={0}>
						<div>Your notes,</div>
						<div>in your pocket</div>
					</Stagger>
				</div>
				<Animate in="rise" delay={20}>
					<div style={{fontFamily: t.type.body, fontSize: 34 * unit, color: t.colors.muted, lineHeight: 1.35}}>Offline, synced and searchable. Pick up where you left off.</div>
				</Animate>
			</div>
			<div style={{position: 'absolute', right: safe.x + 300 * unit, top: (height - 360 * 2.06 * unit) / 2 + 30 * unit, rotate: '-7deg'}}>
				<DeviceRise delay={-6} tilt={20}>
					<PhoneFrame width={360} finish="silver" camera="dot" screen="#101216">
						<EditorScreen />
					</PhoneFrame>
				</DeviceRise>
			</div>
			<div style={{position: 'absolute', right: safe.x + 40 * unit, top: (height - W * 2.06 * unit) / 2}}>
				<DeviceRise delay={-12} tilt={24}>
					<PhoneFrame width={W} finish="graphite" camera="pill" screen="#FFFFFF" barFill>
						<NotesScreen tapAt={132} />
						<Notification variant="phone" app="Driftnote" title="Maya shared a note" body="Launch checklist: three items left before Friday" time="now" icon="file" delay={86} exitAt={150} inset={12} />
						<TapIndicator
							swipes={[{from: [S.w * 0.55, 640], to: [S.w * 0.55, 640 - NOTES.scroll], at: 30, frames: 18}]}
							taps={[{x: S.w / 2, y: NOTES.rows + NOTES.rowH * 2.5 - NOTES.scroll, at: 132}]}
						/>
					</PhoneFrame>
				</DeviceRise>
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiApp: a 9:16 phone app with touches only

const APP_W = 700;
const APP = phoneScreen(APP_W);
const PAD = 44;
const BTN = {x: PAD, y: 1000, w: APP.w - 2 * PAD, h: 92};
const CHIPS = [
	{label: 'Food', icon: 'coffee' as UiIconName, w: 132},
	{label: 'Transport', icon: 'train' as UiIconName, w: 186},
	{label: 'Home', icon: 'home' as UiIconName, w: 132},
	{label: 'Fun', icon: 'sparkle' as UiIconName, w: 108},
];
const TOG = {x: APP.w - PAD - 64, y: 712};
const TAPS = {add: 60, food: 132, toggle: 190, save: 218};

const money = (v: number) => `$${v.toFixed(2)}`;

const HomeScreen: React.FC<{addedAt: number}> = ({addedAt}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, 'light');
	const u = (v: number) => v * unit;
	const bars = [34, 52, 28, 61, 45, 20, 12];
	const grow = ramp(frame, 4, at30(26, fps), curves.out);
	const newRow = ramp(frame, addedAt, at30(10, fps), curves.out);
	const bal = 642.18 - 12.4 * ramp(frame, addedAt + 2, at30(20, fps), curves.inOut);
	const row = (icon: UiIconName, title: string, sub: string, amount: string, tint: string) => (
		<div style={{display: 'flex', alignItems: 'center', gap: u(18), height: u(104), borderBottom: `${unit}px solid ${P.line}`}}>
			<div style={{width: u(60), height: u(60), borderRadius: u(18), background: `${tint}1F`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
				<UiIcon name={icon} size={30} color={tint} />
			</div>
			<div style={{flex: 1}}>
				<div style={{fontSize: u(28), fontWeight: t.weights.strong, color: P.text}}>{title}</div>
				<div style={{fontSize: u(22), color: P.muted, marginTop: u(2)}}>{sub}</div>
			</div>
			<div style={{fontSize: u(28), fontWeight: t.weights.strong, color: P.text, fontVariantNumeric: 'tabular-nums'}}>{amount}</div>
		</div>
	);
	return (
		<AbsoluteFill style={{background: '#FFFFFF', fontFamily: t.type.body, padding: `${u(118)}px ${u(PAD)}px 0`, boxSizing: 'border-box'}}>
			<div style={{fontSize: u(26), color: P.muted}}>Good morning, Maya</div>
			<div style={{fontSize: u(24), color: P.muted, marginTop: u(22)}}>Left to spend this week</div>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(88), color: P.text, letterSpacing: `${t.tracking.display}em`, fontVariantNumeric: 'tabular-nums', lineHeight: 1.1}}>{money(bal)}</div>
			<div style={{marginTop: u(26), height: u(210), borderRadius: u(28), background: P.panel, padding: `${u(26)}px ${u(30)}px ${u(18)}px`, boxSizing: 'border-box', display: 'flex', alignItems: 'flex-end', gap: u(20)}}>
				{bars.map((h, i) => (
					<div key={i} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: u(8), height: '100%', justifyContent: 'flex-end'}}>
						<div style={{width: '100%', height: `${h * 2 * grow}%`, borderRadius: u(10), background: i === 3 ? P.accent : `${P.accent}40`}} />
						<div style={{fontSize: u(18), color: P.muted}}>{'MTWTFSS'[i]}</div>
					</div>
				))}
			</div>
			<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: u(34), marginBottom: u(4)}}>
				<span style={{fontSize: u(30), fontWeight: t.weights.strong, color: P.text}}>Recent</span>
				<span style={{fontSize: u(24), fontWeight: t.weights.strong, color: P.accent}}>See all</span>
			</div>
			<div style={{display: 'grid', gridTemplateRows: `minmax(0, ${newRow}fr)`}}>
				<div style={{minHeight: 0, overflow: 'hidden', opacity: newRow}}>{row('coffee', 'Lunch with Arif', 'Today, split in two', '-$12.40', '#E76F51')}</div>
			</div>
			{row('coffee', 'Brew Lab coffee', 'Today, 8:40', '-$4.60', '#E76F51')}
			{row('bag', 'Groceries', 'Yesterday', '-$38.20', '#2A9D8F')}
			<div style={{display: 'grid', gridTemplateRows: `minmax(0, ${1 - newRow}fr)`}}>
				<div style={{minHeight: 0, overflow: 'hidden', opacity: 1 - newRow}}>{row('train', 'Train pass', 'Monday', '-$25.00', '#3D5A80')}</div>
			</div>
			<div style={{position: 'absolute', left: u(BTN.x), top: u(BTN.y)}}>
				<UiButton label="Add expense" icon="plus" size="lg" width={BTN.w} pressAt={TAPS.add} style={{height: u(BTN.h), fontSize: u(30), borderRadius: u(BTN.h / 2)}} />
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: u(150), borderTop: `${unit}px solid ${P.line}`, background: '#FFFFFF', display: 'flex', justifyContent: 'space-around', paddingTop: u(26)}}>
				{(['home', 'chart', 'wallet', 'user'] as UiIconName[]).map((n, i) => (
					<UiIcon key={n} name={n} size={34} color={i === 0 ? P.accent : P.muted} />
				))}
			</div>
		</AbsoluteFill>
	);
};

const ADD = {amountLabel: 200, amount: 232, categoryLabel: 404, chips: 446, chipH: 66, note: 560};

const AddScreen: React.FC = () => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t, 'light');
	const u = (v: number) => v * unit;
	const amount = useUiTyping('12.40', 96, {cps: 9, seed: 'amount'});
	const food = ramp(frame, TAPS.food, 5, curves.out);
	const at = (y: number): React.CSSProperties => ({position: 'absolute', left: u(PAD), top: u(y)});
	let cx = PAD;
	return (
		<AbsoluteFill style={{background: '#FFFFFF', fontFamily: t.type.body}}>
			<div style={{...at(112), display: 'flex', alignItems: 'center', gap: u(14), marginLeft: u(-8)}}>
				<UiIcon name="chevronLeft" size={40} color={P.accent} stroke={2.4} />
				<span style={{fontSize: u(34), fontWeight: t.weights.strong, color: P.text}}>New expense</span>
			</div>
			<div style={{...at(ADD.amountLabel), fontSize: u(24), color: P.muted}}>Amount</div>
			<div style={{...at(ADD.amount), display: 'flex', alignItems: 'center', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(112), color: P.text, letterSpacing: `${t.tracking.display}em`, fontVariantNumeric: 'tabular-nums', height: u(140)}}>
				<span style={{color: amount.count ? P.text : P.faint}}>$</span>
				<span style={{color: amount.count ? P.text : P.faint}}>{amount.count ? amount.shown : '0.00'}</span>
				{frame >= 88 && frame < 128 ? <span style={{width: u(5), height: u(96), background: P.accent, marginLeft: u(6), opacity: amount.caret}} /> : null}
			</div>
			<div style={{...at(ADD.categoryLabel), fontSize: u(24), color: P.muted}}>Category</div>
			{CHIPS.map((c, i) => {
				const left = cx;
				cx += c.w + 12;
				const on = i === 0 ? food : 0;
				return (
					<div key={c.label} style={{position: 'absolute', left: u(left), top: u(ADD.chips)}}>
						<Pressable at={i === 0 ? TAPS.food : undefined}>
							<div style={{height: u(ADD.chipH), width: u(c.w), boxSizing: 'border-box', borderRadius: u(ADD.chipH / 2), display: 'flex', alignItems: 'center', justifyContent: 'center', gap: u(8), fontSize: u(24), fontWeight: t.weights.strong, background: on > 0.5 ? P.accent : P.panel, color: on > 0.5 ? P.onAccent : P.text, boxShadow: `inset 0 0 0 ${unit}px ${on > 0.5 ? P.accent : P.line}`}}>
								<UiIcon name={c.icon} size={24} />
								{c.label}
							</div>
						</Pressable>
					</div>
				);
			})}
			<div style={at(ADD.note)}>
				<FormField label="Note" value="Lunch with Arif" typeAt={146} cps={13} blurAt={184} width={APP.w - 2 * PAD} height={76} mode="light" />
			</div>
			<div style={{position: 'absolute', left: u(PAD), right: u(PAD), top: u(TOG.y), height: u(38), display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
				<span style={{fontSize: u(28), color: P.text}}>Split with Arif</span>
				<Toggle on at={TAPS.toggle} mode="light" />
			</div>
			<div style={{position: 'absolute', left: u(BTN.x), top: u(BTN.y)}}>
				<UiButton label="Save" size="lg" width={BTN.w} pressAt={TAPS.save} doneLabel="Saved" doneIcon="check" style={{height: u(BTN.h), fontSize: u(30), borderRadius: u(BTN.h / 2)}} mode="light" />
			</div>
		</AbsoluteFill>
	);
};

const AppDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const {unit, width, safe, fps} = useStage();
	const H = APP_W * 2.06;
	const push = ramp(frame, 66, at30(20, fps), curves.inOut) * (1 - ramp(frame, 228, at30(20, fps), curves.inOut));
	const back = frame >= 228;
	const top = safe.y + safe.h / 2 - (H * unit) / 2;
	let cx = PAD;
	const chipX = CHIPS.map((c) => {
		const x = cx + c.w / 2;
		cx += c.w + 12;
		return x;
	});
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: (width - APP_W * unit) / 2, top}}>
				<PhoneFrame width={APP_W} finish="graphite" camera="pill" screen="#FFFFFF">
					<AbsoluteFill style={{translate: `${-28 * push}% 0px`}}>
						<HomeScreen addedAt={250} />
						<AbsoluteFill style={{background: `rgba(10, 12, 20, ${0.25 * push})`}} />
					</AbsoluteFill>
					{frame >= 60 && frame < 252 ? (
						<AbsoluteFill style={{translate: `${(1 - push) * 100}%`, boxShadow: `${-20 * unit}px 0 ${40 * unit}px rgba(10,12,20,${0.15 * push})`}}>
							<AddScreen />
						</AbsoluteFill>
					) : null}
					<TapIndicator
						size={78}
						taps={[
							{x: BTN.x + BTN.w / 2, y: BTN.y + BTN.h / 2, at: TAPS.add},
							{x: chipX[0], y: ADD.chips + ADD.chipH / 2, at: TAPS.food},
							{x: TOG.x + 32, y: TOG.y + 19, at: TAPS.toggle},
							{x: BTN.x + BTN.w / 2, y: BTN.y + BTN.h / 2, at: TAPS.save},
						]}
					/>
					{back ? <Notification variant="pill" title="Expense saved" delay={256} area="parent" place="bottom" inset={176} /> : null}
				</PhoneFrame>
			</div>
			<ClickSounds frames={Object.values(TAPS)} src={staticFile('ui/tap.wav')} volume={0.6} />
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiCode and DemoUiCodeLight

const TS_CODE = `import {publish} from './api';

// খসড়া সেভ করে তারপর প্রকাশ করো
export async function ship(doc: Draft) {
  const saved = await doc.save({version: 3});
  if (!saved.ok) throw new Error('Save failed');
  return publish(saved.id, {public: true});
}`;

const JSON_CODE = `{
  "name": "driftnote-web",
  "version": "2.4.0",
  "offline": true,
  "regions": ["eu-west", "ap-south"],
  "maxUploadMb": 25
}`;

const PY_CODE = `from driftnote import Client

client = Client(token=TOKEN)

@client.on("note.shared")
def notify(event):
    """Tell the owner who opened their note."""
    who = event.user.name
    client.send(event.owner, f"{who} opened your note")
    return True`;

const CodeDemo: React.FC = () => {
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: safe.x + 10 * unit, top: safe.y + 250 * unit}}>
				<CodeBlock code={TS_CODE} lang="ts" title="ship.ts" typing="char" startAt={6} cps={50} width={1060} fontSize={28} focus={[{lines: '5-6', at: 150}, {lines: [7], at: 192}]} />
			</div>
			<div style={{position: 'absolute', right: safe.x + 10 * unit, top: safe.y + 430 * unit}}>
				<CodeBlock code={JSON_CODE} lang="json" title="driftnote.json" typing="line" startAt={40} lineEvery={6} width={600} fontSize={24} />
			</div>
		</AbsoluteFill>
	);
};

const CodeLightDemo: React.FC = () => {
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill>
			<UiBackdrop variant="dots" />
			<div style={{position: 'absolute', left: safe.x + 120 * unit, top: safe.y + 60 * unit}}>
				<CodeBlock code={PY_CODE} lang="py" title="hooks.py" typing="char" startAt={4} cps={62} width={1100} height={560} fontSize={26} focus={[{lines: [5, 6], at: 150}, {lines: [8, 9], at: 190}]} />
			</div>
			<div style={{position: 'absolute', right: safe.x + 60 * unit, top: safe.y + 610 * unit}}>
				<CodeBlock code={`# deploy the hooks\ndriftnote deploy --env prod --region eu-west\necho "done: $RELEASE"`} lang="bash" title="deploy.sh" typing="none" startAt={40} width={760} fontSize={22} />
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiTerminal

const TERM: TermLine[] = [
	{cmd: 'npm create driftnote@latest team-notes'},
	{out: 'Scaffolding a new workspace in ~/team-notes', tone: 'muted'},
	{out: 'Templates copied', tone: 'ok', icon: 'check'},
	{cmd: 'cd team-notes && npm install'},
	{progress: 'Installing', frames: 46},
	{out: 'added 214 packages in 6s', tone: 'muted'},
	{cmd: 'npm run deploy'},
	{spinner: 'Deploying to the edge', frames: 40, done: 'Live at team-notes.driftnote.example'},
	{out: 'খসড়া প্রকাশিত হয়েছে, সবাই দেখতে পাবে', tone: 'info'},
];

const TerminalDemo: React.FC = () => (
	<AbsoluteFill>
		<UiBackdrop variant="glow" />
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
			<Terminal lines={TERM} startAt={8} width={1320} height={640} fontSize={26} path="~/team-notes" />
		</AbsoluteFill>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiChat (16:9 in a phone) and DemoUiChatVertical

const ChatDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe, height} = useStage();
	const W = 440;
	const S = phoneScreen(W);
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: safe.x + 30 * unit, top: safe.y, height: safe.h, width: safe.w * 0.48, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 28 * unit}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 88 * unit, lineHeight: 1.04, letterSpacing: `${t.tracking.display}em`, color: t.colors.text}}>
					<Stagger in="mask" each={4} delay={4}>
						<div>Reply without</div>
						<div>leaving the doc</div>
					</Stagger>
				</div>
				<Animate in="rise" delay={24}>
					<div style={{fontFamily: t.type.body, fontSize: 34 * unit, lineHeight: 1.35, color: t.colors.muted}}>Every note has its own thread, so decisions stay next to the work.</div>
				</Animate>
			</div>
			<div style={{position: 'absolute', right: safe.x + 120 * unit, top: (height - W * 2.06 * unit) / 2}}>
				<DeviceRise tilt={18} delay={-10}>
					<PhoneFrame width={W} finish="graphite">
						<div style={{position: 'absolute', left: 0, top: S.top * unit}}>
							<ChatThread
								panel={false}
								width={S.w}
								height={S.h - S.top - S.bottom * 0.4}
								fontSize={24}
								composer
								receipt="Read 10:24"
								header={{name: 'Arif Rahman', status: 'online'}}
								messages={[
									{from: 'them', text: 'Morning! Is the release still on for today?', at: -90},
									{from: 'me', text: 'Yes, final checks now', at: -60},
									{from: 'them', text: 'Did the new build go out?', at: 40},
									{from: 'me', text: 'Yes, ten minutes ago', at: 104},
									{from: 'them', text: 'অসাধারণ! ক্লায়েন্ট কি দেখেছে?', at: 164},
									{from: 'me', text: 'Sending them the link now', at: 226, react: {at: 252}},
								]}
							/>
						</div>
					</PhoneFrame>
				</DeviceRise>
			</div>
		</AbsoluteFill>
	);
};

const ChatVerticalDemo: React.FC = () => {
	const {unit, safe} = useStage();
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', left: safe.x, top: safe.y}}>
				<ChatThread
					width={safe.w / unit}
					height={safe.h / unit}
					fontSize={36}
					header={{name: 'Launch team', status: '4 members'}}
					startAt={10}
					receipt="Seen by 3"
					messages={[
						{from: 'them', name: 'Lena Ortiz', text: 'Morning all', at: -120},
						{from: 'me', text: 'Morning! Big day', at: -90},
						{from: 'them', name: 'Maya Chen', text: 'Pricing page is live on staging'},
						{from: 'them', name: 'Maya Chen', text: 'Can someone check the mobile layout?', typing: false},
						{from: 'me', text: 'On it, give me five minutes'},
						{from: 'them', name: 'আরিফ রহমান', text: 'বাংলা অনুবাদটাও দেখে নিও', react: {at: 200}},
						{from: 'me', text: 'Both look good. Shipping it.'},
					]}
				/>
			</div>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiToast

const ToastDemo: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const P = uiPalette(t);
	const W = 380;
	const S = phoneScreen(W);
	const u = (v: number) => v * unit;
	return (
		<AbsoluteFill>
			<UiBackdrop variant="glow" />
			<div style={{position: 'absolute', right: safe.x - 20 * unit, top: safe.y + 30 * unit}}>
				<MacWindow width={1260} height={800} title="Driftnote" sidebarWidth={250} sidebar={<div style={{padding: u(22), display: 'flex', flexDirection: 'column', gap: u(16), fontFamily: t.type.body, fontSize: u(18), color: P.muted}}>{['Inbox', 'Launch plan', 'Weekly sync', 'Archive'].map((x, i) => <div key={x} style={{color: i === 1 ? P.text : P.muted, fontWeight: i === 1 ? t.weights.strong : t.weights.body}}>{x}</div>)}</div>}>
					<div style={{padding: `${u(40)}px ${u(48)}px`, fontFamily: t.type.body, color: P.text}}>
						<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(40), letterSpacing: `${t.tracking.display}em`}}>Launch plan</div>
						<div style={{fontSize: u(19), color: P.muted, marginTop: u(8)}}>Edited by Maya 2 minutes ago</div>
						{[520, 610, 480, 560, 300].map((w, i) => (
							<div key={i} style={{height: u(14), width: u(w), borderRadius: u(7), background: P.line, marginTop: u(i === 0 ? 40 : 18)}} />
						))}
					</div>
				</MacWindow>
			</div>
			<div style={{position: 'absolute', left: safe.x + 20 * unit, top: safe.y + 70 * unit}}>
				<PhoneFrame width={W} screen="#1B2230" statusBar="light">
					<AbsoluteFill style={{background: 'linear-gradient(160deg, #3B4A6B 0%, #1B2230 60%)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 140 * unit, color: '#FFFFFF', fontFamily: t.type.body}}>
						<div style={{fontSize: 24 * unit, opacity: 0.85}}>Friday 10 October</div>
						<div style={{fontFamily: t.type.display, fontWeight: 300, fontSize: 98 * unit, lineHeight: 1, letterSpacing: '-0.02em'}}>10:24</div>
					</AbsoluteFill>
					<NotificationStack
						variant="phone"
						inset={14}
						style={{top: (S.top + 240) * unit}}
						items={[
							{at: 20, app: 'Coinlet', title: 'নতুন খরচ যোগ হয়েছে', body: 'দুপুরের খাবার, ১২.৪০ ডলার', icon: 'wallet', width: S.w - 28},
							{at: 64, app: 'Driftnote', title: 'Maya shared a note', body: 'Launch checklist: three items left', icon: 'file', width: S.w - 28},
						]}
					/>
				</PhoneFrame>
			</div>
			<NotificationStack
				variant="desktop"
				items={[
					{at: 12, title: 'Build passed', body: 'main, 2 min 14 s', icon: 'check', iconColor: t.colors.positive},
					{at: 52, title: 'Maya commented', body: 'Can we move the launch to Thursday?', icon: 'mail', actions: ['Reply', 'Mark read']},
					{at: 92, title: 'Invoice paid', body: 'Harbor & Pine paid $1,240.00', icon: 'wallet', iconColor: t.colors.accent2},
				]}
			/>
			<Notification variant="pill" title="Changes saved" delay={130} />
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiLowerThirds (16:9) and vertical

const LowerThirdsDemo: React.FC = () => (
	<AbsoluteFill>
		<Footage tone="warm" />
		<Sequence durationInFrames={96}>
			<LowerThird variant="bar" name="Maya Chen" role="Head of Product, Driftnote" delay={6} />
		</Sequence>
		<Sequence from={96} durationInFrames={96}>
			<LowerThird variant="split" name="আরিফ রহমান" role="Founder, Coinlet" delay={6} scrim />
		</Sequence>
		<Sequence from={192} durationInFrames={96}>
			<LowerThird variant="minimal" name="Lena Ortiz" role="Design lead" delay={6} scrim side="right" />
		</Sequence>
		<Sequence from={288} durationInFrames={96}>
			<LowerThird variant="card" name="Tanvir Hasan" role="Staff engineer, Taskwell" delay={6} />
		</Sequence>
	</AbsoluteFill>
);

const LowerThirdsVerticalDemo: React.FC = () => (
	<AbsoluteFill>
		<Footage tone="cool" />
		<Sequence durationInFrames={100}>
			<LowerThird variant="bar" name="তানভীর হাসান" role="সফটওয়্যার ইঞ্জিনিয়ার" delay={6} size={1.1} />
		</Sequence>
		<Sequence from={100} durationInFrames={100}>
			<LowerThird variant="minimal" name="Maya Chen" role="Head of Product" delay={6} scrim size={1.1} />
		</Sequence>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiTitles and vertical

const TitlesDemo: React.FC = () => (
	<AbsoluteFill>
		<Sequence durationInFrames={110}>
			<TitleCard kicker="Product update" title={'Notes that\norganize themselves'} accentWord="organize" subtitle="Driftnote now files every page where you would look for it." rule exit={14} />
		</Sequence>
		<Sequence from={110} durationInFrames={110}>
			<SectionTitle index={2} total={5} title="Setting up your workspace" />
		</Sequence>
		<Sequence from={220} durationInFrames={110}>
			<TitleCard kicker="নতুন আপডেট" title={'এক ক্লিকে\nসব নোট গুছিয়ে নিন'} subtitle="অফলাইনেও কাজ করে, পরে নিজে থেকেই সিঙ্ক হয়" align="center" exit={14} />
		</Sequence>
	</AbsoluteFill>
);

const TitlesVerticalDemo: React.FC = () => (
	<AbsoluteFill>
		<Sequence durationInFrames={110}>
			<TitleCard kicker="3 tips" title={'Write less,\nship more'} accentWord="ship" subtitle="How small teams keep launch notes short" exit={14} />
		</Sequence>
		<Sequence from={110} durationInFrames={100}>
			<SectionTitle index={1} total={3} title={'Start with\nthe outcome'} align="center" />
		</Sequence>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiEndCard, vertical, DemoUiSubscribe

const EndCardDemo: React.FC = () => <EndCard slots={2} clickAt={118} doneCta="See you inside" />;

const EndCardVerticalDemo: React.FC = () => (
	<EndCard title={'Start writing\nwith Driftnote'} subtitle="Free for your first three projects." cta="Try it free" handle="@driftnote" url="driftnote.example" logo={<LogoMarkTile />} />
);

const LogoMarkTile: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{width: 64 * unit, height: 64 * unit}}>
			<svg width={64 * unit} height={64 * unit} viewBox={UI_MARKS.note.viewBox}>
				{UI_MARKS.note.parts.map((p, i) => (
					<path key={i} d={p.d} fill={'fill' in p ? (p.fill === 'accent' ? t.colors.accent : t.colors.accent2) : 'none'} stroke={'stroke' in p ? t.colors.onAccent : undefined} strokeWidth={'strokeWidth' in p ? p.strokeWidth : undefined} strokeLinecap="round" />
				))}
			</svg>
		</div>
	);
};

const SubscribeDemo: React.FC = () => {
	const {fps} = useStage();
	const clicks = subscribeClicks({delay: 10}, fps);
	return (
		<AbsoluteFill>
			<Footage tone="cool" />
			<Subscribe delay={10} channel="Studio Loop" handle="@studioloop" />
			<ClickSounds frames={clicks} src={staticFile('ui/click.wav')} volume={0.45} />
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiLogo (all looks) and DemoUiLogoSting

const LOGO_CELLS: {variant: LogoRevealVariant; mark: keyof typeof UI_MARKS; name: string}[] = [
	{variant: 'mask', mark: 'note', name: 'Driftnote'},
	{variant: 'stroke', mark: 'orbit', name: 'Orbitly'},
	{variant: 'scale', mark: 'coin', name: 'Coinlet'},
	{variant: 'split', mark: 'peak', name: 'Taskwell'},
	{variant: 'wipe', mark: 'note', name: 'Driftnote'},
	{variant: 'stroke', mark: 'note', name: 'Driftnote'},
];

const LogoGridDemo: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill style={{background: t.colors.bg, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gridTemplateRows: 'repeat(2, 1fr)', gap: 2 * unit}}>
			{LOGO_CELLS.map((c, i) => (
				<div key={i} style={{position: 'relative', overflow: 'hidden', background: t.colors.bg2}}>
					<LogoReveal variant={c.variant} mark={UI_MARKS[c.mark]} name={c.name} tagline={i === 5 ? 'stack layout' : undefined} layout={i === 5 ? 'stack' : 'row'} size={i === 5 ? 110 : 96} background="none" push={0} delay={6} />
					<Label style={{position: 'absolute', left: 20 * unit, top: 16 * unit}}>{c.variant}</Label>
				</div>
			))}
		</AbsoluteFill>
	);
};

const LogoStingDemo: React.FC = () => <LogoReveal variant="stroke" mark={UI_MARKS.orbit} name="Orbitly" tagline="Plan the week in one view" size={190} exit={16} delay={6} />;

// ------------------------------------------------------------------ DemoUiProgress: chapter bar and countdowns

const ProgressDemo: React.FC = () => {
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<Footage tone="warm" />
			<div style={{position: 'absolute', left: 150 * unit, top: 250 * unit, width: 420 * unit, height: 420 * unit}}>
				<Countdown variant="ring" from={3} delay={10} size={320} go="Go" />
			</div>
			<div style={{position: 'absolute', left: 750 * unit, top: 250 * unit, width: 420 * unit, height: 420 * unit}}>
				<Countdown variant="roll" from={5} delay={10} size={300} go="" />
			</div>
			<div style={{position: 'absolute', left: 1320 * unit, top: 250 * unit, width: 460 * unit, height: 420 * unit}}>
				<Countdown variant="clock" seconds={12} delay={10} size={300} />
			</div>
			<ChapterBar
				delay={4}
				chapters={[
					{title: 'Why offline matters', at: 0},
					{title: 'Setting it up', at: 60},
					{title: 'Syncing a team', at: 130},
					{title: 'What comes next', at: 190},
				]}
			/>
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ DemoUiFrames: every frame in a light and a dark theme

const MiniPage: React.FC<{title: string}> = ({title}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t);
	const u = (v: number) => v * unit;
	return (
		<AbsoluteFill style={{padding: u(40), boxSizing: 'border-box', fontFamily: t.type.body, color: P.text, background: P.page}}>
			<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: u(44), letterSpacing: `${t.tracking.display}em`}}>{title}</div>
			<div style={{fontSize: u(20), color: P.muted, marginTop: u(8)}}>Three drafts ready for review</div>
			<div style={{display: 'flex', gap: u(20), marginTop: u(30)}}>
				{['Pricing page', 'Launch email', 'Help center'].map((c, i) => (
					<div key={c} style={{flex: 1, height: u(170), borderRadius: u(16), background: P.panel, boxShadow: `inset 0 0 0 ${unit}px ${P.line}`, padding: u(20), boxSizing: 'border-box'}}>
						<div style={{width: u(36), height: u(36), borderRadius: u(10), background: [P.accent, P.accent2, P.positive][i]}} />
						<div style={{fontSize: u(20), fontWeight: t.weights.strong, marginTop: u(16)}}>{c}</div>
						<div style={{fontSize: u(16), color: P.muted, marginTop: u(4)}}>Edited today</div>
					</div>
				))}
			</div>
		</AbsoluteFill>
	);
};

const FrameRow: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const shrink = (k: number, w: number, h: number, node: React.ReactNode) => (
		<div style={{width: w * k * unit, height: h * k * unit, position: 'relative', flex: '0 0 auto'}}>
			<div style={{position: 'absolute', left: 0, top: 0, scale: `${k}`, transformOrigin: '0 0'}}>{node}</div>
		</div>
	);
	return (
		<div style={{position: 'relative', flex: 1, background: t.colors.bg, overflow: 'hidden'}}>
			<UiBackdrop variant="glow" />
			<Label style={{position: 'absolute', left: 60 * unit, top: 24 * unit}}>{t.name}</Label>
			<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 44 * unit}}>
				{shrink(0.36, 1440, 900, <BrowserWindow width={1440} height={900} tabs={['Drafts: Driftnote', 'Docs']} url="driftnote.example/drafts"><MiniPage title="Drafts" /></BrowserWindow>)}
				{shrink(0.36, 1100, 760, <MacWindow width={1100} height={760} title="Driftnote" sidebar={<div />} sidebarWidth={220}><MiniPage title="Inbox" /></MacWindow>)}
				<PhoneFrame width={170}>
					<AbsoluteFill style={{padding: `${40 * unit}px ${12 * unit}px`, boxSizing: 'border-box', fontFamily: t.type.body}}>
						<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 20 * unit, color: uiPalette(t).text}}>Notes</div>
						{[0, 1, 2, 3].map((i) => (
							<div key={i} style={{height: 34 * unit, marginTop: 8 * unit, borderRadius: 8 * unit, background: uiPalette(t).panel}} />
						))}
					</AbsoluteFill>
				</PhoneFrame>
				{shrink(0.4, 1100 * 1.16 * 1.04, 1100 * 0.7, <LaptopFrame width={1100}><MiniPage title="Reports" /></LaptopFrame>)}
			</div>
		</div>
	);
};

const FramesDemo: React.FC = () => (
	<AbsoluteFill style={{flexDirection: 'column'}}>
		<ThemeProvider theme="studio">
			<FrameRow />
		</ThemeProvider>
		<ThemeProvider theme="midnight">
			<FrameRow />
		</ThemeProvider>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiCodeTsx: JSX colours, typed by line

const TSX_CODE = `export const PriceTag = ({amount, sale}: Props) => {
  const label = sale ? 'Sale price' : 'Price';
  return (
    <div className="tag" aria-label={label}>
      <span>{formatMoney(amount)}</span>
      {sale && <Badge tone="accent">-20%</Badge>}
    </div>
  );
};`;

const CodeTsxDemo: React.FC = () => (
	<AbsoluteFill>
		<UiBackdrop variant="glow" />
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
			<CodeBlock code={TSX_CODE} lang="tsx" title="PriceTag.tsx" typing="line" startAt={4} lineEvery={5} width={1180} fontSize={30} focus={[{lines: '4-7', at: 80}]} />
		</AbsoluteFill>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiThemeCheck: caps, serif, square and hand-drawn themes

const ThemeCheckDemo: React.FC = () => (
	<AbsoluteFill>
		<Sequence durationInFrames={75}>
			<ThemeProvider theme="kinetic">
				<TitleCard kicker="New season" title={'Built for\nspeed'} accentWord="speed" exit={12} />
			</ThemeProvider>
		</Sequence>
		<Sequence from={75} durationInFrames={75}>
			<ThemeProvider theme="luxury">
				<Footage tone="warm" />
				<LowerThird variant="minimal" name="Amara Okafor" role="Creative director" scrim delay={4} />
			</ThemeProvider>
		</Sequence>
		<Sequence from={150} durationInFrames={75}>
			<ThemeProvider theme="brutalist">
				<Footage tone="cool" />
				<LowerThird variant="bar" name="Tanvir Hasan" role="Founder, Taskwell" delay={4} />
			</ThemeProvider>
		</Sequence>
		<Sequence from={225} durationInFrames={75}>
			<ThemeProvider theme="whiteboard">
				<SectionTitle index={3} total={4} title="Draw the flow first" />
			</ThemeProvider>
		</Sequence>
		<Sequence from={300} durationInFrames={75}>
			<ThemeProvider theme="retro">
				<LogoReveal variant="scale" mark={UI_MARKS.coin} name="Coin" tagline="Budgets that add up" exit={12} />
			</ThemeProvider>
		</Sequence>
	</AbsoluteFill>
);

// ------------------------------------------------------------------ DemoUiScale4k: the same scene at 3840 x 2160 (unit = 2)

const SCALE_KEYS: CursorKey[] = [
	{x: 900, y: 520, at: 4},
	{x: 1260, y: 130, at: 30, click: true},
];

const Scale4kDemo: React.FC = () => {
	const {fps} = useStage();
	const tl = cursorTimeline(SCALE_KEYS, fps);
	return (
		<AbsoluteFill>
			<UiBackdrop variant="dots" />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
				<BrowserWindow width={1440} height={800} url="driftnote.example/drafts" tabs={['Drafts: Driftnote']}>
					<MiniPage title="Drafts" />
					<ScaledButton pressAt={tl.pressOf(1)} />
					<Cursor keys={SCALE_KEYS} />
				</BrowserWindow>
			</AbsoluteFill>
			<LowerThird variant="bar" name="Maya Chen" role="Head of Product" delay={6} />
		</AbsoluteFill>
	);
};

const ScaledButton: React.FC<{pressAt?: number}> = ({pressAt}) => {
	const {unit} = useStage();
	return (
		<div style={{position: 'absolute', left: 1160 * unit, top: 100 * unit}}>
			<UiButton label="Publish" width={200} pressAt={pressAt} doneLabel="Published" doneIcon="check" />
		</div>
	);
};

export const demos: DemoDef[] = [
	{id: 'DemoUiCursorShapes', component: themed('studio', Shapes), durationInFrames: 20},
	{id: 'DemoUiCursor', component: themed('studio', CursorDemo), durationInFrames: 190},
	{id: 'DemoUiInputs', component: themed('midnight', InputsDemo), durationInFrames: 190},
	{id: 'DemoUiBrowser', component: themed('studio', BrowserDemo), durationInFrames: 260},
	{id: 'DemoUiLaptop', component: themed('midnight', LaptopDemo), durationInFrames: 270},
	{id: 'DemoUiPhone', component: themed('keynoteLight', PhoneDemo), durationInFrames: 180},
	{id: 'DemoUiApp', component: themed('fresh', AppDemo), durationInFrames: 300, width: 1080, height: 1920},
	{id: 'DemoUiCode', component: themed('midnight', CodeDemo), durationInFrames: 250},
	{id: 'DemoUiCodeLight', component: themed('studio', CodeLightDemo), durationInFrames: 230},
	{id: 'DemoUiTerminal', component: themed('terminal', TerminalDemo), durationInFrames: 330},
	{id: 'DemoUiChat', component: themed('studio', ChatDemo), durationInFrames: 300},
	{id: 'DemoUiChatVertical', component: themed('midnight', ChatVerticalDemo), durationInFrames: 260, width: 1080, height: 1920},
	{id: 'DemoUiToast', component: themed('midnight', ToastDemo), durationInFrames: 190},
	{id: 'DemoUiLowerThirds', component: themed('studio', LowerThirdsDemo), durationInFrames: 384},
	{id: 'DemoUiLowerThirdsVertical', component: themed('midnight', LowerThirdsVerticalDemo), durationInFrames: 200, width: 1080, height: 1920},
	{id: 'DemoUiTitles', component: themed('studio', TitlesDemo), durationInFrames: 330},
	{id: 'DemoUiTitlesVertical', component: themed('fresh', TitlesVerticalDemo), durationInFrames: 210, width: 1080, height: 1920},
	{id: 'DemoUiEndCard', component: themed('midnight', EndCardDemo), durationInFrames: 180},
	{id: 'DemoUiEndCardVertical', component: themed('fresh', EndCardVerticalDemo), durationInFrames: 120, width: 1080, height: 1920},
	{id: 'DemoUiSubscribe', component: themed('studio', SubscribeDemo), durationInFrames: 150},
	{id: 'DemoUiLogo', component: themed('studio', LogoGridDemo), durationInFrames: 110},
	{id: 'DemoUiLogoSting', component: themed('midnight', LogoStingDemo), durationInFrames: 150},
	{id: 'DemoUiProgress', component: themed('studio', ProgressDemo), durationInFrames: 240},
	{id: 'DemoUiFrames', component: FramesDemo, durationInFrames: 2},
	{id: 'DemoUiCodeTsx', component: themed('keynote', CodeTsxDemo), durationInFrames: 130},
	{id: 'DemoUiThemeCheck', component: ThemeCheckDemo, durationInFrames: 375},
	{id: 'DemoUiScale4k', component: themed('studio', Scale4kDemo), durationInFrames: 60, width: 3840, height: 2160},
];
