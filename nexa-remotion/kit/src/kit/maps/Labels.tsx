// Country names on a map: placed at the pole of inaccessibility (the point deepest inside the country), with a
// halo so they read over borders, and a callout with a leader line when the country is too small to hold its name.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Rect, type Theme} from '../core';
import {ramp} from '../motion';
import {allCountries, countryName, requireCountryKey, type CountryRef} from './countries';
import {useMap, type MapApi} from './context';
import {countryAnchor} from './plate';

const BANGLA = /[\u0980-\u09FF]/;

export type LabelStyle = 'caps' | 'title' | 'plain';
export type Side = 'auto' | 'left' | 'right' | 'top' | 'bottom';

/** Rough text width (px) for layout decisions; real text is never measured, so this stays deterministic. */
export const estimateWidth = (text: string, fontSize: number, caps: boolean): number => {
	let w = 0;
	for (const ch of text) {
		w += BANGLA.test(ch) ? 0.52 : ch === ' ' ? 0.3 : caps ? 0.7 : /[A-Z]/.test(ch) ? 0.66 : 0.54;
	}
	return w * fontSize + (caps ? text.length * fontSize * 0.08 : 0);
};

type TextSpec = {fontFamily: string; fontWeight: number; fontSize: number; letterSpacing: string; textTransform: 'uppercase' | 'none'};

const textSpec = (t: Theme, style: LabelStyle, unit: number, size: number | undefined, text: string): TextSpec => {
	const bangla = BANGLA.test(text);
	if (style === 'title') {
		return {
			fontFamily: bangla ? t.type.bangla : t.type.display,
			fontWeight: t.weights.display,
			fontSize: (size ?? 40) * unit,
			letterSpacing: bangla ? '0em' : `${t.tracking.display}em`,
			textTransform: t.caps && !bangla ? 'uppercase' : 'none',
		};
	}
	if (style === 'plain') {
		return {fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: (size ?? 22) * unit, letterSpacing: '0em', textTransform: 'none'};
	}
	return {
		fontFamily: t.type.body,
		fontWeight: t.weights.strong,
		fontSize: (size ?? 17) * unit,
		letterSpacing: bangla ? '0em' : `${Math.max(0.06, t.tracking.caps)}em`,
		textTransform: bangla ? 'none' : 'uppercase',
	};
};

/** Enter, hold and exit progress for a temporary map element (1 = fully shown). */
export const useLife = (delay: number, inFrames: number, out: boolean, outAt?: number, outFrames?: number): {p: number; q: number} => {
	const frame = useCurrentFrame();
	const {durationInFrames, fps} = useStage();
	const t = useTheme();
	const outDur = outFrames ?? at30(t.motion.exitFrames, fps);
	const p = ramp(frame, delay, inFrames, curves.out);
	const exitStart = outAt ?? durationInFrames - 1 - outDur;
	const q = out && Number.isFinite(exitStart) ? ramp(frame, exitStart, outDur, curves.in) : 0;
	return {p, q};
};

/** Keeps a box (left, top, w, h) inside a rect by shifting it. */
export const clampInto = (x: number, y: number, w: number, h: number, r: Rect): [number, number] => [
	Math.min(Math.max(x, r.x), Math.max(r.x, r.x + r.w - w)),
	Math.min(Math.max(y, r.y), Math.max(r.y, r.y + r.h - h)),
];

export type TagProps = {
	x: number; // the point the tag belongs to, box px
	y: number;
	title: string;
	sub?: string;
	side: Exclude<Side, 'auto'>;
	gap: number; // px between the point and the tag
	p: number; // entrance 0 to 1
	q: number; // exit 0 to 1
	map: MapApi;
	size?: number; // title size, px at 1080
	accent?: string; // a small bar in this colour on the leading edge
};

const OPPOSITE: Record<Exclude<Side, 'auto'>, Exclude<Side, 'auto'>> = {left: 'right', right: 'left', top: 'bottom', bottom: 'top'};

