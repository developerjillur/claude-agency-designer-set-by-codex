// Default content drawn with the 2D canvas in the theme's colours and fonts: an app screen for Phone3D, the two
// faces of a payment card for Card3D and stat cards for FloatingCards. Real-looking copy, never placeholder text.
import type {Theme} from '../core';
import {roundRectPath} from './textures';
import {mix, withAlpha} from './util';

const font = (weight: number, px: number, stack: string) => `${weight} ${Math.round(px)}px ${stack}`;

/** The font shorthands a drawing uses, for useCanvasTexture's `fonts` (so drawing waits for them). */
export const drawingFonts = (t: Theme): string[] => [
	font(t.weights.display, 60, t.type.display),
	font(t.weights.body, 30, t.type.body),
	font(t.weights.strong, 30, t.type.body),
	font(500, 30, t.type.mono),
];

// ---------------------------------------------------------------- phone app screen

export const APP_SCREEN_TEXT = '9:41 Good morning Your week Revenue $48,210 +12.4% vs last week Orders 1,284 Visitors 32.9k New order #4821 Payout sent Refund processed $129.00 $2,400.00 $36.50 2 min ago 1 h ago Yesterday';

export const drawAppScreen = (ctx: CanvasRenderingContext2D, W: number, H: number, t: Theme): void => {
	const c = t.colors;
	const u = W / 1000; // drawn on a 1000 px wide grid
	const ink = c.text;
	const soft = c.muted;
	const card = t.dark ? mix(c.bg, c.surface, 1) : '#ffffff';
	ctx.fillStyle = t.dark ? c.bg : mix(c.bg, '#ffffff', 0.35);
	ctx.fillRect(0, 0, W, H);
	ctx.textBaseline = 'alphabetic';

	// status bar (the island sits in the middle)
	ctx.fillStyle = ink;
	ctx.font = font(t.weights.strong, 44 * u, t.type.body);
	ctx.fillText('9:41', 84 * u, 118 * u);
	for (let i = 0; i < 4; i++) {
		const bh = (14 + i * 7) * u;
		roundRectPath(ctx, W - 250 * u + i * 20 * u, 116 * u - bh, 12 * u, bh, 3 * u);
		ctx.fill();
	}
	roundRectPath(ctx, W - 150 * u, 84 * u, 74 * u, 36 * u, 10 * u);
	ctx.lineWidth = 3 * u;
	ctx.strokeStyle = withAlpha(ink, 0.55);
	ctx.stroke();
	roundRectPath(ctx, W - 145 * u, 89 * u, 52 * u, 26 * u, 6 * u);
	ctx.fill();

	// greeting
	ctx.fillStyle = soft;
	ctx.font = font(t.weights.body, 38 * u, t.type.body);
	ctx.fillText('Good morning', 84 * u, 290 * u);
	ctx.fillStyle = ink;
	ctx.font = font(t.weights.display, 92 * u, t.type.display);
	ctx.fillText('Your week', 80 * u, 392 * u);

	// hero card
	const hx = 60 * u;
	const hy = 450 * u;
	const hw = W - 120 * u;
	const hh = 560 * u;
	const g = ctx.createLinearGradient(hx, hy, hx + hw, hy + hh);
	g.addColorStop(0, c.accent);
	g.addColorStop(1, mix(c.accent, c.accent2, 0.55));
	roundRectPath(ctx, hx, hy, hw, hh, 48 * u);
	ctx.fillStyle = g;
	ctx.fill();
	ctx.fillStyle = withAlpha(c.onAccent, 0.8);
	ctx.font = font(t.weights.body, 38 * u, t.type.body);
	ctx.fillText('Revenue', hx + 56 * u, hy + 96 * u);
	ctx.fillStyle = c.onAccent;
	ctx.font = font(t.weights.display, 118 * u, t.type.display);
	ctx.fillText('$48,210', hx + 50 * u, hy + 232 * u);
	ctx.font = font(t.weights.strong, 36 * u, t.type.body);
	ctx.fillText('+12.4% vs last week', hx + 56 * u, hy + 300 * u);
	const bars = [0.42, 0.58, 0.5, 0.72, 0.64, 0.86, 1];
	const bw = 62 * u;
	bars.forEach((b, i) => {
		const bx = hx + 56 * u + i * (bw + 50 * u);
		const bhh = 170 * u * b;
		roundRectPath(ctx, bx, hy + hh - 52 * u - bhh, bw, bhh, 14 * u);
		ctx.fillStyle = withAlpha(c.onAccent, i === bars.length - 1 ? 0.95 : 0.4);
		ctx.fill();
	});

	// two small cards
	const sy = hy + hh + 40 * u;
	const sw = (hw - 36 * u) / 2;
	const stat = (x: number, label: string, value: string) => {
		roundRectPath(ctx, x, sy, sw, 250 * u, 40 * u);
		ctx.fillStyle = card;
		ctx.fill();
		ctx.fillStyle = soft;
		ctx.font = font(t.weights.body, 34 * u, t.type.body);
		ctx.fillText(label, x + 44 * u, sy + 84 * u);
		ctx.fillStyle = ink;
		ctx.font = font(t.weights.display, 76 * u, t.type.display);
		ctx.fillText(value, x + 40 * u, sy + 190 * u);
	};
	stat(hx, 'Orders', '1,284');
	stat(hx + sw + 36 * u, 'Visitors', '32.9k');

	// activity list
	const rows: [string, string, string][] = [
		['New order #4821', '2 min ago', '$129.00'],
		['Payout sent', '1 h ago', '$2,400.00'],
		['Refund processed', 'Yesterday', '$36.50'],
	];
	const ly = sy + 300 * u;
	rows.forEach(([title, when, amount], i) => {
		const y = ly + i * 170 * u;
		roundRectPath(ctx, hx, y, hw, 144 * u, 36 * u);
		ctx.fillStyle = card;
		ctx.fill();
		ctx.beginPath();
		ctx.arc(hx + 76 * u, y + 72 * u, 34 * u, 0, Math.PI * 2);
		ctx.fillStyle = withAlpha(i === 2 ? c.negative : c.accent, 0.16);
		ctx.fill();
		ctx.beginPath();
		ctx.arc(hx + 76 * u, y + 72 * u, 12 * u, 0, Math.PI * 2);
		ctx.fillStyle = i === 2 ? c.negative : c.accent;
		ctx.fill();
		ctx.fillStyle = ink;
		ctx.font = font(t.weights.strong, 36 * u, t.type.body);
		ctx.fillText(title, hx + 140 * u, y + 64 * u);
		ctx.fillStyle = soft;
		ctx.font = font(t.weights.body, 30 * u, t.type.body);
		ctx.fillText(when, hx + 140 * u, y + 108 * u);
		ctx.fillStyle = ink;
		ctx.font = font(t.weights.strong, 36 * u, t.type.body);
		ctx.textAlign = 'right';
		ctx.fillText(amount, hx + hw - 44 * u, y + 84 * u);
		ctx.textAlign = 'left';
	});

	// tab bar and home indicator
	const ty = H - 190 * u;
	ctx.fillStyle = withAlpha(t.dark ? '#000000' : '#ffffff', t.dark ? 0.35 : 0.9);
	ctx.fillRect(0, ty, W, H - ty);
	for (let i = 0; i < 4; i++) {
		const x = W * (0.16 + i * 0.227);
		roundRectPath(ctx, x - 26 * u, ty + 38 * u, 52 * u, 52 * u, 14 * u);
		ctx.fillStyle = i === 0 ? c.accent : withAlpha(ink, 0.28);
		ctx.fill();
	}
	roundRectPath(ctx, W / 2 - 150 * u, H - 44 * u, 300 * u, 12 * u, 6 * u);
	ctx.fillStyle = withAlpha(ink, 0.85);
	ctx.fill();
};

