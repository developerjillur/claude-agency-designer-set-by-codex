// Patterns laid over a ground: grid lines, dots, crosses, diagonal stripes, ruled lines, a checker and halftone
// dots. Lines and dots are CSS gradients (cheap, sharp, scaled by unit); crosses and halftone are drawn on a canvas.
// All of them can fade towards a side or the middle, and drift seamlessly.
import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp, useStage, useTheme} from '../core';
import {withAlpha} from './color';

export type PatternKind = 'grid' | 'dots' | 'cross' | 'stripes' | 'rules' | 'checker' | 'halftone';
export type PatternFade = 'none' | 'center' | 'edges' | 'top' | 'bottom' | 'left' | 'right';

export type PatternProps = {
	kind?: PatternKind;
	size?: number; // cell or period, px at 1080 (defaults: grid 80, dots 32, cross 96, stripes 28, rules 56, checker 64, halftone 26)
	weight?: number; // line width or dot diameter, px at 1080 (halftone: the largest dot as a share of the cell, 0 to 1.3)
	color?: string; // default: the theme's text at a low alpha, chosen per kind
	opacity?: number; // 0 to 1 (default 1)
	angle?: number; // stripes and halftone: degrees (default 45 for stripes, 20 for halftone)
	fade?: PatternFade; // where the pattern is strongest (halftone: where the dots are biggest)
	drift?: [number, number]; // px a second at 1080: a seamless slow scroll (default still)
	style?: React.CSSProperties;
};

const DEFAULT_SIZE: Record<PatternKind, number> = {grid: 80, dots: 32, cross: 96, stripes: 28, rules: 56, checker: 64, halftone: 26};
const DEFAULT_WEIGHT: Record<PatternKind, number> = {grid: 1.5, dots: 5, cross: 2, stripes: 10, rules: 1.5, checker: 0, halftone: 0.9};
const DEFAULT_ALPHA: Record<PatternKind, number> = {grid: 0.09, dots: 0.16, cross: 0.28, stripes: 0.06, rules: 0.12, checker: 0.045, halftone: 0.5};

const maskFor = (fade: PatternFade): string | undefined => {
	switch (fade) {
		case 'center':
			return 'radial-gradient(ellipse 75% 80% at 50% 50%, #000 0%, #000 25%, rgba(0,0,0,0.5) 55%, transparent 100%)';
		case 'edges':
			return 'radial-gradient(ellipse 80% 85% at 50% 50%, transparent 20%, rgba(0,0,0,0.5) 60%, #000 100%)';
		case 'top':
			return 'linear-gradient(180deg, #000 0%, rgba(0,0,0,0.6) 35%, transparent 80%)';
		case 'bottom':
			return 'linear-gradient(0deg, #000 0%, rgba(0,0,0,0.6) 35%, transparent 80%)';
		case 'left':
			return 'linear-gradient(90deg, #000 0%, rgba(0,0,0,0.6) 35%, transparent 80%)';
		case 'right':
			return 'linear-gradient(270deg, #000 0%, rgba(0,0,0,0.6) 35%, transparent 80%)';
		default:
			return undefined;
	}
};

// 0 to 1: how strong the pattern is at (u, v) for a fade, the same shapes as the masks (for halftone dot sizes)
const strengthAt = (fade: PatternFade, u: number, v: number): number => {
	const lin = (x: number) => clamp(1 - x / 0.85, 0, 1);
	switch (fade) {
		case 'center': {
			const d = Math.hypot((u - 0.5) / 0.75, (v - 0.5) / 0.8) * 2;
			return clamp(1.15 - d, 0, 1);
		}
		case 'edges': {
			const d = Math.hypot((u - 0.5) / 0.8, (v - 0.5) / 0.85) * 2;
			return clamp((d - 0.25) / 0.75, 0, 1);
		}
		case 'top':
			return lin(v);
		case 'bottom':
			return lin(1 - v);
		case 'left':
			return lin(u);
		case 'right':
			return lin(1 - u);
		default:
			return 1;
	}
};

