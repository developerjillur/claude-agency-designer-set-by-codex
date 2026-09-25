// Caption data: word timings in, pages and subtitle cues out. Captions are milliseconds (the @remotion/captions
// Caption type); frames only appear when something is drawn. Pure functions, safe in Node and the browser.
import {createTikTokStyleCaptions, serializeSrt, type Caption, type TikTokPage} from '@remotion/captions';
import {clamp} from '../core';
import {endsClause, endsSentence, isPunctuation} from './text';

export type {Caption, TikTokPage};

/** A word from any transcriber: whisper (word/start/end in s), ElevenLabs (text/start/end, type), ms or s. */
export type WordLike = {
	text?: string;
	word?: string;
	punctuated_word?: string;
	start?: number;
	end?: number;
	startMs?: number;
	endMs?: number;
	start_time?: number;
	end_time?: number;
	confidence?: number | null;
	probability?: number;
	type?: string; // ElevenLabs: 'word', 'spacing', 'audio_event'
};

export type TranscriptLike =
	| readonly WordLike[]
	| {words?: readonly WordLike[]; segments?: readonly {words?: readonly WordLike[]}[]};

const FILLER = /^\s*(\[[^\]]*\]|\([^)]*\)|TT_\d+|<\|[^|]*\|>)\s*$/;

const listOf = (input: TranscriptLike): readonly WordLike[] => {
	if (Array.isArray(input)) {
		return input as readonly WordLike[];
	}
	const o = input as {words?: readonly WordLike[]; segments?: readonly {words?: readonly WordLike[]}[]};
	if (o.words?.length) {
		return o.words;
	}
	return (o.segments ?? []).flatMap((s) => s.words ?? []);
};

export type ToCaptionsOptions = {
	unit?: 'auto' | 's' | 'ms'; // 'auto': seconds unless every time is a whole number and some exceed 30
	offsetMs?: number; // added to every time (a transcript of a clip that starts later)
};

/**
 * Word timings from a transcriber (an array of words, `{words}` or `{segments: [{words}]}`) as Caption[] with the
 * whitespace createTikTokStyleCaptions needs: a space before every word, none before punctuation or before
 * sub-word tokens that arrived without one. Fillers like [BLANK_AUDIO], (music) and TT_12 are dropped.
 */
export const toCaptions = (input: TranscriptLike, o: ToCaptionsOptions = {}): Caption[] => {
	const raw = listOf(input).filter((w) => w.type === undefined || w.type === 'word');
	const items = raw
		.map((w) => {
			const text = w.text ?? w.word ?? w.punctuated_word ?? '';
			const ms = w.startMs !== undefined || w.endMs !== undefined;
			const s = ms ? (w.startMs ?? 0) : (w.start ?? w.start_time ?? 0);
			const e = ms ? (w.endMs ?? s) : (w.end ?? w.end_time ?? s);
			return {text, s, e, ms, conf: w.confidence ?? w.probability ?? null};
		})
		.filter((w) => w.text.trim() !== '' && !FILLER.test(w.text));
	const plain = items.filter((w) => !w.ms);
	const allWhole = plain.every((w) => Number.isInteger(w.s) && Number.isInteger(w.e));
	const isMs = o.unit === 'ms' || (o.unit !== 's' && allWhole && plain.some((w) => w.e > 30));
	const k = isMs ? 1 : 1000;
	const tokenLevel = items.some((w) => /^\s/.test(w.text));
	const off = o.offsetMs ?? 0;
	return items
		.map((w, i) => {
			const bare = w.text.replace(/\s+$/, '');
			let text: string;
			if (tokenLevel) {
				text = bare; // the transcriber already marks word starts with spaces
			} else {
				const t = bare.trim();
				text = i === 0 || isPunctuation(t) ? t : ` ${t}`;
			}
			const startMs = (w.ms ? w.s : w.s * k) + off;
			const endMs = Math.max(startMs, (w.ms ? w.e : w.e * k) + off);
			return {text, startMs, endMs, timestampMs: null, confidence: w.conf};
		})
		.sort((a, b) => a.startMs - b.startMs);
};

