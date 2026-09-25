// The plate: the world projected once into a fixed coordinate space the size of the map box, with the whole world
// fitted at zoom 1. Country paths are built once per plate and level and reused every frame; the camera only
// changes the SVG viewBox, so vectors are redrawn sharp at any zoom and nothing is re-projected per frame.
import {geoGraticule10, geoPath, type GeoPermissibleObjects, type GeoProjection} from 'd3-geo';
import {atlas, loadedAtlas, type Detail, type LonLat} from './atlas';
import {requireCountryKey, type CountryRef} from './countries';
import {boundsOf, clusterBoxes, labelAnchor, linesToPath, makeProjection, Recorder, type Anchor, type Box, type Line, type ProjectionName} from './geo';

export type OceanMode = 'sphere' | 'frame';

export type PlateOptions = {
	projection: ProjectionName;
	width: number;
	height: number;
	ocean: OceanMode;
	antarctica: boolean;
	padding: number; // px around the world at zoom 1
	meridian: number; // central meridian in degrees (150 or 180 centres the Pacific)
};

export type Shape = {d: string; box: Box; lines: Line[]; area: number};

export type Plate = {
	opts: PlateOptions;
	projection: GeoProjection;
	world: Box; // the world at zoom 1, in plate units
	ppd: number; // plate units per degree of longitude along the equator
	worldWidth: number; // plate x span of 360 degrees
	sphere: string;
	graticule: string;
	project: (c: LonLat) => [number, number] | null;
	shape: (detail: Detail, key: string) => Shape | null;
	borders: (detail: Detail, key: string) => string;
	coast: (detail: Detail, key: string) => string;
	outline: (detail: Detail, key: string) => Line[]; // rings as open lines (for draw-ons)
	mainBox: (key: string) => Box | null; // the main body of a country (50m), for framing
	keys: (detail: Detail) => string[];
};

const ringArea = (pts: readonly [number, number][]): number => {
	let s = 0;
	for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
		s += (pts[j][0] + pts[i][0]) * (pts[j][1] - pts[i][1]);
	}
	return Math.abs(s / 2);
};

const plates = new Map<string, Plate>();

const fitObject = (opts: PlateOptions): GeoPermissibleObjects => {
	if (opts.ocean === 'sphere') {
		return {type: 'Sphere'};
	}
	// the land extent: the whole width, and from the southern capes (or the pole) to northern Greenland
	const south = opts.antarctica ? -85 : -57;
	const north = 83.7;
	const pts: LonLat[] = [];
	for (let lon = -180; lon <= 180; lon += 5) {
		pts.push([lon, south], [lon, 0], [lon, north]);
	}
	return {type: 'MultiPoint', coordinates: pts};
};

