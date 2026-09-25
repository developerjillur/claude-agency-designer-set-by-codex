// <GeoLayer>: your own GeoJSON on a map or a globe (a district, a river, a coastline, a study area, a line of
// latitude): lines draw on over time, areas fill in after them. The kit's data has countries only; this is how
// anything else gets onto the map. Lines are cut in lon/lat before they are projected, so a draw-on stays steady
// while the camera moves.
import {geoArea, geoPath} from 'd3-geo';
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage} from '../core';
import {ramp} from '../motion';
import {withAlpha} from './color';
import {useMap} from './context';
import {sliceLines, type Line} from './geo';
import {useLife} from './Labels';

export type GeoLayerProps = {
	data: GeoJSON.GeoJSON; // a Feature, FeatureCollection or Geometry, in [lon, lat]
	stroke?: string; // default the theme accent
	strokeWidth?: number; // px at 1080 (default 3)
	dash?: 'solid' | 'dashed' | 'dotted';
	fill?: string; // areas (default none)
	fillOpacity?: number; // default 0.35
	delay?: number;
	draw?: number; // frames to draw the lines on (0: there at once; default 36 at 30 fps)
	fillFrames?: number; // default 18; the fill starts when the lines are 70% drawn
	head?: boolean; // a bright point leading each line while it draws (rivers, tracks)
	out?: boolean; // fade out at the end of the Sequence (default false)
	outAt?: number;
};

const collect = (g: GeoJSON.GeoJSON, lines: GeoJSON.Position[][], areas: GeoJSON.Geometry[]): void => {
	switch (g.type) {
		case 'FeatureCollection':
			g.features.forEach((f) => collect(f, lines, areas));
			return;
		case 'Feature':
			if (g.geometry) {
				collect(g.geometry, lines, areas);
			}
			return;
		case 'GeometryCollection':
			g.geometries.forEach((x) => collect(x, lines, areas));
			return;
		case 'LineString':
			lines.push(g.coordinates);
			return;
		case 'MultiLineString':
			lines.push(...g.coordinates);
			return;
		case 'Polygon':
			lines.push(...g.coordinates);
			areas.push(g);
			return;
		case 'MultiPolygon':
			g.coordinates.forEach((p) => lines.push(...p));
			areas.push(g);
			return;
		default:
			return;
	}
};

// d3 reads a polygon wound the other way as "the whole Earth except this". Files that follow the GeoJSON
// standard (RFC 7946, counter-clockwise outer rings) come out inverted, so every area is turned the d3 way.
const windClockwise = (g: GeoJSON.Geometry): GeoJSON.Geometry => {
	const fix = (rings: GeoJSON.Position[][]): GeoJSON.Position[][] =>
		geoArea({type: 'Polygon', coordinates: rings}) > 2 * Math.PI ? rings.map((r) => [...r].reverse()) : rings;
	if (g.type === 'Polygon') {
		return {...g, coordinates: fix(g.coordinates)};
	}
	if (g.type === 'MultiPolygon') {
		return {...g, coordinates: g.coordinates.map(fix)};
	}
	return g;
};

export const GeoLayer: React.FC<GeoLayerProps> = ({
	data,
	stroke,
	strokeWidth = 3,
	dash = 'solid',
	fill,
	fillOpacity = 0.35,
	delay = 0,
	draw,
	fillFrames,
	head = false,
	out = false,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const map = useMap();
	const {fps} = useStage();
	const {unit, palette} = map;
	const parts = useMemo(() => {
		const lines: GeoJSON.Position[][] = [];
		const areas: GeoJSON.Geometry[] = [];
		collect(data, lines, areas);
		// measured with longitude shrunk by the cosine of latitude, so a line draws at an even ground speed
		const geoLines: Line[] = lines.map((l) => ({points: l.map((p) => [p[0] * Math.cos((p[1] * Math.PI) / 180), p[1]] as [number, number]), closed: false}));
		return {geoLines, areas: areas.map(windClockwise)};
	}, [data]);
	const drawFrames = draw ?? at30(36, fps);
	const fillLen = fillFrames ?? at30(18, fps);
	const p = drawFrames > 0 ? ramp(frame, delay, drawFrames, curves.inOut) : frame >= delay ? 1 : 0;
	const fp = ramp(frame, delay + Math.round(drawFrames * 0.7), fillLen, curves.outCubic);
	const {q} = useLife(delay, 1, out, outAt);
	if (p <= 0 || q >= 1) {
		return null;
	}
	const path = geoPath(map.projection);
	const c = stroke ?? palette.highlight[0];
	const w = strokeWidth * unit;
	const partial = sliceLines(parts.geoLines, p).map((l) => ({
		points: l.points.map(([x, y]) => [x / Math.max(1e-6, Math.cos((y * Math.PI) / 180)), y] as [number, number]),
		closed: false,
	}));
	const lineD = path({type: 'MultiLineString', coordinates: partial.map((l) => l.points)}) ?? '';
	const dashArray = dash === 'dashed' ? `${3 * w} ${2.4 * w}` : dash === 'dotted' ? `0.01 ${2.6 * w}` : undefined;
	const heads =
		head && p < 1
			? partial.map((l, i) => {
					const end = l.points[l.points.length - 1];
					const pt = end ? map.project(end) : null;
					return pt && pt.visible > 0.1 ? (
						<g key={i} opacity={pt.visible}>
							<circle cx={pt.x} cy={pt.y} r={w * 3.2} fill={withAlpha(c, 0.25)} />
							<circle cx={pt.x} cy={pt.y} r={w * 1.1} fill={palette.pinRing} />
						</g>
					) : null;
				})
			: null;
	return (
		<svg width={map.width} height={map.height} style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: 1 - q}}>
			{fill && fp > 0
				? parts.areas.map((a, i) => <path key={i} d={path(a) ?? ''} fill={fill} fillOpacity={fillOpacity * fp} />)
				: null}
			<path d={lineD} fill="none" stroke={c} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dashArray} />
			{heads}
		</svg>
	);
};
