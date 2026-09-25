// <Scramble>: a seeded decode. Every glyph flickers through random characters, then locks in order. The final text
// is laid out from the first frame (transparent until locked) and the random glyphs are drawn over each slot, so
// nothing reflows or jitters while it decodes. <WordRotator>: one word of a line cycles through options.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, lerp, rand, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {maskPad, typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {measureTextWidth, typeCss} from './layout';
import {staggerRank, type SplitOrder} from './SplitText';
import {graphemes, isBangla} from './text';

export const SCRAMBLE_CHARSETS = {
	latin: 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789',
	upper: 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789',
	digits: '0123456789',
	symbols: '#%&*+=<>/\\|{}[]$@!?',
	binary: '01',
	hex: '0123456789ABCDEF',
	bangla: 'অআইঈউএওকখগঘচছজঝটঠডঢণতথদধনপফবভমযরলশষসহ০১২৩৪৫৬৭৮৯',
} as const;

export type ScrambleCharset = keyof typeof SCRAMBLE_CHARSETS;

const pickPool = (text: string, charset: ScrambleCharset | string | undefined, caps: boolean): string[] => {
	if (charset) {
		return graphemes(charset in SCRAMBLE_CHARSETS ? SCRAMBLE_CHARSETS[charset as ScrambleCharset] : charset);
	}
	if (isBangla(text)) {
		return graphemes(SCRAMBLE_CHARSETS.bangla);
	}
	if (/^[\d\s.,:%+-]+$/.test(text)) {
		return graphemes(SCRAMBLE_CHARSETS.digits);
	}
	return graphemes(caps || text === text.toUpperCase() ? SCRAMBLE_CHARSETS.upper : SCRAMBLE_CHARSETS.latin);
};

export type ScrambleProps = TypeProps & {
	text: string;
	delay?: number; // frames before the first glyph appears
	duration?: number; // frames from the first lock to the last (default about 0.8 s)
	hold?: number; // frames all glyphs flicker before the first one locks (default 10)
	order?: SplitOrder | 'left'; // lock order (default 'forward', left to right)
	charset?: ScrambleCharset | string; // default: from the text (Bangla letters for Bangla, digits for numbers)
	rate?: number; // frames per random change (default 2: on twos, readable flicker)
	seed?: string;
	scrambleColor?: string; // colour of unlocked glyphs (default: the accent)
	align?: 'left' | 'center' | 'right';
	style?: React.CSSProperties;
};

export const Scramble: React.FC<ScrambleProps> = (props) => {
	const {text, delay = 0, rate = 2, seed = 'scramble', align = 'left'} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const ts = typeStyle(t, unit, text, props, 96);
	const units = useMemo(() => graphemes(text), [text]);
	const pool = useMemo(() => pickPool(text, props.charset, ts.textTransform === 'uppercase'), [text, props.charset, ts.textTransform]);
	const letters = units.map((g, i) => (g.trim() ? i : -1)).filter((i) => i >= 0);
	const n = letters.length;
	const hold = props.hold ?? at30(10, fps);
	const duration = props.duration ?? at30(24, fps);
	const order: SplitOrder = props.order === 'left' || props.order === undefined ? 'forward' : props.order;
	const color = props.color ?? t.colors.text;
	const scrambleColor = props.scrambleColor ?? t.colors.accent;
	return (
		<div style={{...typeCss(ts), color, textAlign: align, ...props.style}}>
			{units.map((g, i) => {
				const k = letters.indexOf(i);
				if (k < 0) {
					return <React.Fragment key={i}>{g}</React.Fragment>;
				}
				const rank = staggerRank(k, n, order, seed);
				const appear = delay + Math.round(rank * Math.min(1, 12 / Math.max(1, n)));
				const lock = delay + hold + Math.round((n > 1 ? rank / (n - 1) : 1) * duration);
				const locked = frame >= lock;
				const visible = frame >= appear;
				const tick = Math.floor(frame / Math.max(1, rate));
				const glyph = pool[Math.floor(rand(`${seed}-${i}-${tick}`) * pool.length)] ?? g;
				return (
					<span key={i} style={{position: 'relative'}}>
						<span style={{color: locked ? undefined : 'transparent'}}>{g}</span>
						{!locked && visible ? (
							<span
								style={{
									position: 'absolute',
									left: '50%',
									top: 0,
									translate: '-50% 0',
									color: scrambleColor,
									opacity: 0.9,
									whiteSpace: 'pre',
								}}
							>
								{glyph}
							</span>
						) : null}
					</span>
				);
			})}
		</div>
	);
};

