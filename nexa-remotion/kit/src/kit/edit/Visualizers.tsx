// Audio visualisers drawn from the real sound: spectrum bars, a waveform line, a scrolling level strip and a
// radial ring, plus hooks for your own. Audio is loaded in windows (useWindowedAudioData), so hour-long files
// work, and every value is a pure function of the frame.
import {createSmoothSvgPath, useWindowedAudioData, visualizeAudio, type MediaUtilsAudioData} from '@remotion/media-utils';
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {useStage, useTheme} from '../core';

export type AudioSourceOptions = {
	src: string;
	/**
	 * Frame on this component's timeline where the audio starts playing (like <Audio from>). The analysis reads the
	 * file at `frame - from + trimBefore`. Inside a Sequence that starts at S, while the audio plays from the
	 * composition start, pass from={-S}.
	 */
	from?: number;
	trimBefore?: number;
	/** Seconds per loaded window; three are kept around the playhead. Fixed after mount. */
	windowSeconds?: number;
};

export type AudioAt = {
	/** The loaded audio, or null before the audio starts, after it ends, or while loading. */
	data: MediaUtilsAudioData | null;
	/** Seconds of the file before the loaded data starts (pass to visualizeAudio as dataOffsetInSeconds). */
	offset: number;
	/** Frames into the file at the current frame. */
	position: number;
	fps: number;
};

/** The analysed audio at the current frame, with the file position worked out from `from` and `trimBefore`. */
export const useAudioAt = ({src, from = 0, trimBefore = 0, windowSeconds = 10}: AudioSourceOptions): AudioAt => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const position = frame - from + trimBefore;
	const {audioData, dataOffsetInSeconds} = useWindowedAudioData({
		src,
		frame: Math.max(0, position),
		fps,
		windowInSeconds: windowSeconds,
	});
	return {data: position >= 0 ? audioData : null, offset: dataOffsetInSeconds, position, fps};
};

// ------------------------------------------------------------------ spectrum

export type SpectrumOptions = AudioSourceOptions & {
	/** Bars across the band (log spaced). */
	bars?: number;
	minHz?: number;
	maxHz?: number;
	/** dB mapped to an empty bar and to a full one. */
	floorDb?: number;
	ceilDb?: number;
	/** dB per octave added above 1 kHz: raw spectra slope down, this levels the highs with the bass. */
	tilt?: number;
	/** Share of a peak left after one frame (0.7): bars fall like a meter instead of flickering. 0 = off. */
	decay?: number;
	/** Frames of history the fall-off looks at. */
	lookback?: number;
};

const FFT_SIZE = 1024; // visualizeAudio samples: a 2048-sample FFT, 23 Hz bins at 48 kHz

const magnitudes = (a: AudioAt, frame: number): number[] | null => {
	if (!a.data || frame < 0) {
		return null;
	}
	return visualizeAudio({
		audioData: a.data,
		frame,
		fps: a.fps,
		numberOfSamples: FFT_SIZE,
		optimizeFor: 'speed',
		dataOffsetInSeconds: a.offset,
		smoothing: false,
	});
};

const bandLevels = (mags: number[], sampleRate: number, o: Required<Omit<SpectrumOptions, keyof AudioSourceOptions | 'decay' | 'lookback'>>) => {
	const res = sampleRate / (2 * FFT_SIZE);
	const out: number[] = [];
	for (let i = 0; i < o.bars; i++) {
		const lo = o.minHz * Math.pow(o.maxHz / o.minHz, i / o.bars);
		const hi = o.minHz * Math.pow(o.maxHz / o.minHz, (i + 1) / o.bars);
		const k0 = Math.max(1, Math.floor(lo / res));
		const k1 = Math.max(k0, Math.min(mags.length - 1, Math.ceil(hi / res) - 1));
		let sum = 0;
		for (let k = k0; k <= k1; k++) {
			sum += mags[k] * mags[k];
		}
		const v = Math.sqrt(sum / (k1 - k0 + 1));
		const centre = Math.sqrt(lo * hi);
		const db = 20 * Math.log10(v + 1e-9) + o.tilt * Math.max(0, Math.log2(centre / 1000));
		out.push(Math.min(1, Math.max(0, (db - o.floorDb) / (o.ceilDb - o.floorDb))));
	}
	return out;
};

