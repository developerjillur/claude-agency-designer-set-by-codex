import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Animate, Card, Float, HandMark, KineticTitle, Marked, curves, fontStack, ramp, useStage, useTheme} from '../kit';
import {CUE, CUT} from '../cues';
import {STAGE_TOP, WORDS_TOP} from '../layout';

// The hook: the paper ledger most shops still keep (illustrative rows). It is messy the way real ones are: the egg
// price was corrected but the total was not, so in the first second the total is struck and rewritten in red. The
// wrong total is circled as the voice says "খাতায়".
const ROWS: [string, string][] = [
	['চাল ৫ কেজি', '৩৮০'],
	['ডাল ২ কেজি', '২৪০'],
	['তেল ১ লিটার', '১৯০'],
];
const INK = '#22304A';
const RED = '#C4122F';

// handwriting: the words appear left to right
const Write: React.FC<{at: number; dur: number; color: string; children: React.ReactNode}> = ({at, dur, color, children}) => {
	const frame = useCurrentFrame();
	const p = ramp(frame, at, dur, curves.inOut);
	return (
		<span style={{display: 'inline-block', color, padding: '0.25em 0', margin: '-0.25em 0', clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`}}>
			{children}
		</span>
	);
};

export const Notebook: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const hand = fontStack('Atma', [500, 600], null);
	const row = (i: number, last = false): React.CSSProperties => ({
		display: 'flex',
		justifyContent: 'space-between',
		alignItems: 'baseline',
		fontFamily: hand,
		fontWeight: last ? 600 : 500,
		fontSize: 50 * unit,
		color: INK,
		lineHeight: 1.15,
		padding: `${14 * unit}px 0`,
		borderBottom: last ? 'none' : `${2 * unit}px solid rgba(34, 48, 74, 0.2)`,
		rotate: `${i % 2 ? -0.6 : 0.5}deg`,
	});
	const pair: React.CSSProperties = {display: 'flex', alignItems: 'baseline', gap: 18 * unit};
	return (
		<AbsoluteFill>
			{/* the title leaves before the first caption arrives (they share the top band) */}
			<Sequence durationInFrames={CUT.phone - 4}>
				<div style={{position: 'absolute', left: 90 * unit, right: 90 * unit, top: WORDS_TOP * unit}}>
					<KineticTitle text="দোকানের হিসাব কি এখনও খাতায়?" size={84} align="center" in="none" out="fade" outDuration={8} emphasis="খাতায়" emphasisStyle="color" emphasisColor={t.colors.highlight} maxLines={2} />
				</div>
			</Sequence>
			<div style={{position: 'absolute', left: 170 * unit, top: (STAGE_TOP + 70) * unit, width: 740 * unit}}>
				<Animate in="none" out="left" outAt={CUT.phone - 6} outDuration={16} distance={380}>
					<Float amp={5} rotate={0.5} freq={0.35}>
						<Card variant="paper" tilt={-3} width={740} padding={[52, 64]} color="#F3EEDF">
							<div style={{fontFamily: hand, fontWeight: 600, fontSize: 62 * unit, color: INK, marginBottom: 10 * unit}}>হিসাবের খাতা</div>
							{ROWS.map(([item, price], i) => (
								<div key={item} style={row(i)}>
									<span>{item}</span>
									<span>{price}</span>
								</div>
							))}
							{/* the corrected egg price, already on the page */}
							<div style={row(3)}>
								<span>ডিম ১ ডজন</span>
								<span style={pair}>
									<Marked kind="strike" progress={1} color={INK} size={5}>
										১৪০
									</Marked>
									<span style={{color: RED}}>১৫০</span>
								</span>
							</div>
							{/* the total still adds the old price: struck and rewritten */}
							<div style={row(4, true)}>
								<span>মোট</span>
								<span style={pair}>
									<Marked kind="strike" delay={6} duration={10} color={RED} size={6}>
										৯৫০
									</Marked>
									<Write at={14} dur={16} color={RED}>
										৯৬০?
									</Write>
								</span>
							</div>
						</Card>
					</Float>
				</Animate>
			</div>
			{/* the circle lands on the mistake (the total that was never corrected), not on the whole book */}
			<HandMark
				kind="circle"
				width={720}
				height={190}
				delay={CUE.khata - 14}
				color={t.colors.highlight}
				size={10}
				exit="fade"
				outAt={CUT.phone - 8}
				outDuration={10}
				style={{position: 'absolute', left: 195 * unit, top: (STAGE_TOP + 505) * unit, rotate: '-3deg'}}
			/>
		</AbsoluteFill>
	);
};
