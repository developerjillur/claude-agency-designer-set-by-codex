// <WorldMap>: a flat world map (natural earth, equal earth, mercator or equirectangular) drawn from Natural Earth
// data, coloured by the theme, with a camera (keys that frame the world, countries, places or a box), animated
// country highlights and per-country fills. Pins, routes and labels go inside it as children.
import React, {useId, useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Rect} from '../core';
import {ramp} from '../motion';
import {useAtlas10m, type Detail, type LonLat} from './atlas';
import {maxZoom, resolveKeys, viewAt, type MapKey} from './camera';
import {lineFor, mapPalette, mix, textOn, type MapPalette} from './color';
import {requireCountryKey, type CountryRef} from './countries';
import {MapContext, type MapApi, type Projected} from './context';
import {linesToPath, makeProjection, sliceLines, type Box, type ProjectionName, type View} from './geo';
import {CountryLabel, type LabelStyle, type Side} from './Labels';
import {countryAnchor, getPlate, type OceanMode, type Plate} from './plate';

export type HighlightSpec = {
	country: CountryRef;
	color?: string; // default: the theme accent (then accent2 ...)
	delay?: number; // frames
	draw?: number; // outline draw-on frames (0: the outline is there at once, or not at all with outline false)
	outline?: boolean; // default true
	fill?: number; // fill frames
	reveal?: 'radial' | 'fade'; // radial: the colour spreads from the heart of the country
	label?: boolean | string; // true: the country's name
	sub?: string; // second line under the label
	lang?: 'en' | 'bn';
	labelStyle?: LabelStyle; // default 'title'
	labelMode?: 'auto' | 'inside' | 'callout';
	labelSide?: Side;
	labelDelay?: number; // frames after the fill starts (default: when it is nearly done)
	out?: boolean; // the label leaves at the end of the Sequence (default false: it stays)
};

export type FillSpec = string | {color: string; delay?: number; duration?: number};

export type WorldMapProps = {
	projection?: ProjectionName | 'auto'; // auto: natural earth for world views, Mercator (true local shapes) once the camera zooms past about 3x
	meridian?: number; // central meridian (default 0; 150 to 180 puts the Pacific in the middle)
	width?: number; // map box, px at 1080 (default: the frame); place it with style={{left, top}}
	height?: number;
	camera?: MapKey[]; // default: the whole world
	rho?: number; // how much long pans rise (default 1.2; 0.8 flatter, 1.6 higher)
	detail?: Detail | 'auto'; // auto: 50m, and 10m once zoomed in close (loaded on demand)
	ocean?: OceanMode; // sphere: the world's outline on the ground; frame: water edge to edge
	antarctica?: boolean; // default false (it takes a fifth of the frame and rarely matters)
	padding?: number; // px at 1080 around the world at zoom 1 (default 40)
	graticule?: boolean;
	borders?: boolean;
	coast?: boolean;
	highlight?: CountryRef | CountryRef[] | HighlightSpec[];
	fills?: Record<string, FillSpec>; // country ref -> colour (choropleths, groups of countries)
	intro?: 'none' | 'fade' | 'sweep'; // how the map itself appears (default none: frame 0 is composed)
	introDuration?: number;
	delay?: number; // frames before the intro
	colors?: Partial<MapPalette>;
	safe?: Rect; // where labels stay, real box px like useStage().safe (default: the frame's safe area, or 5% inside the box)
	style?: React.CSSProperties;
	children?: React.ReactNode;
};

type HL = {
	key: string;
	color: string;
	delay: number;
	draw: number;
	fill: number;
	fillStart: number;
	reveal: 'radial' | 'fade';
	spec: HighlightSpec;
};

// 50m to 10m cross-fade, in screen px per degree
const FINE_START = 34;
const FINE_END = 58;

const cleanId = (s: string) => s.replace(/[^a-zA-Z0-9_-]/g, '');

