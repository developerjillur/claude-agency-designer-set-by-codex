// Text to three.js shapes without a typeface file: draw the text with the loaded web font on a canvas (so the
// browser does the shaping, Bangla conjuncts and vowel signs included), trace the anti-aliased alpha with
// marching squares at the 50% level (sub-pixel accurate), simplify, and nest holes inside their outlines.
// Deterministic for a given machine and font; call it only after the font has loaded (useFontsReady).
import * as THREE from 'three';

export type TraceTextOptions = {
	text: string;
	/** CSS font-family stack, e.g. the theme's t.type.display. */
	family: string;
	weight?: number | string;
	italic?: boolean;
	/** Letter spacing in em (the theme's tracking.display). */
	tracking?: number;
	/** Line advance in em. */
	lineHeight?: number;
	align?: 'left' | 'center' | 'right';
	/** World units per em. */
	worldSize: number;
	/** Canvas px per em while tracing: more is smoother and slower. */
	resolution?: number;
	/**
	 * Shrink the glyphs by this much (em) before tracing, in raster space. Pair it with an extrusion bevel of the
	 * same size (bevelOffset 0) so the bevel grows the outline back to the font's own silhouette: the caps then
	 * triangulate a clean contour, where an inset done by three folds acute features (the V inside an M or N).
	 */
	erode?: number;
};

export type TracedPart = {
	/** Outlines with holes, in world units relative to `pivot`. */
	shapes: THREE.Shape[];
	/** Where the part sits in the text block: its centre x and its line's baseline y (world, block centred). */
	pivot: [number, number];
	box: {minX: number; maxX: number; minY: number; maxY: number};
	line: number;
	/** 0 at the block's left edge, 1 at its right: for staggering left to right. */
	x01: number;
};

export type TracedText = {
	parts: TracedPart[];
	width: number;
	height: number;
	/** Per line, the lowest ink (descenders) and highest ink, in world y. */
	lines: {bottom: number; top: number; baseline: number}[];
	box: {minX: number; maxX: number; minY: number; maxY: number};
};

type Loop = {pts: number[]; area: number; minX: number; maxX: number; minY: number; maxY: number};

// ---------------------------------------------------------------- marching squares

const traceLoops = (alpha: Float32Array, W: number, H: number, iso: number): number[][] => {
	const adj = new Map<number, number[]>();
	const pos = new Map<number, [number, number]>();
	const hId = (x: number, y: number) => y * W + x; // edge (x, y) to (x + 1, y)
	const vId = (x: number, y: number) => W * H + y * W + x; // edge (x, y) to (x, y + 1)
	const link = (a: number, b: number) => {
		const la = adj.get(a);
		if (la) {
			la.push(b);
		} else {
			adj.set(a, [b]);
		}
		const lb = adj.get(b);
		if (lb) {
			lb.push(a);
		} else {
			adj.set(b, [a]);
		}
	};
	const at = (x: number, y: number) => alpha[y * W + x];
	for (let y = 0; y < H - 1; y++) {
		for (let x = 0; x < W - 1; x++) {
			const tl = at(x, y);
			const tr = at(x + 1, y);
			const br = at(x + 1, y + 1);
			const bl = at(x, y + 1);
			const code = (tl >= iso ? 8 : 0) | (tr >= iso ? 4 : 0) | (br >= iso ? 2 : 0) | (bl >= iso ? 1 : 0);
			if (code === 0 || code === 15) {
				continue;
			}
			const T = hId(x, y);
			const B = hId(x, y + 1);
			const L = vId(x, y);
			const R = vId(x + 1, y);
			const need = (id: number, px: number, py: number) => {
				if (!pos.has(id)) {
					pos.set(id, [px, py]);
				}
			};
			const top = () => need(T, x + (iso - tl) / (tr - tl), y);
			const bottom = () => need(B, x + (iso - bl) / (br - bl), y + 1);
			const left = () => need(L, x, y + (iso - tl) / (bl - tl));
			const right = () => need(R, x + 1, y + (iso - tr) / (br - tr));
			const seg = (a: number, b: number) => link(a, b);
			switch (code) {
				case 1:
				case 14:
					left();
					bottom();
					seg(L, B);
					break;
				case 2:
				case 13:
					bottom();
					right();
					seg(B, R);
					break;
				case 3:
				case 12:
					left();
					right();
					seg(L, R);
					break;
				case 4:
				case 11:
					top();
					right();
					seg(T, R);
					break;
				case 6:
				case 9:
					top();
					bottom();
					seg(T, B);
					break;
				case 7:
				case 8:
					top();
					left();
					seg(T, L);
					break;
				case 5:
				case 10: {
					top();
					right();
					bottom();
					left();
					const centreIn = (tl + tr + br + bl) / 4 >= iso;
					// the saddle: join the corners that the centre joins
					if ((code === 5) === centreIn) {
						seg(T, L);
						seg(R, B);
					} else {
						seg(T, R);
						seg(L, B);
					}
					break;
				}
				default:
					break;
			}
		}
	}
	const loops: number[][] = [];
	const seen = new Set<number>();
	for (const start of adj.keys()) {
		if (seen.has(start)) {
			continue;
		}
		const pts: number[] = [];
		let prev = -1;
		let cur = start;
		for (let guard = 0; guard < 4_000_000; guard++) {
			seen.add(cur);
			const p = pos.get(cur);
			if (p) {
				pts.push(p[0], p[1]);
			}
			const nb = adj.get(cur) ?? [];
			const next = nb[0] !== prev ? nb[0] : nb[1];
			if (next === undefined || next === start || seen.has(next)) {
				break;
			}
			prev = cur;
			cur = next;
		}
		if (pts.length >= 6) {
			loops.push(pts);
		}
	}
	return loops;
};