/** A kept range of the source in an edit: source ms `inMs` to `outMs`, placed at `atMs` in the output, sped by `rate`. */
export type CaptionCut = {inMs: number; outMs: number; atMs?: number; rate?: number};

/**
 * Captions of the source remapped into an edit (trims, jump cuts, speed changes). Cuts without `atMs` follow each
 * other. A word is kept when its middle is inside a cut; its times are clipped to the cut.
 */
export const remapCaptions = (captions: readonly Caption[], cuts: readonly CaptionCut[]): Caption[] => {
	const out: Caption[] = [];
	let cursor = 0;
	for (const c of cuts) {
		const rate = c.rate ?? 1;
		const at = c.atMs ?? cursor;
		const map = (x: number) => at + (clamp(x, c.inMs, c.outMs) - c.inMs) / rate;
		for (const w of captions) {
			const mid = (w.startMs + w.endMs) / 2;
			if (mid >= c.inMs && mid < c.outMs) {
				out.push({...w, startMs: map(w.startMs), endMs: map(w.endMs), timestampMs: w.timestampMs === null ? null : map(w.timestampMs)});
			}
		}
		cursor = at + (c.outMs - c.inMs) / rate;
	}
	return out.sort((a, b) => a.startMs - b.startMs);
};

/** Cuts given in frames (source frames at the composition fps) as ms cuts. */
export const cutsFromFrames = (
	cuts: readonly {inFrame: number; outFrame: number; atFrame?: number; rate?: number}[],
	fps: number,
): CaptionCut[] =>
	cuts.map((c) => ({
		inMs: (c.inFrame / fps) * 1000,
		outMs: (c.outFrame / fps) * 1000,
		atMs: c.atFrame === undefined ? undefined : (c.atFrame / fps) * 1000,
		rate: c.rate,
	}));

/** Every time moved by `ms` (negative values move earlier; times never go below 0). */
export const shiftCaptions = (captions: readonly Caption[], ms: number): Caption[] =>
	captions.map((w) => ({
		...w,
		startMs: Math.max(0, w.startMs + ms),
		endMs: Math.max(0, w.endMs + ms),
		timestampMs: w.timestampMs === null ? null : Math.max(0, w.timestampMs + ms),
	}));

/** Timing of a caption layer that sits over a trimmed or sped-up clip in the same Sequence. */
export type CaptionTiming = {
	trimBefore?: number; // source frames skipped (the clip's trimBefore)
	playbackRate?: number; // the clip's playbackRate
	offsetMs?: number; // added after the mapping
};

/** The caption time (ms) shown at a local frame. */
export const captionTimeAt = (frame: number, fps: number, t: CaptionTiming = {}): number =>
	(((t.trimBefore ?? 0) + frame * (t.playbackRate ?? 1)) / fps) * 1000 + (t.offsetMs ?? 0);

export type CaptionPageOptions = {
	pageMs?: number; // combine words for about this long (default 1200: 2 to 4 words)
	silenceMs?: number; // a pause this long starts a new page (default 600)
	maxHoldMs?: number; // a page stays at most this long after its last word (default 900)
	maxWords?: number; // an orphan only joins a page shorter than this (default 8)
	// a sentence spoken within this long is one page, so no word is left dangling on the next page; a longer one
	// splits after its commas, then into even runs of about pageMs (default 0: pages by time only)
	sentenceMs?: number;
};

export type CaptionWord = {text: string; fromMs: number; toMs: number};

export type CaptionPage = {
	startMs: number;
	endMs: number; // when the page leaves (the next page, or the hold after its last word)
	words: CaptionWord[]; // whole words (sub-word tokens glued, multi-word tokens split)
	text: string;
};

/**
 * Tokens as whole words: sub-word tokens without a leading space are glued to the word before, and a token with
 * spaces inside (from SRT or sentence-level captions) is split, its time shared out by length.
 */
