import {geoInterpolate} from 'd3-geo';
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {curves, ramp, springAt, useStage, useTheme} from './kit';
import {useMap, type LonLat} from './kit/maps';
import {CUE} from './cues';
import {SEGMENTS} from './route';

type Leg = {from: LonLat; to: LonLat; start: number; end: number};

// Every leg of every segment on one clock (the Routes draw with the same delays and leg lengths, no dwell).
const LEGS: Leg[] = SEGMENTS.flatMap((seg) => {
	let t = seg.delay;
	return seg.legs.map((d, i) => {
		const leg = {from: seg.stops[i], to: seg.stops[i + 1], start: t, end: t + d};
		t += d;
		return leg;
	});
});

const positionAt = (frame: number): LonLat => {
	let pos: LonLat = LEGS[0].from;
	for (const leg of LEGS) {
		if (frame >= leg.end) {
			pos = leg.to;
		} else if (frame >= leg.start) {
			return geoInterpolate(leg.from, leg.to)((frame - leg.start) / (leg.end - leg.start)) as LonLat;
		} else {
			break;
		}
	}
	return pos;
};

// The ship: one continuous marker along the whole trip. It waits at Colombo and grows when it moves to a bigger ship.
export const Vessel: React.FC = () => {
	const map = useMap();
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps} = useStage();
	const p = map.project(positionAt(frame));
	// at Chattogram on frame 0 (the poster), leaving on "leaves"
	const show = p.visible ? 1 : 0;
	const big = springAt(frame, fps, {delay: CUE.bigger - 3, config: 'pop'});
	// twice the size after the change of ship, with a ring as it swaps, so the picture says it too
	const r = (8 + 8 * big) * map.unit;
	const ring = ramp(frame, CUE.bigger - 3, 22, curves.outCubic);
	return (
		<svg width={map.width} height={map.height} style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: show}}>
			{ring > 0 && ring < 1 ? <circle cx={p.x} cy={p.y} r={r * (1.2 + 2.6 * ring)} fill="none" stroke={t.colors.accent2} strokeWidth={3 * map.unit} opacity={0.8 * (1 - ring)} /> : null}
			<circle cx={p.x} cy={p.y} r={r * 2.3} fill={t.colors.accent2} opacity={0.18} />
			<circle cx={p.x} cy={p.y} r={r} fill={t.colors.accent2} stroke="#FFFFFF" strokeWidth={2.5 * map.unit} />
		</svg>
	);
};
