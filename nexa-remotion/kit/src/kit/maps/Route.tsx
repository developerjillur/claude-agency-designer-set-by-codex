// <Route>: a trip drawn over time along great circles, leg after leg, with a plane (or a dot) turned along the
// path, an optional ghost of the whole route, and pins that land at each stop as the plane arrives. Works on a flat
// map (the arc gets a little lift so short hops still read as flights) and on a globe (the arc rises off the
// surface and hides behind the horizon).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, type Ease} from '../core';
import {ramp} from '../motion';
import type {LonLat} from './atlas';
import {withAlpha} from './color';
import {useMap, type MapApi} from './context';
import {angleDeg, distanceKm, greatCircle} from './geo';
import type {MapKey} from './camera';
import {Pin, type PinProps} from './Pin';
import type {Side} from './Labels';

export type RouteStop = {at: LonLat; label?: string; sub?: string; side?: Side};

export type Leg = {from: LonLat; to: LonLat; start: number; end: number; angle: number; km: number};

const asStop = (s: LonLat | RouteStop): RouteStop => (Array.isArray(s) ? {at: s as LonLat} : (s as RouteStop));

/** Frames a flight of `angle` degrees takes by default: about 1.1 s for a short hop, 2.3 s across a continent. */
export const legFrames = (angle: number, fps: number): number => Math.round(fps * (0.9 + 1.4 * Math.sqrt(Math.max(0, angle) / 90)));

/**
 * When each leg flies: legs follow each other with `dwell` frames on the ground between them. Use the same
 * options as the Route so a camera or a counter can follow it.
 */
export const legSchedule = (
	stops: readonly (LonLat | RouteStop)[],
	fps: number,
	opts: {delay?: number; legDuration?: number | number[]; dwell?: number} = {},
): Leg[] => {
	const pts = stops.map((s) => asStop(s).at);
	const dwell = opts.dwell ?? at30(14, fps);
	let t = opts.delay ?? 0;
	const legs: Leg[] = [];
	for (let i = 0; i < pts.length - 1; i++) {
		const angle = angleDeg(pts[i], pts[i + 1]);
		const given = Array.isArray(opts.legDuration) ? opts.legDuration[i] : opts.legDuration;
		const d = Math.max(4, Math.round(given ?? legFrames(angle, fps)));
		legs.push({from: pts[i], to: pts[i + 1], start: t, end: t + d, angle, km: distanceKm(pts[i], pts[i + 1])});
		t += d + dwell;
	}
	return legs;
};

/** Where the traveller is at a frame: the leg, how far along it (0 to 1, eased like the Route) and km flown so far. */
export const routeProgress = (frame: number, legs: readonly Leg[], ease: Ease = curves.inOut): {leg: number; t: number; km: number} => {
	let km = 0;
	for (let i = 0; i < legs.length; i++) {
		const l = legs[i];
		if (frame < l.end || i === legs.length - 1) {
			const t = ease(Math.min(1, Math.max(0, (frame - l.start) / Math.max(1, l.end - l.start))));
			return {leg: i, t, km: km + l.km * t};
		}
		km += l.km;
	}
	return {leg: 0, t: 0, km: 0};
};

/**
 * Camera keys for a WorldMap that follow a route: each leg framed while it flies, the camera moving to the next
 * leg while the plane climbs out, and (overview > 0) the whole trip framed at the end.
 */
export const followCamera = (
	stops: readonly (LonLat | RouteStop)[],
	legs: readonly Leg[],
	opts: {padding?: number; overview?: number; area?: MapKey['area']; lift?: number} = {},
): MapKey[] => {
	// the leg's great circle plus the top of its lifted arc (the Route bends it poleward by `lift`)
	const lift = opts.lift ?? 0.14;
	const legPts = (l: Leg): LonLat[] => {
		const pts = greatCircle(l.from, l.to, 6);
		const mid = pts[3];
		const kx = Math.cos((mid[1] * Math.PI) / 180);
		const chord = Math.hypot((l.to[0] - l.from[0]) * kx, l.to[1] - l.from[1]);
		const pole = mid[1] >= 0 ? 1 : -1;
		return [...pts, [mid[0], Math.max(-85, Math.min(85, mid[1] + pole * lift * chord))]];
	};
	const keys: MapKey[] = [];
	const push = (k: MapKey) => {
		const last = keys[keys.length - 1];
		keys.push(last && k.at <= last.at ? {...k, at: last.at + 1} : k);
	};
	legs.forEach((l, i) => {
		if (i === 0) {
			push({at: 0, points: legPts(l), padding: opts.padding, area: opts.area});
			return;
		}
		const prev = legs[i - 1];
		push({at: prev.end - 4, points: legPts(prev), padding: opts.padding, area: opts.area});
		push({at: l.start + Math.round((l.end - l.start) * 0.4), points: legPts(l), padding: opts.padding, area: opts.area});
	});
	const last = legs[legs.length - 1];
	if (last && opts.overview && opts.overview > 0) {
		push({at: last.end + 4, points: legPts(last), padding: opts.padding, area: opts.area});
		push({at: last.end + 4 + opts.overview, points: stops.map((s) => asStop(s).at), padding: opts.padding ?? 0.2, area: opts.area});
	}
	return keys;
};