export type WordRotatorProps = TypeProps & {
	words: readonly string[]; // the options, in order; the first shows first
	prefix?: string; // text before the slot ("Built for ")
	suffix?: string; // text after the slot
	delay?: number; // frames before the first change
	hold?: number; // frames each word stays (default 34)
	transition?: number; // frames of one change (default 14)
	loop?: boolean; // keep cycling (default false: stop on the last word)
	reveal?: 'mask' | 'blur' | 'flip';
	width?: 'animate' | 'max'; // the slot's width follows the word (measured) or stays at the widest word
	wordColor?: string; // default: the accent
	align?: 'left' | 'center' | 'right';
	style?: React.CSSProperties;
};

export const WordRotator: React.FC<WordRotatorProps> = (props) => {
	const {words, prefix = '', suffix = '', loop = false, reveal = 'mask', width = 'animate', align = 'left'} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const all = `${prefix}${words.join(' ')}${suffix}`;
	const ts = typeStyle(t, unit, all, props, 96);
	const ready = useTypeFontsReady(props.role ?? 'display');
	const tsKey = JSON.stringify(ts);
	const widths = useMemo(
		() => (ready && width === 'animate' ? words.map((w) => measureTextWidth(w, ts)) : null),
		[ready, width, words.join('|'), tsKey], // ts is keyed by tsKey
	);
	const hold = props.hold ?? at30(34, fps);
	const transition = props.transition ?? at30(14, fps);
	const delay = props.delay ?? 0;
	const n = words.length;
	// change k (1 based) moves from word k-1 to word k; it starts `hold` frames after the previous one settled
	const period = hold + transition;
	const first = delay + hold;
	let k = frame < first ? 0 : Math.floor((frame - first) / period) + 1;
	if (!loop) {
		k = Math.min(k, n - 1);
	}
	const p = k > 0 ? ramp(frame, first + (k - 1) * period, transition, curves.inOutQuart) : 1;
	const cur = words[k % n] ?? '';
	const prev = words[(k - 1 + n) % n] ?? '';
	const moving = k > 0 && p < 1;
	const pad = maskPad(all);
	const travel = ts.lineHeight + pad.top + pad.bottom + 0.04;
	const wordColor = props.wordColor ?? t.colors.accent;
	const slotW = widths ? (moving ? lerp(widths[(k - 1 + n) % n], widths[k % n], p) : widths[k % n]) : undefined;

	const face = (w: string, y: number, o: number, blur: number, rot: number, key: string) => (
		<span
			key={key}
			style={{
				position: 'absolute',
				left: 0,
				top: `${pad.top}em`,
				whiteSpace: 'pre',
				translate: `0 ${y}em`,
				opacity: o,
				filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
				transform: rot ? `perspective(${6 * ts.fontSize}px) rotateX(${rot}deg)` : undefined,
				transformOrigin: '50% 50%',
			}}
		>
			{w}
		</span>
	);

	let faces: React.ReactNode[];
	if (!moving) {
		faces = [face(cur, 0, 1, 0, 0, 'cur')];
	} else if (reveal === 'blur') {
		faces = [face(prev, -0.18 * p, 1 - p, 10 * p * unit, 0, 'prev'), face(cur, 0.18 * (1 - p), p, 10 * (1 - p) * unit, 0, 'cur')];
	} else if (reveal === 'flip') {
		faces = [
			face(prev, 0, p < 0.5 ? 1 : 0, 0, -90 * Math.min(1, p * 2), 'prev'),
			face(cur, 0, p >= 0.5 ? 1 : 0, 0, 90 * (1 - Math.min(1, (p - 0.5) * 2)), 'cur'),
		];
	} else {
		faces = [face(prev, -p * travel, 1, 0, 0, 'prev'), face(cur, (1 - p) * travel, 1, 0, 0, 'cur')];
	}

	return (
		<div style={{...typeCss(ts), color: props.color ?? t.colors.text, textAlign: align, whiteSpace: 'pre', ...props.style}}>
			{prefix}
			<span
				style={{
					display: 'inline-block',
					position: 'relative',
					verticalAlign: 'top',
					overflow: reveal === 'mask' ? 'hidden' : 'visible',
					paddingTop: `${pad.top}em`,
					paddingBottom: `${pad.bottom}em`,
					marginTop: `${-pad.top}em`,
					marginBottom: `${-pad.bottom}em`,
					width: slotW,
					color: wordColor,
				}}
			>
				{/* the widest word (or the current one) sizes the slot; it is never visible itself */}
				<span style={{visibility: 'hidden', display: 'inline-grid'}}>
					{(width === 'max' || !widths ? words : [cur]).map((w, i) => (
						<span key={i} style={{gridArea: '1 / 1'}}>
							{w}
						</span>
					))}
				</span>
				{faces}
			</span>
			{suffix}
		</div>
	);
};