/** A repeating pattern over the ground (put it between the ground and the content). */
export const Pattern: React.FC<PatternProps> = ({kind = 'grid', size, weight, color, opacity = 1, angle, fade = 'none', drift, style}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {width, height, fps, unit} = useStage();
	const ref = useRef<HTMLCanvasElement>(null);
	const cell = Math.max(2, (size ?? DEFAULT_SIZE[kind]) * unit);
	const w = (weight ?? DEFAULT_WEIGHT[kind]) * (kind === 'halftone' ? 1 : unit);
	const ink = color ?? withAlpha(t.colors.text, Math.min(0.6, DEFAULT_ALPHA[kind] * (t.dark ? 1.5 : 1)));
	const sec = frame / fps;
	const dx = (drift?.[0] ?? 0) * unit * sec;
	const dy = (drift?.[1] ?? 0) * unit * sec;
	// centre the cells on the frame, so a grid is symmetric
	const ox = (width % cell) / 2 + dx;
	const oy = (height % cell) / 2 + dy;
	const onCanvas = kind === 'cross' || kind === 'halftone';
	const ang = angle ?? (kind === 'stripes' ? 45 : kind === 'halftone' ? 20 : 0);
	const cw = Math.max(1, Math.ceil(width));
	const ch = Math.max(1, Math.ceil(height));

	useLayoutEffect(() => {
		if (!onCanvas) {
			return;
		}
		const canvas = ref.current;
		const ctx = canvas?.getContext('2d');
		if (!canvas || !ctx) {
			return;
		}
		ctx.clearRect(0, 0, cw, ch);
		ctx.fillStyle = ink;
		ctx.strokeStyle = ink;
		if (kind === 'cross') {
			const arm = cell * 0.09;
			ctx.lineWidth = Math.max(0.5, w);
			ctx.lineCap = 'butt';
			ctx.beginPath();
			const x0 = (((ox % cell) + cell) % cell) - cell;
			const y0 = (((oy % cell) + cell) % cell) - cell;
			for (let x = x0; x <= cw + cell; x += cell) {
				for (let y = y0; y <= ch + cell; y += cell) {
					ctx.moveTo(x - arm, y);
					ctx.lineTo(x + arm, y);
					ctx.moveTo(x, y - arm);
					ctx.lineTo(x, y + arm);
				}
			}
			ctx.stroke();
			return;
		}
		// halftone: a rotated grid of dots whose size follows the fade
		const rad = (ang * Math.PI) / 180;
		const cos = Math.cos(rad);
		const sin = Math.sin(rad);
		const span = Math.hypot(cw, ch) / 2 + cell;
		const n = Math.ceil(span / cell);
		const cx = cw / 2 + (dx % cell);
		const cy = ch / 2 + (dy % cell);
		const maxR = (cell / 2) * clamp(w, 0, 1.3);
		ctx.beginPath();
		for (let i = -n; i <= n; i++) {
			for (let j = -n; j <= n; j++) {
				const x = cx + (i * cos - j * sin) * cell;
				const y = cy + (i * sin + j * cos) * cell;
				if (x < -cell || y < -cell || x > cw + cell || y > ch + cell) {
					continue;
				}
				const s = strengthAt(fade, x / cw, y / ch);
				const r = maxR * s;
				if (r < 0.35) {
					continue;
				}
				ctx.moveTo(x + r, y);
				ctx.arc(x, y, r, 0, Math.PI * 2);
			}
		}
		ctx.fill();
	}, [onCanvas, kind, cell, w, ink, ox, oy, dx, dy, ang, fade, cw, ch]);

	const mask = kind === 'halftone' ? undefined : maskFor(fade);
	const common: React.CSSProperties = {
		pointerEvents: 'none',
		opacity: clamp(opacity, 0, 1),
		...(mask ? {WebkitMaskImage: mask, maskImage: mask} : null),
		...style,
	};

	if (onCanvas) {
		return <canvas ref={ref} width={cw} height={ch} style={{position: 'absolute', left: 0, top: 0, width, height, ...common}} />;
	}

	const soft = Math.max(0.5, 0.75 * unit);
	const line = Math.max(1, w);
	const stroke = (dir: string) =>
		`linear-gradient(${dir}, transparent 0px, ${ink} ${soft}px, ${ink} ${soft + line}px, transparent ${2 * soft + line}px, transparent 100%)`;
	let bg: React.CSSProperties;
	if (kind === 'grid') {
		bg = {
			backgroundImage: `${stroke('180deg')}, ${stroke('90deg')}`,
			backgroundSize: `${cell}px ${cell}px`,
			backgroundPosition: `${ox}px ${oy}px`,
		};
	} else if (kind === 'rules') {
		bg = {backgroundImage: stroke('180deg'), backgroundSize: `100% ${cell}px`, backgroundPosition: `0px ${oy}px`};
	} else if (kind === 'dots') {
		const r = Math.max(0.75, w / 2);
		bg = {
			backgroundImage: `radial-gradient(circle at center, ${ink} 0px, ${ink} ${r - 0.5}px, transparent ${r + 0.6}px)`,
			backgroundSize: `${cell}px ${cell}px`,
			backgroundPosition: `${ox - cell / 2}px ${oy - cell / 2}px`,
		};
	} else if (kind === 'checker') {
		bg = {
			backgroundImage: `repeating-conic-gradient(${ink} 0deg 90deg, transparent 90deg 180deg)`,
			backgroundSize: `${cell * 2}px ${cell * 2}px`,
			backgroundPosition: `${ox}px ${oy}px`,
		};
	} else {
		// stripes: one period is a stripe and a gap, with a one pixel ramp at each edge so leaning stripes stay smooth
		const stripe = Math.max(1, w);
		const period = stripe + Math.max(1, cell - stripe);
		const off = (dx * Math.cos((ang * Math.PI) / 180) + dy * Math.sin((ang * Math.PI) / 180)) % period;
		bg = {
			backgroundImage: `repeating-linear-gradient(${ang}deg, ${ink} ${off}px, ${ink} ${off + stripe - 1}px, transparent ${off + stripe}px, transparent ${off + period - 1}px, ${ink} ${off + period}px)`,
		};
	}
	return <AbsoluteFill style={{...bg, ...common}} />;
};
