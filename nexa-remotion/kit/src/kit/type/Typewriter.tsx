// <Typewriter>: text typed grapheme by grapheme with a caret, human rhythm (seeded jitter, pauses after commas,
// sentences and lines) and line-by-line typing. The untyped rest is laid out but hidden, so typed text never
// reflows and centred text never drifts. typewriterSchedule() returns the frame every character lands, for key
// sounds (<KeySounds>) or anything else that must hit the keystrokes.
import {Audio} from '@remotion/media';
import React, {useMemo} from 'react';
import {Sequence, staticFile, useCurrentFrame} from 'remotion';
import {at30, rand, useStage, useTheme} from '../core';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {layoutText, typeCss, type TypeStyle} from './layout';
import {endsClause, endsSentence, graphemes} from './text';

export type TypewriterTiming = {
	delay?: number; // frames before the first character
	cps?: number; // characters per second (default 18; 10 is a slow human, 30 a fast UI)
	jitter?: number; // 0 to 1: seeded variation of every interval (default 0.35)
	pauses?: {comma?: number; sentence?: number; line?: number; word?: number}; // extra frames at 30 fps
	instant?: readonly number[]; // lines that appear whole instead of typed (a terminal's output)
	seed?: string;
};

export type TypeSchedule = {
	lines: string[][]; // graphemes of every line
	at: number[][]; // the frame each grapheme lands, per line
	flat: number[]; // every landing frame in order (spaces included)
	keys: number[]; // landing frames of visible characters only (for key sounds)
	end: number; // the frame the last character lands
};

/** When every character of `lines` lands. Pure: the same input gives the same frames in every render tab. */
export const typewriterSchedule = (lines: readonly string[], fps: number, timing: TypewriterTiming = {}): TypeSchedule => {
	const {delay = 0, cps = 18, jitter = 0.35, seed = 'type', instant = []} = timing;
	const pauses = {comma: 5, sentence: 12, line: 14, word: 0, ...timing.pauses};
	const step = fps / Math.max(0.5, cps);
	const g = lines.map((l) => graphemes(l));
	const at: number[][] = [];
	const flat: number[] = [];
	const keys: number[] = [];
	let f = delay;
	let n = 0;
	g.forEach((line, li) => {
		const row: number[] = [];
		if (instant.includes(li)) {
			// output, not typing: the whole line lands at once, then the line pause
			const land = Math.round(f);
			line.forEach(() => {
				row.push(land);
				flat.push(land);
			});
			f += step * 2 + (li < g.length - 1 ? at30(pauses.line, fps) : 0);
			at.push(row);
			return;
		}
		line.forEach((ch, ci) => {
			const land = Math.round(f);
			row.push(land);
			flat.push(land);
			if (ch.trim()) {
				keys.push(land);
			}
			const next = line[ci + 1];
			const endOfWord = next === undefined || next === ' ';
			let wait = step * (1 + jitter * (rand(`${seed}-${n}`) * 2 - 1));
			if (ch !== ' ' && endOfWord) {
				if (endsSentence(ch)) {
					wait += at30(pauses.sentence, fps);
				} else if (endsClause(ch)) {
					wait += at30(pauses.comma, fps);
				}
			}
			if (ch === ' ') {
				wait += pauses.word ? at30(pauses.word, fps) : 0;
			}
			if (ci === line.length - 1 && li < g.length - 1) {
				wait += at30(pauses.line, fps);
			}
			f += Math.max(0.5, wait);
			n++;
		});
		at.push(row);
	});
	return {lines: g, at, flat, keys, end: flat.length ? flat[flat.length - 1] : delay};
};

export type CaretStyle = 'bar' | 'block' | 'underscore' | 'none';

const Caret: React.FC<{kind: CaretStyle; color: string; visible: boolean}> = ({kind, color, visible}) => {
	if (kind === 'none') {
		return null;
	}
	const box: React.CSSProperties =
		kind === 'bar'
			? {left: '0.03em', width: '0.075em', bottom: '-0.2em', height: '1.08em'}
			: kind === 'block'
				? {left: '0.02em', width: '0.56em', bottom: '-0.2em', height: '1.08em', opacity: 0.85}
				: {left: '0.02em', width: '0.56em', bottom: '-0.16em', height: '0.085em'};
	return (
		<span style={{display: 'inline-block', position: 'relative', width: 0, height: 0}}>
			<span style={{position: 'absolute', background: color, borderRadius: '0.02em', visibility: visible ? 'visible' : 'hidden', ...box}} />
		</span>
	);
};

export type TypewriterProps = TypeProps &
	TypewriterTiming & {
		text: string; // `\n` for lines
		lines?: readonly string[]; // given lines
		maxWidth?: number; // px at 1080: wrap into measured lines (otherwise only `\n` breaks)
		caret?: CaretStyle; // default 'bar'
		caretColor?: string; // default: the accent
		caretAfter?: 'blink' | 'hide' | 'solid'; // after the last character (default 'blink')
		caretLead?: number; // frames the caret shows before typing starts (default 12)
		align?: 'left' | 'center' | 'right';
		style?: React.CSSProperties;
	};