// ---------------------------------------------------------------- payment card

export type CardDesign = {brand?: string; number?: string; name?: string; expiry?: string; color?: string; color2?: string};

export const cardText = (d: CardDesign): string =>
	[d.brand ?? 'nexa', d.number ?? '4829 1937 5520 0417', d.name ?? 'SAM CARTER', d.expiry ?? '09/29', 'VALID THRU Customer service 24/7'].join(' ');

export const drawCardFront = (ctx: CanvasRenderingContext2D, W: number, H: number, t: Theme, d: CardDesign): void => {
	const c = t.colors;
	const u = W / 1000;
	// one hue, light to deep, reads premium; pass color2 for a two-colour card
	const a = d.color ?? c.accent;
	const b = d.color2 ?? mix(a, '#000000', 0.55);
	const g = ctx.createLinearGradient(0, 0, W, H);
	g.addColorStop(0, a);
	g.addColorStop(1, b);
	ctx.fillStyle = g;
	ctx.fillRect(0, 0, W, H);
	// soft rings for texture
	ctx.lineWidth = 36 * u;
	for (let i = 0; i < 4; i++) {
		ctx.beginPath();
		ctx.arc(W * 0.92, H * 0.1, (190 + i * 120) * u, 0, Math.PI * 2);
		ctx.strokeStyle = withAlpha('#ffffff', 0.07 - i * 0.012);
		ctx.stroke();
	}
	const on = '#ffffff';
	ctx.fillStyle = on;
	ctx.font = font(t.weights.display, 74 * u, t.type.display);
	ctx.fillText(d.brand ?? 'nexa', 70 * u, 130 * u);
	// chip
	const cx = 76 * u;
	const cy = 230 * u;
	const cg = ctx.createLinearGradient(cx, cy, cx + 130 * u, cy + 100 * u);
	cg.addColorStop(0, '#f4dc9a');
	cg.addColorStop(1, '#c9a24e');
	roundRectPath(ctx, cx, cy, 130 * u, 100 * u, 18 * u);
	ctx.fillStyle = cg;
	ctx.fill();
	ctx.strokeStyle = withAlpha('#7a5b1c', 0.55);
	ctx.lineWidth = 4 * u;
	for (const f of [0.33, 0.66]) {
		ctx.beginPath();
		ctx.moveTo(cx, cy + 100 * u * f);
		ctx.lineTo(cx + 130 * u, cy + 100 * u * f);
		ctx.stroke();
	}
	ctx.beginPath();
	ctx.moveTo(cx + 65 * u, cy);
	ctx.lineTo(cx + 65 * u, cy + 100 * u);
	ctx.stroke();
	// contactless
	ctx.strokeStyle = withAlpha(on, 0.9);
	ctx.lineWidth = 9 * u;
	ctx.lineCap = 'round';
	for (let i = 0; i < 3; i++) {
		ctx.beginPath();
		ctx.arc(250 * u, 280 * u, (26 + i * 22) * u, -0.9, 0.9);
		ctx.stroke();
	}
	ctx.fillStyle = on;
	ctx.font = font(500, 60 * u, t.type.mono);
	ctx.fillText(d.number ?? '4829 1937 5520 0417', 72 * u, 470 * u);
	ctx.font = font(t.weights.body, 26 * u, t.type.body);
	ctx.fillStyle = withAlpha(on, 0.75);
	ctx.fillText('VALID THRU', 560 * u, 540 * u);
	ctx.fillStyle = on;
	ctx.font = font(t.weights.strong, 40 * u, t.type.body);
	ctx.fillText(d.name ?? 'SAM CARTER', 72 * u, 572 * u);
	ctx.font = font(500, 40 * u, t.type.mono);
	ctx.fillText(d.expiry ?? '09/29', 560 * u, 582 * u);
	// network mark
	ctx.globalAlpha = 0.92;
	ctx.fillStyle = mix(a, '#ffffff', 0.55);
	ctx.beginPath();
	ctx.arc(840 * u, 540 * u, 46 * u, 0, Math.PI * 2);
	ctx.fill();
	ctx.fillStyle = mix(b, '#ffffff', 0.35);
	ctx.beginPath();
	ctx.arc(900 * u, 540 * u, 46 * u, 0, Math.PI * 2);
	ctx.fill();
	ctx.globalAlpha = 1;
};

