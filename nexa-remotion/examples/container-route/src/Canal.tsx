import React from 'react';
import {useMap, type LonLat} from './kit/maps';

// The Suez Canal as water: the world data has no canal, so a close shot showed the ship crossing plain land. A line
// in the sea's colour through Suez, the Great Bitter Lake and Ismailia to Port Said (drawn under the route).
const PATH: LonLat[] = [
	[32.55, 29.93],
	[32.57, 30.1],
	[32.46, 30.3],
	[32.35, 30.42],
	[32.29, 30.6],
	[32.32, 30.9],
	[32.31, 31.27],
];

export const Canal: React.FC<{color: string}> = ({color}) => {
	const map = useMap();
	const pts = PATH.map((p) => map.project(p));
	if (pts.every((p) => !p.visible)) {
		return null;
	}
	const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
	return (
		<svg width={map.width} height={map.height} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			<path d={d} fill="none" stroke={color} strokeWidth={7 * map.unit} strokeLinecap="round" strokeLinejoin="round" />
		</svg>
	);
};
