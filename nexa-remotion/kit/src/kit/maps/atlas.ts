// The world data: Natural Earth admin 0 countries from world-atlas, at three levels of detail. 110m and 50m are
// bundled; 10m (3.6 MB) is loaded only when a map needs it (useAtlas10m), behind delayRender.
import {geoArea} from 'd3-geo';
import {useEffect, useRef, useState} from 'react';
import {useDelayRender} from 'remotion';
import {feature, mesh} from 'topojson-client';
import type {GeometryCollection, GeometryObject, Topology} from 'topojson-specification';
import w110 from 'world-atlas/countries-110m.json';
import w50 from 'world-atlas/countries-50m.json';
import {requireCountryKey, type CountryRef} from './countries';

export type Detail = '110m' | '50m' | '10m';
export type LonLat = [number, number];

type CountryProps = {name: string};
type CountriesTopology = Topology<{countries: GeometryCollection<CountryProps>; land: GeometryCollection}>;
type CountryGeometry = GeometryObject<CountryProps> & {id?: string | number};
export type CountryFeature = GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon, CountryProps>;

export type Atlas = {
	detail: Detail;
	keys: string[]; // country keys in data order
	feature: (key: string) => CountryFeature | null; // merged feature of a key, cached
	borders: (key: string) => GeoJSON.MultiLineString; // interior borders this country owns, cached
	coast: (key: string) => GeoJSON.MultiLineString; // its coastline, cached
};

const nameOf = (g: CountryGeometry): string => ((g.properties ?? {}) as Partial<CountryProps>).name ?? '';

const rawKey = (g: CountryGeometry): string =>
	g.id !== undefined && g.id !== null && g.id !== '' ? String(g.id).padStart(3, '0') : `n:${nameOf(g)}`;

const build = (detail: Detail, topology: CountriesTopology): Atlas => {
	const collection = topology.objects.countries as GeometryCollection<CountryProps>;
	const all = collection.geometries as CountryGeometry[];
	const keyOf = new Map<GeometryObject, string>();
	const geometries = new Map<string, CountryGeometry[]>();
	for (const g of all) {
		const k = rawKey(g);
		keyOf.set(g, k);
		const list = geometries.get(k) ?? [];
		list.push(g);
		geometries.set(k, list);
	}
	const order = new Map<string, number>([...geometries.keys()].map((k, i) => [k, i]));
	const featureCache = new Map<string, CountryFeature | null>();
	const borderCache = new Map<string, GeoJSON.MultiLineString>();
	const coastCache = new Map<string, GeoJSON.MultiLineString>();

	const featureOf = (key: string): CountryFeature | null => {
		const hit = featureCache.get(key);
		if (hit !== undefined) {
			return hit;
		}
		const gs = geometries.get(key);
		let f: CountryFeature | null = null;
		if (gs && gs.length) {
			const polys: GeoJSON.Position[][][] = [];
			for (const g of gs) {
				const one = feature(topology, g as GeometryObject<CountryProps>) as GeoJSON.Feature<GeoJSON.Geometry | null, CountryProps>;
				const geom = one.geometry;
				const parts = geom?.type === 'Polygon' ? [geom.coordinates] : geom?.type === 'MultiPolygon' ? geom.coordinates : [];
				for (const rings of parts) {
					// a ring wound the wrong way means "the whole Earth except this": 10m has three such slivers
					// (Maldives atolls). Drawn, they cover everything, so they are dropped.
					if (geoArea({type: 'Polygon', coordinates: rings}) <= 2 * Math.PI) {
						polys.push(rings);
					}
				}
			}
			if (polys.length) {
				f = {
					type: 'Feature',
					properties: {name: nameOf(gs[0]) || key},
					geometry: polys.length === 1 ? {type: 'Polygon', coordinates: polys[0]} : {type: 'MultiPolygon', coordinates: polys},
				};
			}
		}
		featureCache.set(key, f);
		return f;
	};

	// Each shared border belongs to exactly one of its two countries (the one first in the data), so it is
	// drawn once however the countries are culled.
	const bordersOf = (key: string): GeoJSON.MultiLineString => {
		const hit = borderCache.get(key);
		if (hit) {
			return hit;
		}
		const m = mesh(topology, collection, (a, b) => {
			const ka = keyOf.get(a) ?? '';
			const kb = keyOf.get(b) ?? '';
			if (ka === kb || (ka !== key && kb !== key)) {
				return false;
			}
			const first = (order.get(ka) ?? 0) <= (order.get(kb) ?? 0) ? ka : kb;
			return first === key;
		});
		borderCache.set(key, m);
		return m;
	};

	const coastOf = (key: string): GeoJSON.MultiLineString => {
		const hit = coastCache.get(key);
		if (hit) {
			return hit;
		}
		const m = mesh(topology, collection, (a, b) => a === b && keyOf.get(a) === key);
		coastCache.set(key, m);
		return m;
	};

	return {detail, keys: [...geometries.keys()], feature: featureOf, borders: bordersOf, coast: coastOf};
};