// A top-view airliner pointing along +x, in a 100 x 100 box centred on (50, 50).
const PLANE =
	'M97 50C97 47.5 94.2 45.6 90 45.6L60 45.6 36 10 29 10 44 45.6 20 45.6 10 32 5 32 11 47 11 53 5 68 10 68 20 54.4 44 54.4 29 90 36 90 60 54.4 90 54.4C94.2 54.4 97 52.5 97 50Z';

export type RouteProps = {
	stops: (LonLat | RouteStop)[]; // two or more places, [lon, lat] or {at, label, sub}
	delay?: number;
	legDuration?: number | number[]; // frames per leg (default: from the distance)
	dwell?: number; // frames on the ground at each stop (default 14 at 30 fps)
	ease?: Ease; // speed along each leg (default ease in-out: takes off, cruises, lands)
	lift?: number; // arc height: share of the leg's length on a flat map, of the radius on a globe
	marker?: 'plane' | 'dot' | 'none';
	markerSize?: number; // px at 1080 (plane length, default 40)
	trail?: 'solid' | 'dashed' | 'dotted';
	ghost?: boolean; // the whole route faintly before it is flown
	width?: number; // line px at 1080 (default 4)
	color?: string;
	casing?: boolean; // a light edge under the line so it reads over borders (default true)
	pins?: boolean; // pins at the stops (default true)
	originPin?: boolean; // a pin at the first stop too (default true; false when several routes share it)
	pinKind?: PinProps['kind'];
	pinColor?: string;
	out?: boolean; // fade the route out at the end of the Sequence (default false: it stays)
	outAt?: number;
};

type Sample = {x: number; y: number; v: number};

const project = (map: MapApi, leg: Leg, lift: number): Sample[] => {
	const n = Math.max(24, Math.min(160, Math.round(leg.angle / 1.2)));
	const geo = greatCircle(leg.from, leg.to, n);
	if (map.kind === 'globe') {
		const hMax = lift * (0.3 + 0.7 * Math.min(1, leg.angle / 90));
		return geo.map((c, i) => {
			const t = i / n;
			const p = map.project(c, hMax * 4 * t * (1 - t));
			return {x: p.x, y: p.y, v: p.visible};
		});
	}
	const pts = geo.map((c) => map.project(c));
	// a leg across the date line splits on a flat map: draw it without lift
	const jump = map.pxPerDeg * 180;
	let broken = false;
	for (let i = 1; i < pts.length; i++) {
		if (Math.abs(pts[i].x - pts[i - 1].x) > jump) {
			broken = true;
		}
	}
	if (broken || lift === 0) {
		return pts.map((p, i) => ({x: p.x, y: p.y, v: i > 0 && Math.abs(p.x - pts[i - 1].x) > jump ? -1 : 1}));
	}
	const a = pts[0];
	const b = pts[pts.length - 1];
	const cx = b.x - a.x;
	const cy = b.y - a.y;
	const len = Math.hypot(cx, cy) || 1;
	let nx = -cy / len;
	let ny = cx / len;
	// bend the way the great circle already bends (poleward); straight ones bend upwards
	const mid = pts[Math.floor(pts.length / 2)];
	const side = (mid.x - (a.x + b.x) / 2) * nx + (mid.y - (a.y + b.y) / 2) * ny;
	if (Math.abs(side) > 2 ? side < 0 : ny > 0) {
		nx = -nx;
		ny = -ny;
	}
	return pts.map((p, i) => {
		const t = i / (pts.length - 1);
		const o = lift * len * 4 * t * (1 - t);
		return {x: p.x + nx * o, y: p.y + ny * o, v: 1};
	});
};

// the first `f` of the samples by index (uniform in distance along the ground), and the heading at the end
const partial = (s: Sample[], f: number): {pts: Sample[]; tip: Sample; angle: number} => {
	const idx = Math.max(0, Math.min(1, f)) * (s.length - 1);
	const i = Math.floor(idx);
	const u = idx - i;
	const out = s.slice(0, i + 1);
	const a = s[Math.min(i, s.length - 1)];
	const b = s[Math.min(i + 1, s.length - 1)];
	const tip: Sample = {x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u, v: a.v + (b.v - a.v) * u};
	if (u > 0) {
		out.push(tip);
	}
	const j = Math.min(Math.max(1, i + 1), s.length - 1);
	const angle = Math.atan2(s[j].y - s[j - 1].y, s[j].x - s[j - 1].x);
	return {pts: out, tip, angle};
};

// visible runs as a path string (hidden or date-line samples break the line)
const toPath = (s: readonly Sample[]): string => {
	const parts: string[] = [];
	let open = false;
	for (const p of s) {
		if (p.v < 0.5 || !Number.isFinite(p.x)) {
			open = false;
			continue;
		}
		parts.push(`${open ? 'L' : 'M'}${p.x.toFixed(2)},${p.y.toFixed(2)}`);
		open = true;
	}
	return parts.join('');
};

