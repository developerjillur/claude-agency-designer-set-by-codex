// Types, fonts, easing and geometry shared by the edit renderer. Every value comes from the EDL that nvc.py compiles;
// nothing here keeps state between frames, so any frame renders the same on its own.
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadHind } from "@remotion/google-fonts/HindSiliguri";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { Easing, interpolate, staticFile } from "remotion";

const montserrat = loadMontserrat("normal", { weights: ["600", "700", "800", "900"], subsets: ["latin"] });
const inter = loadInter("normal", { weights: ["400", "500", "600", "700", "800"], subsets: ["latin"] });
const hind = loadHind("normal", { weights: ["500", "600", "700"], subsets: ["bengali", "latin"] });

export const FONTS: Record<string, string> = {
  Montserrat: montserrat.fontFamily,
  Inter: inter.fontFamily,
  HindSiliguri: hind.fontFamily,
};

export const font = (name?: string): string => {
  if (!name) return FONTS.Inter;
  return FONTS[name] ?? name;
};

export type Box = { x: number; y: number; w: number; h: number };
export type Band = { y: number; h: number };
export type Layout = "camFull" | "screenFull" | "screenPip" | "split" | "stack" | "brollFull" | "voiceOnly";
export type Placement = { source: string; trimBefore: number } | null;
export type Transition = { type: "cut" | "zoom" | "whip" | "dip" | "flash"; frames: number };
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
  progress: boolean;
};

export const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

// A 1080p frame is the design unit; every size scales with the shorter side.
export const unit = (width: number, height: number): number => Math.min(width, height) / 1080;

export const isBengali = (text: string): boolean => /[ঀ-৿]/.test(text);

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

// Numbers inside a label ("62%", "$1,200", "3.5x"), for count-up animations that settle on the exact text.
export const splitNumber = (text: string): { pre: string; num: number | null; post: string; decimals: number; comma: boolean } => {
  const m = String(text).match(/^(\D*?)(\d[\d,]*(?:\.\d+)?)(.*)$/);
  if (!m) return { pre: String(text), num: null, post: "", decimals: 0, comma: false };
  const raw = m[2];
  const decimals = raw.includes(".") ? raw.split(".")[1].length : 0;
  return { pre: m[1], num: parseFloat(raw.replace(/,/g, "")), post: m[3], decimals, comma: raw.includes(",") };
};

export const formatNumber = (n: number, decimals: number, comma: boolean): string => {
  const fixed = n.toFixed(decimals);
  if (!comma) return fixed;
  const [a, b] = fixed.split(".");
  return a.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (b ? "." + b : "");
};

export const hexToRgba = (hex: string, alpha: number): string => {
  const h = hex.replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const n = parseInt(full.slice(0, 6), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
};
