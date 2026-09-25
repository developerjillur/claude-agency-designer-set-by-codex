// Burned-in captions. <TikTokCaptions>: short pages of 2 to 4 words with the spoken word marked (colour, a pill that
// glides from word to word, a scale pop, a karaoke fill) or popping in word by word. <BoxedCaptions>: classic
// boxed subtitles (at most 42 characters a line, 2 lines). Both are laid out by measurement, sit inside the safe
// area (clear of the 9:16 interface) and follow a trimmed or sped-up clip through CaptionTiming.
import {createRoundedTextBox} from '@remotion/rounded-text-box';
import React, {useMemo} from 'react';
import {Artifact, useCurrentFrame} from 'remotion';
import {at30, clamp, curves, lerp, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {captionPageAt, captionPages, captionTimeAt, subtitleCues, toSrt, type Caption, type CaptionPageOptions, type CaptionTiming, type SubtitleCueOptions} from './captionData';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {textAlignOffset, baselineRatio, layoutText, measureTextWidth, typeCss, type TypeStyle} from './layout';
import {plateColors, type PlateTone} from './TextPlate';
import {bindsToNext, isComplexScript} from './text';

export type CaptionHighlight = 'color' | 'pill' | 'scale' | 'karaoke' | 'plain';

export type CaptionPosition = 'bottom' | 'center' | 'top' | number; // a number: the block's centre as a fraction of the safe height

export type TikTokCaptionsProps = TypeProps &
	CaptionTiming &
	CaptionPageOptions & {
		captions: readonly Caption[];
		highlight?: CaptionHighlight; // default 'pill'
		reveal?: 'page' | 'word'; // 'word': every word pops in as it is spoken (default 'page')
		maxLines?: number; // default 2
		maxWidth?: number; // px at 1080 (default: the safe width less 40)
		position?: CaptionPosition; // default 'bottom'
		tone?: 'light' | 'theme'; // light: white with a dark outline, for footage (default); theme: theme colours
		activeColor?: string; // default: the highlight colour (the accent for the pill)
		stroke?: number; // outline width as a fraction of the size (default 0.14, 0.1 for Bangla; 0 for none)
		plate?: PlateTone | false; // a rounded plate behind each page (default false)
		enter?: 'pop' | 'rise' | 'none'; // how each page arrives (default 'pop')
		style?: React.CSSProperties;
	};

type Placed = {text: string; fromMs: number; toMs: number; nextMs: number; x: number; y: number; w: number};

const blockTop = (position: CaptionPosition, safe: {y: number; h: number}, height: number): number => {
	if (position === 'top') {
		return safe.y + safe.h * 0.05;
	}
	if (position === 'center') {
		return safe.y + (safe.h - height) / 2;
	}
	if (typeof position === 'number') {
		return safe.y + safe.h * position - height / 2;
	}
	return safe.y + safe.h * 0.95 - height;
};

export const TikTokCaptions: React.FC<TikTokCaptionsProps> = (props) => {
	const {captions, highlight = 'pill', reveal = 'page', position = 'bottom', tone = 'light', enter = 'pop', plate = false} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps, vertical} = useStage();
	const ready = useTypeFontsReady(props.role ?? 'body');
	const pages = useMemo(
		() => captionPages(captions, {pageMs: props.pageMs, silenceMs: props.silenceMs, maxHoldMs: props.maxHoldMs, sentenceMs: props.sentenceMs}),
		[captions, props.pageMs, props.silenceMs, props.maxHoldMs, props.sentenceMs],
	);
	const now = captionTimeAt(frame, fps, props);
	const page = captionPageAt(pages, now);
	const sample = page?.text ?? '';
	const complex = isComplexScript(pages.map((p) => p.text).join(' '));
	// Bangla and other complex scripts read smaller at the same size: they get about 10% more
	const ts: TypeStyle = typeStyle(t, unit, sample, {strong: true, lineHeight: complex ? 1.42 : 1.14, ...props}, (vertical ? 76 : 58) * (complex ? 1.1 : 1), 'body');
	// 40 px short of the safe width, so the pill and the outline stay inside the safe area too
	const maxW = (props.maxWidth ?? safe.w / unit - 40) * unit;
	const tsKey = JSON.stringify(ts);
	// the scale style reserves room around every word (half of a 10 % growth on each side), so the spoken word can
	// grow without touching its neighbours
	const grow = highlight === 'scale' ? 0.05 : 0;
	const laid = useMemo(() => {
		if (!ready || !page) {
			return null;
		}
		const layout = layoutText(page.words.map((w) => w.text).join(' '), ts, {
			maxWidth: maxW / (1 + 2 * grow),
			maxLines: props.maxLines ?? 2,
			balance: true,
			// never "মোট / বিক্রি" or "the / end": a word that belongs with the next goes down with it
			noBreakAfter: bindsToNext,
		});
		const placed: Placed[] = [];
		layout.lines.forEach((line, li) => {
			const xs: number[] = [];
			let x = 0;
			line.words.forEach((lw, j) => {
				if (j) {
					x += layout.space + grow * (line.words[j - 1].width + lw.width);
				}
				xs.push(x);
				x += lw.width;
			});
			const lx = textAlignOffset('center', maxW, x);
			line.words.forEach((lw, j) => {
				const w = page.words[lw.index];
				const next = page.words[lw.index + 1];
				placed.push({text: w.text, fromMs: w.fromMs, toMs: w.toMs, nextMs: next ? next.fromMs : page.endMs, x: lx + xs[j], y: li * layout.lineHeightPx, w: lw.width});
			});
		});
		return {layout, placed};
	}, [ready, page, tsKey, maxW, props.maxLines, grow]); // ts is keyed by tsKey
	if (!page || !laid) {
		return null;
	}
	const {layout, placed} = laid;
	const fs = layout.fontSize;
	const style = {...ts, fontSize: fs};
	const lh = layout.lineHeightPx;
	const height = layout.lines.length * lh;
	const top = blockTop(position, safe, height);
	const left = safe.x + (safe.w - maxW) / 2;
	const plateTone = plate ? plateColors(t, plate) : null;
	const ink = plateTone ? plateTone.text : tone === 'light' ? '#FFFFFF' : t.colors.text;
	const strokeFrac = plateTone ? 0 : props.stroke ?? (tone === 'light' ? (complex ? 0.1 : 0.14) : 0);
	const outline: React.CSSProperties = strokeFrac > 0 ? {WebkitTextStroke: `${strokeFrac * fs}px rgba(0, 0, 0, 0.92)`, paintOrder: 'stroke fill'} : {};
	const shadow = tone === 'light' && !plateTone ? `0 ${0.05 * fs}px ${0.16 * fs}px rgba(0, 0, 0, 0.45)` : undefined;
	const active = props.activeColor ?? (highlight === 'pill' ? t.colors.accent : t.colors.highlight);
	const onPill = props.activeColor ? '#FFFFFF' : t.colors.onAccent;
	const base = baselineRatio(style.fontFamily, style.fontWeight, style.lineHeight);
	const glide = (at30(5, fps) / fps) * 1000;
	const popMs = (at30(4, fps) / fps) * 1000;

	// page entrance and, when the page ends on a pause, its exit
	const since = now - page.startMs;
	const inP = enter === 'none' ? 1 : ramp(since, 0, (at30(5, fps) / fps) * 1000, curves.out);
	const nextPage = pages[pages.indexOf(page) + 1];
	const endsOnPause = !nextPage || nextPage.startMs > page.endMs + 1;
	const outMs = (at30(5, fps) / fps) * 1000;
	const outP = endsOnPause ? ramp(now, page.endMs - outMs, outMs, curves.in) : 0;
	const pageScale = enter === 'pop' ? 0.9 + 0.1 * inP : 1;
	const pageY = enter === 'rise' ? (1 - inP) * 18 * unit : enter === 'pop' ? (1 - inP) * 10 * unit : 0;

	// the spoken word: the last word that has started (it stays marked through small gaps)
	let ai = -1;
	placed.forEach((w, i) => {
		if (w.fromMs <= now) {
			ai = i;
		}
	});

	// the pill glides between words: a fractional index from short eased steps around each word start
	let pill: {x: number; y: number; w: number; h: number; r: number; o: number} | null = null;
	if (highlight === 'pill' && placed.length) {
		const fi = placed.slice(1).reduce((acc, w) => acc + ramp(now, w.fromMs - glide / 2, glide, curves.inOut), 0);
		const i0 = Math.min(placed.length - 1, Math.floor(fi));
		const i1 = Math.min(placed.length - 1, i0 + 1);
		const f = fi - i0;
		const a = placed[i0];
		const b = placed[i1];
		const show = ramp(now, placed[0].fromMs - glide, glide, curves.outBack);
		if (show > 0) {
			const padX = 0.17 * fs;
			const padY = 0.06 * fs;
			const s = 0.6 + 0.4 * show;
			const w = (lerp(a.w, b.w, f) + 2 * padX) * s;
			// complex scripts hang vowel signs below the letters (ু, ূ): a taller pill, a little lower
			const h = (fs * (complex ? 1.38 : 1.12) + 2 * padY) * s;
			const cx = lerp(a.x + a.w / 2, b.x + b.w / 2, f);
			const cy = lerp(a.y, b.y, f) + lh / 2 + (complex ? 0.05 * fs : 0);
			pill = {x: cx - w / 2, y: cy - h / 2, w, h, r: 0.24 * fs * s, o: clamp(show * 1.4)};
		}
	}

	let plateNode: React.ReactNode = null;
	if (plateTone) {
		const hp = 0.4 * fs;
		const box = createRoundedTextBox({
			textMeasurements: layout.lines.map((l) => ({
				width: l.width + grow * l.words.reduce((a, w, j) => a + (j ? l.words[j - 1].width + w.width : 0), 0),
				height: lh,
			})),
			textAlign: 'center',
			horizontalPadding: hp,
			borderRadius: 0.32 * fs,
		});
		const bb = box.boundingBox;
		plateNode = (
			<svg viewBox={bb.viewBox} width={bb.width} height={bb.height} style={{position: 'absolute', left: (maxW - bb.width) / 2, top: 0, overflow: 'visible'}}>
				<path d={box.d} fill={plateTone.plate} />
			</svg>
		);
	}

	// one word; the 'pill' layer is the copy drawn on the pill (clipped to it), in the pill's text colour
	const word = (w: Placed, i: number, layer: 'base' | 'pill') => {
		const spoken = i <= ai;
		const isActive = i === ai;
		const pop = reveal === 'word' ? ramp(now, w.fromMs - 40, popMs, curves.outBack) : 1;
		let color = layer === 'pill' ? onPill : ink;
		let scale = pop < 1 ? 0.7 + 0.3 * pop : 1;
		let fill: React.ReactNode = null;
		if (layer === 'base') {
			if (highlight === 'color' && isActive) {
				color = active;
			} else if (highlight === 'scale' && isActive) {
				color = active;
				const env = Math.min(ramp(now, w.fromMs, popMs, curves.outBack), 1 - ramp(now, w.nextMs - 60, 120, curves.in));
				scale *= 1 + 0.1 * env;
			} else if (highlight === 'karaoke') {
				const p = spoken ? (i < ai ? 1 : clamp((now - w.fromMs) / Math.max(1, w.toMs - w.fromMs))) : 0;
				fill =
					p > 0 ? (
						<span style={{position: 'absolute', left: 0, top: 0, color: active, textShadow: 'none', clipPath: `inset(-20% ${(1 - p) * 100}% -20% -20%)`}}>
							{w.text}
						</span>
					) : null;
			}
		}
		return (
			<span
				key={`${layer}${i}`}
				style={{
					position: 'absolute',
					left: w.x,
					top: w.y,
					...typeCss(style),
					whiteSpace: 'pre',
					color,
					textShadow: layer === 'pill' ? undefined : shadow,
					...(layer === 'pill' ? {} : outline),
					scale: `${scale}`,
					opacity: reveal === 'word' ? clamp(pop * 1.5) : 1,
					transformOrigin: `50% ${base * 100}%`,
				}}
			>
				{w.text}
				{fill}
			</span>
		);
	};

	return (
		<div
			style={{
				position: 'absolute',
				left,
				top,
				width: maxW,
				height,
				scale: `${pageScale * (1 - 0.04 * outP)}`,
				translate: `0 ${pageY}px`,
				opacity: Math.min(1, inP * 1.5) * (1 - outP),
				transformOrigin: '50% 100%',
				...props.style,
			}}
		>
			{plateNode}
			{placed.map((w, i) => word(w, i, 'base'))}
			{pill ? (
				<>
					<div
						style={{
							position: 'absolute',
							left: pill.x,
							top: pill.y,
							width: pill.w,
							height: pill.h,
							borderRadius: pill.r,
							background: active,
							opacity: pill.o,
							boxShadow: `0 ${0.06 * fs}px ${0.2 * fs}px rgba(0, 0, 0, 0.25)`,
						}}
					/>
					{/* the text on the pill changes colour exactly where the pill is, even while it glides */}
					<div
						style={{
							position: 'absolute',
							left: 0,
							top: 0,
							width: maxW,
							height,
							opacity: pill.o,
							clipPath: `inset(${pill.y}px ${maxW - pill.x - pill.w}px ${height - pill.y - pill.h}px ${pill.x}px round ${pill.r}px)`,
						}}
					>
						{placed.map((w, i) => word(w, i, 'pill'))}
					</div>
				</>
			) : null}
		</div>
	);
};

