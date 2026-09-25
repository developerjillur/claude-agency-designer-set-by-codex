// Shared parts of the ui module: interface colours derived from the theme, shadows, the enter/exit clock of
// temporary elements, grapheme splitting and a human typing rhythm. Only a few names leave the module (see
// index.ts); the rest stay internal so they never clash with other kit modules.
import {interpolateColors, useCurrentFrame} from 'remotion';
import {at30, clamp, curves, rand, useStage, useTheme, type Ease, type Theme} from '../core';
import {ramp} from '../motion';

// ------------------------------------------------------------------ colour

const parsed = new Map<string, [number, number, number, number]>();

/** [r, g, b, a] of any CSS colour Remotion can parse (hex, rgb, hsl, oklch, names). */
export const rgbaOf = (c: string): [number, number, number, number] => {
	const hit = parsed.get(c);
	if (hit) {
		return hit;
	}
	const s = interpolateColors(0, [0, 1], [c, c]);
	const n = (s.match(/-?[\d.]+/g) ?? ['0', '0', '0', '1']).map(Number);
	const out: [number, number, number, number] = [n[0] ?? 0, n[1] ?? 0, n[2] ?? 0, n[3] ?? 1];
	if (parsed.size > 400) {
		parsed.clear();
	}
	parsed.set(c, out);
	return out;
};

/** The colour with its alpha multiplied by `a`. */
export const fade = (c: string, a: number): string => {
	const [r, g, b, a0] = rgbaOf(c);
	return `rgba(${r}, ${g}, ${b}, ${Number((a0 * clamp(a)).toFixed(3))})`;
};

/** `t` of the way from colour a to colour b. */
export const blend = (a: string, b: string, t: number): string => interpolateColors(clamp(t), [0, 1], [a, b]);

/** Relative luminance 0 (black) to 1 (white). */
export const lum = (c: string): number => {
	const [r, g, b] = rgbaOf(c).map((v, i) => (i < 3 ? v / 255 : v));
	const f = (v: number) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
	return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};

/** Black or white, whichever reads better on `bg`. */
export const inkOn = (bg: string, dark = '#111317', light = '#FFFFFF'): string => (lum(bg) > 0.45 ? dark : light);

// ------------------------------------------------------------------ interface palette

export type UiMode = 'auto' | 'light' | 'dark';

/** Colours for interface mock-ups: windows, screens, fields and cards. */
export type UiPalette = {
	dark: boolean;
	page: string; // the page or screen inside a window
	panel: string; // cards and sidebars on the page
	raised: string; // menus, toasts, popovers
	chrome: string; // title and tab bars
	bar: string; // the toolbar under the tabs, the active tab
	field: string; // inputs, the address bar
	text: string;
	muted: string;
	faint: string;
	line: string;
	accent: string;
	onAccent: string;
	accent2: string;
	positive: string;
	negative: string;
	highlight: string;
};

const LIGHT_UI = {
	page: '#FFFFFF',
	panel: '#F6F7F9',
	raised: '#FFFFFF',
	chrome: '#ECEEF1',
	bar: '#FFFFFF',
	field: '#F1F3F5',
	text: '#14171C',
	muted: '#667085',
	faint: '#C9CED6',
	line: '#E4E7EC',
};

const DARK_UI = {
	page: '#15171C',
	panel: '#1D2027',
	raised: '#23262E',
	chrome: '#0F1115',
	bar: '#191B21',
	field: '#0C0E12',
	text: '#EEF0F4',
	muted: '#9AA1AD',
	faint: '#3B404B',
	line: '#2A2E37',
};

/**
 * The interface palette for a theme. 'auto' follows the theme (a light theme gives light windows); 'light' or
 * 'dark' against the theme uses a neutral set with the theme's accents, so a light app can sit in a dark video.
 */
export const uiPalette = (t: Theme, mode: UiMode = 'auto'): UiPalette => {
	const c = t.colors;
	const dark = mode === 'auto' ? t.dark : mode === 'dark';
	const brand = {
		accent: c.accent,
		onAccent: c.onAccent,
		accent2: c.accent2,
		positive: c.positive,
		negative: c.negative,
		highlight: c.highlight,
	};
	if (dark !== t.dark) {
		return {dark, ...(dark ? DARK_UI : LIGHT_UI), ...brand};
	}
	if (!dark) {
		return {
			dark,
			page: c.surface,
			panel: blend(c.surface, c.text, 0.035),
			raised: c.surface,
			chrome: blend(c.surface, c.text, 0.07),
			bar: c.surface,
			field: blend(c.surface, c.text, 0.05),
			text: c.text,
			muted: c.muted,
			faint: c.faint,
			line: c.line,
			...brand,
		};
	}
	return {
		dark,
		page: c.bg2,
		panel: c.surface,
		raised: blend(c.surface, '#FFFFFF', 0.05),
		chrome: blend(c.bg, c.surface, 0.6),
		bar: blend(c.bg2, c.surface, 0.5),
		field: blend(c.bg, '#000000', 0.2),
		text: c.text,
		muted: c.muted,
		faint: c.faint,
		line: c.line,
		...brand,
	};
};