// ---------------------------------------------------------------- simplification and nesting

const simplifyOpen = (pts: number[], from: number, to: number, eps: number, keep: Uint8Array) => {
	const stack: [number, number][] = [[from, to]];
	while (stack.length) {
		const [a, b] = stack.pop() as [number, number];
		const ax = pts[a * 2];
		const ay = pts[a * 2 + 1];
		const bx = pts[b * 2];
		const by = pts[b * 2 + 1];
		const dx = bx - ax;
		const dy = by - ay;
		const len = Math.hypot(dx, dy) || 1;
		let best = -1;
		let bestD = eps;
		for (let i = a + 1; i < b; i++) {
			const d = Math.abs((pts[i * 2] - ax) * dy - (pts[i * 2 + 1] - ay) * dx) / len;
			if (d > bestD) {
				bestD = d;
				best = i;
			}
		}
		if (best >= 0) {
			keep[best] = 1;
			stack.push([a, best], [best, b]);
		}
	}
};

/** Douglas-Peucker on a closed loop: split at the point farthest from the first, simplify both halves. */
const simplifyLoop = (pts: number[], eps: number): number[] => {
	const n = pts.length / 2;
	if (n < 8) {
		return pts;
	}
	let far = 0;
	let farD = -1;
	for (let i = 1; i < n; i++) {
		const d = (pts[i * 2] - pts[0]) ** 2 + (pts[i * 2 + 1] - pts[1]) ** 2;
		if (d > farD) {
			farD = d;
			far = i;
		}
	}
	const closed = pts.concat([pts[0], pts[1]]);
	const keep = new Uint8Array(n + 1);
	keep[0] = 1;
	keep[far] = 1;
	keep[n] = 1;
	simplifyOpen(closed, 0, far, eps, keep);
	simplifyOpen(closed, far, n, eps, keep);
	const out: number[] = [];
	for (let i = 0; i < n; i++) {
		if (keep[i]) {
			out.push(pts[i * 2], pts[i * 2 + 1]);
		}
	}
	return out;
};

const makeLoop = (pts: number[]): Loop => {
	let area = 0;
	let minX = Infinity;
	let maxX = -Infinity;
	let minY = Infinity;
	let maxY = -Infinity;
	const n = pts.length / 2;
	for (let i = 0; i < n; i++) {
		const x = pts[i * 2];
		const y = pts[i * 2 + 1];
		const j = (i + 1) % n;
		area += x * pts[j * 2 + 1] - pts[j * 2] * y;
		minX = Math.min(minX, x);
		maxX = Math.max(maxX, x);
		minY = Math.min(minY, y);
		maxY = Math.max(maxY, y);
	}
	return {pts, area: area / 2, minX, maxX, minY, maxY};
};

const inside = (loop: Loop, x: number, y: number): boolean => {
	if (x < loop.minX || x > loop.maxX || y < loop.minY || y > loop.maxY) {
		return false;
	}
	const p = loop.pts;
	const n = p.length / 2;
	let hit = false;
	for (let i = 0, j = n - 1; i < n; j = i++) {
		const xi = p[i * 2];
		const yi = p[i * 2 + 1];
		const xj = p[j * 2];
		const yj = p[j * 2 + 1];
		if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
			hit = !hit;
		}
	}
	return hit;
};

