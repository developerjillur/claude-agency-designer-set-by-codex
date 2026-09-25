// Two effects @remotion/effects does not have, written with createEffect() from remotion: posterize (colour
// levels) and sliceShift (horizontal band displacement for glitches). Both are single-pass WebGL2 shaders and
// work on every effects host (Solid, Img, Video from @remotion/media, HtmlInCanvas).
import {createEffect} from 'remotion';

type Gl = WebGL2RenderingContext;

type PassState = {
	gl: Gl;
	program: WebGLProgram;
	vao: WebGLVertexArrayObject;
	vbo: WebGLBuffer;
	texture: WebGLTexture;
	loc: Record<string, WebGLUniformLocation | null>;
};

const VERT = `#version 300 es
in vec2 aPos;
in vec2 aUv;
out vec2 vUv;
void main() {
	vUv = aUv;
	gl_Position = vec4(aPos, 0.0, 1.0);
}
`;

const compile = (gl: Gl, type: number, src: string, label: string): WebGLShader => {
	const sh = gl.createShader(type);
	if (!sh) {
		throw new Error(`${label}: could not create a shader`);
	}
	gl.shaderSource(sh, src);
	gl.compileShader(sh);
	if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
		const log = gl.getShaderInfoLog(sh);
		gl.deleteShader(sh);
		throw new Error(`${label}: shader did not compile: ${log ?? ''}`);
	}
	return sh;
};

const setupPass = (target: HTMLCanvasElement, frag: string, uniforms: string[], label: string): PassState => {
	const gl = target.getContext('webgl2', {premultipliedAlpha: true, alpha: true, preserveDrawingBuffer: true});
	if (!gl) {
		throw new Error(`${label}: no WebGL2 context. Render with --gl=angle (or swangle on a machine without a GPU).`);
	}
	const vs = compile(gl, gl.VERTEX_SHADER, VERT, label);
	const fs = compile(gl, gl.FRAGMENT_SHADER, frag, label);
	const program = gl.createProgram();
	if (!program) {
		throw new Error(`${label}: could not create a program`);
	}
	gl.attachShader(program, vs);
	gl.attachShader(program, fs);
	gl.linkProgram(program);
	gl.deleteShader(vs);
	gl.deleteShader(fs);
	if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		throw new Error(`${label}: program did not link: ${gl.getProgramInfoLog(program) ?? ''}`);
	}
	const vao = gl.createVertexArray();
	const vbo = gl.createBuffer();
	const texture = gl.createTexture();
	if (!vao || !vbo || !texture) {
		throw new Error(`${label}: could not allocate GL objects`);
	}
	gl.bindVertexArray(vao);
	gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
	// x, y, u, v for a strip covering the viewport
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 0, 0, 1, -1, 1, 0, -1, 1, 0, 1, 1, 1, 1, 1]), gl.STATIC_DRAW);
	const aPos = gl.getAttribLocation(program, 'aPos');
	const aUv = gl.getAttribLocation(program, 'aUv');
	gl.enableVertexAttribArray(aPos);
	gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 16, 0);
	gl.enableVertexAttribArray(aUv);
	gl.vertexAttribPointer(aUv, 2, gl.FLOAT, false, 16, 8);
	gl.bindVertexArray(null);
	gl.bindTexture(gl.TEXTURE_2D, texture);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
	gl.bindTexture(gl.TEXTURE_2D, null);
	const loc: Record<string, WebGLUniformLocation | null> = {};
	for (const u of ['uSrc', 'uSize', ...uniforms]) {
		loc[u] = gl.getUniformLocation(program, u);
	}
	return {gl, program, vao, vbo, texture, loc};
};

const drawPass = (
	s: PassState,
	source: CanvasImageSource,
	width: number,
	height: number,
	flipSourceY: boolean,
	set: (gl: Gl, loc: PassState['loc']) => void,
) => {
	const {gl} = s;
	gl.viewport(0, 0, width, height);
	gl.bindFramebuffer(gl.FRAMEBUFFER, null);
	gl.clearColor(0, 0, 0, 0);
	gl.clear(gl.COLOR_BUFFER_BIT);
	gl.useProgram(s.program);
	gl.bindVertexArray(s.vao);
	gl.activeTexture(gl.TEXTURE0);
	gl.bindTexture(gl.TEXTURE_2D, s.texture);
	gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, flipSourceY);
	gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source as TexImageSource);
	gl.uniform1i(s.loc.uSrc, 0);
	gl.uniform2f(s.loc.uSize, width, height);
	set(gl, s.loc);
	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
	gl.bindVertexArray(null);
	gl.bindTexture(gl.TEXTURE_2D, null);
	gl.useProgram(null);
};

const cleanupPass = ({gl, program, vao, vbo, texture}: PassState) => {
	gl.deleteTexture(texture);
	gl.deleteBuffer(vbo);
	gl.deleteVertexArray(vao);
	gl.deleteProgram(program);
};

const assertNumber = (v: unknown, name: string, label: string) => {
	if (v !== undefined && (typeof v !== 'number' || !Number.isFinite(v))) {
		throw new TypeError(`${label}: "${name}" must be a finite number, got ${JSON.stringify(v)}`);
	}
};

// ---------------------------------------------------------------- posterize

export type PosterizeParams = {
	/** Colour levels per channel, 2 to 64. Defaults to 5. */
	readonly levels?: number;
	/** 0 keeps the source, 1 is fully posterized. Defaults to 1. */
	readonly amount?: number;
};

