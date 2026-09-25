// Frame formats, safe areas and the size unit. Sizes in the kit are written for a 1080 px short side and
// multiplied by `unit`, so the same scene works at 1080p, in 9:16 and at 4K.
import React, {createContext, useContext} from 'react';
import {useVideoConfig} from 'remotion';

export type Rect = {x: number; y: number; w: number; h: number};
export type FormatName = 'youtube' | '4k' | 'shorts' | 'reels' | 'tiktok' | 'story' | 'feed' | 'square';

// The same numbers as nrk.py and nexa-video-creator's targets.
export const FORMATS: Record<FormatName, {width: number; height: number; safe: Rect; note: string}> = {
	youtube: {width: 1920, height: 1080, safe: {x: 96, y: 54, w: 1728, h: 972}, note: '16:9, 5% margins'},
	'4k': {width: 3840, height: 2160, safe: {x: 192, y: 108, w: 3456, h: 1944}, note: '16:9 at 4K'},
	shorts: {width: 1080, height: 1920, safe: {x: 65, y: 270, w: 875, h: 978}, note: 'clear of the title, buttons and caption'},
	reels: {width: 1080, height: 1920, safe: {x: 65, y: 270, w: 875, h: 978}, note: 'clear of the profile row and buttons'},
	tiktok: {width: 1080, height: 1920, safe: {x: 65, y: 270, w: 875, h: 978}, note: 'clear of the caption and right rail'},
	story: {width: 1080, height: 1920, safe: {x: 65, y: 270, w: 950, h: 978}, note: 'clear of the top bar and reply box'},
	feed: {width: 1080, height: 1350, safe: {x: 54, y: 68, w: 972, h: 1215}, note: '4:5 feed, 5% margins'},
	square: {width: 1080, height: 1080, safe: {x: 54, y: 54, w: 972, h: 972}, note: '1:1, 5% margins'},
};

/** The safe area for a frame: the format's own (scaled), a known format with the same shape, or 5% margins. */
export const safeAreaFor = (width: number, height: number, format?: FormatName): Rect => {
	const pick = format ? FORMATS[format] : Object.values(FORMATS).find((f) => f.width * height === f.height * width);
	if (pick) {
		const k = width / pick.width;
		return {x: pick.safe.x * k, y: pick.safe.y * k, w: pick.safe.w * k, h: pick.safe.h * k};
	}
	const mx = Math.round(width * 0.05);
	const my = Math.round(height * 0.05);
	return {x: mx, y: my, w: width - 2 * mx, h: height - 2 * my};
};

const StageContext = createContext<{format?: FormatName; safe?: Rect} | null>(null);

/** Names the target format (for its safe area) when the frame size alone is ambiguous, or sets a custom one. */
export const Stage: React.FC<{format?: FormatName; safe?: Rect; children: React.ReactNode}> = ({
	format,
	safe,
	children,
}) => <StageContext.Provider value={{format, safe}}>{children}</StageContext.Provider>;

export type StageInfo = {
	width: number;
	height: number;
	fps: number;
	durationInFrames: number; // of the enclosing Sequence when inside one
	unit: number; // 1 at a 1080 px short side
	safe: Rect;
	vertical: boolean;
	aspect: number;
	/** seconds to frames */
	sec: (seconds: number) => number;
	/** px at 1080 to px here */
	u: (px: number) => number;
};

export const useStage = (): StageInfo => {
	const {width, height, fps, durationInFrames} = useVideoConfig();
	const ctx = useContext(StageContext);
	const unit = Math.min(width, height) / 1080;
	return {
		width,
		height,
		fps,
		durationInFrames,
		unit,
		safe: ctx?.safe ?? safeAreaFor(width, height, ctx?.format),
		vertical: height > width,
		aspect: width / height,
		sec: (s) => Math.round(s * fps),
		u: (px) => px * unit,
	};
};

type Align = 'start' | 'center' | 'end';
const flex = (a: Align | 'stretch' | 'space-between' | 'space-around' | 'space-evenly') =>
	a === 'start' ? 'flex-start' : a === 'end' ? 'flex-end' : a;

/** A box exactly on the safe area, laid out as a column: put text and key graphics inside it. */
export const SafeArea: React.FC<{
	children?: React.ReactNode;
	justify?: Align | 'space-between' | 'space-around' | 'space-evenly';
	align?: Align | 'stretch';
	gap?: number; // px at 1080
	row?: boolean;
	inset?: number; // px at 1080 inside the safe area: room for glyphs that overhang their box (W, T, italics)
	style?: React.CSSProperties;
}> = ({children, justify = 'center', align = 'start', gap = 0, row = false, inset = 4, style}) => {
	const {safe, unit} = useStage();
	const i = inset * unit;
	return (
		<div
			style={{
				position: 'absolute',
				left: safe.x + i,
				top: safe.y + i,
				width: safe.w - 2 * i,
				height: safe.h - 2 * i,
				display: 'flex',
				flexDirection: row ? 'row' : 'column',
				justifyContent: flex(justify),
				alignItems: flex(align),
				gap: gap * unit,
				...style,
			}}
		>
			{children}
		</div>
	);
};

/** Authoring guides: the safe area outlined and the areas outside it shaded. Leave out of deliveries. */
export const SafeGuides: React.FC<{color?: string}> = ({color = 'rgba(255, 0, 90, 0.9)'}) => {
	const {safe, width, height, unit} = useStage();
	const shade = 'rgba(255, 0, 90, 0.12)';
	const box = (l: number, t: number, w: number, h: number, key: string) => (
		<div key={key} style={{position: 'absolute', left: l, top: t, width: w, height: h, background: shade}} />
	);
	return (
		<div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
			{box(0, 0, width, safe.y, 't')}
			{box(0, safe.y + safe.h, width, height - safe.y - safe.h, 'b')}
			{box(0, safe.y, safe.x, safe.h, 'l')}
			{box(safe.x + safe.w, safe.y, width - safe.x - safe.w, safe.h, 'r')}
			<div
				style={{
					position: 'absolute',
					left: safe.x,
					top: safe.y,
					width: safe.w,
					height: safe.h,
					border: `${2 * unit}px dashed ${color}`,
				}}
			/>
		</div>
	);
};
