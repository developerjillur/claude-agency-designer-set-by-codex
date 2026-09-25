// <TextPlate>: the TikTok and Instagram caption plate. Measured lines get one rounded outline that hugs every line
// (@remotion/rounded-text-box: rounded outer corners, inverse-rounded inner corners), drawn behind the text.
import {evolvePath} from '@remotion/paths';
import {createRoundedTextBox} from '@remotion/rounded-text-box';
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme, type Theme} from '../core';
import {ramp, springAt, type Reveal} from '../motion';
import {typeStyle, useTypeFontsReady, type TypeProps} from './fonts';
import {layoutText, typeCss} from './layout';
import {RevealUnit} from './SplitText';
import {isComplexScript} from './text';

export type PlateTone = 'invert' | 'accent' | 'surface' | 'light' | 'dark';

export const plateColors = (t: Theme, tone: PlateTone): {plate: string; text: string} => {
	switch (tone) {
		case 'accent':
			return {plate: t.colors.accent, text: t.colors.onAccent};
		case 'surface':
			return {plate: t.colors.surface, text: t.colors.text};
		case 'light':
			return {plate: '#FFFFFF', text: '#111111'};
		case 'dark':
			return {plate: 'rgba(12, 12, 14, 0.82)', text: '#FFFFFF'};
		case 'invert':
		default:
			return {plate: t.colors.text, text: t.colors.bg};
	}
};

export type TextPlateProps = TypeProps & {
	text: string; // `\n` for forced breaks
	lines?: readonly string[];
	maxWidth?: number; // px at 1080 (default 86% of the safe width)
	maxLines?: number; // default 3: the size shrinks to fit
	align?: 'left' | 'center' | 'right';
	padding?: number; // horizontal padding, px at 1080 (default 0.45 of the size)
	radius?: number; // px at 1080 (default 0.36 of the size)
	tone?: PlateTone; // default 'invert' (text colour plate, ground colour text)
	plateColor?: string;
	textColor?: string;
	delay?: number;
	plateIn?: 'pop' | 'wipe' | 'draw' | 'none';
	textIn?: Reveal; // per line (default 'mask')
	out?: boolean; // shrink and fade at the end of the Sequence (default true)
	style?: React.CSSProperties;
};

export const TextPlate: React.FC<TextPlateProps> = (props) => {
	const {text, align = 'center', tone = 'invert', delay = 0, plateIn = 'pop', out = true} = props;
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, safe, fps, durationInFrames} = useStage();
	const source = props.lines ? props.lines.join('\n') : text;
	const complex = isComplexScript(source);
	const ts = typeStyle(t, unit, source, {strong: true, lineHeight: complex ? 1.55 : 1.34, ...props}, 60, 'body');
	const ready = useTypeFontsReady(props.role ?? 'body');
	const size = ts.fontSize;
	const hp = (props.padding ?? (0.45 * size) / unit) * unit;
	const radius = (props.radius ?? (0.36 * size) / unit) * unit;
	const maxW = (props.maxWidth ?? (safe.w / unit) * 0.86) * unit;
	const tsKey = JSON.stringify(ts);
	const shape = useMemo(() => {
		if (!ready) {
			return null;
		}
		const layout = layoutText(source, ts, {maxWidth: maxW - 2 * hp, maxLines: props.maxLines ?? 3});
		const box = createRoundedTextBox({
			textMeasurements: layout.lines.map((l) => ({width: l.width, height: layout.lineHeightPx})),
			textAlign: align,
			horizontalPadding: hp,
			borderRadius: radius,
		});
		return {layout, box};
	}, [ready, source, tsKey, maxW, hp, radius, align, props.maxLines]); // ts is keyed by tsKey
	if (!shape) {
		return null;
	}
	const {layout, box} = shape;
	const colors = plateColors(t, tone);
	const plate = props.plateColor ?? colors.plate;
	const ink = props.textColor ?? colors.text;
	const bb = box.boundingBox;

	// plate entrance
	const pop = plateIn === 'pop' ? springAt(frame, fps, {delay, config: 'settle'}) : 1;
	const appear = plateIn === 'none' ? 1 : ramp(frame, delay, at30(plateIn === 'draw' ? 22 : 6, fps), curves.out);
	const outDur = at30(10, fps);
	const q = out ? ramp(frame, durationInFrames - 1 - outDur, outDur, curves.in) : 0;
	const scale = (plateIn === 'pop' ? 0.9 + 0.1 * pop : 1) * (1 - 0.05 * q);
	const draw = plateIn === 'draw' ? evolvePath(appear, box.d) : null;
	const fill = plateIn === 'draw' ? ramp(frame, delay + at30(16, fps), at30(8, fps)) : 1;
	const textDelay = delay + at30(plateIn === 'none' ? 0 : plateIn === 'draw' ? 14 : 4, fps);
	const textIn = props.textIn ?? 'mask';

	return (
		<div
			style={{
				position: 'relative',
				width: bb.width,
				height: bb.height,
				scale: `${scale}`,
				opacity: (plateIn === 'pop' ? Math.min(1, appear * 1.6) : 1) * (1 - q),
				clipPath: plateIn === 'wipe' ? `inset(-10% ${(1 - appear) * 100}% -10% -10%)` : undefined,
				...props.style,
			}}
		>
			<svg viewBox={bb.viewBox} width={bb.width} height={bb.height} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				<path
					d={box.d}
					fill={plate}
					fillOpacity={fill}
					stroke={draw ? plate : undefined}
					strokeWidth={draw ? 3 * unit : undefined}
					strokeDasharray={draw?.strokeDasharray}
					strokeDashoffset={draw?.strokeDashoffset}
				/>
			</svg>
			<div style={{position: 'relative', ...typeCss({...ts, fontSize: layout.fontSize}), color: ink}}>
				{layout.lines.map((line, i) => (
					<div key={i} style={{whiteSpace: 'pre', textAlign: align, paddingLeft: hp, paddingRight: hp, height: layout.lineHeightPx}}>
						<RevealUnit
							text={line.text}
							kind={textIn}
							out="none"
							delay={textDelay + i * at30(4, fps)}
							duration={at30(14, fps)}
							lineHeight={ts.lineHeight}
						/>
					</div>
				))}
			</div>
		</div>
	);
};
