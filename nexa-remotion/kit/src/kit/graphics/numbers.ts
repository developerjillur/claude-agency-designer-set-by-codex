// Number formatting for charts, stats and counters. Written here (not Intl) so every render machine prints the
// same characters: grouping, decimals, compact units, Bangla or Devanagari digits and a real minus sign.

export type ValueFormat = {
	decimals?: number; // fixed decimals; default: the value's own (up to 3), 1 for compact values under 100
	prefix?: string; // '$', '৳'
	suffix?: string; // '%', ' kg'
	compact?: boolean; // 1.2K, 3.4M (or 1.2L, 3.4Cr with south-asian grouping)
	units?: readonly string[]; // compact suffixes, smallest first: ['K', 'M', 'B', 'T'] or ['K', 'L', 'Cr']
	grouping?: 'intl' | 'south-asian' | 'none'; // 1,234,567 or 12,34,567
	separator?: string; // group separator, default ','
	point?: string; // decimal mark, default '.'
	digits?: 'latin' | 'bengali' | 'devanagari';
	sign?: 'auto' | 'always' | 'never'; // 'always' puts + on positive values (deltas)
	minus?: string; // default U+2212, the typographic minus
};

export type ValueFormatter = ValueFormat | ((value: number) => string);

const DIGITS: Record<'bengali' | 'devanagari', string> = {
	bengali: '০১২৩৪৫৬৭৮৯',
	devanagari: '०१२३४५६७८९',
};

/** Latin digits in a string replaced by Bangla (or Devanagari) digits. */
export const localDigits = (s: string, digits: ValueFormat['digits'] = 'latin'): string => {
	if (!digits || digits === 'latin') {
		return s;
	}
	const set = DIGITS[digits];
	return s.replace(/[0-9]/g, (d) => set[Number(d)]);
};

/** The number of decimals a value really has (0 to 3). */
export const decimalsOf = (v: number): number => {
	const a = Math.abs(v);
	for (let d = 0; d < 3; d++) {
		const k = a * 10 ** d;
		if (Math.abs(Math.round(k) - k) < 1e-7 * Math.max(1, k)) {
			return d;
		}
	}
	return 3;
};

const group = (int: string, mode: ValueFormat['grouping'], sep: string): string => {
	if (mode === 'none' || int.length <= 3) {
		return int;
	}
	if (mode === 'south-asian') {
		const last = int.slice(-3);
		let rest = int.slice(0, -3);
		const parts: string[] = [];
		while (rest.length > 2) {
			parts.unshift(rest.slice(-2));
			rest = rest.slice(0, -2);
		}
		if (rest) {
			parts.unshift(rest);
		}
		return [...parts, last].join(sep);
	}
	const parts: string[] = [];
	let rest = int;
	while (rest.length > 3) {
		parts.unshift(rest.slice(-3));
		rest = rest.slice(0, -3);
	}
	parts.unshift(rest);
	return parts.join(sep);
};

const compactSteps = (f: ValueFormat): [number, string][] => {
	if (f.grouping === 'south-asian') {
		const u = f.units ?? ['K', 'L', 'Cr'];
		return [
			[1e7, u[2] ?? 'Cr'],
			[1e5, u[1] ?? 'L'],
			[1e3, u[0] ?? 'K'],
		];
	}
	const u = f.units ?? ['K', 'M', 'B', 'T'];
	return [
		[1e12, u[3] ?? 'T'],
		[1e9, u[2] ?? 'B'],
		[1e6, u[1] ?? 'M'],
		[1e3, u[0] ?? 'K'],
	];
};

/**
 * A number as display text: `formatValue(1234567, {compact: true})` is "1.2M", `formatValue(-0.25, {suffix: '%',
 * decimals: 1})` is "−0.3%", `formatValue(1234567, {grouping: 'south-asian', digits: 'bengali'})` is "১২,৩৪,৫৬৭".
 */
export const formatValue = (value: number, f: ValueFormat = {}): string => {
	if (!Number.isFinite(value)) {
		return '';
	}
	let a = Math.abs(value);
	let unit = '';
	let autoTrim = false;
	if (f.compact) {
		for (const [k, u] of compactSteps(f)) {
			if (a >= k * 0.9995) {
				a /= k;
				unit = u;
				break;
			}
		}
	}
	let dec = f.decimals;
	if (dec === undefined) {
		if (unit) {
			dec = a < 100 ? 1 : 0;
			autoTrim = true;
		} else {
			dec = decimalsOf(a);
		}
	}
	let fixed = a.toFixed(Math.max(0, Math.min(10, dec)));
	if (autoTrim && fixed.includes('.')) {
		fixed = fixed.replace(/\.?0+$/, '');
	}
	const [int, frac] = fixed.split('.');
	const body = group(int, f.grouping ?? 'intl', f.separator ?? ',') + (frac ? (f.point ?? '.') + frac : '');
	const isZero = Number(fixed) === 0;
	const signMode = f.sign ?? 'auto';
	const sign =
		value < 0 && !isZero && signMode !== 'never' ? (f.minus ?? '−') : value > 0 && !isZero && signMode === 'always' ? '+' : '';
	return localDigits(`${sign}${f.prefix ?? ''}${body}${unit}${f.suffix ?? ''}`, f.digits);
};

/** A ValueFormatter (options or a function) applied to a value. */
export const applyFormat = (value: number, f: ValueFormatter | undefined): string =>
	typeof f === 'function' ? f(value) : formatValue(value, f);

/**
 * The same format for axis ticks: decimals follow each tick (so '$1M', not '$1.0M') and zero is a plain '0' in
 * the chosen digits.
 */
export const tickFormat = (f: ValueFormatter | undefined): ((v: number) => string) => {
	if (typeof f === 'function') {
		return f;
	}
	return (v: number) => (Math.abs(v) < 1e-12 ? localDigits('0', f?.digits) : formatValue(v, {...f, decimals: undefined}));
};

/**
 * The value of a count from `from` to `to` at progress `p`, rounded to the decimals the final value is shown with,
 * so a counter never flickers through extra digits.
 */
export const countValue = (from: number, to: number, p: number, decimals?: number): number => {
	const d = decimals ?? Math.max(decimalsOf(from), decimalsOf(to));
	const v = from + (to - from) * p;
	const k = 10 ** d;
	return Math.round(v * k) / k;
};

/** Decimals a format prints for the final value (so every step of a count uses the same). */
export const decimalsFor = (to: number, f: ValueFormatter | undefined): number | undefined =>
	typeof f === 'function' ? undefined : (f?.decimals ?? (f?.compact ? undefined : decimalsOf(to)));

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** A date as 'Mar 2026', 'Mar 4' or '2026' in UTC (the same on every render machine). */
export const formatChartDate = (d: Date, style: 'month-year' | 'month-day' | 'year' | 'month' = 'month-year'): string => {
	const y = d.getUTCFullYear();
	const m = MONTHS[d.getUTCMonth()];
	if (style === 'year') {
		return String(y);
	}
	if (style === 'month') {
		return m;
	}
	if (style === 'month-day') {
		return `${m} ${d.getUTCDate()}`;
	}
	return `${m} ${y}`;
};
