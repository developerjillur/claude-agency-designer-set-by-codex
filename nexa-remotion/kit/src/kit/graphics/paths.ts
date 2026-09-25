// Path maths on top of @remotion/paths: cached lengths, null-safe points and angles, draw-on dashes per subpath,
// multi-keyframe morphs (interpolatePaths is 4.0.529, so not on 4.0.528) and a resampling morph that works between
// any two closed outlines. Every function is pure; caches only save re-parsing the same string.
import {getLength, getPointAtLength, getSubpaths, getTangentAtLength, interpolatePath, parsePath, reduceInstructions} from '@remotion/paths';
import {interpolate} from 'remotion';
import {curves, type Ease} from '../core';

export type PathPoint = {x: number; y: number};

const cache = <V>(limit = 400) => {
	const m = new Map<string, V>();
	return (key: string, make: () => V): V => {
		const hit = m.get(key);
		if (hit !== undefined) {
			return hit;
		}
		const v = make();
		if (m.size >= limit) {
			const first = m.keys().next().value;
			if (first !== undefined) {
				m.delete(first);
			}
		}
		m.set(key, v);
		return v;
	};
};

const lengths = cache<number>(800);
const subs = cache<string[]>(400);

/** Total length of a path (cached). */
export const pathLength = (d: string): number => lengths(d, () => (d.trim() ? getLength(d) : 0));

/** The subpaths of a path (split at every M), cached. */
export const subpathsOf = (d: string): string[] => subs(d, () => (d.trim() ? getSubpaths(d) : []));

/** The point `len` along the path: clamped to the path, never null (4.0.528 returns null past the end). */
export const pointOnPath = (d: string, len: number): PathPoint => {
	if (!d.trim()) {
		return {x: 0, y: 0};
	}
	const total = pathLength(d);
	const l = Math.min(Math.max(0, len), total);
	return getPointAtLength(d, l) ?? getPointAtLength(d, total) ?? getPointAtLength(d, 0) ?? {x: 0, y: 0};
};

/**
 * Where an object riding the path is at progress t (0 to 1), and its heading in degrees (0 = pointing right). The
 * heading is measured across a short window, so corners turn smoothly and a zero tangent never flips it.
 */
export const pathPose = (d: string, t: number, window = 4): {x: number; y: number; angle: number} => {
	if (!d.trim()) {
		return {x: 0, y: 0, angle: 0};
	}
	const total = pathLength(d);
	const l = Math.min(Math.max(0, t), 1) * total;
	const p = pointOnPath(d, l);
	const w = Math.min(window, total / 2);
	const a = pointOnPath(d, l - w);
	const b = pointOnPath(d, l + w);
	let dx = b.x - a.x;
	let dy = b.y - a.y;
	if (Math.hypot(dx, dy) < 1e-6) {
		const tan = getTangentAtLength(d, Math.min(l, total)) ?? {x: 1, y: 0};
		dx = tan.x;
		dy = tan.y;
	}
	return {x: p.x, y: p.y, angle: (Math.atan2(dy, dx) * 180) / Math.PI};
};

/**
 * Dash props that show the first `p` of a path of length `len`. Use `hidden` to skip rendering at 0 (a round cap
 * would leave a dot), and a solid stroke at 1 (no seam).
 */
export const dashFor = (len: number, p: number): {strokeDasharray?: string; strokeDashoffset?: number; hidden: boolean} => {
	if (p <= 0) {
		return {hidden: true};
	}
	if (p >= 1 || len <= 0.01) {
		// done, or a zero-length subpath (a dot drawn by its round cap): show it whole
		return {hidden: false};
	}
	return {strokeDasharray: `${len * p} ${len * 2 + 10}`, strokeDashoffset: 0, hidden: false};
};

export type DrawMode = 'together' | 'sequence' | 'stagger';

/**
 * Progress of each subpath when the whole drawing is at p. 'together': all at once; 'sequence': one after another
 * by length (a pen); 'stagger': equal overlapping windows (lists of strokes, icons).
 */
export const subProgress = (lens: readonly number[], p: number, mode: DrawMode = 'sequence', overlap = 0.5): number[] => {
	const n = lens.length;
	if (n === 0) {
		return [];
	}
	if (mode === 'together' || n === 1) {
		return lens.map(() => Math.min(1, Math.max(0, p)));
	}
	if (mode === 'stagger') {
		const w = 1 / (1 + (n - 1) * (1 - overlap));
		const step = w * (1 - overlap);
		return lens.map((_, i) => Math.min(1, Math.max(0, (p - i * step) / w)));
	}
	const total = lens.reduce((a, b) => a + b, 0) || 1;
	let acc = 0;
	return lens.map((len) => {
		const start = acc / total;
		acc += len;
		const span = len / total;
		return span <= 0 ? (p >= start ? 1 : 0) : Math.min(1, Math.max(0, (p - start) / span));
	});
};

const vertexCache = cache<number[]>(200);

/**
 * The length along the path at each vertex (the end of every segment), for timing dots and labels to the moment a
 * drawing line reaches them. Index 0 is the start (0).
 */
