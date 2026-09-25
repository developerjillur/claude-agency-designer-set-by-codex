// Types, fonts, easing and geometry shared by the edit renderer. Every value comes from the EDL that nvc.py compiles;
// nothing here keeps state between frames, so any frame renders the same on its own.
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadHind } from "@remotion/google-fonts/HindSiliguri";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadPoppins } from "@remotion/google-fonts/Poppins";
import { loadFont as loadAnek } from "@remotion/google-fonts/AnekBangla";
import { Easing, interpolate, random, staticFile } from "remotion";

const montserrat = loadMontserrat("normal", { weights: ["600", "700", "800", "900"], subsets: ["latin"] });
const inter = loadInter("normal", { weights: ["400", "500", "600", "700", "800"], subsets: ["latin"] });
const hind = loadHind("normal", { weights: ["500", "600", "700"], subsets: ["bengali", "latin"] });
const poppins = loadPoppins("normal", { weights: ["500", "600", "700", "800"], subsets: ["latin"] });
const anek = loadAnek("normal", { weights: ["500", "600", "700", "800"], subsets: ["bengali", "latin"] });

export const FONTS: Record<string, string> = {
  Montserrat: montserrat.fontFamily,
  Inter: inter.fontFamily,
  HindSiliguri: hind.fontFamily,
  Poppins: poppins.fontFamily,
  AnekBangla: anek.fontFamily,
};

export const font = (name?: string): string => {
  if (!name) return FONTS.Inter;
  return FONTS[name] ?? name;
};

export type Box = { x: number; y: number; w: number; h: number };
export type Band = { y: number; h: number };
export type Layout = "camFull" | "screenFull" | "screenPip" | "split" | "stack" | "brollFull" | "voiceOnly";
export type Placement = { source: string; trimBefore: number } | null;
export type Transition = { type: "cut" | "zoom" | "whip" | "dip" | "flash" | "slide" | "sweep" | "leak"; frames: number };
export type Pip = { corner: "tl" | "tr" | "bl" | "br"; shape: "circle" | "rounded"; size: number };

export type Clip = {
  id: string;
  from: number;
  durationInFrames: number;
  layout: Layout;
  masterIn: number;
  masterOut: number;
  segment: number;
  beat?: string | null;
  punch: number;
  pip: Pip;
  cam: Placement;
  screen: Placement;
  broll: Placement;
  transitionIn: Transition;
};

export type Overlay = {
  id: string;
  type: string;
  from: number;
  durationInFrames: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  props: Record<string, any>;
  slot?: string;
  enter?: string | null;
  exit?: string | null;
};

export type Zoom = {
  id: string;
  layer: string;
  from: number;
  durationInFrames: number;
  x: number;
  y: number;
  scale: number;
  ease: number;
};

export type Token = { text: string; fromMs: number; toMs: number; emphasis: boolean };
export type Page = { startMs: number; endMs: number; tokens: Token[] };
export type Cue = { startMs: number; endMs: number; lines: string[] };

export type Source = {
  src: string;
  kind: string;
  width?: number | null;
  height?: number | null;
  alpha?: boolean;
  face?: { x: number; y: number } | null;
  duration?: number | null;
};

export type Theme = {
  accent: string;
  text: string;
  ink: string;
  bg: string;
  card: string;
  cardText: string;
  muted: string;
  danger: string;
  display: string;
  body: string;
  captions: string;
  radius: number;
  // the designed scenes: paper and its text, scene colours, the key-word colour, the faceless backdrop, Bangla fonts
  paper?: string;
  paperText?: string;
  palette?: string[];
  highlight?: string;
  backdrop?: "pools" | "paper" | "dusk" | "grid";
  displayBn?: string;
  bodyBn?: string;
  // the Vox look: the marker stroke and bubble key words, the chart cards, the grid lines on the paper
  marker?: string;
  cream?: string;
  grid?: string;
  grain?: number;
  // Vox graphics "on twos": 2 draws every element's motion on every second frame, like hand animation (1: smooth)
  voxStep?: number;
};

export type Edl = {
  schema: string;
  job: string;
  target: string;
  title?: string | null;
  language: string;
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  safe: Box;
  bands: { title: Band; lower: Band; captions: Band };
  theme: Theme;
  base: string;
  audio: string | null;
  sources: Record<string, Source>;
  clips: Clip[];
  overlays: Overlay[];
  zooms: Zoom[];
  captions: {
    style: string;
    burn: boolean;
    fontPx: number;
    band: Band | null;
    pages: Page[];
    cues: Cue[];
    case: string;
  };
  chapters: { t: number; title: string }[];
  // a thin bar along the top (true or "top"), or a thick one along the bottom ("bottom")
  progress: boolean | "top" | "bottom";
  // speech on the output timeline, in frames: the presenter's ring moves only while someone talks
  speech?: [number, number][];
};