/** Spectrum bars 0 to 1 at the current frame (bass first), log spaced, levelled and falling like a meter. */
export const useAudioSpectrum = (o: SpectrumOptions): number[] => {
	const a = useAudioAt(o);
	const {bars = 32, minHz = 40, maxHz = 12000, floorDb = -62, ceilDb = -12, tilt = 3, decay = 0.7, lookback = 4} = o;
	const opts = {bars, minHz, maxHz, floorDb, ceilDb, tilt};
	const out = new Array<number>(bars).fill(0);
	if (!a.data) {
		return out;
	}
	const steps = decay > 0 ? Math.max(0, lookback) : 0;
	for (let j = 0; j <= steps; j++) {
		const m = magnitudes(a, a.position - j);
		if (!m) {
			break;
		}
		const lv = bandLevels(m, a.data.sampleRate, opts);
		const k = Math.pow(decay, j);
		for (let i = 0; i < bars; i++) {
			out[i] = Math.max(out[i], lv[i] * k);
		}
	}
	return out;
};

/** One 0 to 1 level for a frequency band (default the bass, 30 to 150 Hz): drive a pulse or a flash with it. */
export const useAudioLevel = (
	o: AudioSourceOptions & {band?: readonly [number, number]; floorDb?: number; ceilDb?: number; decay?: number; lookback?: number},
): number => {
	const {band = [30, 150], floorDb = -40, ceilDb = -8} = o;
	const [v] = useAudioSpectrum({...o, bars: 1, minHz: band[0], maxHz: band[1], floorDb, ceilDb, tilt: 0});
	return v ?? 0;
};

// ------------------------------------------------------------------ bars

export type AudioBarsProps = SpectrumOptions & {
	/** Size in px at 1080. */
	width?: number;
	height?: number;
	/** Share of each bar's slot left empty. */
	gap?: number;
	color?: string;
	/** A second colour at the tips (a vertical gradient). */
	color2?: string;
	/** 'bottom' grows up from a baseline; 'center' grows both ways from the middle. */
	align?: 'bottom' | 'center';
	/** Bass in the middle, highs out to both sides (a symmetric shape). */
	mirror?: boolean;
	/** Height of a silent bar, px at 1080. */
	minHeight?: number;
	style?: React.CSSProperties;
};

export const AudioBars: React.FC<AudioBarsProps> = ({width = 1200, height = 320, gap = 0.38, color, color2, align = 'bottom', mirror = false, minHeight = 6, style, ...o}) => {
	const t = useTheme();
	const {unit} = useStage();
	const values = useAudioSpectrum(o);
	const shown = mirror ? [...values.slice().reverse(), ...values] : values;
	const W = width * unit;
	const H = height * unit;
	const slot = W / shown.length;
	const bw = Math.max(1, slot * (1 - gap));
	const minH = minHeight * unit;
	const id = `kit-bars-${React.useId().replace(/[^a-zA-Z0-9_-]/g, '')}`;
	const c1 = color ?? t.colors.accent;
	const c2 = color2 ?? c1;
	return (
		<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{display: 'block', overflow: 'visible', ...style}}>
			<defs>
				<linearGradient id={id} x1="0" x2="0" y1={align === 'center' ? '0.5' : '1'} y2="0">
					<stop offset="0%" stopColor={c1} />
					<stop offset="100%" stopColor={c2} />
				</linearGradient>
			</defs>
			{shown.map((v, i) => {
				const h = minH + Math.pow(v, 1.15) * (H - minH);
				const x = i * slot + (slot - bw) / 2;
				const y = align === 'center' ? (H - h) / 2 : H - h;
				return <rect key={i} x={x} y={y} width={bw} height={h} rx={Math.min(bw / 2, h / 2)} fill={`url(#${id})`} />;
			})}
		</svg>
	);
};

