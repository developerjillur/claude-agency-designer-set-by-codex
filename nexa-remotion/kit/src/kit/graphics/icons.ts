// The kit's stroke icons: drawn for this kit on a 24 x 24 grid, 2 px strokes, round caps and joins, every icon
// made of open or closed strokes so it can draw itself on. Strokes are listed in the order a hand would draw them.

const f = (v: number) => +v.toFixed(2);

/** A circle as one closed stroke from 12 o'clock, clockwise. */
const circle = (cx: number, cy: number, r: number) =>
	`M${f(cx)} ${f(cy - r)}A${r} ${r} 0 1 1 ${f(cx)} ${f(cy + r)}A${r} ${r} 0 1 1 ${f(cx)} ${f(cy - r)}`;

/** A rounded rectangle as one closed stroke from its top-left. */
const rrect = (x: number, y: number, w: number, h: number, r: number) =>
	`M${f(x + r)} ${f(y)}H${f(x + w - r)}A${r} ${r} 0 0 1 ${f(x + w)} ${f(y + r)}V${f(y + h - r)}A${r} ${r} 0 0 1 ${f(x + w - r)} ${f(y + h)}` +
	`H${f(x + r)}A${r} ${r} 0 0 1 ${f(x)} ${f(y + h - r)}V${f(y + r)}A${r} ${r} 0 0 1 ${f(x + r)} ${f(y)}Z`;

/** A gear outline: `teeth` teeth between radius `inner` and `outer`. */
const gear = (cx: number, cy: number, teeth: number, outer: number, inner: number) => {
	const pts: string[] = [];
	const step = 360 / teeth;
	for (let i = 0; i < teeth; i++) {
		const c = i * step;
		for (const [da, r] of [
			[-step * 0.3, inner],
			[-step * 0.17, outer],
			[step * 0.17, outer],
			[step * 0.3, inner],
		] as const) {
			const a = ((c + da - 90) * Math.PI) / 180;
			pts.push(`${f(cx + r * Math.cos(a))} ${f(cy + r * Math.sin(a))}`);
		}
	}
	return `M${pts.join('L')}Z`;
};

/** A five-point star, first tip at 12 o'clock. */
const star = (cx: number, cy: number, outer: number, inner: number) => {
	const pts: string[] = [];
	for (let i = 0; i < 10; i++) {
		const r = i % 2 === 0 ? outer : inner;
		const a = -Math.PI / 2 + (i * Math.PI) / 5;
		pts.push(`${f(cx + r * Math.cos(a))} ${f(cy + r * Math.sin(a))}`);
	}
	return `M${pts.join('L')}Z`;
};