export const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

// A 1080p frame is the design unit; every size scales with the shorter side.
export const unit = (width: number, height: number): number => Math.min(width, height) / 1080;

export const isBengali = (text: string): boolean => /[ঀ-৿]/.test(text);

export const displayFont = (theme: Theme, text: string): string =>
  font(isBengali(text) ? theme.displayBn || "AnekBangla" : theme.display);
export const bodyFont = (theme: Theme, text: string): string =>
  font(isBengali(text) ? theme.bodyBn || "HindSiliguri" : theme.body);

export const mediaSrc = (base: string, src: string): string => {
  if (/^(https?:|data:|blob:)/.test(src)) return src;
  return staticFile(base + src);
};

// 0..1 in over `enter` frames, and 1..0 over the last `exit` frames of a `dur`-frame element.
export const inOut = (frame: number, dur: number, enter = 10, exit = 8): { in: number; out: number; v: number } => {
  const a = enter <= 0 ? 1 : interpolate(frame, [0, enter], [0, 1], { ...clampOpts, easing: easeOut });
  const b = exit <= 0 ? 1 : interpolate(frame, [dur - exit, dur], [1, 0], { ...clampOpts, easing: Easing.in(Easing.cubic) });
  return { in: a, out: b, v: Math.min(a, b) };
};

export type Rect = { left: number; top: number; width: number; height: number };

// Cover a box with a source, keeping the focus point (0..1) as close to the centre as the edges allow.
export const coverRect = (
  srcW: number,
  srcH: number,
  boxW: number,
  boxH: number,
  fx = 0.5,
  fy = 0.5,
  scale = 1,
): Rect => {
  const k = Math.max(boxW / srcW, boxH / srcH) * scale;
  const width = srcW * k;
  const height = srcH * k;
  const left = Math.min(0, Math.max(boxW - width, boxW / 2 - fx * width));
  const top = Math.min(0, Math.max(boxH - height, boxH / 2 - fy * height));
  return { left, top, width, height };
};

export const containRect = (srcW: number, srcH: number, boxW: number, boxH: number): Rect => {
  const k = Math.min(boxW / srcW, boxH / srcH);
  const width = srcW * k;
  const height = srcH * k;
  return { left: (boxW - width) / 2, top: (boxH - height) / 2, width, height };
};

// Zoom on a layer at a global frame: eased in and out, the view kept inside the picture.
export const zoomAt = (
  zooms: Zoom[],
  layer: string,
  globalFrame: number,
): { s: number; cx: number; cy: number } => {
  let s = 1;
  let cx = 0.5;
  let cy = 0.5;
  for (const z of zooms) {
    if (z.layer !== layer) continue;
    const local = globalFrame - z.from;
    if (local < 0 || local > z.durationInFrames) continue;
    const e = Math.max(1, Math.min(z.ease, Math.floor(z.durationInFrames / 3)));
    const p = Math.min(
      interpolate(local, [0, e], [0, 1], { ...clampOpts, easing: easeInOut }),
      interpolate(local, [z.durationInFrames - e, z.durationInFrames], [1, 0], { ...clampOpts, easing: easeInOut }),
    );
    s = 1 + (z.scale - 1) * p;
    cx = 0.5 + (z.x - 0.5) * p;
    cy = 0.5 + (z.y - 0.5) * p;
  }
  return { s, cx, cy };
};

// CSS transform for content of size w x h zoomed around (cx, cy), clamped so no edge shows.
export const zoomTransform = (w: number, h: number, z: { s: number; cx: number; cy: number }): string => {
  if (z.s <= 1.0001) return "none";
  const tx = Math.min(0, Math.max(w - w * z.s, w / 2 - z.cx * w * z.s));
  const ty = Math.min(0, Math.max(h - h * z.s, h / 2 - z.cy * h * z.s));
  return `translate(${tx}px, ${ty}px) scale(${z.s})`;
};

const BN_TO_ASCII: Record<string, string> = { "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4", "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9" };
const ASCII_TO_BN = "০১২৩৪৫৬৭৮৯";
export const toAsciiDigits = (s: string): string => s.replace(/[০-৯]/g, (c) => BN_TO_ASCII[c] ?? c);
export const toBengaliDigits = (s: string): string => s.replace(/[0-9]/g, (c) => ASCII_TO_BN[Number(c)]);

