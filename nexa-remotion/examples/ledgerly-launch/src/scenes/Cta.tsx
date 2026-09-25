import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Animate, EndCard, Ground, LogoMarkView, Notification, PushIn, curves, ramp, useStage, useTheme, wiggle} from '../kit';
import {LEDGERLY_MARK} from '../brand';
import {PAID_NOTE, STAMP} from '../cues';
import {InvoiceCard} from './InvoiceCard';

// The close: the call to action (no pointer: a click that changes nothing reads as a dead button), and the invoice
// from the demo getting paid: the payment arrives on the last downbeat, the stamp lands on the song's last kick (on
// the card's corner, over the status, clear of the amounts).
const Stamp: React.FC<{at: number}> = ({at}) => {
	const t = useTheme();
	const frame = useCurrentFrame();
	const {unit, fps} = useStage();
	const p = ramp(frame, at, 6, curves.in);
	const settle = frame >= at + 6 ? Math.max(0, 1 - (frame - at - 6) / 8) : 0;
	const shake = wiggle(frame, fps, 14, 3) * 6 * settle;
	if (frame < at) {
		return null;
	}
	return (
		<div style={{position: 'absolute', right: -20 * unit, top: -30 * unit, rotate: '-12deg', scale: `${1.9 - 0.9 * p}`, opacity: p, translate: `${shake * unit}px ${shake * 0.6 * unit}px`}}>
			<div style={{fontFamily: t.type.display, fontWeight: 900, fontSize: 70 * unit, letterSpacing: '0.08em', color: '#12A36B', border: `${6 * unit}px solid #12A36B`, borderRadius: 14 * unit, padding: `${2 * unit}px ${22 * unit}px`, background: '#E6F7EF'}}>PAID</div>
		</div>
	);
};

export const Cta: React.FC = () => {
	const {unit, safe, width} = useStage();
	return (
		<Ground kind="spot" light={[0.3, 0.3]}>
			{/* a linear push, anchored on the text's left edge, keeps the held last frames moving (an eased push stops
			    dead at the end and reads as a frozen picture) */}
			<PushIn amount={0.04} ease={curves.linear} origin="5.4% 50%">
			{/* everything arrives after the zoom-through has settled */}
			<EndCard title="Start free today" subtitle="Invoices in one click." cta="Try Ledgerly" url="ledgerly.example" handle="@ledgerly" name="Ledgerly" logo={<LogoMarkView mark={LEDGERLY_MARK} size={44} />} delay={10} push={0} background="none" />
			<div style={{position: 'absolute', left: 1040 * unit, top: 290 * unit, width: 640 * unit, rotate: '3deg'}}>
				<Animate in="rise" delay={16} distance={40}>
					<div style={{position: 'relative'}}>
						<InvoiceCard
							statuses={[
								{at: 0, status: 'Sent'},
								{at: STAMP, status: 'Paid'},
							]}
							scale={1.1}
						/>
						<Stamp at={STAMP} />
					</div>
				</Animate>
			</div>
			{/* why it is paid: the money arrives on the downbeat, the stamp follows on the last kick */}
			{/* drawn life-size, so scaled up to read in a video (anchored on the safe corner), and clipped inside the safe
			    area so its slide-in never puts a letter past the edge */}
			<div style={{position: 'absolute', inset: 0, clipPath: `inset(${safe.y}px ${width - safe.x - safe.w + 14 * unit}px ${safe.y}px ${safe.x}px)`}}>
				<div style={{position: 'absolute', inset: 0, scale: '1.35', transformOrigin: `${safe.x + safe.w - 24 * unit}px ${safe.y}px`}}>
					<Notification variant="desktop" app="Ledgerly" title="Payment received" body="Invoice #1042: $108.00 from Northwind Studio" icon="check" time="now" delay={PAID_NOTE} area="safe" place="top-right" inset={24} width={600} mode="dark" />
				</div>
			</div>
			</PushIn>
		</Ground>
	);
};
