// A small line-icon set drawn in code (24 x 24 grid, round caps), so interface mock-ups never depend on a font
// glyph or a downloaded file. Every icon takes the current text colour unless `color` is given.
import React from 'react';
import {useStage} from '../core';

type Prim =
	| ['p', string] // stroked path
	| ['pf', string] // filled path
	| ['c', number, number, number] // stroked circle
	| ['cf', number, number, number] // filled circle
	| ['r', number, number, number, number, number] // stroked rounded rect
	| ['rf', number, number, number, number, number]; // filled rounded rect

const HEART = 'M12 19.6s-7.6-4.6-9-9.3C2.2 7.4 4 4.6 7 4.6c2 0 3.6 1.2 5 3 1.4-1.8 3-3 5-3 3 0 4.8 2.8 4 5.7-1.4 4.7-9 9.3-9 9.3z';
const STAR = 'M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.2-4.1 5.8-.8z';
const BELL = 'M18 16.4V11a6 6 0 0 0-12 0v5.4L4.4 18h15.2z';

export const UI_ICONS = {
	search: [['c', 11, 11, 6.5], ['p', 'M16 16l4.5 4.5']],
	bell: [['p', BELL], ['p', 'M10 20.6a2.1 2.1 0 0 0 4 0']],
	bellFilled: [['pf', BELL], ['p', BELL], ['p', 'M10 20.6a2.1 2.1 0 0 0 4 0']],
	check: [['p', 'M5 12.5l4.5 4.5L19 7.5']],
	x: [['p', 'M6.5 6.5l11 11M17.5 6.5l-11 11']],
	plus: [['p', 'M12 5v14M5 12h14']],
	minus: [['p', 'M5 12h14']],
	heart: [['p', HEART]],
	heartFilled: [['pf', HEART], ['p', HEART]],
	star: [['p', STAR]],
	starFilled: [['pf', STAR], ['p', STAR]],
	chevronLeft: [['p', 'M14.5 5.5L8 12l6.5 6.5']],
	chevronRight: [['p', 'M9.5 5.5L16 12l-6.5 6.5']],
	chevronDown: [['p', 'M5.5 9.5L12 16l6.5-6.5']],
	arrowLeft: [['p', 'M19 12H5M11 6l-6 6 6 6']],
	arrowRight: [['p', 'M5 12h14M13 6l6 6-6 6']],
	arrowUp: [['p', 'M12 19V5M6 11l6-6 6 6']],
	refresh: [['p', 'M19.4 13.4A7.5 7.5 0 1 1 17.3 6.7'], ['p', 'M19.4 4.3v4.8h-4.8']],
	lock: [['r', 5, 10.5, 14, 10, 2.5], ['p', 'M8 10.5V8a4 4 0 0 1 8 0v2.5']],
	home: [['p', 'M4 10.6L12 4l8 6.6V20h-5.4v-5.8H9.4V20H4z']],
	user: [['c', 12, 8, 4], ['p', 'M4.5 20c.8-3.6 3.8-6 7.5-6s6.7 2.4 7.5 6']],
	sliders: [['p', 'M4 7h9M17 7h3M4 17h3M11 17h9'], ['c', 15, 7, 2], ['c', 9, 17, 2]],
	bolt: [['p', 'M13 3L5 13.5h6.5L10.5 21 19 10.5h-6.5z']],
	copy: [['r', 8.5, 8.5, 11.5, 11.5, 2.5], ['p', 'M15.5 8.5V6.5A2.5 2.5 0 0 0 13 4H6.5A2.5 2.5 0 0 0 4 6.5V13a2.5 2.5 0 0 0 2.5 2.5h2']],
	play: [['pf', 'M8 5.8v12.4a.8.8 0 0 0 1.2.7l10-6.2a.8.8 0 0 0 0-1.4l-10-6.2A.8.8 0 0 0 8 5.8z']],
	pause: [['rf', 6.5, 5, 3.6, 14, 1.2], ['rf', 13.9, 5, 3.6, 14, 1.2]],
	more: [['cf', 6, 12, 1.7], ['cf', 12, 12, 1.7], ['cf', 18, 12, 1.7]],
	menu: [['p', 'M4 7h16M4 12h16M4 17h16']],
	mail: [['r', 3.5, 5.5, 17, 13, 2.5], ['p', 'M4.2 7.2l7.8 5.8 7.8-5.8']],
	calendar: [['r', 4, 5.5, 16, 14.5, 2.5], ['p', 'M4 10h16M8.5 3.5v4M15.5 3.5v4']],
	chart: [['p', 'M5 20V11M12 20V5M19 20v-6']],
	folder: [['p', 'M3.5 7.5a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z']],
	file: [['p', 'M14 3.5H7.5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V8z'], ['p', 'M14 3.5V8h4.5']],
	globe: [['c', 12, 12, 8.5], ['p', 'M3.5 12h17M12 3.5c2.4 2.4 3.6 5.2 3.6 8.5s-1.2 6.1-3.6 8.5c-2.4-2.4-3.6-5.2-3.6-8.5S9.6 5.9 12 3.5z']],
	share: [['p', 'M12 15V4M7.5 8.5L12 4l4.5 4.5'], ['p', 'M5 12.5V18a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5.5']],
	download: [['p', 'M12 4v11M7.5 10.5L12 15l4.5-4.5'], ['p', 'M5 19.5h14']],
	trash: [['p', 'M4.5 7h15M9.5 7V5h5v2M6.5 7l1 12.5A1.5 1.5 0 0 0 9 21h6a1.5 1.5 0 0 0 1.5-1.5L17.5 7']],
	edit: [['p', 'M15 5l4 4L8.5 19.5H4.5v-4z'], ['p', 'M13 7l4 4']],
	clock: [['c', 12, 12, 8.5], ['p', 'M12 7.5V12l3 2']],
	info: [['c', 12, 12, 8.5], ['p', 'M12 11v5.5'], ['cf', 12, 7.8, 1.2]],
	warning: [['p', 'M12 4.5L21 19.5H3z'], ['p', 'M12 10v4'], ['cf', 12, 16.8, 1.1]],
	terminal: [['r', 3, 4.5, 18, 15, 2.5], ['p', 'M7 9.5l3 2.5-3 2.5M12.5 15H17']],
	code: [['p', 'M9 7l-5 5 5 5M15 7l5 5-5 5']],
	sparkle: [['pf', 'M12 3c.6 4.2 2.8 6.4 7 7-4.2.6-6.4 2.8-7 7-.6-4.2-2.8-6.4-7-7 4.2-.6 6.4-2.8 7-7z']],
	camera: [['r', 3.5, 7, 17, 12.5, 2.5], ['c', 12, 13.2, 3.4], ['p', 'M8.5 7L10 4.5h4L15.5 7']],
	image: [['r', 3.5, 4.5, 17, 15, 2.5], ['c', 9, 9.5, 1.8], ['p', 'M20.5 16l-5-5-8.5 8.5']],
	send: [['p', 'M20.5 3.5L10 14M20.5 3.5l-6.5 17-4-6.5-6.5-4z']],
	mic: [['r', 9, 3.5, 6, 11, 3], ['p', 'M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v2.5']],
	cart: [['p', 'M3.5 4.5H6l2 11h10.5l1.8-7.5H7'], ['cf', 9.5, 19.5, 1.4], ['cf', 17, 19.5, 1.4]],
	wifi: [['p', 'M2.5 9a14 14 0 0 1 19 0M5.5 12.2a9.5 9.5 0 0 1 13 0M8.6 15.4a5 5 0 0 1 6.8 0'], ['cf', 12, 18.6, 1.4]],
	sidebar: [['r', 3.5, 4.5, 17, 15, 2.5], ['p', 'M9.5 4.5v15']],
	filter: [['p', 'M4 6h16M7 12h10M10 18h4']],
	grid: [['r', 4, 4, 6.5, 6.5, 1.5], ['r', 13.5, 4, 6.5, 6.5, 1.5], ['r', 4, 13.5, 6.5, 6.5, 1.5], ['r', 13.5, 13.5, 6.5, 6.5, 1.5]],
	thumbUp: [['p', 'M7.5 10.5V20H4.5v-9.5zM7.5 10.5L11 4c1.4 0 2.3 1.1 2 2.5l-.7 3.5h5.3a2 2 0 0 1 2 2.4l-1.3 6.5a2 2 0 0 1-2 1.6H7.5']],
	link: [['p', 'M10 14a4 4 0 0 0 5.7 0l3-3A4 4 0 0 0 13 5.3l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1']],
	coffee: [['p', 'M5 9h11v5.5a4.5 4.5 0 0 1-4.5 4.5h-2A4.5 4.5 0 0 1 5 14.5z'], ['p', 'M16 10.5h1.5a2.5 2.5 0 0 1 0 5H16'], ['p', 'M8.5 3.5V6M12 3.5V6']],
	bag: [['p', 'M5 8h14l-1 12H6z'], ['p', 'M9 10V7a3 3 0 0 1 6 0v3']],
	train: [['r', 6, 3.5, 12, 13, 3], ['p', 'M6 11h12M9 20l1.5-3.5M15 20l-1.5-3.5'], ['cf', 9.5, 14, 1], ['cf', 14.5, 14, 1]],
	wallet: [['r', 3.5, 6, 17, 13, 2.5], ['p', 'M3.5 9.5h13a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2.5'], ['cf', 16, 13, 1.1]],
	cmd: [['p', 'M9 6.5v11M15 6.5v11M6.5 9h11M6.5 15h11'], ['c', 6.5, 6.5, 2.5], ['c', 17.5, 6.5, 2.5], ['c', 6.5, 17.5, 2.5], ['c', 17.5, 17.5, 2.5]],
	enter: [['p', 'M19 5v6.5a2.5 2.5 0 0 1-2.5 2.5H6M10 10l-4 4 4 4']],
	shift: [['p', 'M12 4.5l7.5 8H15V19H9v-6.5H4.5z']],
} satisfies Record<string, Prim[]>;