// ---------------------------------------------------------------- erosion

/**
 * Min filter over a disk of radius `r` px on the anti-aliased coverage: moves every edge inwards by r, whatever
 * the font's contours look like (variable fonts keep overlapping contours, so stroking them would cut the glyph).
 */
const erodeAlpha = (alpha: Float32Array, W: number, H: number, r: number): Float32Array => {
	const R = Math.max(0, Math.round(r));
	if (R < 1) {
		return alpha;
	}
	const offs: number[] = [];
	for (let dy = -R; dy <= R; dy++) {
		for (let dx = -R; dx <= R; dx++) {
			if (dx * dx + dy * dy <= r * r + 0.25) {
				offs.push(dx, dy);
			}
		}
	}
	const out = new Float32Array(alpha.length);
	for (let y = 0; y < H; y++) {
		for (let x = 0; x < W; x++) {
			const i = y * W + x;
			if (alpha[i] <= 0) {
				continue;
			}
			let m = alpha[i];
			for (let k = 0; k < offs.length && m > 0; k += 2) {
				const xx = x + offs[k];
				const yy = y + offs[k + 1];
				const v = xx < 0 || yy < 0 || xx >= W || yy >= H ? 0 : alpha[yy * W + xx];
				if (v < m) {
					m = v;
				}
			}
			out[i] = m;
		}
	}
	return out;
};

// ---------------------------------------------------------------- the whole pipeline

const MAX_W = 8192;
const MAX_PIXELS = 12_000_000;

