import React from 'react';
import {useStage, useTheme} from '../kit';
import {INK} from './InvoiceCard';

// A phone photo of a paper receipt on a wooden table. The default is the receipt the demo's invoice is made from;
// `scan` (0 to 1) draws the reading line moving down it. All vendors and amounts are sample data.
export type ReceiptData = {vendor: string; lines: [string, string][]; total: string};
export const PAPER_AND_CO: ReceiptData = {vendor: 'PAPER & CO.', lines: [['Poster print', ''], ['A2 x 4', '$96.00'], ['Delivery', '$12.00']], total: '$108.00'};

export const ReceiptPhoto: React.FC<{width: number; scan?: number; receipt?: ReceiptData; style?: React.CSSProperties}> = ({width, scan, receipt = PAPER_AND_CO, style}) => {
	const t = useTheme();
	const {unit} = useStage();
	const k = (width / 380) * unit;
	const h = width * 1.12;
	const line = (a: string, b: string, bold = false) => (
		<div style={{display: 'flex', justifyContent: 'space-between', fontFamily: t.type.mono, fontWeight: bold ? 700 : 500, fontSize: 19 * k, color: INK, padding: `${4 * k}px 0`, borderTop: bold ? `${1.5 * k}px dashed #9CA3AF` : undefined}}>
			<span>{a}</span>
			<span>{b}</span>
		</div>
	);
	return (
		<div style={{position: 'relative', width: width * unit, height: h * unit, borderRadius: 14 * k, overflow: 'hidden', background: 'radial-gradient(120% 90% at 28% 18%, #6B5341 0%, #45352A 52%, #251C16 100%)', boxShadow: `0 ${18 * k}px ${44 * k}px rgba(0,0,0,0.5)`, ...style}}>
			<div style={{position: 'absolute', left: '13%', top: '9%', width: '74%', background: 'linear-gradient(170deg, #FFFFFF 0%, #F4F1EA 100%)', rotate: '-4deg', padding: `${22 * k}px ${22 * k}px ${26 * k}px`, boxShadow: `0 ${10 * k}px ${22 * k}px rgba(0,0,0,0.45)`}}>
				<div style={{fontFamily: t.type.mono, fontWeight: 700, fontSize: 22 * k, color: INK, textAlign: 'center', marginBottom: 12 * k}}>{receipt.vendor}</div>
				{receipt.lines.map(([a, b]) => (
					<React.Fragment key={a}>{line(a, b)}</React.Fragment>
				))}
				{line('TOTAL', receipt.total, true)}
			</div>
			{/* soft window light across the photo */}
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(115deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 45%)'}} />
			{scan !== undefined && scan > 0 && scan < 1 ? (
				<>
					<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: `${scan * 100}%`, background: 'linear-gradient(180deg, rgba(91,140,255,0) 55%, rgba(91,140,255,0.22) 100%)'}} />
					<div style={{position: 'absolute', left: 0, right: 0, top: `${scan * 100}%`, height: 3 * k, background: '#8FB0FF', boxShadow: `0 0 ${16 * k}px ${4 * k}px rgba(91,140,255,0.8)`}} />
				</>
			) : null}
		</div>
	);
};