export const captionWordsOf = (tokens: readonly {text: string; fromMs: number; toMs: number}[]): CaptionWord[] => {
	const groups: CaptionWord[] = [];
	tokens.forEach((tok, i) => {
		const glued = i > 0 && !/^\s/.test(tok.text);
		if (glued && groups.length) {
			const g = groups[groups.length - 1];
			g.text += tok.text.trim();
			g.toMs = tok.toMs;
		} else if (tok.text.trim()) {
			groups.push({text: tok.text.trim(), fromMs: tok.fromMs, toMs: tok.toMs});
		}
	});
	return groups.flatMap((g) => {
		const parts = g.text.split(/\s+/).filter(Boolean);
		if (parts.length <= 1) {
			return [g];
		}
		const total = parts.reduce((a, p) => a + p.length, 0);
		let acc = 0;
		return parts.map((p) => {
			const from = g.fromMs + ((g.toMs - g.fromMs) * acc) / total;
			acc += p.length;
			return {text: p, fromMs: from, toMs: g.fromMs + ((g.toMs - g.fromMs) * acc) / total};
		});
	});
};

/** Every word of some captions (glued and split like captionWordsOf). */
export const captionWords = (captions: readonly Caption[]): CaptionWord[] =>
	captionWordsOf(captions.map((c) => ({text: c.text, fromMs: c.startMs, toMs: c.endMs})));

/**
 * Pages cut at phrase boundaries (captionPages with sentenceMs): a pause of silenceMs or a sentence end always ends a
 * page; a sentence spoken within sentenceMs (and at most maxWords words) stays whole; a longer one splits after its
 * commas, joining neighbouring phrases while they fit, and a phrase still too long splits into even runs.
 */
const phrasePages = (
	words: CaptionWord[],
	o: {pageMs: number; silenceMs: number; maxHoldMs: number; maxWords: number; sentenceMs: number},
): CaptionPage[] => {
	const runs: CaptionWord[][] = [];
	let cur: CaptionWord[] = [];
	for (const w of words) {
		if (cur.length && w.fromMs - cur[cur.length - 1].toMs >= o.silenceMs) {
			runs.push(cur);
			cur = [];
		}
		cur.push(w);
		if (endsSentence(w.text)) {
			runs.push(cur);
			cur = [];
		}
	}
	if (cur.length) {
		runs.push(cur);
	}
	const span = (ws: CaptionWord[]) => ws[ws.length - 1].toMs - ws[0].fromMs;
	const fits = (ws: CaptionWord[]) => span(ws) <= o.sentenceMs && ws.length <= o.maxWords;
	const groups: CaptionWord[][] = [];
	for (const run of runs) {
		if (fits(run)) {
			groups.push(run);
			continue;
		}
		const phrases: CaptionWord[][] = [];
		let ph: CaptionWord[] = [];
		for (const w of run) {
			ph.push(w);
			if (endsClause(w.text)) {
				phrases.push(ph);
				ph = [];
			}
		}
		if (ph.length) {
			phrases.push(ph);
		}
		const joined: CaptionWord[][] = [];
		for (const next of phrases) {
			const last = joined[joined.length - 1];
			if (last && fits([...last, ...next])) {
				last.push(...next);
			} else {
				joined.push([...next]);
			}
		}
		for (const g of joined) {
			if (fits(g) || g.length < 2) {
				groups.push(g);
				continue;
			}
			// even runs, so the last one is never a lone word
			const n = Math.min(g.length, Math.max(2, Math.ceil(span(g) / Math.max(o.pageMs, 1)), Math.ceil(g.length / o.maxWords)));
			for (let k = 0; k < n; k++) {
				const part = g.slice(Math.round((k * g.length) / n), Math.round(((k + 1) * g.length) / n));
				if (part.length) {
					groups.push(part);
				}
			}
		}
	}
	return groups
		.map((ws, i) => {
			const next = groups[i + 1];
			const endMs = Math.min(next ? next[0].fromMs : Infinity, ws[ws.length - 1].toMs + o.maxHoldMs);
			return {startMs: ws[0].fromMs, endMs, words: ws, text: ws.map((w) => w.text).join(' ')};
		})
		.filter((p) => p.endMs > p.startMs);
};

