import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ramp, useTheme} from './kit';
import {useMap, type LonLat} from './kit/maps';

// Sea names in the cartographer's style: italic, spaced, in the water colour's darker tone, fading in on their word.
// `along` turns the name to follow a long narrow sea (two points on its axis), so it can sit beside a route that
// runs down the middle instead of across it. `outAt` fades it (the whole-trip view is too small for sea names).
export const WaterLabel: React.FC<{at: LonLat; text: string; delay: number; size?: number; along?: [LonLat, LonLat]; outAt?: number}> = ({at, text, delay, size = 30, along, outAt}) => {
	const map = useMap();
	const t = useTheme();
	const frame = useCurrentFrame();
	const p = map.project(at);
	let rotate = 0;
	if (along) {
		const a = map.project(along[0]);
		const b = map.project(along[1]);
		rotate = (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI;
		// keep the words reading left to right
		if (rotate > 90) rotate -= 180;
		if (rotate < -90) rotate += 180;
	}
	// fade out before any part of the name reaches the safe area's edge while the camera pans (measured from the
	// centre, a long name like "Mediterranean Sea" still crossed it)
	const halfW = ((text.length * size * 0.62) / 2) * map.unit;
	const halfH = size * 0.7 * map.unit;
	const rad = (rotate * Math.PI) / 180;
	const ex = halfW * Math.abs(Math.cos(rad)) + halfH * Math.abs(Math.sin(rad));
	const ey = halfW * Math.abs(Math.sin(rad)) + halfH * Math.abs(Math.cos(rad));
	const s = map.safe;
	const inside = Math.min(p.x - ex - s.x, s.x + s.w - p.x - ex, p.y - ey - s.y, s.y + s.h - p.y - ey);
	const edge = Math.max(0, Math.min(1, inside / (60 * map.unit)));
	const gone = outAt === undefined ? 0 : ramp(frame, outAt, 14);
	const o = ramp(frame, delay, 12) * (1 - gone) * (p.visible ? 1 : 0) * edge;
	return (
		<div
			style={{
				position: 'absolute',
				left: p.x,
				top: p.y,
				translate: '-50% -50%',
				rotate: `${rotate}deg`,
				fontFamily: t.type.serif,
				fontStyle: 'italic',
				fontWeight: 400,
				fontSize: size * map.unit,
				letterSpacing: '0.06em',
				color: '#3E6A87',
				opacity: o,
				whiteSpace: 'nowrap',
			}}
		>
			{text}
		</div>
	);
};
