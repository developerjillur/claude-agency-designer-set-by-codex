// Drawing any SVG path on: <DrawnPath> inside your own <svg>, <DrawPath> as a sized block, <SvgLayer> as a
// full-frame SVG in frame pixels for overlays. Every subpath gets its own dash (Chrome restarts the dash pattern
// per subpath, so one dash over a multi-part icon would draw all parts at the same speed).
import {cutPath, getBoundingBox, reversePath} from '@remotion/paths';
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp} from '../motion';
import {dashFor, pathLength, subProgress, subpathsOf, type DrawMode} from './paths';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type DrawTiming = {
	progress?: number; // drive it yourself (0 to 1); otherwise delay + duration + ease
	delay?: number; // frames
	duration?: number; // frames (default 30 at 30 fps)
	ease?: Ease; // default in-out: a hand speeds up and slows down
};

/** Progress of a draw from its timing props (or the given progress), clamped 0 to 1. */
export const useDrawProgress = ({progress, delay = 0, duration, ease = curves.inOut}: DrawTiming): number => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	if (progress !== undefined) {
		return Math.min(1, Math.max(0, progress));
	}
	return ramp(frame, delay, duration ?? at30(30, fps), ease);
};

export type DrawnPathProps = DrawTiming &
	GraphicExitProps & {
		d: string;
		mode?: DrawMode; // how subpaths share the draw: 'sequence' (default), 'together', 'stagger'
		reverse?: boolean; // draw each subpath from its end
		stroke?: string; // default: the theme's text colour
		strokeWidth?: number; // in the SVG's own units
		linecap?: 'round' | 'butt' | 'square';
		linejoin?: 'round' | 'miter' | 'bevel';
		dash?: string; // a dash pattern ('12 14'): drawn by cutting the path, so the dashes stay put
		fill?: string; // fades in after the stroke has mostly drawn
		fillFrom?: number; // stroke progress at which the fill starts (default 0.75)
		fillOpacity?: number; // final fill opacity (default 1)
		opacity?: number;
		style?: React.CSSProperties;
	};

/** A path that draws itself on, for use inside an <svg>. Exit 'undraw' erases it from the start. */
export const DrawnPath: React.FC<DrawnPathProps> = ({
	d,
	mode = 'sequence',
	reverse = false,
	stroke,
	strokeWidth = 4,
	linecap = 'round',
	linejoin = 'round',
	dash,
	fill,
	fillFrom = 0.75,
	fillOpacity = 1,
	opacity = 1,
	style,
	exit = 'none',
	outDuration,
	outAt,
	...timing
}) => {
	const t = useTheme();
	const p = useDrawProgress(timing);
	const q = useGraphicExit({exit, outDuration, outAt});
	const parts = useMemo(() => {
		const list = subpathsOf(d).map((s) => (reverse ? reversePath(s) : s));
		return list.map((s) => ({d: s, len: pathLength(s)}));
	}, [d, reverse]);
	const lens = parts.map((x) => x.len);
	const each = subProgress(lens, p, mode);
	// an undraw erases from the start: the visible part is the tail
	const erased = exit === 'undraw' ? subProgress(lens, q, mode) : lens.map(() => 0);
	const fade = exit === 'fade' ? 1 - q : 1;
	const color = stroke ?? t.colors.text;
	const fillP = !fill ? 0 : p >= 1 ? 1 : Math.min(1, Math.max(0, (p - fillFrom) / Math.max(0.001, 1 - fillFrom)));
	return (
		<g opacity={opacity * fade} style={style}>
			{fill && fillP > 0 ? <path d={d} fill={fill} fillOpacity={fillOpacity * fillP * (1 - (exit === 'undraw' ? q : 0))} stroke="none" /> : null}
			{parts.map((part, i) => {
				const pi = each[i];
				const gone = erased[i];
				if (pi <= 0 || gone >= 1) {
					return null;
				}
				const common = {
					fill: 'none',
					stroke: color,
					strokeWidth,
					strokeLinecap: linecap,
					strokeLinejoin: linejoin,
				} as const;
				if (dash) {
					// dashed strokes are cut, not dashed on; an undraw of a dashed path fades instead
					const shown = cutPath(part.d, part.len * pi);
					return <path key={i} d={shown} {...common} strokeDasharray={dash} opacity={1 - gone} />;
				}
				if (gone > 0) {
					// visible from gone*len to pi*len: one dash shifted along by a negative offset (a leading
					// zero-length dash would leave a round-cap dot at the start)
					const a = part.len * gone;
					const b = part.len * pi;
					if (b - a <= 0.01) {
						return null;
					}
					return <path key={i} d={part.d} {...common} strokeDasharray={`${b - a} ${part.len * 2 + 10}`} strokeDashoffset={-a} />;
				}
				const dsh = dashFor(part.len, pi);
				return <path key={i} d={part.d} {...common} strokeDasharray={dsh.strokeDasharray} strokeDashoffset={dsh.strokeDashoffset} />;
			})}
		</g>
	);
};

export type DrawPathProps = Omit<DrawnPathProps, 'style'> & {
	viewBox?: string; // default: the path's bounding box plus room for the stroke
	width?: number; // px at 1080 (default: the viewBox width at 1:1)
	height?: number;
	style?: React.CSSProperties; // on the <svg> (position it here)
};

/** A self-contained drawing: an <svg> block sized in px at 1080 with one path drawing on. */
export const DrawPath: React.FC<DrawPathProps> = ({viewBox, width, height, style, strokeWidth = 4, d, ...rest}) => {
	const {unit} = useStage();
	const box = useMemo(() => {
		if (viewBox) {
			const [x, y, w, h] = viewBox.split(/[\s,]+/).map(Number);
			return {x, y, w, h};
		}
		if (!d.trim()) {
			return {x: 0, y: 0, w: 1, h: 1};
		}
		const b = getBoundingBox(d);
		const pad = strokeWidth * 1.5;
		return {x: b.x1 - pad, y: b.y1 - pad, w: b.width + 2 * pad, h: b.height + 2 * pad};
	}, [viewBox, d, strokeWidth]);
	const w = width ?? (height ? (height * box.w) / box.h : box.w);
	const h = height ?? (width ? (width * box.h) / box.w : box.h);
	return (
		<svg
			viewBox={`${box.x} ${box.y} ${box.w} ${box.h}`}
			width={w * unit}
			height={h * unit}
			style={{display: 'block', overflow: 'visible', ...style}}
		>
			<DrawnPath d={d} strokeWidth={strokeWidth} {...rest} />
		</svg>
	);
};

/**
 * A full-frame SVG whose coordinates are frame pixels (0 to width, 0 to height), for arrows, routes and marks laid
 * over a scene. Put DrawnPath, ArrowPath, PathFollow, MorphPath and HandStroke inside it.
 */
export const SvgLayer: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => {
	const {width, height} = useStage();
	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			width={width}
			height={height}
			style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none', ...style}}
		>
			{children}
		</svg>
	);
};