const cache = new Map<Detail, Atlas>();

/** The atlas for a bundled level (110m or 50m); the 10m one once useAtlas10m() has loaded it. */
export const atlas = (detail: Detail): Atlas => {
	const hit = cache.get(detail);
	if (hit) {
		return hit;
	}
	if (detail === '10m') {
		throw new Error('maps: the 10m data loads on demand; the map components call useAtlas10m() before they use it.');
	}
	const a = build(detail, (detail === '110m' ? w110 : w50) as unknown as CountriesTopology);
	cache.set(detail, a);
	return a;
};

/** The atlas at a level if it is available now (10m only after it has loaded in this tab). */
export const loadedAtlas = (detail: Detail): Atlas | null => (detail === '10m' ? cache.get('10m') ?? null : atlas(detail));

let pending10m: Promise<Atlas> | null = null;

const load10m = (): Promise<Atlas> => {
	if (!pending10m) {
		pending10m = import('world-atlas/countries-10m.json').then((m) => {
			const topo = ((m as {default?: unknown}).default ?? m) as unknown as CountriesTopology;
			const a = build('10m', topo);
			cache.set('10m', a);
			return a;
		});
	}
	return pending10m;
};

/**
 * Loads the 10m data when `needed` and holds the render until it is ready. Returns the atlas (null while loading
 * or when not needed). Every map may call it: the file is fetched once per tab.
 */
export const useAtlas10m = (needed: boolean): Atlas | null => {
	const {delayRender, continueRender, cancelRender} = useDelayRender();
	const [loaded, setLoaded] = useState<Atlas | null>(() => cache.get('10m') ?? null);
	const [handle] = useState<number | null>(() =>
		needed && !cache.get('10m') ? delayRender('maps: loading the 10m world data', {timeoutInMilliseconds: 60000}) : null,
	);
	const released = useRef(false);
	useEffect(() => {
		if (!needed || loaded) {
			return;
		}
		let alive = true;
		load10m()
			.then((a) => {
				if (alive) {
					setLoaded(a);
				}
				if (handle !== null && !released.current) {
					released.current = true;
					continueRender(handle);
				}
			})
			.catch((err: unknown) => cancelRender(err instanceof Error ? err : new Error(String(err))));
		return () => {
			alive = false;
		};
	}, [needed, loaded, handle, continueRender, cancelRender]);
	return needed ? loaded : null;
};

/** The merged feature of a country at a level (50m when 10m is not loaded), or null when the level lacks it. */
export const countryFeature = (ref: CountryRef, detail: Detail = '50m'): CountryFeature | null => {
	const a = loadedAtlas(detail) ?? atlas('50m');
	return a.feature(requireCountryKey(ref));
};

/** The polygons of a feature (a Polygon becomes a list of one). */
export const polygonsOf = (f: CountryFeature): GeoJSON.Position[][][] =>
	f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;

/** Area of a country in km2 from its outline (Natural Earth 50m). */
export const countryAreaKm2 = (ref: CountryRef): number => {
	const f = countryFeature(ref, '50m');
	return f ? geoArea(f) * 6371.0088 ** 2 : 0;
};
