// Device and window frames. Each takes its screen as children and sizes in px at 1080, reads the theme for light or
// dark materials, and draws no brand marks. Also: a 3D rise for bringing a device in, a scroll view for page content
// and a lit ground to stand devices on.
import React, {createContext, useContext} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp, track} from '../motion';
import {UiIcon} from './Icon';
import {blend, fade, lum, shadowFor, uiPalette, useUiLife, useUiTyping, type UiMode} from './shared';

// ------------------------------------------------------------------ window controls

const Lights: React.FC<{mono?: boolean; dark: boolean; size?: number}> = ({mono = false, dark, size = 13}) => {
	const {unit} = useStage();
	const colors = mono ? (dark ? ['#4A4F59', '#4A4F59', '#4A4F59'] : ['#D3D7DE', '#D3D7DE', '#D3D7DE']) : ['#FF5F57', '#FEBC2E', '#28C840'];
	return (
		<div style={{display: 'flex', gap: size * 0.62 * unit, flex: '0 0 auto'}}>
			{colors.map((c, i) => (
				<div key={i} style={{width: size * unit, height: size * unit, borderRadius: '50%', background: c, boxShadow: `inset 0 0 0 ${0.8 * unit}px rgba(0, 0, 0, ${dark ? 0.25 : 0.12})`}} />
			))}
		</div>
	);
};

// ------------------------------------------------------------------ BrowserWindow

export type BrowserTab = string | {title: string; letter?: string; color?: string};