export const vertexLengths = (d: string): number[] =>
	vertexCache(d, () => {
		const ins = reduceInstructions(parsePath(d));
		const out: number[] = [];
		let cur: PathPoint = {x: 0, y: 0};
		let start: PathPoint = {x: 0, y: 0};
		let acc = 0;
		for (const i of ins) {
			if (i.type === 'M') {
				cur = {x: i.x, y: i.y};
				start = cur;
				out.push(acc);
			} else if (i.type === 'L') {
				acc += Math.hypot(i.x - cur.x, i.y - cur.y);
				cur = {x: i.x, y: i.y};
				out.push(acc);
			} else if (i.type === 'C') {
				acc += getLength(`M${cur.x} ${cur.y}C${i.cp1x} ${i.cp1y} ${i.cp2x} ${i.cp2y} ${i.x} ${i.y}`);
				cur = {x: i.x, y: i.y};
				out.push(acc);
			} else if (i.type === 'Z') {
				acc += Math.hypot(start.x - cur.x, start.y - cur.y);
				cur = start;
			}
		}
		return out;
	});

const sampleCache = cache<PathPoint[]>(200);

/** n points at equal spacing along a path (its first subpath when `firstOnly`), cached. */
export const resamplePath = (d: string, n: number): PathPoint[] =>
	sampleCache(`${n}|${d}`, () => {
		const total = pathLength(d);
		const pts: PathPoint[] = [];
		for (let i = 0; i < n; i++) {
			pts.push(pointOnPath(d, (i / n) * total));
		}
		return pts;
	});

const area = (pts: readonly PathPoint[]): number => {
	let s = 0;
	for (let i = 0; i < pts.length; i++) {
		const a = pts[i];
		const b = pts[(i + 1) % pts.length];
		s += a.x * b.y - b.x * a.y;
	}
	return s / 2;
};

const alignCache = cache<PathPoint[]>(100);

/** `b` rotated (and reversed if its winding differs) so its points line up with `a`'s: a morph without twisting. */
const alignRing = (a: PathPoint[], b: PathPoint[], key: string): PathPoint[] =>
	alignCache(key, () => {
		const n = a.length;
		const src = Math.sign(area(a)) !== Math.sign(area(b)) ? [...b].reverse() : b;
		let best = 0;
		let bestCost = Infinity;
		const stride = n > 120 ? 2 : 1;
		for (let s = 0; s < n; s++) {
			let cost = 0;
			for (let i = 0; i < n; i += stride) {
				const p = a[i];
				const q = src[(i + s) % n];
				cost += (p.x - q.x) ** 2 + (p.y - q.y) ** 2;
				if (cost >= bestCost) {
					break;
				}
			}
			if (cost < bestCost) {
				bestCost = cost;
				best = s;
			}
		}
		return src.map((_, i) => src[(i + best) % n]);
	});

const ring = (pts: readonly PathPoint[]): string =>
	pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join('') + 'Z';

export type MorphMode = 'points' | 'native';

/**
 * The shape between `a` (t = 0) and `b` (t = 1). 'points' (default) resamples both outlines to the same number
 * of points and lines them up, which morphs any two single closed outlines cleanly (circle to star to heart);
 * shapes with the same number of subpaths are morphed subpath by subpath. 'native' is @remotion/paths
 * interpolatePath (fine for shapes made to match). The exact source strings are returned at 0 and 1.
 */
export const morphBetween = (a: string, b: string, t: number, mode: MorphMode = 'points', samples = 240): string => {
	if (t <= 0) {
		return a;
	}
	if (t >= 1) {
		return b;
	}
	if (mode === 'native') {
		return interpolatePath(t, a, b);
	}
	const sa = subpathsOf(a);
	const sb = subpathsOf(b);
	if (sa.length !== sb.length || sa.length === 0) {
		return interpolatePath(t, a, b);
	}
	return sa
		.map((da, k) => {
			const db = sb[k];
			const pa = resamplePath(da, samples);
			const pb = alignRing(pa, resamplePath(db, samples), `${samples}|${da}|${db}`);
			return ring(pa.map((p, i) => ({x: p.x + (pb[i].x - p.x) * t, y: p.y + (pb[i].y - p.y) * t})));
		})
		.join('');
};

/**
 * A morph through several shapes on a frame timeline: `paths[i]` is shown at `frames[i]` (strictly increasing), eased
 * per segment. It is the 4.0.528 stand-in for interpolatePaths (4.0.529): clamped at both ends.
 */