/**
 * TikTok-style pages (createTikTokStyleCaptions) with whole words and a bounded hold after the last word. Two
 * craft rules on top: a page never runs across the end of a sentence (pageBreakAfter on sentence ends), and a
 * lone word is never left on a page of its own when it can join its neighbour (the "it." orphan).
 */
export const captionPages = (captions: readonly Caption[], o: CaptionPageOptions = {}): CaptionPage[] => {
	const {pageMs = 1200, silenceMs = 600, maxHoldMs = 900, maxWords = 8} = o;
	if (o.sentenceMs && o.sentenceMs > 0) {
		return phrasePages(captionWords(captions), {pageMs, silenceMs, maxHoldMs, maxWords, sentenceMs: o.sentenceMs});
	}
	const marked = captions.map((c, i) => (i < captions.length - 1 && endsSentence(c.text) && !c.pageBreakAfter ? {...c, pageBreakAfter: true} : c));
	const {pages} = createTikTokStyleCaptions({
		captions: marked,
		combineTokensWithinMilliseconds: pageMs,
		breakOnSilenceAfterMilliseconds: silenceMs,
	});
	const raw = pages
		.map((p) => {
			const words = captionWordsOf(p.tokens);
			return {startMs: p.startMs, endMs: p.startMs + p.durationMs, words, text: ''};
		})
		.filter((p) => p.words.length > 0);
	// merge orphans: a one-word page joins the page before it (same sentence, no real pause), or the one after it
	const merged: CaptionPage[] = [];
	raw.forEach((p, i) => {
		const prev = merged[merged.length - 1];
		if (p.words.length === 1 && prev) {
			const prevLast = prev.words[prev.words.length - 1];
			if (!endsSentence(prevLast.text) && p.words[0].fromMs - prevLast.toMs < silenceMs && prev.words.length < maxWords) {
				prev.words.push(...p.words);
				prev.endMs = p.endMs;
				return;
			}
		}
		const next = raw[i + 1];
		if (p.words.length === 1 && next && !endsSentence(p.words[0].text) && next.words[0].fromMs - p.words[0].toMs < silenceMs && next.words.length < maxWords) {
			next.words.unshift(...p.words);
			next.startMs = p.startMs;
			return;
		}
		merged.push({...p, words: [...p.words]});
	});
	return merged
		.map((p) => {
			const last = p.words[p.words.length - 1].toMs;
			return {...p, endMs: Math.min(p.endMs, last + maxHoldMs), text: p.words.map((w) => w.text).join(' ')};
		})
		.filter((p) => p.endMs > p.startMs);
};

/** The page on screen at `ms`, if any. */
export const captionPageAt = (pages: readonly CaptionPage[], ms: number): CaptionPage | null => {
	for (let i = pages.length - 1; i >= 0; i--) {
		if (pages[i].startMs <= ms) {
			return ms < pages[i].endMs ? pages[i] : null;
		}
	}
	return null;
};

export type SubtitleCueOptions = {
	maxChars?: number; // characters per line (default 42, the broadcast and YouTube limit)
	maxLines?: number; // default 2
	maxMs?: number; // longest cue (default 7000)
	minMs?: number; // shortest cue (default 833, five sixths of a second)
	gapMs?: number; // a pause this long ends a cue (default 700)
	cps?: number; // reading speed: a cue stays at least chars / cps seconds (default 20)
};

export type SubtitleCue = {startMs: number; endMs: number; lines: string[]; words: CaptionWord[]};

const SMALL = new Set(['a', 'an', 'the', 'to', 'of', 'and', 'or', 'in', 'on', 'for', 'with', 'at', 'by', 'is', 'my', 'our', 'your']);