// ------------------------------------------------------------------ waveform line and scrolling strip

export type AudioWaveProps = AudioSourceOptions & {
	/** 'line': the live waveform (an oscilloscope). 'scroll': level bars sliding past a centre playhead. */
	variant?: 'line' | 'scroll';
	width?: number;
	height?: number;
	color?: string;
	/** 'scroll': colour of the part not played yet. */
	color2?: string;
	/** 'line': stroke in px at 1080. */
	strokeWidth?: number;
	/** 'line': seconds of sound across the width (0.04 to 0.1); 'scroll': seconds visible (4 to 8). */
	seconds?: number;
	/** 'line': points drawn; 'scroll': bars visible. */
	points?: number;
	/** 'line': how tall the waveform draws (1 = full scale fills the height). */
	gain?: number;
	/** 'scroll': dB range mapped to bar height. */
	floorDb?: number;
	ceilDb?: number;
	/** A soft glow under the line. */
	glow?: boolean;
	style?: React.CSSProperties;
};

const sampleAt = (a: AudioAt, seconds: number): number => {
	if (!a.data) {
		return 0;
	}
	const d = a.data.channelWaveforms[0];
	const i = Math.floor((seconds - a.offset) * a.data.sampleRate);
	return i >= 0 && i < d.length ? d[i] : 0;
};

const rmsBetween = (a: AudioAt, s0: number, s1: number): number => {
	if (!a.data) {
		return 0;
	}
	const d = a.data.channelWaveforms[0];
	const sr = a.data.sampleRate;
	const i0 = Math.max(0, Math.floor((s0 - a.offset) * sr));
	const i1 = Math.min(d.length, Math.floor((s1 - a.offset) * sr));
	if (i1 <= i0) {
		return 0;
	}
	// every 4th sample is plenty for a level
	let sum = 0;
	let n = 0;
	for (let i = i0; i < i1; i += 4) {
		sum += d[i] * d[i];
		n++;
	}
	return Math.sqrt(sum / Math.max(1, n));
};

export const AudioWave: React.FC<AudioWaveProps> = ({
	variant = 'line',
	width = 1200,
	height = 240,
	color,
	color2,
	strokeWidth = 6,
	seconds,
	points,
	gain = 1.6,
	floorDb = -46,
	ceilDb = -10,
	glow = false,
	style,
	...o
}) => {
	const t = useTheme();
	const {unit} = useStage();
	const a = useAudioAt(o);
	const W = width * unit;
	const H = height * unit;
	const c1 = color ?? t.colors.accent;
	const now = a.position / a.fps;
	if (variant === 'scroll') {
		const span = seconds ?? 6;
		const n = points ?? 64;
		const slice = span / n;
		const pitch = W / n;
		const bw = pitch * 0.56;
		const first = Math.floor((now - span / 2) / slice) - 1;
		const bars: React.ReactNode[] = [];
		for (let m = first; m <= first + n + 2; m++) {
			const x = W / 2 + ((m + 0.5) * slice - now) * (pitch / slice) - bw / 2;
			if (x < -bw || x > W) {
				continue;
			}
			const rms = m < 0 ? 0 : rmsBetween(a, m * slice, (m + 1) * slice);
			const db = 20 * Math.log10(rms + 1e-9);
			const v = Math.min(1, Math.max(0, (db - floorDb) / (ceilDb - floorDb)));
			const h = Math.max(bw, v * H);
			const played = (m + 0.5) * slice <= now;
			// bars fade out towards both ends of the strip
			const edge = Math.min(1, Math.min(x + bw, W - x) / (W * 0.12));
			bars.push(
				<rect key={m} x={x} y={(H - h) / 2} width={bw} height={h} rx={bw / 2} fill={played ? c1 : color2 ?? t.colors.faint} opacity={Math.max(0, edge)} />,
			);
		}
		return (
			<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{display: 'block', overflow: 'visible', ...style}}>
				{bars}
				<rect x={W / 2 - 1.5 * unit} y={-8 * unit} width={3 * unit} height={H + 16 * unit} rx={1.5 * unit} fill={t.colors.text} opacity={0.85} />
			</svg>
		);
	}
	const span = seconds ?? 0.06;
	const n = points ?? 96;
	const pts: {x: number; y: number}[] = [];
	for (let i = 0; i < n; i++) {
		const s = now - span / 2 + (i / (n - 1)) * span;
		// a short average keeps the line from aliasing
		const v = (sampleAt(a, s) + sampleAt(a, s + 0.0002) + sampleAt(a, s - 0.0002)) / 3;
		// tanh saturates softly, so loud passages round off instead of flat-topping
		const y = H / 2 - Math.tanh(v * gain) * (H / 2 - strokeWidth * unit);
		pts.push({x: (i / (n - 1)) * W, y});
	}
	const d = createSmoothSvgPath({points: pts});
	return (
		<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{display: 'block', overflow: 'visible', ...style}}>
			{glow ? <path d={d} fill="none" stroke={c1} strokeWidth={strokeWidth * unit * 3} strokeLinecap="round" opacity={0.25} style={{filter: `blur(${10 * unit}px)`}} /> : null}
			<path d={d} fill="none" stroke={c1} strokeWidth={strokeWidth * unit} strokeLinecap="round" strokeLinejoin="round" />
		</svg>
	);
};

