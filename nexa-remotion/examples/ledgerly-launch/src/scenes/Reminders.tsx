import React from 'react';
import {Ground, KineticTitle, NotificationStack, PushIn, useStage} from '../kit';

// Feature 2: reminders that send themselves, then the payment lands.
export const Reminders: React.FC = () => {
	const {unit, safe, width} = useStage();
	return (
		<Ground kind="lit" light={[0.75, -0.2]} drift={0.5}>
			<div style={{position: 'absolute', left: safe.x + 8 * unit, top: 330 * unit, width: 700 * unit}}>
				<KineticTitle text={'Reminders go out\non their own.'} size={78} by="line" delay={4} />
			</div>
			{/* desktop notifications are drawn life-size; scaled up so they read in a video, and pushed in slowly. The times
			    say the reminders went out over days, on their own */}
			{/* each card slides in from the right: clipped 14 px inside the safe area (OCR boxes run a few px past the ink),
			    so no letter is ever outside it; the push is anchored on that edge too */}
			<div style={{position: 'absolute', inset: 0, clipPath: `inset(${safe.y}px ${width - safe.x - safe.w + 14 * unit}px ${safe.y}px ${safe.x}px)`}}>
			<PushIn amount={0.06} origin="95% 30%">
			<div style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', scale: '1.42', transformOrigin: `${1824 * unit}px ${300 * unit}px`}}>
			<NotificationStack
				variant="desktop"
				place="top-right"
				area="safe"
				inset={24}
				gap={18}
				items={[
					{app: 'Ledgerly', title: 'Reminder sent', body: 'Invoice #1039 to Lumen Labs, 3 days late', icon: 'bell', time: '2d ago', at: 25, width: 660},
					{app: 'Ledgerly', title: 'Reminder sent', body: 'Invoice #1041 to Harbor & Co, due tomorrow', icon: 'bell', time: 'Yesterday', at: 76, width: 660},
					{app: 'Ledgerly', title: 'Paid', body: 'Invoice #1039: $2,400 from Lumen Labs', icon: 'check', time: 'now', at: 124, width: 660},
				]}
				style={{top: 300 * unit}}
			/>
			</div>
			</PushIn>
			</div>
		</Ground>
	);
};
