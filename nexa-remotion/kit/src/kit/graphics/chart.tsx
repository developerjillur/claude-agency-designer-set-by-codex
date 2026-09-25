// What every chart shares: its size (explicit, from a <ChartFrame>, or the safe area), an estimate of text width
// for layout (charts never measure the DOM, so every frame lays out the same), HTML labels placed in chart
// coordinates, and <ChartFrame>: a titled chart scene inside the safe area with a source line.
import React, {createContext, useContext, useRef} from 'react';
import {at30, useStage, useTheme} from '../core';
import {Animate} from '../motion';
import {useMeasuredSize} from './measure';
import {useGraphicExit, type GraphicExitProps} from './timing';

export type ChartBox = {width: number; height: number; delay: number};

const ChartBoxContext = createContext<ChartBox | null>(null);

/** The size a chart should take (px at 1080): explicit props, then a ChartFrame's area, then the safe area. */
export const useChartBox = (width?: number, height?: number, delay?: number): ChartBox => {
	const ctx = useContext(ChartBoxContext);
	const {safe, unit} = useStage();
	const w = width ?? ctx?.width ?? safe.w / unit;
	const h = height ?? ctx?.height ?? Math.round((safe.h / unit) * 0.74);
	return {width: w, height: h, delay: delay ?? ctx?.delay ?? 0};
};

const BANGLA = /[ঀ-৿]/;

/**
 * About how wide `text` sets at `size` px (glyph classes averaged for common sans faces, a little generous). Used
 * for layout only: label columns, margins, collisions.
 */
export const estimateLabelWidth = (text: string, size: number, bold = false): number => {
	let w = 0;
	for (const ch of text) {
		if (ch === ' ') {
			w += 0.28;
		} else if (/[0-9]/.test(ch)) {
			w += 0.6;
		} else if (/[.,:;'!|]/.test(ch)) {
			w += 0.3;
		} else if (/[A-Z%$€£৳]/.test(ch)) {
			w += 0.68;
		} else if (/[mwMW]/.test(ch)) {
			w += 0.85;
		} else if (BANGLA.test(ch)) {
			w += 0.56;
		} else {
			w += 0.55;
		}
	}
	return w * size * (bold ? 1.07 : 1);
};

/** Words of `text` greedily broken into at most `maxLines` lines no wider than `width` (estimated). */
export const breakLabelLines = (text: string, size: number, width: number, maxLines = 2, bold = false): string[] => {
	const words = text.split(/\s+/).filter(Boolean);
	const lines: string[] = [];
	let cur = '';
	for (const word of words) {
		const next = cur ? `${cur} ${word}` : word;
		if (cur && estimateLabelWidth(next, size, bold) > width && lines.length < maxLines - 1) {
			lines.push(cur);
			cur = word;
		} else {
			cur = next;
		}
	}
	if (cur) {
		lines.push(cur);
	}
	return lines;
};

export type LabelAnchor = 'center' | 'left' | 'right' | 'top' | 'bottom' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

const ANCHOR: Record<LabelAnchor, string> = {
	center: '-50% -50%',
	left: '0 -50%',
	right: '-100% -50%',
	top: '-50% 0',
	bottom: '-50% -100%',
	'top-left': '0 0',
	'top-right': '-100% 0',
	'bottom-left': '0 -100%',
	'bottom-right': '-100% -100%',
};

/** An HTML label placed at chart coordinates (px at 1080) with an anchor, for use inside a chart root. */
export const ChartLabel: React.FC<{
	x: number;
	y: number;
	anchor?: LabelAnchor;
	children: React.ReactNode;
	style?: React.CSSProperties;
	maxWidth?: number; // px at 1080: wraps inside it
}> = ({x, y, anchor = 'center', children, style, maxWidth}) => {
	const {unit} = useStage();
	return (
		<div
			style={{
				position: 'absolute',
				left: x * unit,
				top: y * unit,
				translate: ANCHOR[anchor],
				whiteSpace: maxWidth ? 'normal' : 'nowrap',
				width: maxWidth ? maxWidth * unit : undefined,
				textRendering: 'geometricPrecision',
				...style,
			}}
		>
			{children}
		</div>
	);
};

/** The root box of a chart: sized in px at 1080, with an SVG in the same coordinates behind the HTML labels. */
export const ChartRoot: React.FC<{
	width: number;
	height: number;
	svg: React.ReactNode;
	children?: React.ReactNode;
	style?: React.CSSProperties;
}> = ({width, height, svg, children, style}) => {
	const {unit} = useStage();
	return (
		<div style={{position: 'relative', width: width * unit, height: height * unit, flexShrink: 0, ...style}}>
			<svg
				viewBox={`0 0 ${width} ${height}`}
				width={width * unit}
				height={height * unit}
				style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}
			>
				{svg}
			</svg>
			{children}
		</div>
	);
};

