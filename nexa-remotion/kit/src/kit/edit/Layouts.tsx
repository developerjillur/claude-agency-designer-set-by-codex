// Frames within the frame: split screens, picture in picture, a two-source layout that morphs between full,
// split and PiP (the Recorder's interpolated-layout idea), and letterbox bars. Children are usually <Clip>s,
// which fill whatever box they are given (objectFit 'cover').
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease, type Rect} from '../core';
import {ramp, springAt} from '../motion';

// ------------------------------------------------------------------ shared pieces

/** A small name chip for panes and insets: theme surface and text, readable over any footage. */
export const LayoutLabel: React.FC<{text: string; style?: React.CSSProperties}> = ({text, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div
			style={{
				position: 'absolute',
				padding: `${10 * unit}px ${18 * unit}px`,
				borderRadius: Math.min(t.radius, 14) * unit,
				background: t.colors.surface,
				color: t.colors.text,
				fontFamily: t.type.body,
				fontWeight: t.weights.strong,
				fontSize: 26 * unit,
				lineHeight: 1.15,
				whiteSpace: 'nowrap',
				boxShadow: `0 ${6 * unit}px ${18 * unit}px rgba(0,0,0,0.18)`,
				...style,
			}}
		>
			{text}
		</div>
	);
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// ------------------------------------------------------------------ split screen

export type SplitScreenProps = {
	/** One pane per child (2 to 4 read well). */
	children: React.ReactNode;
	/** 'auto': side by side in landscape, stacked in portrait. */
	direction?: 'auto' | 'row' | 'column';
	/** Relative pane sizes, default equal: [2, 1] gives the first pane two thirds. */
	sizes?: readonly number[];
	/** Gutter between panes in px at 1080; the ground shows through. 0 = a hard split. */
	gap?: number;
	/** An accent line on each seam, px at 1080 (0 = none). */
	divider?: number;
	dividerColor?: string;
	/** A chip per pane (null for none), placed inside the safe area. */
	labels?: readonly (string | null | undefined)[];
	/** Where the chips sit in their panes. */
	labelPosition?: 'top' | 'bottom';
	/** How panes arrive: slide in from their own sides, wipe along the split, or cut in. */
	enter?: 'slide' | 'wipe' | 'none';
	delay?: number;
	duration?: number;
	stagger?: number;
	ease?: Ease;
	background?: string;
	style?: React.CSSProperties;
};

/** The pane rectangles of a split, in px. */
export const splitRects = (
	n: number,
	o: {width: number; height: number; direction: 'row' | 'column'; sizes?: readonly number[]; gap?: number},
): Rect[] => {
	const {width, height, direction, gap = 0} = o;
	const sizes = Array.from({length: n}, (_, i) => Math.max(0.0001, o.sizes?.[i] ?? 1));
	const total = sizes.reduce((a, b) => a + b, 0);
	const main = (direction === 'row' ? width : height) - gap * (n - 1);
	const rects: Rect[] = [];
	let at = 0;
	for (let i = 0; i < n; i++) {
		const len = (main * sizes[i]) / total;
		rects.push(direction === 'row' ? {x: at, y: 0, w: len, h: height} : {x: 0, y: at, w: width, h: len});
		at += len + gap;
	}
	return rects;
};

export const SplitScreen: React.FC<SplitScreenProps> = ({
	children,
	direction = 'auto',
	sizes,
	gap = 0,
	divider = 0,
	dividerColor,
	labels,
	labelPosition = 'bottom',
	enter = 'slide',
	delay = 0,
	duration,
	stagger,
	ease = curves.out,
	background,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, unit, fps, safe, vertical} = useStage();
	const items = React.Children.toArray(children);
	const n = items.length;
	const dir = direction === 'auto' ? (vertical ? 'column' : 'row') : direction;
	const g = gap * unit;
	const rects = splitRects(n, {width, height, direction: dir, sizes, gap: g});
	const dur = duration ?? at30(24, fps);
	const each = stagger ?? at30(5, fps);
	return (
		<AbsoluteFill style={{background: background ?? t.colors.bg, overflow: 'hidden', ...style}}>
			{items.map((child, i) => {
				const r = rects[i];
				const p = enter === 'none' ? 1 : ramp(frame, delay + i * each, dur, ease);
				let translate = '0px 0px';
				let clipPath: string | undefined;
				if (enter === 'slide') {
					const first = i === 0;
					const last = i === n - 1 && n > 1;
					if (dir === 'row') {
						const dx = first ? -(r.x + r.w) : last ? width - r.x : 0;
						const dy = !first && !last ? height : 0;
						translate = `${dx * (1 - p)}px ${dy * (1 - p)}px`;
					} else {
						const dy = first ? -(r.y + r.h) : last ? height - r.y : 0;
						const dx = !first && !last ? width : 0;
						translate = `${dx * (1 - p)}px ${dy * (1 - p)}px`;
					}
				} else if (enter === 'wipe') {
					const hide = (1 - p) * 100;
					clipPath = dir === 'row' ? `inset(0 ${hide}% 0 0)` : `inset(0 0 ${hide}% 0)`;
				}
				const label = labels?.[i];
				// the chip sits in the pane's lower (or upper) left corner, pushed inside the safe area
				const lx = Math.max(r.x + 28 * unit, safe.x);
				const top = labelPosition === 'top';
				const ly = top ? Math.max(r.y + 28 * unit, safe.y) : Math.min(r.y + r.h - 28 * unit, safe.y + safe.h);
				const lp = ramp(frame, delay + i * each + dur * 0.6, at30(14, fps), curves.out);
				return (
					<React.Fragment key={i}>
						<div style={{position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, overflow: 'hidden', translate, clipPath}}>
							{child}
						</div>
						{label ? (
							<LayoutLabel
								text={label}
								style={{left: lx, top: ly, translate: top ? `0px ${(1 - lp) * 14 * unit}px` : `0px calc(-100% + ${(1 - lp) * 14 * unit}px)`, opacity: lp}}
							/>
						) : null}
					</React.Fragment>
				);
			})}
			{divider > 0
				? rects.slice(1).map((r, i) => {
						const p = enter === 'none' ? 1 : ramp(frame, delay + dur * 0.5, dur, curves.inOut);
						const thick = divider * unit;
						const seam: React.CSSProperties =
							dir === 'row'
								? {left: r.x - g / 2 - thick / 2, top: 0, width: thick, height: height * p}
								: {top: r.y - g / 2 - thick / 2, left: 0, height: thick, width: width * p};
						return <div key={i} style={{position: 'absolute', background: dividerColor ?? t.colors.accent, ...seam}} />;
					})
				: null}
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ picture in picture

export type PipCorner = 'bottomRight' | 'bottomLeft' | 'topRight' | 'topLeft';
export type PipShape = 'rect' | 'round' | 'circle';

export type PipOptions = {
	corner?: PipCorner;
	shape?: PipShape;
	/** Width in px at 1080 (default 520 for rect and round, 300 for a circle). */
	width?: number;
	/** Width over height for rect and round (default 16 / 9). */
	aspect?: number;
	/** Distance from the safe-area edges, px at 1080. */
	margin?: number;
};

/** The box and corner radius of an inset, in px, inside the safe area. */
export const pipRect = (
	o: PipOptions,
	stage: {safe: Rect; unit: number},
	themeRadius = 20,
): Rect & {radius: number} => {
	const {corner = 'bottomRight', shape = 'round', margin = 0} = o;
	const {safe, unit} = stage;
	const w = (o.width ?? (shape === 'circle' ? 300 : 520)) * unit;
	const h = shape === 'circle' ? w : w / (o.aspect ?? 16 / 9);
	const m = margin * unit;
	const right = corner === 'bottomRight' || corner === 'topRight';
	const bottom = corner === 'bottomRight' || corner === 'bottomLeft';
	const x = right ? safe.x + safe.w - w - m : safe.x + m;
	const y = bottom ? safe.y + safe.h - h - m : safe.y + m;
	const radius = shape === 'circle' ? w / 2 : shape === 'round' ? Math.max(18, themeRadius) * unit : Math.min(themeRadius, 10) * unit;
	return {x, y, w, h, radius};
};

export type PictureInPictureProps = PipOptions & {
	/** The inset content, usually a <Clip>. */
	children: React.ReactNode;
	/** A ring around the inset, px at 1080 (0 = none). */
	border?: number;
	borderColor?: string;
	/** Drop shadow strength, 0 to 1. */
	shadow?: number;
	/** A name chip on the inset's lower edge. */
	label?: string;
	/** Push in on the content (1.4 = 40 % closer): a webcam bubble framed on the face. */
	zoom?: number;
	/** The point of the content to centre when zoomed, as fractions [x, y] of the inset (edges never show). */
	focus?: readonly [number, number];
	enter?: 'pop' | 'slide' | 'fade' | 'none';
	/** The exit plays at the end of the enclosing Sequence (none by default: an inset usually cuts with its scene). */
	exit?: 'pop' | 'slide' | 'fade' | 'none';
	delay?: number;
	duration?: number;
	exitDuration?: number;
	style?: React.CSSProperties;
};

export const PictureInPicture: React.FC<PictureInPictureProps> = ({
	children,
	border = 6,
	borderColor,
	shadow = 1,
	label,
	zoom = 1,
	focus = [0.5, 0.5],
	enter = 'pop',
	exit = 'none',
	delay = 0,
	duration,
	exitDuration,
	style,
	...pip
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const stage = useStage();
	const {unit, fps, width, durationInFrames} = stage;
	const r = pipRect(pip, stage, t.radius);
	const corner = pip.corner ?? 'bottomRight';
	const right = corner === 'bottomRight' || corner === 'topRight';
	const bottom = corner === 'bottomRight' || corner === 'bottomLeft';
	const inDur = duration ?? at30(enter === 'slide' ? 20 : 16, fps);
	const outDur = exitDuration ?? at30(12, fps);
	const exitStart = durationInFrames - 1 - outDur;
	const motion = (kind: 'pop' | 'slide' | 'fade' | 'none', p: number, leaving: boolean) => {
		// p: 1 = in place, 0 = gone
		if (kind === 'none') {
			return {scale: 1, x: 0, opacity: 1};
		}
		if (kind === 'slide') {
			const off = right ? width - r.x + 40 * unit : -(r.x + r.w + 40 * unit);
			return {scale: 1, x: off * (1 - p), opacity: 1};
		}
		if (kind === 'fade') {
			return {scale: 0.96 + 0.04 * p, x: 0, opacity: p};
		}
		return {scale: leaving ? 0.7 + 0.3 * p : 0.55 + 0.45 * p, x: 0, opacity: Math.min(1, p * (leaving ? 1.4 : 2.2))};
	};
	const pIn =
		enter === 'pop'
			? springAt(frame, fps, {delay, config: 'settle', durationInFrames: inDur})
			: ramp(frame, delay, inDur, enter === 'slide' ? curves.out : curves.outCubic);
	const pOut = exit === 'none' || !Number.isFinite(exitStart) ? 1 : 1 - ramp(frame, exitStart, outDur, curves.in);
	const a = motion(enter, pIn, false);
	const b = motion(exit, pOut, true);
	const ring = border > 0 ? `0 0 0 ${border * unit}px ${borderColor ?? (t.dark ? t.colors.text : t.colors.surface)}, ` : '';
	const drop = shadow > 0 ? `0 ${18 * unit}px ${50 * unit}px rgba(0,0,0,${0.38 * shadow})` : '0 0 0 transparent';
	const lp = ramp(frame, delay + inDur * 0.7, at30(12, fps), curves.out) * (exit === 'none' ? 1 : pOut);
	// zoom: move the focus point to the centre, but never past an edge of the content
	const z = Math.max(1, zoom);
	const zx = Math.min(0, Math.max(r.w - z * r.w, r.w / 2 - z * focus[0] * r.w));
	const zy = Math.min(0, Math.max(r.h - z * r.h, r.h / 2 - z * focus[1] * r.h));
	return (
		<div
			style={{
				position: 'absolute',
				left: r.x,
				top: r.y,
				width: r.w,
				height: r.h,
				translate: `${a.x + b.x}px 0px`,
				scale: `${a.scale * b.scale}`,
				transformOrigin: `${right ? '100%' : '0%'} ${bottom ? '100%' : '0%'}`,
				opacity: a.opacity * b.opacity,
				...style,
			}}
		>
			<div style={{position: 'absolute', inset: 0, borderRadius: r.radius, overflow: 'hidden', boxShadow: ring + drop}}>
				<div style={{position: 'absolute', inset: 0, transformOrigin: '0 0', scale: z !== 1 ? `${z}` : undefined, translate: z !== 1 ? `${zx}px ${zy}px` : undefined}}>{children}</div>
			</div>
			{label ? (
				<LayoutLabel
					text={label}
					style={{left: '50%', top: '100%', translate: `-50% ${-50 + (1 - lp) * 30}%`, opacity: lp, fontSize: 22 * unit}}
				/>
			) : null}
		</div>
	);
};

// ------------------------------------------------------------------ two sources, layouts that morph

/** 'a' or 'b' full frame; 'a+b' A full with B inset; 'b+a' B full with A inset; 'split' side by side. */
export type Shot = 'a' | 'b' | 'a+b' | 'b+a' | 'split';

type LayerBox = {x: number; y: number; w: number; h: number; r: number; o: number; ring: number};

export type LayoutSwitchProps = {
	a: React.ReactNode;
	b: React.ReactNode;
	/** Shot changes: [{at: 0, shot: 'a'}, {at: 90, shot: 'b+a'}, {at: 180, shot: 'split'}]. */
	keys: readonly {at: number; shot: Shot}[];
	/** Frames each change takes (0 = a cut). */
	transition?: number;
	ease?: Ease;
	pip?: PipOptions;
	/** Gutter of the split, px at 1080. */
	gap?: number;
	border?: number;
	borderColor?: string;
	background?: string;
	style?: React.CSSProperties;
};

export const LayoutSwitch: React.FC<LayoutSwitchProps> = ({
	a,
	b,
	keys,
	transition,
	ease = curves.inOut,
	pip = {},
	gap = 16,
	border = 6,
	borderColor,
	background,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const stage = useStage();
	const {width, height, unit, fps, vertical} = stage;
	const dur = transition ?? at30(20, fps);
	const inset = pipRect(pip, stage, t.radius);
	const full: LayerBox = {x: 0, y: 0, w: width, h: height, r: 0, o: 1, ring: 0};
	const small: LayerBox = {x: inset.x, y: inset.y, w: inset.w, h: inset.h, r: inset.radius, o: 1, ring: 1};
	const gone: LayerBox = {...small, x: small.x + small.w * 0.15, y: small.y + small.h * 0.15, w: small.w * 0.7, h: small.h * 0.7, o: 0};
	const halves = splitRects(2, {width, height, direction: vertical ? 'column' : 'row', gap: gap * unit}).map(
		(q): LayerBox => ({x: q.x, y: q.y, w: q.w, h: q.h, r: 0, o: 1, ring: 0}),
	);
	const boxes = (s: Shot): [LayerBox, LayerBox] => {
		switch (s) {
			case 'b':
				return [gone, full];
			case 'a+b':
				return [full, small];
			case 'b+a':
				return [small, full];
			case 'split':
				return [halves[0], halves[1]];
			case 'a':
			default:
				return [full, gone];
		}
	};
	const sorted = [...keys].sort((x, y) => x.at - y.at);
	let cur = 0;
	for (let i = 0; i < sorted.length; i++) {
		if (sorted[i].at <= frame) {
			cur = i;
		}
	}
	const now = sorted[cur]?.shot ?? 'a';
	const before = cur > 0 ? sorted[cur - 1].shot : now;
	const p = dur > 0 && cur > 0 ? ramp(frame, sorted[cur].at, dur, ease) : 1;
	const [a0, b0] = boxes(before);
	const [a1, b1] = boxes(now);
	const mix = (x: LayerBox, y: LayerBox): LayerBox => ({
		x: lerp(x.x, y.x, p),
		y: lerp(x.y, y.y, p),
		w: lerp(x.w, y.w, p),
		h: lerp(x.h, y.h, p),
		r: lerp(x.r, y.r, p),
		o: lerp(x.o, y.o, p),
		ring: lerp(x.ring, y.ring, p),
	});
	const A = mix(a0, a1);
	const B = mix(b0, b1);
	const bOnTop = B.w * B.h <= A.w * A.h;
	const layer = (box: LayerBox, node: React.ReactNode, z: number) => (
		<div
			style={{
				position: 'absolute',
				left: box.x,
				top: box.y,
				width: box.w,
				height: box.h,
				borderRadius: box.r,
				overflow: 'hidden',
				opacity: box.o,
				zIndex: z,
				boxShadow:
					box.ring > 0.01
						? `0 0 0 ${border * unit * box.ring}px ${borderColor ?? (t.dark ? t.colors.text : t.colors.surface)}, 0 ${18 * unit}px ${50 * unit}px rgba(0,0,0,${0.38 * box.ring})`
						: undefined,
			}}
		>
			{node}
		</div>
	);
	return (
		<AbsoluteFill style={{background: background ?? t.colors.bg, overflow: 'hidden', isolation: 'isolate', ...style}}>
			{layer(A, a, bOnTop ? 1 : 2)}
			{layer(B, b, bOnTop ? 2 : 1)}
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ letterbox

export type LetterboxProps = {
	/** The picture aspect left between the bars: 2.39 scope, 2 univisium, 1.85 flat, 4 / 3 for pillar bars. */
	aspect?: number;
	color?: string;
	/** Frames before the bars move in, and how long they take (0 = already in). */
	delay?: number;
	duration?: number;
	/** Pull the bars back out, ending on the last frame of the Sequence. */
	out?: boolean;
	ease?: Ease;
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** Bar thickness in px for an aspect: [top/bottom, left/right] (one of them is 0). */
export const letterboxBars = (width: number, height: number, aspect: number): [number, number] => {
	if (width / height < aspect) {
		return [Math.max(0, (height - width / aspect) / 2), 0];
	}
	return [0, Math.max(0, (width - height * aspect) / 2)];
};

export const Letterbox: React.FC<LetterboxProps> = ({
	aspect = 2.39,
	color = '#000000',
	delay = 0,
	duration,
	out = false,
	ease = curves.inOut,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const {width, height, fps, durationInFrames} = useStage();
	const dur = duration ?? at30(24, fps);
	const pIn = dur > 0 ? ramp(frame, delay, dur, ease) : 1;
	const pOut = out && Number.isFinite(durationInFrames) ? 1 - ramp(frame, durationInFrames - 1 - dur, dur, ease) : 1;
	const p = Math.min(pIn, pOut);
	const [tb, lr] = letterboxBars(width, height, aspect);
	return (
		<AbsoluteFill style={style}>
			{children}
			{tb > 0 ? (
				<>
					<div style={{position: 'absolute', left: 0, top: 0, width, height: tb * p, background: color}} />
					<div style={{position: 'absolute', left: 0, bottom: 0, width, height: tb * p, background: color}} />
				</>
			) : null}
			{lr > 0 ? (
				<>
					<div style={{position: 'absolute', left: 0, top: 0, height, width: lr * p, background: color}} />
					<div style={{position: 'absolute', right: 0, top: 0, height, width: lr * p, background: color}} />
				</>
			) : null}
		</AbsoluteFill>
	);
};
