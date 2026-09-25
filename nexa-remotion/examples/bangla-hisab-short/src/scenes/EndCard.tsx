import React from 'react';
import {Animate, KineticTitle, PushIn, SafeArea, Stagger, useStage, useTheme} from '../kit';
import {CUE, CUT} from '../cues';
import {NUM, RULES} from './Phone';

// The close: the call to action as the voice says it, the three rules in the voice's words, then where to keep the
// record, read during the music tail. A slow push keeps the held frame alive.
export const EndCard: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const voice = CUE.ajker - CUT.end;
	return (
		// anchored on the column's centre (the safe area's middle): about the frame centre the title rose past the safe top
		<PushIn amount={0.03} origin="50% 39.5%">
			<SafeArea justify="center" align="center" gap={20}>
				<KineticTitle text="আজই শুরু করুন" size={128} align="center" emphasis="আজই" emphasisColor={t.colors.highlight} />
				<Animate in="rise" delay={voice - 2}>
					<div style={{fontFamily: t.type.body, fontWeight: 500, fontSize: 54 * unit, color: t.colors.text, opacity: 0.88, textAlign: 'center'}}>আজকের বিক্রি দিয়েই</div>
				</Animate>
				<div style={{display: 'flex', flexDirection: 'column', gap: 16 * unit, marginTop: 16 * unit}}>
					<Stagger in="rise" each={6} delay={voice + 20} distance={20}>
						{RULES.map((r, i) => (
							<div key={r} style={{display: 'flex', alignItems: 'center', gap: 22 * unit, background: 'rgba(255, 255, 255, 0.07)', border: `${2 * unit}px solid rgba(255, 255, 255, 0.12)`, borderRadius: 999, padding: `${14 * unit}px ${34 * unit}px ${14 * unit}px ${14 * unit}px`}}>
								<div style={{flexShrink: 0, width: 62 * unit, height: 62 * unit, borderRadius: 31 * unit, background: t.colors.highlight, color: '#1D2B24', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: 800, fontSize: 38 * unit}}>{NUM[i]}</div>
								<div style={{fontFamily: t.type.body, fontWeight: 600, fontSize: 40 * unit, color: t.colors.text}}>{r}</div>
							</div>
						))}
					</Stagger>
				</div>
				{/* the "how": no brand, any notes or ledger app will do */}
				<Animate in="rise" delay={voice + 36} distance={16}>
					<div style={{fontFamily: t.type.body, fontWeight: 500, fontSize: 42 * unit, lineHeight: 1.4, color: t.colors.text, opacity: 0.82, textAlign: 'center', maxWidth: 720 * unit, textWrap: 'balance'}}>ফোনের নোটে বা যেকোনো হিসাবের অ্যাপে রাখা যায়</div>
				</Animate>
			</SafeArea>
		</PushIn>
	);
};
