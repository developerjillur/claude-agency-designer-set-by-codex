// <Choropleth>: countries coloured by a value (d3-scale classes or a smooth ramp from the theme), revealed in a
// sweep, by rank or all together, with a legend that builds with them. <Legend> also works on its own.
import {scaleLinear, scaleQuantile, scaleQuantize, scaleThreshold} from 'd3-scale';
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Rect} from '../core';
import {ramp} from '../motion';
import {mapPalette, ramp as colorRamp} from './color';
import {requireCountryKey, type CountryRef} from './countries';
import {useLife} from './Labels';
import {countryAnchor} from './plate';
import {WorldMap, type FillSpec, type WorldMapProps} from './WorldMap';

export type LegendItem = {color: string; label: string};

export type LegendProps = {
	title?: string;
	note?: string; // a source line under the swatches
	items: LegendItem[]; // swatches in order, low to high
	position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
	area?: Rect; // default the frame's safe area
	swatch?: number; // swatch width px at 1080 (default 84)
	delay?: number;
	out?: boolean;
	outAt?: number;
};

/** A row of colour swatches with labels under them, a title above and a source note below. */
export const Legend: React.FC<LegendProps> = ({title, note, items, position = 'bottom-left', area, swatch = 84, delay = 0, out = true, outAt}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps} = useStage();
	const r = area ?? safe;
	const {p, q} = useLife(delay, at30(18, fps), out, outAt);
	if (p <= 0 || q >= 1) {
		return null;
	}
	const sw = swatch * unit;
	const each = at30(3, fps);
	const bottom = position.startsWith('bottom');
	const right = position.endsWith('right');
	return (
		<div
			style={{
				position: 'absolute',
				left: right ? r.x + r.w : r.x,
				top: bottom ? r.y + r.h : r.y,
				translate: `${right ? '-100%' : '0'} ${bottom ? '-100%' : '0'}`,
				opacity: 1 - q,
				display: 'flex',
				flexDirection: 'column',
				alignItems: right ? 'flex-end' : 'flex-start',
				gap: 10 * unit,
			}}
		>
			{title ? (
				<div
					style={{
						fontFamily: /[\u0980-\u09FF]/.test(title) ? t.type.bangla : t.type.body,
						fontWeight: t.weights.strong,
						fontSize: 26 * unit,
						color: t.colors.text,
						opacity: p,
						translate: `0px ${(1 - p) * 10 * unit}px`,
						textRendering: 'geometricPrecision',
						whiteSpace: 'nowrap',
					}}
				>
					{title}
				</div>
			) : null}
			<div style={{display: 'flex', gap: 3 * unit}}>
				{items.map((it, i) => {
					const k = ramp(frame, delay + 4 + i * each, at30(12, fps), curves.outCubic);
					return (
						<div key={i} style={{width: sw, display: 'flex', flexDirection: 'column', gap: 8 * unit}}>
							<div style={{height: 14 * unit, background: it.color, borderRadius: 3 * unit, clipPath: `inset(0 ${(1 - k) * 100}% 0 0)`}} />
							<div
								style={{
									fontFamily: t.type.body,
									fontWeight: t.weights.body,
									fontSize: 18 * unit,
									color: t.colors.muted,
									fontVariantNumeric: 'tabular-nums',
									opacity: k,
									whiteSpace: 'nowrap',
									textRendering: 'geometricPrecision',
								}}
							>
								{it.label}
							</div>
						</div>
					);
				})}
			</div>
			{note ? (
				<div
					style={{
						fontFamily: t.type.body,
						fontWeight: t.weights.body,
						fontSize: 16 * unit,
						color: t.colors.muted,
						opacity: 0.85 * ramp(frame, delay + 10, at30(14, fps), curves.outCubic),
						whiteSpace: 'nowrap',
					}}
				>
					{note}
				</div>
			) : null}
		</div>
	);
};

export type ChoroplethDatum = {country: CountryRef; value: number};

export type ChoroplethProps = Omit<WorldMapProps, 'fills'> & {
	data: Record<string, number> | ChoroplethDatum[];
	scale?: 'quantize' | 'quantile' | 'threshold' | 'linear'; // default quantile (the same count in every class)
	classes?: number; // default 5
	breaks?: number[]; // threshold: the class limits
	ramp?: string[]; // class colours low to high (default: from the theme)
	reveal?: 'sweep' | 'rank' | 'together'; // sweep: west to east
	delay?: number;
	duration?: number; // frames for the whole reveal (default 1.6 s)
	format?: (v: number) => string; // legend numbers (default compact: 1.2K, 3.4M)
	legend?: false | Omit<LegendProps, 'items'>;
};