export const ICONS = {
	check: 'M4.5 12.5L9.5 17.5L19.5 6.5',
	x: 'M6 6L18 18M18 6L6 18',
	'arrow-right': 'M4 12H20M13.5 5.5L20 12L13.5 18.5',
	'arrow-left': 'M20 12H4M10.5 5.5L4 12L10.5 18.5',
	'arrow-up': 'M12 20V4M5.5 10.5L12 4L18.5 10.5',
	'arrow-down': 'M12 4V20M5.5 13.5L12 20L18.5 13.5',
	trend: 'M4.5 19.5L19 5M9.5 5H19V14.5',
	play: 'M7.5 4.8L19 12L7.5 19.2Z',
	pause: 'M8.5 5V19M15.5 5V19',
	star: star(12, 12.8, 9.6, 4.2),
	heart: 'M12 20.3C7.4 17.2 3 13.7 3 9.2C3 6.4 5.2 4.3 7.8 4.3C9.6 4.3 11.1 5.3 12 6.9C12.9 5.3 14.4 4.3 16.2 4.3C18.8 4.3 21 6.4 21 9.2C21 13.7 16.6 17.2 12 20.3Z',
	bolt: 'M13.5 2.5L5 13.5H11.5L10.5 21.5L19 10.5H12.5Z',
	globe: `${circle(12, 12, 9)}M12 3C9.3 5.4 8 8.6 8 12C8 15.4 9.3 18.6 12 21C14.7 18.6 16 15.4 16 12C16 8.6 14.7 5.4 12 3ZM3 12H21`,
	'chart-up': 'M3.5 3.5V20.5H20.5M7.5 15.5L11 12L14 14.5L19.5 8.5M15.5 8.5H19.5V12.5',
	'chart-down': 'M3.5 3.5V20.5H20.5M7.5 8.5L11 12L14 9.5L19.5 15.5M15.5 15.5H19.5V11.5',
	'chart-bar': 'M3.5 20.5H20.5M6.5 20.5V13M11 20.5V8M15.5 20.5V11M20 20.5V5',
	user: `${circle(12, 8, 4)}M4.5 20.5C4.9 16.8 8 14.5 12 14.5C16 14.5 19.1 16.8 19.5 20.5`,
	users: `${circle(9, 8.5, 3.5)}M2.5 20C2.9 16.6 5.5 14.5 9 14.5C12.5 14.5 15.1 16.6 15.5 20M15.2 5.3A3.3 3.3 0 0 1 15.2 11.7M17.3 14.4C19.7 15 21.2 16.9 21.5 19.8`,
	lock: `${rrect(5, 10.5, 14, 10.5, 2.2)}M8 10.5V7.5A4 4 0 0 1 16 7.5V10.5M12 14.5V17`,
	bell: 'M18 16.5V11A6 6 0 0 0 6 11V16.5L4.5 18.5H19.5ZM10.2 21A2 2 0 0 0 13.8 21',
	cart: `M2.5 3.5H5.5L8 15.5H18L20.5 7H6.5${circle(9.5, 19.5, 1.5)}${circle(16.5, 19.5, 1.5)}`,
	clock: `${circle(12, 12, 9)}M12 6.5V12L15.5 14`,
	pin: `M12 21.5C12 21.5 5 15 5 9.8A7 7 0 0 1 19 9.8C19 15 12 21.5 12 21.5Z${circle(12, 9.8, 2.6)}`,
	mail: `${rrect(3, 5.5, 18, 13, 2)}M3.8 7.2L12 13L20.2 7.2`,
	phone: `${rrect(6.5, 2.5, 11, 19, 2.5)}M10.5 18.5H13.5`,
	search: `${circle(10.5, 10.5, 6.5)}M15.3 15.3L20.5 20.5`,
	plus: 'M12 5V19M5 12H19',
	minus: 'M5 12H19',
	home: 'M3.5 11L12 3.8L20.5 11M5.8 9.3V20H18.2V9.3M9.8 20V14.5H14.2V20',
	settings: `${gear(12, 12, 8, 9.6, 7.2)}${circle(12, 12, 3)}`,
	camera: `M3 8.5A2 2 0 0 1 5 6.5H7.5L9.2 4H14.8L16.5 6.5H19A2 2 0 0 1 21 8.5V17.5A2 2 0 0 1 19 19.5H5A2 2 0 0 1 3 17.5Z${circle(12, 13, 3.5)}`,
	cloud: 'M7 19H17A4.25 4.25 0 0 0 17.6 10.55A6 6 0 0 0 6.3 9.4A4.8 4.8 0 0 0 7 19Z',
	code: 'M8.5 7L3.5 12L8.5 17M15.5 7L20.5 12L15.5 17M13.5 4.5L10.5 19.5',
	file: 'M14 2.5H7A2 2 0 0 0 5 4.5V19.5A2 2 0 0 0 7 21.5H17A2 2 0 0 0 19 19.5V7.5ZM14 2.5V7.5H19M9 12.5H15M9 16.5H15',
	money: `${rrect(2.5, 6, 19, 12, 2)}${circle(12, 12, 2.8)}M6 12L6 12M18 12L18 12`,
	trophy: 'M7 3.5H17V9A5 5 0 0 1 7 9ZM7 5.5H4.5V7A3.5 3.5 0 0 0 7.6 10.5M17 5.5H19.5V7A3.5 3.5 0 0 1 16.4 10.5M12 14V18M8.5 20.5H15.5M9.5 18H14.5',
	rocket: `M12 2.5C15.4 5 16.4 9.2 15.4 15H8.6C7.6 9.2 8.6 5 12 2.5Z${circle(12, 8.8, 2)}M8.9 11.6C6.9 12.5 5.8 14.3 5.8 16.9L8.6 15.3M15.1 11.6C17.1 12.5 18.2 14.3 18.2 16.9L15.4 15.3M12 18V21.5M9.8 18V19.8M14.2 18V19.8`,
	leaf: 'M5 19.5C4.5 11 10 4.5 19.5 4.5C19.5 14 13 19.5 5 19.5ZM5 19.5L13.5 11',
	shield: 'M12 2.8L19.5 5.8V11.5C19.5 16 16.3 19.6 12 21.2C7.7 19.6 4.5 16 4.5 11.5V5.8ZM8.8 12L11 14.2L15.3 9.9',
	spark: 'M12 3C12.5 8.3 15.7 11.5 21 12C15.7 12.5 12.5 15.7 12 21C11.5 15.7 8.3 12.5 3 12C8.3 11.5 11.5 8.3 12 3Z',
	calendar: `${rrect(3.5, 5, 17, 15.5, 2)}M3.5 10H20.5M8 3V7M16 3V7M8 14L8 14M12 14L12 14M16 14L16 14`,
	chat: 'M4 5.5A2 2 0 0 1 6 3.5H18A2 2 0 0 1 20 5.5V14A2 2 0 0 1 18 16H10.5L6 20V16A2 2 0 0 1 4 14ZM8.5 9.8H15.5',
	bulb: 'M9 17.5V15.6C7.2 14.4 6 12.4 6 10A6 6 0 0 1 18 10C18 12.4 16.8 14.4 15 15.6V17.5ZM10 21H14',
	target: `${circle(12, 12, 9)}${circle(12, 12, 5.2)}M12 12L12 12`,
	eye: `M2.5 12C5 7.6 8.3 5.5 12 5.5C15.7 5.5 19 7.6 21.5 12C19 16.4 15.7 18.5 12 18.5C8.3 18.5 5 16.4 2.5 12Z${circle(12, 12, 3)}`,
	download: 'M12 3.5V15M6.5 10L12 15.5L17.5 10M4.5 20.5H19.5',
	link: 'M10 14A4.2 4.2 0 0 0 16 14L19 11A4.2 4.2 0 0 0 13 5L11.8 6.2M14 10A4.2 4.2 0 0 0 8 10L5 13A4.2 4.2 0 0 0 11 19L12.2 17.8',
	flag: 'M5 21.5V3.5M5 4.5C8.5 2.5 11.5 6.5 15 4.5C16.5 3.7 18 3.8 19 4.5V13.5C18 12.8 16.5 12.7 15 13.5C11.5 15.5 8.5 11.5 5 13.5',
	gift: `${rrect(3.5, 8, 17, 4.5, 1.2)}M5 12.5V20.5H19V12.5M12 8V20.5M12 8C10.5 4 6.5 3.8 6.6 6.2C6.7 7.6 8.8 8 12 8C15.2 8 17.3 7.6 17.4 6.2C17.5 3.8 13.5 4 12 8`,
} as const;

export type IconName = keyof typeof ICONS;

export const ICON_NAMES = Object.keys(ICONS) as IconName[];
