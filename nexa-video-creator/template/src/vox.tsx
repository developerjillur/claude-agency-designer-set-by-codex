// Vox-style explainer beats. One locked paper backdrop with a faint grid and grain, and on it elements that rise,
// pop, slide and drop on the narration's words: cutouts (black and white halftone people with an offset marker
// stroke, colour buildings and objects), clips blended into the collage, bold headlines with highlighter marks, small
// labels, price tags that count and follow what they price, comic speech bubbles, a newspaper page with words
// highlighted as they are said, a chart card that draws itself, a typewriter line typed word by word, hand-drawn
// circles and arrows, and a source line. A beat pushes in slowly with a little parallax between its layers, and every
// element floats once it has landed, so the frame is never still. Every time is a frame from the beat's start, baked
// by the compiler from word ids; nothing depends on the frame before, so frames render in any order.
import React from "react";
import { AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Video } from "@remotion/media";
import { loadFont as loadMerriweather } from "@remotion/google-fonts/Merriweather";
import { loadFont as loadBangers } from "@remotion/google-fonts/Bangers";
import { loadFont as loadSpecialElite } from "@remotion/google-fonts/SpecialElite";
import { Edl, Overlay, Theme, bodyFont, clampOpts, countUp, displayFont, easeInOut, easeOut, fitSize, font, graphemes, isBengali, mediaSrc, unit } from "./lib";