export type BrowserWindowProps = {
	width?: number; // px at 1080 (default 1440)
	height?: number; // default 860
	url?: string;
	typeUrlAt?: number; // the address types itself from this frame
	tabs?: BrowserTab[]; // omit for a compact single-row window
	activeTab?: number;
	loadAt?: number; // a thin loading bar runs under the toolbar from this frame
	controls?: 'color' | 'mono';
	mode?: UiMode;
	page?: string; // page background (default: the palette's page colour)
	radius?: number; // px at 1080 (default 14)
	shadow?: boolean;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** Height of the browser chrome above the page, px at 1080: use it to place things on the page from outside. */
export const browserChromeHeight = (withTabs: boolean): number => (withTabs ? 44 + 54 : 58);

/** A browser window: tabs, an address bar with a lock, and the page as children. */
export const BrowserWindow: React.FC<BrowserWindowProps> = ({
	width = 1440,
	height = 860,
	url = 'driftnote.example/workspace',
	typeUrlAt,
	tabs,
	activeTab = 0,
	loadAt,
	controls = 'color',
	mode = 'auto',
	page,
	radius = 14,
	shadow = true,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const typed = useUiTyping(url, typeUrlAt ?? -1e6, {cps: 22, seed: `url-${url}`});
	const shownUrl = typeUrlAt === undefined ? url : typed.shown;
	const slash = shownUrl.indexOf('/');
	const domain = slash < 0 ? shownUrl : shownUrl.slice(0, slash);
	const path = slash < 0 ? '' : shownUrl.slice(slash);
	const load = loadAt === undefined ? 0 : ramp(frame, loadAt, at30(22, fps), curves.outCubic);
	const loadGone = loadAt === undefined ? 1 : ramp(frame, loadAt + at30(22, fps), at30(8, fps), curves.out);
	const hasTabs = Boolean(tabs && tabs.length);
	const topH = browserChromeHeight(hasTabs);
	const toolH = hasTabs ? 54 : 58;
	const chromeBg = hasTabs ? P.chrome : P.bar;
	return (
		<div
			style={{
				position: 'relative',
				width: width * unit,
				height: height * unit,
				borderRadius: radius * unit,
				overflow: 'hidden',
				background: page ?? P.page,
				boxShadow: shadow ? shadowFor(P.dark, unit, 3) : `0 0 0 ${unit}px ${P.line}`,
				fontFamily: t.type.body,
				...style,
			}}
		>
			{hasTabs ? (
				<div style={{height: 44 * unit, display: 'flex', alignItems: 'flex-end', gap: 2 * unit, padding: `0 ${14 * unit}px`, background: chromeBg}}>
					<div style={{height: 44 * unit, display: 'flex', alignItems: 'center', marginRight: 14 * unit}}>
						<Lights mono={controls === 'mono'} dark={P.dark} />
					</div>
					{tabs!.map((tab, i) => {
						const tt = typeof tab === 'string' ? {title: tab} : tab;
						const active = i === activeTab;
						const letter = tt.letter ?? tt.title.slice(0, 1).toUpperCase();
						return (
							<div
								key={i}
								style={{
									height: 36 * unit,
									width: 236 * unit,
									display: 'flex',
									alignItems: 'center',
									gap: 10 * unit,
									padding: `0 ${14 * unit}px`,
									boxSizing: 'border-box',
									borderRadius: `${10 * unit}px ${10 * unit}px 0 0`,
									background: active ? P.bar : 'transparent',
									color: active ? P.text : P.muted,
									fontSize: 16 * unit,
									fontWeight: active ? t.weights.strong : t.weights.body,
									position: 'relative',
								}}
							>
								<div style={{width: 20 * unit, height: 20 * unit, borderRadius: 6 * unit, background: tt.color ?? (active ? P.accent : blend(P.muted, chromeBg, 0.4)), color: '#FFFFFF', fontSize: 12 * unit, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto'}}>
									{letter}
								</div>
								<div style={{flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{tt.title}</div>
								<UiIcon name="x" size={14} color={P.muted} />
								{!active && i !== activeTab - 1 ? <div style={{position: 'absolute', right: -1 * unit, top: 9 * unit, width: unit, height: 18 * unit, background: P.line}} /> : null}
							</div>
						);
					})}
					<div style={{height: 36 * unit, display: 'flex', alignItems: 'center', padding: `0 ${10 * unit}px`}}>
						<UiIcon name="plus" size={16} color={P.muted} />
					</div>
				</div>
			) : null}
			<div
				style={{
					position: 'relative',
					height: toolH * unit,
					display: 'flex',
					alignItems: 'center',
					gap: 16 * unit,
					padding: `0 ${18 * unit}px`,
					background: P.bar,
					borderBottom: `${unit}px solid ${P.line}`,
				}}
			>
				{hasTabs ? null : <Lights mono={controls === 'mono'} dark={P.dark} />}
				<div style={{display: 'flex', gap: 14 * unit, alignItems: 'center', marginLeft: hasTabs ? 0 : 8 * unit}}>
					<UiIcon name="arrowLeft" size={20} color={P.muted} />
					<UiIcon name="arrowRight" size={20} color={P.faint} />
					<UiIcon name="refresh" size={19} color={P.muted} />
				</div>
				<div
					style={{
						flex: 1,
						height: 36 * unit,
						borderRadius: 18 * unit,
						background: P.field,
						display: 'flex',
						alignItems: 'center',
						gap: 9 * unit,
						padding: `0 ${16 * unit}px`,
						fontSize: 17 * unit,
						color: P.muted,
						whiteSpace: 'pre',
						overflow: 'hidden',
						boxShadow: typeUrlAt !== undefined && typed.started && !typed.done ? `0 0 0 ${2 * unit}px ${fade(P.accent, 0.5)}` : undefined,
					}}
				>
					<UiIcon name="lock" size={15} color={P.muted} stroke={2.2} />
					<span>
						<span style={{color: P.text}}>{domain}</span>
						{path}
					</span>
					{typeUrlAt !== undefined && typed.started && !typed.done ? <span style={{width: 2 * unit, height: 20 * unit, background: P.accent, marginLeft: -6 * unit}} /> : null}
				</div>
				<UiIcon name="share" size={19} color={P.muted} />
				<div style={{width: 28 * unit, height: 28 * unit, borderRadius: '50%', background: blend(P.accent, P.bar, 0.25), color: P.onAccent, fontSize: 13 * unit, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>M</div>
				{loadAt !== undefined && load > 0 ? (
					<div style={{position: 'absolute', left: 0, bottom: -1 * unit, height: 3 * unit, width: `${load * 100}%`, background: P.accent, opacity: 1 - loadGone}} />
				) : null}
			</div>
			<div style={{position: 'absolute', left: 0, top: topH * unit, right: 0, bottom: 0, overflow: 'hidden'}}>{children}</div>
		</div>
	);
};

// ------------------------------------------------------------------ MacWindow

export type MacWindowProps = {
	width?: number; // px at 1080 (default 1280)
	height?: number; // default 800
	title?: string;
	toolbar?: React.ReactNode; // right side of the title bar
	sidebar?: React.ReactNode;
	sidebarWidth?: number; // default 280
	controls?: 'color' | 'mono';
	mode?: UiMode;
	radius?: number; // default 14
	shadow?: boolean;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** Height of the title bar, px at 1080. */
export const MAC_TITLE_HEIGHT = 52;

/** A desktop app window: title bar with window controls, an optional sidebar, content as children. */
export const MacWindow: React.FC<MacWindowProps> = ({
	width = 1280,
	height = 800,
	title = 'Untitled',
	toolbar,
	sidebar,
	sidebarWidth = 280,
	controls = 'color',
	mode = 'auto',
	radius = 14,
	shadow = true,
	children,
	style,
}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t, mode);
	return (
		<div
			style={{
				position: 'relative',
				width: width * unit,
				height: height * unit,
				borderRadius: radius * unit,
				overflow: 'hidden',
				background: P.page,
				boxShadow: shadow ? shadowFor(P.dark, unit, 3) : `0 0 0 ${unit}px ${P.line}`,
				fontFamily: t.type.body,
				display: 'flex',
				flexDirection: 'column',
				...style,
			}}
		>
			<div style={{height: MAC_TITLE_HEIGHT * unit, flex: '0 0 auto', display: 'flex', alignItems: 'center', padding: `0 ${18 * unit}px`, background: P.chrome, borderBottom: `${unit}px solid ${P.line}`, position: 'relative'}}>
				<Lights mono={controls === 'mono'} dark={P.dark} />
				<div style={{position: 'absolute', left: 0, right: 0, textAlign: 'center', fontSize: 17 * unit, fontWeight: t.weights.strong, color: P.text, pointerEvents: 'none', whiteSpace: 'nowrap'}}>{title}</div>
				<div style={{marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 * unit, color: P.muted}}>{toolbar}</div>
			</div>
			<div style={{flex: 1, minHeight: 0, display: 'flex', position: 'relative'}}>
				{sidebar ? (
					<div style={{width: sidebarWidth * unit, flex: '0 0 auto', background: P.panel, borderRight: `${unit}px solid ${P.line}`, position: 'relative', overflow: 'hidden'}}>{sidebar}</div>
				) : null}
				<div style={{flex: 1, minWidth: 0, position: 'relative', overflow: 'hidden'}}>{children}</div>
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ PhoneFrame

export type PhoneScreen = {
	w: number; // screen width, px at 1080
	h: number; // screen height
	top: number; // status bar height: start content below it
	bottom: number; // home indicator area at the bottom
	radius: number;
};

/** Screen geometry of a PhoneFrame of body width `width` (px at 1080). */
export const phoneScreen = (width = 400): PhoneScreen => {
	const bezel = width * 0.03;
	const w = width - 2 * bezel;
	const h = width * 2.06 - 2 * bezel;
	return {w, h, top: width * 0.135, bottom: width * 0.075, radius: width * 0.155 - bezel};
};

const PhoneContext = createContext<PhoneScreen | null>(null);

/** Inside a PhoneFrame's children: the screen size and its safe insets, px at 1080. */
export const usePhoneScreen = (): PhoneScreen => useContext(PhoneContext) ?? phoneScreen();

/** The screen of the PhoneFrame this component sits in, or null outside a phone. */
export const useInsidePhone = (): PhoneScreen | null => useContext(PhoneContext);

export type StatusBarProps = {
	width: number; // px at 1080 (the screen width)
	time?: string;
	tone?: 'dark' | 'light'; // dark icons (for light screens) or light icons
	battery?: number; // 0 to 1
};

/** Time on the left, signal, wifi and battery on the right. */
export const StatusBar: React.FC<StatusBarProps> = ({width, time = '10:24', tone = 'dark', battery = 0.8}) => {
	const t = useTheme();
	const {unit} = useStage();
	const c = tone === 'dark' ? '#0B0C0F' : '#FFFFFF';
	const s = width / 380;
	const bar = (h: number, i: number) => <div key={i} style={{width: 3.6 * s * unit, height: h * s * unit, borderRadius: 1.2 * s * unit, background: c}} />;
	return (
		<div style={{height: width * 0.135 * unit, display: 'flex', alignItems: 'center', padding: `0 ${width * 0.085 * unit}px`, paddingTop: 4 * s * unit, boxSizing: 'border-box', color: c}}>
			<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 16.5 * s * unit, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em'}}>{time}</div>
			<div style={{marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 * s * unit}}>
				<div style={{display: 'flex', alignItems: 'flex-end', gap: 1.8 * s * unit, height: 12 * s * unit}}>{[5, 7.4, 9.8, 12].map(bar)}</div>
				<UiIcon name="wifi" size={17 * s} color={c} stroke={2.4} />
				<div style={{position: 'relative', width: 26 * s * unit, height: 12.5 * s * unit, borderRadius: 3.8 * s * unit, border: `${1.2 * s * unit}px solid ${tone === 'dark' ? 'rgba(11,12,15,0.4)' : 'rgba(255,255,255,0.5)'}`, boxSizing: 'border-box', padding: 1.6 * s * unit}}>
					<div style={{width: `${battery * 100}%`, height: '100%', borderRadius: 2 * s * unit, background: c}} />
					<div style={{position: 'absolute', right: -3.4 * s * unit, top: 3.4 * s * unit, width: 1.8 * s * unit, height: 4 * s * unit, borderRadius: `0 ${unit}px ${unit}px 0`, background: tone === 'dark' ? 'rgba(11,12,15,0.4)' : 'rgba(255,255,255,0.5)'}} />
				</div>
			</div>
		</div>
	);
};

export type PhoneFrameProps = {
	width?: number; // body width, px at 1080 (default 400; the body is 2.06 times as tall)
	finish?: 'auto' | 'graphite' | 'silver' | 'sand';
	camera?: 'pill' | 'dot' | 'none';
	statusBar?: 'dark' | 'light' | 'none' | 'auto'; // icon colour; auto picks from the screen colour
	barFill?: boolean | string; // a strip behind the status bar (the screen colour, or this colour) for content that scrolls under it
	time?: string;
	screen?: string; // screen background (default: the palette page colour)
	mode?: UiMode;
	homeIndicator?: boolean;
	glare?: boolean; // a faint diagonal reflection on the glass
	shadow?: boolean;
	children?: React.ReactNode; // the screen: fills it, under the status bar
	style?: React.CSSProperties;
};

const FINISH = {
	graphite: {edge: 'linear-gradient(150deg, #6B6F77 0%, #2B2D32 22%, #4B4E55 55%, #1F2024 80%, #5A5E66 100%)', button: '#34363B'},
	silver: {edge: 'linear-gradient(150deg, #F4F5F7 0%, #B9BDC4 25%, #E6E8EC 55%, #A7ABB3 80%, #EDEFF2 100%)', button: '#BFC3CA'},
	sand: {edge: 'linear-gradient(150deg, #EFE3D3 0%, #B8A68F 25%, #E2D4C1 55%, #A8967F 80%, #EFE5D8 100%)', button: '#BBAA93'},
};

/** A modern phone with a screen slot: metal rim, side buttons, a camera cut-out, status bar and home indicator. */
export const PhoneFrame: React.FC<PhoneFrameProps> = ({
	width = 400,
	finish = 'auto',
	camera = 'pill',
	statusBar = 'auto',
	barFill = false,
	time = '10:24',
	screen,
	mode = 'auto',
	homeIndicator = true,
	glare = true,
	shadow = true,
	children,
	style,
}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t, mode);
	const f = FINISH[finish === 'auto' ? (t.dark ? 'silver' : 'graphite') : finish];
	const W = width;
	const H = width * 2.06;
	const rim = W * 0.009;
	const bezel = W * 0.03;
	const S = phoneScreen(W);
	const bg = screen ?? P.page;
	const screenIsDark = lum(bg) < 0.3;
	const tone: 'light' | 'dark' = statusBar === 'auto' || statusBar === 'none' ? (screenIsDark ? 'light' : 'dark') : statusBar;
	const u = (v: number) => v * unit;
	const side = (top: number, h: number, left: boolean) => (
		<div
			style={{
				position: 'absolute',
				top: u(H * top),
				height: u(H * h),
				width: u(W * 0.014),
				[left ? 'left' : 'right']: u(-W * 0.009),
				borderRadius: u(W * 0.006),
				background: f.button,
				boxShadow: `inset ${left ? 1 : -1}px 0 0 rgba(255,255,255,0.18)`,
			}}
		/>
	);
	return (
		<div style={{position: 'relative', width: u(W), height: u(H), flex: '0 0 auto', ...style}}>
			{side(0.17, 0.045, true)}
			{side(0.245, 0.075, true)}
			{side(0.335, 0.075, true)}
			{side(0.27, 0.11, false)}
			<div
				style={{
					position: 'absolute',
					inset: 0,
					borderRadius: u(W * 0.155),
					background: f.edge,
					boxShadow: shadow ? `0 ${u(40)}px ${u(80)}px rgba(10, 12, 20, ${t.dark ? 0.55 : 0.22}), 0 ${u(12)}px ${u(24)}px rgba(10, 12, 20, ${t.dark ? 0.4 : 0.14})` : undefined,
				}}
			/>
			<div style={{position: 'absolute', inset: u(rim), borderRadius: u(W * 0.155 - rim), background: '#050506'}} />
			<div
				style={{
					position: 'absolute',
					left: u(bezel),
					top: u(bezel),
					width: u(S.w),
					height: u(S.h),
					borderRadius: u(S.radius),
					overflow: 'hidden',
					background: bg,
					isolation: 'isolate',
				}}
			>
				<PhoneContext.Provider value={S}>{children}</PhoneContext.Provider>
				{barFill ? <div style={{position: 'absolute', left: 0, top: 0, width: u(S.w), height: u(S.top), zIndex: 29, background: typeof barFill === 'string' ? barFill : fade(bg, 0.94), boxShadow: `0 ${u(1)}px 0 ${fade(screenIsDark ? '#FFFFFF' : '#000000', 0.06)}`}} /> : null}
				{statusBar !== 'none' ? (
					<div style={{position: 'absolute', left: 0, top: 0, width: u(S.w), zIndex: 30}}>
						<StatusBar width={S.w} time={time} tone={tone} />
					</div>
				) : null}
				{homeIndicator ? (
					<div style={{position: 'absolute', left: u(S.w * 0.33), bottom: u(W * 0.02), width: u(S.w * 0.34), height: u(W * 0.0125), borderRadius: u(W * 0.01), background: tone === 'dark' ? 'rgba(10,10,12,0.85)' : 'rgba(255,255,255,0.85)', zIndex: 30}} />
				) : null}
				{glare ? <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(118deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.03) 28%, rgba(255,255,255,0) 42%)', pointerEvents: 'none', zIndex: 31}} /> : null}
			</div>
			{camera === 'pill' ? (
				<div style={{position: 'absolute', left: u(W / 2 - W * 0.14), top: u(bezel + W * 0.027), width: u(W * 0.28), height: u(W * 0.083), borderRadius: u(W * 0.05), background: '#000000', zIndex: 32}}>
					<div style={{position: 'absolute', right: u(W * 0.03), top: u(W * 0.024), width: u(W * 0.035), height: u(W * 0.035), borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #2A3348 0%, #0B0E16 60%)'}} />
				</div>
			) : camera === 'dot' ? (
				<div style={{position: 'absolute', left: u(W / 2 - W * 0.031), top: u(bezel + W * 0.03), width: u(W * 0.062), height: u(W * 0.062), borderRadius: '50%', background: '#000000', zIndex: 32, boxShadow: `0 0 0 ${u(W * 0.006)}px rgba(255,255,255,0.05)`}} />
			) : null}
		</div>
	);
};

// ------------------------------------------------------------------ LaptopFrame

export type LaptopFrameProps = {
	width?: number; // screen width, px at 1080 (default 1100; the screen is 16:10)
	finish?: 'auto' | 'silver' | 'space';
	screen?: string; // screen background
	mode?: UiMode;
	shadow?: boolean;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** Screen size of a LaptopFrame, px at 1080. */
export const laptopScreen = (width = 1100): {w: number; h: number} => ({w: width, h: width * 0.625});

/** A laptop: a thin black bezel with a camera dot, and the base with its thumb scoop. */
export const LaptopFrame: React.FC<LaptopFrameProps> = ({width = 1100, finish = 'auto', screen, mode = 'auto', shadow = true, children, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	const P = uiPalette(t, mode);
	const fin = finish === 'auto' ? (t.dark ? 'silver' : 'space') : finish;
	const metal = fin === 'silver' ? ['#E8EAEE', '#C5C9D0', '#9EA3AB'] : ['#5C6068', '#3E4148', '#2A2C31'];
	const u = (v: number) => v * unit;
	const S = laptopScreen(width);
	const side = width * 0.02;
	const top = width * 0.03;
	const chin = width * 0.03;
	const lidW = S.w + 2 * side;
	const lidH = S.h + top + chin;
	const baseW = lidW * 1.16;
	const baseH = width * 0.024;
	return (
		<div style={{position: 'relative', width: u(baseW), height: u(lidH + baseH + width * 0.006), flex: '0 0 auto', ...style}}>
			<div
				style={{
					position: 'absolute',
					left: u((baseW - lidW) / 2),
					top: 0,
					width: u(lidW),
					height: u(lidH),
					borderRadius: `${u(width * 0.024)}px ${u(width * 0.024)}px ${u(width * 0.006)}px ${u(width * 0.006)}px`,
					background: '#0A0A0C',
					boxShadow: `0 0 0 ${u(width * 0.0028)}px ${metal[1]}, inset 0 0 0 ${u(1)}px rgba(255,255,255,0.06)`,
				}}
			>
				<div style={{position: 'absolute', left: u(lidW / 2 - width * 0.004), top: u(top / 2 - width * 0.004), width: u(width * 0.008), height: u(width * 0.008), borderRadius: '50%', background: '#1C2230', boxShadow: `inset 0 0 ${u(1)}px rgba(120,140,190,0.6)`}} />
				<div style={{position: 'absolute', left: u(side), top: u(top), width: u(S.w), height: u(S.h), overflow: 'hidden', background: screen ?? P.page, borderRadius: u(width * 0.004)}}>
					{children}
					<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(125deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 35%)', pointerEvents: 'none'}} />
				</div>
			</div>
			<div style={{position: 'absolute', left: u((baseW - lidW * 0.97) / 2), top: u(lidH), width: u(lidW * 0.97), height: u(width * 0.006), background: '#15161A'}} />
			<div
				style={{
					position: 'absolute',
					left: 0,
					top: u(lidH + width * 0.006),
					width: u(baseW),
					height: u(baseH),
					borderRadius: `${u(width * 0.004)}px ${u(width * 0.004)}px ${u(width * 0.03)}px ${u(width * 0.03)}px`,
					background: `linear-gradient(180deg, ${metal[0]} 0%, ${metal[1]} 45%, ${metal[2]} 100%)`,
					boxShadow: shadow ? `0 ${u(30)}px ${u(60)}px rgba(10, 12, 20, ${t.dark ? 0.55 : 0.22}), 0 ${u(8)}px ${u(16)}px rgba(10, 12, 20, 0.15)` : undefined,
				}}
			>
				<div style={{position: 'absolute', left: u(baseW / 2 - width * 0.075), top: 0, width: u(width * 0.15), height: u(baseH * 0.38), borderRadius: `0 0 ${u(width * 0.012)}px ${u(width * 0.012)}px`, background: `linear-gradient(180deg, ${blend(metal[2], '#000000', 0.25)} 0%, ${metal[1]} 100%)`}} />
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ DeviceRise

export type DeviceRiseProps = {
	delay?: number;
	duration?: number; // entrance frames (default 30 at 30 fps: a hero move)
	tilt?: number; // degrees it starts tipped back (default 28)
	distance?: number; // px at 1080 it rises (default 160)
	exit?: number | false; // exit frames (default false: stays)
	exitAt?: number;
	ease?: Ease;
	origin?: string; // default 'center bottom'
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** A device rises into place, tipping up from lying back (the keynote device entrance), and optionally leaves. */
export const DeviceRise: React.FC<DeviceRiseProps> = ({delay = 0, duration, tilt = 28, distance = 160, exit = false, exitAt, ease = curves.out, origin = '50% 100%', children, style}) => {
	const {fps, unit} = useStage();
	const life = useUiLife({delay, enter: duration ?? at30(30, fps), exit, exitAt});
	const p = life.enter(0, life.inFrames, ease);
	const q = life.leave();
	// the fade runs on its own even curve: on the motion's ease-in a bright device vanished in the last frames (a
	// brightness jump the QA flags)
	const fade = life.leave(0, undefined, curves.sine);
	const o = Math.min(1, p * 2.2) * (1 - fade);
	const rot = tilt * (1 - p) + -tilt * 0.5 * q;
	const y = distance * (1 - p) + distance * 0.6 * q;
	const s = 0.9 + 0.1 * p - 0.04 * q;
	return (
		<div style={{perspective: 1800 * unit, ...style}}>
			<div style={{transformOrigin: origin, transform: `translateY(${y * unit}px) rotateX(${rot}deg) scale(${s})`, opacity: o}}>{children}</div>
		</div>
	);
};

// ------------------------------------------------------------------ ScrollView

export type ScrollKey = {at: number; y: number}; // y: px at 1080 scrolled from the top

export type ScrollViewProps = {
	keys: ScrollKey[];
	ease?: Ease | Ease[]; // default: a smooth in-out per move
	scrollbar?: boolean; // a thin bar that shows while it moves
	mode?: UiMode;
	children: React.ReactNode;
	style?: React.CSSProperties;
};

/** Page content that scrolls between keyframes; fills its parent. Repeat a y on a later frame to hold. */
export const ScrollView: React.FC<ScrollViewProps> = ({keys, ease = curves.inOut, scrollbar = true, mode = 'auto', children, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const ks = [...keys].sort((a, b) => a.at - b.at);
	const y = ks.length === 0 ? 0 : ks.length === 1 ? ks[0].y : track(frame, ks.map((k) => k.at), ks.map((k) => k.y), ease);
	let moving = 0;
	for (let i = 1; i < ks.length; i++) {
		if (ks[i].y !== ks[i - 1].y) {
			const inn = ramp(frame, ks[i - 1].at - at30(2, fps), at30(4, fps), curves.out);
			const out = 1 - ramp(frame, ks[i].at + at30(10, fps), at30(8, fps), curves.in);
			moving = Math.max(moving, Math.min(inn, out));
		}
	}
	const maxY = Math.max(1, ...ks.map((k) => k.y));
	// the bar's position shows how far the page has scrolled between its first and last key
	const barH = 22;
	const progress = Math.min(1, Math.max(0, y / maxY));
	return (
		<div style={{position: 'absolute', inset: 0, overflow: 'hidden', ...style}}>
			<div style={{translate: `0px ${-y * unit}px`}}>{children}</div>
			{scrollbar && moving > 0.001 ? (
				<div
					style={{
						position: 'absolute',
						right: 5 * unit,
						top: `${progress * (100 - barH)}%`,
						height: `${barH}%`,
						width: 6 * unit,
						borderRadius: 3 * unit,
						background: fade(P.text, 0.35),
						opacity: moving,
					}}
				/>
			) : null}
		</div>
	);
};

// ------------------------------------------------------------------ UiBackdrop

export type UiBackdropProps = {
	variant?: 'glow' | 'dots' | 'plain';
	color?: string; // ground colour (default: the theme background)
	light?: string; // the tint of the light (default: the accent)
	style?: React.CSSProperties;
};

/** A lit ground for product shots: never a flat vacuum behind a device. */
export const UiBackdrop: React.FC<UiBackdropProps> = ({variant = 'glow', color, light, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	const bg = color ?? t.colors.bg;
	const tint = light ?? t.colors.accent;
	const glow = `radial-gradient(ellipse 70% 60% at 50% 18%, ${fade(tint, t.dark ? 0.16 : 0.1)} 0%, ${fade(tint, 0)} 70%), radial-gradient(ellipse 90% 70% at 50% 110%, ${fade(t.dark ? '#000000' : t.colors.text, t.dark ? 0.35 : 0.05)} 0%, rgba(0,0,0,0) 70%)`;
	const dots = `radial-gradient(${fade(t.colors.text, t.dark ? 0.12 : 0.1)} ${1.3 * unit}px, transparent ${1.6 * unit}px)`;
	return (
		<AbsoluteFill style={{background: bg, ...style}}>
			{variant !== 'plain' ? <AbsoluteFill style={{background: glow}} /> : null}
			{variant === 'dots' ? (
				<AbsoluteFill
					style={{
						backgroundImage: dots,
						backgroundSize: `${28 * unit}px ${28 * unit}px`,
						WebkitMaskImage: 'radial-gradient(ellipse 75% 70% at 50% 45%, #000 20%, transparent 75%)',
						maskImage: 'radial-gradient(ellipse 75% 70% at 50% 45%, #000 20%, transparent 75%)',
					}}
				/>
			) : null}
		</AbsoluteFill>
	);
};
