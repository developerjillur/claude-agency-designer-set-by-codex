// Code on screen: a small tokenizer (ts, tsx, js, jsx, py, json, bash) with light and dark colours, a CodeBlock that
// types itself by character or by line and walks the viewer through highlighted lines, and a Terminal that types
// commands and prints their output, progress bars and spinners. Monospace from the theme; sizes px at 1080.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {UiIcon, type UiIconName} from './Icon';
import {blend, caretOpacity, fade, shadowFor, smoothed, splitGraphemes, typedCount, uiPalette, uiTypeSchedule, type UiMode} from './shared';

// ------------------------------------------------------------------ tokenizer

export type CodeLang = 'ts' | 'tsx' | 'js' | 'jsx' | 'py' | 'json' | 'bash' | 'text';
export type TokenKind = 'plain' | 'kw' | 'str' | 'num' | 'com' | 'fn' | 'type' | 'prop' | 'punc' | 'op' | 'tag' | 'attr' | 'var' | 'const';
export type CodeToken = {text: string; kind: TokenKind};

const JS_KW = new Set(
	'const let var function return if else for while do switch case break continue new class extends import export from default as async await try catch finally throw typeof instanceof in of void yield interface type enum implements public private protected readonly static get set this super satisfies keyof declare namespace'.split(' '),
);
const JS_CONST = new Set(['true', 'false', 'null', 'undefined', 'NaN', 'Infinity']);
const PY_KW = new Set(
	'def class return if elif else for while in not and or is import from as with try except finally raise lambda yield pass break continue global nonlocal async await del assert match case'.split(' '),
);
const PY_CONST = new Set(['None', 'True', 'False']);
const PY_BUILTIN = new Set('print len range str int float list dict set tuple open enumerate zip map filter sum min max sorted round abs any all isinstance super'.split(' '));
const SH_KW = new Set('if then else elif fi for in do done while until case esac function export local return sudo'.split(' '));

const OPS = /=>|===|!==|==|!=|<=|>=|&&|\|\||\?\?|\?\.|\.\.\.|\*\*|->|[+\-*/%=<>!&|^~?:@]/y;
const PUNC = /[{}()[\];,.]/y;
const WS = /\s+/y;
const NUM = /(?:0x[\da-fA-F_]+|\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?n?)(?![\w$])/y;
const IDENT = /[A-Za-z_$\u0080-￿][\w$\u0080-￿]*/y;

const at = (re: RegExp, src: string, pos: number): string | null => {
	re.lastIndex = pos;
	const m = re.exec(src);
	return m ? m[0] : null;
};

const nextNonSpace = (src: string, pos: number): string => {
	for (let i = pos; i < src.length; i++) {
		if (src[i] !== ' ' && src[i] !== '\t') {
			return src[i];
		}
	}
	return '';
};

const lastReal = (out: CodeToken[]): CodeToken | undefined => {
	for (let i = out.length - 1; i >= 0; i--) {
		if (out[i].text.trim() !== '') {
			return out[i];
		}
	}
	return undefined;
};