/** A label pill next to a point (pins, route stops, callouts). */
export const Tag: React.FC<TagProps> = ({x, y, title, sub, side: wanted, gap, p, q, map, size = 26, accent}) => {
	const t = useTheme();
	const {unit, palette} = map;
	const fs = size * unit;
	const subFs = Math.round(size * 0.72) * unit;
	const padX = 16 * unit;
	const padY = 10 * unit;
	const w = Math.max(estimateWidth(title, fs, false), sub ? estimateWidth(sub, subFs, false) : 0) + 2 * padX + (accent ? 10 * unit : 0);
	const h = fs * 1.2 + (sub ? subFs * 1.25 : 0) + 2 * padY;
	const place = (sd: Exclude<Side, 'auto'>): [number, number, number] => {
		const l0 = sd === 'right' ? x + gap : sd === 'left' ? x - gap - w : x - w / 2;
		const t0 = sd === 'top' ? y - gap - h : sd === 'bottom' ? y + gap : y - h / 2;
		const [l1, t1] = clampInto(l0, t0, w, h, map.safe);
		return [l1, t1, Math.abs(l1 - l0) + Math.abs(t1 - t0)];
	};
	// when the safe area pushes the tag back over its own point, it goes to the other side instead
	let side = wanted;
	let [left, top, shift] = place(side);
	if (shift > gap * 0.6) {
		const [l2, t2, s2] = place(OPPOSITE[side]);
		if (s2 < shift) {
			side = OPPOSITE[side];
			left = l2;
			top = t2;
		}
	}
	// a tag belongs to its point: when the camera leaves the point behind, the tag goes too. A tag the safe area
	// pushes off its point fades out over the next 60 px (it used to stay pinned to the edge while its point slid
	// away, then vanish in place): it never slides along the edge on its own
	const m = 40 * unit;
	const onFrame = Number.isFinite(x) && x > -m && x < map.width + m && y > -m && y < map.height + m;
	const loose = Math.max(0, Math.min(1, (shift - gap * 0.6) / (60 * unit)));
	const vis = onFrame ? p * (1 - q) * (1 - loose) : 0;
	if (vis <= 0) {
		return null;
	}
	const dx = side === 'right' ? -10 : side === 'left' ? 10 : 0;
	const dy = side === 'top' ? 10 : side === 'bottom' ? -10 : 0;
	const move = (1 - p) + q * 0.6;
	const radius = Math.min(t.radius, 14) * unit;
	return (
		<div
			style={{
				position: 'absolute',
				left,
				top,
				minWidth: w,
				height: h,
				boxSizing: 'border-box',
				padding: `${padY}px ${padX}px`,
				paddingLeft: accent ? padX + 10 * unit : padX,
				borderRadius: radius,
				background: palette.tagBg,
				boxShadow: `0 ${6 * unit}px ${18 * unit}px rgba(0, 0, 0, ${palette.dark ? 0.45 : 0.16}), 0 0 0 ${unit}px rgba(0, 0, 0, ${palette.dark ? 0.35 : 0.08})`,
				opacity: vis,
				translate: `${dx * move * unit}px ${dy * move * unit}px`,
				scale: `${0.96 + 0.04 * p}`,
				transformOrigin: side === 'right' ? '0% 50%' : side === 'left' ? '100% 50%' : side === 'top' ? '50% 100%' : '50% 0%',
				display: 'flex',
				flexDirection: 'column',
				justifyContent: 'center',
				whiteSpace: 'nowrap',
				overflow: 'hidden',
			}}
		>
			{accent ? (
				<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 5 * unit, background: accent}} />
			) : null}
			<div
				style={{
					fontFamily: BANGLA.test(title) ? t.type.bangla : t.type.body,
					fontWeight: t.weights.strong,
					fontSize: fs,
					lineHeight: 1.2,
					color: palette.tagText,
					textRendering: 'geometricPrecision',
				}}
			>
				{title}
			</div>
			{sub ? (
				<div
					style={{
						fontFamily: BANGLA.test(sub) ? t.type.bangla : t.type.body,
						fontWeight: t.weights.body,
						fontSize: subFs,
						lineHeight: 1.25,
						color: palette.tagMuted,
						textRendering: 'geometricPrecision',
					}}
				>
					{sub}
				</div>
			) : null}
		</div>
	);
};

export type ScreenBox = {x0: number; y0: number; x1: number; y1: number};

/** The side with room for a tag of width `wantW` next to a point (or past a box) inside the safe area. */
export const bestSide = (x: number, y: number, safe: Rect, wantW: number, box?: ScreenBox | null): Exclude<Side, 'auto'> => {
	const right = safe.x + safe.w - Math.max(x, box?.x1 ?? x);
	const left = Math.min(x, box?.x0 ?? x) - safe.x;
	if (right >= wantW + 20) {
		return 'right';
	}
	if (left >= wantW + 20) {
		return 'left';
	}
	return y - safe.y > safe.y + safe.h - y ? 'top' : 'bottom';
};