// the best split of words into at most maxLines lines of at most maxChars
const breakLines = (words: string[], maxChars: number, maxLines: number): string[] | null => {
	const text = words.join(' ');
	if (text.length <= maxChars) {
		return [text];
	}
	if (maxLines === 2) {
		let best: string[] | null = null;
		let bestCost = Infinity;
		for (let j = 1; j < words.length; j++) {
			const a = words.slice(0, j).join(' ');
			const b = words.slice(j).join(' ');
			if (a.length > maxChars || b.length > maxChars) {
				continue;
			}
			// even lines, a slightly shorter top line, breaks after punctuation, never after a small word
			const cost =
				Math.max(a.length, b.length) +
				(a.length > b.length ? 2 : 0) +
				(endsClause(words[j - 1]) ? -6 : 0) +
				(SMALL.has(words[j - 1].toLowerCase()) ? 5 : 0);
			if (cost < bestCost) {
				bestCost = cost;
				best = [a, b];
			}
		}
		return best;
	}
	const lines: string[] = [];
	let cur = '';
	for (const w of words) {
		const next = cur ? `${cur} ${w}` : w;
		if (next.length > maxChars && cur) {
			lines.push(cur);
			cur = w;
		} else {
			cur = next;
		}
	}
	if (cur) {
		lines.push(cur);
	}
	return lines.length <= maxLines ? lines : null;
};

/**
 * Subtitle cues from word captions: at most `maxLines` lines of `maxChars`, balanced line breaks, a new cue at
 * sentence ends and pauses, timed to stay readable (min duration, reading speed) without overlapping the next.
 */
export const subtitleCues = (captions: readonly Caption[], o: SubtitleCueOptions = {}): SubtitleCue[] => {
	const {maxChars = 42, maxLines = 2, maxMs = 7000, minMs = 833, gapMs = 700, cps = 20} = o;
	const words = captionWords(captions);
	const groups: CaptionWord[][] = [];
	let cur: CaptionWord[] = [];
	const flush = () => {
		if (cur.length) {
			groups.push(cur);
			cur = [];
		}
	};
	for (const w of words) {
		if (cur.length) {
			const last = cur[cur.length - 1];
			const tooLong = w.toMs - cur[0].fromMs > maxMs;
			const pause = w.fromMs - last.toMs >= gapMs;
			const fits = breakLines([...cur, w].map((x) => x.text), maxChars, maxLines) !== null;
			if (tooLong || pause || !fits) {
				flush();
			}
		}
		cur.push(w);
		if (endsSentence(w.text) && cur.map((x) => x.text).join(' ').length >= 16) {
			flush();
		}
	}
	flush();
	const cues: SubtitleCue[] = groups.map((g) => {
		const text = g.map((x) => x.text);
		return {
			startMs: g[0].fromMs,
			endMs: g[g.length - 1].toMs,
			lines: breakLines(text, maxChars, maxLines) ?? [text.join(' ')],
			words: g,
		};
	});
	// readable durations that never run into the next cue
	return cues.map((c, i) => {
		const chars = c.lines.join(' ').length;
		const want = Math.max(c.endMs, c.startMs + minMs, c.startMs + (chars / cps) * 1000);
		const next = cues[i + 1];
		const end = next ? Math.min(want, next.startMs - 40) : want;
		return {...c, endMs: Math.max(c.endMs, end)};
	});
};

/** An SRT file from word captions (or from cues you built), for YouTube or an editor. */
export const toSrt = (input: readonly Caption[] | readonly SubtitleCue[], o: SubtitleCueOptions = {}): string => {
	const cues = (input.length && 'lines' in input[0] ? input : subtitleCues(input as readonly Caption[], o)) as readonly SubtitleCue[];
	return serializeSrt({
		lines: cues.map((c) => [
			{text: c.lines.join('\n'), startMs: Math.max(0, c.startMs), endMs: Math.max(0, c.endMs), timestampMs: null, confidence: null},
		]),
	});
};
