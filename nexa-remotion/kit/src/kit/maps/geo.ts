// Geometry for maps: projections, a path recorder (d3 draws into it, we keep the points), polyline slicing for
// draw-ons, great circles, the smooth zoom path between two views, and label anchors (pole of inaccessibility).
import {
	geoArea,
	geoBounds,
	geoCentroid,
	geoCircle,
	geoDistance,
	geoEqualEarth,
	geoEquirectangular,
	geoInterpolate,
	geoMercator,
	geoNaturalEarth1,
	geoOrthographic,
	type GeoProjection,
} from 'd3-geo';
import polylabel from 'polylabel';
import type {CountryFeature, LonLat} from './atlas';
import {polygonsOf} from './atlas';

export type ProjectionName = 'naturalEarth1' | 'equalEarth' | 'mercator' | 'equirectangular';

export const makeProjection = (name: ProjectionName | 'orthographic'): GeoProjection => {
	switch (name) {
		case 'equalEarth':
			return geoEqualEarth();
		case 'mercator':
			return geoMercator();
		case 'equirectangular':
			return geoEquirectangular();
		case 'orthographic':
			return geoOrthographic();
		case 'naturalEarth1':
		default:
			return geoNaturalEarth1();
	}
};

export type Pt = [number, number];
export type Line = {points: Pt[]; closed: boolean};

/** A d3 path context that keeps the points instead of drawing: projected rings and lines, ready to reuse. */
export class Recorder {
	lines: Line[] = [];
	private cur: Line | null = null;
	beginPath(): void {}
	moveTo(x: number, y: number): void {
		this.cur = {points: [[x, y]], closed: false};
		this.lines.push(this.cur);
	}
	lineTo(x: number, y: number): void {
		if (this.cur) {
			this.cur.points.push([x, y]);
		} else {
			this.moveTo(x, y);
		}
	}
	closePath(): void {
		if (this.cur) {
			this.cur.closed = true;
		}
		this.cur = null;
	}
	arc(): void {}
	take(): Line[] {
		const out = this.lines.filter((l) => l.points.length > 1);
		this.lines = [];
		this.cur = null;
		return out;
	}
}

const num = (v: number) => {
	const r = Math.round(v * 100) / 100;
	return Object.is(r, -0) ? '0' : String(r);
};

/** An SVG path string from lines (2 decimals). */
export const linesToPath = (lines: readonly Line[]): string => {
	const parts: string[] = [];
	for (const l of lines) {
		const p = l.points;
		if (p.length < 2) {
			continue;
		}
		parts.push(`M${num(p[0][0])},${num(p[0][1])}`);
		for (let i = 1; i < p.length; i++) {
			parts.push(`L${num(p[i][0])},${num(p[i][1])}`);
		}
		if (l.closed) {
			parts.push('Z');
		}
	}
	return parts.join('');
};

export type Box = [number, number, number, number]; // x0, y0, x1, y1

export const boundsOf = (lines: readonly Line[]): Box | null => {
	let x0 = Infinity;
	let y0 = Infinity;
	let x1 = -Infinity;
	let y1 = -Infinity;
	for (const l of lines) {
		for (const [x, y] of l.points) {
			if (x < x0) x0 = x;
			if (y < y0) y0 = y;
			if (x > x1) x1 = x;
			if (y > y1) y1 = y;
		}
	}
	return Number.isFinite(x0) ? [x0, y0, x1, y1] : null;
};

export const unionBox = (a: Box | null, b: Box | null): Box | null =>
	!a ? b : !b ? a : [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])];

export const boxesOverlap = (a: Box, b: Box): boolean => a[0] <= b[2] && b[0] <= a[2] && a[1] <= b[3] && b[1] <= a[3];

const segLen = (a: Pt, b: Pt) => Math.hypot(b[0] - a[0], b[1] - a[1]);

export const lineLength = (pts: readonly Pt[]): number => {
	let s = 0;
	for (let i = 1; i < pts.length; i++) {
		s += segLen(pts[i - 1], pts[i]);
	}
	return s;
};

/** The first `f` (0 to 1) of a polyline by length, and the direction at its end (radians). */
export const slicePolyline = (pts: readonly Pt[], f: number): {points: Pt[]; angle: number; end: Pt} => {
	if (pts.length === 0) {
		return {points: [], angle: 0, end: [0, 0]};
	}
	const total = lineLength(pts);
	const want = Math.max(0, Math.min(1, f)) * total;
	const out: Pt[] = [pts[0]];
	let acc = 0;
	let angle = pts.length > 1 ? Math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]) : 0;
	for (let i = 1; i < pts.length; i++) {
		const a = pts[i - 1];
		const b = pts[i];
		const l = segLen(a, b);
		if (l > 1e-9) {
			angle = Math.atan2(b[1] - a[1], b[0] - a[0]);
		}
		if (acc + l >= want) {
			const t = l > 1e-9 ? (want - acc) / l : 0;
			const end: Pt = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
			out.push(end);
			return {points: out, angle, end};
		}
		out.push(b);
		acc += l;
	}
	return {points: out, angle, end: out[out.length - 1]};
};