const TypedLines: React.FC<{p: TypewriterProps; lines: string[]; ts: TypeStyle}> = ({p, lines, ts}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps} = useStage();
	const timingKey = JSON.stringify([p.delay, p.cps, p.jitter, p.pauses, p.seed, p.instant]);
	const sched = useMemo(
		() => typewriterSchedule(lines, fps, p),
		[lines.join('\n'), fps, timingKey], // p is keyed by timingKey
	);
	const caret = p.caret ?? 'bar';
	const caretColor = p.caretColor ?? t.colors.accent;
	// the caret line: the line of the last landed character, or the first line before typing starts
	let cl = 0;
	let cc = 0;
	sched.at.forEach((row, li) => {
		const typed = row.filter((f) => f <= frame).length;
		if (typed > 0) {
			cl = li;
			cc = typed;
		}
	});
	const lastLand = sched.flat.filter((f) => f <= frame).pop();
	const typing = lastLand !== undefined && frame - lastLand < at30(10, fps) && frame <= sched.end;
	const blinkOn = Math.floor(Math.max(0, frame - (lastLand ?? 0)) / at30(16, fps)) % 2 === 0;
	const done = frame >= sched.end;
	const after = p.caretAfter ?? 'blink';
	// the caret shows up a moment before the first key, never alone on an empty frame long before
	const lead = frame >= (p.delay ?? 0) - at30(p.caretLead ?? 12, fps);
	const caretVisible = lead && (typing || (done ? (after === 'solid' ? true : after === 'hide' ? false : blinkOn) : blinkOn));
	return (
		<div style={{...typeCss(ts), color: p.color ?? t.colors.text, textAlign: p.align ?? 'left', ...p.style}}>
			{sched.lines.map((row, li) => {
				const typed = sched.at[li].filter((f) => f <= frame).length;
				const here = li === cl;
				const shown = here ? cc : typed;
				return (
					<div key={li} style={{whiteSpace: 'pre'}}>
						<span>{row.slice(0, shown).join('')}</span>
						{here ? <Caret kind={caret} color={caretColor} visible={caretVisible} /> : null}
						<span style={{visibility: 'hidden'}}>{row.slice(shown).join('') || (row.length ? '' : ' ')}</span>
					</div>
				);
			})}
		</div>
	);
};

const TypedMeasured: React.FC<{p: TypewriterProps; ts: TypeStyle}> = ({p, ts}) => {
	const {unit} = useStage();
	const ready = useTypeFontsReady(p.role ?? 'mono');
	const maxW = (p.maxWidth ?? 0) * unit;
	const tsKey = JSON.stringify(ts);
	const lines = useMemo(
		() => (ready ? layoutText(p.text, ts, {maxWidth: maxW, shrink: false}).lines.map((l) => l.text) : null),
		[ready, p.text, tsKey, maxW], // ts is keyed by tsKey
	);
	if (!lines) {
		return <div style={{...typeCss(ts), visibility: 'hidden'}}>{p.text}</div>;
	}
	return <TypedLines p={p} lines={lines} ts={ts} />;
};

export const Typewriter: React.FC<TypewriterProps> = (props) => {
	const t = useTheme();
	const {unit} = useStage();
	const ts = typeStyle(t, unit, props.text, props, 56, 'mono');
	if (props.maxWidth !== undefined && !props.lines) {
		return <TypedMeasured p={props} ts={ts} />;
	}
	const lines = props.lines ? [...props.lines] : props.text.split('\n');
	return <TypedLines p={props} lines={lines} ts={ts} />;
};

/** The kit's key click samples (in kit/public/type/; copy that folder into a project's public/). */
export const KEY_SOUNDS = ['type/key-1.wav', 'type/key-2.wav', 'type/key-3.wav'];

/**
 * A key click on each landing frame: the samples alternate (seeded) and vary in level so a run of keys never
 * sounds like a machine gun, and keys closer than `minGap` frames are thinned out.
 */
export const KeySounds: React.FC<{
	frames: readonly number[];
	src?: string | readonly string[]; // default: the kit's three clicks through staticFile()
	volume?: number; // default 0.35: a sweetener under the voice
	minGap?: number; // frames (default 2)
	seed?: string;
}> = ({frames, src, volume = 0.35, minGap = 2, seed = 'keys'}) => {
	const list = src === undefined ? KEY_SOUNDS.map((s) => staticFile(s)) : typeof src === 'string' ? [src] : [...src];
	const kept: number[] = [];
	for (const f of [...frames].sort((a, b) => a - b)) {
		if (!kept.length || f - kept[kept.length - 1] >= minGap) {
			kept.push(f);
		}
	}
	return (
		<>
			{kept.map((f, i) => (
				<Sequence key={`${f}-${i}`} from={f} durationInFrames={8} layout="none" showInTimeline={false}>
					<Audio src={list[Math.floor(rand(`${seed}-s${i}`) * list.length)]} volume={volume * (0.75 + 0.25 * rand(`${seed}-v${i}`))} />
				</Sequence>
			))}
		</>
	);
};