const POSTERIZE_FRAG = `#version 300 es
precision highp float;
in vec2 vUv;
out vec4 outColor;
uniform sampler2D uSrc;
uniform vec2 uSize;
uniform float uLevels;
uniform float uAmount;
void main() {
	vec4 c = texture(uSrc, vUv);
	if (c.a <= 0.0001) {
		outColor = vec4(0.0);
		return;
	}
	// work on straight colour so edges with partial alpha keep their hue
	vec3 straight = c.rgb / c.a;
	float n = max(uLevels - 1.0, 1.0);
	vec3 stepped = floor(straight * n + 0.5) / n;
	outColor = vec4(mix(straight, stepped, uAmount) * c.a, c.a);
}
`;

const posterizeResolve = (p: PosterizeParams) => ({
	levels: Math.round(Math.min(64, Math.max(2, p.levels ?? 5))),
	amount: Math.min(1, Math.max(0, p.amount ?? 1)),
});

/** Reduces every channel to a few levels: poster, screen-print and stop-motion colour. WebGL2, one pass. */
export const posterize = createEffect<PosterizeParams, PassState>({
	type: 'nexa.fx.posterize',
	label: 'posterize()',
	documentationLink: null,
	backend: 'webgl2',
	calculateKey: (p) => {
		const r = posterizeResolve(p);
		return `posterize-${r.levels}-${r.amount}`;
	},
	setup: (target) => setupPass(target, POSTERIZE_FRAG, ['uLevels', 'uAmount'], 'posterize()'),
	apply: ({source, width, height, params, state, flipSourceY}) => {
		const r = posterizeResolve(params);
		drawPass(state, source, width, height, flipSourceY, (gl, loc) => {
			gl.uniform1f(loc.uLevels, r.levels);
			gl.uniform1f(loc.uAmount, r.amount);
		});
	},
	cleanup: cleanupPass,
	schema: {},
	validateParams: (p) => {
		assertNumber(p.levels, 'levels', 'posterize()');
		assertNumber(p.amount, 'amount', 'posterize()');
	},
});

// ---------------------------------------------------------------- sliceShift

export type SliceShiftParams = {
	/** Largest sideways move of a broken band, in canvas pixels. Defaults to 60. */
	readonly amount?: number;
	/** Number of horizontal bands, 2 to 400. Defaults to 24. */
	readonly bands?: number;
	/** Share of bands that break, 0 to 1. Defaults to 0.35. */
	readonly density?: number;
	/** Pattern seed: change it every frame or two during a burst. Defaults to 0. */
	readonly seed?: number;
	/** Extra red and blue split inside broken bands, in canvas pixels. Defaults to 0. */
	readonly split?: number;
};

const SLICE_FRAG = `#version 300 es
precision highp float;
in vec2 vUv;
out vec4 outColor;
uniform sampler2D uSrc;
uniform vec2 uSize;
uniform float uAmount;
uniform float uBands;
uniform float uDensity;
uniform float uSeed;
uniform float uSplit;
float h21(vec2 p) {
	vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));
	q += dot(q, q.yzx + 33.33);
	return fract((q.x + q.y) * q.z);
}
void main() {
	float band = floor(vUv.y * uBands);
	float pick = h21(vec2(band, uSeed));
	float broken = step(1.0 - uDensity, pick);
	float dir = h21(vec2(band * 1.7 + 11.0, uSeed + 5.0)) * 2.0 - 1.0;
	float dx = dir * broken * uAmount / uSize.x;
	vec2 p = vec2(clamp(vUv.x + dx, 0.0, 1.0), vUv.y);
	vec4 g = texture(uSrc, p);
	if (broken > 0.5 && uSplit > 0.0) {
		float s = uSplit / uSize.x;
		vec4 r = texture(uSrc, vec2(clamp(p.x + s, 0.0, 1.0), p.y));
		vec4 b = texture(uSrc, vec2(clamp(p.x - s, 0.0, 1.0), p.y));
		float a = max(max(r.a, g.a), b.a);
		outColor = vec4(min(vec3(r.r, g.g, b.b), vec3(a)), a);
	} else {
		outColor = g;
	}
}
`;

const sliceResolve = (p: SliceShiftParams) => ({
	amount: Math.max(0, p.amount ?? 60),
	bands: Math.round(Math.min(400, Math.max(2, p.bands ?? 24))),
	density: Math.min(1, Math.max(0, p.density ?? 0.35)),
	seed: p.seed ?? 0,
	split: Math.max(0, p.split ?? 0),
});

/** Pushes random horizontal bands sideways (a broken digital signal). Deterministic for a given seed. */
export const sliceShift = createEffect<SliceShiftParams, PassState>({
	type: 'nexa.fx.slice-shift',
	label: 'sliceShift()',
	documentationLink: null,
	backend: 'webgl2',
	calculateKey: (p) => {
		const r = sliceResolve(p);
		return `slice-${r.amount}-${r.bands}-${r.density}-${r.seed}-${r.split}`;
	},
	setup: (target) =>
		setupPass(target, SLICE_FRAG, ['uAmount', 'uBands', 'uDensity', 'uSeed', 'uSplit'], 'sliceShift()'),
	apply: ({source, width, height, params, state, flipSourceY}) => {
		const r = sliceResolve(params);
		drawPass(state, source, width, height, flipSourceY, (gl, loc) => {
			gl.uniform1f(loc.uAmount, r.amount);
			gl.uniform1f(loc.uBands, r.bands);
			gl.uniform1f(loc.uDensity, r.density);
			gl.uniform1f(loc.uSeed, r.seed);
			gl.uniform1f(loc.uSplit, r.split);
		});
	},
	cleanup: cleanupPass,
	schema: {},
	validateParams: (p) => {
		for (const k of ['amount', 'bands', 'density', 'seed', 'split'] as const) {
			assertNumber(p[k], k, 'sliceShift()');
		}
	},
});
