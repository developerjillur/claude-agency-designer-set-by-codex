// <CountryShape>: one country on its own, fitted to a box in an equal-area conic projection centred on it (true
// shape at any latitude). Its outline draws on, the fill spreads from its heart, then its name rises below.
import {geoBounds, geoConicEqualArea, geoPath} from 'd3-geo';
import React, {useId, useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {atlas, loadedAtlas, useAtlas10m, type Detail} from './atlas';
import {mapPalette, mix, type MapPalette} from './color';
import {countryName, requireCountryKey, type CountryRef} from './countries';
import {boundsOf, linesToPath, mainCentroid, mainPolygons, Recorder, sliceLines, type Line} from './geo';
import {useLife} from './Labels';
import {countryAnchor} from './plate';

export type CountryShapeProps = {
	country: CountryRef;
	width?: number; // px at 1080 (default: the frame's safe area)
	height?: number;
	detail?: Detail; // default 50m; 10m (loaded on demand) for a shape taller than about 500 px
	mainland?: boolean; // only the main body, without far territories (default true)
	delay?: number;
	draw?: number; // outline frames (default 40 at 30 fps)
	fill?: number; // fill frames (default 20)
	reveal?: 'radial' | 'fade';
	color?: string; // fill (default the accent)
	lineColor?: string;
	lineWidth?: number; // px at 1080 (default 3)
	label?: boolean | string; // default true: the country's name below the shape
	sub?: string;
	lang?: 'en' | 'bn';
	labelSize?: number; // px at 1080 (default 64)
	neighbours?: boolean; // the land around it, faint (default false)
	scale?: number; // px at 1080 per degree of latitude: the same number on several shapes compares their sizes
	shadow?: boolean; // a soft shadow under the shape (default true)
	out?: boolean; // the label leaves at the end of the Sequence (default false: it stays)
	outAt?: number;
	colors?: Partial<MapPalette>;
	style?: React.CSSProperties; // on the box (position it here when width and height are set)
};

export const CountryShape: React.FC<CountryShapeProps> = ({
	country,
	width,
	height,
	detail = '50m',
	mainland = true,
	delay = 0,
	draw,
	fill,
	reveal = 'radial',
	color,
	lineColor,
	lineWidth = 3,
	label = true,
	sub,
	lang = 'en',
	labelSize = 64,
	neighbours = false,
	scale,
	shadow = true,
	out = false,
	outAt,
	colors,
	style,
}) => {
	const frame = useCurrentFrame();
	const stage = useStage();
	const t = useTheme();
	const {unit, fps} = stage;
	const palette = useMemo(() => mapPalette(t, colors), [t, colors]);
	const key = requireCountryKey(country);
	const fine = useAtlas10m(detail === '10m');
	const level: Detail = detail === '10m' && !fine ? '50m' : detail;
	const uid = useId().replace(/[^a-zA-Z0-9_-]/g, '');

	const box = width !== undefined && height !== undefined ? {x: 0, y: 0, w: width * unit, h: height * unit} : stage.safe;
	const text = label === false ? '' : typeof label === 'string' ? label : countryName(key, lang);
	const labelH = text ? labelSize * unit * (sub ? 1.75 : 1.25) : 0;
	const pad = lineWidth * unit * 2 + 6 * unit;

	const geo = useMemo(() => {
		const a = loadedAtlas(level) ?? atlas('50m');
		const f = a.feature(key) ?? atlas('50m').feature(key);
		if (!f) {
			return null;
		}
		const polys = mainland ? mainPolygons(f) : f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
		const shape: GeoJSON.MultiPolygon = {type: 'MultiPolygon', coordinates: polys};
		const [[w, s], [e, n]] = geoBounds(shape);
		const c = mainCentroid(f);
		const p1 = s + (n - s) / 6;
		const p2 = n - (n - s) / 6;
		const proj = geoConicEqualArea()
			.parallels([p1, p2])
			.rotate([-c[0], 0])
			.fitExtent(
				[
					[box.x + pad, box.y + pad],
					[box.x + box.w - pad, box.y + box.h - labelH - pad],
				],
				shape,
			);
		if (scale !== undefined) {
			// a fixed scale (one degree of latitude = `scale` px), centred in the box
			const ay = proj([c[0], c[1] - 0.5]);
			const by = proj([c[0], c[1] + 0.5]);
			const now = ay && by ? Math.hypot(ay[0] - by[0], ay[1] - by[1]) : 1;
			proj.scale(proj.scale() * ((scale * unit) / Math.max(1e-6, now)));
			const b = geoPath(proj).bounds(shape);
			const [tx, ty] = proj.translate();
			proj.translate([tx + (box.x + box.w / 2 - (b[0][0] + b[1][0]) / 2), ty + (box.y + (box.h - labelH) / 2 - (b[0][1] + b[1][1]) / 2)]);
		}
		const rec = new Recorder();
		const path = geoPath(proj, rec);
		path(shape);
		const rings = rec.take();
		const bounds = boundsOf(rings) ?? [box.x, box.y, box.x + box.w, box.y + box.h];
		const d = linesToPath(rings);
		const anchor = countryAnchor(key);
		const ap = anchor ? (proj(anchor.lonlat) as [number, number] | null) : null;
		let around = '';
		let aroundBorders = '';
		if (neighbours) {
			const str = geoPath(proj);
			const expand = Math.max(e - w, n - s) * 0.9 + 3;
			const near = a.keys.filter((k) => {
				if (k === key) {
					return false;
				}
				const g = a.feature(k);
				if (!g) {
					return false;
				}
				const [[gw, gs], [ge, gn]] = geoBounds(g);
				return ge >= w - expand && gw <= e + expand && gn >= s - expand && gs <= n + expand;
			});
			around = near.map((k) => str(a.feature(k) as GeoJSON.Feature) ?? '').join('');
			aroundBorders = near.map((k) => str(a.borders(k)) ?? '').join('');
		}
		return {rings, d, bounds, anchor: ap, around, aroundBorders};
	}, [level, key, mainland, box.x, box.y, box.w, box.h, labelH, pad, neighbours, scale, unit]);

	const drawFrames = draw ?? at30(40, fps);
	const fillFrames = fill ?? at30(20, fps);
	const fillStart = delay + Math.round(drawFrames * 0.55);
	const labelStart = fillStart + Math.round(fillFrames * 0.5);
	const drawP = ramp(frame, delay, drawFrames, curves.inOut);
	const fillP = ramp(frame, fillStart, fillFrames, curves.outCubic);
	const settle = ramp(frame, fillStart + fillFrames * 0.7, at30(16, fps), curves.outCubic);
	const fillColor = color ?? palette.highlight[0];
	const shownFill = mix(mix(fillColor, '#FFFFFF', 0.28), fillColor, settle);
	const {p: lp, q: lq} = useLife(labelStart, at30(18, fps), out, outAt);

	if (!geo) {
		return null;
	}
	const [x0, y0, x1, y1] = geo.bounds;
	const ax = geo.anchor ? geo.anchor[0] : (x0 + x1) / 2;
	const ay = geo.anchor ? geo.anchor[1] : (y0 + y1) / 2;
	const R = Math.max(Math.hypot(x0 - ax, y0 - ay), Math.hypot(x1 - ax, y0 - ay), Math.hypot(x0 - ax, y1 - ay), Math.hypot(x1 - ax, y1 - ay)) * 1.05;
	const outline = drawP <= 0 ? '' : drawP >= 1 ? geo.d : linesToPath(sliceLines(geo.rings as Line[], drawP));
	const W = width !== undefined && height !== undefined ? box.w : stage.width;
	const H = width !== undefined && height !== undefined ? box.h : stage.height;
	const bangla = /[\u0980-\u09FF]/.test(text);

	return (
		<div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, ...style}}>
			<svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				<defs>
					<radialGradient id={`${uid}-g`}>
						<stop offset="0.86" stopColor="#FFFFFF" />
						<stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
					</radialGradient>
					<mask id={`${uid}-m`} maskUnits="userSpaceOnUse" x={x0 - R} y={y0 - R} width={x1 - x0 + 2 * R} height={y1 - y0 + 2 * R}>
						<circle cx={ax} cy={ay} r={Math.max(0.01, R * 1.15 * fillP)} fill={`url(#${uid}-g)`} />
					</mask>
				</defs>
				{geo.around ? (
					<g opacity={ramp(frame, delay - at30(8, fps), at30(12, fps), curves.outCubic)}>
						<path d={geo.around} fill={palette.land} />
						<path d={geo.aroundBorders} fill="none" stroke={palette.border} strokeWidth={1.2 * unit} strokeLinejoin="round" />
					</g>
				) : null}
				{fillP > 0 ? (
					<g style={shadow ? {filter: `drop-shadow(0px ${10 * unit}px ${18 * unit}px rgba(0, 0, 0, ${palette.dark ? 0.45 : 0.16}))`} : undefined}>
						<path
							d={geo.d}
							fill={shownFill}
							opacity={reveal === 'fade' ? fillP : 1}
							mask={reveal === 'radial' && fillP < 1 ? `url(#${uid}-m)` : undefined}
						/>
					</g>
				) : null}
				{outline ? (
					<path d={outline} fill="none" stroke={lineColor ?? palette.highlightLine} strokeWidth={lineWidth * unit} strokeLinejoin="round" strokeLinecap="round" />
				) : null}
			</svg>
			{text && lp > 0 && lq < 1 ? (
				<div
					style={{
						position: 'absolute',
						left: box.x,
						width: box.w,
						top: box.y + box.h - labelH,
						height: labelH,
						display: 'flex',
						flexDirection: 'column',
						alignItems: 'center',
						justifyContent: 'center',
						opacity: lp * (1 - lq),
						translate: `0px ${(1 - lp) * 18 * unit - lq * 10 * unit}px`,
					}}
				>
					<div
						style={{
							fontFamily: bangla ? t.type.bangla : t.type.display,
							fontWeight: t.weights.display,
							fontSize: labelSize * unit,
							lineHeight: 1.1,
							letterSpacing: bangla ? '0em' : `${t.tracking.display}em`,
							textTransform: t.caps && !bangla ? 'uppercase' : 'none',
							color: t.colors.text,
							textRendering: 'geometricPrecision',
							whiteSpace: 'nowrap',
						}}
					>
						{text}
					</div>
					{sub ? (
						<div
							style={{
								fontFamily: /[\u0980-\u09FF]/.test(sub) ? t.type.bangla : t.type.body,
								fontWeight: t.weights.body,
								fontSize: labelSize * 0.42 * unit,
								lineHeight: 1.3,
								marginTop: labelSize * 0.08 * unit,
								color: t.colors.muted,
								textRendering: 'geometricPrecision',
								whiteSpace: 'nowrap',
							}}
						>
							{sub}
						</div>
					) : null}
				</div>
			) : null}
		</div>
	);
};