export const useHighlights = (
	highlight: WorldMapProps['highlight'],
	palette: MapPalette,
	fps: number,
): HL[] =>
	useMemo(() => {
		if (highlight === undefined) {
			return [];
		}
		const list: HighlightSpec[] = (Array.isArray(highlight) ? highlight : [highlight]).map((h) =>
			typeof h === 'object' && h !== null && !Array.isArray(h) && 'country' in h ? h : {country: h as CountryRef},
		);
		return list.map((h, i) => {
			const draw = h.draw ?? at30(30, fps);
			const fill = h.fill ?? at30(20, fps);
			const delay = h.delay ?? 0;
			return {
				key: requireCountryKey(h.country),
				color: h.color ?? palette.highlight[i % palette.highlight.length],
				delay,
				draw,
				fill,
				fillStart: delay + Math.round(draw * 0.45),
				reveal: h.reveal ?? 'radial',
				spec: h,
			};
		});
	}, [highlight, palette, fps]);

export const WorldMap: React.FC<WorldMapProps> = ({
	projection: projectionProp = 'auto',
	meridian = 0,
	width,
	height,
	camera,
	rho = 1.2,
	detail = 'auto',
	ocean,
	antarctica = false,
	padding = 40,
	graticule = false,
	borders = true,
	coast = false,
	highlight,
	fills,
	intro = 'none',
	introDuration,
	delay = 0,
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
	// auto: a close zoom in a world projection shears the place (a circle round Dhaka turns into a tilted 1.2 : 1
	// ellipse in natural earth); Mercator keeps local shapes true, so zooms past a continent use it
	const projection: ProjectionName = useMemo(() => {
		if (projectionProp !== 'auto') {
			return projectionProp;
		}
		const probe = getPlate({projection: 'naturalEarth1', width: W, height: H, ocean: 'sphere', antarctica, padding: padding * unit, meridian});
		return maxZoom(resolveKeys(camera, probe, W, H), W) > 3 ? 'mercator' : 'naturalEarth1';
	}, [projectionProp, camera, W, H, antarctica, padding, unit, meridian]);
	const oceanMode: OceanMode = ocean ?? (projection === 'mercator' || projection === 'equirectangular' ? 'frame' : 'sphere');
	const plate = getPlate({projection, width: W, height: H, ocean: oceanMode, antarctica, padding: padding * unit, meridian});
	const keys = useMemo(() => resolveKeys(camera, plate, W, H), [camera, plate, W, H]);
	const view = viewAt(frame, keys, rho);
	const k = W / view[2];
	const ppdNow = plate.ppd * k;
	const needs10m = detail === '10m' || (detail === 'auto' && maxZoom(keys, W) * plate.ppd > FINE_START);
	const fine = useAtlas10m(needs10m);
	const hls = useHighlights(highlight, palette, fps);
	const uid = cleanId(useId());

	const levels: {detail: Detail; opacity: number}[] = (() => {
		if (detail !== 'auto') {
			return [{detail: detail === '10m' && !fine ? '50m' : detail, opacity: 1}];
		}
		const x = fine ? Math.min(1, Math.max(0, (ppdNow - FINE_START) / (FINE_END - FINE_START))) : 0;
		if (x <= 0) {
			return [{detail: '50m', opacity: 1}];
		}
		if (x >= 1) {
			return [{detail: '10m', opacity: 1}];
		}
		// the fine level underneath at full strength, the coarse one on top fading out (no see-through land)
		return [
			{detail: '10m', opacity: 1},
			{detail: '50m', opacity: 1 - curves.sine(x)},
		];
	})();

	const vb: Box = [view[0] - view[2] / 2, view[1] - (view[2] * H) / W / 2, view[0] + view[2] / 2, view[1] + (view[2] * H) / W / 2];
	const margin = view[2] * 0.03;
	const cull: Box = [vb[0] - margin, vb[1] - margin, vb[2] + margin, vb[3] + margin];

	// the intro: whole map fading, or countries appearing west to east
	const introFrames = introDuration ?? at30(36, fps);
	// the ground (ocean, sphere) is there from frame 0 in a sweep; only the land arrives
	const baseOpacity = intro === 'fade' ? ramp(frame, delay, introFrames, curves.outCubic) : 1;
	const countryIntro = (box: Box): number => {
		if (intro !== 'sweep') {
			return 1;
		}
		const rel = ((box[0] + box[2]) / 2 - plate.world[0]) / Math.max(1, plate.world[2] - plate.world[0]);
		const start = delay + Math.max(0, Math.min(1, rel)) * introFrames * 0.7;
		return ramp(frame, start, Math.max(6, introFrames * 0.3), curves.outCubic);
	};

	const fillMap = useMemo(() => {
		const m = new Map<string, {color: string; delay: number; duration: number}>();
		for (const [ref, spec] of Object.entries(fills ?? {})) {
			const s = typeof spec === 'string' ? {color: spec} : spec;
			m.set(requireCountryKey(ref), {color: s.color, delay: s.delay ?? 0, duration: s.duration ?? at30(14, fps)});
		}
		return m;
	}, [fills, fps]);

	const fillOf = (key: string): string => {
		const f = fillMap.get(key);
		if (!f) {
			return palette.land;
		}
		return mix(palette.land, f.color, ramp(frame, f.delay, f.duration, curves.outCubic));
	};

	const cullBox = (key: string): Box | null => plate.shape('50m', key)?.box ?? plate.shape('10m', key)?.box ?? null;
	const lineW = 1.1 * unit;
	const hlLine = 2.4 * unit;

	const renderLevel = (lv: {detail: Detail; opacity: number}) => {
		const visible = plate.keys(lv.detail).filter((key) => {
			const b = cullBox(key);
			return b !== null && b[0] <= cull[2] && cull[0] <= b[2] && b[1] <= cull[3] && cull[1] <= b[3];
		});
		return (
			<g key={lv.detail} opacity={lv.opacity}>
				{visible.map((key) => {
					const s = plate.shape(lv.detail, key);
					if (!s) {
						return null;
					}
					const o = countryIntro(s.box);
					const fill = fillOf(key);
					return (
						<path
							key={key}
							d={s.d}
							fill={fill}
							opacity={o < 1 ? o : undefined}
							stroke={borders ? undefined : fill}
							strokeWidth={borders ? undefined : 0.6 * unit}
							vectorEffect={borders ? undefined : 'non-scaling-stroke'}
						/>
					);
				})}
				{borders
					? visible.map((key) => {
							const d = plate.borders(lv.detail, key);
							const s = plate.shape(lv.detail, key);
							const o = s ? countryIntro(s.box) : 1;
							return d ? (
								<path key={`b${key}`} d={d} fill="none" stroke={palette.border} strokeWidth={lineW} strokeLinejoin="round" vectorEffect="non-scaling-stroke" opacity={o < 1 ? o : undefined} />
							) : null;
						})
					: null}
				{coast
					? visible.map((key) => {
							const d = plate.coast(lv.detail, key);
							return d ? <path key={`c${key}`} d={d} fill="none" stroke={palette.coast} strokeWidth={lineW} strokeLinejoin="round" vectorEffect="non-scaling-stroke" /> : null;
						})
					: null}
				{hls.map((h, i) => renderHighlight(plate, lv.detail, h, `${uid}-${lv.detail}-${i}`))}
			</g>
		);
	};

	const renderHighlight = (pl: Plate, lv: Detail, h: HL, id: string) => {
		const s = pl.shape(lv, h.key);
		if (!s) {
			return null;
		}
		const drawP = h.spec.outline === false ? 0 : h.draw > 0 ? ramp(frame, h.delay, h.draw, curves.inOut) : 1;
		const fillP = ramp(frame, h.fillStart, h.fill, curves.outCubic);
		const settle = h.fill <= 0 ? 1 : ramp(frame, h.fillStart + h.fill * 0.7, at30(16, fps), curves.outCubic);
		const color = settle >= 1 ? h.color : mix(mix(h.color, '#FFFFFF', 0.28), h.color, settle);
		const anchor = countryAnchor(h.key);
		const a = anchor ? pl.project(anchor.lonlat) : null;
		const ax = a ? a[0] : (s.box[0] + s.box[2]) / 2;
		const ay = a ? a[1] : (s.box[1] + s.box[3]) / 2;
		const R = Math.max(...[s.box[0], s.box[2]].flatMap((x) => [s.box[1], s.box[3]].map((y) => Math.hypot(x - ax, y - ay)))) * 1.05;
		const lines = drawP > 0 ? pl.outline(lv, h.key) : [];
		const outlineD = drawP >= 1 ? linesToPath(lines) : linesToPath(sliceLines(lines, drawP));
		return (
			<g key={id}>
				{fillP > 0 ? (
					h.reveal === 'radial' && fillP < 1 ? (
						<>
							<defs>
								<radialGradient id={`${id}-g`}>
									<stop offset="0.86" stopColor="#FFFFFF" />
									<stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
								</radialGradient>
								<mask id={`${id}-m`} maskUnits="userSpaceOnUse" x={s.box[0] - R} y={s.box[1] - R} width={s.box[2] - s.box[0] + 2 * R} height={s.box[3] - s.box[1] + 2 * R}>
									<circle cx={ax} cy={ay} r={Math.max(1e-3, R * fillP * 1.15)} fill={`url(#${id}-g)`} />
								</mask>
							</defs>
							<path d={s.d} fill={color} mask={`url(#${id}-m)`} />
						</>
					) : (
						<path d={s.d} fill={color} opacity={h.reveal === 'fade' ? fillP : 1} />
					)
				) : null}
				{outlineD ? (
					<path d={outlineD} fill="none" stroke={h.color === palette.highlight[0] ? palette.highlightLine : lineFor(h.color, palette.dark)} strokeWidth={hlLine} strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
				) : null}
			</g>
		);
	};

	const projector = (v: View) => {
		const kk = W / v[2];
		return (c: LonLat): Projected => {
			const p = plate.project(c);
			return p ? {x: (p[0] - v[0]) * kk + W / 2, y: (p[1] - v[1]) * kk + H / 2, visible: 1} : {x: NaN, y: NaN, visible: 0};
		};
	};
	const boxAt = (v: View) => {
		const kk = W / v[2];
		return (ref: CountryRef) => {
			const b = plate.mainBox(requireCountryKey(ref));
			return b ? {x0: (b[0] - v[0]) * kk + W / 2, y0: (b[1] - v[1]) * kk + H / 2, x1: (b[2] - v[0]) * kk + W / 2, y1: (b[3] - v[1]) * kk + H / 2} : null;
		};
	};
	// this frame's projection straight to box px: the plate projection scaled and shifted by the camera
	const s0 = plate.projection.scale();
	const t0 = plate.projection.translate();
	const screenProjection = makeProjection(projection)
		.rotate([-meridian, 0])
		.precision(0.3)
		.scale(s0 * k)
		.translate([(t0[0] - view[0]) * k + W / 2, (t0[1] - view[1]) * k + H / 2]);
	const fullFrame = W === stage.width && H === stage.height;
	const api: MapApi = {
		kind: 'flat',
		width: W,
		height: H,
		safe: safe ?? (fullFrame ? stage.safe : {x: W * 0.05, y: H * 0.05, w: W * 0.9, h: H * 0.9}),
		unit,
		palette,
		detail: levels[0].detail,
		project: projector(view),
		projectAt: (f: number) => projector(viewAt(f, keys, rho)),
		pxPerDeg: ppdNow,
		projection: screenProjection,
		countryBox: (ref, f) => boxAt(f === undefined ? view : viewAt(f, keys, rho))(ref),
	};

	const sphere = oceanMode === 'sphere';
	return (
		<div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, overflow: 'hidden', background: sphere ? palette.stage : palette.ocean, ...style}}>
			<svg width={W} height={H} viewBox={`${vb[0]} ${vb[1]} ${vb[2] - vb[0]} ${vb[3] - vb[1]}`} style={{position: 'absolute', left: 0, top: 0, opacity: baseOpacity}}>
				{sphere ? <path d={plate.sphere} fill={palette.ocean} /> : null}
				{graticule ? <path d={plate.graticule} fill="none" stroke={palette.graticule} strokeWidth={unit} vectorEffect="non-scaling-stroke" /> : null}
				{levels.map(renderLevel)}
				{sphere ? <path d={plate.sphere} fill="none" stroke={palette.sphere} strokeWidth={1.2 * unit} vectorEffect="non-scaling-stroke" /> : null}
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
							out={h.spec.out ?? false}
							color={textOn(h.color, [t.colors.text, t.colors.bg, '#FFFFFF', '#111111'])}
							halo={h.color}
						/>
					))}
				{children}
			</MapContext.Provider>
		</div>
	);
};
