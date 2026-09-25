// What a map shares with the things drawn on it (pins, routes, labels): how to turn lon/lat into pixels this
// frame, its size, safe area and colours. WorldMap and Globe provide it; useMap() reads it.
import type {GeoProjection} from 'd3-geo';
import {createContext, useContext} from 'react';
import type {Rect} from '../core';
import type {Detail, LonLat} from './atlas';
import type {MapPalette} from './color';
import type {CountryRef} from './countries';

export type Projected = {
	x: number;
	y: number;
	/** 1 fully visible, 0 hidden (behind the globe); in between near the globe's edge. */
	visible: number;
};

export type MapApi = {
	kind: 'flat' | 'globe';
	width: number; // map box, px
	height: number;
	safe: Rect; // where labels must stay, in box px
	unit: number;
	palette: MapPalette;
	detail: Detail;
	/** lon/lat (and an altitude as a fraction of the globe radius) to box pixels this frame. */
	project: (c: LonLat, altitude?: number) => Projected;
	/** The same for another frame of the map's timeline (to decide layouts once, before a camera move). */
	projectAt: (frame: number) => (c: LonLat, altitude?: number) => Projected;
	/** Screen px per degree of longitude at the view centre: how zoomed in the map is. */
	pxPerDeg: number;
	/** This frame's d3 projection into box px: geoPath(map.projection)(anyGeoJSON) draws your own data. */
	projection: GeoProjection;
	/** The screen box of a country's main body, this frame or at another frame (null when off the map). */
	countryBox: (ref: CountryRef, frame?: number) => {x0: number; y0: number; x1: number; y1: number} | null;
	/** The globe: centre and radius in px, and the view centre in lon/lat. */
	globe?: {cx: number; cy: number; r: number; center: LonLat};
};

export const MapContext = createContext<MapApi | null>(null);

/** The map this component sits in. Throws outside a WorldMap or Globe. */
export const useMap = (): MapApi => {
	const m = useContext(MapContext);
	if (!m) {
		throw new Error('maps: Pin, Route and the labels must be placed inside <WorldMap>, <MapZoom>, <Choropleth> or <Globe>.');
	}
	return m;
};