export type UiIconName = keyof typeof UI_ICONS;

export type UiIconProps = {
	name: UiIconName;
	size?: number; // px at 1080 (default 24)
	color?: string; // default: currentColor
	stroke?: number; // line width on the 24 grid (default 2)
	style?: React.CSSProperties;
};

/** One icon from the kit's set, drawn as SVG. */
export const UiIcon: React.FC<UiIconProps> = ({name, size = 24, color = 'currentColor', stroke = 2, style}) => {
	const {unit} = useStage();
	const prims = UI_ICONS[name] as Prim[];
	const s = size * unit;
	return (
		<svg
			width={s}
			height={s}
			viewBox="0 0 24 24"
			fill="none"
			stroke={color}
			strokeWidth={stroke}
			strokeLinecap="round"
			strokeLinejoin="round"
			style={{display: 'block', flex: '0 0 auto', overflow: 'visible', ...style}}
		>
			{prims.map((p, i) => {
				switch (p[0]) {
					case 'p':
						return <path key={i} d={p[1]} />;
					case 'pf':
						return <path key={i} d={p[1]} fill={color} stroke="none" />;
					case 'c':
						return <circle key={i} cx={p[1]} cy={p[2]} r={p[3]} />;
					case 'cf':
						return <circle key={i} cx={p[1]} cy={p[2]} r={p[3]} fill={color} stroke="none" />;
					case 'r':
						return <rect key={i} x={p[1]} y={p[2]} width={p[3]} height={p[4]} rx={p[5]} />;
					case 'rf':
						return <rect key={i} x={p[1]} y={p[2]} width={p[3]} height={p[4]} rx={p[5]} fill={color} stroke="none" />;
					default:
						return null;
				}
			})}
		</svg>
	);
};