export const drawCardBack = (ctx: CanvasRenderingContext2D, W: number, H: number, t: Theme, d: CardDesign): void => {
	const c = t.colors;
	const u = W / 1000;
	const a = d.color ?? c.accent;
	const b = d.color2 ?? mix(a, '#000000', 0.55);
	const g = ctx.createLinearGradient(W, 0, 0, H);
	g.addColorStop(0, mix(a, '#000000', 0.2));
	g.addColorStop(1, mix(b, '#000000', 0.15));
	ctx.fillStyle = g;
	ctx.fillRect(0, 0, W, H);
	ctx.fillStyle = '#16171a';
	ctx.fillRect(0, 70 * u, W, 120 * u);
	roundRectPath(ctx, 70 * u, 250 * u, 600 * u, 90 * u, 10 * u);
	ctx.fillStyle = '#f2f2ef';
	ctx.fill();
	ctx.fillStyle = '#1b1c1f';
	ctx.font = font(500, 40 * u, t.type.mono);
	ctx.fillText('417', 700 * u, 312 * u);
	ctx.fillStyle = withAlpha('#ffffff', 0.85);
	ctx.font = font(t.weights.body, 28 * u, t.type.body);
	ctx.fillText('Customer service 24/7', 72 * u, 470 * u);
	ctx.font = font(t.weights.display, 54 * u, t.type.display);
	ctx.fillText(d.brand ?? 'nexa', 72 * u, 560 * u);
};

