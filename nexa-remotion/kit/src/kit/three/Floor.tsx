// <Floor>: a ground that never shows an edge. It draws only what grounds a scene: shadows (a transparent shadow
// catcher, when Scene3D has `shadows`) and an optional grid that fades out radially into the CSS background.
import React, {useEffect, useMemo} from 'react';
import * as THREE from 'three';
import {useTheme} from '../core';
import {useScene3D} from './Scene3D';
import {mix} from './util';

export type FloorProps = {
	/** World y of the floor. */
	y?: number;
	/** Grid spacing in world units, or false for no grid. */
	grid?: number | false;
	gridColor?: string;
	gridOpacity?: number;
	/** Radius in world units where the grid has faded out. */
	fade?: number;
	/** Darkness of received shadows (needs Scene3D `shadows` and meshes with castShadow). */
	shadowOpacity?: number;
	/** Size of the shadow catcher in world units. */
	size?: number;
};

const gridTexture = (fadePx: number, stepPx: number, line: number): THREE.CanvasTexture => {
	const S = 1024;
	const c = document.createElement('canvas');
	c.width = S;
	c.height = S;
	const ctx = c.getContext('2d') as CanvasRenderingContext2D;
	ctx.strokeStyle = '#ffffff';
	ctx.lineWidth = line;
	const mid = S / 2;
	for (let o = 0; o <= mid; o += stepPx) {
		for (const p of o === 0 ? [mid] : [mid - o, mid + o]) {
			ctx.beginPath();
			ctx.moveTo(p, 0);
			ctx.lineTo(p, S);
			ctx.moveTo(0, p);
			ctx.lineTo(S, p);
			ctx.stroke();
		}
	}
	// radial fade: keep the grid where the gradient is opaque
	ctx.globalCompositeOperation = 'destination-in';
	const g = ctx.createRadialGradient(mid, mid, 0, mid, mid, fadePx);
	g.addColorStop(0, 'rgba(0,0,0,1)');
	g.addColorStop(0.55, 'rgba(0,0,0,0.6)');
	g.addColorStop(1, 'rgba(0,0,0,0)');
	ctx.fillStyle = g;
	ctx.fillRect(0, 0, S, S);
	const tex = new THREE.CanvasTexture(c);
	tex.anisotropy = 8;
	return tex;
};

export const Floor: React.FC<FloorProps> = ({y = 0, grid = 1, gridColor, gridOpacity, fade = 7, shadowOpacity, size = 60}) => {
	const t = useTheme();
	const s = useScene3D();
	const span = fade * 2;
	const tex = useMemo(() => (grid === false ? null : gridTexture(512, Math.max(4, (grid / span) * 1024), 2.2)), [grid, span]);
	useEffect(() => () => tex?.dispose(), [tex]);
	const color = gridColor ?? (t.dark ? mix(t.colors.bg, '#ffffff', 0.5) : mix(t.colors.bg, t.colors.text, 0.55));
	return (
		<group position={[0, y, 0]}>
			<mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow renderOrder={-1}>
				<planeGeometry args={[size, size]} />
				<shadowMaterial transparent opacity={shadowOpacity ?? (s.dark ? 0.5 : 0.2)} depthWrite={false} />
			</mesh>
			{tex ? (
				<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, 0]} renderOrder={-1}>
					<planeGeometry args={[span, span]} />
					<meshBasicMaterial map={tex} color={color} transparent opacity={gridOpacity ?? (s.dark ? 0.35 : 0.3)} depthWrite={false} toneMapped={false} polygonOffset polygonOffsetFactor={-1} polygonOffsetUnits={-2} />
				</mesh>
			) : null}
		</group>
	);
};