const compact = (v: number): string =>
	new Intl.NumberFormat('en-US', {notation: 'compact', maximumFractionDigits: Math.abs(v) >= 1000 || Number.isInteger(v) ? 0 : 1}).format(v);

// class labels read as limits: the first class "< b1", the others "b+"
const classLabels = (lower: readonly number[], format: (v: number) => string): string[] =>
	lower.map((b, i) => (i === 0 ? `< ${format(lower[1] ?? b)}` : `${format(b)}+`));

export const Choropleth: React.FC<ChoroplethProps> = ({
	data,
	scale = 'quantile',
	classes = 5,
	breaks,
	ramp: rampColors,
	reveal = 'sweep',
	delay = 0,
	duration,
	format = compact,
	legend,
	children,
	...map
}) => {
	const t = useTheme();
	const {fps} = useStage();
	const palette = useMemo(() => mapPalette(t, map.colors), [t, map.colors]);
	const rows = useMemo(
		() =>
			(Array.isArray(data) ? data : Object.entries(data).map(([country, value]) => ({country, value})))
				.map((d) => ({key: requireCountryKey(d.country), value: d.value}))
				.filter((d) => Number.isFinite(d.value)),
		[data],
	);

	const {colorOf, items} = useMemo(() => {
		const values = rows.map((r) => r.value);
		const lo = Math.min(...values);
		const hi = Math.max(...values);
		const n = scale === 'threshold' && breaks ? breaks.length + 1 : classes;
		const classColors = rampColors && rampColors.length === n ? rampColors : colorRamp(rampColors ?? palette.ramp, n);
		if (scale === 'linear') {
			const s = scaleLinear().domain([lo, hi]).range([0, 1]).clamp(true);
			const steps = colorRamp(rampColors ?? palette.ramp, 101);
			return {
				colorOf: (v: number) => steps[Math.round(s(v) * 100)],
				items: colorRamp(rampColors ?? palette.ramp, 5).map((c, i) => ({color: c, label: format(lo + ((hi - lo) * i) / 4)})),
			};
		}
		if (scale === 'threshold') {
			const b = breaks ?? [];
			const s = scaleThreshold<number, string>().domain(b).range(classColors);
			const labels = classLabels([lo, ...b], format);
			return {
				colorOf: (v: number) => s(v),
				items: classColors.map((c, i) => ({color: c, label: labels[i]})),
			};
		}
		if (scale === 'quantize') {
			const s = scaleQuantize<string>().domain([lo, hi]).range(classColors);
			const labels = classLabels(classColors.map((c) => s.invertExtent(c)[0]), format);
			return {
				colorOf: (v: number) => s(v),
				items: classColors.map((c, i) => ({color: c, label: labels[i]})),
			};
		}
		const s = scaleQuantile<string>().domain(values).range(classColors);
		const labels = classLabels(classColors.map((c) => s.invertExtent(c)[0] ?? lo), format);
		return {
			colorOf: (v: number) => s(v),
			items: classColors.map((c, i) => ({color: c, label: labels[i]})),
		};
	}, [rows, scale, classes, breaks, rampColors, palette.ramp, format]);

	const total = duration ?? Math.round(1.6 * fps);
	const each = at30(12, fps);
	const fills = useMemo(() => {
		const order = [...rows];
		if (reveal === 'rank') {
			order.sort((a, b) => a.value - b.value);
		} else if (reveal === 'sweep') {
			order.sort((a, b) => (countryAnchor(a.key)?.lonlat[0] ?? 0) - (countryAnchor(b.key)?.lonlat[0] ?? 0));
		}
		const out: Record<string, FillSpec> = {};
		order.forEach((r, i) => {
			const start = reveal === 'together' ? delay : delay + Math.round((i / Math.max(1, order.length - 1)) * Math.max(0, total - each));
			out[r.key] = {color: colorOf(r.value), delay: start, duration: each};
		});
		return out;
	}, [rows, reveal, delay, total, each, colorOf]);

	return (
		<WorldMap {...map} fills={fills}>
			{children}
			{legend === false ? null : <Legend {...(legend ?? {})} items={items} delay={legend && legend.delay !== undefined ? legend.delay : delay + Math.round(total * 0.35)} />}
		</WorldMap>
	);
};