/** A soft, layered shadow for windows and cards (depth 1 small, 2 card, 3 floating window). */
export const shadowFor = (dark: boolean, unit: number, depth: 1 | 2 | 3 = 2): string => {
	const u = (v: number) => `${(v * unit).toFixed(2)}px`;
	if (dark) {
		const k = [0.35, 0.45, 0.55][depth - 1];
		return `0 ${u(1)} 0 rgba(255, 255, 255, 0.04) inset, 0 0 0 ${u(1)} rgba(255, 255, 255, 0.07), 0 ${u(8 * depth)} ${u(24 * depth)} rgba(0, 0, 0, ${k}), 0 ${u(2)} ${u(6)} rgba(0, 0, 0, 0.3)`;
	}
	const k = [0.07, 0.1, 0.13][depth - 1];
	return `0 0 0 ${u(1)} rgba(16, 24, 40, 0.06), 0 ${u(1)} ${u(2)} rgba(16, 24, 40, 0.06), 0 ${u(6 * depth)} ${u(18 * depth)} rgba(16, 24, 40, ${k}), 0 ${u(18 * depth)} ${u(44 * depth)} rgba(16, 24, 40, ${k * 0.9})`;
};

// ------------------------------------------------------------------ the clock of a temporary element

export type UiLifeProps = {
	delay?: number; // frames before the entrance starts
	enter?: number; // entrance frames (default: the theme's, scaled to the fps)
	exit?: number | false; // exit frames; false keeps it on screen to the end
	exitAt?: number; // local frame the exit starts (default: it ends on the last frame of the Sequence)
};

export type UiLife = {
	frame: number;
	fps: number;
	unit: number;
	start: number;
	inFrames: number;
	outFrames: number;
	exitStart: number; // Infinity when there is no exit
	/** 0 to 1: the entrance of a part that starts `offset` frames after `start` */
	enter: (offset?: number, frames?: number, ease?: Ease) => number;
	/** 0 to 1: the exit of a part that starts leaving `offset` frames after the exit starts */
	leave: (offset?: number, frames?: number, ease?: Ease) => number;
};

/** Entrance and exit progress for overlays; the exit ends on the last frame of the enclosing Sequence. */
export const useUiLife = (o: UiLifeProps = {}): UiLife => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, durationInFrames, unit} = useStage();
	const start = o.delay ?? 0;
	const inFrames = o.enter ?? at30(t.motion.enterFrames, fps);
	const outFrames = o.exit === false ? 0 : (o.exit ?? at30(t.motion.exitFrames, fps));
	const exitStart =
		o.exit === false
			? Infinity
			: (o.exitAt ?? (Number.isFinite(durationInFrames) ? durationInFrames - 1 - outFrames : Infinity));
	return {
		frame,
		fps,
		unit,
		start,
		inFrames,
		outFrames,
		exitStart,
		enter: (offset = 0, frames = inFrames, ease = curves.out) => ramp(frame, start + offset, frames, ease),
		leave: (offset = 0, frames = outFrames, ease = curves.in) =>
			Number.isFinite(exitStart) ? ramp(frame, exitStart + offset, Math.max(1, frames), ease) : 0,
	};
};

/** A press: 0 at rest, 1 fully down at frame `at`, back to 0 with a small overshoot below 0 (the release). */
export const pressDepth = (frame: number, at: number, fps: number): number => {
	const down = at30(2, fps);
	const up = at30(9, fps);
	if (frame < at - down || frame > at + 1 + up) {
		return 0;
	}
	if (frame <= at) {
		return ramp(frame, at - down, down, curves.inCubic);
	}
	if (frame <= at + 1) {
		return 1;
	}
	// release: 1 -> 0 with a small undershoot (the control pops back a little proud of rest)
	return 1 - ramp(frame, at + 1, up, curves.outBack);
};

// ------------------------------------------------------------------ text

let segmenter: Intl.Segmenter | null = null;
const segCache = new Map<string, string[]>();

/** User-perceived characters (Bangla conjuncts and vowel signs stay whole). */
export const splitGraphemes = (s: string): string[] => {
	const hit = segCache.get(s);
	if (hit) {
		return hit;
	}
	segmenter = segmenter ?? new Intl.Segmenter(undefined, {granularity: 'grapheme'});
	const out = Array.from(segmenter.segment(s), (x) => x.segment);
	if (segCache.size > 300) {
		segCache.clear();
	}
	segCache.set(s, out);
	return out;
};

export type TypingOptions = {
	cps?: number; // characters a second (default 16)
	jitter?: number; // 0 even, 0.5 human (default 0.35)
	seed?: string | number;
	instantIndent?: boolean; // leading spaces of a line appear at once (code editors)
	pause?: number; // scale of the beats after spaces, punctuation and new lines (1 prose, about 0.2 for code)
};

export type TypingPlan = {chars: string[]; times: number[]; total: number};

const planCache = new Map<string, TypingPlan>();

/**
 * When each character of `text` appears, in frames from the start of typing: a steady human rhythm (seeded
 * jitter, a beat after a space, longer after punctuation and new lines). Pure and cached.
 */
