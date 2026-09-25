// Designed full-frame scenes and the pieces they share, built on the remotion-broll kit's craft: words that rise out
// of a blur with hand-drawn underlines on key words, numbered step cards on colour with drifting bubbles, a big
// number with its curve, bar charts that grow in turn, a split for before and after, recap cards, a subscribe end
// card with a cursor click, photo cards with a label chip, and colour bars that sweep over a cut. Every size scales
// with the frame and every time comes from the overlay's own length or from events the compiler put in props.t.
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Video } from "@remotion/media";
import {
  Edl,
  Overlay,
  Theme,
  clampOpts,
  countUp,
  coverRect,
  displayFont,
  easeOut,
  fitSize,
  formatNumber,
  graphemes,
  highlightOf,
  isBengali,
  luminance,
  mediaSrc,
  mix,
  onColor,
  paletteOf,
  paperOf,
  paperTextOf,
  smoothNoise,
  toBengaliDigits,
  unit,
} from "./lib";

type P = { edl: Edl; overlay: Overlay };
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Props = Record<string, any>;

const IMAGE = /\.(png|jpe?g|webp|gif|bmp)$/i;

export const SCENE_TYPES = new Set(["kinetic", "step", "bigStat", "bars", "versus", "recap", "endCard", "photo"]);

const useScene = (edl: Edl, overlay: Overlay) => {
  const frame = useCurrentFrame();
  const { width: W, height: H, fps } = useVideoConfig();
  const t = edl.theme;
  return {
    frame,
    fps,
    W,
    H,
    u: unit(W, H),
    t,
    dur: overlay.durationInFrames,
    vertical: H > W,
    safe: edl.safe,
    pal: paletteOf(t),
    ev: (overlay.props.t || {}) as Record<string, number>,
    bnDigits: String(edl.language || "").startsWith("bn"),
    floor: sceneFloor(edl, overlay, H),
    ...sceneSides(edl, overlay, W, H),
  };
};

// The presenter's round picture over a scene: its size, its corner, and the left and right edges it leaves the
// scene's cards (they stay clear of it).
export const scenePip = (edl: Edl, overlay: Overlay, W: number, H: number) => {
  const clip = edl.clips.find((c) => c.cam && c.from < overlay.from + overlay.durationInFrames && overlay.from < c.from + c.durationInFrames);
  const pip = clip?.pip ?? { corner: "br" as const, shape: "circle" as const, size: 0.17 };
  const corner = H > W ? (pip.corner.endsWith("l") ? "tl" : "tr") : pip.corner;
  return { corner, size: Math.round(Math.min(pip.size, 0.15) * W) };
};

const sceneSides = (edl: Edl, overlay: Overlay, W: number, H: number) => {
  const u = unit(W, H);
  let left = edl.safe.x;
  let right = edl.safe.x + edl.safe.w;
  if (overlay.props.pip) {
    const p = scenePip(edl, overlay, W, H);
    if (H <= W) {
      if (p.corner.endsWith("r")) right -= p.size + 52 * u;
      else left += p.size + 52 * u;
    }
  }
  return { left, right };
};

// Where a scene's cards must end: above the caption band when captions are burned over this scene, else the safe
// frame's bottom.
const sceneFloor = (edl: Edl, overlay: Overlay, H: number): number => {
  const safeBottom = edl.safe.y + edl.safe.h;
  if (!edl.captions?.burn || overlay.props.hideCaptions) return safeBottom;
  const band = edl.captions.band || edl.bands.captions;
  if (edl.captions.style === "sentence") {
    // a two-line subtitle box grows up from the band's bottom (captions.tsx: 8 px padding, 1.45 or 1.3 lines)
    const u = unit(edl.width, edl.height);
    const bn = String(edl.language || "").startsWith("bn");
    const box = 2 * edl.captions.fontPx * (bn ? 1.08 * 1.45 : 1.3) + 16 * u;
    return Math.min(safeBottom, band.y + band.h - box - 0.02 * H);
  }
  return Math.min(safeBottom, band.y - 0.02 * H);
};

// A slow push-in: a hold longer than about 0.7 s reads as a frozen frame without one.
const push = (frame: number, dur: number, amount = 0.04): number => 1 + amount * Math.min(1, frame / Math.max(1, dur));

const norm = (w: string): string => w.toLowerCase().replace(/[^\p{L}\p{N}\p{M}]/gu, "");

export const keySet = (highlight: unknown): Set<string> => {
  const list = Array.isArray(highlight) ? highlight : String(highlight || "").split(/\s+/);
  return new Set(list.map((x) => norm(String(x))).filter(Boolean));
};

// Lines as written in the plan (pre-broken by the compiler), else the single text.
export const linesOf = (props: Props, key = "lines", fallback = "text"): string[] => {
  const v = props[key];
  if (Array.isArray(v)) return v.map(String).filter((x) => x.trim());
  if (typeof v === "string" && v.trim()) return [v];
  const f = props[fallback];
  if (Array.isArray(f)) return f.map(String).filter((x) => x.trim());
  return f ? [String(f)] : [];
};

const digits = (text: string, bn: boolean): string => (bn ? toBengaliDigits(text) : text);

// ---------------------------------------------------------------- shared pieces

// A hand-drawn underline: two uneven strokes, revealed left to right.
export const Scribble: React.FC<{ progress: number; color: string; seed: string; thick: number }> = ({
  progress,
  color,
  seed,
  thick,
}) => {
  if (progress <= 0) return null;
  const j = (k: string, a: number) => (random(`${seed}-${k}`) - 0.5) * a;
  const d1 = `M 1 ${58 + j("a", 14)} C 25 ${46 + j("b", 16)}, 60 ${66 + j("c", 16)}, 99 ${52 + j("d", 14)}`;
  const d2 = `M 5 ${72 + j("e", 12)} C 32 ${62 + j("f", 14)}, 64 ${76 + j("g", 14)}, 95 ${64 + j("h", 12)}`;
  return (
    <span
      style={{
        position: "absolute",
        left: "-4%",
        width: "108%",
        bottom: "-0.22em",
        height: "0.34em",
        clipPath: `inset(-60% ${(1 - Math.min(1, progress)) * 100}% -60% 0)`,
        pointerEvents: "none",
      }}
    >
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ overflow: "visible", display: "block" }}>
        <path d={d1} fill="none" stroke={color} strokeWidth={thick} strokeLinecap="round" vectorEffect="non-scaling-stroke" />
        <path d={d2} fill="none" stroke={color} strokeWidth={thick * 0.5} strokeLinecap="round" vectorEffect="non-scaling-stroke" opacity={0.8} />
      </svg>
    </span>
  );
};

