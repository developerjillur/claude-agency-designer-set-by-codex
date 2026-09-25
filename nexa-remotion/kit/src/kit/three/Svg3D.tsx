// <Svg3D>: an extruded, lit vector shape drawn as plain SVG, no WebGL (so it renders anywhere, fast, at any
// concurrency). The side walls come from @remotion/svg-3d-engine's extrudeElement (curves subdivided so walls
// follow them); the caps, the lighting, hole-aware normals, back-face culling, depth sorting, perspective and the
// content on the front face are ours.
import {getBoundingBox, getSubpaths, parsePath, reduceInstructions, scalePath, translatePath} from '@remotion/paths';
import {makeCircle, makeHeart, makePolygon, makeRect, makeStar, makeTriangle} from '@remotion/shapes';
import {
	extrudeElement,
	reduceMatrices,
	rotateX,
	rotateY,
	rotateZ,
	threeDIntoSvgPath,
	type MatrixTransform4D,
	type ThreeDReducedInstruction,
	type Vector4D,
} from '@remotion/svg-3d-engine';
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp, springAt} from '../motion';
import {shade, type Vec3} from './util';

export type Svg3DShape = 'star' | 'heart' | 'badge' | 'hexagon' | 'rect' | 'circle' | 'triangle';

export type Svg3DProps = {
	/** Any SVG path (subpaths become separate solids); or use `shape`. */
	path?: string;
	shape?: Svg3DShape;
	/** The shape's longer side in px at 1080. */
	size?: number;
	/** Extrusion depth in px at 1080. */
	depth?: number;
	/** Front face colour. */
	color?: string;
	/** Wall colour; default the face colour darkened. */
	sideColor?: string;
	/** Base orientation, degrees (CSS conventions: +x tips the top away, +y turns the right side away). */
	rotateX?: number;
	rotateY?: number;
	rotateZ?: number;
	/** An eased turn about the shape's own vertical axis, degrees, over `delay` .. `delay + duration`. */
	turnFrom?: number;
	turnTo?: number;
	delay?: number;
	duration?: number;
	ease?: Ease;
	enter?: 'pop' | 'flip' | 'none';
	enterDuration?: number;
	/** Bob in px at 1080. */
	float?: number;
	/** Direction the light comes from (x right, y down, z toward the viewer). */
	light?: Vec3;
	/** Perspective distance in px at 1080; 0 for orthographic. */
	perspective?: number;
	/** Centre in px at 1080 from the frame centre (y down). */
	x?: number;
	y?: number;
	/** SVG content on the front face, in the face's own coordinates (centred on 0, 0, px at the drawn size). */
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

/** The path of a preset, about `size` px across. */
export const svg3dShapePath = (shape: Svg3DShape, size: number): string => {
	const r = size / 2;
	switch (shape) {
		case 'star':
			return makeStar({points: 5, innerRadius: r * 0.48, outerRadius: r, cornerRadius: r * 0.08}).path;
		case 'heart':
			return makeHeart({height: size * 0.9}).path;
		case 'badge':
			return makeStar({points: 14, innerRadius: r * 0.88, outerRadius: r, cornerRadius: r * 0.05}).path;
		case 'hexagon':
			return makePolygon({points: 6, radius: r, cornerRadius: r * 0.12}).path;
		case 'rect':
			return makeRect({width: size, height: size * 0.62, cornerRadius: size * 0.1}).path;
		case 'triangle':
			return makeTriangle({length: size, direction: 'up', cornerRadius: size * 0.08}).path;
		case 'circle':
		default:
			return makeCircle({radius: r}).path;
	}
};

const mul = (m: MatrixTransform4D, p: Vector4D): Vector4D => [
	m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3] * p[3],
	m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7] * p[3],
	m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11] * p[3],
	m[12] * p[0] + m[13] * p[1] + m[14] * p[2] + m[15] * p[3],
];

const mapInstruction = (ins: ThreeDReducedInstruction, f: (p: Vector4D) => Vector4D): ThreeDReducedInstruction => {
	switch (ins.type) {
		case 'C':
			return {type: 'C', cp1: f(ins.cp1), cp2: f(ins.cp2), point: f(ins.point)};
		case 'Q':
			return {type: 'Q', cp: f(ins.cp), point: f(ins.point)};
		default:
			return {type: ins.type, point: f(ins.point)};
	}
};

