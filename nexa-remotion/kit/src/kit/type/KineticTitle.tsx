// <KineticTitle>: a headline that rises out of masks word by word (or line by line), set tight like a designer
// would set it: measured, balanced lines, tracking that tightens with size, and one emphasised word that punches in
// from its baseline so it never wobbles.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, clamp, curves, useStage, useTheme} from '../core';
import {ramp, springAt, type Reveal} from '../motion';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {baselineRatio, layoutText, typeCss} from './layout';
import {RevealUnit, staggerRank, type RevealTiming} from './SplitText';

export type EmphasisStyle = 'punch' | 'color' | 'marker' | 'block';

export type KineticTitleProps = TypeProps &
	RevealTiming & {
		text: string; // `\n` forces a line break
		by?: 'word' | 'line';
		lines?: readonly string[]; // given lines instead of measured ones
		maxWidth?: number; // px at 1080 (default: the safe width)
		maxLines?: number; // default 3: the size shrinks until the title fits
		align?: 'left' | 'center' | 'right';
		emphasis?: string | number | readonly (string | number)[]; // words (text or index) to emphasise
		emphasisColor?: string; // default: the accent
		emphasisStyle?: EmphasisStyle; // default 'punch'
		style?: React.CSSProperties;
	};

const clean = (w: string) => w.toLowerCase().replace(/[^\p{L}\p{N}\p{M}]+/gu, '');

const isEmphasis = (word: string, index: number, e: KineticTitleProps['emphasis']): boolean => {
	if (e === undefined) {
		return false;
	}
	const list = Array.isArray(e) ? e : [e];
	return list.some((x) => (typeof x === 'number' ? x === index : clean(x) === clean(word)));
};

// the emphasis: a punch from 1.12 to 1 with a small settle, pivoting on the baseline
const Punch: React.FC<{at: number; origin: string; enabled: boolean; children: React.ReactNode}> = ({at, origin, enabled, children}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	if (!enabled) {
		return <>{children}</>;
	}
	const s = springAt(frame, fps, {delay: at, config: 'pop', from: 1.12, to: 1});
	return <span style={{display: 'inline-block', scale: `${frame < at ? 1.12 : s}`, transformOrigin: origin}}>{children}</span>;
};

/**
 * A bar that sweeps in behind the word once it has landed and clears when the word leaves. 'marker' sits on the
 * lower half like a highlighter pen; 'block' fills the line and repaints the text in `ink` exactly where the bar
 * is (a clipped copy), so light text on a bright bar never goes unreadable.
 */
const Sweep: React.FC<{
	at: number;
	exitStart: number | null;
	exitDur: number;
	color: string;
	block: boolean;
	baseline: number; // em from the top of the line box
	lineHeight: number;
	ink?: React.ReactNode;
	children: React.ReactNode;
}> = ({at, exitStart, exitDur, color, block, baseline, lineHeight, ink, children}) => {
	const frame = useCurrentFrame();
	const {fps} = useStage();
	const p = clamp(springAt(frame, fps, {delay: at, config: 'calm', durationInFrames: at30(14, fps)}));
	const q = exitStart === null ? 0 : ramp(frame, exitStart, exitDur, curves.in);
	const w = Math.max(0, p - q);
	const bleed = 0.08;
	return (
		<span style={{display: 'inline-block', position: 'relative'}}>
			{w > 0 ? (
				<span
					style={{
						position: 'absolute',
						left: `calc(${q * 100}% - ${bleed}em)`,
						width: `calc(${w * 100}% + ${2 * bleed * w}em)`,
						top: block ? '0.04em' : `${baseline - 0.36}em`,
						height: block ? `${lineHeight - 0.08}em` : '0.46em',
						background: color,
						borderRadius: '0.04em',
					}}
				/>
			) : null}
			{children}
			{ink && w > 0 ? (
				<span style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', clipPath: `inset(-40% ${(1 - p) * 100}% -40% ${q * 100}%)`}}>
					{ink}
				</span>
			) : null}
		</span>
	);
};