// ------------------------------------------------------------------ radial ring

export type AudioCircleProps = SpectrumOptions & {
	/** Inner diameter, px at 1080. */
	size?: number;
	/** Longest bar, px at 1080. */
	length?: number;
	barWidth?: number;
	color?: string;
	/** Left half mirrors the right, so the ring is symmetric (bass at the top). */
	mirror?: boolean;
	/** Slow turn in degrees per second (0 = still). */
	spin?: number;
	/** Scale of the inner content with the bass (0.04 = up to 4 % bigger). */
	pulse?: number;
	/** Inside the ring: a cover, a logo, a face. */
	children?: React.ReactNode;
	style?: React.CSSProperties;
};

export const AudioCircle: React.FC<AudioCircleProps> = ({
	size = 380,
	length = 110,
	barWidth = 7,
	color,
	mirror = true,
	spin = 6,
	pulse = 0.04,
	children,
	style,
	bars = 36,
	...o
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {unit, fps} = useStage();
	const values = useAudioSpectrum({...o, bars});
	const ring = mirror ? [...values, ...values.slice().reverse()] : values;
	const r0 = (size / 2) * unit + 10 * unit;
	const L = length * unit;
	const outer = r0 + L + barWidth * unit;
	const S = outer * 2;
	const bass = (values[0] + values[1] + values[2]) / 3;
	const turn = (spin * frame) / fps;
	const c1 = color ?? t.colors.accent;
	return (
		<div style={{position: 'relative', width: S, height: S, ...style}}>
			<svg width={S} height={S} viewBox={`0 0 ${S} ${S}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				{ring.map((v, i) => {
					const ang = ((i / ring.length) * 360 + turn - 90) * (Math.PI / 180);
					const len = 4 * unit + Math.pow(v, 1.1) * L;
					const x0 = S / 2 + Math.cos(ang) * r0;
					const y0 = S / 2 + Math.sin(ang) * r0;
					const x1 = S / 2 + Math.cos(ang) * (r0 + len);
					const y1 = S / 2 + Math.sin(ang) * (r0 + len);
					return <line key={i} x1={x0} y1={y0} x2={x1} y2={y1} stroke={c1} strokeWidth={barWidth * unit} strokeLinecap="round" opacity={0.55 + 0.45 * v} />;
				})}
			</svg>
			<div
				style={{
					position: 'absolute',
					left: S / 2 - (size / 2) * unit,
					top: S / 2 - (size / 2) * unit,
					width: size * unit,
					height: size * unit,
					borderRadius: '50%',
					overflow: 'hidden',
					scale: `${1 + pulse * bass}`,
				}}
			>
				{children}
			</div>
		</div>
	);
};
