// <Globe>: an orthographic globe that turns to face places (keys), can spin slowly, and zooms. Land, borders and
// a graticule are re-projected every frame (d3 clips them at the horizon); shading and a thin atmosphere give it
// volume. Routes lift off the surface and pass behind it; pins and labels fade at the edge.
import {geoInterpolate, geoOrthographic, geoPath, geoRotation, geoGraticule10} from 'd3-geo';
import React, {useId, useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease, type Rect} from '../core';
import {ramp} from '../motion';
import {atlas, type Detail, type LonLat} from './atlas';
import {lineFor, mapPalette, mix, textOn, type MapPalette} from './color';
import {requireCountryKey, type CountryRef} from './countries';
import {MapContext, type MapApi, type Projected} from './context';
import {linesToPath, mainBounds, mainCentroid, Recorder, sliceLines, type Line} from './geo';
import {CountryLabel} from './Labels';
import {countryAnchor} from './plate';
import {useHighlights, type FillSpec, type WorldMapProps} from './WorldMap';

export type GlobeKey = {
	at: number;
	center?: LonLat | CountryRef; // the place that faces the viewer
	zoom?: number; // 1: the globe at its size; 2: twice as big
	ease?: Ease;
};

export type GlobeProps = {
	size?: number; // diameter px at 1080 (default 82% of the box's short side)
	x?: number; // centre, px at 1080 from the box's left (default the middle)
	y?: number;
	width?: number; // box, px at 1080 (default the frame)
	height?: number;
	keys?: GlobeKey[];
	center?: LonLat | CountryRef; // when there are no keys (default [15, 22])
	zoom?: number;
	spin?: number; // degrees per second of steady turn to the east (default 0)
	detail?: Detail | 'auto'; // auto: 110m, 50m once zoomed in
	graticule?: boolean;
	borders?: boolean;
	shade?: boolean; // light from the upper left and a darker rim
	glow?: boolean; // a thin atmosphere
	highlight?: WorldMapProps['highlight'];
	fills?: Record<string, FillSpec>;
	colors?: Partial<MapPalette>;
	safe?: Rect;
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

type Resolved = {at: number; center: LonLat; zoom: number; ease: Ease};

const centerOf = (c: LonLat | CountryRef | undefined, fallback: LonLat): LonLat => {
	if (c === undefined) {
		return fallback;
	}
	if (Array.isArray(c)) {
		return c as LonLat;
	}
	const f = atlas('50m').feature(requireCountryKey(c as CountryRef));
	return f ? mainCentroid(f) : fallback;
};

const viewAt = (frame: number, keys: readonly Resolved[]): {center: LonLat; zoom: number} => {
	if (frame <= keys[0].at) {
		return keys[0];
	}
	for (let i = 0; i < keys.length - 1; i++) {
		const a = keys[i];
		const b = keys[i + 1];
		if (frame < b.at) {
			const t = b.ease(Math.min(1, Math.max(0, (frame - a.at) / Math.max(1, b.at - a.at))));
			return {center: geoInterpolate(a.center, b.center)(t) as LonLat, zoom: a.zoom * (b.zoom / a.zoom) ** t};
		}
	}
	return keys[keys.length - 1];
};

export const Globe: React.FC<GlobeProps> = ({
	size,
	x,
	y,
	width,
	height,
	keys,
	center,
	zoom = 1,
	spin = 0,
	detail = 'auto',
	graticule = true,
	borders = true,
	shade = true,
	glow = true,
	highlight,
	fills,
	colors,
	safe,
	style,
	children,
}) => {
	const frame = useCurrentFrame();
	const stage = useStage();
	const t = useTheme();
	const {unit, fps} = stage;
	const W = width !== undefined ? width * unit : stage.width;
	const H = height !== undefined ? height * unit : stage.height;
	const palette = useMemo(() => mapPalette(t, colors), [t, colors]);
	const uid = useId().replace(/[^a-zA-Z0-9_-]/g, '');
	const hls = useHighlights(highlight, palette, fps);

	const resolved: Resolved[] = useMemo(() => {
		const list = keys && keys.length ? [...keys].sort((a, b) => a.at - b.at) : [{at: 0, center, zoom}];
		let last: LonLat = centerOf(center, [15, 22]);
		let lastZoom = zoom;
		return list.map((k) => {
			last = centerOf(k.center, last);
			lastZoom = k.zoom ?? lastZoom;
			return {at: k.at, center: last, zoom: lastZoom, ease: k.ease ?? curves.inOut};
		});
	}, [keys, center, zoom]);

	const v = viewAt(frame, resolved);
	const lon = v.center[0] + (spin * frame) / fps;
	const lat = v.center[1];
	const R = ((size ?? (Math.min(W, H) / unit) * 0.82) * unit * v.zoom) / 2;
	const cx = x !== undefined ? x * unit : W / 2;
	const cy = y !== undefined ? y * unit : H / 2;
	const rotate: [number, number, number] = [-lon, -lat, 0];
	const pxPerDeg = (R * Math.PI) / 180;
	const level: Detail = detail === 'auto' ? (pxPerDeg > 14 ? '50m' : '110m') : detail === '10m' ? '50m' : detail;

	const projection = geoOrthographic().rotate(rotate).scale(R).translate([cx, cy]).clipAngle(90).precision(0.4);
	const path = geoPath(projection);
	path.digits(1);
	const rec = new Recorder();
	const recPath = geoPath(projection, rec);

	const a = atlas(level);
	const fine = atlas('50m');
	const fillMap = useMemo(() => {
		const m = new Map<string, {color: string; delay: number; duration: number}>();
		for (const [ref, spec] of Object.entries(fills ?? {})) {
			const s = typeof spec === 'string' ? {color: spec} : spec;
			m.set(requireCountryKey(ref), {color: s.color, delay: s.delay ?? 0, duration: s.duration ?? at30(14, fps)});
		}
		return m;
	}, [fills, fps]);

	const land = a.keys.map((k) => {
		const f = a.feature(k);
		const d = f ? path(f) : null;
		if (!d) {
			return null;
		}
		const fill = fillMap.get(k);
		const col = fill ? mix(palette.land, fill.color, ramp(frame, fill.delay, fill.duration, curves.outCubic)) : palette.land;
		// without border lines, a hairline in the fill colour hides the seams between neighbours
		return <path key={k} d={d} fill={col} stroke={borders ? undefined : col} strokeWidth={borders ? undefined : 0.6 * unit} />;
	});
	const borderPaths = borders
		? a.keys.map((k) => {
				const d = path(a.borders(k));
				return d ? <path key={`b${k}`} d={d} fill="none" stroke={palette.border} strokeWidth={1.1 * unit} strokeLinejoin="round" /> : null;
			})
		: null;

	const rot = geoRotation(rotate);
	const project = (c: LonLat, alt = 0): Projected => {
		const r = rot(c);
		const l = (r[0] * Math.PI) / 180;
		const p = (r[1] * Math.PI) / 180;
		const X = Math.cos(p) * Math.sin(l);
		const Y = Math.sin(p);
		const Z = Math.cos(p) * Math.cos(l);
		const s = 1 + Math.max(0, alt);
		let visible: number;
		if (alt <= 0) {
			visible = Math.min(1, Math.max(0, (Z + 0.02) / 0.14));
		} else {
			visible = Z >= 0 || (X * X + Y * Y) * s * s >= 1 ? 1 : 0;
		}
		return {x: cx + R * s * X, y: cy - R * s * Y, visible};
	};

	const highlights = hls.map((h, i) => {
		const f = fine.feature(h.key);
		if (!f) {
			return null;
		}
		const d = path(f);
		const drawP = h.spec.outline === false ? 0 : h.draw > 0 ? ramp(frame, h.delay, h.draw, curves.inOut) : 1;
		const fillP = ramp(frame, h.fillStart, h.fill, curves.outCubic);
		const settle = h.fill <= 0 ? 1 : ramp(frame, h.fillStart + h.fill * 0.7, at30(16, fps), curves.outCubic);
		const color = settle >= 1 ? h.color : mix(mix(h.color, '#FFFFFF', 0.28), h.color, settle);
		let outline = '';
		if (drawP > 0) {
			const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
			const rings: Line[] = polys.flatMap((r) => r).map((ring) => ({points: ring.map((q) => [q[0], q[1]] as [number, number]), closed: false}));
			const part = sliceLines(rings, drawP);
			recPath({type: 'MultiLineString', coordinates: part.map((l) => l.points)});
			outline = linesToPath(rec.take());
		}
		const b = d ? path.bounds(f) : null;
		const anchor = countryAnchor(h.key);
		const ap = anchor ? project(anchor.lonlat) : null;
		const ax = ap ? ap.x : b ? (b[0][0] + b[1][0]) / 2 : cx;
		const ay = ap ? ap.y : b ? (b[0][1] + b[1][1]) / 2 : cy;
		const rr = b ? Math.max(Math.hypot(b[0][0] - ax, b[0][1] - ay), Math.hypot(b[1][0] - ax, b[1][1] - ay), Math.hypot(b[0][0] - ax, b[1][1] - ay), Math.hypot(b[1][0] - ax, b[0][1] - ay)) : R;
		const id = `${uid}-h${i}`;
		return (
			<g key={id}>
				{d && fillP > 0 ? (
					h.reveal === 'radial' && fillP < 1 ? (
						<>
							<defs>
								<radialGradient id={`${id}-g`}>
									<stop offset="0.86" stopColor="#FFFFFF" />
									<stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
								</radialGradient>
								<mask id={`${id}-m`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
									<circle cx={ax} cy={ay} r={Math.max(0.01, rr * 1.15 * fillP)} fill={`url(#${id}-g)`} />
								</mask>
							</defs>
							<path d={d} fill={color} mask={`url(#${id}-m)`} />
						</>
					) : (
						<path d={d} fill={color} opacity={h.reveal === 'fade' ? fillP : 1} />
					)
				) : null}
				{outline ? <path d={outline} fill="none" stroke={h.color === palette.highlight[0] ? palette.highlightLine : lineFor(h.color, palette.dark)} strokeWidth={2.2 * unit} strokeLinejoin="round" strokeLinecap="round" /> : null}
			</g>
		);
	});

	const fullFrame = W === stage.width && H === stage.height;
	const api: MapApi = {
		kind: 'globe',
		width: W,
		height: H,
		safe: safe ?? (fullFrame ? stage.safe : {x: W * 0.05, y: H * 0.05, w: W * 0.9, h: H * 0.9}),
		unit,
		palette,
		detail: level,
		project,
		projectAt: (f: number) => {
			const vv = viewAt(f, resolved);
			const rr = geoRotation([-(vv.center[0] + (spin * f) / fps), -vv.center[1], 0]);
			const RR = ((size ?? (Math.min(W, H) / unit) * 0.82) * unit * vv.zoom) / 2;
			return (c: LonLat, alt = 0) => {
				const r = rr(c);
				const l = (r[0] * Math.PI) / 180;
				const p = (r[1] * Math.PI) / 180;
				const s = 1 + Math.max(0, alt);
				const Z = Math.cos(p) * Math.cos(l);
				return {x: cx + RR * s * Math.cos(p) * Math.sin(l), y: cy - RR * s * Math.sin(p), visible: Math.min(1, Math.max(0, (Z + 0.02) / 0.14))};
			};
		},
		pxPerDeg,
		projection,
		countryBox: (ref, f) => {
			const feat = fine.feature(requireCountryKey(ref));
			if (!feat) {
				return null;
			}
			const [[w, s], [e, n]] = mainBounds(feat);
			const east = e < w ? e + 360 : e;
			const pr = f === undefined ? project : api.projectAt(f);
			let box: {x0: number; y0: number; x1: number; y1: number} | null = null;
			for (let i = 0; i <= 4; i++) {
				for (let j = 0; j <= 4; j++) {
					const q = pr([w + ((east - w) * i) / 4, s + ((n - s) * j) / 4]);
					if (q.visible > 0.2) {
						box = box ? {x0: Math.min(box.x0, q.x), y0: Math.min(box.y0, q.y), x1: Math.max(box.x1, q.x), y1: Math.max(box.y1, q.y)} : {x0: q.x, y0: q.y, x1: q.x, y1: q.y};
					}
				}
			}
			return box;
		},
		globe: {cx, cy, r: R, center: [lon, lat]},
	};

	const glowColor = palette.dark ? mix(palette.ocean, t.colors.accent, 0.55) : mix(palette.ocean, t.colors.accent, 0.35);
	return (
		<div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, overflow: 'hidden', ...style}}>
			<svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
				<defs>
					<radialGradient id={`${uid}-glow`} cx={cx} cy={cy} r={R * 1.14} gradientUnits="userSpaceOnUse">
						<stop offset={0.86} stopColor={glowColor} stopOpacity={palette.dark ? 0.55 : 0.4} />
						<stop offset={0.9} stopColor={glowColor} stopOpacity={palette.dark ? 0.22 : 0.16} />
						<stop offset={1} stopColor={glowColor} stopOpacity={0} />
					</radialGradient>
					<radialGradient id={`${uid}-sea`} cx={cx - R * 0.35} cy={cy - R * 0.4} r={R * 1.45} gradientUnits="userSpaceOnUse">
						<stop offset={0} stopColor={mix(palette.ocean, '#FFFFFF', palette.dark ? 0.1 : 0.5)} />
						<stop offset={1} stopColor={mix(palette.ocean, palette.dark ? '#000000' : t.colors.text, palette.dark ? 0.35 : 0.08)} />
					</radialGradient>
					<radialGradient id={`${uid}-rim`} cx={cx} cy={cy} r={R} gradientUnits="userSpaceOnUse">
						<stop offset={0.62} stopColor="#000000" stopOpacity={0} />
						<stop offset={1} stopColor="#000000" stopOpacity={palette.dark ? 0.42 : 0.16} />
					</radialGradient>
					<radialGradient id={`${uid}-spec`} cx={cx - R * 0.42} cy={cy - R * 0.45} r={R * 0.9} gradientUnits="userSpaceOnUse">
						<stop offset={0} stopColor="#FFFFFF" stopOpacity={palette.dark ? 0.1 : 0.28} />
						<stop offset={1} stopColor="#FFFFFF" stopOpacity={0} />
					</radialGradient>
				</defs>
				{glow ? <circle cx={cx} cy={cy} r={R * 1.14} fill={`url(#${uid}-glow)`} /> : null}
				<circle cx={cx} cy={cy} r={R} fill={shade ? `url(#${uid}-sea)` : palette.ocean} />
				{graticule ? <path d={path(geoGraticule10()) ?? ''} fill="none" stroke={palette.graticule} strokeWidth={unit} /> : null}
				{land}
				{borderPaths}
				{highlights}
				{shade ? (
					<>
						<circle cx={cx} cy={cy} r={R} fill={`url(#${uid}-rim)`} />
						<circle cx={cx} cy={cy} r={R} fill={`url(#${uid}-spec)`} />
					</>
				) : null}
				<circle cx={cx} cy={cy} r={R} fill="none" stroke={palette.sphere} strokeWidth={1.2 * unit} />
			</svg>
			<MapContext.Provider value={api}>
				{hls
					.filter((h) => h.spec.label)
					.map((h) => (
						<CountryLabel
							key={`l${h.key}`}
							country={h.key}
							text={typeof h.spec.label === 'string' ? h.spec.label : undefined}
							sub={h.spec.sub}
							lang={h.spec.lang}
							style={h.spec.labelStyle ?? 'title'}
							mode={h.spec.labelMode ?? 'auto'}
							side={h.spec.labelSide}
							delay={h.fillStart + (h.spec.labelDelay ?? Math.round(h.fill * 0.6))}
							out={h.spec.out ?? true}
							color={textOn(h.color, [t.colors.text, t.colors.bg, '#FFFFFF', '#111111'])}
							halo={h.color}
						/>
					))}
				{children}
			</MapContext.Provider>
		</div>
	);
};