/** Type sizes of a chart's text roles (px at 1080) and the tabular-number style. */
export const useChartType = () => {
	const t = useTheme();
	const numeric: React.CSSProperties = {fontVariantNumeric: 'tabular-nums'};
	return {
		tick: {fontFamily: t.type.body, fontWeight: t.weights.body, color: t.colors.muted, ...numeric} as React.CSSProperties,
		label: {fontFamily: t.type.body, fontWeight: t.weights.body, color: t.colors.text} as React.CSSProperties,
		value: {fontFamily: t.type.body, fontWeight: t.weights.strong, color: t.colors.text, ...numeric} as React.CSSProperties,
	};
};

export type ChartFrameProps = GraphicExitProps & {
	title?: React.ReactNode;
	subtitle?: React.ReactNode;
	source?: React.ReactNode; // 'Source: ...' line at the bottom (keep numbers honest: say where they come from)
	align?: 'left' | 'center';
	titleSize?: number; // px at 1080 (default 64, 58 in 9:16)
	titleLines?: 1 | 2; // lines to reserve for the title (default: estimated)
	delay?: number; // the title's entrance; the chart starts about 10 frames later
	children: React.ReactNode;
};

/**
 * A chart scene inside the safe area: title and subtitle at the top, the chart in the space left (charts inside
 * read their size from this frame), and a source line at the bottom. The header is measured once the fonts load,
 * so the chart gets exactly the room left over.
 */
export const ChartFrame: React.FC<ChartFrameProps> = ({
	title,
	subtitle,
	source,
	align = 'left',
	titleSize,
	titleLines,
	delay = 0,
	children,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const t = useTheme();
	const {safe, unit, fps, vertical} = useStage();
	const q = useGraphicExit({exit, outDuration, outAt});
	const headRef = useRef<HTMLDivElement>(null);
	const measured = useMeasuredSize(headRef, 'graphics: measuring a chart title');
	const W = safe.w / unit;
	const H = safe.h / unit;
	const ts = titleSize ?? (vertical ? 58 : 64);
	const ss = Math.round(ts * 0.5);
	const titleText = typeof title === 'string' ? title : '';
	const lines = titleLines ?? (title ? (estimateLabelWidth(titleText, ts, true) * (1 + Math.min(0, t.tracking.display)) > W * 0.98 ? 2 : 1) : 0);
	const estimated = (title ? ts * 1.08 * lines : 0) + (subtitle ? ss * 1.35 + 10 : 0);
	const headH = measured && measured.h > 0 ? measured.h / unit : estimated;
	const footH = source ? 22 * 1.3 + 24 : 0;
	const gap = title || subtitle ? 36 : 0;
	const chartH = Math.max(120, H - headH - gap - footH);
	return (
		<div
			style={{
				position: 'absolute',
				left: safe.x,
				top: safe.y,
				width: safe.w,
				height: safe.h,
				opacity: exit === 'fade' ? 1 - q : 1,
				translate: exit === 'fade' ? `0 ${-10 * unit * q}px` : undefined,
			}}
		>
			<div ref={headRef} style={{position: 'absolute', left: 0, top: 0, width: '100%', display: 'flex', flexDirection: 'column', gap: 10 * unit}}>
				{title ? (
					<Animate delay={delay}>
						<div
							style={{
								fontFamily: t.type.display,
								fontWeight: t.weights.display,
								fontSize: ts * unit,
								lineHeight: 1.08,
								letterSpacing: `${t.tracking.display}em`,
								textTransform: t.caps ? 'uppercase' : 'none',
								color: t.colors.text,
								textAlign: align,
								textWrap: 'balance',
							}}
						>
							{title}
						</div>
					</Animate>
				) : null}
				{subtitle ? (
					<Animate delay={delay + at30(5, fps)}>
						<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: ss * unit, lineHeight: 1.35, color: t.colors.muted, textAlign: align}}>{subtitle}</div>
					</Animate>
				) : null}
			</div>
			<div style={{position: 'absolute', left: 0, top: (headH + gap) * unit, width: W * unit, height: chartH * unit}}>
				<ChartBoxContext.Provider value={{width: W, height: chartH, delay: delay + at30(10, fps)}}>{children}</ChartBoxContext.Provider>
			</div>
			{source ? (
				<Animate in="fade" delay={delay + at30(20, fps)} style={{position: 'absolute', left: 0, bottom: 0, width: '100%'}}>
					<div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: 22 * unit, lineHeight: 1.3, color: t.colors.muted, textAlign: align}}>{source}</div>
				</Animate>
			) : null}
		</div>
	);
};