export const traceText = ({
	text,
	family,
	weight = 800,
	italic = false,
	tracking = 0,
	lineHeight = 1.08,
	align = 'center',
	worldSize,
	resolution = 220,
	erode = 0,
}: TraceTextOptions): TracedText => {
	const lines = text.split('\n');
	const canvas = document.createElement('canvas');
	const ctx = canvas.getContext('2d', {willReadFrequently: true});
	if (!ctx) {
		throw new Error('traceText: no 2D canvas');
	}
	const fontAt = (R: number) => `${italic ? 'italic ' : ''}${weight} ${R}px ${family}`;
	const setup = (R: number) => {
		ctx.font = fontAt(R);
		ctx.textAlign = 'left';
		ctx.textBaseline = 'alphabetic';
		const c = ctx as CanvasRenderingContext2D & {letterSpacing?: string};
		if ('letterSpacing' in c) {
			c.letterSpacing = `${tracking * R}px`;
		}
	};
	// measure at the requested resolution, then shrink it if the canvas would be too big
	let R = resolution;
	const measure = () => {
		setup(R);
		return lines.map((l) => {
			const m = ctx.measureText(l || ' ');
			return {left: m.actualBoundingBoxLeft, right: m.actualBoundingBoxRight, asc: m.fontBoundingBoxAscent, desc: m.fontBoundingBoxDescent};
		});
	};
	let ms = measure();
	const size = () => {
		const pad = Math.ceil(R * 0.2) + 4;
		const inkW = Math.max(1, ...ms.map((m) => m.left + m.right));
		const adv = lineHeight * R;
		const asc = Math.max(...ms.map((m) => m.asc));
		const desc = Math.max(...ms.map((m) => m.desc));
		return {pad, inkW, adv, asc, desc, W: Math.ceil(inkW + pad * 2), H: Math.ceil(asc + desc + adv * (lines.length - 1) + pad * 2)};
	};
	let s = size();
	const shrink = Math.min(1, MAX_W / s.W, Math.sqrt(MAX_PIXELS / (s.W * s.H)));
	if (shrink < 1) {
		R = Math.max(48, Math.floor(R * shrink));
		ms = measure();
		s = size();
	}
	canvas.width = s.W;
	canvas.height = s.H;
	setup(R); // resizing a canvas resets its state
	ctx.fillStyle = '#ffffff';
	const baselines: number[] = [];
	lines.forEach((l, i) => {
		const m = ms[i];
		const w = m.left + m.right;
		const x0 = align === 'left' ? s.pad : align === 'right' ? s.pad + s.inkW - w : s.pad + (s.inkW - w) / 2;
		const y = s.pad + s.asc + i * s.adv;
		baselines.push(y);
		if (l) {
			ctx.fillText(l, x0 + m.left, y);
		}
	});
	const data = ctx.getImageData(0, 0, s.W, s.H).data;
	let alpha: Float32Array = new Float32Array(s.W * s.H);
	for (let i = 0; i < alpha.length; i++) {
		alpha[i] = data[i * 4 + 3] / 255;
	}
	if (erode > 0) {
		alpha = erodeAlpha(alpha, s.W, s.H, erode * R);
	}
	const eps = Math.max(0.18, R / 900);
	const loops = traceLoops(alpha, s.W, s.H, 0.5)
		.map((l) => makeLoop(simplifyLoop(l, eps)))
		.filter((l) => Math.abs(l.area) > R * R * 0.00004);
	// nesting: a loop inside an even number of loops is an outline, inside an odd number a hole
	const order = [...loops].sort((a, b) => Math.abs(b.area) - Math.abs(a.area));
	const depth = new Map<Loop, number>();
	const parent = new Map<Loop, Loop | null>();
	order.forEach((l, i) => {
		let d = 0;
		let smallest: Loop | null = null;
		for (let j = 0; j < i; j++) {
			const o = order[j];
			if (inside(o, l.pts[0], l.pts[1])) {
				d++;
				if (!smallest || Math.abs(o.area) < Math.abs(smallest.area)) {
					smallest = o;
				}
			}
		}
		depth.set(l, d);
		parent.set(l, smallest);
	});
	if (!loops.length) {
		return {parts: [], width: 0, height: 0, lines: [], box: {minX: 0, maxX: 0, minY: 0, maxY: 0}};
	}
	// block box in canvas px, then world transform: centre the ink box at the origin, y up
	const minX = Math.min(...loops.map((l) => l.minX));
	const maxX = Math.max(...loops.map((l) => l.maxX));
	const minY = Math.min(...loops.map((l) => l.minY));
	const maxY = Math.max(...loops.map((l) => l.maxY));
	const k = worldSize / R;
	const cx = (minX + maxX) / 2;
	const cy = (minY + maxY) / 2;
	const wx = (x: number) => (x - cx) * k;
	const wy = (y: number) => (cy - y) * k;
	const lineOf = (yMid: number) => {
		let best = 0;
		let bestD = Infinity;
		baselines.forEach((b, i) => {
			// the ink of a line sits between its ascent and its descent
			const mid = b - s.asc * 0.35;
			const d = Math.abs(yMid - mid);
			if (d < bestD) {
				bestD = d;
				best = i;
			}
		});
		return best;
	};
	const outlines = order.filter((l) => (depth.get(l) ?? 0) % 2 === 0);
	const parts: TracedPart[] = outlines.map((o) => {
		const holes = order.filter((h) => parent.get(h) === o && (depth.get(h) ?? 0) % 2 === 1);
		const line = lineOf((o.minY + o.maxY) / 2);
		const px = wx((o.minX + o.maxX) / 2);
		const py = wy(baselines[line]);
		const toV = (pts: number[]) => {
			const out: THREE.Vector2[] = [];
			for (let i = 0; i < pts.length; i += 2) {
				out.push(new THREE.Vector2(wx(pts[i]) - px, wy(pts[i + 1]) - py));
			}
			return out;
		};
		// ExtrudeGeometry wants outlines clockwise and holes counter-clockwise, and only fixes the holes when it had
		// to reverse the outline: traced loops come in either direction, so set both here
		const outline = toV(o.pts);
		if (!THREE.ShapeUtils.isClockWise(outline)) {
			outline.reverse();
		}
		const shape = new THREE.Shape(outline);
		holes.forEach((h) => {
			const hv = toV(h.pts);
			if (THREE.ShapeUtils.isClockWise(hv)) {
				hv.reverse();
			}
			shape.holes.push(new THREE.Path(hv));
		});
		return {
			shapes: [shape],
			pivot: [px, py],
			box: {minX: wx(o.minX), maxX: wx(o.maxX), minY: wy(o.maxY), maxY: wy(o.minY)},
			line,
			x01: maxX > minX ? ((o.minX + o.maxX) / 2 - minX) / (maxX - minX) : 0,
		};
	});
	parts.sort((a, b) => a.line - b.line || a.x01 - b.x01);
	const lineInfo = baselines.map((b, i) => {
		const own = parts.filter((p) => p.line === i);
		const bottom = own.length ? Math.min(...own.map((p) => p.box.minY)) : wy(b + s.desc);
		const top = own.length ? Math.max(...own.map((p) => p.box.maxY)) : wy(b - s.asc);
		return {bottom, top, baseline: wy(b)};
	});
	return {
		parts,
		width: (maxX - minX) * k,
		height: (maxY - minY) * k,
		lines: lineInfo,
		box: {minX: wx(minX), maxX: wx(maxX), minY: wy(maxY), maxY: wy(minY)},
	};
};