const SERIF = loadMerriweather("normal", { weights: ["400", "700", "900"], subsets: ["latin", "latin-ext"] }).fontFamily;
loadMerriweather("italic", { weights: ["400"], subsets: ["latin", "latin-ext"] });
const COMIC = loadBangers("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] }).fontFamily;
const TYPED = loadSpecialElite("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Props = Record<string, any>;

export const VOX_EXIT = 12; // frames an element takes to leave; a beat joined to the next runs this long under it

type Move = { at: number; x?: number; y?: number; scale?: number; rotate?: number; frames?: number };

export type VoxElement = {
  id: string;
  kind: string;
  layer?: string;
  at: number;
  out?: number | null;
  x: number;
  y: number;
  anchor?: string;
  w?: number;
  rotate?: number;
  scale?: number;
  enter?: string;
  exit?: string;
  moves?: Move[];
  float?: boolean;
} & Props;

// Nearer layers move more when the beat pushes in; text moves least, so it stays easy to read.
const LAYER_ORDER: Record<string, number> = { back: 0, mid: 1, fore: 2, text: 3 };
const LAYER_PUSH: Record<string, number> = { back: 0.5, mid: 0.8, fore: 1, text: 0.35 };

// Where an element's own box sits around its point (x, y), as CSS translate percentages.
const ANCHOR: Record<string, [number, number]> = {
  bottom: [-50, -100],
  top: [-50, 0],
  center: [-50, -50],
  left: [0, -50],
  right: [-100, -50],
  "bottom-left": [0, -100],
  "bottom-right": [-100, -100],
  "top-left": [0, 0],
  "top-right": [-100, 0],
};

// The look, measured on the reference (warm grey paper #D3D1CB with light grid lines every ~106 px at 1080p, an
// orange #FF8900 accent, the red-orange marker #E04329, an amber highlighter, cream chart cards).
export const voxColors = (t: Theme) => ({
  paper: t.paper || "#D9D7D1",
  ink: t.paperText || "#161616",
  accent: t.accent || "#FF8900",
  marker: t.marker || "#E04329",
  highlight: t.highlight || "#F4B41A",
  cream: t.cream || "#F9F5ED",
  grid: t.grid || "rgba(250, 248, 242, 0.62)",
  grey: "#A3A09A",
  soft: "#77746E",
});

const norm = (w: string): string => w.toLowerCase().replace(/[^\p{L}\p{N}\p{M}$%¥€£৳.,+-]/gu, "").replace(/[.,]+$/, "");

const linesOf = (el: Props, key = "lines", fallback = "text"): string[] => {
  const v = el[key] ?? el[fallback];
  if (Array.isArray(v)) return v.map(String).filter((x) => x.trim());
  return v ? [String(v)] : [];
};

const wordSet = (v: unknown): Set<string> => {
  const list = Array.isArray(v) ? v.map(String) : String(v || "").split(/\s+/);
  return new Set(list.map(norm).filter(Boolean));
};

// ---------------------------------------------------------------- time and place

// Where an element's point is at this frame (px, before the entrance and exit): its place, eased from one move to
// the next.
const placeAt = (el: VoxElement, frame: number, W: number, H: number) => {
  let x = el.x;
  let y = el.y;
  let scale = el.scale ?? 1;
  let rotate = el.rotate ?? 0;
  for (const m of el.moves || []) {
    const p = interpolate(frame, [m.at, m.at + (m.frames ?? 18)], [0, 1], { ...clampOpts, easing: easeInOut });
    if (p <= 0) break;
    if (m.x !== undefined) x += (m.x - x) * p;
    if (m.y !== undefined) y += (m.y - y) * p;
    if (m.scale !== undefined) scale += (m.scale - scale) * p;
    if (m.rotate !== undefined) rotate += (m.rotate - rotate) * p;
  }
  return { x: x * W, y: y * H, scale, rotate };
};

type Motion = { visible: boolean; dx: number; dy: number; s: number; o: number; r: number; clip: number; landed: number };

// How far into its entrance and exit an element is, and the offsets, scale, turn and opacity that gives it.
const motionAt = (el: VoxElement, frame: number, fps: number, W: number, H: number, u: number): Motion => {
  const local = frame - el.at;
  const m: Motion = { visible: false, dx: 0, dy: 0, s: 1, o: 1, r: 0, clip: 1, landed: 0 };
  if (local < 0) return m;
  m.visible = true;
  const enter = el.enter || "pop";
  const sp = (damping: number, stiffness: number, mass = 1) => spring({ frame: local, fps, config: { damping, stiffness, mass } });
  const grounded = (el.anchor || "").startsWith("bottom") && el.y > 0.8;
  if (enter === "rise") {
    const p = sp(22, 110, 0.9);
    // things standing on the bottom edge come up from under it; the rest rise a little and fade in
    m.dy = (1 - p) * (grounded ? H * 0.75 : H * 0.2);
    m.o = grounded ? 1 : interpolate(local, [0, 6], [0, 1], clampOpts);
    m.landed = p;
  } else if (enter === "pop") {
    const p = sp(15, 190, 0.7);
    m.s = 0.5 + 0.5 * p;
    m.o = interpolate(local, [0, 4], [0, 1], clampOpts);
    m.r = (1 - p) * (el.kind === "bubble" ? -8 : 0);
    m.landed = p;
  } else if (enter === "slideLeft" || enter === "slideRight") {
    const p = sp(24, 100);
    m.dx = (1 - p) * W * 0.75 * (enter === "slideLeft" ? 1 : -1);
    m.landed = p;
  } else if (enter === "drop") {
    const p = sp(16, 130, 0.8);
    m.dy = -(1 - p) * H * 0.7;
    m.landed = p;
  } else if (enter === "wipe") {
    m.clip = interpolate(local, [0, 12], [0, 1], { ...clampOpts, easing: easeOut });
    m.dx = (1 - m.clip) * -24 * u;
    m.landed = m.clip;
  } else if (enter === "fade") {
    m.o = interpolate(local, [0, 10], [0, 1], clampOpts);
    m.dy = (1 - m.o) * 16 * u;
    m.landed = m.o;
  } else {
    m.landed = 1;
  }
  const out = el.out;
  if (out !== null && out !== undefined && frame >= out) {
    const exit = el.exit || "drop";
    if (exit === "cut") return { ...m, visible: false };
    const q = interpolate(frame, [out, out + VOX_EXIT], [0, 1], { ...clampOpts, easing: Easing.in(Easing.cubic) });
    if (q >= 1) return { ...m, visible: false };
    if (exit === "drop") {
      m.dy += q * H * 0.9;
      m.o *= interpolate(q, [0.6, 1], [1, 0], clampOpts);
    } else if (exit === "fade") {
      m.o *= 1 - q;
    } else if (exit === "slideLeft" || exit === "slideRight") {
      m.dx += q * W * 0.8 * (exit === "slideLeft" ? -1 : 1);
    } else if (exit === "pop") {
      m.s *= 1 - 0.5 * q;
      m.o *= 1 - q;
    } else if (exit === "rise") {
      m.dy -= q * H * 0.8;
      m.o *= interpolate(q, [0.6, 1], [1, 0], clampOpts);
    }
  }
  return m;
};

// A steady drift while an element is on screen (a ship sailing across, a page sliding on the desk), in shares of the
// frame per second.
const driftAt = (el: VoxElement, frame: number, fps: number, W: number, H: number) => {
  const d = el.drift as { x?: number; y?: number } | undefined;
  if (!d) return { x: 0, y: 0 };
  const s = Math.max(0, frame - el.at) / fps;
  return { x: (d.x ?? 0) * W * s, y: (d.y ?? 0) * H * s };
};

// A little life once an element has landed: a slow float, out of phase with its neighbours.
const floatAt = (el: VoxElement, frame: number, u: number): { y: number; r: number } => {
  if (el.float === false) return { y: 0, r: 0 };
  const seed = random(`vox-float-${el.id}`) * Math.PI * 2;
  const k = el.kind === "bubble" ? 1.4 : el.kind === "cutout" ? 0.8 : 1;
  return { y: Math.sin(frame / 36 + seed) * 5 * u * k, r: el.kind === "bubble" ? Math.sin(frame / 44 + seed) * 0.8 : 0 };
};

// ---------------------------------------------------------------- pictures

const shadowOf = (kind: string | undefined, u: number): string | undefined => {
  if (kind === "soft") return `drop-shadow(0 ${10 * u}px ${14 * u}px rgba(40, 30, 20, 0.28))`;
  if (kind === "hard") return `drop-shadow(${8 * u}px ${10 * u}px 0 rgba(30, 20, 10, 0.3))`;
  return undefined;
};

// A cut-out picture (styled by `nvc.py cutout`: halftone, marker stroke), with a soft shadow or a floating one.
const Cutout: React.FC<{ edl: Edl; el: VoxElement; W: number; u: number }> = ({ edl, el, W, u }) => {
  const src = edl.sources[el.source];
  if (!src) return null;
  const w = (el.w ?? 0.3) * W;
  const h = src.width && src.height ? (w * src.height) / src.width : w;
  const ground = el.shadow === "ground";
  return (
    <div style={{ position: "relative", width: w, height: h }}>
      {ground ? (
        <div
          style={{
            position: "absolute",
            left: "8%",
            right: "8%",
            bottom: -h * 0.22,
            height: Math.max(18 * u, h * 0.12),
            borderRadius: "50%",
            background: "radial-gradient(ellipse at 50% 50%, rgba(40, 30, 20, 0.34) 0%, rgba(40, 30, 20, 0) 70%)",
            filter: `blur(${6 * u}px)`,
          }}
        />
      ) : null}
      <Img
        src={mediaSrc(edl.base, src.src)}
        style={{ position: "absolute", inset: 0, width: w, height: h, filter: shadowOf(el.shadow, u), transform: el.flip ? "scaleX(-1)" : undefined }}
      />
    </div>
  );
};

// A photograph as a print: a white border, a shadow, a typed caption.
const Card: React.FC<{ edl: Edl; el: VoxElement; W: number; u: number }> = ({ edl, el, W, u }) => {
  const src = edl.sources[el.source];
  if (!src) return null;
  const w = (el.w ?? 0.34) * W;
  const h = src.width && src.height ? (w * src.height) / src.width : w * 0.66;
  const still = /\.(png|jpe?g|webp|gif|bmp)$/i.test(src.src);
  const b = 14 * u;
  const style: React.CSSProperties = { width: w, height: h, display: "block", objectFit: "cover", filter: el.bw ? "grayscale(1) contrast(1.08)" : undefined };
  return (
    <div style={{ padding: b, paddingBottom: el.caption ? b * 0.7 : b, backgroundColor: "#FBFAF6", boxShadow: `0 ${18 * u}px ${40 * u}px rgba(30, 20, 10, 0.3)` }}>
      {still ? (
        <Img src={mediaSrc(edl.base, src.src)} style={style} />
      ) : (
        <Video src={mediaSrc(edl.base, src.src)} trimBefore={Number(el.trimBefore || 0)} muted loop objectFit="cover" style={style} />
      )}
      {el.caption ? (
        <div style={{ marginTop: 10 * u, fontFamily: isBengali(String(el.caption)) ? font("HindSiliguri") : TYPED, fontSize: 24 * u, color: "#34322E", maxWidth: w }}>
          {String(el.caption)}
        </div>
      ) : null}
    </div>
  );
};

// Edges faded out, so a clip melts into the paper (an ocean band with a soft top, a smoke plume).
const featherMask = (f: unknown): string | undefined => {
  if (!f) return undefined;
  const e = typeof f === "number" ? { top: f, bottom: f, left: f, right: f } : (f as Record<string, number>);
  const pct = (v?: number) => `${Math.round(Math.max(0, Math.min(0.5, v || 0)) * 100)}%`;
  const v = `linear-gradient(to bottom, transparent 0%, #000 ${pct(e.top)}, #000 calc(100% - ${pct(e.bottom)}), transparent 100%)`;
  const h = `linear-gradient(to right, transparent 0%, #000 ${pct(e.left)}, #000 calc(100% - ${pct(e.right)}), transparent 100%)`;
  return `${v}, ${h}`;
};

// A clip or picture in the collage: a band of sea, fire over a bill (blended as screen), smoke, a map.
const Clip: React.FC<{ edl: Edl; el: VoxElement; W: number; H: number }> = ({ edl, el, W, H }) => {
  const src = edl.sources[el.source];
  if (!src) return null;
  const w = (el.w ?? 1) * W;
  const h = el.h !== undefined ? Number(el.h) * H : src.width && src.height ? (w * src.height) / src.width : w * 0.5625;
  const mask = featherMask(el.feather);
  const box: React.CSSProperties = {
    width: w,
    height: h,
    overflow: "hidden",
    WebkitMaskImage: mask,
    maskImage: mask,
    WebkitMaskComposite: mask ? "source-in" : undefined,
    maskComposite: mask ? "intersect" : undefined,
  };
  const media: React.CSSProperties = { width: "100%", height: "100%", display: "block", objectFit: "cover", filter: el.bw ? "grayscale(1)" : undefined };
  const url = mediaSrc(edl.base, src.src);
  let body: React.ReactNode;
  if (/\.(png|jpe?g|webp|gif|bmp)$/i.test(src.src)) body = <Img src={url} style={media} />;
  else if (src.alpha) body = <OffthreadVideo src={url} trimBefore={Number(el.trimBefore || 0)} muted transparent style={media} />;
  else body = <Video src={url} trimBefore={Number(el.trimBefore || 0)} muted loop objectFit="cover" style={media} />;
  return <div style={box}>{body}</div>;
};

// ---------------------------------------------------------------- words

// A bold headline, revealed left to right when it wipes in; key words take the accent, marked words get a
// highlighter band when they are said, and a number can count up to its value.
const Headline: React.FC<{ t: Theme; el: VoxElement; W: number; u: number; clip: number; frame: number }> = ({ t, el, W, u, clip, frame }) => {
  const c = voxColors(t);
  const lines = linesOf(el);
  const text = lines.join(" ");
  const bn = isBengali(text);
  const caps = el.caps !== false && !bn;
  const size = fitSize(lines, (el.size ?? 104) * u, (el.w ?? 0.8) * W, { upper: caps, floor: 0.45 });
  const keys = wordSet(el.highlight);
  const marks = wordSet(el.mark);
  const mp = el.markAt !== undefined ? interpolate(frame, [el.markAt, el.markAt + 12], [0, 1], { ...clampOpts, easing: easeOut }) : 0;
  const count = el.count ? interpolate(frame, [el.at + 4, el.land ?? el.at + 40], [0, 1], { ...clampOpts, easing: Easing.out(Easing.cubic) }) : 1;
  return (
    <div
      style={{
        fontFamily: displayFont(t, text),
        fontWeight: 900,
        fontSize: size,
        lineHeight: bn ? 1.28 : 1.02,
        letterSpacing: bn ? 0 : "-0.015em",
        textTransform: caps ? "uppercase" : "none",
        color: el.color || c.ink,
        textAlign: (el.align as React.CSSProperties["textAlign"]) || "center",
        whiteSpace: "nowrap",
        textShadow: el.shadow === false ? undefined : `0 ${5 * u}px ${14 * u}px rgba(30, 20, 10, 0.18)`,
        clipPath: clip < 1 ? `inset(-30% ${(1 - clip) * 100}% -30% -5%)` : undefined,
      }}
    >
      {lines.map((line, i) => (
        <div key={i}>
          {line.split(" ").map((w, k, all) => {
            const key = norm(w);
            const marked = marks.has(key);
            const next = k + 1 < all.length && marks.has(norm(all[k + 1]));
            return (
              <span key={k} style={{ position: "relative", display: "inline-block", paddingRight: k + 1 < all.length ? "0.24em" : 0 }}>
                {marked && mp > 0 ? (
                  <span
                    style={{
                      position: "absolute",
                      left: "-0.06em",
                      right: next ? 0 : "0.14em",
                      top: "16%",
                      bottom: "2%",
                      backgroundColor: c.highlight,
                      transformOrigin: "0% 50%",
                      transform: `scaleX(${mp}) rotate(-0.6deg)`,
                      zIndex: 0,
                    }}
                  />
                ) : null}
                <span style={{ position: "relative", color: keys.has(key) ? c.accent : undefined }}>{count < 1 && /\d/.test(w) ? countUp(w, count) : w}</span>
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// A small line of text: a figure's caption, a quantity, a place.
const Label: React.FC<{ t: Theme; el: VoxElement; u: number }> = ({ t, el, u }) => {
  const c = voxColors(t);
  const text = String(el.text || "");
  const bn = isBengali(text);
  const caps = !!el.caps && !bn;
  const style: React.CSSProperties = {
    fontFamily: bn ? displayFont(t, text) : font(el.font || "Inter"),
    fontWeight: el.weight ?? 700,
    fontSize: (el.size ?? 46) * u * (bn ? 1.04 : 1),
    lineHeight: bn ? 1.3 : 1.15,
    color: el.color || "#232323",
    whiteSpace: "nowrap",
    letterSpacing: caps ? "0.08em" : "-0.01em",
    textTransform: caps ? "uppercase" : "none",
  };
  if (el.box) {
    Object.assign(style, { backgroundColor: "#FBFAF6", padding: `${10 * u}px ${18 * u}px`, borderRadius: 10 * u, boxShadow: `0 ${8 * u}px ${20 * u}px rgba(30, 20, 10, 0.2)` });
  } else if (el.shadow !== false) {
    style.textShadow = `0 ${3 * u}px ${10 * u}px rgba(30, 20, 10, 0.16)`;
  }
  return <div style={style}>{el.accent ? <span style={{ color: c.accent }}>{text}</span> : text}</div>;
};

// A source line at the bottom-left, the way explainers cite their numbers.
const Credit: React.FC<{ t: Theme; el: VoxElement; u: number }> = ({ t, el, u }) => {
  const c = voxColors(t);
  const text = String(el.text || "");
  const bn = isBengali(text);
  return (
    <div
      style={{
        fontFamily: bn ? bodyFont(t, text) : font("Inter"),
        fontWeight: 700,
        fontSize: (el.size ?? 18) * u * (bn ? 1.1 : 1),
        letterSpacing: bn ? 0 : "0.1em",
        textTransform: bn ? "none" : "uppercase",
        color: c.soft,
        whiteSpace: "nowrap",
      }}
    >
      {text}
    </div>
  );
};

// ---------------------------------------------------------------- icons

const Icon: React.FC<{ name: string; color: string; size: number }> = ({ name, color, size }) => {
  const shade = "rgba(0, 0, 0, 0.22)";
  if (name === "barrel") {
    return (
      <svg width={size * 0.66} height={size} viewBox="0 0 40 60" style={{ display: "block" }}>
        <defs>
          <linearGradient id="vox-barrel" x1="0" x2="1">
            <stop offset="0" stopColor={color} stopOpacity="1" />
            <stop offset="0.5" stopColor="#FFFFFF" stopOpacity="0.18" />
            <stop offset="1" stopColor="#000000" stopOpacity="0.16" />
          </linearGradient>
        </defs>
        <rect x="1" y="1" width="38" height="58" rx="3" fill={color} />
        <rect x="1" y="1" width="38" height="58" rx="3" fill="url(#vox-barrel)" />
        <rect x="1" y="14" width="38" height="2.5" fill={shade} />
        <rect x="1" y="43.5" width="38" height="2.5" fill={shade} />
        <circle cx="20" cy="30" r="7.5" fill="#FFFFFF" />
        <path d="M20 24.5 C 22.6 28 24 30.2 24 32 A 4 4 0 0 1 16 32 C 16 30.2 17.4 28 20 24.5 Z" fill="#161616" />
      </svg>
    );
  }
  if (name === "up" || name === "down") {
    return (
      <svg width={size * 0.8} height={size} viewBox="0 0 40 50" style={{ display: "block", transform: name === "down" ? "rotate(180deg)" : undefined }}>
        <path d="M20 2 L38 26 H27 V48 H13 V26 H2 Z" fill={color} />
      </svg>
    );
  }
  if (name === "pin") {
    return (
      <svg width={size * 0.72} height={size} viewBox="0 0 36 50" style={{ display: "block" }}>
        <path d="M18 2 C8 2 2 10 2 18 C2 30 18 48 18 48 C18 48 34 30 34 18 C34 10 28 2 18 2 Z" fill={color} />
        <circle cx="18" cy="18" r="6" fill="#FFFFFF" />
      </svg>
    );
  }
  if (name === "coin" || name === "dollar" || name === "taka") {
    const sign = name === "taka" ? "৳" : "$";
    return (
      <svg width={size} height={size} viewBox="0 0 50 50" style={{ display: "block" }}>
        <circle cx="25" cy="25" r="23" fill={color} />
        <circle cx="25" cy="25" r="18" fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth="2" />
        <text x="25" y="33" textAnchor="middle" fontSize="24" fontWeight="900" fill="#FFFFFF" fontFamily="Arial, sans-serif">
          {sign}
        </text>
      </svg>
    );
  }
  if (name === "warning") {
    return (
      <svg width={size} height={size * 0.9} viewBox="0 0 50 45" style={{ display: "block" }}>
        <path d="M25 2 L48 43 H2 Z" fill={color} stroke="#161616" strokeWidth="2.5" strokeLinejoin="round" />
        <rect x="23" y="14" width="4" height="16" rx="2" fill="#161616" />
        <circle cx="25" cy="36" r="2.6" fill="#161616" />
      </svg>
    );
  }
  if (name === "check" || name === "cross") {
    return (
      <svg width={size} height={size} viewBox="0 0 50 50" style={{ display: "block" }}>
        <circle cx="25" cy="25" r="23" fill={color} />
        {name === "check" ? (
          <path d="M14 26 L22 34 L37 17" fill="none" stroke="#FFFFFF" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        ) : (
          <path d="M16 16 L34 34 M34 16 L16 34" fill="none" stroke="#FFFFFF" strokeWidth="6" strokeLinecap="round" />
        )}
      </svg>
    );
  }
  return null;
};

const IconEl: React.FC<{ t: Theme; el: VoxElement; u: number }> = ({ t, el, u }) => {
  const c = voxColors(t);
  return <Icon name={String(el.icon || el.name || "pin")} color={el.color || c.accent} size={(el.size ?? 90) * u} />;
};

// A price or quantity tag: an icon, a number that counts to its value and lands with a small bump, a unit under it.
const Tag: React.FC<{ t: Theme; el: VoxElement; u: number; frame: number }> = ({ t, el, u, frame }) => {
  const c = voxColors(t);
  const value = String(el.value ?? "");
  const unitText = el.unit ? String(el.unit) : "";
  const land = el.land ?? el.at + 45;
  const p = interpolate(frame, [el.at + 6, land], [0, 1], { ...clampOpts, easing: Easing.out(Easing.cubic) });
  const bump = interpolate(frame, [land, land + 4, land + 12], [1, 1.1, 1], clampOpts);
  const size = (el.size ?? 128) * u;
  const bn = isBengali(value + unitText);
  const icon = el.icon && el.icon !== "none" ? String(el.icon) : null;
  const shadow = `0 ${6 * u}px ${14 * u}px rgba(30, 20, 10, 0.22)`;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22 * u }}>
        {icon ? (
          <div style={{ filter: `drop-shadow(0 ${6 * u}px ${10 * u}px rgba(30, 20, 10, 0.25))` }}>
            <Icon name={icon} color={el.color || c.accent} size={size * 1.05} />
          </div>
        ) : null}
        <div
          style={{
            fontFamily: displayFont(t, value),
            fontWeight: 900,
            fontSize: size,
            lineHeight: 1,
            color: el.valueColor || c.ink,
            letterSpacing: bn ? 0 : "-0.04em",
            fontVariantNumeric: "tabular-nums",
            transformOrigin: "30% 60%",
            transform: `scale(${bump})`,
            whiteSpace: "nowrap",
            textShadow: shadow,
          }}
        >
          {countUp(value, p, Number(el.from ?? 0))}
        </div>
      </div>
      {unitText ? (
        <div
          style={{
            marginTop: 14 * u,
            fontFamily: displayFont(t, unitText),
            fontWeight: 800,
            fontSize: size * 0.3,
            letterSpacing: bn ? 0 : "0.12em",
            textTransform: bn ? "none" : "uppercase",
            color: "#1E1E1E",
            whiteSpace: "nowrap",
            textShadow: `0 ${3 * u}px ${8 * u}px rgba(30, 20, 10, 0.16)`,
          }}
        >
          {unitText}
        </div>
      ) : null}
    </div>
  );
};

// ---------------------------------------------------------------- comic speech bubble

const TAIL_ANGLE: Record<string, number> = { right: 12, "down-right": 58, down: 90, "down-left": 122, left: 168, "up-left": 235, up: 270, "up-right": 305 };

// A hand-lettered line in a round bubble with a curved tail towards the speaker; key words in the marker colour.
const Bubble: React.FC<{ t: Theme; el: VoxElement; u: number }> = ({ t, el, u }) => {
  const c = voxColors(t);
  const lines = linesOf(el);
  const text = lines.join(" ");
  const bn = isBengali(text);
  const keys = wordSet(el.highlight);
  const size = (el.size ?? 54) * u * (bn ? 0.82 : 1);
  const per = bn ? 0.72 : 0.47; // Bangers is narrow
  const tw = Math.max(...lines.map((l) => graphemes(l))) * per * size;
  const th = lines.length * size * (bn ? 1.3 : 1.02);
  const rx = tw * 0.72 + 30 * u;
  const ry = th * 0.72 + 26 * u;
  const angle = typeof el.tail === "number" ? el.tail : TAIL_ANGLE[String(el.tail || "down-right")] ?? 58;
  const a = (angle * Math.PI) / 180;
  const spread = 0.2;
  const pad = 70 * u;
  const cx = rx + pad;
  const cy = ry + pad;
  const pt = (ang: number, kx = 1, ky = 1) => [cx + rx * kx * Math.cos(ang), cy + ry * ky * Math.sin(ang)];
  const [x1, y1] = pt(a + spread);
  const [x2, y2] = pt(a - spread);
  const bend = angle > 90 && angle < 270 ? -0.35 : 0.35;
  const [tx, ty] = pt(a + bend * 0.5, 1.42, 1.62);
  const [c1x, c1y] = pt(a - spread * 0.2, 1.18, 1.25);
  const [c2x, c2y] = pt(a + spread * 0.9, 1.1, 1.2);
  const path = `M ${x1} ${y1} A ${rx} ${ry} 0 1 1 ${x2} ${y2} Q ${c1x} ${c1y} ${tx} ${ty} Q ${c2x} ${c2y} ${x1} ${y1} Z`;
  const stroke = 4.5 * u;
  const [sx1, sy1] = pt(-1.25, 0.78, 0.72);
  const [sx2, sy2] = pt(-0.55, 0.8, 0.74);
  return (
    <div style={{ position: "relative", width: 2 * cx, height: 2 * cy, margin: -pad }}>
      <svg width={2 * cx} height={2 * cy} style={{ position: "absolute", inset: 0, overflow: "visible", filter: `drop-shadow(0 ${6 * u}px ${10 * u}px rgba(30, 20, 10, 0.2))` }}>
        <path d={path} fill={el.fill || "#F4F1EA"} stroke="#2A2826" strokeWidth={stroke} strokeLinejoin="round" />
        <path d={`M ${sx1} ${sy1} Q ${cx + rx * 0.72} ${cy - ry * 0.86} ${sx2} ${sy2}`} fill="none" stroke="#2A2826" strokeWidth={stroke * 0.8} strokeLinecap="round" />
      </svg>
      <div
        style={{
          position: "absolute",
          left: cx - tw / 2 - 20 * u,
          top: cy - th / 2,
          width: tw + 40 * u,
          fontFamily: bn ? displayFont(t, text) : COMIC,
          fontWeight: bn ? 800 : 400,
          fontSize: size,
          lineHeight: bn ? 1.3 : 1.02,
          letterSpacing: bn ? 0 : "0.01em",
          color: "#1B1A18",
          textAlign: "center",
          whiteSpace: "nowrap",
          textTransform: bn ? "none" : "uppercase",
        }}
      >
        {lines.map((line, i) => (
          <div key={i}>
            {line.split(" ").map((w, k, all) => (
              <span key={k} style={{ color: keys.has(norm(w)) ? c.marker : undefined }}>
                {w}
                {k + 1 < all.length ? " " : ""}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- newspaper

// A newspaper page tilted on the desk: masthead, date line, section rules, a headline whose marked words get a
// highlighter stroke when they are said, a deck, a byline, and three columns (text, grey lines, a photo).
const Newspaper: React.FC<{ edl: Edl; t: Theme; el: VoxElement; W: number; u: number; frame: number }> = ({ edl, t, el, W, u, frame }) => {
  const c = voxColors(t);
  const w = (el.w ?? 0.64) * W;
  const ink = "#151515";
  const inner = w - 2 * 50 * u;
  const head = linesOf(el, "headline", "title");
  const marks: { text: string; at: number }[] = Array.isArray(el.marks) ? el.marks : [];
  // the words each mark covers, in reading order over the whole headline
  const flat = head.flatMap((line, li) => line.split(" ").map((word, wi) => ({ word, li, wi })));
  const markOf: Record<string, { at: number; k: number; n: number; last: boolean }> = {};
  for (const m of marks) {
    const want = String(m.text || "").split(/\s+/).map(norm).filter(Boolean);
    if (!want.length) continue;
    for (let i = 0; i + want.length <= flat.length; i++) {
      if (want.every((x, k) => norm(flat[i + k].word) === x)) {
        want.forEach((_, k) => {
          const f = flat[i + k];
          markOf[`${f.li}-${f.wi}`] = { at: m.at, k, n: want.length, last: k === want.length - 1 || flat[i + k + 1].li !== f.li };
        });
        break;
      }
    }
  }
  const headSize = fitSize(head, 70 * u, inner * 0.86);
  const photo = el.source ? edl.sources[el.source] : null;
  const smallCaps: React.CSSProperties = { fontFamily: SERIF, fontWeight: 700, fontSize: 15 * u, letterSpacing: "0.14em", textTransform: "uppercase", color: "#3A3834" };
  const rows = (n: number, seed: string) =>
    Array.from({ length: n }).map((_, i) => (
      <div key={i} style={{ height: 7 * u, marginBottom: 11 * u, width: `${i === n - 1 ? 50 + random(`${el.id}${seed}${i}`) * 25 : 86 + random(`${el.id}${seed}${i}`) * 14}%`, backgroundColor: "#D9D5CC", borderRadius: 2 * u }} />
    ));
  const tilt = el.tilt === false ? "none" : "perspective(2400px) rotateX(9deg) rotateY(-8deg) rotateZ(-1.6deg)";
  return (
    <div style={{ width: w, transform: tilt, transformOrigin: "50% 50%" }}>
      <div style={{ width: w, backgroundColor: "#FAF8F2", padding: `${40 * u}px ${50 * u}px ${46 * u}px`, boxShadow: `0 ${34 * u}px ${70 * u}px rgba(30, 20, 10, 0.32)`, color: ink, boxSizing: "border-box" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div style={{ ...smallCaps, fontWeight: 400, width: "25%", lineHeight: 1.35 }}>{linesOf(el, "left", "est").map((x, i) => <div key={i}>{x}</div>)}</div>
          <div style={{ fontFamily: SERIF, fontWeight: 900, fontSize: fitSize([String(el.masthead || "")], 74 * u, inner * 0.46), lineHeight: 1, whiteSpace: "nowrap", letterSpacing: "-0.01em" }}>{String(el.masthead || "")}</div>
          <div style={{ ...smallCaps, width: "25%", textAlign: "right", lineHeight: 1.35 }}>{linesOf(el, "right", "date").map((x, i) => <div key={i}>{x}</div>)}</div>
        </div>
        <div style={{ borderTop: `${2.5 * u}px solid ${ink}`, marginTop: 14 * u }} />
        <div style={{ borderTop: `${1 * u}px solid ${ink}`, marginTop: 4 * u }} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: `${10 * u}px 0 ${6 * u}px` }}>
          <div style={smallCaps}>{String(el.section || "")}</div>
          <div style={{ ...smallCaps, fontWeight: 400, fontSize: 14 * u }}>{String(el.kicker || "")}</div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 16 * u, letterSpacing: "0.08em", color: "#3A3834" }}>{String(el.corner || "")}</div>
        </div>
        <div style={{ borderTop: `${1 * u}px solid ${ink}` }} />
        <div style={{ fontFamily: SERIF, fontWeight: 900, fontSize: headSize, lineHeight: 1.14, textAlign: "center", margin: `${26 * u}px 0 ${14 * u}px`, letterSpacing: "-0.01em" }}>
          {head.map((line, li) => (
            <div key={li}>
              {line.split(" ").map((word, wi, all) => {
                const m = markOf[`${li}-${wi}`];
                const p = m ? interpolate(frame, [m.at + (m.k * 12) / m.n, m.at + ((m.k + 1) * 12) / m.n], [0, 1], clampOpts) : 0;
                return (
                  <span key={wi} style={{ position: "relative", display: "inline-block", paddingRight: wi + 1 < all.length ? "0.24em" : 0 }}>
                    {p > 0 ? (
                      <span
                        style={{
                          position: "absolute",
                          left: m && m.k === 0 ? "-0.08em" : 0,
                          right: m && m.last ? (wi + 1 < all.length ? "0.16em" : "-0.08em") : 0,
                          top: "14%",
                          bottom: "-2%",
                          backgroundColor: c.highlight,
                          transformOrigin: "0% 50%",
                          transform: `scaleX(${p})`,
                          borderRadius: 2 * u,
                        }}
                      />
                    ) : null}
                    <span style={{ position: "relative" }}>{word}</span>
                  </span>
                );
              })}
            </div>
          ))}
        </div>
        {el.deck ? (
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 25 * u, textAlign: "center", color: "#2E2C29", margin: `0 0 ${10 * u}px` }}>{String(el.deck)}</div>
        ) : null}
        {el.byline ? <div style={{ ...smallCaps, fontWeight: 400, textAlign: "center", marginBottom: 16 * u }}>{String(el.byline)}</div> : null}
        <div style={{ borderTop: `${1.5 * u}px solid ${ink}`, marginBottom: 20 * u }} />
        <div style={{ display: "flex", gap: 26 * u }}>
          <div style={{ flex: 1, borderRight: `${1 * u}px solid #CFCAC0`, paddingRight: 20 * u }}>
            {el.body ? (
              <div style={{ fontFamily: SERIF, fontSize: 15 * u, lineHeight: 1.55, textAlign: "justify", color: "#2B2926" }}>
                <span style={{ float: "left", fontWeight: 900, fontSize: 54 * u, lineHeight: 0.9, marginRight: 6 * u }}>{String(el.body).slice(0, 1)}</span>
                {String(el.body).slice(1)}
              </div>
            ) : (
              rows(7, "a")
            )}
          </div>
          <div style={{ flex: 1, borderRight: `${1 * u}px solid #CFCAC0`, paddingRight: 20 * u }}>{rows(8, "b")}</div>
          <div style={{ flex: 1 }}>
            {photo ? (
              <Img src={mediaSrc(edl.base, photo.src)} style={{ width: "100%", height: inner * 0.16, objectFit: "cover", filter: "grayscale(1) contrast(1.1)", display: "block" }} />
            ) : (
              <div style={{ width: "100%", height: inner * 0.16, background: "linear-gradient(120deg, #2E2E2E, #6B6B6B)" }} />
            )}
            {el.photoCaption ? <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 12 * u, color: "#55524C", margin: `${8 * u}px 0 ${12 * u}px` }}>{String(el.photoCaption)}</div> : <div style={{ height: 14 * u }} />}
            {rows(5, "c")}
          </div>
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- chart card

// Round gridlines: the smallest step of 1, 2, 2.5 or 5 (times a power of ten) that covers the range in at most five
// lines, the top line at or just above the highest value (8.0 gives 2, 4, 6, 8).
const niceScale = (lo: number, hi: number): { step: number; top: number } => {
  const span = Math.max(1e-9, hi - lo);
  const mag = Math.pow(10, Math.floor(Math.log10(span / 4)));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((st) => Math.ceil(span / st - 1e-9) <= 5) ?? 10 * mag;
  return { step, top: lo + Math.ceil(span / step - 1e-9) * step };
};

const tickLabel = (v: number, el: Props): string => {
  const s = Math.abs(v) >= 100 || Number.isInteger(v) ? String(Math.round(v)) : v.toFixed(1);
  return `${el.yPrefix ?? ""}${s}${el.ySuffix ?? ""}`;
};

// A line chart on a cream card: title, legend, axes, the lines drawn left to right, dots on the main line, a pulsing
// call-out on one point when it is said.
const ChartCard: React.FC<{ t: Theme; el: VoxElement; W: number; u: number; frame: number }> = ({ t, el, W, u, frame }) => {
  const c = voxColors(t);
  const w = (el.w ?? 0.54) * W;
  const h = w * (el.aspect ?? 0.58);
  const series: { name?: string; color?: string; values: number[] }[] = Array.isArray(el.series) ? el.series : [];
  const xs: string[] = Array.isArray(el.xLabels) ? el.xLabels.map(String) : [];
  const n = Math.max(2, ...series.map((s) => s.values.length));
  const all = series.flatMap((s) => s.values).filter((v) => Number.isFinite(v));
  const lo = Math.min(0, ...all);
  const { step: tick, top } = niceScale(lo, Math.max(...all, lo + 1));
  const k = w / 1030;
  const pad = { l: 86 * k, r: 40 * k, t: 116 * k, b: 72 * k };
  const pw = w - pad.l - pad.r;
  const ph = h - pad.t - pad.b;
  const X = (i: number) => pad.l + (i / (n - 1)) * pw;
  const Y = (v: number) => pad.t + ph - ((v - lo) / (top - lo)) * ph;
  const drawFrom = el.drawAt ?? el.at + 8;
  const drawTo = el.drawEnd ?? drawFrom + 50;
  const prog = interpolate(frame, [drawFrom, drawTo], [0, 1], { ...clampOpts, easing: Easing.inOut(Easing.sin) });
  const colors = [el.color || c.accent, c.grey, c.marker];
  const title = String(el.title || "");
  const ticks = Array.from({ length: Math.round((top - lo) / tick) }, (_, i) => lo + tick * (i + 1));
  const call = el.callout as { text?: string[] | string; at?: number; index?: number; series?: number } | undefined;
  const cs = call ? series[call.series ?? 0] : undefined;
  const ci = call && cs ? Math.min(cs.values.length - 1, call.index ?? cs.values.length - 1) : 0;
  // the call-out comes once the line has reached its point
  const callAt = call && call.at !== undefined ? Math.max(call.at, Math.round(drawFrom + (drawTo - drawFrom) * (ci / Math.max(1, n - 1)))) : undefined;
  const callP = callAt !== undefined ? spring({ frame: frame - callAt, fps: 30, config: { damping: 12, stiffness: 160 } }) : 0;
  const pulse = callAt !== undefined && frame >= callAt ? ((frame - callAt) % 36) / 36 : 0;
  const label: React.CSSProperties = { fontFamily: font("Inter"), fontWeight: 700, fill: "#7A7770" };
  const bn = isBengali(title);
  const callLines = call ? (Array.isArray(call.text) ? call.text : [String(call.text || "")]).filter(Boolean) : [];
  return (
    <div style={{ width: w, height: h, backgroundColor: c.cream, borderRadius: 24 * k, boxShadow: `0 ${18 * u}px ${40 * u}px rgba(30, 20, 10, 0.22)`, position: "relative", border: `${1.5 * k}px solid rgba(0, 0, 0, 0.05)` }}>
      <div style={{ position: "absolute", left: pad.l - 24 * k, top: 30 * k, fontFamily: bn ? displayFont(t, title) : font("Inter"), fontWeight: 800, fontSize: 32 * k, letterSpacing: bn ? 0 : "0.07em", textTransform: bn ? "none" : "uppercase", color: "#1B1A18", whiteSpace: "nowrap" }}>
        {title}
      </div>
      <div style={{ position: "absolute", right: pad.r, top: 30 * k, display: "flex", flexDirection: "column", gap: 8 * k }}>
        {series.map((s, i) =>
          s.name ? (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 * k, fontFamily: isBengali(s.name) ? displayFont(t, s.name) : font("Inter"), fontWeight: 700, fontSize: 17 * k, color: "#4A4843", textTransform: "uppercase", letterSpacing: "0.04em", whiteSpace: "nowrap" }}>
              <div style={{ width: 56 * k, height: 8 * k, borderRadius: 4 * k, backgroundColor: s.color || colors[i % colors.length] }} />
              {s.name}
              {i === 0 && el.note ? <span style={{ color: "#8A877F", fontWeight: 600, textTransform: "none", letterSpacing: 0 }}>{String(el.note)}</span> : null}
            </div>
          ) : null,
        )}
      </div>
      <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
        <defs>
          <clipPath id={`vox-draw-${el.id}`}>
            <rect x={0} y={0} width={pad.l + pw * prog + 10 * k} height={h} />
          </clipPath>
        </defs>
        {ticks.map((v, i) => (
          <g key={i}>
            <line x1={pad.l} x2={pad.l + pw} y1={Y(v)} y2={Y(v)} stroke="#E2DDD2" strokeWidth={2 * k} />
            <text x={pad.l - 16 * k} y={Y(v)} textAnchor="end" dominantBaseline="middle" fontSize={22 * k} style={label}>
              {tickLabel(v, el)}
            </text>
          </g>
        ))}
        <line x1={pad.l} x2={pad.l} y1={pad.t - 20 * k} y2={Y(lo)} stroke="#BFBAB0" strokeWidth={2.5 * k} />
        <line x1={pad.l} x2={pad.l + pw} y1={Y(lo)} y2={Y(lo)} stroke="#BFBAB0" strokeWidth={2.5 * k} />
        {xs.map((lab, i) =>
          i < n && (xs.length <= 12 || i % Math.ceil(xs.length / 12) === 0 || i === xs.length - 1) ? (
            <text key={i} x={X(i)} y={pad.t + ph + 40 * k} textAnchor="middle" fontSize={19 * k} style={label}>
              {lab}
            </text>
          ) : null,
        )}
        <g clipPath={`url(#vox-draw-${el.id})`}>
          {series
            .map((s, si) => ({ s, si }))
            .reverse()
            .map(({ s, si }) => (
              <g key={si}>
                <polyline
                  points={s.values.map((v, i) => `${X(i)},${Y(v)}`).join(" ")}
                  fill="none"
                  stroke={s.color || colors[si % colors.length]}
                  strokeWidth={(si === 0 ? 9 : 5.5) * k}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                />
                {si === 0
                  ? s.values.map((v, i) => {
                      const reach = drawFrom + (drawTo - drawFrom) * (i / Math.max(1, n - 1));
                      const pop = spring({ frame: frame - reach, fps: 30, config: { damping: 19, stiffness: 280 } });
                      return pop > 0.01 ? <circle key={i} cx={X(i)} cy={Y(v)} r={7 * k * pop} fill="#FFFFFF" stroke={s.color || colors[0]} strokeWidth={3.5 * k} /> : null;
                    })
                  : null}
              </g>
            ))}
        </g>
        {call && cs && callP > 0.01 ? (
          <g>
            <circle cx={X(ci)} cy={Y(cs.values[ci])} r={(12 + 22 * pulse) * k} fill={c.accent} opacity={0.35 * (1 - pulse)} />
            <circle cx={X(ci)} cy={Y(cs.values[ci])} r={10 * k} fill="#FFFFFF" stroke={c.accent} strokeWidth={3 * k} />
            <circle cx={X(ci)} cy={Y(cs.values[ci])} r={5 * k} fill="#1B1A18" />
          </g>
        ) : null}
      </svg>
      {call && cs && callP > 0.01 && callLines.length ? (
        <div
          style={{
            position: "absolute",
            left: Math.max(pad.l, Math.min(w - pad.r - 190 * k, X(ci) - 190 * k)),
            // above the point when there is room under the title and legend band, else below it
            top: Y(cs.values[ci]) - 150 * k >= pad.t - 10 * k ? Y(cs.values[ci]) - 150 * k : Y(cs.values[ci]) + 34 * k,
            padding: `${10 * k}px ${16 * k}px`,
            border: `${3.5 * k}px solid ${c.accent}`,
            borderRadius: 12 * k,
            backgroundColor: "#FFFDF8",
            fontFamily: font("Inter"),
            fontWeight: 800,
            fontSize: 22 * k,
            lineHeight: 1.2,
            color: "#1B1A18",
            textAlign: "center",
            whiteSpace: "nowrap",
            transformOrigin: "100% 100%",
            transform: `scale(${0.6 + 0.4 * Math.min(1.1, callP)})`,
            opacity: Math.min(1, callP * 2),
          }}
        >
          {callLines.map((line, i) => (
            <div key={i} style={i === callLines.length - 1 && callLines.length > 1 ? { color: c.accent, fontWeight: 900, fontSize: 26 * k } : undefined}>
              {line}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
};

// ---------------------------------------------------------------- typewriter

// Typed word by word as each is said (the compiler gives every word its spoken frame), with a block cursor that
// blinks when the typing stops.
const letters = (w: string): string[] => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Seg = (Intl as any).Segmenter;
  return Seg ? Array.from(new Seg("bn", { granularity: "grapheme" }).segment(w), (x: { segment: string }) => x.segment) : Array.from(w);
};

const Typewriter: React.FC<{ t: Theme; el: VoxElement; u: number; frame: number; fps: number }> = ({ t, el, u, frame, fps }) => {
  const c = voxColors(t);
  const lines = linesOf(el);
  const words = lines.flatMap((line, li) => line.split(" ").filter(Boolean).map((w) => ({ w, li })));
  const times: number[] = Array.isArray(el.times) && el.times.length === words.length ? el.times : words.map((_, i) => el.at + i * 7);
  const bn = isBengali(lines.join(" "));
  const size = (el.size ?? 58) * u;
  const shown: string[] = lines.map(() => "");
  let cursorLine = 0;
  let typing = false;
  words.forEach((wd, i) => {
    const start = times[i];
    if (frame < start) return;
    const next = i + 1 < times.length ? times[i + 1] : start + Math.round(0.4 * fps);
    const span = Math.max(2, Math.min(next - start, Math.round(0.32 * fps)));
    const parts = letters(wd.w);
    const k = Math.min(parts.length, Math.floor(((frame - start + 1) / span) * parts.length));
    if (k < parts.length) typing = true;
    cursorLine = wd.li;
    shown[wd.li] += (shown[wd.li] ? " " : "") + parts.slice(0, Math.max(1, k)).join("");
  });
  const on = typing || Math.floor(frame / 16) % 2 === 0;
  return (
    <div
      style={{
        fontFamily: bn ? bodyFont(t, lines.join(" ")) : TYPED,
        fontWeight: bn ? 600 : 400,
        fontSize: size,
        lineHeight: 1.62,
        color: el.color || "#1C1B19",
        textTransform: el.caps === false || bn ? "none" : "uppercase",
        whiteSpace: "pre",
        textAlign: (el.align as React.CSSProperties["textAlign"]) || "left",
      }}
    >
      {lines.map((_, i) => (
        <div key={i} style={{ minHeight: size * 1.62 }}>
          {shown[i]}
          {i === cursorLine && el.cursor !== false ? (
            <span style={{ display: "inline-block", width: size * 0.22, height: size * 0.98, marginLeft: size * 0.18, backgroundColor: el.color || c.ink, opacity: on ? 1 : 0, verticalAlign: "-0.14em" }} />
          ) : null}
        </div>
      ))}
    </div>
  );
};

// ---------------------------------------------------------------- hand-drawn marks

// A marker circle, underline, arrow, cross or box, drawn on over a few frames and boiling a little afterwards.
const Scribble: React.FC<{ t: Theme; el: VoxElement; W: number; H: number; u: number; frame: number }> = ({ t, el, W, H, u, frame }) => {
  const c = voxColors(t);
  const shape = String(el.shape || "circle");
  const w = (el.w ?? 0.2) * W;
  const h = (el.h ?? (shape === "underline" ? 0.03 : 0.12)) * H;
  const thick = (el.thick ?? 7) * u;
  const draw = el.draw ?? 14;
  const p = interpolate(frame, [el.at, el.at + draw], [0, 1], { ...clampOpts, easing: easeOut });
  const boil = Math.floor(frame / 4);
  const j = (s: string) => (random(`${el.id}-${s}-${boil}`) - 0.5) * 3 * u;
  const pad = thick * 2 + 30 * u;
  let d = "";
  if (shape === "circle") {
    const pts: string[] = [];
    const turns = 1.12;
    for (let i = 0; i <= 48; i++) {
      const a = -Math.PI * 0.6 + (i / 48) * Math.PI * 2 * turns;
      const r = 1 + 0.05 * Math.sin(i * 0.7 + 1.3) + (i / 48) * 0.06;
      pts.push(`${pad + w / 2 + (w / 2) * r * Math.cos(a) + j(`c${i}x`)} ${pad + h / 2 + (h / 2) * r * Math.sin(a) + j(`c${i}y`)}`);
    }
    d = "M " + pts.join(" L ");
  } else if (shape === "underline") {
    d = `M ${pad} ${pad + h * 0.6 + j("a")} Q ${pad + w * 0.5} ${pad + h * 0.2 + j("b")} ${pad + w} ${pad + h * 0.5 + j("c")}`;
  } else if (shape === "cross") {
    d = `M ${pad} ${pad + j("a")} L ${pad + w} ${pad + h + j("b")} M ${pad + w} ${pad + j("c")} L ${pad} ${pad + h + j("d")}`;
  } else if (shape === "box") {
    d = `M ${pad + j("a")} ${pad + j("b")} L ${pad + w + j("c")} ${pad + j("d")} L ${pad + w + j("e")} ${pad + h + j("f")} L ${pad + j("g")} ${pad + h + j("h")} Z`;
  } else if (shape === "arrow") {
    // from the left end to the right end with a bow; the element's rotate points it
    const x0 = pad;
    const y0 = pad + h * 0.5;
    const x1 = pad + w;
    const y1 = pad + h * 0.5;
    const hx = x1 - 26 * u;
    d = `M ${x0} ${y0 + j("a")} Q ${pad + w * 0.5} ${pad + h * 0.5 - h * 0.9 + j("b")} ${x1} ${y1} M ${hx} ${y1 - 20 * u} L ${x1} ${y1} L ${hx - 6 * u} ${y1 + 18 * u}`;
  }
  return (
    <svg width={w + 2 * pad} height={h + 2 * pad} style={{ display: "block", overflow: "visible", margin: -pad }}>
      <path d={d} fill="none" stroke={el.color || c.marker} strokeWidth={thick} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

// ---------------------------------------------------------------- the beat

export const VoxBeat: React.FC<{ edl: Edl; overlay: Overlay }> = ({ edl, overlay }) => {
  const now = useCurrentFrame();
  // graphics "on twos" when the look asks for it: every move holds for `step` frames (clips keep their own time)
  const step = Math.max(1, Math.round(Number(overlay.props.step ?? edl.theme.voxStep ?? 1)));
  const frame = step > 1 ? Math.floor(now / step) * step : now;
  const { width: W, height: H, fps } = useVideoConfig();
  const u = unit(W, H);
  const t = edl.theme;
  const dur = overlay.durationInFrames;
  const elements: VoxElement[] = (overlay.props.elements || []) as VoxElement[];
  const pushTo = Number(overlay.props.push ?? 0.035);
  const pushP = Math.min(1, frame / Math.max(1, dur));
  const byId: Record<string, VoxElement> = {};
  for (const el of elements) byId[el.id] = el;
  const where = (el: VoxElement) => {
    const place = placeAt(el, frame, W, H);
    const m = motionAt(el, frame, fps, W, H, u);
    const f = m.visible && m.landed > 0.9 ? floatAt(el, frame, u) : { y: 0, r: 0 };
    const d = driftAt(el, frame, fps, W, H);
    place.x += d.x;
    place.y += d.y;
    return { place, m, f };
  };
  const sorted = elements
    .map((el, i) => ({ el, i }))
    .sort((a, b) => (LAYER_ORDER[a.el.layer || "mid"] ?? 1) - (LAYER_ORDER[b.el.layer || "mid"] ?? 1) || a.i - b.i)
    .map((x) => x.el);
  return (
    <AbsoluteFill>
      {sorted.map((el) => {
        const { place, m, f } = where(el);
        if (!m.visible) return null;
        let x = place.x + m.dx;
        let y = place.y + m.dy + f.y;
        if (el.follow && byId[el.follow]) {
          // stays with what it describes (a price tag over a moving ship)
          const o = where(byId[el.follow]);
          x = o.place.x + o.m.dx + (el.dx ?? 0) * W;
          y = o.place.y + o.m.dy + o.f.y + (el.dy ?? 0) * H;
        }
        // the push: around the frame's centre, more for nearer layers
        const k = 1 + pushTo * pushP * (LAYER_PUSH[el.layer || "mid"] ?? 0.8);
        x = W / 2 + (x - W / 2) * k;
        y = H / 2 + (y - H / 2) * k;
        const [ax, ay] = ANCHOR[el.anchor || "center"] || ANCHOR.center;
        let body: React.ReactNode = null;
        switch (el.kind) {
          case "cutout":
            body = <Cutout edl={edl} el={el} W={W} u={u} />;
            break;
          case "card":
            body = <Card edl={edl} el={el} W={W} u={u} />;
            break;
          case "clip":
            body = <Clip edl={edl} el={el} W={W} H={H} />;
            break;
          case "headline":
            body = <Headline t={t} el={el} W={W} u={u} clip={m.clip} frame={frame} />;
            break;
          case "label":
            body = <Label t={t} el={el} u={u} />;
            break;
          case "credit":
            body = <Credit t={t} el={el} u={u} />;
            break;
          case "icon":
            body = <IconEl t={t} el={el} u={u} />;
            break;
          case "tag":
            body = <Tag t={t} el={el} u={u} frame={frame} />;
            break;
          case "bubble":
            body = <Bubble t={t} el={el} u={u} />;
            break;
          case "newspaper":
            body = <Newspaper edl={edl} t={t} el={el} W={W} u={u} frame={frame} />;
            break;
          case "chart":
            body = <ChartCard t={t} el={el} W={W} u={u} frame={frame} />;
            break;
          case "typewriter":
            body = <Typewriter t={t} el={el} u={u} frame={frame} fps={fps} />;
            break;
          case "scribble":
            body = <Scribble t={t} el={el} W={W} H={H} u={u} frame={frame} />;
            break;
          default:
            body = null;
        }
        if (!body) return null;
        return (
          <div
            key={el.id}
            style={{
              position: "absolute",
              left: x,
              top: y,
              opacity: m.o,
              transform: `translate(${ax}%, ${ay}%) scale(${m.s * place.scale * k}) rotate(${place.rotate + m.r + f.r}deg)`,
              transformOrigin: `${-ax}% ${-ay}%`,
              clipPath: el.kind !== "headline" && m.clip < 1 ? `inset(-10% ${(1 - m.clip) * 100}% -10% -10%)` : undefined,
              // a blend (fire or smoke shot on black, as screen) mixes with the paper under it: it must sit on this
              // outer box, or the box's own stacking context keeps the black
              mixBlendMode: (el.blend as React.CSSProperties["mixBlendMode"]) || undefined,
            }}
          >
            {body}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- the locked ground, grain and light leaks

// Warm grey paper with a faint square grid, a printed grain and a soft vignette, as measured on the reference (the
// grain is strong: a luma spread of about 7 levels). It never changes between beats, so a run of beats reads as one
// continuous shot, and a still texture costs the encoder almost nothing.
export const PaperGrid: React.FC<{ theme: Theme }> = ({ theme }) => {
  const { width: W, height: H } = useVideoConfig();
  const u = unit(W, H);
  const c = voxColors(theme);
  const cell = Math.round(106 * u);
  const line = Math.max(1, 1.7 * u);
  const soft = Math.max(0.6, 0.9 * u);
  const ox = Math.round((W % cell) / 2);
  const oy = Math.round((H % cell) / 2);
  const stroke = (dir: string) =>
    `linear-gradient(${dir}, transparent 0px, ${c.grid} ${soft}px, ${c.grid} ${soft + line}px, transparent ${2 * soft + line}px, transparent 100%)`;
  return (
    <AbsoluteFill style={{ backgroundColor: c.paper }}>
      <AbsoluteFill
        style={{
          backgroundImage: [stroke("180deg"), stroke("90deg")].join(", "),
          backgroundSize: `${cell}px ${cell}px, ${cell}px ${cell}px`,
          backgroundPosition: `${ox}px ${oy}px, ${ox}px ${oy}px`,
        }}
      />
      <AbsoluteFill style={{ backgroundImage: grainTile(0), backgroundSize: `${Math.round(GRAIN_TILE * 1.25 * u)}px`, opacity: 0.74, mixBlendMode: "overlay" }} />
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0) 55%, rgba(60, 50, 40, 0.10) 100%)" }}
      />
    </AbsoluteFill>
  );
};

// Pixel grain: a 256 px tile of grey noise (the mean of three uniform draws per pixel, so it clusters around mid
// grey like film grain) from a seeded generator, made once per tab and reused on every frame. SVG turbulence cannot
// draw noise this fine, and Chrome draws SVG filters on the CPU.
const GRAIN_TILE = 256;
const grainTiles: Record<number, string> = {};
const mulberry32 = (seed: number) => () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const grainTile = (seed: number): string => {
  if (grainTiles[seed]) return grainTiles[seed];
  if (typeof document === "undefined") return "none";
  const canvas = document.createElement("canvas");
  canvas.width = GRAIN_TILE;
  canvas.height = GRAIN_TILE;
  const ctx = canvas.getContext("2d");
  if (!ctx) return "none";
  const img = ctx.createImageData(GRAIN_TILE, GRAIN_TILE);
  const rnd = mulberry32(9173 + seed * 7919);
  for (let i = 0; i < GRAIN_TILE * GRAIN_TILE; i++) {
    const v = Math.round(((rnd() + rnd() + rnd()) / 3) * 255);
    img.data[i * 4] = v;
    img.data[i * 4 + 1] = v;
    img.data[i * 4 + 2] = v;
    img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  grainTiles[seed] = `url(${canvas.toDataURL("image/png")})`;
  return grainTiles[seed];
};

// Film grain over the whole picture, pictures and cards included: six plates swapped every ten frames (a boil, not a
// buzz), faint enough that the encoder keeps it cheap.
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.16 }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  const seed = 1 + (Math.floor(frame / 10) % 6);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: grainTile(seed),
        backgroundSize: `${Math.round(GRAIN_TILE * 1.25 * u)}px`,
        opacity,
        mixBlendMode: "overlay",
        pointerEvents: "none",
      }}
    />
  );
};

// A warm burst of light that washes across a cut and hides it.
export const LightLeak: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = frame / Math.max(1, durationInFrames - 1);
  const a = Math.sin(p * Math.PI);
  const x = 15 + 70 * p;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 70% 90% at ${x}% 45%, rgba(255, 236, 200, ${a}) 0%, rgba(255, 170, 90, ${0.85 * a}) 30%, rgba(255, 110, 70, ${0.5 * a}) 55%, rgba(255, 80, 120, 0) 80%)`,
          mixBlendMode: "screen",
        }}
      />
      <AbsoluteFill style={{ backgroundColor: `rgba(255, 244, 225, ${Math.max(0, a - 0.55) * 1.6})` }} />
    </AbsoluteFill>
  );
};