export const Route: React.FC<RouteProps> = ({
	stops,
	delay = 0,
	legDuration,
	dwell,
	ease = curves.inOut,
	lift,
	marker = 'plane',
	markerSize = 46,
	trail = 'solid',
	ghost = false,
	width = 4,
	color,
	casing = true,
	pins = true,
	originPin = true,
	pinKind = 'dot',
	pinColor,
	out = false,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const map = useMap();
	const {fps, durationInFrames} = useStage();
	const {unit, palette} = map;
	const legs = legSchedule(stops, fps, {delay, legDuration, dwell});
	const c = color ?? palette.route;
	const w = width * unit;
	const h = lift ?? (map.kind === 'globe' ? 0.2 : 0.14);
	const outFrames = at30(14, fps);
	const fade = out ? 1 - ramp(frame, outAt ?? durationInFrames - 1 - outFrames, outFrames, curves.in) : 1;
	const stopList = stops.map(asStop);
	const dash = trail === 'dashed' ? `${3.2 * w} ${2.6 * w}` : trail === 'dotted' ? `0.01 ${2.8 * w}` : undefined;

	// every casing under every line: a leg's casing drawn after the leg before it painted a light gap at each waypoint
	const casings: React.ReactNode[] = [];
	const trails: React.ReactNode[] = [];
	const heads: React.ReactNode[] = [];
	legs.forEach((leg, i) => {
		const samples = project(map, leg, h);
		const raw = Math.min(1, Math.max(0, (frame - leg.start) / Math.max(1, leg.end - leg.start)));
		const f = frame < leg.start ? 0 : ease(raw);
		if (ghost) {
			const gd = toPath(samples);
			trails.push(<path key={`g${i}`} d={gd} fill="none" stroke={withAlpha(palette.labelMuted, 0.55)} strokeWidth={w * 0.6} strokeDasharray={`0.01 ${2.4 * w}`} strokeLinecap="round" />);
		}
		if (f <= 0) {
			return;
		}
		const part = partial(samples, f);
		const d = toPath(part.pts);
		if (casing && trail === 'solid') {
			casings.push(<path key={`c${i}`} d={d} fill="none" stroke={withAlpha(palette.pinRing, 0.55)} strokeWidth={w + 3.5 * unit} strokeLinecap="round" strokeLinejoin="round" />);
		}
		trails.push(<path key={`t${i}`} d={d} fill="none" stroke={c} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} />);

		// the traveller: shown while this leg flies
		const flying = frame >= leg.start && frame <= leg.end + 2;
		if (!flying || marker === 'none') {
			return;
		}
		const vis = Math.max(0, Math.min(1, part.tip.v));
		const inOut = Math.min(ramp(raw, 0, 0.08, curves.linear), 1 - ramp(raw, 0.9, 0.1, curves.linear));
		if (vis <= 0.01 || inOut <= 0) {
			return;
		}
		if (marker === 'dot') {
			heads.push(
				<g key={`h${i}`} opacity={vis * inOut}>
					<circle cx={part.tip.x} cy={part.tip.y} r={w * 2.4} fill={withAlpha(c, 0.25)} />
					<circle cx={part.tip.x} cy={part.tip.y} r={w * 1.25} fill={c} stroke={palette.pinRing} strokeWidth={1.5 * unit} />
				</g>,
			);
			return;
		}
		const L = markerSize * unit;
		const sc = (L / 100) * (0.75 + 0.25 * inOut);
		const deg = (part.angle * 180) / Math.PI;
		heads.push(
			<g key={`h${i}`} opacity={vis * Math.min(1, inOut * 1.4)}>
				<g transform={`translate(${part.tip.x + 5 * unit} ${part.tip.y + 9 * unit}) rotate(${deg}) scale(${sc}) translate(-50 -50)`}>
					<path d={PLANE} fill="rgba(0, 0, 0, 0.22)" />
				</g>
				<g transform={`translate(${part.tip.x} ${part.tip.y}) rotate(${deg}) scale(${sc}) translate(-50 -50)`}>
					<path d={PLANE} fill={palette.plane} stroke={palette.pinRing} strokeWidth={(1.6 * unit) / sc} strokeLinejoin="round" />
				</g>
			</g>,
		);
	});

	return (
		<>
			<svg width={map.width} height={map.height} style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: fade}}>
				{casings}
				{trails}
			</svg>
			{pins
				? stopList.map((s, i) => {
						if (i === 0 && !originPin) {
							return null;
						}
						const at = i === 0 ? delay : legs[i - 1].end - 1;
						return (
							<Pin
								key={`p${i}`}
								at={s.at}
								label={s.label}
								sub={s.sub}
								side={s.side}
								delay={at}
								kind={pinKind}
								color={pinColor}
								// the stops leave with the line (they used to fade on the last frames while the line stayed)
								out={out}
								outAt={outAt}
							/>
						);
					})
				: null}
			<svg width={map.width} height={map.height} style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: fade}}>
				{heads}
			</svg>
		</>
	);
};
