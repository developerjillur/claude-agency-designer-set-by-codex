// <Particles>: background particle fields (dust, bokeh, stars, embers, snow, confetti). Every particle has seeded
// start values and its position is a pure function of the frame (drift, wrap-around and noise wobble), so any
// frame renders the same in any tab: no simulation state. Buffers are written in useLayoutEffect.
import {useThree} from '@react-three/fiber';
import React, {useEffect, useLayoutEffect, useMemo, useRef} from 'react';
import {random, useCurrentFrame} from 'remotion';
import * as THREE from 'three';
import {curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {useScene3D} from './Scene3D';
import {mix, noise} from './util';

export type ParticleKind = 'dust' | 'bokeh' | 'stars' | 'embers' | 'snow' | 'confetti';

export type ParticlesProps = {
	kind?: ParticleKind;
	count?: number;
	/** Colours to pick from (seeded); default from the theme. */
	colors?: string[];
	/** Speed multiplier (1 = the kind's natural pace). */
	speed?: number;
	/** Size multiplier. */
	size?: number;
	/** Overall opacity. */
	opacity?: number;
	/** Nearest and farthest depth, world z (the camera looks at z = 0 from +z). */
	near?: number;
	far?: number;
	/** How far past the frame edges particles spread (1 = exactly the frame). */
	spread?: number;
	/** Frames to fade the field in from the start of the Sequence. */
	fadeIn?: number;
	seed?: string;
};

type Kind = {
	count: number;
	size: [number, number]; // world units at z = 0
	alpha: [number, number];
	drift: [number, number, number]; // world units per second
	jitter: number; // noise wobble amplitude, world units
	wobble: number; // noise frequency, Hz
	soft: number; // 0 hard disc .. 1 very soft
	rim: number; // a brighter edge, like a lens's out-of-focus highlight (bokeh)
	twinkle: number; // 0 .. 1
	additive: boolean | 'dark';
};

const KINDS: Record<Exclude<ParticleKind, 'confetti'>, Kind> = {
	dust: {count: 700, size: [0.012, 0.034], alpha: [0.3, 0.75], drift: [0.05, 0.08, 0], jitter: 0.12, wobble: 0.12, soft: 0.55, rim: 0, twinkle: 0.15, additive: 'dark'},
	bokeh: {count: 34, size: [0.4, 1.3], alpha: [0.05, 0.16], drift: [0.03, 0.05, 0], jitter: 0.22, wobble: 0.05, soft: 0.32, rim: 0.35, twinkle: 0.08, additive: 'dark'},
	stars: {count: 1400, size: [0.012, 0.038], alpha: [0.45, 1], drift: [0.015, 0, 0], jitter: 0, wobble: 0, soft: 0.5, rim: 0, twinkle: 0.55, additive: true},
	embers: {count: 320, size: [0.03, 0.09], alpha: [0.55, 1], drift: [0.05, 0.45, 0], jitter: 0.35, wobble: 0.35, soft: 0.8, rim: 0, twinkle: 0.45, additive: true},
	snow: {count: 700, size: [0.02, 0.065], alpha: [0.55, 0.95], drift: [0.04, -0.32, 0], jitter: 0.3, wobble: 0.22, soft: 0.45, rim: 0, twinkle: 0, additive: false},
};

const vertex = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
attribute vec3 aColor;
uniform float uScale;
varying float vAlpha;
varying vec3 vColor;
void main() {
	vec4 mv = modelViewMatrix * vec4(position, 1.0);
	gl_Position = projectionMatrix * mv;
	gl_PointSize = max(1.0, aSize * uScale / max(0.05, -mv.z));
	vAlpha = aAlpha;
	vColor = aColor;
}`;

// Colours arrive in linear space and leave through three's tone-mapping and colour-space chunks, so they match the
// theme's hex values on the canvas and stay right when a post pass (Bloom) renders to a linear target first.
const fragment = /* glsl */ `
uniform float uSoft;
uniform float uRim;
uniform float uOpacity;
varying float vAlpha;
varying vec3 vColor;
void main() {
	float d = length(gl_PointCoord - 0.5) * 2.0;
	float a = 1.0 - smoothstep(1.0 - uSoft, 1.0, d);
	if (a <= 0.001) discard;
	a *= 1.0 - uRim + uRim * smoothstep(0.35, 0.9, d) * 1.6;
	gl_FragColor = vec4(vColor, a * vAlpha * uOpacity);
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`;

const wrap = (v: number, lo: number, hi: number) => {
	const span = hi - lo;
	return lo + ((((v - lo) % span) + span) % span);
};

const defaultColors = (kind: ParticleKind, t: ReturnType<typeof useTheme>): string[] => {
	const c = t.colors;
	if (kind === 'confetti') {
		return [c.accent, c.accent2, c.highlight, c.positive, t.dark ? '#ffffff' : c.text];
	}
	if (kind === 'embers') {
		return ['#ffb347', '#ff7a2f', '#ffd27a'];
	}
	if (kind === 'stars' || kind === 'snow') {
		return ['#ffffff', t.dark ? '#dfe8ff' : c.muted];
	}
	if (kind === 'bokeh') {
		// one hue, like out-of-focus lights of one colour temperature
		return t.dark ? [mix('#ffffff', c.accent, 0.25), mix('#ffffff', c.accent, 0.6), c.accent] : [c.accent, mix(c.accent, '#ffffff', 0.4)];
	}
	return t.dark ? ['#ffffff', mix('#ffffff', c.accent, 0.5)] : [c.muted, c.accent];
};

const PointField: React.FC<Required<Omit<ParticlesProps, 'kind' | 'colors'>> & {kind: Exclude<ParticleKind, 'confetti'>; colors: string[]}> = ({
	kind,
	count,
	colors,
	speed,
	size,
	opacity,
	near,
	far,
	spread,
	fadeIn,
	seed,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const s = useScene3D();
	const gl = useThree((st) => st.gl);
	const k = KINDS[kind];
	const n = Math.max(1, Math.round(count));
	const camZ = s.pose.position[2];
	const halfH = Math.tan((s.pose.fov * Math.PI) / 360); // view height per unit of distance, halved
	const aspect = s.width / s.height;

	// seeded start values, fixed for the render
	const base = useMemo(() => {
		const a = new Float32Array(n * 8);
		for (let i = 0; i < n; i++) {
			const z = far + (near - far) * random(`${seed}-z-${i}`) ** 0.8;
			const dist = Math.max(0.5, camZ - z);
			a[i * 8] = (random(`${seed}-x-${i}`) * 2 - 1) * dist * halfH * aspect * spread;
			a[i * 8 + 1] = (random(`${seed}-y-${i}`) * 2 - 1) * dist * halfH * spread;
			a[i * 8 + 2] = z;
			a[i * 8 + 3] = k.size[0] + (k.size[1] - k.size[0]) * random(`${seed}-s-${i}`) ** 2;
			a[i * 8 + 4] = k.alpha[0] + (k.alpha[1] - k.alpha[0]) * random(`${seed}-a-${i}`);
			a[i * 8 + 5] = 0.6 + 0.8 * random(`${seed}-v-${i}`); // speed variation
			a[i * 8 + 6] = random(`${seed}-p-${i}`) * Math.PI * 2; // twinkle phase
			a[i * 8 + 7] = Math.floor(random(`${seed}-c-${i}`) * colors.length);
		}
		return a;
	}, [n, seed, near, far, camZ, halfH, aspect, spread, k.size, k.alpha, colors.length]);

	const geo = useMemo(() => {
		const g = new THREE.BufferGeometry();
		g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
		g.setAttribute('aSize', new THREE.BufferAttribute(new Float32Array(n), 1));
		g.setAttribute('aAlpha', new THREE.BufferAttribute(new Float32Array(n), 1));
		const col = new Float32Array(n * 3);
		// THREE.Color parses hex as sRGB and stores linear values (colour management is on in R3F v9)
		const pal = colors.map((c) => {
			const k = new THREE.Color(c);
			return [k.r, k.g, k.b];
		});
		for (let i = 0; i < n; i++) {
			const p = pal[base[i * 8 + 7]] ?? [1, 1, 1];
			col[i * 3] = p[0];
			col[i * 3 + 1] = p[1];
			col[i * 3 + 2] = p[2];
		}
		g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
		// particles move anywhere in the field: never cull the whole cloud by a stale bounding sphere
		g.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), 1e5);
		return g;
	}, [n, base, colors]);
	useEffect(() => () => geo.dispose(), [geo]);

	const additive = k.additive === true || (k.additive === 'dark' && s.dark);
	const mat = useMemo(
		() =>
			new THREE.ShaderMaterial({
				vertexShader: vertex,
				fragmentShader: fragment,
				uniforms: {uScale: {value: 1}, uSoft: {value: k.soft}, uRim: {value: k.rim}, uOpacity: {value: 1}},
				transparent: true,
				depthWrite: false,
				blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
			}),
		[k.soft, k.rim, additive],
	);
	useEffect(() => () => mat.dispose(), [mat]);

	const tSec = frame / fps;
	const fade = fadeIn > 0 ? ramp(frame, 0, fadeIn, curves.sine) : 1;
	const ref = useRef<THREE.Points>(null);
	useLayoutEffect(() => {
		const pos = geo.getAttribute('position') as THREE.BufferAttribute;
		const sz = geo.getAttribute('aSize') as THREE.BufferAttribute;
		const al = geo.getAttribute('aAlpha') as THREE.BufferAttribute;
		for (let i = 0; i < n; i++) {
			const o = i * 8;
			const z = base[o + 2];
			const dist = Math.max(0.5, camZ - z);
			const hx = dist * halfH * aspect * spread;
			const hy = dist * halfH * spread;
			const v = base[o + 5] * speed;
			let x = base[o] + k.drift[0] * v * tSec;
			let y = base[o + 1] + k.drift[1] * v * tSec;
			if (k.jitter) {
				x += noise(seed, tSec * k.wobble + i * 0.37, 1) * k.jitter;
				y += noise(seed, tSec * k.wobble + i * 0.37, 2) * k.jitter;
			}
			pos.setXYZ(i, wrap(x, -hx, hx), wrap(y, -hy, hy), z);
			sz.setX(i, base[o + 3] * size);
			const tw = k.twinkle ? 1 - k.twinkle * (0.5 + 0.5 * Math.sin(tSec * (1.2 + base[o + 5] * 1.6) + base[o + 6])) : 1;
			al.setX(i, base[o + 4] * tw);
		}
		pos.needsUpdate = true;
		sz.needsUpdate = true;
		al.needsUpdate = true;
		// gl_PointSize is in drawing-buffer pixels: the frame height times the pixel ratio (2 in a Retina Studio)
		mat.uniforms.uScale.value = (s.height * gl.getPixelRatio()) / (2 * halfH);
		mat.uniforms.uOpacity.value = opacity * fade;
	});

	return <points ref={ref} geometry={geo} material={mat} frustumCulled={false} renderOrder={-2} />;
};

const Confetti: React.FC<Required<Omit<ParticlesProps, 'kind' | 'colors'>> & {colors: string[]}> = ({
	count,
	colors,
	speed,
	size,
	opacity,
	near,
	far,
	spread,
	fadeIn,
	seed,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const s = useScene3D();
	const n = Math.max(1, Math.round(count));
	const camZ = s.pose.position[2];
	const halfH = Math.tan((s.pose.fov * Math.PI) / 360);
	const aspect = s.width / s.height;
	const ref = useRef<THREE.InstancedMesh>(null);
	const geo = useMemo(() => new THREE.PlaneGeometry(0.11, 0.06), []);
	const mat = useMemo(() => new THREE.MeshStandardMaterial({side: THREE.DoubleSide, roughness: 0.55, metalness: 0.1, transparent: opacity < 1, opacity}), [opacity]);
	useEffect(() => () => {
		geo.dispose();
		mat.dispose();
	}, [geo, mat]);
	const dummy = useMemo(() => new THREE.Object3D(), []);
	const tSec = frame / fps;
	const fade = fadeIn > 0 ? ramp(frame, 0, fadeIn, curves.sine) : 1;
	useLayoutEffect(() => {
		const m = ref.current;
		if (!m) {
			return;
		}
		const col = new THREE.Color();
		for (let i = 0; i < n; i++) {
			const z = far + (near - far) * random(`${seed}-z-${i}`);
			const dist = Math.max(0.5, camZ - z);
			const hx = dist * halfH * aspect * spread;
			const hy = dist * halfH * spread;
			const v = (0.55 + 0.7 * random(`${seed}-v-${i}`)) * speed;
			const x0 = (random(`${seed}-x-${i}`) * 2 - 1) * hx;
			const y0 = (random(`${seed}-y-${i}`) * 2 - 1) * hy;
			const sway = noise(seed, tSec * 0.5 + i * 0.21, 3) * 0.35;
			dummy.position.set(wrap(x0 + sway, -hx, hx), wrap(y0 - 0.9 * v * tSec, -hy, hy), z);
			const spin = (1.5 + 3 * random(`${seed}-r-${i}`)) * v;
			dummy.rotation.set(
				random(`${seed}-rx-${i}`) * 6.28 + tSec * spin,
				random(`${seed}-ry-${i}`) * 6.28 + tSec * spin * 0.7,
				random(`${seed}-rz-${i}`) * 6.28 + tSec * spin * 0.4,
			);
			dummy.scale.setScalar(size * (0.7 + 0.6 * random(`${seed}-s-${i}`)) * Math.max(0.001, fade));
			dummy.updateMatrix();
			m.setMatrixAt(i, dummy.matrix);
			m.setColorAt(i, col.set(colors[Math.floor(random(`${seed}-c-${i}`) * colors.length)] ?? '#ffffff'));
		}
		m.instanceMatrix.needsUpdate = true;
		if (m.instanceColor) {
			m.instanceColor.needsUpdate = true;
		}
	});
	return <instancedMesh ref={ref} args={[geo, mat, n]} frustumCulled={false} />;
};

/**
 * A seeded particle field behind or around the subject. Kinds: dust (fine motes, the default), bokeh (large soft
 * discs), stars (a twinkling field), embers (rising sparks), snow (falling flakes), confetti (tumbling paper).
 * Glowing kinds add light on dark themes and blend normally on light ones.
 */
export const Particles: React.FC<ParticlesProps> = ({
	kind = 'dust',
	count,
	colors,
	speed = 1,
	size = 1,
	opacity = 1,
	near = 2.5,
	far = -9,
	spread = 1.1,
	fadeIn = 0,
	seed = 'particles',
}) => {
	const t = useTheme();
	const pal = colors ?? defaultColors(kind, t);
	const common = {speed, size, opacity, near, far, spread, fadeIn, seed};
	if (kind === 'confetti') {
		return <Confetti count={count ?? 260} colors={pal} {...common} />;
	}
	return <PointField kind={kind} count={count ?? KINDS[kind].count} colors={pal} {...common} />;
};
