// <FitText>: the biggest size at which a text fits a width on one line (fitText) or on N lines (fitTextOnNLines),
// measured with @remotion/layout-utils after the fonts load. Tracking is in em (it scales linearly with the size,
// which fitText assumes) and is re-derived once for the size found. The lines are rendered exactly as measured.
import {fitText, fitTextOnNLines} from '@remotion/layout-utils';
import React, {useMemo} from 'react';
import {at30, useStage, useTheme} from '../core';
import type {Reveal} from '../motion';
import {trackingFor, typeStyle, useTypeFontsReady, type FontNeed, type TypeProps} from './fonts';
import {typeCss, type TypeStyle} from './layout';
import {RevealUnit} from './SplitText';

export type FitTextOptions = TypeProps & {
	maxWidth?: number; // px at 1080 (default: the safe width)
	maxLines?: number; // default 1
	maxSize?: number; // px at 1080 (default 280)
	minSize?: number; // px at 1080 (default 24)
	fonts?: FontNeed[]; // extra kit fonts to wait for (with a custom fontFamily)
};

export type FitTextResult = {fontSize: number; lines: string[]; style: TypeStyle; width: number};

const fitOnce = (text: string, s: TypeStyle, maxW: number, maxLines: number, maxSize: number): {fontSize: number; lines: string[]} => {
	const common = {
		fontFamily: s.fontFamily,
		fontWeight: s.fontWeight,
		letterSpacing: `${s.letterSpacing}em`,
		textTransform: s.textTransform ?? 'none',
		validateFontIsLoaded: true,
	} as const;
	if (maxLines <= 1) {
		const {fontSize} = fitText({text, withinWidth: maxW, ...common, additionalStyles: {textRendering: 'geometricPrecision'}});
		return {fontSize: Math.min(maxSize, fontSize), lines: [text]};
	}
	return fitTextOnNLines({
		text,
		maxBoxWidth: maxW,
		maxLines,
		maxFontSize: maxSize,
		...common,
		additionalStyles: {textRendering: 'geometricPrecision'},
	});
};

/** The fitted size and lines of `text` (null until the fonts have loaded). */
export const useFitText = (text: string, o: FitTextOptions = {}): FitTextResult | null => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const ready = useTypeFontsReady(o.role ?? 'display', o.fonts ?? []);
	const maxW = (o.maxWidth ?? safe.w / unit) * unit;
	const maxLines = o.maxLines ?? 1;
	const maxSize = (o.maxSize ?? 280) * unit;
	const minSize = (o.minSize ?? 24) * unit;
	const base = typeStyle(t, unit, text, {...o, size: o.maxSize ?? 280}, 280);
	const key = JSON.stringify([base, maxW, maxLines, maxSize, minSize, o.tracking]);
	return useMemo(() => {
		if (!ready || !text.trim()) {
			return null;
		}
		const first = fitOnce(text, base, maxW, maxLines, maxSize);
		// tracking follows the size: refit once with the tracking of the size found
		const caps = base.textTransform === 'uppercase';
		const tracking = o.tracking ?? trackingFor(t, first.fontSize / unit, text, o.role ?? 'display', caps);
		const style = {...base, letterSpacing: tracking};
		const second = tracking === base.letterSpacing ? first : fitOnce(text, style, maxW, maxLines, maxSize);
		const fontSize = Math.max(minSize, second.fontSize);
		return {fontSize, lines: second.lines, style: {...style, fontSize}, width: maxW};
	}, [ready, text, key]); // base and the options are keyed by key
};

export type FitTextProps = FitTextOptions & {
	text: string;
	align?: 'left' | 'center' | 'right';
	in?: Reveal; // reveal the lines (default: none, the text is simply there)
	out?: Reveal;
	delay?: number;
	each?: number; // frames between lines
	style?: React.CSSProperties;
	children?: (fit: FitTextResult) => React.ReactNode; // render the fitted lines yourself
};

export const FitText: React.FC<FitTextProps> = (props) => {
	const {text, align = 'left'} = props;
	const t = useTheme();
	const {fps} = useStage();
	const fit = useFitText(text, props);
	if (!fit) {
		return null;
	}
	if (props.children) {
		return <>{props.children(fit)}</>;
	}
	const each = props.each ?? at30(5, fps);
	const reveal = props.in ?? 'none';
	return (
		<div style={{...typeCss(fit.style), color: props.color ?? t.colors.text, width: fit.width, textAlign: align, ...props.style}}>
			{fit.lines.map((line, i) => (
				<div key={i} style={{whiteSpace: 'pre'}}>
					{reveal === 'none' && (props.out ?? 'none') === 'none' ? (
						line
					) : (
						<RevealUnit
							text={line}
							kind={reveal}
							out={props.out ?? 'none'}
							delay={(props.delay ?? 0) + i * each}
							duration={at30(Math.max(14, t.motion.enterFrames), fps)}
							lineHeight={fit.style.lineHeight}
						/>
					)}
				</div>
			))}
		</div>
	);
};
