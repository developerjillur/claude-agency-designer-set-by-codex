import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Animate, Float, Ground, KineticTitle, LogoReveal, PushIn, curves, ramp, useStage, useTheme} from '../kit';
import {LEDGERLY_MARK} from '../brand';
import {DOWNBEAT} from '../cues';
import {PAPER_AND_CO, ReceiptPhoto, type ReceiptData} from './Photo';

// Frame 0 is the poster: the lockup, the promise and the problem (a receipt waiting to be billed). More receipts land
// on the beats, the pile a freelancer knows; the invoice itself first appears in the demo, so its story (made, sent,
// paid) runs once, in order.
const CITY: ReceiptData = {vendor: 'CITY PRINT LAB', lines: [['Photo prints x 12', '$54.50'], ['Mounting', '$10.00']], total: '$64.50'};
const METRO: ReceiptData = {vendor: 'METRO COURIER', lines: [['Same-day, 2 parcels', '$18.00']], total: '$18.00'};
const BEAT = (DOWNBEAT[1] - DOWNBEAT[0]) / 4;

export const Hook: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const frame = useCurrentFrame();
	const second = Math.round(DOWNBEAT[0] + 2 * BEAT);
	const third = DOWNBEAT[1];
	const scan = ramp(frame, third + 30, 30, curves.inOut);
	const drop = (delay: number, children: React.ReactNode) => (
		<Animate in="drop" delay={delay} duration={14} distance={320} ease={curves.outBack}>
			{children}
		</Animate>
	);
	return (
		<Ground kind="spot" light={[0.3, 0.4]}>
			{/* anchored on the text's left edge: the push moves only the receipts, never the words past the safe area */}
			<PushIn amount={0.04} origin="5.4% 50%">
				{/* LogoReveal fills its box: a box of its own, as wide as the lockup so it sits on the left edge */}
				<div style={{position: 'absolute', left: 104 * unit, top: 240 * unit, width: 470 * unit, height: 120 * unit}}>
					<LogoReveal mark={LEDGERLY_MARK} name="Ledgerly" variant="mask" size={76} delay={-40} background="none" push={0} />
				</div>
				<div style={{position: 'absolute', left: 104 * unit, top: 410 * unit, width: 820 * unit}}>
					<KineticTitle text={'Invoices in\none click.'} size={124} emphasis="click." emphasisStyle="color" in="none" />
				</div>
				<div style={{position: 'absolute', left: 108 * unit, top: 740 * unit, fontFamily: t.type.body, fontSize: 40 * unit, color: t.colors.muted}}>Invoicing for freelancers</div>
				<div style={{position: 'absolute', left: 1010 * unit, top: 210 * unit, rotate: '-7deg'}}>
					<Float amp={5} rotate={0.4} freq={0.3}>
						<ReceiptPhoto width={340} receipt={PAPER_AND_CO} />
					</Float>
				</div>
				<div style={{position: 'absolute', left: 1330 * unit, top: 260 * unit, rotate: '6deg'}}>
					{drop(second, (
						<Float amp={5} rotate={0.4} freq={0.28} lane={1}>
							<ReceiptPhoto width={330} receipt={CITY} />
						</Float>
					))}
				</div>
				<div style={{position: 'absolute', left: 1150 * unit, top: 470 * unit, rotate: '-2deg'}}>
					{drop(third, (
						<Float amp={5} rotate={0.4} freq={0.32} lane={2}>
							<ReceiptPhoto width={340} receipt={METRO} scan={scan} />
						</Float>
					))}
				</div>
			</PushIn>
		</Ground>
	);
};
