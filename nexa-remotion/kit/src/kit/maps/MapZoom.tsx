// <MapZoom>: the classic "from the world down to one place" move in one line. It is a WorldMap with two camera
// keys (hold on `from`, then travel to `to` on the smooth zoom path) and, when the target is a country, a
// highlight that lands as the camera settles.
import React from 'react';
import {at30, useStage, type Ease, type Rect} from '../core';
import type {LonLat} from './atlas';
import type {MapKey} from './camera';
import type {CountryRef} from './countries';
import {WorldMap, type HighlightSpec, type WorldMapProps} from './WorldMap';

export type ZoomTarget =
	| 'world'
	| CountryRef
	| CountryRef[]
	| {points: LonLat[]}
	| {bbox: [LonLat, LonLat]}
	| {center: LonLat; zoom: number};

export type MapZoomProps = Omit<WorldMapProps, 'camera'> & {
	to: ZoomTarget;
	from?: ZoomTarget; // default the world
	delay?: number; // frames held on `from` before the move (default 0.5 s)
	duration?: number; // frames of the move (default 2.4 s)
	padding?: number; // around the target (default 0.16)
	area?: Rect; // the part of the box to land the target in (leave room for a title)
	ease?: Ease;
	highlightTarget?: boolean | Omit<HighlightSpec, 'country'>; // default true when `to` is one country
};

const toKey = (target: ZoomTarget, at: number, padding: number | undefined, area: Rect | undefined, ease?: Ease): MapKey => {
	if (target === 'world') {
		return {at, fit: 'world', ease};
	}
	if (typeof target === 'object' && !Array.isArray(target)) {
		return {at, padding, area, ease, ...target};
	}
	return {at, fit: target, padding, area, ease};
};

export const MapZoom: React.FC<MapZoomProps> = ({to, from = 'world', delay, duration, padding = 0.16, area, ease, highlightTarget = true, highlight, ...rest}) => {
	const {fps} = useStage();
	const hold = delay ?? Math.round(0.5 * fps);
	const move = duration ?? Math.round(2.4 * fps);
	const camera: MapKey[] = [toKey(from, 0, padding, undefined), toKey(from, hold, padding, undefined), toKey(to, hold + move, padding, area, ease)];
	const single = typeof to === 'string' || typeof to === 'number';
	const extra: HighlightSpec[] =
		single && to !== 'world' && highlightTarget
			? [{country: to as CountryRef, delay: hold + Math.round(move * 0.62), draw: at30(30, fps), ...(typeof highlightTarget === 'object' ? highlightTarget : {})}]
			: [];
	const given: HighlightSpec[] = highlight === undefined ? [] : (Array.isArray(highlight) ? highlight : [highlight]).map((h) => (typeof h === 'object' && h !== null && 'country' in h ? (h as HighlightSpec) : {country: h as CountryRef}));
	return <WorldMap {...rest} camera={camera} highlight={[...extra, ...given]} />;
};