// Numbers inside a label ("62%", "$1,200", "3.5x", "৫০০ টাকা"), for count-ups that settle on the exact text.
export const splitNumber = (
  text: string,
): { pre: string; num: number | null; post: string; decimals: number; comma: boolean; bengali: boolean } => {
  const raw0 = String(text);
  const bengali = /[০-৯]/.test(raw0);
  const m = toAsciiDigits(raw0).match(/^(\D*?)(\d[\d,]*(?:\.\d+)?)(.*)$/);
  if (!m) return { pre: raw0, num: null, post: "", decimals: 0, comma: false, bengali };
  const raw = m[2];
  const decimals = raw.includes(".") ? raw.split(".")[1].length : 0;
  const back = (s: string) => (bengali ? toBengaliDigits(s) : s);
  return { pre: back(m[1]), num: parseFloat(raw.replace(/,/g, "")), post: back(m[3]), decimals, comma: raw.includes(","), bengali };
};

export const formatNumber = (n: number, decimals: number, comma: boolean): string => {
  const fixed = n.toFixed(decimals);
  if (!comma) return fixed;
  const [a, b] = fixed.split(".");
  return a.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (b ? "." + b : "");
};

// The label at progress p (0..1) of its count-up; at 1 it is exactly the given text.
export const countUp = (text: string, p: number, from = 0): string => {
  if (p >= 1) return text;
  const n = splitNumber(text);
  if (n.num === null) return text;
  const v = from + (n.num - from) * Math.max(0, p);
  const s = formatNumber(v, n.decimals, n.comma);
  return n.pre + (n.bengali ? toBengaliDigits(s) : s) + n.post;
};

export const hexToRgba = (hex: string, alpha: number): string => {
  const [r, g, b] = rgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const rgb = (hex: string): [number, number, number] => {
  const h = String(hex || "#000000").replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const n = parseInt(full.slice(0, 6), 16) || 0;
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
};

// Mix two colours: t = 0 gives a, t = 1 gives b.
export const mix = (a: string, b: string, t: number): string => {
  const x = rgb(a);
  const y = rgb(b);
  const c = x.map((v, i) => Math.round(v + (y[i] - v) * t));
  return "#" + c.map((v) => v.toString(16).padStart(2, "0")).join("");
};

// Relative luminance (0 dark to 1 light), for choosing text on a colour.
export const luminance = (hex: string): number => {
  const [r, g, b] = rgb(hex).map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

export const onColor = (hex: string, dark = "#1E1B2E", light = "#FFFFFF"): string => (luminance(hex) > 0.45 ? dark : light);

// The scene palette: the theme's own, else the default set (warm orange, violet, deep teal, burnt orange, blue).
export const paletteOf = (t: Theme): string[] =>
  t.palette && t.palette.length ? t.palette : ["#FF7A2F", "#6D3AF0", "#1F5C63", "#E8521A", "#2A6FDB"];
export const paperOf = (t: Theme): string => t.paper || "#F4EEE5";
export const paperTextOf = (t: Theme): string => t.paperText || "#1E1B2E";
export const highlightOf = (t: Theme): string => t.highlight || "#FFC43D";

// Letters as a reader counts them: a Bengali conjunct or a vowel sign is part of one letter.
export const graphemes = (text: string): number => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Seg = (Intl as any).Segmenter;
  if (Seg) {
    let n = 0;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    for (const _ of new Seg("bn", { granularity: "grapheme" }).segment(text)) n++;
    return n;
  }
  return Array.from(text).filter((ch) => !/[ঁ-ঃ়া-্ৗৢৣ‌‍]/.test(ch)).length;
};

// Average advance of a letter as a share of the font size, for the fonts the scenes use at weight 700 to 800
// (Anek Bangla 800 measured in a render: 14.4 em for 20 Bengali letters with their vowel signs).
const PER_CHAR = (text: string, upper: boolean): number => (isBengali(text) ? 0.74 : upper ? 0.72 : 0.58);

// The largest size up to `base` at which every line fits `width` on one line (never under `floor` x base).
export const fitSize = (lines: string[], base: number, width: number, opts: { upper?: boolean; floor?: number; spacing?: number } = {}): number => {
  const floor = opts.floor ?? 0.55;
  let size = base;
  for (const line of lines) {
    const est = graphemes(line) * PER_CHAR(line, !!opts.upper) * base + (opts.spacing ?? 0) * graphemes(line);
    if (est > width) size = Math.min(size, (base * width) / est);
  }
  return Math.round(Math.max(base * floor, size));
};

// Smooth noise in 0..1 from a seed and a position (value noise with a smoothstep), for boiling lines and talking rings.
export const smoothNoise = (seed: string, x: number): number => {
  const i = Math.floor(x);
  const f = x - i;
  const a = random(`${seed}-${i}`);
  const b = random(`${seed}-${i + 1}`);
  const s = f * f * (3 - 2 * f);
  return a + (b - a) * s;
};

// Is anyone speaking at this output frame (with a short tail)?
export const speakingAt = (edl: Edl, frame: number, tail = 3): boolean =>
  (edl.speech || []).some(([a, b]) => frame >= a && frame < b + tail);