/** Split source into coloured tokens. Pure; good enough for short on-screen snippets, not a parser. */
export const tokenizeCode = (src: string, lang: CodeLang = 'ts'): CodeToken[] => {
	const out: CodeToken[] = [];
	const push = (text: string, kind: TokenKind) => {
		const prev = out[out.length - 1];
		if (prev && prev.kind === kind && (kind === 'plain' || kind === 'com')) {
			prev.text += text;
		} else {
			out.push({text, kind});
		}
	};
	if (lang === 'text') {
		return [{text: src, kind: 'plain'}];
	}
	const js = lang === 'ts' || lang === 'tsx' || lang === 'js' || lang === 'jsx';
	const jsx = lang === 'tsx' || lang === 'jsx';
	let pos = 0;
	let cmdStart = true; // bash: the next word is a command
	let inTag = false; // jsx: inside <Tag ...>
	let prevKw = '';
	while (pos < src.length) {
		let m: string | null;
		// comments
		if (js && (m = at(/\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|$)/y, src, pos))) {
			push(m, 'com');
			pos += m.length;
			continue;
		}
		if ((lang === 'py' || lang === 'bash') && (m = at(/#[^\n]*/y, src, pos)) && (lang === 'py' || pos === 0 || /\s/.test(src[pos - 1]))) {
			push(m, 'com');
			pos += m.length;
			continue;
		}
		// strings
		if (lang === 'py' && (m = at(/[rbfuRBFU]{0,2}("""|''')[\s\S]*?(?:\1|$)/y, src, pos))) {
			push(m, 'str');
			pos += m.length;
			continue;
		}
		if ((m = at(js ? /`(?:\\[\s\S]|[^\\`])*`?|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?/y : lang === 'py' ? /[rbfuRBFU]{0,2}(?:"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)/y : /"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?/y, src, pos))) {
			const kind: TokenKind = lang === 'json' && nextNonSpace(src, pos + m.length) === ':' ? 'prop' : 'str';
			push(m, kind);
			pos += m.length;
			cmdStart = false;
			continue;
		}
		// bash variables and flags
		if (lang === 'bash') {
			if ((m = at(/\$\{[^}\n]*\}|\$[A-Za-z_]\w*|\$\d|\$\?/y, src, pos))) {
				push(m, 'var');
				pos += m.length;
				cmdStart = false;
				continue;
			}
			if (!cmdStart && /\s/.test(src[pos - 1] ?? ' ') && (m = at(/--?[A-Za-z][\w-]*(?:=[^\s]*)?/y, src, pos))) {
				push(m, 'attr');
				pos += m.length;
				continue;
			}
			if ((m = at(/&&|\|\||[|;]/y, src, pos))) {
				push(m, 'op');
				pos += m.length;
				cmdStart = true;
				continue;
			}
			if ((m = at(/[^\s|;&$'"#]+/y, src, pos))) {
				const kind: TokenKind = SH_KW.has(m) ? 'kw' : cmdStart ? 'fn' : /^\d+(\.\d+)?$/.test(m) ? 'num' : 'plain';
				push(m, kind);
				pos += m.length;
				cmdStart = SH_KW.has(m) && m !== 'fi' && m !== 'done' && m !== 'esac';
				continue;
			}
		}
		// jsx tags
		if (jsx && (m = at(/<\/?[A-Za-z][\w.]*/y, src, pos))) {
			push(m.startsWith('</') ? '</' : '<', 'punc');
			push(m.replace(/^<\/?/, ''), 'tag');
			pos += m.length;
			inTag = true;
			continue;
		}
		if (jsx && inTag && (m = at(/\/?>/y, src, pos))) {
			push(m, 'punc');
			pos += m.length;
			inTag = false;
			continue;
		}
		if (lang === 'py' && (m = at(/@[A-Za-z_][\w.]*/y, src, pos))) {
			push(m, 'fn');
			pos += m.length;
			continue;
		}
		if ((m = at(NUM, src, pos))) {
			push(m, 'num');
			pos += m.length;
			continue;
		}
		if ((m = at(IDENT, src, pos))) {
			const prev = lastReal(out);
			const next = nextNonSpace(src, pos + m.length);
			let kind: TokenKind = 'plain';
			if (lang === 'json') {
				kind = m === 'true' || m === 'false' || m === 'null' ? 'const' : 'plain';
			} else if (lang === 'py') {
				if (PY_KW.has(m)) {
					kind = 'kw';
				} else if (PY_CONST.has(m)) {
					kind = 'const';
				} else if (prevKw === 'def') {
					kind = 'fn';
				} else if (prevKw === 'class') {
					kind = 'type';
				} else if (m === 'self' || m === 'cls') {
					kind = 'var';
				} else if (prev?.text === '.') {
					kind = next === '(' ? 'fn' : 'prop';
				} else if (next === '(') {
					kind = 'fn';
				} else if (PY_BUILTIN.has(m)) {
					kind = 'fn';
				} else if (/^[A-Z]/.test(m)) {
					kind = 'type';
				}
			} else {
				if (jsx && inTag && next === '=') {
					kind = 'attr';
				} else if (JS_KW.has(m)) {
					kind = 'kw';
				} else if (JS_CONST.has(m)) {
					kind = 'const';
				} else if (prev?.text === '.' || prev?.text === '?.') {
					kind = next === '(' ? 'fn' : 'prop';
				} else if (next === '(' || (prevKw === 'function' && prev?.text === 'function')) {
					kind = 'fn';
				} else if (/^[A-Z]/.test(m)) {
					kind = 'type';
				} else if (next === ':' && (prev?.text === '{' || prev?.text === ',')) {
					kind = 'prop';
				}
			}
			push(m, kind);
			prevKw = kind === 'kw' ? m : '';
			pos += m.length;
			continue;
		}
		if ((m = at(WS, src, pos))) {
			push(m, 'plain');
			pos += m.length;
			if (m.includes('\n')) {
				cmdStart = true;
			}
			continue;
		}
		if ((m = at(OPS, src, pos))) {
			push(m, 'op');
			pos += m.length;
			continue;
		}
		if ((m = at(PUNC, src, pos))) {
			push(m, 'punc');
			pos += m.length;
			continue;
		}
		push(src[pos], 'plain');
		pos += 1;
	}
	return out;
};

/** Tokens split into lines (multi-line comments and strings are cut at each new line). */
export const tokenLines = (src: string, lang: CodeLang): CodeToken[][] => {
	const lines: CodeToken[][] = [[]];
	for (const tok of tokenizeCode(src, lang)) {
		const parts = tok.text.split('\n');
		parts.forEach((p, i) => {
			if (i > 0) {
				lines.push([]);
			}
			if (p.length) {
				lines[lines.length - 1].push({text: p, kind: tok.kind});
			}
		});
	}
	return lines;
};

export type CodePalette = Record<TokenKind, string> & {bg: string; gutter: string};

const DARK_CODE: Omit<CodePalette, 'bg' | 'gutter'> = {
	plain: '#E6EAF0',
	kw: '#FF8C8C',
	str: '#A1E3A9',
	num: '#FFBA73',
	com: '#7F899B',
	fn: '#7DC5FF',
	type: '#F3D77A',
	prop: '#C9B6FF',
	punc: '#A5ADBA',
	op: '#FF8C8C',
	tag: '#7FE1C6',
	attr: '#F3D77A',
	var: '#FFBA73',
	const: '#FFBA73',
};

const LIGHT_CODE: Omit<CodePalette, 'bg' | 'gutter'> = {
	plain: '#1F2328',
	kw: '#C0175D',
	str: '#0A7A3D',
	num: '#B35900',
	com: '#6E7781',
	fn: '#1B5FD0',
	type: '#8A5A00',
	prop: '#6A3EC3',
	punc: '#57606A',
	op: '#C0175D',
	tag: '#0A7A69',
	attr: '#8A5A00',
	var: '#B35900',
	const: '#B35900',
};

/** Syntax colours for a light or dark code surface, with the theme's background. */
export const codePalette = (dark: boolean, bg: string): CodePalette => ({...(dark ? DARK_CODE : LIGHT_CODE), bg, gutter: dark ? '#5D6675' : '#A0A7B1'});

// ------------------------------------------------------------------ CodeBlock

export type CodeFocus = {lines: number[] | string; at: number}; // lines 1-based: [3, 4] or '3-5'

export type CodeBlockProps = {
	code: string;
	lang?: CodeLang;
	typing?: 'none' | 'line' | 'char';
	startAt?: number;
	cps?: number; // characters a second for 'char' (default 45: code types fast and evenly)
	lineEvery?: number; // frames between lines for 'line' (default 5 at 30 fps)
	focus?: CodeFocus[]; // walk through lines: the band moves and other lines dim
	dim?: number; // opacity of lines out of focus (default 0.38)
	lineNumbers?: boolean;
	firstLine?: number; // the first line number (default 1)
	title?: string; // file name in the title bar
	chrome?: boolean; // a title bar with window controls (default true)
	width?: number; // px at 1080 (default 1100)
	height?: number; // px at 1080 (default: fits every line; with a height, it scrolls to follow the caret)
	fontSize?: number; // px at 1080 (default 26)
	lineHeight?: number; // default 1.6
	mode?: UiMode;
	palette?: Partial<CodePalette>;
	radius?: number;
	shadow?: boolean;
	caret?: boolean;
	style?: React.CSSProperties;
};

const parseLines = (l: number[] | string): Set<number> => {
	if (Array.isArray(l)) {
		return new Set(l);
	}
	const s = new Set<number>();
	for (const part of l.split(',')) {
		const [a, b] = part.split('-').map((x) => parseInt(x.trim(), 10));
		if (Number.isFinite(a)) {
			for (let i = a; i <= (Number.isFinite(b) ? b : a); i++) {
				s.add(i);
			}
		}
	}
	return s;
};

/** A code window: typed by character or line, coloured by language, with a moving highlight for walkthroughs. */
export const CodeBlock: React.FC<CodeBlockProps> = ({
	code,
	lang = 'ts',
	typing = 'char',
	startAt = 0,
	cps = 45,
	lineEvery,
	focus = [],
	dim = 0.38,
	lineNumbers = true,
	firstLine = 1,
	title,
	chrome = true,
	width = 1100,
	height,
	fontSize = 26,
	lineHeight = 1.6,
	mode = 'auto',
	palette,
	radius = 16,
	shadow = true,
	caret = true,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode);
	const C = {...codePalette(P.dark, P.page), ...palette};
	const lines = tokenLines(code, lang);
	const n = lines.length;
	const lineH = fontSize * lineHeight;
	const titleH = chrome ? 52 : 0;
	const padY = 22;
	const viewH = height !== undefined ? height - titleH : n * lineH + padY * 2;
	const every = lineEvery ?? at30(5, fps);
	// grapheme bookkeeping for 'char' typing
	const lineText = code.split('\n');
	const lineG = lineText.map((l) => splitGraphemes(l));
	const lineStart: number[] = [];
	let acc = 0;
	for (let i = 0; i < n; i++) {
		lineStart.push(acc);
		acc += (lineG[i]?.length ?? 0) + 1; // + the new line
	}
	const plan = uiTypeSchedule(code, fps, {cps, jitter: 0.2, seed: `code-${code.length}`, instantIndent: true, pause: 0.2});
	const countAt = (f: number) => (typing === 'char' ? typedCount(f - startAt, plan.times) : Infinity);
	const count = countAt(frame);
	const caretLineAt = (f: number): number => {
		if (typing === 'line') {
			return clamp(Math.floor((f - startAt) / every), 0, n - 1);
		}
		const c = countAt(f);
		let li = 0;
		for (let i = 0; i < n; i++) {
			if (c >= lineStart[i]) {
				li = i;
			}
		}
		return li;
	};
	const caretLine = caretLineAt(frame);
	const lastTyped = typing === 'char' && count > 0 ? startAt + plan.times[Math.min(count, plan.times.length) - 1] : startAt;
	const typingDone = typing !== 'char' || count >= plan.chars.length;
	// focus steps
	const steps = [...focus].sort((a, b) => a.at - b.at).map((s) => ({at: s.at, set: parseLines(s.lines)}));
	const focusOf = (line: number): number => {
		let v = 0;
		let prevSet: Set<number> | null = null;
		for (const s of steps) {
			const p = ramp(frame, s.at, at30(9, fps), curves.inOut);
			if (p <= 0) {
				break;
			}
			const was = prevSet?.has(line) ? 1 : 0;
			const now = s.set.has(line) ? 1 : 0;
			v = was + (now - was) * p;
			prevSet = s.set;
		}
		return v;
	};
	const anyFocus = steps.length ? ramp(frame, steps[0].at, at30(9, fps), curves.inOut) : 0;
	// scrolling (only with a fixed height)
	const visible = Math.max(1, Math.floor((viewH - padY * 2) / lineH));
	const targetTop = (f: number): number => {
		if (height === undefined || n <= visible) {
			return 0;
		}
		let active = caretLineAt(f);
		const firstFocused = [...steps].reverse().find((s) => f >= s.at);
		if (typingDone && firstFocused) {
			active = Math.min(...Array.from(firstFocused.set)) - firstLine + Math.floor(visible / 2);
		}
		return clamp(active - (visible - 2), 0, n - visible);
	};
	const topLine = smoothed(frame, at30(9, fps), targetTop);
	const digits = String(firstLine + n - 1).length;
	const gutterW = lineNumbers ? (digits * 0.62 + 1.6) * fontSize : 0;
	return (
		<div
			style={{
				position: 'relative',
				width: width * unit,
				height: (viewH + titleH) * unit,
				borderRadius: radius * unit,
				overflow: 'hidden',
				background: C.bg,
				boxShadow: shadow ? shadowFor(P.dark, unit, 2) : `0 0 0 ${unit}px ${P.line}`,
				...style,
			}}
		>
			{chrome ? (
				<div style={{height: titleH * unit, display: 'flex', alignItems: 'center', gap: 14 * unit, padding: `0 ${20 * unit}px`, background: P.chrome, borderBottom: `${unit}px solid ${P.line}`}}>
					<div style={{display: 'flex', gap: 8 * unit}}>
						{['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
							<div key={c} style={{width: 13 * unit, height: 13 * unit, borderRadius: '50%', background: c}} />
						))}
					</div>
					{title ? (
						<div style={{display: 'flex', alignItems: 'center', gap: 8 * unit, marginLeft: 10 * unit, fontFamily: t.type.body, fontSize: 17 * unit, fontWeight: t.weights.strong, color: P.muted}}>
							<UiIcon name="file" size={17} color={P.muted} />
							{title}
						</div>
					) : null}
				</div>
			) : null}
			<div style={{position: 'relative', height: viewH * unit, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 0, right: 0, top: (padY - topLine * lineH) * unit}}>
					{lines.map((toks, i) => {
						const lineNo = firstLine + i;
						const g = lineG[i] ?? [];
						let shownG = g.length;
						let started = true;
						let lineIn = 1;
						if (typing === 'char') {
							shownG = clamp(count - lineStart[i], 0, g.length);
							started = count >= lineStart[i] && (i === 0 ? count > 0 || frame >= startAt : true);
						} else if (typing === 'line') {
							lineIn = ramp(frame, startAt + i * every, at30(7, fps), curves.out);
							started = lineIn > 0;
						} else {
							lineIn = ramp(frame, startAt, at30(10, fps), curves.out);
						}
						const cut = g.slice(0, shownG).join('').length; // UTF-16 length visible
						let used = 0;
						const f = focusOf(lineNo);
						const opacity = (1 - (1 - dim) * anyFocus * (1 - f)) * lineIn;
						const showCaret = caret && typing === 'char' && i === caretLine && frame >= startAt - at30(4, fps) && (!typingDone || frame < lastTyped + at30(40, fps));
						return (
							<div key={i} style={{position: 'relative', height: lineH * unit, display: 'flex', alignItems: 'center'}}>
								{f > 0.001 ? (
									<div style={{position: 'absolute', inset: 0, background: fade(P.accent, 0.13 * f)}}>
										<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 4 * unit, background: P.accent, opacity: f}} />
									</div>
								) : null}
								{lineNumbers ? (
									<div style={{position: 'relative', width: gutterW * unit, flex: '0 0 auto', textAlign: 'right', paddingRight: fontSize * 0.9 * unit, boxSizing: 'border-box', fontFamily: t.type.mono, fontSize: fontSize * 0.86 * unit, color: blend(C.gutter, P.accent, f), opacity: started ? Math.max(opacity, 0.5 * lineIn) : 0, fontVariantNumeric: 'tabular-nums'}}>
										{lineNo}
									</div>
								) : (
									<div style={{width: 24 * unit, flex: '0 0 auto'}} />
								)}
								<div
									style={{
										position: 'relative',
										whiteSpace: 'pre',
										fontFamily: t.type.mono,
										fontSize: fontSize * unit,
										color: C.plain,
										opacity,
										translate: typing === 'line' ? `${(1 - lineIn) * -10 * unit}px 0px` : undefined,
									}}
								>
									{toks.map((tok, j) => {
										if (typing === 'char' && used >= cut) {
											return null;
										}
										const text = typing === 'char' ? tok.text.slice(0, Math.max(0, cut - used)) : tok.text;
										used += tok.text.length;
										return (
											<span key={j} style={{color: C[tok.kind], fontStyle: tok.kind === 'com' && /^[\x00-\x7F]*$/.test(tok.text) ? 'italic' : undefined}}>
												{text}
											</span>
										);
									})}
									{showCaret ? (
										<span style={{display: 'inline-block', width: 3 * unit, height: fontSize * 1.2 * unit, verticalAlign: 'middle', translate: `0px ${-0.06 * fontSize * unit}px`, background: P.accent, opacity: caretOpacity(frame, lastTyped, fps), marginLeft: unit}} />
									) : null}
								</div>
							</div>
						);
					})}
				</div>
			</div>
		</div>
	);
};

// ------------------------------------------------------------------ Terminal

export type TermTone = 'plain' | 'muted' | 'ok' | 'warn' | 'err' | 'accent' | 'info';

export type TermLine =
	| {cmd: string; cps?: number}
	| {out: string; tone?: TermTone; icon?: UiIconName}
	| {progress: string; frames?: number; tone?: TermTone}
	| {spinner: string; frames?: number; done?: string}
	| {gap: number};

export type TermSlot = {start: number; end: number}; // local frames: the line appears, the line is finished

/** When each terminal line appears and finishes; `end` is when the whole session is done. */
export const terminalTimeline = (lines: readonly TermLine[], fps: number, startAt = 0, cps = 24): {slots: TermSlot[]; end: number} => {
	let time = startAt;
	const slots: TermSlot[] = [];
	for (const l of lines) {
		if ('cmd' in l) {
			const plan = uiTypeSchedule(l.cmd, fps, {cps: l.cps ?? cps, seed: `term-${l.cmd}`, pause: 0.35});
			const end = time + plan.total;
			slots.push({start: time, end});
			time = end + at30(9, fps);
		} else if ('out' in l) {
			slots.push({start: time, end: time});
			time += at30(2, fps);
		} else if ('progress' in l) {
			const f = l.frames ?? at30(40, fps);
			slots.push({start: time, end: time + f});
			time += f + at30(4, fps);
		} else if ('spinner' in l) {
			const f = l.frames ?? at30(36, fps);
			slots.push({start: time, end: time + f});
			time += f + at30(4, fps);
		} else {
			slots.push({start: time, end: time});
			time += l.gap;
		}
	}
	return {slots, end: time};
};

export type TerminalProps = {
	lines: TermLine[];
	startAt?: number;
	cps?: number; // typing speed of commands (default 24)
	path?: string; // the prompt's folder (default '~/driftnote')
	symbol?: string; // the prompt symbol (default '$')
	title?: string;
	idlePrompt?: boolean; // an empty prompt with a blinking caret after the last line (default true)
	width?: number; // px at 1080 (default 1100)
	height?: number; // default 620; lines scroll up when they overflow
	fontSize?: number; // default 24
	mode?: UiMode;
	chrome?: boolean;
	radius?: number;
	shadow?: boolean;
	style?: React.CSSProperties;
};

const Spinner: React.FC<{size: number; color: string}> = ({size, color}) => {
	const frame = useCurrentFrame();
	const {unit} = useStage();
	return (
		<svg width={size * unit} height={size * unit} viewBox="0 0 24 24" style={{rotate: `${frame * 18}deg`, flex: '0 0 auto'}}>
			<circle cx={12} cy={12} r={9} fill="none" stroke={fade(color, 0.25)} strokeWidth={3} />
			<path d="M12 3a9 9 0 0 1 9 9" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" />
		</svg>
	);
};

/** A terminal session: commands type at a human pace, output prints fast, the view scrolls as it fills. */
export const Terminal: React.FC<TerminalProps> = ({
	lines,
	startAt = 0,
	cps = 24,
	path = '~/driftnote',
	symbol = '$',
	title,
	idlePrompt = true,
	width = 1100,
	height = 620,
	fontSize = 24,
	mode = 'auto',
	chrome = true,
	radius = 16,
	shadow = true,
	style,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit} = useStage();
	const P = uiPalette(t, mode === 'auto' ? 'dark' : mode);
	const {slots, end} = terminalTimeline(lines, fps, startAt, cps);
	const lineH = fontSize * 1.62;
	const titleH = chrome ? 48 : 0;
	const padY = 20;
	const viewH = height - titleH;
	const tones: Record<TermTone, string> = {plain: P.text, muted: P.muted, ok: P.positive, warn: P.highlight, err: P.negative, accent: P.accent, info: P.accent2};
	const bg = P.dark ? blend(P.page, '#000000', 0.2) : P.page;
	const visibleAt = (f: number) => slots.filter((s) => f >= s.start).length + (idlePrompt && f >= end ? 1 : 0);
	const cap = Math.floor((viewH - padY * 2) / lineH);
	const scroll = smoothed(frame, at30(6, fps), (f) => Math.max(0, visibleAt(f) - cap));
	const prompt = (
		<>
			<span style={{color: P.accent2}}>{path}</span>
			<span style={{color: P.accent}}> {symbol} </span>
		</>
	);
	const rows: React.ReactNode[] = [];
	lines.forEach((l, i) => {
		const s = slots[i];
		if (frame < s.start) {
			return;
		}
		let body: React.ReactNode = null;
		if ('cmd' in l) {
			const plan = uiTypeSchedule(l.cmd, fps, {cps: l.cps ?? cps, seed: `term-${l.cmd}`, pause: 0.35});
			const c = typedCount(frame - s.start, plan.times);
			const typing = frame <= s.end + at30(6, fps);
			const last = c > 0 ? s.start + plan.times[c - 1] : s.start;
			body = (
				<>
					{prompt}
					<span style={{color: P.text}}>{plan.chars.slice(0, c).join('')}</span>
					{typing ? <span style={{display: 'inline-block', width: 0.6 * fontSize * unit, height: fontSize * 1.15 * unit, verticalAlign: 'middle', translate: `0px ${-0.08 * fontSize * unit}px`, background: P.text, opacity: 0.85 * caretOpacity(frame, last, fps)}} /> : null}
				</>
			);
		} else if ('out' in l) {
			const c = tones[l.tone ?? 'plain'];
			body = (
				<span style={{display: 'inline-flex', alignItems: 'center', gap: 10 * unit, color: c}}>
					{l.icon ? <UiIcon name={l.icon} size={fontSize * 0.9} color={c} stroke={2.6} /> : null}
					{l.out}
				</span>
			);
		} else if ('progress' in l) {
			const p = ramp(frame, s.start, s.end - s.start, curves.outCubic);
			const c = tones[l.tone ?? 'accent'];
			body = (
				<span style={{display: 'inline-flex', alignItems: 'center', gap: 14 * unit, color: P.text}}>
					<span style={{minWidth: 9 * fontSize * 0.6 * unit}}>{l.progress}</span>
					<span style={{position: 'relative', width: 16 * fontSize * unit, height: fontSize * 0.5 * unit, borderRadius: fontSize * 0.25 * unit, background: fade(P.text, 0.12), overflow: 'hidden'}}>
						<span style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${p * 100}%`, background: c, borderRadius: fontSize * 0.25 * unit}} />
					</span>
					<span style={{color: P.muted, fontVariantNumeric: 'tabular-nums', minWidth: 3 * fontSize * 0.62 * unit, textAlign: 'right'}}>{Math.round(p * 100)}%</span>
				</span>
			);
		} else if ('spinner' in l) {
			const done = frame >= s.end;
			body = done ? (
				<span style={{display: 'inline-flex', alignItems: 'center', gap: 10 * unit, color: P.positive}}>
					<UiIcon name="check" size={fontSize * 0.9} color={P.positive} stroke={2.8} />
					{l.done ?? l.spinner}
				</span>
			) : (
				<span style={{display: 'inline-flex', alignItems: 'center', gap: 10 * unit, color: P.text}}>
					<Spinner size={fontSize * 0.85} color={P.accent} />
					{l.spinner}
				</span>
			);
		} else {
			body = null;
		}
		rows.push(
			<div key={i} style={{height: lineH * unit, display: 'flex', alignItems: 'center', whiteSpace: 'pre', overflow: 'hidden'}}>
				{body}
			</div>,
		);
	});
	if (idlePrompt && frame >= end) {
		rows.push(
			<div key="idle" style={{height: lineH * unit, display: 'flex', alignItems: 'center', whiteSpace: 'pre'}}>
				{prompt}
				<span style={{display: 'inline-block', width: 0.6 * fontSize * unit, height: fontSize * 1.15 * unit, background: P.text, opacity: 0.85 * caretOpacity(frame, end, fps)}} />
			</div>,
		);
	}
	return (
		<div
			style={{
				position: 'relative',
				width: width * unit,
				height: height * unit,
				borderRadius: radius * unit,
				overflow: 'hidden',
				background: bg,
				boxShadow: shadow ? shadowFor(P.dark, unit, 2) : undefined,
				...style,
			}}
		>
			{chrome ? (
				<div style={{height: titleH * unit, display: 'flex', alignItems: 'center', padding: `0 ${18 * unit}px`, background: P.chrome, borderBottom: `${unit}px solid ${P.line}`, position: 'relative'}}>
					<div style={{display: 'flex', gap: 8 * unit}}>
						{['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
							<div key={c} style={{width: 13 * unit, height: 13 * unit, borderRadius: '50%', background: c}} />
						))}
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, textAlign: 'center', fontFamily: t.type.body, fontSize: 16 * unit, fontWeight: t.weights.strong, color: P.muted}}>{title ?? `${path.split('/').pop() ?? 'shell'}: zsh`}</div>
				</div>
			) : null}
			<div style={{position: 'relative', height: viewH * unit, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 24 * unit, right: 24 * unit, top: (padY - scroll * lineH) * unit, fontFamily: t.type.mono, fontSize: fontSize * unit, color: P.text}}>{rows}</div>
			</div>
		</div>
	);
};