/** A 2D subpath as 3D instructions at depth z (M, L, C and Z only). */
const cap = (d: string, z: number): ThreeDReducedInstruction[] => {
	const out: ThreeDReducedInstruction[] = [];
	let start: Vector4D = [0, 0, z, 1];
	for (const ins of reduceInstructions(parsePath(d))) {
		if (ins.type === 'M') {
			start = [ins.x, ins.y, z, 1];
			out.push({type: 'M', point: start});
		} else if (ins.type === 'L') {
			out.push({type: 'L', point: [ins.x, ins.y, z, 1]});
		} else if (ins.type === 'C') {
			out.push({type: 'C', cp1: [ins.cp1x, ins.cp1y, z, 1], cp2: [ins.cp2x, ins.cp2y, z, 1], point: [ins.x, ins.y, z, 1]});
		} else {
			out.push({type: 'Z', point: start});
		}
	}
	return out;
};

const points = (ins: ThreeDReducedInstruction[]): Vector4D[] => ins.map((i) => i.point);

type Face = {d: string; fill: string; z: number; seam: boolean};

export const Svg3D: React.FC<Svg3DProps> = ({
	path,
	shape = 'star',
	size = 360,
	depth = 70,
	color,
	sideColor,
	rotateX: rx = -12,
	rotateY: ry = 0,
	rotateZ: rz = 0,
	turnFrom = -30,
	turnTo = 30,
	delay = 0,
	duration,
	ease = curves.inOut,
	enter = 'pop',
	enterDuration,
	float = 8,
	light = [-0.45, -0.7, 0.55],
	perspective = 1800,
	x = 0,
	y = 0,
	children,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, unit, fps, durationInFrames} = useStage();
	const face = color ?? t.colors.accent;
	const wall = sideColor ?? shade(face, 0.72);
	const px = size * unit;
	const dz = depth * unit;

	// the shape centred on 0, 0 at the drawn size, split into its subpaths
	const subs = useMemo(() => {
		const raw = path ?? svg3dShapePath(shape, 100);
		const bb = getBoundingBox(raw);
		const k = px / Math.max(bb.width, bb.height, 1e-6);
		// scalePath re-zeroes the path at its top-left corner, so scale first and centre afterwards
		const scaled = scalePath(raw, k, k);
		const sb = getBoundingBox(scaled);
		const centred = translatePath(scaled, -(sb.x1 + sb.width / 2), -(sb.y1 + sb.height / 2));
		return getSubpaths(centred);
	}, [path, shape, px]);

	// the walls in the shape's own space, each with its outward normal. Outward is decided by an even-odd inside
	// test next to the edge, so holes (a ring, a letter O) get walls that face into the hole.
	const walls = useMemo(() => {
		const raw = subs.map((sub) => extrudeElement({depth: dz, pressInDepth: 0, sideColor: '#000', points: parsePath(sub), crispEdges: false}));
		const polys = raw.map((ws) => ws.map((w) => [w.points[0].point[0], w.points[0].point[1]] as [number, number]));
		const insideAll = (x: number, y: number) => {
			let hit = false;
			for (const p of polys) {
				for (let i = 0, j = p.length - 1; i < p.length; j = i++) {
					if (p[i][1] > y !== p[j][1] > y && x < ((p[j][0] - p[i][0]) * (y - p[i][1])) / (p[j][1] - p[i][1]) + p[i][0]) {
						hit = !hit;
					}
				}
			}
			return hit;
		};
		const eps = Math.max(0.25, px * 0.002);
		const out: {ins: ThreeDReducedInstruction[]; n: [number, number]}[] = [];
		for (const ws of raw) {
			for (const w of ws) {
				const a = w.points[0]?.point;
				const b = w.points[1]?.point;
				if (!a || !b) {
					continue;
				}
				const ex = b[0] - a[0];
				const ey = b[1] - a[1];
				const len = Math.hypot(ex, ey);
				if (len < 1e-6) {
					continue;
				}
				let nx = ey / len;
				let ny = -ex / len;
				if (insideAll((a[0] + b[0]) / 2 + nx * eps, (a[1] + b[1]) / 2 + ny * eps)) {
					nx = -nx;
					ny = -ny;
				}
				out.push({ins: w.points, n: [nx, ny]});
			}
		}
		return out;
	}, [subs, dz, px]);

	// motion
	const turnFrames = duration ?? Math.max(1, durationInFrames - delay);
	const turn = turnFrom + (turnTo - turnFrom) * (Number.isFinite(turnFrames) ? ramp(frame, delay, turnFrames, ease) : 0);
	const eDur = enterDuration ?? at30(24, fps);
	let scale = 1;
	let flip = 0;
	if (enter === 'pop') {
		scale = Math.max(0.001, springAt(frame, fps, {delay, config: 'pop', durationInFrames: eDur}));
		flip = -(1 - Math.min(1, ramp(frame, delay, eDur, curves.out))) * 70;
	} else if (enter === 'flip') {
		const k = ramp(frame, delay, eDur, curves.outBack);
		flip = -(1 - k) * 90;
		scale = Math.max(0.001, Math.min(1, ramp(frame, delay, eDur) * 3));
	}
	const bob = float ? float * unit * Math.sin((2 * Math.PI * frame) / (fps * 3.2)) * ramp(frame, delay, fps, curves.sine) : 0;

	const rad = Math.PI / 180;
	// spin about the shape's own vertical axis first, then tilt it in view space
	const M = reduceMatrices([rotateY((ry + turn) * rad), rotateX((rx + flip) * rad), rotateZ(rz * rad)]);
	const L = (() => {
		const l = Math.hypot(light[0], light[1], light[2]) || 1;
		return [light[0] / l, light[1] / l, light[2] / l] as Vec3;
	})();
	const f = perspective > 0 ? perspective * unit : 0;
	const project = (p: Vector4D): Vector4D => {
		const k = f > 0 ? f / Math.max(1, f - p[2] * scale) : 1;
		return [p[0] * scale * k, p[1] * scale * k, p[2] * scale, 1];
	};
	const lit = (n: Vec3) => Math.max(0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2]);

	const faces: Face[] = [];
	const frontN = mul(M, [0, 0, 1, 0]);
	const frontFacing = frontN[2] >= 0;
	for (const w of walls) {
		const n4 = mul(M, [w.n[0], w.n[1], 0, 0]);
		if (n4[2] < -0.02) {
			continue; // faces away from the viewer
		}
		const tp = w.ins.map((i) => mapInstruction(i, (p) => mul(M, p)));
		const pts = points(tp);
		const z = pts.reduce((a, p) => a + p[2], 0) / pts.length;
		faces.push({d: threeDIntoSvgPath(tp.map((i) => mapInstruction(i, project))), fill: shade(wall, 0.55 + 0.62 * lit([n4[0], n4[1], n4[2]])), z, seam: true});
	}
	faces.sort((a, b) => a.z - b.z);
	// the cap that faces the viewer goes on top (nothing of the same solid can cover it), all subpaths in one
	// even-odd path so holes stay open
	const capZ = frontFacing ? dz / 2 : -dz / 2;
	const capN: Vec3 = frontFacing ? [frontN[0], frontN[1], frontN[2]] : [-frontN[0], -frontN[1], -frontN[2]];
	const capD = subs
		.map((sub) => threeDIntoSvgPath(cap(sub, capZ).map((i) => mapInstruction(mapInstruction(i, (p) => mul(M, p)), project))))
		.join(' ');
	const capFill = frontFacing ? shade(face, 0.86 + 0.3 * lit(capN)) : shade(wall, 0.7 + 0.4 * lit(capN));

	// the front face's plane as an affine SVG transform (exact when orthographic, at the centre with perspective)
	const zc = mul(M, [0, 0, dz / 2, 1])[2];
	const kc = (f > 0 ? f / Math.max(1, f - zc * scale) : 1) * scale;
	const o = mul(M, [0, 0, dz / 2, 1]);
	const faceMatrix = `matrix(${M[0] * kc} ${M[4] * kc} ${M[1] * kc} ${M[5] * kc} ${o[0] * kc} ${o[1] * kc})`;

	const cx = width / 2 + x * unit;
	const cy = height / 2 + y * unit + bob;
	return (
		<AbsoluteFill style={{pointerEvents: 'none', ...style}}>
			<svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<g transform={`translate(${cx} ${cy})`}>
					{faces.map((fc, i) => (
						<path key={i} d={fc.d} fill={fc.fill} stroke={fc.seam ? fc.fill : 'none'} strokeWidth={fc.seam ? 0.9 * unit : 0} strokeLinejoin="round" />
					))}
					<path d={capD} fill={capFill} fillRule="evenodd" />
					{children && frontFacing ? <g transform={faceMatrix}>{children}</g> : null}
				</g>
			</svg>
		</AbsoluteFill>
	);
};
