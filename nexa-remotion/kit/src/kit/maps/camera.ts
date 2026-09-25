// The flat-map camera: keys say what to frame (the world, countries, points, a box, or a centre and zoom) and when;
// between keys the view travels on the smooth zoom path (it rises for long pans), eased in and out.
import {curves, type Ease, type Rect} from '../core';
import type {LonLat} from './atlas';
import {requireCountryKey, type CountryRef} from './countries';
import {unionBox, zoomPath, type Box, type View} from './geo';
import type {Plate} from './plate';

export type MapKey = {
	at: number; // frame
	fit?: 'world' | CountryRef | CountryRef[]; // countries are framed by their main body (no far territories)
	points?: LonLat[]; // frame these places
	bbox?: [LonLat, LonLat]; // [[west, south], [east, north]]
	center?: LonLat; // with zoom: 1 is the whole world
	zoom?: number;
	padding?: number; // share of the area left around the subject on each side (default 0.14, world 0)
	area?: Rect; // the part of the map box to frame into, real px like useStage().safe (default the whole box): leave room for text
	ease?: Ease; // curve of the move that arrives at this key (default ease in-out)
};

const MAX_ZOOM = 80;

const fitBox = (box: Box, area: Rect, pad: number, W: number, H: number, minSize: number): View => {
	const bw = Math.max(box[2] - box[0], minSize);
	const bh = Math.max(box[3] - box[1], minSize);
	const k = Math.min(MAX_ZOOM, (area.w * (1 - 2 * pad)) / bw, (area.h * (1 - 2 * pad)) / bh);
	const bx = (box[0] + box[2]) / 2;
	const by = (box[1] + box[3]) / 2;
	const cx = bx - (area.x + area.w / 2 - W / 2) / k;
	const cy = by - (area.y + area.h / 2 - H / 2) / k;
	return [cx, cy, W / k];
};

const pointsBox = (plate: Plate, pts: readonly LonLat[]): Box | null => {
	let box: Box | null = null;
	for (const c of pts) {
		const p = plate.project(c);
		if (p) {
			box = unionBox(box, [p[0], p[1], p[0], p[1]]);
		}
	}
	return box;
};

/** The view (centre and visible width in plate units) a key asks for. */
export const resolveView = (key: MapKey, plate: Plate, W: number, H: number): View => {
	const area = key.area ?? {x: 0, y: 0, w: W, h: H};
	const minSize = plate.ppd * 1.5; // never frame less than about 1.5 degrees
	if (key.center) {
		const p = plate.project(key.center) ?? [W / 2, H / 2];
		const k = Math.min(MAX_ZOOM, Math.max(0.2, key.zoom ?? 4));
		return [p[0] - (area.x + area.w / 2 - W / 2) / k, p[1] - (area.y + area.h / 2 - H / 2) / k, W / k];
	}
	if (key.points && key.points.length) {
		const b = pointsBox(plate, key.points);
		if (b) {
			return fitBox(b, area, key.padding ?? 0.18, W, H, minSize);
		}
	}
	if (key.bbox) {
		const [[w, s], [e, n]] = key.bbox;
		const east = e < w ? e + 360 : e;
		const pts: LonLat[] = [];
		for (let i = 0; i <= 8; i++) {
			const lon = w + ((east - w) * i) / 8;
			const L = lon > 180 ? lon - 360 : lon;
			pts.push([L, s], [L, n], [L, (s + n) / 2]);
		}
		const b = pointsBox(plate, pts);
		if (b) {
			return fitBox(b, area, key.padding ?? 0.06, W, H, minSize);
		}
	}
	const fit = key.fit ?? 'world';
	if (fit !== 'world') {
		const refs = Array.isArray(fit) ? fit : [fit];
		let box: Box | null = null;
		for (const r of refs) {
			box = unionBox(box, plate.mainBox(requireCountryKey(r)));
		}
		if (box) {
			return fitBox(box, area, key.padding ?? 0.14, W, H, minSize);
		}
	}
	if (!key.area && !key.padding) {
		return [W / 2, H / 2, W]; // zoom 1: the plate as fitted, padding included
	}
	return fitBox(plate.world, area, key.padding ?? 0, W, H, minSize);
};

export type ResolvedKey = {at: number; view: View; ease: Ease};

export const resolveKeys = (keys: readonly MapKey[] | undefined, plate: Plate, W: number, H: number): ResolvedKey[] => {
	const list = keys && keys.length ? [...keys] : [{at: 0, fit: 'world' as const}];
	return list
		.sort((a, b) => a.at - b.at)
		.map((k) => ({at: k.at, view: resolveView(k, plate, W, H), ease: k.ease ?? curves.inOut}));
};

/** The view at a frame: held before the first key and after the last, on the zoom path in between. */
export const viewAt = (frame: number, keys: readonly ResolvedKey[], rho: number): View => {
	if (keys.length === 0) {
		return [0, 0, 1];
	}
	if (frame <= keys[0].at) {
		return keys[0].view;
	}
	for (let i = 0; i < keys.length - 1; i++) {
		const a = keys[i];
		const b = keys[i + 1];
		if (frame < b.at) {
			const span = b.at - a.at;
			const t = span > 0 ? b.ease(Math.min(1, Math.max(0, (frame - a.at) / span))) : 1;
			const same = Math.abs(a.view[0] - b.view[0]) < 1e-6 && Math.abs(a.view[1] - b.view[1]) < 1e-6 && Math.abs(a.view[2] - b.view[2]) < 1e-9;
			return same ? a.view : zoomPath(a.view, b.view, rho).at(t);
		}
	}
	return keys[keys.length - 1].view;
};

/** The largest zoom (screen px per plate unit at zoom 1 = 1) any key reaches. */
export const maxZoom = (keys: readonly ResolvedKey[], W: number): number => Math.max(1, ...keys.map((k) => W / k.view[2]));