export const morphAt = (
	frame: number,
	frames: readonly number[],
	paths: readonly string[],
	ease: Ease | readonly Ease[] = curves.inOut,
	mode: MorphMode = 'points',
): string => {
	if (paths.length === 0) {
		return '';
	}
	if (paths.length === 1 || frame <= frames[0]) {
		return paths[0];
	}
	const last = Math.min(frames.length, paths.length) - 1;
	if (frame >= frames[last]) {
		return paths[last];
	}
	let i = 0;
	while (i < last - 1 && frame >= frames[i + 1]) {
		i++;
	}
	if (paths[i] === paths[i + 1]) {
		// a hold: repeat a shape on a later frame to keep it still
		return paths[i];
	}
	const e = Array.isArray(ease) ? (ease as readonly Ease[])[i] ?? curves.inOut : (ease as Ease);
	const t = interpolate(frame, [frames[i], frames[i + 1]], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
	return morphBetween(paths[i], paths[i + 1], t, mode);
};

// ---------------------------------------------------------------- building paths

const f2 = (v: number) => +v.toFixed(2);

/** A circle as a closed path starting at 12 o'clock, going clockwise. */
export const circlePath = (cx: number, cy: number, r: number): string =>
	`M${f2(cx)} ${f2(cy - r)}A${f2(r)} ${f2(r)} 0 1 1 ${f2(cx)} ${f2(cy + r)}A${f2(r)} ${f2(r)} 0 1 1 ${f2(cx)} ${f2(cy - r)}Z`;

/** A rounded rectangle as a closed path. */
export const roundedRectPath = (x: number, y: number, w: number, h: number, r: number): string => {
	const k = Math.max(0, Math.min(r, w / 2, h / 2));
	if (k === 0) {
		return `M${f2(x)} ${f2(y)}H${f2(x + w)}V${f2(y + h)}H${f2(x)}Z`;
	}
	return (
		`M${f2(x + k)} ${f2(y)}H${f2(x + w - k)}A${f2(k)} ${f2(k)} 0 0 1 ${f2(x + w)} ${f2(y + k)}` +
		`V${f2(y + h - k)}A${f2(k)} ${f2(k)} 0 0 1 ${f2(x + w - k)} ${f2(y + h)}` +
		`H${f2(x + k)}A${f2(k)} ${f2(k)} 0 0 1 ${f2(x)} ${f2(y + h - k)}` +
		`V${f2(y + k)}A${f2(k)} ${f2(k)} 0 0 1 ${f2(x + k)} ${f2(y)}Z`
	);
};

/** A regular star (points, outer and inner radius) centred on (cx, cy), first tip at 12 o'clock. */
export const starPath = (cx: number, cy: number, points: number, outer: number, inner: number): string => {
	const pts: PathPoint[] = [];
	for (let i = 0; i < points * 2; i++) {
		const r = i % 2 === 0 ? outer : inner;
		const a = -Math.PI / 2 + (i * Math.PI) / points;
		pts.push({x: cx + r * Math.cos(a), y: cy + r * Math.sin(a)});
	}
	return pts.map((p, i) => `${i ? 'L' : 'M'}${f2(p.x)} ${f2(p.y)}`).join('') + 'Z';
};

/** A polyline (or polygon when closed) through points. */
export const polyPath = (pts: readonly (readonly [number, number])[], closed = false): string =>
	pts.map((p, i) => `${i ? 'L' : 'M'}${f2(p[0])} ${f2(p[1])}`).join('') + (closed ? 'Z' : '');

/**
 * A smooth curve through points (Catmull-Rom as cubic Beziers). `tension` 0 is straight segments, 1 the classic
 * curve; the curve passes through every point.
 */
export const smoothPath = (pts: readonly (readonly [number, number])[], tension = 1, closed = false): string => {
	const n = pts.length;
	if (n < 2) {
		return n === 1 ? `M${f2(pts[0][0])} ${f2(pts[0][1])}` : '';
	}
	const at = (i: number) => (closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))]);
	let d = `M${f2(pts[0][0])} ${f2(pts[0][1])}`;
	const segs = closed ? n : n - 1;
	for (let i = 0; i < segs; i++) {
		const p0 = at(i - 1);
		const p1 = at(i);
		const p2 = at(i + 1);
		const p3 = at(i + 2);
		const k = tension / 6;
		const c1 = [p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k];
		const c2 = [p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k];
		d += `C${f2(c1[0])} ${f2(c1[1])} ${f2(c2[0])} ${f2(c2[1])} ${f2(p2[0])} ${f2(p2[1])}`;
	}
	return closed ? d + 'Z' : d;
};

/**
 * A path from `a` to `b` that bends by `bend` (0 = straight; 0.3 is a gentle arc; negative bends the other way),
 * as one quadratic curve whose control point sits off the middle of the chord.
 */
export const bendPath = (a: readonly [number, number], b: readonly [number, number], bend = 0): string => {
	const [x1, y1] = a;
	const [x2, y2] = b;
	if (Math.abs(bend) < 1e-4) {
		return `M${f2(x1)} ${f2(y1)}L${f2(x2)} ${f2(y2)}`;
	}
	const mx = (x1 + x2) / 2;
	const my = (y1 + y2) / 2;
	const dx = x2 - x1;
	const dy = y2 - y1;
	const len = Math.hypot(dx, dy) || 1;
	// the normal on the left of the direction of travel; bend > 0 arcs to that side
	const nx = dy / len;
	const ny = -dx / len;
	const h = bend * len;
	return `M${f2(x1)} ${f2(y1)}Q${f2(mx + nx * h)} ${f2(my + ny * h)} ${f2(x2)} ${f2(y2)}`;
};