export type CountryLabelProps = {
	country: CountryRef;
	text?: string; // default: the country's name
	sub?: string; // a second, smaller line
	lang?: 'en' | 'bn';
	style?: LabelStyle; // caps (default, quiet context), title (the subject), plain
	mode?: 'auto' | 'inside' | 'callout'; // auto: a callout when the name does not fit inside
	side?: Side; // callout side
	size?: number; // px at 1080
	color?: string;
	halo?: string; // the outline behind the letters (default the land colour; the fill colour on a highlight)
	delay?: number;
	duration?: number;
	out?: boolean; // leave at the end of the Sequence (default false: it stays, so the last frame is never half-faded)
	outAt?: number;
	offset?: [number, number]; // nudge in px at 1080
	decideAt?: number; // the frame whose view decides inside or callout, and the side (default: delay)
};

/** One country's name, inside the country or as a callout with a leader line. */
export const CountryLabel: React.FC<CountryLabelProps> = ({
	country,
	text,
	sub,
	lang = 'en',
	style = 'caps',
	mode = 'auto',
	side = 'auto',
	size,
	color,
	halo,
	delay = 0,
	duration,
	out = false,
	outAt,
	offset = [0, 0],
	decideAt,
}) => {
	const map = useMap();
	const t = useTheme();
	const {fps} = useStage();
	const inFrames = duration ?? at30(t.motion.enterFrames, fps);
	const {p, q} = useLife(delay, inFrames, out, outAt);
	const anchor = countryAnchor(country);
	if (!anchor || p <= 0 || q >= 1) {
		return null;
	}
	const label = text ?? countryName(country, lang);
	const pt = map.project(anchor.lonlat);
	if (!Number.isFinite(pt.x) || pt.visible <= 0.01) {
		return null;
	}
	// inside or callout, and the callout side, are decided on one frame so they never flip during a move
	const then = map.projectAt(decideAt ?? delay);
	const pt0 = then(anchor.lonlat);
	const up0 = then([anchor.lonlat[0], anchor.lonlat[1] + anchor.radiusDeg]);
	const radiusPx = Math.abs(pt0.y - up0.y) || anchor.radiusDeg * map.pxPerDeg;
	const spec = textSpec(t, style, map.unit, size, label);
	const width = estimateWidth(label, spec.fontSize, spec.textTransform === 'uppercase');
	const fitsInside = width <= radiusPx * 2.6 && spec.fontSize * 1.2 <= radiusPx * 2;
	const useCallout = mode === 'callout' || (mode === 'auto' && !fitsInside);
	const x = pt.x + offset[0] * map.unit;
	const y = pt.y + offset[1] * map.unit;
	const vis = pt.visible;

	if (useCallout) {
		// the leader runs from the heart of the country to just past its edge, so the tag never covers it
		const box0 = map.countryBox(country, decideAt ?? delay);
		const box = map.countryBox(country);
		const tagW = estimateWidth(label, (size ?? 26) * map.unit, false) + 60 * map.unit;
		const s = side === 'auto' ? bestSide(pt0.x, pt0.y, map.safe, tagW, box0) : side;
		const lead = 40 * map.unit;
		const past = 30 * map.unit;
		const ex = s === 'right' ? Math.max(x + lead, (box?.x1 ?? x) + past) : s === 'left' ? Math.min(x - lead, (box?.x0 ?? x) - past) : x;
		const ey = s === 'top' ? Math.min(y - lead, (box?.y0 ?? y) - past) : s === 'bottom' ? Math.max(y + lead, (box?.y1 ?? y) + past) : y;
		const lp = Math.min(1, p * 1.6);
		return (
			<>
				<svg style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: vis * (1 - q)}} width={map.width} height={map.height}>
					<line x1={x} y1={y} x2={x + (ex - x) * lp} y2={y + (ey - y) * lp} stroke={map.palette.label} strokeWidth={2 * map.unit} strokeLinecap="round" />
					<circle cx={x} cy={y} r={5 * map.unit * Math.min(1, p * 2)} fill={map.palette.label} stroke={map.palette.pinRing} strokeWidth={1.5 * map.unit} />
				</svg>
				<Tag x={ex} y={ey} title={label} sub={sub} side={s} gap={6 * map.unit} p={ramp(p, 0.35, 0.65, curves.linear)} q={q} map={map} size={size ?? 26} />
			</>
		);
	}

	const lift = (1 - p) * 8 * map.unit - q * 6 * map.unit;
	const haloW = Math.max(3, spec.fontSize * 0.22);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				translate: `-50% calc(-50% + ${lift}px)`,
				opacity: p * (1 - q) * vis,
				textAlign: 'center',
				whiteSpace: 'nowrap',
				pointerEvents: 'none',
			}}
		>
			<div
				style={{
					...spec,
					lineHeight: 1.05,
					color: color ?? (style === 'caps' ? map.palette.labelMuted : map.palette.label),
					WebkitTextStroke: `${haloW}px ${halo ?? map.palette.halo}`,
					paintOrder: 'stroke fill',
					textRendering: 'geometricPrecision',
				}}
			>
				{label}
			</div>
			{sub ? (
				<div
					style={{
						fontFamily: BANGLA.test(sub) ? t.type.bangla : t.type.body,
						fontWeight: t.weights.body,
						fontSize: spec.fontSize * 0.62,
						lineHeight: 1.3,
						marginTop: spec.fontSize * 0.12,
						color: color ?? map.palette.labelMuted,
						opacity: color ? 0.85 : 1,
						WebkitTextStroke: `${haloW * 0.7}px ${halo ?? map.palette.halo}`,
						paintOrder: 'stroke fill',
						textRendering: 'geometricPrecision',
					}}
				>
					{sub}
				</div>
			) : null}
		</div>
	);
};

