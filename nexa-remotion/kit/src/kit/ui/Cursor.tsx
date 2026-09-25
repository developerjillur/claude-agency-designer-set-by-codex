// The pointer as a stage prop: a life-size-plus arrow or hand (44 x 54 px at 1080) that travels between targets on
// bowed arcs, anticipates, blooms on hover, presses, springs back and leaves a small ring; plus a touch indicator
// for phone demos and a helper that puts a click sound on every press. Positions are px at 1080 in the box the
// component sits in, and the tip (not the corner of the drawing) lands on the target.
import {Audio} from '@remotion/media';
import React, {useMemo} from 'react';
import {Easing, Sequence, useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {pulse, ramp} from '../motion';
import {fade, pressDepth} from './shared';

export type CursorShape = 'arrow' | 'hand' | 'grab' | 'text';

export type CursorKey = {
	x: number; // where the tip lands, px at 1080 in the parent box
	y: number;
	at: number; // the frame the tip arrives here (the first key: the frame it appears)
	click?: boolean | number; // true: press `lead` frames after arriving; a number: the press frame itself
	double?: boolean; // a second press 5 frames after the first
	drag?: boolean; // keep the button down from this press until the next key (drag and drop)
	shape?: CursorShape; // from the arrival on (default: hand where it clicks or drags, else arrow)
	duration?: number; // frames of the move into this key (default: from the distance)
	arc?: number; // bow of the move into this key as a share of its length (default 0.1, 0 is straight)
};

type Resolved = {
	x: number;
	y: number;
	at: number;
	press?: number;
	press2?: number;
	release?: number;
	drag: boolean;
	shape: CursorShape;
	leave: number;
	arc: number;
	index: number;
};

type Move = {a: Resolved; b: Resolved; start: number; end: number};

export type CursorTimeline = {
	keys: Resolved[];
	moves: Move[];
	/** Every press frame (the bottom of the press), in time order: put click sounds and control presses here. */
	clicks: number[];
	/** Frames where a drag lets go. */
	releases: number[];
	/** The frame the cursor appears. */
	start: number;
	/** The last frame anything happens (arrival, press or release). */
	end: number;
	/** The press frame of the key at `index` in the list you gave (undefined if it does not click). */
	pressOf: (index: number) => number | undefined;
	/** The arrival frame of the key at `index`. */
	arriveOf: (index: number) => number;
};

const EASE_X = Easing.bezier(0.5, 0, 0.18, 1);
const EASE_Y = Easing.bezier(0.38, 0, 0.24, 1);

/** Frames for a pointer move of `dist` px at 1080 (a quick hand: 14 f for 100 px, 24 f for 900 px at 30 fps). */
export const cursorMoveFrames = (dist: number, fps: number): number =>
	at30(Math.round(clamp(9 + 0.5 * Math.sqrt(Math.max(0, dist)), 10, 30)), fps);

/**
 * The cursor's plan as data: when it moves, where it presses and its click frames. Pure, so a scene can read the
 * same numbers for sound, for the pressed controls and for a camera.
 */
export const cursorTimeline = (keys: readonly CursorKey[], fps: number, lead = at30(4, fps)): CursorTimeline => {
	const order = keys.map((k, i) => ({k, i})).sort((p, q) => p.k.at - q.k.at);
	const settle = at30(5, fps);
	const res: Resolved[] = order.map(({k, i}) => {
		const press = k.click === true ? k.at + lead : typeof k.click === 'number' ? Math.max(k.click, k.at) : undefined;
		const press2 = press !== undefined && k.double ? press + at30(5, fps) : undefined;
		const acting = press !== undefined || k.drag;
		return {
			x: k.x,
			y: k.y,
			at: k.at,
			press: k.drag && press === undefined ? k.at + lead : press,
			press2,
			release: undefined,
			drag: Boolean(k.drag),
			shape: k.shape ?? (acting ? 'hand' : 'arrow'),
			leave: k.at + 1,
			arc: k.arc ?? 0.1,
			index: i,
		};
	});
	// a drag lets go just after it arrives at the next key
	for (let j = 0; j < res.length; j++) {
		const r = res[j];
		if (r.drag && res[j + 1]) {
			r.release = res[j + 1].at + at30(2, fps);
		}
		const lastPress = r.press2 ?? r.press;
		r.leave = r.drag ? (r.press ?? r.at) + 1 : lastPress !== undefined ? lastPress + settle : r.at + 1;
		// after a drop, wait for the release before moving on
		const before = res[j - 1];
		if (before?.drag && before.release !== undefined) {
			r.leave = Math.max(r.leave, before.release + settle);
		}
	}
	const moves: Move[] = [];
	for (let j = 1; j < res.length; j++) {
		const a = res[j - 1];
		const b = res[j];
		const given = keys[b.index].duration;
		const dur = given ?? cursorMoveFrames(Math.hypot(b.x - a.x, b.y - a.y), fps);
		const earliest = Math.max(a.leave, a.at + 1);
		let start = Math.max(earliest, b.at - dur);
		if (start > b.at - 2) {
			start = Math.max(a.at + 1, b.at - 2); // packed too tight: a fast move rather than a missed target
		}
		moves.push({a, b, start, end: b.at});
	}
	const clicks: number[] = [];
	const releases: number[] = [];
	for (const r of res) {
		if (r.press !== undefined) {
			clicks.push(r.press);
		}
		if (r.press2 !== undefined) {
			clicks.push(r.press2);
		}
		if (r.release !== undefined) {
			releases.push(r.release);
		}
	}
	const last = res[res.length - 1];
	const end = Math.max(last?.at ?? 0, ...clicks, ...releases);
	return {
		keys: res,
		moves,
		clicks: clicks.sort((p, q) => p - q),
		releases,
		start: res[0]?.at ?? 0,
		end,
		pressOf: (index) => res.find((r) => r.index === index)?.press,
		arriveOf: (index) => res.find((r) => r.index === index)?.at ?? 0,
	};
};

export type CursorPose = {
	x: number; // px at 1080
	y: number;
	shape: CursorShape;
	press: number; // 0 up, 1 fully down (a little below 0 during the release overshoot)
	bloom: number; // 0 to 1
	ripples: {x: number; y: number; t: number}[];
	moving: boolean;
};

/** Where the cursor is and what it is doing at `frame`. */
export const cursorPose = (tl: CursorTimeline, frame: number, fps: number): CursorPose => {
	const ks = tl.keys;
	if (ks.length === 0) {
		return {x: 0, y: 0, shape: 'arrow', press: 0, bloom: 0, ripples: [], moving: false};
	}
	let x = ks[0].x;
	let y = ks[0].y;
	let shape: CursorShape = ks[0].shape;
	let moving = false;
	let dragging: Resolved | null = null;
	// the last key reached, or the move under way
	for (const k of ks) {
		if (frame >= k.at) {
			x = k.x;
			y = k.y;
			shape = k.shape;
		}
	}
	for (const m of tl.moves) {
		if (frame >= m.start && frame < m.end) {
			moving = true;
			const T = Math.max(1, m.end - m.start);
			const antF = Math.min(at30(3, fps), Math.floor(T / 3));
			const a0 = antF / (2 * T);
			const t = clamp((frame - m.start) / T);
			const tt = clamp((t - a0) / (1 - a0));
			const px = EASE_X(tt);
			const py = EASE_Y(tt);
			const dx = m.b.x - m.a.x;
			const dy = m.b.y - m.a.y;
			const L = Math.hypot(dx, dy) || 1;
			let nx = -dy / L;
			let ny = dx / L;
			if (ny < -1e-6 || (Math.abs(ny) <= 1e-6 && nx < 0)) {
				nx = -nx;
				ny = -ny;
			}
			const bow = Math.min(m.b.arc * L, 80) * Math.sin(Math.PI * px);
			const back = Math.min(8, 0.05 * L) * pulse(frame, m.start, Math.max(2, antF));
			x = m.a.x + dx * px + nx * bow - (dx / L) * back;
			y = m.a.y + dy * py + ny * bow - (dy / L) * back;
			const arriving = frame >= m.end - at30(3, fps);
			shape = arriving ? m.b.shape : m.a.drag ? (m.a.shape === 'arrow' ? 'arrow' : 'grab') : 'arrow';
			if (m.a.drag) {
				dragging = m.a;
			}
		}
	}
	let press = 0;
	let bloom = 0;
	const ripples: CursorPose['ripples'] = [];
	for (const k of ks) {
		if (k.drag && k.press !== undefined) {
			const rel = k.release ?? k.press + at30(6, fps);
			const down = frame <= k.press ? pressDepth(frame, k.press, fps) : frame <= rel ? 1 : pressDepth(frame, rel - 1, fps);
			press = Math.max(press, down);
			if (frame >= k.press && frame <= rel && k.shape !== 'arrow') {
				shape = 'grab';
			}
		} else {
			for (const p of [k.press, k.press2]) {
				if (p === undefined) {
					continue;
				}
				const d = pressDepth(frame, p, fps);
				press = Math.abs(d) > Math.abs(press) ? d : press;
				const r = ramp(frame, p, at30(14, fps), curves.out);
				if (frame >= p && r < 1) {
					ripples.push({x: k.x, y: k.y, t: r});
				}
			}
		}
		if (k.press !== undefined) {
			const lastUp = k.release ?? k.press2 ?? k.press;
			const b = ramp(frame, k.at, at30(4, fps), curves.out) * (1 - ramp(frame, lastUp + at30(2, fps), at30(10, fps), curves.in));
			bloom = Math.max(bloom, b);
		}
	}
	if (dragging && shape === 'arrow' && dragging.shape !== 'arrow') {
		shape = 'grab';
	}
	return {x, y, shape, press, bloom, ripples, moving};
};

// ------------------------------------------------------------------ the drawings (44 x 54 box)

const TIPS: Record<CursorShape, [number, number]> = {
	arrow: [4, 2],
	hand: [16.5, 3.5],
	grab: [25, 27],
	text: [18, 23],
};

const ARROW = 'M4 2 L4 44.6 L14.1 35 L21.4 51.8 L28.6 48.8 L21.5 32.6 L35.4 32.2 Z';

type Blob = {x: number; y: number; w: number; h: number; r: number; rot?: number};

const handBlobs = (grab: boolean): Blob[] => [
	grab ? {x: 13, y: 15.5, w: 7.6, h: 16, r: 3.8} : {x: 12.6, y: 2.5, w: 8, h: 28, r: 4},
	{x: 20.3, y: grab ? 14.5 : 15.5, w: 7.4, h: 15.5, r: 3.7},
	{x: 27.4, y: grab ? 15.5 : 17.2, w: 7, h: 14.5, r: 3.5},
	{x: 34, y: grab ? 18 : 20.4, w: 6.4, h: 12.5, r: 3.2},
	{x: 12.6, y: 24, w: 28, h: 23.5, r: 9},
	{x: 17, y: 42, w: 19, h: 10, r: 3},
	{x: 5.2, y: 22, w: 8.2, h: 17, r: 4.1, rot: -40},
];

const Blobs: React.FC<{blobs: Blob[]; fill: string; stroke?: string; width?: number}> = ({blobs, fill, stroke, width}) => (
	<>
		{blobs.map((b, i) => (
			<rect
				key={i}
				x={b.x}
				y={b.y}
				width={b.w}
				height={b.h}
				rx={b.r}
				fill={fill}
				stroke={stroke}
				strokeWidth={width}
				strokeLinejoin="round"
				transform={b.rot ? `rotate(${b.rot} ${b.x + b.w / 2} ${b.y + b.h / 2})` : undefined}
			/>
		))}
	</>
);

const Glyph: React.FC<{shape: CursorShape; fill: string; stroke: string; sw: number}> = ({shape, fill, stroke, sw}) => {
	if (shape === 'arrow') {
		return <path d={ARROW} fill={fill} stroke={stroke} strokeWidth={sw} strokeLinejoin="round" />;
	}
	if (shape === 'text') {
		const d = 'M13 5.5c2.5 0 4 .8 5 2.2 1-1.4 2.5-2.2 5-2.2M18 7.7v30.6M13 40.5c2.5 0 4-.8 5-2.2 1 1.4 2.5 2.2 5 2.2';
		return (
			<>
				<path d={d} fill="none" stroke={fill} strokeWidth={sw + 3} strokeLinecap="round" />
				<path d={d} fill="none" stroke={stroke} strokeWidth={sw + 0.4} strokeLinecap="round" />
			</>
		);
	}
	const blobs = handBlobs(shape === 'grab');
	const creases = shape === 'grab' ? [[20.3, 17], [27.4, 18], [34, 20.5]] : [[20.3, 18], [27.4, 20], [34, 22.8]];
	return (
		<>
			<Blobs blobs={blobs} fill={stroke} stroke={stroke} width={sw * 2} />
			<Blobs blobs={blobs} fill={fill} />
			{creases.map(([cx, cy], i) => (
				<path key={i} d={`M${cx} ${cy}v${shape === 'grab' ? 8 : 8.5}`} stroke={stroke} strokeWidth={sw * 0.8} strokeLinecap="round" opacity={0.85} />
			))}
		</>
	);
};

export type CursorProps = {
	keys: CursorKey[];
	size?: number; // 1 = 44 x 54 px at 1080
	fill?: string; // default white
	stroke?: string; // outline, default near-black
	bloom?: string | false; // hover bloom colour (default: the theme accent)
	ripple?: string | false; // click ring colour (default white with a dark hairline, so it reads on any control); false for none
	lead?: number; // frames from arriving to pressing when `click: true` (default 4 at 30 fps)
	hideAfter?: number; // frames after the last event before it fades out (default 22 at 30 fps; Infinity keeps it)
	appear?: 'fade' | 'none';
	debug?: boolean; // red target marks at every key, with the key index and its press frame
	style?: React.CSSProperties;
};

/**
 * A pointer that follows `keys`. Put it last inside the positioned box whose coordinates the keys use (a page, a
 * window's content, the whole frame), so it draws on top. Read the same plan with `cursorTimeline(keys, fps)`.
 */
export const Cursor: React.FC<CursorProps> = ({
	keys,
	size = 1,
	fill = '#FFFFFF',
	stroke = '#111317',
	bloom,
	ripple,
	lead,
	hideAfter,
	appear = 'fade',
	debug = false,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, durationInFrames} = useStage();
	const tl = useMemo(() => cursorTimeline(keys, fps, lead ?? at30(4, fps)), [keys, fps, lead]);
	if (tl.keys.length === 0) {
		return null;
	}
	const pose = cursorPose(tl, frame, fps);
	const k = unit * size;
	const fadeIn = at30(6, fps);
	const fadeOut = at30(8, fps);
	const hold = hideAfter ?? at30(22, fps);
	let hideStart = Number.isFinite(hold) ? tl.end + hold : Infinity;
	if (Number.isFinite(durationInFrames)) {
		hideStart = Math.min(hideStart, durationInFrames - 1 - fadeOut);
	}
	const shown =
		(appear === 'fade' ? ramp(frame, tl.start, fadeIn, curves.out) : frame >= tl.start ? 1 : 0) *
		(Number.isFinite(hideStart) ? 1 - ramp(frame, hideStart, fadeOut, curves.in) : 1);
	const bloomColor = bloom === false ? null : (bloom ?? t.colors.accent);
	const ringColor = ripple === false ? null : (ripple ?? '#FFFFFF');
	const [tx, ty] = TIPS[pose.shape];
	const scale = 1 - 0.14 * pose.press;
	const X = pose.x * unit;
	const Y = pose.y * unit;
	const bloomR = 30 * k;
	return (
		<div style={{position: 'absolute', left: 0, top: 0, width: 0, height: 0, overflow: 'visible', pointerEvents: 'none', zIndex: 40, ...style}}>
			{debug
				? tl.keys.map((kk) => (
						<div key={`dbg-${kk.index}`} style={{position: 'absolute', left: kk.x * unit, top: kk.y * unit}}>
							<div style={{position: 'absolute', left: -14 * unit, top: -1 * unit, width: 28 * unit, height: 2 * unit, background: '#FF1E56'}} />
							<div style={{position: 'absolute', left: -1 * unit, top: -14 * unit, width: 2 * unit, height: 28 * unit, background: '#FF1E56'}} />
							<div style={{position: 'absolute', left: 8 * unit, top: 6 * unit, font: `${14 * unit}px monospace`, color: '#FF1E56', whiteSpace: 'nowrap', background: 'rgba(255,255,255,0.85)', padding: `0 ${3 * unit}px`}}>
								{kk.index} @{kk.at}
								{kk.press !== undefined ? ` click ${kk.press}` : ''}
							</div>
						</div>
					))
				: null}
			{shown > 0.001 && bloomColor && pose.bloom > 0.001 ? (
				<div
					style={{
						position: 'absolute',
						left: X - bloomR,
						top: Y - bloomR,
						width: bloomR * 2,
						height: bloomR * 2,
						borderRadius: '50%',
						background: `radial-gradient(circle, ${fade(bloomColor, 0.42)} 0%, ${fade(bloomColor, 0.18)} 45%, ${fade(bloomColor, 0)} 70%)`,
						opacity: shown * pose.bloom,
						scale: `${0.5 + 0.5 * pose.bloom}`,
					}}
				/>
			) : null}
			{ringColor && shown > 0.001
				? pose.ripples.map((r, i) => {
						const rad = (12 + 30 * r.t) * k;
						return (
							<div
								key={`rip-${i}`}
								style={{
									position: 'absolute',
									left: r.x * unit - rad,
									top: r.y * unit - rad,
									width: rad * 2,
									height: rad * 2,
									borderRadius: '50%',
									boxSizing: 'border-box',
									border: `${(3 - 1.6 * r.t) * k}px solid ${fade(ringColor, 0.85 * (1 - r.t))}`,
									boxShadow: `0 0 0 ${0.8 * k}px rgba(0, 0, 0, ${0.16 * (1 - r.t)}), inset 0 0 0 ${0.8 * k}px rgba(0, 0, 0, ${0.12 * (1 - r.t)})`,
								}}
							/>
						);
					})
				: null}
			{shown > 0.001 ? (
				<svg
					width={44 * k}
					height={54 * k}
					viewBox="0 0 44 54"
					style={{
						position: 'absolute',
						left: X - tx * k,
						top: Y - ty * k,
						overflow: 'visible',
						opacity: shown,
						scale: `${scale}`,
						transformOrigin: `${tx * k}px ${ty * k}px`,
						filter: `drop-shadow(0 ${2.5 * k}px ${3.5 * k}px rgba(0, 0, 0, 0.32))`,
					}}
				>
					<Glyph shape={pose.shape} fill={fill} stroke={stroke} sw={1.6} />
				</svg>
			) : null}
		</div>
	);
};

// ------------------------------------------------------------------ touches for phone demos

export type TapKey = {
	x: number; // px at 1080 in the parent box (usually a phone screen)
	y: number;
	at: number; // the frame the finger is fully down (the tap: put the press and the sound here)
	hold?: number; // frames it stays down (default 5 at 30 fps; a long press about 24)
	long?: boolean; // draw a ring that fills while it holds
};

export type SwipeKey = {
	from: [number, number];
	to: [number, number];
	at: number; // the frame the finger touches down
	frames?: number; // travel frames (default 14 at 30 fps)
};

export type TapIndicatorProps = {
	taps?: TapKey[];
	swipes?: SwipeKey[];
	size?: number; // finger circle diameter, px at 1080 (default 62)
	color?: string; // fill (default a translucent grey that reads on light and dark screens)
	ring?: string; // outline (default white)
};

/** A cursor-free touch: a translucent finger dot that presses, holds and lifts, and swipes with a short trail. */
export const TapIndicator: React.FC<TapIndicatorProps> = ({taps = [], swipes = [], size = 62, color = 'rgba(118, 122, 134, 0.45)', ring = 'rgba(255, 255, 255, 0.9)'}) => {
	const frame = useCurrentFrame();
	const {fps, unit} = useStage();
	const D = size * unit;
	const dot = (key: string, x: number, y: number, s: number, o: number, fill = color) => (
		<div
			key={key}
			style={{
				position: 'absolute',
				left: x * unit - D / 2,
				top: y * unit - D / 2,
				width: D,
				height: D,
				borderRadius: '50%',
				background: fill,
				boxSizing: 'border-box',
				border: `${2 * unit}px solid ${ring}`,
				boxShadow: `0 ${3 * unit}px ${12 * unit}px rgba(0, 0, 0, 0.22)`,
				opacity: o,
				scale: `${s}`,
			}}
		/>
	);
	const parts: React.ReactNode[] = [];
	taps.forEach((tp, i) => {
		const down = at30(3, fps);
		const hold = tp.hold ?? (tp.long ? at30(24, fps) : at30(5, fps));
		const up = at30(10, fps);
		if (frame < tp.at - down || frame > tp.at + hold + up) {
			return;
		}
		const pIn = ramp(frame, tp.at - down, down, curves.out);
		const pOut = ramp(frame, tp.at + hold, up, curves.out);
		const s = (1.35 - 0.35 * pIn) * (1 + 0.55 * pOut);
		parts.push(dot(`tap-${i}`, tp.x, tp.y, s, pIn * (1 - pOut)));
		if (tp.long) {
			const fill = ramp(frame, tp.at, hold, curves.linear);
			const R = D * 0.78;
			parts.push(
				<svg key={`long-${i}`} width={R * 2} height={R * 2} viewBox="0 0 100 100" style={{position: 'absolute', left: tp.x * unit - R, top: tp.y * unit - R, opacity: pIn * (1 - pOut), rotate: '-90deg'}}>
					<circle cx={50} cy={50} r={45} fill="none" stroke={ring} strokeWidth={5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - fill} strokeLinecap="round" />
				</svg>,
			);
		}
	});
	swipes.forEach((sw, i) => {
		const frames = sw.frames ?? at30(14, fps);
		const down = at30(3, fps);
		const up = at30(8, fps);
		if (frame < sw.at - down || frame > sw.at + frames + up) {
			return;
		}
		const pos = (f: number) => {
			const p = ramp(f, sw.at, frames, curves.inOut);
			return [sw.from[0] + (sw.to[0] - sw.from[0]) * p, sw.from[1] + (sw.to[1] - sw.from[1]) * p] as const;
		};
		const pIn = ramp(frame, sw.at - down, down, curves.out);
		const pOut = ramp(frame, sw.at + frames, up, curves.out);
		const o = pIn * (1 - pOut);
		[6, 4, 2].forEach((lag, j) => {
			const [gx, gy] = pos(frame - lag);
			parts.push(dot(`sw-${i}-${lag}`, gx, gy, 0.75 - 0.1 * j, o * (0.12 + 0.1 * j)));
		});
		const [x, y] = pos(frame);
		parts.push(dot(`sw-${i}`, x, y, (1.3 - 0.3 * pIn) * (1 + 0.4 * pOut), o));
	});
	return <div style={{position: 'absolute', left: 0, top: 0, width: 0, height: 0, overflow: 'visible', pointerEvents: 'none', zIndex: 40}}>{parts}</div>;
};

// ------------------------------------------------------------------ sound on the presses

export type ClickSoundsProps = {
	frames: readonly number[]; // press frames, for example cursorTimeline(keys, fps).clicks
	src: string; // staticFile('ui/click.wav') after copying the kit's public/ui files into the project
	volume?: number;
	offset?: number; // frames between the start of the file and its transient (0 for the kit's files)
	length?: number; // frames each sound may play (default 12)
};

/** A click sound on every frame of `frames`, lined up to the transient. */
export const ClickSounds: React.FC<ClickSoundsProps> = ({frames, src, volume = 0.6, offset = 0, length = 12}) => (
	<>
		{frames.map((f, i) => (
			<Sequence key={`${f}-${i}`} from={Math.max(0, Math.round(f - offset))} durationInFrames={length} layout="none" name="ui click">
				<Audio src={src} volume={volume} />
			</Sequence>
		))}
	</>
);
