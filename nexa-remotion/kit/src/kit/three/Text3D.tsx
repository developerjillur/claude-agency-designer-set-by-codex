// <Text3D>: extruded, bevelled 3D type in the theme's display font (any loaded web font, Bangla included),
// with staggered reveals. The glyph outlines come from traceText (the browser shapes the text, we trace it),
// because three no longer ships typeface fonts and TextGeometry cannot shape Bangla.
import type {ThreeElements} from '@react-three/fiber';
import React, {useEffect, useLayoutEffect, useMemo, useRef} from 'react';
import {useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {FONTS, at30, curves, useStage, useTheme, type Ease} from '../core';
import {ramp, springAt} from '../motion';
import {useFontsReady, useHoldUntil, type KitFontRef} from './hooks';
import {useScene3D} from './Scene3D';
import {traceText} from './traceText';
import {shade} from './util';

export type Text3DReveal = 'rise' | 'flip' | 'drop' | 'extrude' | 'wipe' | 'none';
export type Text3DExit = 'sink' | 'flip' | 'drop' | 'wipe' | 'none';
export type Text3DLook = 'duo' | 'solid' | 'metal' | 'glossy';

export type Text3DProps = Omit<ThreeElements['group'], 'children'> & {
	text: string;
	/** Font size (the em) in px at 1080, like 2D type. */
	size?: number;
	/** Extrusion depth in em. */
	depth?: number;
	/** Rounded edge in em (0 for sharp edges). */
	bevel?: number;
	/** CSS font-family stack; default the theme's display stack. */
	font?: string;
	weight?: number;
	italic?: boolean;
	/** Letter spacing in em; default the theme's display tracking. */
	tracking?: number;
	lineHeight?: number;
	align?: 'left' | 'center' | 'right';
	/** Capitals; default the theme's `caps`. */
	caps?: boolean;
	/** World units the text may span before it is scaled down; default 96% of the safe width. */
	maxWidth?: number;
	/** Face colour (exact, unlit in the duo and solid looks). */
	color?: string;
	/** Side and bevel colour. */
	sideColor?: string;
	look?: Text3DLook;
	in?: Text3DReveal;
	out?: Text3DExit;
	delay?: number;
	/** Frames each part takes to arrive. */
	duration?: number;
	/** Frames between the first and the last part (left to right, line by line). */
	stagger?: number;
	outDuration?: number;
	/** Local frame the exit starts; default so it ends on the last frame of the Sequence. */
	outAt?: number;
	ease?: Ease;
	/** Canvas px per em while tracing (220 default; raise for very large type). */
	resolution?: number;
};

const FAR = 1e6;

export const Text3D: React.FC<Text3DProps> = ({
	text,
	size = 150,
	depth = 0.22,
	bevel = 0.016,
	font,
	weight,
	italic = false,
	tracking,
	lineHeight = 1.05,
	align = 'center',
	caps,
	maxWidth,
	color,
	sideColor,
	look = 'duo',
	in: reveal = 'rise',
	out = 'none',
	delay = 0,
	duration,
	stagger,
	outDuration,
	outAt,
	ease,
	resolution = 220,
	...group
}) => {
	const t = useTheme();
	const s = useScene3D();
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useStage();

	const family = font ?? t.type.display;
	const w = weight ?? t.weights.display;
	const shown = caps ?? t.caps ? text.toUpperCase() : text;
	const track = tracking ?? t.tracking.display;
	const em = s.px(size);
	const thickEm = Math.max(0.002, depth);
	// the traced outline is eroded by the bevel size and the bevel grows it back: true silhouette, clean caps
	const bevelEm = Math.max(0, Math.min(bevel, thickEm * 0.45));
	// theme fonts: wait on the kit's loaders (see useFontsReady); a custom stack is polled by family name
	const kit = useMemo<KitFontRef[]>(
		() => (font ? [] : [{key: t.fonts.display, weights: [w], italic}, ...(FONTS[t.fonts.display].bangla ? [] : [{key: t.fonts.bangla, weights: [w]}])]),
		[font, t.fonts.display, t.fonts.bangla, w, italic],
	);
	const ready = useFontsReady([`${italic ? 'italic ' : ''}${w} 100px ${family}`], shown, kit);

	const traced = useMemo(
		() =>
			ready
				? traceText({text: shown, family, weight: w, italic, tracking: track, lineHeight, align, worldSize: em, resolution, erode: bevelEm})
				: null,
		[ready, shown, family, w, italic, track, lineHeight, align, em, resolution, bevelEm],
	);
	useHoldUntil(traced !== null, `Text3D tracing "${shown.slice(0, 24)}"`);

	const thick = thickEm * em;
	const bv = bevelEm * em;
	const geos = useMemo(() => {
		if (!traced) {
			return [];
		}
		const core = Math.max(0.0005, thick - 2 * bv);
		return traced.parts.map((p) => {
			const g = new THREE.ExtrudeGeometry(p.shapes, {
				depth: core,
				bevelEnabled: bv > 0,
				bevelThickness: bv,
				bevelSize: bv,
				bevelOffset: 0, // the outline was eroded by bv while tracing, so the bevel restores the true outline
				bevelSegments: 3,
				curveSegments: 1,
				steps: 1,
			});
			g.translate(0, 0, -(core + bv)); // front face at z = 0, depth grows backwards
			return g;
		});
	}, [traced, thick, bv]);
	useEffect(() => () => geos.forEach((g) => g.dispose()), [geos]);

	// per line: a floor plane (rise, sink), a wipe-in plane and a wipe-out plane, placed in world space each frame
	const planes = useMemo(
		() =>
			(traced?.lines ?? []).map(() => ({
				floor: new THREE.Plane(new THREE.Vector3(0, 1, 0), FAR),
				wipeIn: new THREE.Plane(new THREE.Vector3(-1, 0, 0), FAR),
				wipeOut: new THREE.Plane(new THREE.Vector3(1, 0, 0), FAR),
			})),
		[traced],
	);

	// metal needs a light base colour to read as metal: silver on dark grounds, gunmetal on light ones
	const faceColor = color ?? (look === 'metal' ? (t.dark ? '#e4e8ef' : '#5d636e') : t.colors.text);
	const sides = sideColor ?? (look === 'duo' ? t.colors.accent : shade(faceColor, look === 'metal' ? 0.85 : 0.62));
	const mats = useMemo(
		() =>
			planes.map((pl) => {
				const clip = [pl.floor, pl.wipeIn, pl.wipeOut];
				const face =
					look === 'metal'
						? new THREE.MeshPhysicalMaterial({color: faceColor, metalness: 1, roughness: 0.22, clearcoat: 0.4, envMapIntensity: 2.4, clippingPlanes: clip})
						: look === 'glossy'
							? new THREE.MeshPhysicalMaterial({color: faceColor, metalness: 0, roughness: 0.18, clearcoat: 1, envMapIntensity: 1.4, clippingPlanes: clip})
							: new THREE.MeshBasicMaterial({color: faceColor, toneMapped: false, clippingPlanes: clip});
				const side =
					look === 'metal'
						? new THREE.MeshPhysicalMaterial({color: sides, metalness: 1, roughness: 0.3, envMapIntensity: 2.4, clippingPlanes: clip})
						: new THREE.MeshStandardMaterial({color: sides, roughness: look === 'glossy' ? 0.25 : 0.5, metalness: 0.02, clippingPlanes: clip});
				return [face, side] as THREE.Material[];
			}),
		[planes, look, faceColor, sides],
	);
	useEffect(() => () => mats.forEach((m) => m.forEach((x) => x.dispose())), [mats]);

	// timing
	const inDur = duration ?? at30(reveal === 'drop' ? 26 : 22, fps);
	const span = stagger ?? at30(reveal === 'wipe' || reveal === 'extrude' ? 0 : 14, fps);
	const outDur = outDuration ?? at30(16, fps);
	const outSpan = Math.round(span * 0.5);
	const exitStart = outAt ?? durationInFrames - 1 - outDur - outSpan;
	const nLines = Math.max(1, traced?.lines.length ?? 1);
	const orderOf = (line: number, x01: number) => (line + x01) / nLines;
	const inEase = ease ?? (reveal === 'flip' ? curves.outBack : curves.out);

	const fit = traced && traced.width > 0 ? Math.min(1, (maxWidth ?? s.safe.w * 0.96) / traced.width) : 1;
	const inner = useRef<THREE.Group>(null);

	// block-level progress for the wipes and the extrusion
	const blockIn = ramp(frame, delay, reveal === 'extrude' ? Math.round(inDur * 0.45) : inDur, reveal === 'wipe' || reveal === 'extrude' ? curves.inOut : inEase);
	const grow = reveal === 'extrude' ? ramp(frame, delay + Math.round(inDur * 0.3), inDur, curves.out) : 1;
	const blockOut = out === 'wipe' && Number.isFinite(exitStart) ? ramp(frame, exitStart, outDur + outSpan, curves.inOut) : 0;

	useLayoutEffect(() => {
		const g = inner.current;
		if (!g || !traced) {
			return;
		}
		g.updateWorldMatrix(true, false);
		const pad = em * 0.25;
		const {minX, maxX} = traced.box;
		traced.lines.forEach((ln, i) => {
			const pl = planes[i];
			if (!pl) {
				return;
			}
			const useFloor = reveal === 'rise' || out === 'sink';
			pl.floor.set(new THREE.Vector3(0, 1, 0), useFloor ? -(ln.bottom - em * 0.04) : FAR).applyMatrix4(g.matrixWorld);
			const inX = reveal === 'wipe' || reveal === 'extrude' ? minX - pad + (maxX - minX + 2 * pad) * blockIn : null;
			pl.wipeIn.set(new THREE.Vector3(-1, 0, 0), inX === null ? FAR : inX).applyMatrix4(g.matrixWorld);
			const outX = out === 'wipe' ? minX - pad + (maxX - minX + 2 * pad) * blockOut : null;
			pl.wipeOut.set(new THREE.Vector3(1, 0, 0), outX === null ? FAR : -outX).applyMatrix4(g.matrixWorld);
		});
	});

	if (!traced) {
		return null;
	}

	const lineRise = (line: number) => {
		const ln = traced.lines[line];
		return ln ? (ln.top - ln.bottom) * 1.12 + em * 0.08 : em;
	};
	const dropFrom = s.visible.h * 0.85;

	return (
		<group {...group}>
			<group ref={inner} scale={fit}>
				{traced.parts.map((p, i) => {
					const order = orderOf(p.line, p.x01);
					const d0 = delay + Math.round(span * order);
					let x = p.pivot[0];
					let y = p.pivot[1];
					let rx = 0;
					let sc = 1;
					let sz = 1;
					if (reveal === 'rise') {
						y -= (1 - ramp(frame, d0, inDur, inEase)) * lineRise(p.line);
					} else if (reveal === 'flip') {
						const k = ramp(frame, d0, inDur, inEase);
						rx = -(1 - k) * (Math.PI * 0.55);
						sc = Math.max(0.001, Math.min(1, ramp(frame, d0, inDur) * 3.2));
					} else if (reveal === 'drop') {
						const k = springAt(frame, fps, {delay: d0, config: 'settle', durationInFrames: inDur});
						y += (1 - k) * dropFrom;
					} else if (reveal === 'extrude') {
						sz = Math.max(0.015, grow);
					}
					if (out !== 'none' && out !== 'wipe' && Number.isFinite(exitStart)) {
						const q = ramp(frame, exitStart + Math.round(outSpan * order), outDur, curves.in);
						if (out === 'sink') {
							y -= q * lineRise(p.line);
						} else if (out === 'flip') {
							rx += q * (Math.PI * 0.55);
							sc *= Math.max(0.001, 1 - Math.max(0, q - 0.7) / 0.3);
						} else if (out === 'drop') {
							y -= q * q * dropFrom;
							x += q * em * 0.1 * (p.x01 - 0.5);
						}
					}
					const m = mats[p.line] ?? mats[0];
					return (
						<mesh
							key={i}
							geometry={geos[i]}
							material={m}
							position={[x, y, 0]}
							rotation={[rx, 0, 0]}
							scale={[sc, sc, sc * sz]}
							castShadow
						/>
					);
				})}
			</group>
		</group>
	);
};