/** Every line cut to the same fraction of its own length: rings of a country all finish together. */
export const sliceLines = (lines: readonly Line[], f: number): Line[] => {
	if (f >= 1) {
		return lines as Line[];
	}
	if (f <= 0) {
		return [];
	}
	return lines.map((l) => {
		const pts = l.closed ? [...l.points, l.points[0]] : l.points;
		return {points: slicePolyline(pts, f).points, closed: false};
	});
};

/** Points along the great circle from a to b (lon/lat degrees), `n` segments. */
export const greatCircle = (a: LonLat, b: LonLat, n = 64): LonLat[] => {
	const ip = geoInterpolate(a, b);
	const out: LonLat[] = [];
	for (let i = 0; i <= n; i++) {
		out.push(ip(i / n) as LonLat);
	}
	return out;
};

/**
 * A line of latitude as GeoJSON, with a point every `step` degrees. d3 joins the points of a LineString by great
 * circles, so a parallel given by its two ends alone bows towards the pole; dense points keep it on the parallel.
 */
export const parallelLine = (lat: number, west: number, east: number, step = 0.5): GeoJSON.Feature<GeoJSON.LineString> => {
	const e = east < west ? east + 360 : east;
	const n = Math.max(2, Math.ceil((e - west) / step));
	const coordinates: GeoJSON.Position[] = [];
	for (let i = 0; i <= n; i++) {
		const lon = west + ((e - west) * i) / n;
		coordinates.push([lon > 180 ? lon - 360 : lon, lat]);
	}
	return {type: 'Feature', properties: {}, geometry: {type: 'LineString', coordinates}};
};

/** A circle of `km` around a place, as a GeoJSON polygon (wound the way d3 expects). */
export const circleKm = (center: LonLat, km: number, step = 2): GeoJSON.Feature<GeoJSON.Polygon> => ({
	type: 'Feature',
	properties: {},
	geometry: geoCircle().center(center).radius((km / EARTH_KM) * (180 / Math.PI)).precision(step)(),
});

export const EARTH_KM = 6371.0088;

/** Great-circle distance in km. */
export const distanceKm = (a: LonLat, b: LonLat): number => geoDistance(a, b) * EARTH_KM;

/** Central angle between two points in degrees. */
export const angleDeg = (a: LonLat, b: LonLat): number => (geoDistance(a, b) * 180) / Math.PI;

// ----------------------------------------------------------------------------------------- the zoom path

export type View = [number, number, number]; // centre x, centre y, visible width (plate units)

/**
 * The smooth path between two views (van Wijk and Nuij 2003): it zooms out as far as a long pan needs and back
 * in, at a steady perceived speed. `rho` sets how much it rises (sqrt 2 is the paper's value; 1 is flatter).
 * Returns the path length S (for timing) and the view at t in [0, 1].
 */
export const zoomPath = (a: View, b: View, rho = Math.SQRT2): {S: number; at: (t: number) => View} => {
	const [ux0, uy0, w0] = a;
	const [ux1, uy1, w1] = b;
	const dx = ux1 - ux0;
	const dy = uy1 - uy0;
	const d2 = dx * dx + dy * dy;
	const r2 = rho * rho;
	const r4 = r2 * r2;
	if (d2 < 1e-12 || w0 <= 0 || w1 <= 0) {
		const S = Math.log(Math.max(w1, 1e-9) / Math.max(w0, 1e-9)) / rho;
		return {
			S: Math.abs(S),
			at: (t) => [ux0 + t * dx, uy0 + t * dy, w0 * Math.exp(rho * t * S)],
		};
	}
	const d1 = Math.sqrt(d2);
	const b0 = (w1 * w1 - w0 * w0 + r4 * d2) / (2 * w0 * r2 * d1);
	const b1 = (w1 * w1 - w0 * w0 - r4 * d2) / (2 * w1 * r2 * d1);
	const r0 = Math.log(Math.sqrt(b0 * b0 + 1) - b0);
	const r1 = Math.log(Math.sqrt(b1 * b1 + 1) - b1);
	const S = (r1 - r0) / rho;
	return {
		S,
		at: (t) => {
			const s = t * S;
			const c0 = Math.cosh(r0);
			const u = (w0 / (r2 * d1)) * (c0 * Math.tanh(rho * s + r0) - Math.sinh(r0));
			return [ux0 + u * dx, uy0 + u * dy, (w0 * c0) / Math.cosh(rho * s + r0)];
		},
	};
};

// ----------------------------------------------------------------------------------------- country shape facts

/** Spherical area of each polygon of a feature. */
export const polygonAreas = (f: CountryFeature): number[] =>
	polygonsOf(f).map((rings) => geoArea({type: 'Polygon', coordinates: rings}));