export type CountryLabelsProps = {
	countries?: CountryRef[]; // default: every country whose name fits inside it
	exclude?: CountryRef[];
	lang?: 'en' | 'bn';
	style?: LabelStyle;
	size?: number;
	max?: number; // at most this many (biggest first)
	delay?: number;
	stagger?: number; // frames between labels (biggest first)
	out?: boolean;
	outAt?: number;
	decideAt?: number; // the frame whose view decides which names show (default: delay)
};

/**
 * Names for many countries at once: only where the name fits inside the country, biggest countries first, and
 * never two labels on top of each other. The set is decided on one frame (decideAt) so names do not pop in and
 * out while the camera moves; after that they simply travel with the map.
 */
export const CountryLabels: React.FC<CountryLabelsProps> = ({
	countries,
	exclude = [],
	lang = 'en',
	style = 'caps',
	size,
	max = 40,
	delay = 0,
	stagger = 2,
	out = false,
	outAt,
	decideAt,
}) => {
	const map = useMap();
	const t = useTheme();
	const project = map.projectAt(decideAt ?? delay);
	const skip = new Set(exclude.map((c) => requireCountryKey(c)));
	const keys = (countries ? countries.map((c) => requireCountryKey(c)) : allCountries().map((c) => c.key)).filter((k) => !skip.has(k) && k !== '010');
	type Cand = {key: string; x: number; y: number; w: number; h: number; r: number};
	const cands: Cand[] = [];
	for (const key of keys) {
		const a = countryAnchor(key);
		if (!a) {
			continue;
		}
		const pt = project(a.lonlat);
		if (!Number.isFinite(pt.x) || pt.visible < 0.5) {
			continue;
		}
		const up = project([a.lonlat[0], a.lonlat[1] + a.radiusDeg]);
		const r = Math.abs(pt.y - up.y);
		const label = countryName(key, lang);
		const spec = textSpec(t, style, map.unit, size, label);
		const w = estimateWidth(label, spec.fontSize, spec.textTransform === 'uppercase');
		const h = spec.fontSize * 1.1;
		const inside = pt.x - w / 2 >= map.safe.x && pt.x + w / 2 <= map.safe.x + map.safe.w && pt.y - h / 2 >= map.safe.y && pt.y + h / 2 <= map.safe.y + map.safe.h;
		if (!inside) {
			continue;
		}
		if (!countries && !(w <= r * 3.6 && h <= r * 1.8)) {
			continue;
		}
		cands.push({key, x: pt.x, y: pt.y, w, h, r});
	}
	cands.sort((a, b) => b.r - a.r);
	const placed: Cand[] = [];
	const pad = 6 * map.unit;
	for (const c of cands) {
		if (placed.length >= max) {
			break;
		}
		const hit = placed.some((o) => Math.abs(o.x - c.x) * 2 < o.w + c.w + pad * 2 && Math.abs(o.y - c.y) * 2 < o.h + c.h + pad * 2);
		if (!hit) {
			placed.push(c);
		}
	}
	return (
		<>
			{placed.map((c, i) => (
				<CountryLabel key={c.key} country={c.key} lang={lang} style={style} size={size} mode="inside" delay={delay + i * stagger} out={out} outAt={outAt} />
			))}
		</>
	);
};