// ---------------------------------------------------------------- stat card (FloatingCards)

export type StatCardContent = {title?: string; value?: string; caption?: string; chart?: number[]; accent?: string; up?: boolean};

export const statCardText = (s: StatCardContent): string => [s.title, s.value, s.caption].filter(Boolean).join(' ');

export const drawStatCard = (ctx: CanvasRenderingContext2D, W: number, H: number, t: Theme, s: StatCardContent, fill: string): void => {
	const c = t.colors;
	const u = W / 840; // drawn on an 840 px wide grid (a 420 px card at 2x)
	const accent = s.accent ?? c.accent;
	ctx.fillStyle = fill;
	ctx.fillRect(0, 0, W, H);
	const onFill = (a: number) => withAlpha(mix(fill, c.text, 1), a);
	ctx.textBaseline = 'alphabetic';
	if (s.title) {
		ctx.fillStyle = onFill(0.62);
		ctx.font = font(t.weights.strong, 36 * u, t.type.body);
		ctx.fillText(s.title, 56 * u, 100 * u);
	}
	if (s.value) {
		ctx.fillStyle = onFill(1);
		ctx.font = font(t.weights.display, 104 * u, t.type.display);
		ctx.fillText(s.value, 50 * u, 224 * u);
	}
	if (s.caption) {
		const up = s.up ?? !s.caption.trim().startsWith('-');
		ctx.fillStyle = up ? c.positive : c.negative;
		ctx.font = font(t.weights.strong, 34 * u, t.type.body);
		ctx.fillText(s.caption, 56 * u, 288 * u);
	}
	const pts = s.chart ?? [];
	if (pts.length > 1) {
		const x0 = 56 * u;
		const x1 = W - 56 * u;
		const y0 = H - 60 * u;
		const y1 = H - 210 * u;
		const lo = Math.min(...pts);
		const hi = Math.max(...pts);
		const px = (i: number) => x0 + ((x1 - x0) * i) / (pts.length - 1);
		const py = (v: number) => y0 + (y1 - y0) * (hi > lo ? (v - lo) / (hi - lo) : 0.5);
		const area = ctx.createLinearGradient(0, y1, 0, y0);
		area.addColorStop(0, withAlpha(accent, 0.28));
		area.addColorStop(1, withAlpha(accent, 0));
		ctx.beginPath();
		ctx.moveTo(px(0), y0);
		pts.forEach((v, i) => ctx.lineTo(px(i), py(v)));
		ctx.lineTo(px(pts.length - 1), y0);
		ctx.closePath();
		ctx.fillStyle = area;
		ctx.fill();
		ctx.beginPath();
		pts.forEach((v, i) => (i ? ctx.lineTo(px(i), py(v)) : ctx.moveTo(px(i), py(v))));
		ctx.strokeStyle = accent;
		ctx.lineWidth = 7 * u;
		ctx.lineJoin = 'round';
		ctx.lineCap = 'round';
		ctx.stroke();
		ctx.beginPath();
		ctx.arc(px(pts.length - 1), py(pts[pts.length - 1]), 12 * u, 0, Math.PI * 2);
		ctx.fillStyle = accent;
		ctx.fill();
	}
};
