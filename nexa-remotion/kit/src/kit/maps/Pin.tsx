// <Pin>: a place marker (a dot, a map pin or a ring) that lands with a short settle, sends one pulse ring on
// arrival, and opens a label pill beside it. Places come as [lon, lat] props: world-atlas has no cities.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage} from '../core';
import {ramp, springAt} from '../motion';
import type {LonLat} from './atlas';
import {withAlpha} from './color';
import {useMap} from './context';
import {bestSide, estimateWidth, Tag, useLife, type Side} from './Labels';

export type PinProps = {
	at: LonLat; // [longitude, latitude]
	label?: string;
	sub?: string; // second line (a country, a number, the Bangla name)
	delay?: number;
	kind?: 'dot' | 'pin' | 'ring';
	color?: string;
	size?: number; // px at 1080: dot diameter (pin height is 2.2x)
	pulse?: 'none' | 'once' | 'loop'; // once: two rings as it lands; loop: a slow ring every 1.8 s
	side?: Side; // where the label goes (auto: the side with room)
	labelDelay?: number; // frames after the pin lands (default 6)
	labelSize?: number; // px at 1080 (default 26)
	out?: boolean; // leave at the end of the Sequence (default false: it stays, so the last frame is never half-faded)
	outAt?: number;
};

const PIN_PATH = 'M12 0C5.4 0 0 5.2 0 11.7 0 20.2 12 32 12 32s12-11.8 12-20.3C24 5.2 18.6 0 12 0z';

export const Pin: React.FC<PinProps> = ({
	at,
	label,
	sub,
	delay = 0,
	kind = 'dot',
	color,
	size = 18,
	pulse = 'once',
	side = 'auto',
	labelDelay = 6,
	labelSize = 26,
	out = false,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const map = useMap();
	const {fps} = useStage();
	const {unit, palette} = map;
	const c = color ?? palette.pin;
	const pt = map.project(at);
	const inFrames = at30(14, fps);
	const {q} = useLife(delay, inFrames, out, outAt);
	const land = springAt(frame, fps, {delay, config: 'pop'});
	const shown = frame >= delay && q < 1 && Number.isFinite(pt.x);
	if (!shown || pt.visible <= 0.01) {
		return null;
	}
	const vis = pt.visible * (1 - q);
	const d = size * unit;
	const x = pt.x;
	const y = pt.y;

	// pulse rings: once (two rings on landing) or loop (one ring every 1.8 s)
	const rings: number[] = [];
	const ringLife = at30(34, fps);
	if (pulse === 'once') {
		rings.push(delay + 3, delay + 3 + at30(10, fps));
	} else if (pulse === 'loop') {
		const period = Math.round(1.8 * fps);
		const n = Math.floor((frame - delay - 3) / period);
		for (let i = Math.max(0, n - 1); i <= n; i++) {
			rings.push(delay + 3 + i * period);
		}
	}

	const markerTop = kind === 'pin' ? y - 1.9 * d : y;
	const lp = ramp(frame, delay + labelDelay, at30(12, fps), curves.outCubic);
	const s = side === 'auto' ? bestSide(x, markerTop, map.safe, estimateWidth(label ?? '', labelSize * unit, false) + 80 * unit) : side;
	const gap = (kind === 'pin' ? 0.62 * d : 0.5 * d) + 12 * unit;

	return (
		<>
			<svg style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: vis}} width={map.width} height={map.height}>
				{rings.map((r0) => {
					const k = ramp(frame, r0, ringLife, curves.outCubic);
					if (k <= 0 || k >= 1) {
						return null;
					}
					return <circle key={r0} cx={x} cy={y} r={d * (0.5 + 1.9 * k)} fill="none" stroke={withAlpha(c, 0.65 * (1 - k))} strokeWidth={2.4 * unit} />;
				})}
				{kind === 'dot' ? (
					<g style={{scale: `${0.35 + 0.65 * land}`, transformOrigin: `${x}px ${y}px`}}>
						<circle cx={x} cy={y + 1.5 * unit} r={d / 2 + 4 * unit} fill="rgba(0, 0, 0, 0.18)" />
						<circle cx={x} cy={y} r={d / 2 + 3.5 * unit} fill={palette.pinRing} />
						<circle cx={x} cy={y} r={d / 2} fill={c} />
					</g>
				) : kind === 'ring' ? (
					<g style={{scale: `${0.35 + 0.65 * land}`, transformOrigin: `${x}px ${y}px`}}>
						<circle cx={x} cy={y} r={d / 2} fill={withAlpha(c, 0.16)} stroke={c} strokeWidth={3.5 * unit} />
					</g>
				) : (
					<g>
						<ellipse cx={x} cy={y} rx={d * 0.42 * land} ry={d * 0.14 * land} fill="rgba(0, 0, 0, 0.22)" />
						<g
							style={{
								translate: `0px ${-(1 - Math.min(1, land)) * 26 * unit}px`,
								scale: `${1 + (land - 1) * 0.6} ${1 - (land - 1) * 0.5}`,
								transformOrigin: `${x}px ${y}px`,
							}}
						>
							<g transform={`translate(${x - 1.1 * d} ${y - 2.95 * d}) scale(${(2.2 * d) / 24})`}>
								<path d={PIN_PATH} fill={c} stroke={palette.pinRing} strokeWidth={24 / (2.2 * d) * 2 * unit} />
								<circle cx={12} cy={11.5} r={4.6} fill={palette.pinRing} />
							</g>
						</g>
					</g>
				)}
			</svg>
			{label ? (
				<div style={{position: 'absolute', inset: 0, opacity: pt.visible}}>
					<Tag x={x} y={markerTop} title={label} sub={sub} side={s} gap={gap} p={lp} q={q} map={map} size={labelSize} />
				</div>
			) : null}
		</>
	);
};

/** Frames a pin needs to land and show its label, for timing the next beat. */
export const pinFrames = (fps: number): number => at30(26, fps);