export type BoxedCaptionsProps = TypeProps &
	CaptionTiming &
	SubtitleCueOptions & {
		captions: readonly Caption[];
		position?: 'bottom' | 'top';
		box?: string; // the line boxes (default near-black at 78%)
		textColor?: string; // default white
		readAlong?: boolean; // words not yet spoken are dimmer (default false)
		style?: React.CSSProperties;
	};

/** Classic subtitles: each cue centred low in the safe area, every line in its own box. */
export const BoxedCaptions: React.FC<BoxedCaptionsProps> = (props) => {
	const {captions, position = 'bottom', readAlong = false} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps, vertical} = useStage();
	const ready = useTypeFontsReady(props.role ?? 'body');
	const maxChars = props.maxChars ?? (vertical ? 32 : 42);
	const cues = useMemo(
		() => subtitleCues(captions, {maxChars, maxLines: props.maxLines, maxMs: props.maxMs, minMs: props.minMs, gapMs: props.gapMs, cps: props.cps}),
		[captions, maxChars, props.maxLines, props.maxMs, props.minMs, props.gapMs, props.cps],
	);
	const now = captionTimeAt(frame, fps, props);
	const cue = cues.find((c) => c.startMs <= now && now < c.endMs) ?? null;
	const sample = cues.map((c) => c.lines.join(' ')).join(' ');
	const complex = isComplexScript(sample);
	const ts = typeStyle(t, unit, sample, {weight: t.weights.body, lineHeight: complex ? 1.5 : 1.28, ...props}, vertical ? 50 : 46, 'body');
	const tsKey = JSON.stringify(ts);
	// a cue whose longest line is wider than the safe area is set smaller, never cut
	const fit = useMemo(() => {
		if (!ready || !cue) {
			return 1;
		}
		const widest = Math.max(...cue.lines.map((l) => measureTextWidth(l, ts)));
		return Math.min(1, (safe.w * 0.94 - 0.84 * ts.fontSize) / widest);
	}, [ready, cue, tsKey, safe.w]); // ts is keyed by tsKey
	if (!cue || !ready) {
		return null;
	}
	const fade = (at30(3, fps) / fps) * 1000;
	const o = Math.min(ramp(now, cue.startMs, fade), 1 - ramp(now, cue.endMs - fade, fade));
	const fs = ts.fontSize * fit;
	const box = props.box ?? 'rgba(8, 8, 8, 0.78)';
	const ink = props.textColor ?? '#FFFFFF';
	let wi = 0;
	return (
		<div
			style={{
				position: 'absolute',
				left: safe.x,
				width: safe.w,
				...(position === 'top' ? {top: safe.y + safe.h * 0.03} : {bottom: `calc(100% - ${safe.y + safe.h * 0.97}px)`}),
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'center',
				gap: 0.14 * fs,
				opacity: o,
				...props.style,
			}}
		>
			{cue.lines.map((line, li) => (
				<div
					key={li}
					style={{
						...typeCss({...ts, fontSize: fs}),
						color: ink,
						background: box,
						padding: `${0.08 * fs}px ${0.42 * fs}px`,
						borderRadius: 0.14 * fs,
						whiteSpace: 'pre',
					}}
				>
					{readAlong
						? line.split(' ').map((word, k) => {
								const w = cue.words[wi++];
								const said = w ? w.fromMs <= now : true;
								return (
									<React.Fragment key={k}>
										{k ? ' ' : null}
										<span style={{opacity: said ? 1 : 0.5}}>{word}</span>
									</React.Fragment>
								);
							})
						: line}
				</div>
			))}
		</div>
	);
};

/** Writes an .srt of the captions next to the render (out/<composition>/<filename>) on frame 0. */
export const SubtitleFile: React.FC<{captions: readonly Caption[]; filename?: string; options?: SubtitleCueOptions}> = ({
	captions,
	filename = 'subtitles.srt',
	options,
}) => {
	const frame = useCurrentFrame();
	const content = useMemo(() => toSrt(captions, options), [captions, options]);
	return frame === 0 ? <Artifact filename={filename} content={content} /> : null;
};
