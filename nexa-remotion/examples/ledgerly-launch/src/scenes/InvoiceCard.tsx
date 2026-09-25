import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Stagger, pulse, useStage, useTheme} from '../kit';

// The product's invoice, drawn once and used in three scenes (all names and amounts are sample data). The status
// follows the story: Draft when it is made, Sent after the click, Paid on the end card.
export const INK = '#16181D';
export const SOFT = '#6B7280';

export type Status = 'Draft' | 'Sent' | 'Paid';
const TONE: Record<Status, {color: string; bg: string}> = {
	Draft: {color: '#4B5563', bg: '#EEF0F3'},
	Sent: {color: '#2446B8', bg: '#E6EDFF'},
	Paid: {color: '#0F7A52', bg: '#E3F7EE'},
};

export const Line: React.FC<{left: string; right: string; bold?: boolean; size?: number}> = ({left, right, bold, size = 26}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{display: 'flex', justifyContent: 'space-between', gap: 24 * unit, fontFamily: t.type.body, fontSize: size * unit, fontWeight: bold ? 700 : 500, color: INK, padding: `${7 * unit}px 0`, borderTop: bold ? `${2 * unit}px solid #E5E7EB` : undefined, fontVariantNumeric: 'tabular-nums'}}>
			<span>{left}</span>
			<span>{right}</span>
		</div>
	);
};

// exactly the receipt's lines: the invoice is made from it, so a viewer can check one against the other
const ROWS: [string, string][] = [
	['Poster print A2 x 4', '$96.00'],
	['Delivery', '$12.00'],
];

export const InvoiceCard: React.FC<{
	statuses: {at: number; status: Status}[]; // the status from each frame on (the first is the start)
	rowsAt?: number; // the lines rise in from this frame (default: there from the start)
	scale?: number;
}> = ({statuses, rowsAt, scale = 1}) => {
	const t = useTheme();
	const frame = useCurrentFrame();
	const {unit} = useStage();
	const u = unit * scale;
	const current = [...statuses].reverse().find((s) => frame >= s.at) ?? statuses[0];
	const tone = TONE[current.status];
	// the status pill swells once when it changes
	const swell = statuses.slice(1).reduce((m, s) => Math.max(m, pulse(frame, s.at, 10)), 0);
	const lines = [
		...ROWS.map(([a, b]) => <Line key={a} left={a} right={b} />),
		<Line key="total" left={current.status === 'Paid' ? 'Total paid' : 'Total due'} right="$108.00" bold />,
	];
	return (
		<div style={{background: '#FFFFFF', borderRadius: 18 * u, padding: `${28 * u}px ${32 * u}px`, boxShadow: `0 ${16 * u}px ${40 * u}px rgba(0,0,0,0.35)`}}>
			<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20 * u}}>
				<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: 38 * u, color: INK}}>Invoice #1042</div>
				<div style={{fontFamily: t.type.body, fontWeight: 700, fontSize: 20 * u, color: tone.color, background: tone.bg, borderRadius: 999, padding: `${5 * u}px ${16 * u}px`, scale: `${1 + 0.16 * swell}`}}>{current.status}</div>
			</div>
			<div style={{fontFamily: t.type.body, fontSize: 24 * u, color: SOFT, margin: `${6 * u}px 0 ${14 * u}px`}}>Bill to Northwind Studio</div>
			<div style={{scale: `${scale}`, transformOrigin: '0 0', width: `${100 / scale}%`}}>
				{rowsAt === undefined ? (
					lines
				) : (
					<Stagger in="rise" each={4} delay={rowsAt} distance={12}>
						{lines}
					</Stagger>
				)}
			</div>
		</div>
	);
};
