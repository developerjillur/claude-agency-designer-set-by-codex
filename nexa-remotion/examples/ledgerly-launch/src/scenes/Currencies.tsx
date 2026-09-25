import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Animate, Ground, PushIn, SafeArea, Stagger, WordRotator, curves, ramp, useStage, useTheme} from '../kit';
import {INK, SOFT} from './InvoiceCard';

// Feature 3: three currencies, shown on the product. The word cycles; the chip of the word on screen lights up and an
// invoice in that currency lands under it (each for a client in that currency; all sample data).
const CHIPS: [string, string][] = [
	['$', 'US dollar'],
	['€', 'Euro'],
	['£', 'Pound sterling'],
];
const INVOICES: {no: string; client: string; total: string}[] = [
	{no: '#1042', client: 'Northwind Studio', total: '$108.00'},
	{no: '#1043', client: 'Atelier Brun', total: '€240.00'},
	{no: '#1044', client: 'Harbor & Co', total: '£180.00'},
];
const ROT = {delay: 10, hold: 26, transition: 12};
const landsAt = (i: number) => ROT.delay + i * (ROT.hold + ROT.transition);

const Chip: React.FC<{i: number; sym: string; name: string}> = ({i, sym, name}) => {
	const t = useTheme();
	const {unit} = useStage();
	const frame = useCurrentFrame();
	const on = ramp(frame, landsAt(i), 8) - (i < CHIPS.length - 1 ? ramp(frame, landsAt(i + 1), 8) : 0);
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: 16 * unit, background: t.colors.surface, border: `${2 * unit}px solid ${on > 0.5 ? t.colors.accent : t.colors.line}`, borderRadius: 999, padding: `${14 * unit}px ${28 * unit}px ${14 * unit}px ${14 * unit}px`, scale: `${1 + 0.07 * on}`, boxShadow: `0 0 ${36 * on * unit}px rgba(91, 140, 255, ${0.45 * on})`}}>
			<div style={{width: 52 * unit, height: 52 * unit, borderRadius: 26 * unit, background: t.colors.accent, color: t.colors.onAccent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: 800, fontSize: 28 * unit}}>{sym}</div>
			<div style={{fontFamily: t.type.body, fontWeight: 600, fontSize: 30 * unit, color: t.colors.text}}>{name}</div>
		</div>
	);
};

// the invoice of the currency on screen: it swaps as the word lands (a short rise), never mid-word
const MiniInvoice: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const frame = useCurrentFrame();
	let i = 0;
	for (let k = 0; k < INVOICES.length; k++) {
		if (frame >= landsAt(k) - 4) {
			i = k;
		}
	}
	const inv = INVOICES[i];
	const rise = i === 0 ? 1 : ramp(frame, landsAt(i) - 4, 10, curves.out);
	return (
		<div style={{width: 700 * unit, background: '#FFFFFF', borderRadius: 18 * unit, padding: `${22 * unit}px ${30 * unit}px`, boxShadow: `0 ${16 * unit}px ${40 * unit}px rgba(0,0,0,0.35)`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', overflow: 'hidden'}}>
			<div style={{opacity: rise, translate: `0 ${(1 - rise) * 14 * unit}px`}}>
				<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 32 * unit, color: INK}}>Invoice {inv.no}</div>
				<div style={{fontFamily: t.type.body, fontSize: 24 * unit, color: SOFT, marginTop: 4 * unit}}>Bill to {inv.client}</div>
			</div>
			<div style={{opacity: rise, translate: `0 ${(1 - rise) * 14 * unit}px`, textAlign: 'right'}}>
				<div style={{fontFamily: t.type.body, fontSize: 20 * unit, color: SOFT}}>Total due</div>
				<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 40 * unit, color: INK, fontVariantNumeric: 'tabular-nums'}}>{inv.total}</div>
			</div>
		</div>
	);
};

export const Currencies: React.FC = () => {
	const {unit} = useStage();
	return (
		<Ground kind="spot" light={[0.5, 0.45]} drift={0.25}>
			{/* a steady push: after the last word lands the scene holds, and a held frame read as frozen */}
			<PushIn amount={0.05} ease={curves.linear}>
			<SafeArea justify="center" align="center" gap={48}>
				<Animate in="rise" delay={2}>
					<WordRotator prefix="Get paid in " words={['USD', 'EUR', 'GBP']} size={116} delay={ROT.delay} hold={ROT.hold} transition={ROT.transition} align="center" />
				</Animate>
				<div style={{display: 'flex', gap: 28 * unit}}>
					<Stagger in="pop" each={6} delay={4}>
						{CHIPS.map(([sym, name], i) => (
							<Chip key={name} i={i} sym={sym} name={name} />
						))}
					</Stagger>
				</div>
				<Animate in="rise" delay={8} distance={24}>
					<MiniInvoice />
				</Animate>
			</SafeArea>
			</PushIn>
		</Ground>
	);
};
