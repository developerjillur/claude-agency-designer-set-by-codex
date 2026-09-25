import type {LogoMark} from './kit/ui/Logo';

// Ledgerly's one mark, used everywhere: the lockup, the end card and the browser tab (a rounded square with an L,
// the same shape the tab draws for its letter). The brand and its domain are invented for this demo.
export const LEDGERLY_MARK: LogoMark = {
	viewBox: '0 0 120 120',
	parts: [
		{d: 'M40 8H80a32 32 0 0 1 32 32V80a32 32 0 0 1-32 32H40A32 32 0 0 1 8 80V40A32 32 0 0 1 40 8Z', fill: 'accent'},
		{d: 'M47 30V88H83', stroke: 'onAccent', strokeWidth: 15},
	],
};

export const LEDGERLY_TAB = {title: 'Ledgerly', letter: 'L'};