/**
 * The part of a country a camera should frame: its largest polygon and the polygons close to it (islands and
 * archipelagos chain in; far territories such as French Guiana, Alaska or the Canaries stay out).
 */
export const mainPolygons = (f: CountryFeature): GeoJSON.Position[][][] => {
	const polys = polygonsOf(f);
	if (polys.length <= 1) {
		return polys;
	}
	const areas = polys.map((rings) => geoArea({type: 'Polygon', coordinates: rings}));
	const boxes = polys.map((rings) => geoBounds({type: 'Polygon', coordinates: rings}));
	let seed = 0;
	for (let i = 1; i < polys.length; i++) {
		if (areas[i] > areas[seed]) seed = i;
	}
	const lat0 = ((boxes[seed][0][1] + boxes[seed][1][1]) / 2) * (Math.PI / 180);
	const kx = Math.max(0.2, Math.cos(lat0));
	const local: (Box | null)[] = boxes.map((b) => (b[1][0] < b[0][0] ? null : [b[0][0] * kx, b[0][1], b[1][0] * kx, b[1][1]]));
	const keep = clusterBoxes(local, areas, seed, 1);
	return polys.filter((_, i) => keep.has(i));
};

/**
 * Grows a cluster from the `seed` box: a part joins when it is near (a gap under 2.2 degrees plus 5% of the
 * cluster size) or when it is a big sibling (a quarter of the seed's area or more) within 0.8 cluster sizes.
 * `perDegree` converts degrees to the boxes' units. Null boxes never join.
 */
export const clusterBoxes = (boxes: readonly (Box | null)[], areas: readonly number[], seed: number, perDegree: number): Set<number> => {
	const inCluster = new Set<number>([seed]);
	let box = boxes[seed];
	if (!box) {
		return inCluster;
	}
	let grew = true;
	while (grew) {
		grew = false;
		const size = Math.hypot(box[2] - box[0], box[3] - box[1]);
		const near = 2.2 * perDegree + 0.05 * size;
		const sibling = 0.8 * size;
		for (let i = 0; i < boxes.length; i++) {
			const b = boxes[i];
			if (!b || inCluster.has(i) || areas[i] < areas[seed] * 1e-5) {
				continue;
			}
			const dx = Math.max(0, box[0] - b[2], b[0] - box[2]);
			const dy = Math.max(0, box[1] - b[3], b[1] - box[3]);
			const gap = Math.hypot(dx, dy);
			if (gap <= near || (areas[i] >= areas[seed] * 0.25 && gap <= sibling)) {
				inCluster.add(i);
				box = unionBox(box, b) as Box;
				grew = true;
			}
		}
	}
	return inCluster;
};

export type Anchor = {lonlat: LonLat; radiusDeg: number};

/**
 * Where a country's name goes: the pole of inaccessibility (the point farthest inside) of its largest polygon,
 * found in a local equal-scale frame. Centroids fall on edges or outside (Chile, Indonesia); this does not.
 */
export const labelAnchor = (f: CountryFeature): Anchor => {
	const polys = polygonsOf(f);
	const areas = polys.map((rings) => geoArea({type: 'Polygon', coordinates: rings}));
	let best = 0;
	for (let i = 1; i < polys.length; i++) {
		if (areas[i] > areas[best]) best = i;
	}
	const rings = polys[best];
	const c = geoCentroid({type: 'Polygon', coordinates: rings});
	const kx = Math.max(0.15, Math.cos((c[1] * Math.PI) / 180));
	const local = rings.map((ring) => ring.map((p) => [p[0] * kx, p[1]] as [number, number]));
	const b = geoBounds({type: 'Polygon', coordinates: rings});
	const size = Math.max((b[1][0] - b[0][0]) * kx, b[1][1] - b[0][1], 0.01);
	const pole = polylabel(local, size / 400);
	return {lonlat: [pole[0] / kx, pole[1]], radiusDeg: pole.distance};
};

/** The lon/lat bounding box of the main polygons, as [[west, south], [east, north]]. */
export const mainBounds = (f: CountryFeature): [LonLat, LonLat] => {
	const b = geoBounds({type: 'MultiPolygon', coordinates: mainPolygons(f)});
	return [b[0] as LonLat, b[1] as LonLat];
};

/** The centre of a country's main body (for globes and conic projections). */
export const mainCentroid = (f: CountryFeature): LonLat => geoCentroid({type: 'MultiPolygon', coordinates: mainPolygons(f)}) as LonLat;

/** Turns country rings into lines, so clipping at the map edge or the globe horizon never closes a ring. */
export const ringsAsLines = (polys: GeoJSON.Position[][][]): GeoJSON.MultiLineString => ({
	type: 'MultiLineString',
	coordinates: polys.flatMap((rings) => rings),
});
