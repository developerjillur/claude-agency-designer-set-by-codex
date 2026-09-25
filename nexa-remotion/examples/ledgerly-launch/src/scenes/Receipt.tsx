import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Animate, BrowserWindow, Cursor, Ground, KineticTitle, Notification, PushIn, UiButton, UiIcon, cursorPose, cursorTimeline, curves, ramp, useStage, useTheme, type CursorKey} from '../kit';
import {LEDGERLY_TAB} from '../brand';
import {InvoiceCard} from './InvoiceCard';
import {ReceiptPhoto} from './Photo';

// Feature 1, the promise shown honestly: a receipt photo is dragged from the desktop into the app, the app reads it
// and drafts the invoice by itself, and one click sends it. Everything here is in frame px at 1080 (the cursor
// travels from the desktop into the browser, so it lives outside the window).
const WIN = {x: 720, y: 190, w: 1100, h: 700};
const PAGE = {x: WIN.x, y: WIN.y + 98}; // the page under the tab bar and the address bar
const ZONE = {x: 48, y: 56, w: 420, h: 400}; // page px
const PHOTO = {x: 93, y: 71, w: 330}; // the photo inside the drop zone, page px
const FILE = {x: 290, y: 760, w: 120}; // the photo's file on the desktop
const SEND = {x: 520, y: 402, w: 300, h: 72}; // page px
const KEYS: CursorKey[] = [
	{x: FILE.x + 60, y: FILE.y + 52, at: 26, drag: true},
	{x: PAGE.x + ZONE.x + ZONE.w / 2 + 8, y: PAGE.y + ZONE.y + ZONE.h / 2 + 4, at: 58},
	// on the right of the button: the pointer never covers its label
	{x: PAGE.x + SEND.x + SEND.w - 34, y: PAGE.y + SEND.y + SEND.h / 2 + 6, at: 146, click: true},
];

export const Receipt: React.FC = () => {
	const t = useTheme();
	const {unit, safe, fps} = useStage();
	const frame = useCurrentFrame();
	const tl = cursorTimeline(KEYS, fps);
	const grab = tl.pressOf(0) ?? 30;
	const drop = tl.releases[0] ?? 60;
	const send = tl.pressOf(2) ?? 150;
	const pose = cursorPose(tl, frame, fps);
	const dragging = frame >= grab && frame < drop;
	const inZone = (px: number, py: number) => px >= PAGE.x + ZONE.x && px <= PAGE.x + ZONE.x + ZONE.w && py >= PAGE.y + ZONE.y && py <= PAGE.y + ZONE.y + ZONE.h;
	const hover = dragging && inZone(pose.x, pose.y) ? 1 : 0;
	const dropped = frame >= drop;
	const land = ramp(frame, drop, 8, curves.out);
	const scan = ramp(frame, drop + 10, 30, curves.inOut);
	// where the photo was let go, as a transform origin inside the photo box
	const originX = KEYS[1].x - PAGE.x - PHOTO.x;
	const originY = KEYS[1].y - PAGE.y - PHOTO.y;
	return (
		<Ground kind="lit">
			<div style={{position: 'absolute', left: safe.x + 8 * unit, top: 330 * unit, width: 600 * unit}}>
				<KineticTitle text={'Drop in a receipt.\nGet an invoice.'} size={70} maxWidth={580} by="line" delay={4} />
			</div>
			{/* anchored on the window's left edge: it grows away from the headline, never into it */}
			<PushIn amount={0.04} origin="37.5% 50%">
				<div style={{position: 'absolute', left: WIN.x * unit, top: WIN.y * unit}}>
					<BrowserWindow width={WIN.w} height={WIN.h} url="app.ledgerly.example/new" mode="dark" tabs={[LEDGERLY_TAB, 'Inbox']}>
						<div style={{position: 'absolute', inset: 0, background: '#14161B'}}>
							<div style={{position: 'absolute', left: ZONE.x * unit, top: 18 * unit, fontFamily: t.type.body, fontSize: 20 * unit, fontWeight: 700, color: '#8B93A3', letterSpacing: '0.08em', textTransform: 'uppercase'}}>Receipt photo</div>
							<div style={{position: 'absolute', left: ZONE.x * unit, top: ZONE.y * unit, width: ZONE.w * unit, height: ZONE.h * unit, boxSizing: 'border-box', borderRadius: 18 * unit, border: `${2.5 * unit}px ${dropped ? 'solid' : 'dashed'} ${hover ? t.colors.accent : 'rgba(255,255,255,0.2)'}`, background: hover ? 'rgba(91,140,255,0.10)' : 'rgba(255,255,255,0.03)'}}>
								{dropped ? null : (
									<div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14 * unit}}>
										<UiIcon name="download" size={46} color={hover ? t.colors.accent : '#8B93A3'} style={{rotate: '180deg'}} />
										<div style={{fontFamily: t.type.body, fontSize: 26 * unit, fontWeight: 600, color: '#C9CED8'}}>Drop a receipt photo</div>
									</div>
								)}
							</div>
							{dropped ? (
								<div style={{position: 'absolute', left: PHOTO.x * unit, top: PHOTO.y * unit, scale: `${0.36 + 0.64 * land}`, transformOrigin: `${originX * unit}px ${originY * unit}px`}}>
									<ReceiptPhoto width={PHOTO.w} scan={scan} />
								</div>
							) : null}
							<div style={{position: 'absolute', left: SEND.x * unit, top: 36 * unit, width: 540 * unit}}>
								<Animate in="pop" delay={drop + 36} origin="0% 0%">
									<InvoiceCard
										statuses={[
											{at: 0, status: 'Draft'},
											{at: send, status: 'Sent'},
										]}
										rowsAt={drop + 40}
									/>
								</Animate>
							</div>
							<div style={{position: 'absolute', left: SEND.x * unit, top: SEND.y * unit}}>
								<Animate in="rise" delay={drop + 56} distance={14}>
									<UiButton label="Send invoice" icon="send" size="lg" width={SEND.w} pressAt={send} doneLabel="Sent" doneIcon="check" mode="dark" />
								</Animate>
							</div>
							{/* the confirmation sits under the photo, clear of the buttons */}
							<div style={{position: 'absolute', left: ZONE.x * unit, top: 470 * unit, width: ZONE.w * unit, height: 90 * unit}}>
								<Notification variant="pill" title="Sent to Northwind Studio" delay={send + 8} area="parent" place="top" inset={0} mode="dark" />
							</div>
						</div>
					</BrowserWindow>
				</div>
				{/* the photo's file on the desktop; it rides under the pointer while dragged */}
				{dropped ? null : (
					<div
						style={{
							position: 'absolute',
							left: (dragging ? pose.x - 60 : FILE.x) * unit,
							top: (dragging ? pose.y - 52 : FILE.y) * unit,
							display: 'flex',
							flexDirection: 'column',
							alignItems: 'center',
							gap: 8 * unit,
							scale: dragging ? '1.06' : '1',
							opacity: dragging ? 0.94 : 1,
						}}
					>
						<ReceiptPhoto width={FILE.w} />
						{dragging ? null : <div style={{fontFamily: t.type.body, fontSize: 20 * unit, fontWeight: 600, color: t.colors.text, background: 'rgba(0,0,0,0.35)', borderRadius: 6 * unit, padding: `${2 * unit}px ${8 * unit}px`}}>receipt.jpg</div>}
					</div>
				)}
				<Cursor keys={KEYS} />
			</PushIn>
		</Ground>
	);
};