export const getPlate = (opts: PlateOptions): Plate => {
	const id = `${opts.projection}|${Math.round(opts.width)}|${Math.round(opts.height)}|${opts.ocean}|${opts.antarctica}|${Math.round(opts.padding)}|${opts.meridian}`;
	const hit = plates.get(id);
	if (hit) {
		return hit;
	}
	const {width, height, padding} = opts;
	const projection = makeProjection(opts.projection)
		.rotate([-opts.meridian, 0])
		.precision(0.1)
		.fitExtent(
			[
				[padding, padding],
				[width - padding, height - padding],
			],
			fitObject(opts),
		);
	const rec = new Recorder();
	const path = geoPath(projection, rec);
	const toStr = geoPath(projection);
	toStr.digits(2);

	const wb = geoPath(projection).bounds(fitObject(opts));
	const world: Box = [wb[0][0], wb[0][1], wb[1][0], wb[1][1]];
	const eq0 = projection([opts.meridian - 179.999, 0]);
	const eq1 = projection([opts.meridian + 179.999, 0]);
	const worldWidth = eq0 && eq1 ? Math.abs(eq1[0] - eq0[0]) : world[2] - world[0];

	const shapes = new Map<string, Shape | null>();
	const borderPaths = new Map<string, string>();
	const coastPaths = new Map<string, string>();
	const outlines = new Map<string, Line[]>();
	const mainBoxes = new Map<string, Box | null>();

	const levelAtlas = (detail: Detail) => loadedAtlas(detail) ?? atlas('50m');

	const shape = (detail: Detail, key: string): Shape | null => {
		const a = levelAtlas(detail);
		const k = `${a.detail}|${key}`;
		const cached = shapes.get(k);
		if (cached !== undefined) {
			return cached;
		}
		const f = a.feature(key);
		let s: Shape | null = null;
		if (f) {
			path(f);
			const lines = rec.take();
			const box = boundsOf(lines);
			if (box) {
				s = {d: linesToPath(lines), box, lines, area: lines.reduce((acc, l) => acc + ringArea(l.points), 0)};
			}
		}
		shapes.set(k, s);
		return s;
	};

	const lineString = (cache: Map<string, string>, detail: Detail, key: string, pick: 'borders' | 'coast') => {
		const a = levelAtlas(detail);
		const k = `${a.detail}|${key}`;
		const cached = cache.get(k);
		if (cached !== undefined) {
			return cached;
		}
		const d = toStr(pick === 'borders' ? a.borders(key) : a.coast(key)) ?? '';
		cache.set(k, d);
		return d;
	};

	const outline = (detail: Detail, key: string): Line[] => {
		const a = levelAtlas(detail);
		const k = `${a.detail}|${key}`;
		const cached = outlines.get(k);
		if (cached) {
			return cached;
		}
		const f = a.feature(key);
		let lines: Line[] = [];
		if (f) {
			const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
			path({type: 'MultiLineString', coordinates: polys.flatMap((r) => r)});
			lines = rec.take();
		}
		outlines.set(k, lines);
		return lines;
	};

	const ppd = worldWidth / 360;

	const mainBox = (key: string): Box | null => {
		const cached = mainBoxes.get(key);
		if (cached !== undefined) {
			return cached;
		}
		const s = shape('50m', key);
		let box: Box | null = null;
		if (s) {
			// cluster the projected rings: the largest ring and what sits close to it
			const rings = s.lines.filter((l) => l.closed);
			const boxes = rings.map((l) => boundsOf([l]));
			const areas = rings.map((l) => ringArea(l.points));
			let seed = 0;
			for (let i = 1; i < rings.length; i++) {
				if (areas[i] > areas[seed]) seed = i;
			}
			if (rings.length) {
				const keep = clusterBoxes(boxes, areas, seed, ppd);
				for (const i of keep) {
					const b = boxes[i];
					if (b) {
						box = box ? [Math.min(box[0], b[0]), Math.min(box[1], b[1]), Math.max(box[2], b[2]), Math.max(box[3], b[3])] : b;
					}
				}
			}
			box = box ?? s.box;
		}
		mainBoxes.set(key, box);
		return box;
	};

	const plate: Plate = {
		opts,
		projection,
		world,
		ppd,
		worldWidth,
		sphere: toStr({type: 'Sphere'}) ?? '',
		graticule: toStr(geoGraticule10()) ?? '',
		project: (c) => projection(c) as [number, number] | null,
		shape,
		borders: (detail, key) => lineString(borderPaths, detail, key, 'borders'),
		coast: (detail, key) => lineString(coastPaths, detail, key, 'coast'),
		outline,
		mainBox,
		keys: (detail) => levelAtlas(detail).keys.filter((k) => opts.antarctica || k !== '010'),
	};
	plates.set(id, plate);
	return plate;
};

const anchors = new Map<string, Anchor | null>();

/** The label anchor of a country (50m outline): lon/lat and the radius of the largest circle inside, degrees. */
export const countryAnchor = (ref: CountryRef): Anchor | null => {
	const key = requireCountryKey(ref);
	const hit = anchors.get(key);
	if (hit !== undefined) {
		return hit;
	}
	const f = atlas('50m').feature(key);
	const a = f ? labelAnchor(f) : null;
	anchors.set(key, a);
	return a;
};
