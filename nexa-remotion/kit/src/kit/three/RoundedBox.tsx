// Rounded shapes: a rounded-rectangle Shape, a flat rounded plane with 0..1 UVs (for screens, cards and
// labels), and RoundedBox, an extruded rounded rectangle with bevelled edges (devices, cards, bars, tiles).
import type {ThreeElements} from '@react-three/fiber';
import React, {useEffect, useMemo} from 'react';
import * as THREE from 'three';

/** A rounded rectangle centred on the origin (radius clamped to half the shorter side). */
export const roundedRectShape = (width: number, height: number, radius: number): THREE.Shape => {
	const w = Math.max(1e-4, width);
	const h = Math.max(1e-4, height);
	const r = Math.max(0, Math.min(radius, w / 2, h / 2));
	const x = -w / 2;
	const y = -h / 2;
	const s = new THREE.Shape();
	s.moveTo(x + r, y);
	s.lineTo(x + w - r, y);
	s.absarc(x + w - r, y + r, r, -Math.PI / 2, 0, false);
	s.lineTo(x + w, y + h - r);
	s.absarc(x + w - r, y + h - r, r, 0, Math.PI / 2, false);
	s.lineTo(x + r, y + h);
	s.absarc(x + r, y + h - r, r, Math.PI / 2, Math.PI, false);
	s.lineTo(x, y + r);
	s.absarc(x + r, y + r, r, Math.PI, Math.PI * 1.5, false);
	return s;
};

/** Maps a geometry's UVs to 0..1 over its bounding box, so a texture covers a shape exactly once. */
export const normalizeUvs = (geo: THREE.BufferGeometry): THREE.BufferGeometry => {
	geo.computeBoundingBox();
	const box = geo.boundingBox;
	const pos = geo.getAttribute('position');
	if (!box || !pos) {
		return geo;
	}
	const w = box.max.x - box.min.x || 1;
	const h = box.max.y - box.min.y || 1;
	const uv = new Float32Array(pos.count * 2);
	for (let i = 0; i < pos.count; i++) {
		uv[i * 2] = (pos.getX(i) - box.min.x) / w;
		uv[i * 2 + 1] = (pos.getY(i) - box.min.y) / h;
	}
	geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
	return geo;
};

/** A flat rounded rectangle in the XY plane with 0..1 UVs. */
export const roundedPlaneGeometry = (width: number, height: number, radius: number, segments = 16): THREE.BufferGeometry =>
	normalizeUvs(new THREE.ShapeGeometry(roundedRectShape(width, height, radius), segments));

/**
 * An extruded rounded rectangle, centred, `depth` thick, with rounded (bevelled) edges of `bevel`. Front face at
 * z = +depth / 2. Groups: 0 the front and back faces, 1 the sides (pass two materials to colour them apart).
 */
export const roundedBoxGeometry = (
	width: number,
	height: number,
	depth: number,
	radius: number,
	bevel = Math.min(width, height, depth) * 0.12,
	bevelSegments = 4,
	curveSegments = 12,
): THREE.ExtrudeGeometry => {
	const b = Math.max(0, Math.min(bevel, width / 2 - 1e-3, height / 2 - 1e-3, depth / 2 - 1e-3));
	const core = Math.max(1e-4, depth - 2 * b);
	const shape = roundedRectShape(width - 2 * b, height - 2 * b, Math.max(0, radius - b));
	const geo = new THREE.ExtrudeGeometry(shape, {
		depth: core,
		bevelEnabled: b > 0,
		bevelThickness: b,
		bevelSize: b,
		bevelSegments,
		curveSegments,
	});
	geo.translate(0, 0, -core / 2);
	return geo;
};

export type RoundedBoxProps = Omit<ThreeElements['mesh'], 'args' | 'geometry'> & {
	width?: number;
	height?: number;
	depth?: number;
	radius?: number;
	bevel?: number;
	bevelSegments?: number;
	color?: string;
	roughness?: number;
	metalness?: number;
	/** A material element to use instead of the default MeshStandardMaterial. */
	material?: React.ReactNode;
};

/** A rounded box in world units (default 1 x 1 x 1, radius 0.18) with a standard material in `color`. */
export const RoundedBox: React.FC<RoundedBoxProps> = ({
	width = 1,
	height = 1,
	depth = 1,
	radius = 0.18,
	bevel,
	bevelSegments = 4,
	color = '#d7dbe2',
	roughness = 0.45,
	metalness = 0.05,
	material,
	children,
	...mesh
}) => {
	const geo = useMemo(
		() => roundedBoxGeometry(width, height, depth, radius, bevel, bevelSegments),
		[width, height, depth, radius, bevel, bevelSegments],
	);
	useEffect(() => () => geo.dispose(), [geo]);
	return (
		<mesh geometry={geo} castShadow receiveShadow {...mesh}>
			{material ?? <meshStandardMaterial color={color} roughness={roughness} metalness={metalness} />}
			{children}
		</mesh>
	);
};