export const uiTypeSchedule = (text: string, fps: number, o: TypingOptions = {}): TypingPlan => {
	const cps = Math.max(1, o.cps ?? 16);
	const jitter = o.jitter ?? 0.35;
	const seed = o.seed ?? 'type';
	const pause = o.pause ?? 1;
	const key = `${text}|${fps}|${cps}|${jitter}|${seed}|${o.instantIndent ? 1 : 0}|${pause}`;
	const hit = planCache.get(key);
	if (hit) {
		return hit;
	}
	const chars = splitGraphemes(text);
	const base = fps / cps;
	const times: number[] = [];
	let t = 0;
	let lineStart = true;
	for (let i = 0; i < chars.length; i++) {
		const ch = chars[i];
		const prev = i > 0 ? chars[i - 1] : '';
		let d = base * (1 + jitter * (rand(`${seed}-${i}`) * 2 - 1));
		if (prev === ' ') {
			d += base * 0.5 * pause;
		}
		if (/[.,!?;:।]/.test(prev)) {
			d += base * 2.5 * pause;
		}
		if (prev === '\n') {
			d += base * 3 * pause;
		}
		if (o.instantIndent && lineStart && (ch === ' ' || ch === '\t')) {
			d = 0;
		}
		if (i === 0) {
			d = 0;
		}
		t += Math.max(0, d);
		times.push(t);
		lineStart = ch === '\n' || (lineStart && (ch === ' ' || ch === '\t'));
	}
	const plan = {chars, times, total: t};
	if (planCache.size > 200) {
		planCache.clear();
	}
	planCache.set(key, plan);
	return plan;
};

/** How many characters of a plan are visible `elapsed` frames after typing started. */
export const typedCount = (elapsed: number, times: readonly number[]): number => {
	if (elapsed < 0) {
		return 0;
	}
	let lo = 0;
	let hi = times.length;
	while (lo < hi) {
		const mid = (lo + hi) >> 1;
		if (times[mid] <= elapsed) {
			lo = mid + 1;
		} else {
			hi = mid;
		}
	}
	return lo;
};

/** Caret opacity: solid while typing, then a soft blink about once a second. */
export const caretOpacity = (frame: number, lastTyped: number, fps: number): number => {
	const since = frame - lastTyped;
	const hold = at30(12, fps);
	if (since < hold) {
		return 1;
	}
	const period = fps * 1.06;
	const c = Math.cos((2 * Math.PI * (since - hold)) / period);
	return clamp(0.5 + 1.6 * c * 0.5, 0, 1);
};

export type TypedText = {
	shown: string;
	count: number;
	total: number;
	started: boolean;
	done: boolean;
	endFrame: number; // local frame the last character appears
	caret: number; // caret opacity now
};

/** Typing state of `text` that starts at frame `start`. */
export const useUiTyping = (text: string, start: number, o: TypingOptions = {}): TypedText => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const plan = uiTypeSchedule(text, fps, o);
	const count = typedCount(frame - start, plan.times);
	const lastTyped = count > 0 ? start + plan.times[count - 1] : start;
	return {
		shown: plan.chars.slice(0, count).join(''),
		count,
		total: plan.chars.length,
		started: frame >= start,
		done: count >= plan.chars.length,
		endFrame: start + plan.total,
		caret: caretOpacity(frame, lastTyped, fps),
	};
};

// ------------------------------------------------------------------ small helpers

/** px at 1080 to px here, rounded to a hundredth so styles stay stable between frames. */
export const px = (v: number, unit: number): number => Math.round(v * unit * 100) / 100;

/** A soft average of a value over the last `window` frames: smooth following without state. */
export const smoothed = (frame: number, window: number, f: (frame: number) => number): number => {
	const n = Math.max(1, Math.round(window));
	let sum = 0;
	let wsum = 0;
	for (let i = 0; i < n; i++) {
		// a raised-cosine kernel: eases in and out
		const w = 0.5 - 0.5 * Math.cos((2 * Math.PI * (i + 0.5)) / n);
		sum += w * f(frame - i);
		wsum += w;
	}
	return sum / wsum;
};

/** Initials for an avatar: "Maya Chen" -> "MC", "আরিফ রহমান" -> "আর". */
export const initialsOf = (name: string): string => {
	const words = name.trim().split(/\s+/).filter(Boolean);
	const firsts = words.map((w) => splitGraphemes(w)[0] ?? '');
	return (firsts.length > 1 ? firsts[0] + firsts[firsts.length - 1] : firsts[0] ?? '').toUpperCase();
};

/** A pleasant avatar colour picked by name from the theme's accents and a few neutrals. */
export const avatarColor = (name: string, t: Theme): string => {
	const choices = [t.colors.accent, t.colors.accent2, blend(t.colors.accent, t.colors.accent2, 0.5), blend(t.colors.accent, '#7C3AED', 0.5), blend(t.colors.accent2, '#0EA5A4', 0.5)];
	return choices[Math.floor(rand(`avatar-${name}`) * choices.length)];
};