// Words that rise out of a blur one after another; key words take their colour and a hand-drawn underline once the
// line has landed. Lines are kept as given (the compiler breaks and balances them), so nothing wraps by surprise.
export const Words: React.FC<{
  lines: string[];
  size: number;
  color: string;
  family: string;
  weight?: number;
  start?: number;
  stagger?: number;
  keys?: Set<string>;
  keyColor?: string;
  underlineAt?: number | null;
  underlineColor?: string;
  align?: "center" | "left";
  lineHeight?: number;
  tracking?: string | number;
  upper?: boolean;
  shadow?: string;
  blur?: boolean;
  seed?: string;
}> = ({
  lines,
  size,
  color,
  family,
  weight = 800,
  start = 6,
  stagger = 4,
  keys,
  keyColor,
  underlineAt = null,
  underlineColor,
  align = "center",
  lineHeight,
  tracking,
  upper,
  shadow,
  blur = true,
  seed = "w",
}) => {
  const frame = useCurrentFrame();
  const bn = isBengali(lines.join(" "));
  let k = 0;
  let keyNo = 0;
  return (
    <div
      style={{
        fontFamily: family,
        fontWeight: weight,
        fontSize: size,
        lineHeight: lineHeight ?? (bn ? 1.34 : 1.08),
        color,
        textAlign: align,
        letterSpacing: tracking ?? (bn ? 0 : "-0.02em"),
        textTransform: upper && !bn ? "uppercase" : "none",
      }}
    >
      {lines.map((line, row) => (
        <div key={row} style={{ whiteSpace: "nowrap" }}>
          {line
            .split(/\s+/)
            .filter(Boolean)
            .map((w, col) => {
              const i = k++;
              const at = start + i * stagger;
              const o = interpolate(frame, [at, at + 8], [0, 1], clampOpts);
              const rise = interpolate(frame, [at, at + 10], [size * 0.35, 0], { ...clampOpts, easing: easeOut });
              const b = blur ? interpolate(frame, [at, at + 8], [size * 0.1, 0], clampOpts) : 0;
              const isKey = !!keys && keys.size > 0 && keys.has(norm(w));
              const mine = isKey ? keyNo++ : 0;
              const ul =
                isKey && underlineAt !== null
                  ? interpolate(frame, [underlineAt + mine * 5, underlineAt + mine * 5 + 12], [0, 1], clampOpts)
                  : 0;
              return (
                <span
                  key={col}
                  style={{
                    display: "inline-block",
                    position: "relative",
                    margin: "0 0.13em",
                    opacity: o,
                    transform: `translateY(${rise}px)`,
                    filter: b > 0.05 ? `blur(${b}px)` : undefined,
                    color: isKey && keyColor ? keyColor : undefined,
                    textShadow: shadow,
                  }}
                >
                  {w}
                  {isKey && underlineAt !== null ? (
                    <Scribble progress={ul} color={underlineColor || keyColor || color} seed={`${seed}-${i}`} thick={Math.max(3, size * 0.085)} />
                  ) : null}
                </span>
              );
            })}
        </div>
      ))}
    </div>
  );
};

// Soft circles that drift up across a coloured scene.
export const Bubbles: React.FC<{ seed: string; count?: number; alpha?: number; speed?: number }> = ({ seed, count = 6, alpha = 0.08, speed = 1 }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = unit(W, H);
  return (
    <>
      {Array.from({ length: count }).map((_, i) => {
        const r = (80 + random(`${seed}-r-${i}`) * 160) * u;
        const span = H + 2 * r;
        const y0 = random(`${seed}-y-${i}`) * span - frame * (0.4 + i * 0.12) * u * speed;
        const y = (((y0 % span) + span) % span) - r;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: random(`${seed}-x-${i}`) * W - r,
              top: y - r,
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              backgroundColor: `rgba(255, 255, 255, ${alpha})`,
            }}
          />
        );
      })}
    </>
  );
};

// Warm paper with a fine dot grid (the kit's data-card ground).
export const Paper: React.FC<{ theme: Theme; color?: string }> = ({ theme, color }) => {
  const { width: W, height: H } = useVideoConfig();
  const u = unit(W, H);
  const bg = color || paperOf(theme);
  const dot = luminance(bg) > 0.3 ? "rgba(120, 90, 60, 0.12)" : "rgba(255, 255, 255, 0.06)";
  const r = Math.max(1.5, 2 * u);
  return (
    <AbsoluteFill
      style={{ backgroundColor: bg, backgroundImage: `radial-gradient(${dot} ${r}px, transparent ${r}px)`, backgroundSize: `${36 * u}px ${36 * u}px` }}
    />
  );
};

// A dark location-style tag that pops in ("DAY 1", "RACE DAY").
export const Chip: React.FC<{
  text: string;
  theme: Theme;
  delay?: number;
  tone?: "dark" | "light" | "accent";
  size?: number;
  style?: React.CSSProperties;
  origin?: string;
}> = ({ text, theme, delay = 0, tone = "dark", size = 34, style, origin = "0% 50%" }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const u = unit(width, height);
  const pop = spring({ frame: frame - delay, fps, config: { damping: 13, stiffness: 190 } });
  const bn = isBengali(text);
  const sz = size * u * (bn ? 1.18 : 1);
  const bg = tone === "light" ? "#FFF4E4" : tone === "accent" ? theme.accent : "rgba(30, 22, 18, 0.9)";
  const fg = tone === "light" ? "#2B1D16" : tone === "accent" ? onColor(theme.accent) : "#FFF4E4";
  return (
    <div
      style={{
        position: "absolute",
        padding: `${0.36 * sz}px ${0.7 * sz}px`,
        borderRadius: 0.42 * sz,
        backgroundColor: bg,
        color: fg,
        fontFamily: displayFont(theme, text),
        fontWeight: 700,
        fontSize: sz,
        lineHeight: bn ? 1.3 : 1.1,
        letterSpacing: bn ? 0 : "0.06em",
        textTransform: bn ? "none" : "uppercase",
        whiteSpace: "nowrap",
        transformOrigin: origin,
        transform: `scale(${pop})`,
        opacity: Math.min(1, Math.max(0, pop * 1.6)),
        boxShadow: `0 ${10 * u}px ${24 * u}px rgba(43, 29, 22, 0.25)`,
        ...style,
      }}
    >
      {text}
    </div>
  );
};

const cardShadow = (u: number): string => `0 ${30 * u}px ${80 * u}px rgba(60, 30, 10, 0.16)`;

// Picture or clip covering a box, with a slow push.
const Media: React.FC<{ edl: Edl; sourceId: string; w: number; h: number; scale: number; trimBefore?: number }> = ({
  edl,
  sourceId,
  w,
  h,
  scale,
  trimBefore = 0,
}) => {
  const src = edl.sources[sourceId];
  if (!src) return null;
  const url = mediaSrc(edl.base, src.src);
  const r = coverRect(src.width || w, src.height || h, w, h, 0.5, 0.45, scale);
  const style: React.CSSProperties = { position: "absolute", left: r.left, top: r.top, width: r.width, height: r.height };
  return IMAGE.test(src.src) ? (
    <Img src={url} style={style} />
  ) : (
    <Video src={url} trimBefore={trimBefore} muted objectFit="fill" style={style} />
  );
};

// The card area of a data scene: the safe frame, a little inset on landscape.
const cardRect = (s: ReturnType<typeof useScene>) => {
  const inset = s.vertical ? 0 : 44 * s.u;
  const top = s.vertical ? 30 * s.u : 56 * s.u;
  const y = s.safe.y + top;
  return { x: s.left + inset, y, w: s.right - s.left - 2 * inset, h: Math.min(s.safe.h - 2 * top, s.floor - top * 0.4 - y) };
};

// ---------------------------------------------------------------- kinetic words

