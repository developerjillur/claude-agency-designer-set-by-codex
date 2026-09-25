// LUTs for fx.lut(): make a .cube in code, or load one from public/ while holding the render.
import {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

type Rgb = [number, number, number];

/**
 * A 3D .cube LUT from a colour function (inputs and outputs 0 to 1). 17 points is plenty for a look (4913 rows);
 * 33 for a precise grade. Build it once at module level or in useMemo, never per frame (lut() caches 4 contents).
 */
export const makeCubeLut = (fn: (r: number, g: number, b: number) => Rgb, size = 17, title = 'nexa lut'): string => {
	const n = Math.min(64, Math.max(2, Math.round(size)));
	const rows = [`TITLE "${title.replace(/"/g, '')}"`, `LUT_3D_SIZE ${n}`, 'DOMAIN_MIN 0 0 0', 'DOMAIN_MAX 1 1 1'];
	const c = (v: number) => Math.min(1, Math.max(0, Number.isFinite(v) ? v : 0)).toFixed(5);
	// red changes fastest, then green, then blue (the .cube order)
	for (let b = 0; b < n; b++) {
		for (let g = 0; g < n; g++) {
			for (let r = 0; r < n; r++) {
				const [R, G, B] = fn(r / (n - 1), g / (n - 1), b / (n - 1));
				rows.push(`${c(R)} ${c(G)} ${c(B)}`);
			}
		}
	}
	return rows.join('\n');
};

/**
 * Keeps only what lut() accepts from a .cube exported by a grading app: TITLE, LUT_3D_SIZE, DOMAIN_MIN/MAX and the
 * rows. Other directives (LUT_3D_INPUT_RANGE, LUT_1D_SIZE) make lut() throw; a 1D LUT cannot be converted.
 */
export const cleanCube = (text: string): string =>
	text
		.split(/\r?\n/)
		.filter((line) => {
			const l = line.trim();
			return l === '' || l.startsWith('#') || /^(TITLE|LUT_3D_SIZE|DOMAIN_MIN|DOMAIN_MAX)\b/.test(l) || /^[-+0-9.eE]+\s+[-+0-9.eE]+\s+[-+0-9.eE]+$/.test(l);
		})
		.join('\n');

/**
 * The text of a .cube file in public/ (for fx.lut). Holds the render until it has loaded; null until then, so
 * pass `effects={cube ? [fx.lut(cube)] : []}`.
 */
export const useLutFile = (file: string): string | null => {
	const [cube, setCube] = useState<string | null>(null);
	const [handle] = useState(() => delayRender(`Loading LUT ${file}`));
	useEffect(() => {
		let live = true;
		fetch(file.startsWith('http') || file.startsWith('/') ? file : staticFile(file))
			.then((r) => {
				if (!r.ok) {
					throw new Error(`Could not load the LUT ${file}: HTTP ${r.status}`);
				}
				return r.text();
			})
			.then((text) => {
				if (live) {
					setCube(cleanCube(text));
				}
			})
			.catch((err) => cancelRender(err));
		return () => {
			live = false;
		};
	}, [file, handle]);
	// release the render only after the LUT is in the tree, so the effect host has started applying it
	useEffect(() => {
		if (cube !== null) {
			continueRender(handle);
		}
	}, [cube, handle]);
	return cube;
};