export const KineticTitle: React.FC<KineticTitleProps> = (props) => {
	const {text, by = 'word', align = 'left', emphasisStyle = 'punch'} = props;
	const t = useTheme();
	const {unit, safe, fps, durationInFrames, vertical} = useStage();
	const ready = useTypeFontsReady(props.role ?? 'display');
	const ts = typeStyle(t, unit, text, props, vertical ? 104 : 124);
	const tsKey = JSON.stringify(ts);
	const maxW = (props.maxWidth ?? safe.w / unit) * unit;
	const source = props.lines ? props.lines.join('\n') : text;
	const layout = useMemo(
		() => (ready ? layoutText(source, ts, {maxWidth: maxW, maxLines: props.maxLines ?? 3}) : null),
		[ready, source, tsKey, maxW, props.maxLines], // ts is keyed by tsKey
	);
	const color = props.color ?? t.colors.text;
	if (!layout) {
		return <div style={{...typeCss(ts), color, visibility: 'hidden', ...props.style}}>{text}</div>;
	}

	const kind: Reveal = props.in ?? 'mask';
	const out: Reveal = props.out ?? 'none';
	const each = props.each ?? at30(by === 'line' ? 6 : 3, fps);
	const duration = props.duration ?? at30(Math.max(14, t.motion.enterFrames), fps);
	const outDuration = props.outDuration ?? at30(t.motion.exitFrames, fps);
	const outEach = props.outEach ?? 0;
	const delay = props.delay ?? 0;
	const accent = props.emphasisColor ?? t.colors.accent;
	// a marker on a dark ground becomes a block with the text repainted in the ground colour where it is covered
	const block = emphasisStyle === 'block' || (emphasisStyle === 'marker' && t.dark);
	const style = {...ts, fontSize: layout.fontSize};
	const base = baselineRatio(style.fontFamily, style.fontWeight, style.lineHeight);
	const total = by === 'line' ? layout.lines.length : layout.words.length;
	const timing = (i: number) => {
		const rank = staggerRank(i, total, props.order ?? 'forward', props.seed ?? 'title');
		return {
			delay: delay + Math.round(rank * each),
			outAt: outEach > 0 ? durationInFrames - 1 - outDuration - (total - 1 - rank) * outEach : undefined,
		};
	};

	return (
		<div style={{...typeCss(style), color, width: maxW, ...props.style}}>
			{layout.lines.map((line, li) => (
				<div key={li} style={{whiteSpace: 'pre', textAlign: align}}>
					{by === 'line' ? (
						<RevealUnit
							text={line.text}
							kind={kind}
							out={out}
							duration={duration}
							outDuration={outDuration}
							distance={props.distance}
							lineHeight={style.lineHeight}
							{...timing(li)}
						>
							{line.words.map((w, wi) => (
								<React.Fragment key={wi}>
									{wi ? ' ' : null}
									{isEmphasis(w.text, w.index, props.emphasis) ? <span style={{color: accent}}>{w.text}</span> : w.text}
								</React.Fragment>
							))}
						</RevealUnit>
					) : (
						line.words.map((w, wi) => {
							const tm = timing(w.index);
							const emph = isEmphasis(w.text, w.index, props.emphasis);
							const ox = wi === 0 && align === 'left' ? 0 : wi === line.words.length - 1 && align === 'right' ? 100 : 50;
							const unitOf = (innerStyle?: React.CSSProperties) => (
								<RevealUnit
									text={w.text}
									kind={kind}
									out={out}
									duration={duration}
									outDuration={outDuration}
									distance={props.distance}
									lineHeight={style.lineHeight}
									innerStyle={innerStyle}
									{...tm}
								/>
							);
							const swept = emph && (emphasisStyle === 'marker' || emphasisStyle === 'block');
							const unitNode = unitOf(emph && !swept ? {color: accent} : undefined);
							const exitStart = out === 'none' ? null : (tm.outAt ?? durationInFrames - 1 - outDuration);
							return (
								<React.Fragment key={wi}>
									{wi ? ' ' : null}
									{swept ? (
										<Sweep
											at={tm.delay + Math.round(duration * 0.6)}
											exitStart={exitStart}
											exitDur={outDuration}
											color={props.emphasisColor ?? t.colors.highlight}
											block={block}
											baseline={base * style.lineHeight}
											lineHeight={style.lineHeight}
											ink={block ? unitOf({color: t.dark ? t.colors.bg : t.colors.text}) : undefined}
										>
											{unitNode}
										</Sweep>
									) : (
										<Punch at={tm.delay} origin={`${ox}% ${base * 100}%`} enabled={emph && emphasisStyle === 'punch'}>
											{unitNode}
										</Punch>
									)}
								</React.Fragment>
							);
						})
					)}
				</div>
			))}
		</div>
	);
};