const Kinetic: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const lines = linesOf(p);
  const text = lines.join(" ");
  const bn = isBengali(text);
  const bg = p.bg || "dusk";
  const base = (s.vertical ? 92 : 104) * s.u * (bn ? 0.92 : 1) * (p.scale || 1);
  const size = fitSize(lines, base, s.safe.w * (s.vertical ? 0.94 : 0.84));
  const n = text.split(/\s+/).filter(Boolean).length;
  const stagger = Math.max(2, Math.min(4, Math.floor((s.dur * 0.4) / Math.max(1, n))));
  const landed = 6 + (n - 1) * stagger + 10;
  let background: string | undefined;
  let color = "#FFFFFF";
  let keyColor = highlightOf(s.t);
  if (bg === "paper") {
    color = paperTextOf(s.t);
    keyColor = p.color || s.pal[0];
  } else if (bg === "color") {
    const c = p.color || s.pal[0];
    background = c;
    color = onColor(c);
    keyColor = color === "#FFFFFF" ? highlightOf(s.t) : s.pal[1];
  } else {
    const c = p.color || s.pal[1];
    background = `radial-gradient(ellipse at 50% 58%, ${mix(c, "#000000", 0.6)} 0%, ${mix(c, "#000000", 0.83)} 55%, #0B070B 100%)`;
  }
  return (
    <AbsoluteFill style={{ background, overflow: "hidden" }}>
      {bg === "paper" ? <Paper theme={s.t} /> : null}
      {bg === "color" ? <Bubbles seed={overlay.id} /> : null}
      <div
        style={{
          position: "absolute",
          left: s.safe.x,
          top: s.safe.y,
          width: s.safe.w,
          height: s.safe.h,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${push(s.frame, s.dur, 0.05)})`,
        }}
      >
        <Words
          lines={lines}
          size={size}
          color={color}
          family={displayFont(s.t, text)}
          weight={700}
          start={6}
          stagger={stagger}
          keys={keySet(p.highlight)}
          keyColor={keyColor}
          underlineAt={landed}
          seed={overlay.id}
        />
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- step card

const STEP_ACCENTS = ["#FFE08A", "#FFB3D9", "#8EE3C8", "#FFE08A", "#BFD8FF"];

const StepCard: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const n = Math.max(1, Number(p.n) || 1);
  const idx = (n - 1) % s.pal.length;
  const color = p.color || s.pal[idx];
  const accent = p.accent || (edl.theme.palette && edl.theme.palette.length ? mix(color, "#FFFFFF", 0.7) : STEP_ACCENTS[idx]);
  const fg = onColor(color);
  const lines = linesOf(p, "lines", "title");
  const text = lines.join(" ");
  const bn = isBengali(text);
  const label = String(p.label ?? "");
  const numText = String(p.numText ?? n);
  const badge = spring({ frame: s.frame - 2, fps: s.fps, config: { damping: 11, stiffness: 160 } });
  const lab = interpolate(s.frame, [6, 16], [0, 1], { ...clampOpts, easing: easeOut });
  const bar = interpolate(s.frame, [12, 28], [0, 1], { ...clampOpts, easing: easeOut });
  const B = (s.vertical ? 230 : 260) * s.u;
  const left = s.safe.x + 0.05 * s.W;
  const textW = s.vertical ? s.safe.w * 0.9 : s.safe.x + s.safe.w - left - B - 70 * s.u - 30 * s.u;
  const size = fitSize(lines, (s.vertical ? 88 : 104) * s.u * (bn ? 0.9 : 1), textW);
  const align = s.vertical ? "center" : "left";
  const number = (
    <div
      style={{
        width: B,
        height: B,
        flexShrink: 0,
        borderRadius: "50%",
        backgroundColor: "#FFFFFF",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: displayFont(s.t, numText),
        fontWeight: 800,
        fontSize: B * (isBengali(numText) ? 0.56 : 0.65),
        lineHeight: 1,
        color,
        transform: `scale(${badge}) rotate(${(1 - badge) * -40}deg) translateY(${Math.sin(s.frame / 8) * 6 * s.u}px)`,
        boxShadow: `0 ${24 * s.u}px ${60 * s.u}px rgba(0, 0, 0, 0.18)`,
      }}
    >
      {numText}
    </div>
  );
  const words = (
    <div style={{ textAlign: align }}>
      {label ? (
        <div
          style={{
            fontFamily: displayFont(s.t, label),
            fontWeight: 700,
            fontSize: (isBengali(label) ? 52 : 40) * s.u,
            letterSpacing: isBengali(label) ? 0 : "0.15em",
            textTransform: "uppercase",
            color: accent,
            opacity: lab,
            transform: `translateX(${s.vertical ? 0 : (1 - lab) * -30 * s.u}px) translateY(${s.vertical ? (1 - lab) * 20 * s.u : 0}px)`,
            marginBottom: 10 * s.u,
          }}
        >
          {label}
        </div>
      ) : null}
      <Words lines={lines} size={size} color={fg} family={displayFont(s.t, text)} weight={800} start={10} stagger={3} align={align} lineHeight={bn ? 1.3 : 1.05} tracking={bn ? 0 : "-0.02em"} />
      <div
        style={{
          marginTop: 28 * s.u,
          height: 12 * s.u,
          width: 260 * s.u * bar,
          borderRadius: 6 * s.u,
          backgroundColor: accent,
          marginLeft: s.vertical ? "auto" : 0,
          marginRight: s.vertical ? "auto" : 0,
        }}
      />
    </div>
  );
  return (
    <AbsoluteFill style={{ backgroundColor: color, overflow: "hidden" }}>
      <Bubbles seed={`step-${n}`} />
      {s.vertical ? (
        <div
          style={{
            position: "absolute",
            left: s.safe.x,
            width: s.safe.w,
            top: s.safe.y,
            height: s.safe.h,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 48 * s.u,
            transform: `scale(${push(s.frame, s.dur, 0.05)})`,
          }}
        >
          {number}
          {words}
        </div>
      ) : (
        <div
          style={{
            position: "absolute",
            left,
            top: 0,
            bottom: 0,
            display: "flex",
            alignItems: "center",
            gap: 70 * s.u,
            transformOrigin: "30% 50%",
            transform: `scale(${push(s.frame, s.dur, 0.05)})`,
          }}
        >
          {number}
          {words}
        </div>
      )}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- big number, with its curve when there is data

const niceTop = (v: number): number => {
  if (v <= 0) return 1;
  const mag = Math.pow(10, Math.floor(Math.log10(v)));
  return [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].map((m) => m * mag).find((x) => x >= v) ?? 10 * mag;
};

const compact = (v: number): string => {
  const a = Math.abs(v);
  const f = (x: number, s: string) => `${Number(x.toFixed(x < 10 ? 1 : 0))}${s}`;
  if (a >= 1e9) return f(v / 1e9, "B");
  if (a >= 1e6) return f(v / 1e6, "M");
  if (a >= 1e3) return f(v / 1e3, "K");
  return a < 10 && a % 1 ? v.toFixed(1) : String(Math.round(v));
};

// A smooth path through the points (Catmull-Rom as cubic Bezier).
const smoothPath = (pts: [number, number][]): string => {
  if (pts.length < 2) return "";
  let d = `M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C ${c1[0].toFixed(1)} ${c1[1].toFixed(1)}, ${c2[0].toFixed(1)} ${c2[1].toFixed(1)}, ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  return d;
};

const Chart: React.FC<{
  id: string;
  series: number[];
  w: number;
  h: number;
  progress: number;
  color: string;
  ink: string;
  u: number;
  family: string;
  xLabels: string[];
  pulse: number;
  bn: boolean;
}> = ({ id, series, w, h, progress, color, ink, u, family, xLabels, pulse, bn }) => {
  const lo = Math.min(0, ...series);
  const top = niceTop(Math.max(...series) * 1.05);
  const n = series.length;
  const X = (i: number) => (i / (n - 1)) * w;
  const Y = (v: number) => h - ((v - lo) / (top - lo)) * h;
  const pts = series.map((v, i) => [X(i), Y(v)] as [number, number]);
  const d = smoothPath(pts);
  const pos = progress * (n - 1);
  const i0 = Math.min(n - 2, Math.floor(pos));
  const f = pos - i0;
  const tip = { x: X(pos), y: Y(series[i0] + (series[i0 + 1] - series[i0]) * f) };
  const ticks = [1, 2, 3, 4].map((k) => lo + ((top - lo) * k) / 4);
  const txt = (s: string) => (bn ? toBengaliDigits(s) : s);
  return (
    <svg width={w} height={h} style={{ overflow: "visible", position: "absolute", left: 0, top: 0 }}>
      <defs>
        <linearGradient id={`${id}-fill`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.24} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
        <clipPath id={`${id}-reveal`}>
          <rect x={-20 * u} y={-60 * u} width={progress * w + 20 * u} height={h + 120 * u} />
        </clipPath>
      </defs>
      {ticks.map((v, i) => (
        <g key={i}>
          <line x1={0} x2={w} y1={Y(v)} y2={Y(v)} stroke={ink} strokeOpacity={0.08} strokeWidth={2 * u} />
          <text x={-16 * u} y={Y(v)} textAnchor="end" dominantBaseline="middle" fontSize={(bn ? 25 : 22) * u} fill={ink} fillOpacity={0.45} fontFamily={family} fontWeight={600}>
            {txt(compact(v))}
          </text>
        </g>
      ))}
      <line x1={0} x2={w} y1={Y(lo)} y2={Y(lo)} stroke={ink} strokeOpacity={0.25} strokeWidth={3 * u} />
      <g clipPath={`url(#${id}-reveal)`}>
        <path d={`${d} L ${w} ${Y(lo)} L 0 ${Y(lo)} Z`} fill={`url(#${id}-fill)`} />
        <path d={d} fill="none" stroke={color} strokeWidth={7 * u} strokeLinecap="round" strokeLinejoin="round" />
      </g>
      {pulse > 0 ? (
        <circle cx={tip.x} cy={tip.y} r={(11 + 26 * pulse) * u} fill="none" stroke={color} strokeWidth={3 * u} opacity={1 - pulse} />
      ) : null}
      <circle cx={tip.x} cy={tip.y} r={11 * u} fill={color} stroke="#FFFFFF" strokeWidth={4 * u} />
      {xLabels.length ? (
        <>
          <text x={0} y={h + 40 * u} fontSize={(bn ? 27 : 24) * u} fill={ink} fillOpacity={0.55} fontFamily={family} fontWeight={600}>
            {xLabels[0]}
          </text>
          <text x={w} y={h + 40 * u} textAnchor="end" fontSize={(bn ? 27 : 24) * u} fill={ink} fillOpacity={0.55} fontFamily={family} fontWeight={600}>
            {xLabels[xLabels.length - 1]}
          </text>
        </>
      ) : null}
    </svg>
  );
};

const BigStat: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const value = String(p.value ?? "");
  const title = linesOf(p, "title", "_");
  const label = String(p.label ?? "");
  const source = p.source ? String(p.source) : "";
  const series: number[] = Array.isArray(p.series) ? p.series.map(Number).filter((v: number) => Number.isFinite(v)) : [];
  const chart = series.length >= 2;
  const ink = paperTextOf(s.t);
  const color = p.color || s.pal[0];
  const all = [value, label, ...title].join(" ");
  const bn = isBengali(all);
  const fam = displayFont(s.t, all);
  const card = spring({ frame: s.frame, fps: s.fps, config: { damping: 200 }, durationInFrames: 18 });
  const tIn = interpolate(s.frame, [4, 16], [0, 1], { ...clampOpts, easing: easeOut });
  const drawEnd = s.ev.land ?? Math.min(s.dur - 12, 12 + Math.max(24, Math.round(0.35 * s.dur)));
  const prog = interpolate(s.frame, [12, drawEnd], [0, 1], { ...clampOpts, easing: Easing.inOut(Easing.sin) });
  const land = interpolate(s.frame, [drawEnd, drawEnd + 5, drawEnd + 12], [1, 1.1, 1], clampOpts);
  const pulse = s.frame > drawEnd ? ((s.frame - drawEnd) % 24) / 24 : 0;
  const c = cardRect(s);
  const pad = (s.vertical ? 70 : 90) * s.u;
  const colW = chart && !s.vertical ? c.w * 0.42 : c.w - 2 * pad;
  // a tall frame with a chart: smaller words, so the curve gets room under them inside the short safe area
  const stack = s.vertical && chart;
  const titleSize = fitSize(title, (stack ? 58 : chart ? 76 : 64) * s.u * (bn ? 0.9 : 1), colW);
  const numSize = fitSize([value], (stack ? 140 : chart ? 190 : 230) * s.u, colW, { floor: 0.4 });
  const labelSize = (stack ? 34 : 40) * s.u * (bn ? 0.92 : 1);
  const centred = !chart || s.vertical;
  const text = (
    <div style={{ textAlign: centred ? "center" : "left", opacity: tIn, transform: `translateY(${(1 - tIn) * 30 * s.u}px)` }}>
      {title.length ? (
        <div style={{ fontFamily: fam, fontWeight: 800, fontSize: titleSize, lineHeight: bn ? 1.3 : 1.05, letterSpacing: bn ? 0 : "-0.02em", color: ink }}>
          {title.map((l, i) => (
            <div key={i} style={{ whiteSpace: "nowrap" }}>
              {l}
            </div>
          ))}
        </div>
      ) : null}
      <div
        style={{
          marginTop: 26 * s.u,
          fontFamily: fam,
          fontWeight: 800,
          fontSize: numSize,
          lineHeight: 1,
          letterSpacing: bn ? 0 : "-0.03em",
          color,
          fontVariantNumeric: "tabular-nums",
          transformOrigin: centred ? "50% 70%" : "0% 70%",
          transform: `scale(${land})`,
          whiteSpace: "nowrap",
        }}
      >
        {countUp(value, prog)}
      </div>
      {label ? (
        <div style={{ marginTop: (stack ? 12 : 18) * s.u, fontFamily: fam, fontWeight: 600, fontSize: labelSize, lineHeight: bn ? 1.4 : 1.2, color: mix(ink, "#FFFFFF", 0.2) }}>
          {label}
        </div>
      ) : null}
    </div>
  );
  // on a tall frame the chart goes under the words: their height is added up so the two never meet
  const textH =
    (title.length ? title.length * titleSize * (bn ? 1.3 : 1.05) : 0) +
    26 * s.u +
    numSize +
    (label ? 12 * s.u + labelSize * (bn ? 1.4 : 1.2) : 0);
  const vTextTop = c.y + 45 * s.u;
  const vChartTop = vTextTop + textH + 44 * s.u;
  const vChartBottom = c.y + c.h - (source ? 110 : 76) * s.u;
  const chartW = s.vertical ? c.w - 2 * pad - 60 * s.u : c.w * 0.44;
  const chartH = s.vertical ? Math.max(120 * s.u, vChartBottom - vChartTop) : c.h * 0.52;
  return (
    <AbsoluteFill>
      <Paper theme={s.t} />
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.035)})` }}>
        <div
          style={{
            position: "absolute",
            left: c.x,
            top: c.y,
            width: c.w,
            height: c.h,
            borderRadius: 36 * s.u,
            backgroundColor: "#FFFFFF",
            boxShadow: cardShadow(s.u),
            opacity: card,
            transform: `translateY(${(1 - card) * 80 * s.u}px)`,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: c.x + pad,
            width: centred ? c.w - 2 * pad : colW,
            top: s.vertical && chart ? vTextTop : c.y + pad,
            height: s.vertical && chart ? textH : c.h - 2 * pad,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          {text}
        </div>
        {chart ? (
          <div
            style={{
              position: "absolute",
              left: s.vertical ? c.x + pad + 60 * s.u : c.x + c.w - pad - chartW,
              top: s.vertical ? vChartTop : c.y + (c.h - chartH) / 2 - 10 * s.u,
              width: chartW,
              height: chartH,
              opacity: interpolate(s.frame, [8, 16], [0, 1], clampOpts),
            }}
          >
            <Chart
              id={`chart-${overlay.id}`}
              series={series}
              w={chartW}
              h={chartH}
              progress={prog}
              color={color}
              ink={ink}
              u={s.u}
              family={fam}
              xLabels={Array.isArray(p.xLabels) ? p.xLabels.map(String) : []}
              pulse={pulse}
              bn={s.bnDigits}
            />
          </div>
        ) : null}
        {source ? (
          <div
            style={{
              position: "absolute",
              left: c.x + pad,
              top: c.y + c.h - (stack ? 50 : 64) * s.u,
              fontFamily: displayFont(s.t, source),
              fontWeight: 500,
              fontSize: (isBengali(source) ? 27 : 24) * s.u,
              color: mix(ink, "#FFFFFF", 0.5),
              opacity: tIn,
            }}
          >
            {source}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- bars that grow in turn

const Bars: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const rows: { label: string; value: number; text?: string }[] = (Array.isArray(p.rows) ? p.rows : []).map((r: Props) => ({
    label: String(r.label ?? ""),
    value: Math.max(0, Number(r.value) || 0),
    text: r.text != null ? String(r.text) : undefined,
  }));
  const n = Math.max(1, rows.length);
  const maxV = Math.max(1e-9, ...rows.map((r) => r.value));
  const focus = Number.isInteger(s.ev.focus)
    ? Number(s.ev.focus)
    : Number.isInteger(p.focus)
      ? Number(p.focus)
      : rows.reduce((b, r, i) => (r.value > rows[b].value ? i : b), 0);
  const title = linesOf(p, "title", "_");
  const note = p.note ? String(p.note) : "";
  const ink = paperTextOf(s.t);
  const color = p.color || s.pal[0];
  const all = [...title, ...rows.map((r) => r.label + " " + (r.text ?? ""))].join(" ");
  const bn = isBengali(all);
  const fam = displayFont(s.t, all);
  const card = spring({ frame: s.frame, fps: s.fps, config: { damping: 200 }, durationInFrames: 18 });
  const tIn = interpolate(s.frame, [4, 16], [0, 1], { ...clampOpts, easing: easeOut });
  // bars start after the title, one after another; the focus bar grows slowest and lands with a bounce
  const t0 = s.ev.start ?? 20;
  const step = s.ev.step ?? Math.floor(Math.max(n * 10, Math.round(0.42 * s.dur)) / n);
  const len = s.ev.len ?? Math.max(12, Math.round(step * 1.1));
  const starts = rows.map((_, i) => t0 + i * step);
  const lens = rows.map((_, i) => (i === focus ? Math.round(len * 1.8) : len));
  const done = s.ev.land ?? (starts[focus] ?? t0) + (lens[focus] ?? len);
  const c = cardRect(s);
  const pad = (s.vertical ? 64 : 90) * s.u;
  const padY = (s.vertical ? 56 : 70) * s.u;
  const titleSize = fitSize(title, 76 * s.u * (bn ? 0.9 : 1), c.w - 2 * pad);
  const titleH = title.length ? titleSize * (bn ? 1.3 : 1.08) * title.length + 36 * s.u : 0;
  const top = c.y + padY + titleH;
  const bottom = c.y + c.h - padY - (note ? 36 * s.u : 0);
  const gap = Math.min(130 * s.u, (bottom - top) / n);
  const labelSize = Math.min((s.vertical ? 36 : 44) * s.u, gap * 0.42) * (bn ? 0.95 : 1);
  const labelW = Math.min(c.w * 0.3, Math.max(...rows.map((r) => graphemes(r.label))) * labelSize * (bn ? 0.74 : 0.58) + 24 * s.u);
  const valueW = (s.vertical ? 190 : 260) * s.u;
  const barMax = c.w - 2 * pad - labelW - valueW;
  const barH = Math.min(72 * s.u, gap * 0.56);
  const valueSize = (isFocus: boolean) => Math.min((isFocus ? 64 : 48) * s.u * (s.vertical ? 0.8 : 1), gap * 0.6);
  return (
    <AbsoluteFill>
      <Paper theme={s.t} />
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.035)})` }}>
        <div
          style={{
            position: "absolute",
            left: c.x,
            top: c.y,
            width: c.w,
            height: c.h,
            borderRadius: 36 * s.u,
            backgroundColor: "#FFFFFF",
            boxShadow: cardShadow(s.u),
            opacity: card,
            transform: `translateY(${(1 - card) * 80 * s.u}px)`,
          }}
        />
        {title.length ? (
          <div
            style={{
              position: "absolute",
              left: c.x + pad,
              top: c.y + padY,
              fontFamily: fam,
              fontWeight: 800,
              fontSize: titleSize,
              lineHeight: bn ? 1.3 : 1.08,
              letterSpacing: bn ? 0 : "-0.02em",
              color: ink,
              opacity: tIn,
              transform: `translateY(${(1 - tIn) * 30 * s.u}px)`,
            }}
          >
            {title.map((l, i) => (
              <div key={i} style={{ whiteSpace: "nowrap" }}>
                {l}
              </div>
            ))}
          </div>
        ) : null}
        {rows.map((r, i) => {
          const isFocus = i === focus;
          const grow = interpolate(s.frame, [starts[i], starts[i] + lens[i]], [0, 1], {
            ...clampOpts,
            easing: isFocus ? Easing.inOut(Easing.cubic) : Easing.out(Easing.cubic),
          });
          const rowIn = interpolate(s.frame, [starts[i] - 8, starts[i]], [0, 1], clampOpts);
          const width = Math.max(26 * s.u, (barMax * r.value) / maxV) * Math.min(1, grow * 3);
          const dec = (String(r.value).split(".")[1] || "").length;
          const shown = r.text !== undefined ? countUp(r.text, grow) : digits(formatNumber(r.value * grow, dec, false), s.bnDigits);
          const land = isFocus ? interpolate(s.frame, [done, done + 5, done + 12], [1, 1.12, 1], clampOpts) : 1;
          const y = top + i * gap + (gap - barH) / 2;
          const fill = isFocus
            ? `linear-gradient(90deg, ${mix(color, "#FFFFFF", 0.28)} 0%, ${color} 100%)`
            : `linear-gradient(90deg, ${mix(color, "#FFFFFF", 0.72)} 0%, ${mix(color, "#FFFFFF", 0.5)} 100%)`;
          const labelEl = (
            <div
              style={{
                width: labelW,
                fontFamily: fam,
                fontWeight: 700,
                fontSize: labelSize,
                lineHeight: bn ? 1.3 : 1.1,
                color: mix(ink, "#FFFFFF", 0.12),
                whiteSpace: "nowrap",
              }}
            >
              {r.label}
            </div>
          );
          return (
            <div key={i} style={{ position: "absolute", left: c.x + pad, top: y, opacity: rowIn }}>
              <div style={{ display: "flex", alignItems: "center", height: barH }}>
                {labelEl}
                <div style={{ width, height: barH, borderRadius: barH / 2, background: fill }} />
                <div
                  style={{
                    marginLeft: 26 * s.u,
                    fontFamily: fam,
                    fontWeight: 800,
                    fontSize: valueSize(isFocus),
                    color: isFocus ? color : mix(ink, "#FFFFFF", 0.3),
                    fontVariantNumeric: "tabular-nums",
                    transformOrigin: "0% 50%",
                    transform: `scale(${land})`,
                    whiteSpace: "nowrap",
                  }}
                >
                  {shown}
                </div>
              </div>
            </div>
          );
        })}
        {note ? (
          <div
            style={{
              position: "absolute",
              left: c.x + pad,
              top: c.y + c.h - padY - 8 * s.u,
              fontFamily: displayFont(s.t, note),
              fontWeight: 500,
              fontSize: (isBengali(note) ? 28 : 26) * s.u,
              color: mix(ink, "#FFFFFF", 0.5),
              opacity: tIn,
            }}
          >
            {note}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- before and after, side by side

type Side = { label?: string; text?: string; value?: string; source?: string; color?: string };

const sideOf = (x: unknown): Side => (typeof x === "string" ? { text: x } : ((x || {}) as Side));

// A hand-drawn divider that boils a little (redrawn every 4 frames).
const Divider: React.FC<{ vertical: boolean; progress: number; color: string; seed: string; at: number }> = ({ vertical, progress, color, seed, at }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = unit(W, H);
  const k = Math.floor(frame / 4);
  const pts = Array.from({ length: 9 }).map((_, i) => {
    const t = i / 8;
    const wob = (smoothNoise(`${seed}-${k}`, i * 1.7) - 0.5) * 16 * u;
    return vertical ? [t * W, at + wob] : [at + wob, t * H];
  });
  const d = pts.map((q, i) => `${i ? "L" : "M"} ${q[0].toFixed(1)} ${q[1].toFixed(1)}`).join(" ");
  const clip = vertical ? `inset(0 ${(1 - progress) * 100}% 0 0)` : `inset(0 0 ${(1 - progress) * 100}% 0)`;
  return (
    <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0, clipPath: clip, overflow: "visible" }}>
      <path d={d} fill="none" stroke={color} strokeWidth={14 * u} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

const Versus: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const sides = [sideOf(p.left), sideOf(p.right)];
  const enter = [0, 5].map((d) => spring({ frame: s.frame - d, fps: s.fps, config: { damping: 18, stiffness: 140 } }));
  const div = interpolate(s.frame, [6, 18], [0, 1], { ...clampOpts, easing: easeOut });
  const seam = s.vertical ? Math.round(s.safe.y + (s.floor - s.safe.y) / 2) : Math.round(s.W / 2);
  const colors = [sides[0].color || "#E7E1D8", sides[1].color || s.pal[0]];
  return (
    <AbsoluteFill style={{ backgroundColor: "#111111", overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.05)})` }}>
      {sides.map((side, i) => {
        const x0 = s.vertical ? 0 : i * seam;
        const y0 = s.vertical ? i * seam : 0;
        const half = s.vertical ? { w: s.W, h: i === 0 ? seam : s.H - seam } : { w: i === 0 ? seam : s.W - seam, h: s.H };
        // where this side's words go: its share of the safe area (on a tall frame, above the captions)
        const zone = s.vertical
          ? i === 0
            ? { top: s.safe.y - y0, bottom: half.h }
            : { top: 0, bottom: s.floor - y0 }
          : { top: 0, bottom: half.h };
        const off = (1 - enter[i]) * (i === 0 ? -1 : 1);
        const bg = colors[i];
        const fg = side.source ? "#FFFFFF" : onColor(bg);
        const words = [side.value, side.text].filter(Boolean).join(" ");
        const bn = isBengali(words + (side.label || ""));
        const innerW = half.w * 0.8;
        const valueSize = side.value ? fitSize([String(side.value)], (s.vertical ? 150 : 160) * s.u, innerW, { floor: 0.4 }) : 0;
        const textSize = side.text ? fitSize([String(side.text)], (side.value ? 54 : 84) * s.u * (bn ? 0.9 : 1), innerW) : 0;
        const padX = s.vertical ? s.safe.x + 10 * s.u : i === 0 ? s.safe.x + 10 * s.u : 56 * s.u;
        const chipTop = s.vertical ? zone.top + (i === 0 ? 10 : 30) * s.u : s.safe.y + 20 * s.u;
        const valIn = interpolate(s.frame, [10 + i * 6, 34 + i * 6], [0, 1], { ...clampOpts, easing: easeOut });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x0,
              top: y0,
              width: half.w,
              height: half.h,
              overflow: "hidden",
              backgroundColor: bg,
            }}
          >
            {side.source ? (
              <>
                <Media edl={edl} sourceId={side.source} w={half.w} h={half.h} scale={push(s.frame, s.dur, 0.08)} />
                {words ? (
                  <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: half.h * 0.5, background: "linear-gradient(0deg, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0) 100%)" }} />
                ) : null}
              </>
            ) : (
              <Bubbles seed={`vs-${overlay.id}-${i}`} count={6} alpha={luminance(bg) > 0.5 ? 0.22 : 0.1} speed={2} />
            )}
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: side.source ? Math.max(zone.top, half.h * 0.5) : zone.top + (s.vertical ? 60 * s.u : 0),
                bottom: side.source ? (s.vertical ? half.h - zone.bottom + 20 * s.u : s.H - s.safe.y - s.safe.h + 60 * s.u) : half.h - zone.bottom,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: side.source ? "flex-end" : "center",
                textAlign: "center",
                color: fg,
                opacity: Math.min(valIn, enter[i] * 1.5),
                transform: `translateX(${off * half.w * 0.35}px) scale(${push(s.frame, s.dur, 0.04)})`,
              }}
            >
              {side.value ? (
                <div
                  style={{
                    fontFamily: displayFont(s.t, String(side.value)),
                    fontWeight: 800,
                    fontSize: valueSize,
                    lineHeight: 1,
                    letterSpacing: bn ? 0 : "-0.03em",
                    whiteSpace: "nowrap",
                    transform: `scale(${1 + (valIn >= 1 ? 0.015 * Math.sin((s.frame - 34) / 9) : 0)})`,
                  }}
                >
                  {countUp(String(side.value), valIn)}
                </div>
              ) : null}
              {side.text ? (
                <div
                  style={{
                    marginTop: side.value ? 16 * s.u : 0,
                    fontFamily: displayFont(s.t, String(side.text)),
                    fontWeight: side.value ? 700 : 800,
                    fontSize: textSize,
                    lineHeight: bn ? 1.3 : 1.1,
                    letterSpacing: bn ? 0 : "-0.02em",
                    whiteSpace: "nowrap",
                  }}
                >
                  {side.text}
                </div>
              ) : null}
            </div>
            {side.label ? (
              <Chip text={side.label} theme={s.t} delay={8 + i * 6} tone={luminance(bg) > 0.6 && !side.source ? "dark" : "light"} style={{ left: padX, top: chipTop }} />
            ) : null}
          </div>
        );
      })}
      <Divider vertical={s.vertical} progress={div} color={highlightOf(s.t)} seed={overlay.id} at={seam} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- recap cards

const Recap: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const items: { label: string; text?: string; source?: string }[] = (Array.isArray(p.items) ? p.items : []).map((it: Props | string) =>
    typeof it === "string" ? { label: it } : { label: String(it.label ?? ""), text: it.text != null ? String(it.text) : undefined, source: it.source },
  );
  const n = Math.max(1, items.length);
  const title = linesOf(p, "title", "_");
  const base = p.color || s.pal[1];
  const bg = `radial-gradient(ellipse at 50% 42%, ${mix(base, "#000000", 0.62)} 0%, ${mix(base, "#000000", 0.84)} 60%, #09070C 100%)`;
  const bnT = isBengali(title.join(" "));
  const titleSize = fitSize(title, 68 * s.u * (bnT ? 0.9 : 1), s.safe.w * 0.9);
  const titleH = title.length ? titleSize * (bnT ? 1.3 : 1.1) * title.length + 40 * s.u : 0;
  const cols = s.vertical ? Math.min(2, n) : n;
  const rows = Math.ceil(n / cols);
  const gapX = 48 * s.u;
  const labelH = 90 * s.u;
  const availW = (s.right - s.left) * 0.94;
  const availH = s.floor - s.safe.y - titleH - 40 * s.u;
  let cw = Math.min(460 * s.u, (availW - (cols - 1) * gapX) / cols);
  let ch = cw * 1.18;
  const fitH = (availH - rows * labelH - (rows - 1) * 30 * s.u) / rows;
  if (ch > fitH) {
    ch = fitH;
    cw = ch / 1.18;
  }
  const gridW = cols * cw + (cols - 1) * gapX;
  const gridH = rows * (ch + labelH) + (rows - 1) * 30 * s.u;
  const top0 = s.safe.y + titleH + (s.floor - s.safe.y - titleH - gridH) / 2;
  const left0 = (s.left + s.right - gridW) / 2;
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <Bubbles seed={`recap-${overlay.id}`} count={5} alpha={0.04} />
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.035)})` }}>
        {title.length ? (
          <div style={{ position: "absolute", left: s.safe.x, width: s.safe.w, top: s.safe.y + 10 * s.u, display: "flex", justifyContent: "center" }}>
            <Words lines={title} size={titleSize} color="#FFFFFF" family={displayFont(s.t, title.join(" "))} weight={800} start={2} stagger={3} />
          </div>
        ) : null}
        {items.map((it, i) => {
          const col = i % cols;
          const row = Math.floor(i / cols);
          const inRow = Math.min(cols, n - row * cols);
          const rowShift = ((cols - inRow) * (cw + gapX)) / 2;
          const pop = spring({ frame: s.frame - 6 - i * 6, fps: s.fps, config: { damping: 14, stiffness: 150 } });
          const tilt = (i % 2 ? 2.2 : -2.2) * (1 - 0.45 * pop);
          const float = Math.sin((s.frame + i * 20) / 18) * 6 * s.u;
          const x = left0 + rowShift + col * (cw + gapX);
          const y = top0 + row * (ch + labelH + 30 * s.u);
          const fill = s.pal[i % s.pal.length];
          const big = it.text ?? digits(String(i + 1), s.bnDigits);
          const bn = isBengali(it.label + " " + big);
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: x,
                top: y,
                width: cw,
                transform: `translateY(${(1 - pop) * 60 * s.u + float}px) scale(${0.85 + 0.15 * pop}) rotate(${tilt}deg)`,
                opacity: Math.min(1, pop * 1.4),
              }}
            >
              <div
                style={{
                  position: "relative",
                  width: cw,
                  height: ch,
                  borderRadius: 30 * s.u,
                  border: `${10 * s.u}px solid #FFFFFF`,
                  overflow: "hidden",
                  backgroundColor: fill,
                  boxShadow: `0 ${24 * s.u}px ${60 * s.u}px rgba(0, 0, 0, 0.4)`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxSizing: "border-box",
                }}
              >
                {it.source && edl.sources[it.source] ? (
                  <Media edl={edl} sourceId={it.source} w={cw - 20 * s.u} h={ch - 20 * s.u} scale={push(s.frame, s.dur, 0.06)} />
                ) : (
                  <div style={{ fontFamily: displayFont(s.t, big), fontWeight: 800, fontSize: fitSize([big], cw * 0.42, cw * 0.78, { floor: 0.35 }), color: onColor(fill), lineHeight: 1 }}>{big}</div>
                )}
              </div>
              <div
                style={{
                  marginTop: 22 * s.u,
                  textAlign: "center",
                  fontFamily: displayFont(s.t, it.label),
                  fontWeight: 700,
                  fontSize: fitSize([it.label], 44 * s.u * (bn ? 0.92 : 1), cw + gapX * 0.8),
                  lineHeight: bn ? 1.3 : 1.1,
                  color: "#FFFFFF",
                  whiteSpace: "nowrap",
                }}
              >
                {it.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- end card with a subscribe click

const BELL = "M12 3a6 6 0 0 0-6 6v3.6L4.2 16h15.6L18 12.6V9a6 6 0 0 0-6-6zm-2.4 14.5a2.4 2.4 0 0 0 4.8 0z";

const EndCard: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const lines = linesOf(p);
  const text = lines.join(" ");
  const bn = isBengali(text);
  const color = p.color || s.pal[0];
  const clickAt = s.ev.click ?? Math.min(84, s.dur - 30);
  const button = p.button ? String(p.button) : "";
  const pressed = p.pressed ? String(p.pressed) : button;
  const size = fitSize(lines, (s.vertical ? 96 : 116) * s.u * (bn ? 0.9 : 1), s.safe.w * 0.86);
  const n = text.split(/\s+/).filter(Boolean).length;
  const btnIn = spring({ frame: s.frame - Math.max(10, Math.round(6 + n * 4)), fps: s.fps, config: { damping: 12, stiffness: 160 } });
  const subscribed = !!button && s.frame >= clickAt + 2;
  const label = subscribed ? pressed : button;
  const bs = 50 * s.u * (isBengali(label) ? 0.9 : 1);
  const bw = Math.max(460 * s.u, graphemes(label) * bs * (isBengali(label) ? 0.62 : 0.6) + (p.icon === "none" ? 110 : 180) * s.u);
  const bh = 124 * s.u;
  const bx = s.W / 2;
  const by = s.H * (s.vertical ? 0.62 : 0.68);
  const travel = interpolate(s.frame, [clickAt - 32, clickAt - 4], [0, 1], { ...clampOpts, easing: Easing.bezier(0.33, 0, 0.2, 1) });
  const cx = interpolate(travel, [0, 1], [s.W * 0.82, bx + bw * 0.22]);
  const cy = interpolate(travel, [0, 1], [s.H * 0.94, by + bh * 0.1]);
  const press = interpolate(s.frame, [clickAt, clickAt + 3, clickAt + 12], [1, 0.92, 1], clampOpts);
  const ripple = interpolate(s.frame, [clickAt, clickAt + 16], [0, 1], clampOpts);
  const age = s.frame - clickAt - 2;
  const bell = age >= 0 ? 22 * Math.exp(-age / 10) * Math.sin(age * 0.9) : 0;
  const cursorOp = interpolate(s.frame, [clickAt - 34, clickAt - 28, clickAt + 36, clickAt + 46], [0, 1, 1, 0], clampOpts);
  return (
    <AbsoluteFill style={{ background: `linear-gradient(140deg, ${mix(color, "#FFFFFF", 0.22)} 0%, ${color} 60%, ${mix(color, "#000000", 0.1)} 100%)`, overflow: "hidden" }}>
      <Bubbles seed={`end-${overlay.id}`} />
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.04)})` }}>
        <div
          style={{
            position: "absolute",
            left: s.safe.x,
            width: s.safe.w,
            top: 0,
            height: button ? by - bh * 0.9 : s.H,
            display: "flex",
            alignItems: button ? "flex-end" : "center",
            justifyContent: "center",
          }}
        >
          <Words lines={lines} size={size} color="#FFFFFF" family={displayFont(s.t, text)} weight={800} start={6} stagger={4} lineHeight={bn ? 1.3 : 1.1} />
        </div>
        {button ? (
          <>
            <div
              style={{
                position: "absolute",
                left: bx - bw / 2,
                top: by - bh / 2,
                width: bw,
                height: bh,
                borderRadius: bh / 2,
                backgroundColor: subscribed ? "#2B1D16" : "#FFFFFF",
                color: subscribed ? "#FFF4E4" : mix(color, "#000000", 0.12),
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 18 * s.u,
                fontFamily: displayFont(s.t, label),
                fontWeight: 800,
                fontSize: bs,
                transform: `scale(${btnIn * press})`,
                boxShadow: `0 ${20 * s.u}px ${50 * s.u}px rgba(120, 40, 0, 0.35)`,
                whiteSpace: "nowrap",
              }}
            >
              {p.icon === "none" ? null : (
                <svg width={52 * s.u} height={52 * s.u} viewBox="0 0 24 24" style={{ transform: `rotate(${bell}deg)` }}>
                  <path d={BELL} fill={subscribed ? highlightOf(s.t) : mix(color, "#000000", 0.12)} />
                </svg>
              )}
              {label}
            </div>
            {ripple > 0 && ripple < 1 ? (
              <div
                style={{
                  position: "absolute",
                  left: cx - (40 + 90 * ripple) * s.u,
                  top: cy - (40 + 90 * ripple) * s.u,
                  width: (80 + 180 * ripple) * s.u,
                  height: (80 + 180 * ripple) * s.u,
                  borderRadius: "50%",
                  border: `${6 * s.u}px solid rgba(255, 255, 255, 0.9)`,
                  opacity: 1 - ripple,
                }}
              />
            ) : null}
            <svg
              width={56 * s.u}
              height={70 * s.u}
              viewBox="0 0 28 42"
              style={{
                position: "absolute",
                left: cx,
                top: cy,
                opacity: cursorOp,
                transformOrigin: "0 0",
                transform: `scale(${s.frame >= clickAt && s.frame < clickAt + 6 ? 0.88 : 1})`,
                filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.3))",
              }}
            >
              <path d="M1,1 L1,33 L9,26 L15,40 L21,37 L15,24 L26,24 Z" fill="#FFFFFF" stroke="#1E1B2E" strokeWidth={2} strokeLinejoin="round" />
            </svg>
          </>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- a picture as a designed card

const Photo: React.FC<P> = ({ edl, overlay }) => {
  const s = useScene(edl, overlay);
  const p = overlay.props;
  const src = edl.sources[p.source];
  if (!src) return null;
  const label = p.label ? String(p.label) : "";
  const trim = Number(p.trimBefore || 0);
  if ((p.style || "card") === "full") {
    const z = p.motion === "pull" ? 1.1 - 0.08 * Math.min(1, s.frame / s.dur) : push(s.frame, s.dur, 0.08);
    return (
      <AbsoluteFill style={{ backgroundColor: "#000000", overflow: "hidden" }}>
        <Media edl={edl} sourceId={p.source} w={s.W} h={s.H} scale={z} trimBefore={trim} />
        {label ? <Chip text={label} theme={s.t} delay={6} style={{ left: s.safe.x + 10 * s.u, top: s.safe.y + 10 * s.u }} /> : null}
      </AbsoluteFill>
    );
  }
  const aspect = Math.max(0.75, Math.min(1.9, (src.width || 16) / (src.height || 9)));
  const caption = p.caption ? String(p.caption) : "";
  const roomTop = s.safe.y + 40 * s.u;
  const roomH = s.floor - 30 * s.u - roomTop;
  const maxW = s.vertical ? s.safe.w * 0.92 : Math.min(s.W * 0.56, (s.right - s.left) * 0.9);
  const maxH = Math.min(s.vertical ? s.safe.h * 0.56 : s.H * 0.7, roomH - 40 * s.u) - (caption ? 80 * s.u : 0);
  let w = maxW;
  let h = w / aspect;
  if (h > maxH) {
    h = maxH;
    w = h * aspect;
  }
  const b = 14 * s.u;
  const enter = spring({ frame: s.frame, fps: s.fps, config: { damping: 16, stiffness: 120 } });
  const rot = -4 + 2.6 * enter;
  const x = (s.left + s.right - w) / 2;
  const y = roomTop + (roomH - h - (caption ? 80 * s.u : 0)) / 2;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {p.bg ? <AbsoluteFill style={{ backgroundColor: p.bg }} /> : <Paper theme={s.t} />}
      <AbsoluteFill style={{ transform: `scale(${push(s.frame, s.dur, 0.035)})` }}>
        <div
          style={{
            position: "absolute",
            left: x - b,
            top: y - b,
            width: w + 2 * b,
            height: h + 2 * b,
            borderRadius: 28 * s.u,
            backgroundColor: "#FFFFFF",
            boxShadow: `0 ${30 * s.u}px ${70 * s.u}px rgba(40, 20, 10, 0.25)`,
            transform: `translateY(${(1 - enter) * 60 * s.u}px) scale(${0.94 + 0.06 * enter}) rotate(${rot}deg)`,
            opacity: Math.min(1, enter * 1.5),
          }}
        >
          <div style={{ position: "absolute", left: b, top: b, width: w, height: h, borderRadius: 18 * s.u, overflow: "hidden", backgroundColor: "#222222" }}>
            <Media edl={edl} sourceId={p.source} w={w} h={h} scale={1.04 + 0.08 * Math.min(1, s.frame / s.dur)} trimBefore={trim} />
          </div>
          {label ? <Chip text={label} theme={s.t} delay={8} style={{ left: -18 * s.u, top: -30 * s.u }} /> : null}
        </div>
        {caption ? (
          <div
            style={{
              position: "absolute",
              left: s.safe.x,
              width: s.safe.w,
              top: y + h + b + 40 * s.u,
              textAlign: "center",
              fontFamily: displayFont(s.t, caption),
              fontWeight: 700,
              fontSize: fitSize([caption], 44 * s.u, s.safe.w * 0.9),
              color: p.bg ? onColor(p.bg) : paperTextOf(s.t),
              opacity: interpolate(s.frame, [10, 20], [0, 1], clampOpts),
            }}
          >
            {caption}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- label chip over anything (not a full scene)

export const LabelOverlay: React.FC<P> = ({ edl, overlay }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = unit(W, H);
  const p = overlay.props;
  const corner = String(p.corner || "tl");
  const out = interpolate(frame, [overlay.durationInFrames - 6, overlay.durationInFrames], [1, 0], clampOpts);
  const pos: React.CSSProperties = {};
  if (corner.includes("r")) pos.right = W - edl.safe.x - edl.safe.w + 10 * u;
  else pos.left = edl.safe.x + 10 * u;
  if (corner.startsWith("b")) pos.bottom = H - edl.safe.y - edl.safe.h + 10 * u;
  else pos.top = edl.safe.y + 10 * u;
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Chip text={String(p.text || "")} theme={edl.theme} tone={p.tone || "dark"} size={p.size || 34} style={pos} origin={corner.includes("r") ? "100% 50%" : "0% 50%"} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- colour bars that sweep across and hide a cut

export const BarSweep: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width: W, height: H } = useVideoConfig();
  const c = paletteOf(theme)[0];
  const colors = [mix(c, "#000000", 0.1), paperOf(theme), c, mix(c, "#FFFFFF", 0.55), highlightOf(theme)];
  const flex = [3, 0.35, 4, 0.5, 3];
  const BW = W + H * 0.25 + W * 0.12;
  const mid = (durationInFrames - 1) / 2;
  const left = interpolate(frame, [0, mid, durationInFrames - 1], [-BW - W * 0.16, W / 2 - BW / 2, W + W * 0.16], {
    ...clampOpts,
    easing: Easing.bezier(0.45, 0, 0.55, 1),
  });
  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: -0.06 * H, left, width: BW, height: H * 1.12, display: "flex", transform: "skewX(-12deg)" }}>
        {colors.map((col, i) => (
          <div key={i} style={{ flex: flex[i], backgroundColor: col }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- entering and leaving

// How a full scene comes in and goes out: slide (from the right), slideUp, pop, fade or cut. A sweep is drawn by the
// edit over the boundary, so the scene itself just cuts under it.
export const SceneMotion: React.FC<{ overlay: Overlay; children: React.ReactNode }> = ({ overlay, children }) => {
  const frame = useCurrentFrame();
  const { fps, width: W, height: H } = useVideoConfig();
  const dur = overlay.durationInFrames;
  const enter = overlay.enter || "cut";
  const exit = overlay.exit || "cut";
  let tx = 0;
  let ty = 0;
  let sc = 1;
  let op = 1;
  const inP = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 12 });
  if (enter === "slide") tx += (1 - inP) * W;
  else if (enter === "slideUp") ty += (1 - inP) * H;
  else if (enter === "pop") {
    sc *= 0.94 + 0.06 * inP;
    op *= interpolate(frame, [0, 6], [0, 1], clampOpts);
  } else if (enter === "fade") op *= interpolate(frame, [0, 8], [0, 1], clampOpts);
  const outP = spring({ frame: frame - (dur - 12), fps, config: { damping: 200 }, durationInFrames: 12 });
  if (exit === "slide") tx -= outP * W;
  else if (exit === "slideUp") ty -= outP * H;
  else if (exit === "fade") op *= interpolate(frame, [dur - 8, dur], [1, 0], clampOpts);
  else if (exit === "pop") {
    sc *= 1 - 0.06 * outP;
    op *= interpolate(frame, [dur - 6, dur], [1, 0], clampOpts);
  }
  return <AbsoluteFill style={{ transform: `translate(${tx}px, ${ty}px) scale(${sc})`, opacity: op }}>{children}</AbsoluteFill>;
};

export const SceneView: React.FC<P> = ({ edl, overlay }) => {
  let body: React.ReactNode = null;
  switch (overlay.type) {
    case "kinetic":
      body = <Kinetic edl={edl} overlay={overlay} />;
      break;
    case "step":
      body = <StepCard edl={edl} overlay={overlay} />;
      break;
    case "bigStat":
      body = <BigStat edl={edl} overlay={overlay} />;
      break;
    case "bars":
      body = <Bars edl={edl} overlay={overlay} />;
      break;
    case "versus":
      body = <Versus edl={edl} overlay={overlay} />;
      break;
    case "recap":
      body = <Recap edl={edl} overlay={overlay} />;
      break;
    case "endCard":
      body = <EndCard edl={edl} overlay={overlay} />;
      break;
    case "photo":
      body = <Photo edl={edl} overlay={overlay} />;
      break;
    default:
      return null;
  }
  return <SceneMotion overlay={overlay}>{body}</SceneMotion>;
};
