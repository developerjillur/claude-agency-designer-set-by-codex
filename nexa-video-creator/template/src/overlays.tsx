// On-screen graphics for the edit: hook titles, keyword pops, stat and list cards, comparisons, quotes, chapter
// cards, lower thirds, calls to action, b-roll and image inserts, and marks that sit on a recording (callouts and
// redactions). Sizes scale with the frame; placement follows the target's safe zone and bands from the EDL.
import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Video } from "@remotion/media";
import {
  Edl,
  Overlay,
  Rect,
  clampOpts,
  containRect,
  coverRect,
  easeOut,
  font,
  formatNumber,
  hexToRgba,
  inOut,
  isBengali,
  mediaSrc,
  splitNumber,
  unit,
} from "./lib";

const IMAGE = /\.(png|jpe?g|webp|gif|bmp)$/i;

export const isLayerOverlay = (o: Overlay): boolean =>
  (o.type === "callout" || o.type === "redact") && (o.props.layer ?? "screen") !== "frame";

type P = { edl: Edl; overlay: Overlay };

const useBasics = (edl: Edl) => {
  const frame = useCurrentFrame();
  const { width: W, height: H, fps } = useVideoConfig();
  return { frame, W, H, fps, u: unit(W, H), vertical: H > W, t: edl.theme };
};

const H_VERTICAL = (edl: Edl) => edl.height > edl.width;

const displayFont = (edl: Edl, text: string) => font(isBengali(text) ? "HindSiliguri" : edl.theme.display);
const bodyFont = (edl: Edl, text: string) => font(isBengali(text) ? "HindSiliguri" : edl.theme.body);

const clipAt = (edl: Edl, frame: number) => edl.clips.find((c) => frame >= c.from && frame < c.from + c.durationInFrames);

// Which side of a 16:9 frame is free for a card: away from the camera panel of a split, away from a picture-in-
// picture on the right, otherwise away from the speaker's face.
const freeSide = (edl: Edl, overlay: Overlay): "left" | "right" => {
  const end = overlay.from + overlay.durationInFrames;
  const spanned = edl.clips.filter((c) => c.from < end && overlay.from < c.from + c.durationInFrames);
  if (spanned.some((c) => c.layout === "split")) return "left";
  if (spanned.some((c) => c.layout === "screenPip" && c.pip.corner === "tr")) return "left";
  if (spanned.some((c) => c.layout === "screenPip" && c.pip.corner === "tl")) return "right";
  const clip = clipAt(edl, overlay.from);
  const cam = clip?.cam ? edl.sources[clip.cam.source] : Object.values(edl.sources).find((s) => s.face);
  return cam?.face && cam.face.x > 0.55 ? "left" : "right";
};

const shadow = (u: number, strength = 0.35) => `0 ${Math.round(18 * u)}px ${Math.round(48 * u)}px rgba(0,0,0,${strength})`;

// Words that pop in one after another; `highlight` words take the accent colour.
const WordsIn: React.FC<{
  text: string;
  frame: number;
  fps: number;
  size: number;
  color: string;
  accent: string;
  highlight?: string;
  family: string;
  weight?: number;
  align?: "center" | "left";
  upper?: boolean;
  stroke?: number;
}> = ({ text, frame, fps, size, color, accent, highlight, family, weight = 900, align = "center", upper, stroke = 0 }) => {
  const words = text.split(/\s+/).filter(Boolean);
  const hl = new Set((highlight || "").toLowerCase().split(/\s+/).filter(Boolean));
  const bn = isBengali(text);
  return (
    <div
      style={{
        fontFamily: family,
        fontWeight: weight,
        fontSize: size,
        lineHeight: bn ? 1.35 : 1.08,
        textAlign: align,
        color,
        textTransform: upper && !bn ? "uppercase" : "none",
        letterSpacing: bn ? 0 : "-0.01em",
        display: "flex",
        flexWrap: "wrap",
        justifyContent: align === "center" ? "center" : "flex-start",
        gap: `${Math.round(size * 0.12)}px ${Math.round(size * 0.24)}px`,
      }}
    >
      {words.map((w, i) => {
        const p = spring({ frame: frame - i * 2, fps, config: { damping: 16, stiffness: 180, mass: 0.7 } });
        const key = w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, "");
        const on = hl.has(key) || hl.has(w.toLowerCase());
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              transform: `translateY(${(1 - p) * size * 0.45}px)`,
              opacity: Math.min(1, p * 1.4),
              color: on ? accent : color,
              WebkitTextStroke: stroke ? `${stroke}px rgba(0,0,0,0.85)` : undefined,
              paintOrder: "stroke fill",
              textShadow: stroke ? undefined : `0 ${Math.round(size * 0.05)}px ${Math.round(size * 0.18)}px rgba(0,0,0,0.45)`,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

const Hook: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u, vertical, t } = useBasics(edl);
  const text = String(overlay.props.text || "");
  const band = edl.bands.title;
  const io = inOut(frame, overlay.durationInFrames, 0, 8);
  const size = Math.round((vertical ? 92 : 84) * u * (overlay.props.scale || 1));
  const boxed = overlay.props.box !== false;
  return (
    <AbsoluteFill style={{ opacity: io.out, transform: `translateY(${(1 - io.out) * -20 * u}px)` }}>
      <div style={{ position: "absolute", left: edl.safe.x, width: edl.safe.w, top: band.y, height: band.h, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            padding: boxed ? `${Math.round(18 * u)}px ${Math.round(30 * u)}px` : 0,
            borderRadius: Math.round(t.radius * u),
            backgroundColor: boxed ? hexToRgba(t.ink, 0.72) : "transparent",
            boxShadow: boxed ? shadow(u, 0.3) : undefined,
            maxWidth: edl.safe.w,
          }}
        >
          <WordsIn text={text} frame={frame} fps={fps} size={size} color={t.text} accent={t.accent} highlight={overlay.props.highlight} family={displayFont(edl, text)} upper={overlay.props.upper !== false && !vertical} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Keyword: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, W, H, u, vertical, t } = useBasics(edl);
  const text = String(overlay.props.text || "");
  const pop = spring({ frame, fps, config: { damping: 11, stiffness: 190, mass: 0.6 } });
  const io = inOut(frame, overlay.durationInFrames, 0, 6);
  const size = Math.round((vertical ? 130 : 150) * u * (overlay.props.scale || 1));
  const pos = overlay.props.position || "center";
  const top = pos === "top" ? edl.bands.title.y + edl.bands.title.h / 2 : pos === "bottom" ? edl.bands.lower.y + edl.bands.lower.h / 2 : H * (vertical ? 0.4 : 0.5);
  const bn = isBengali(text);
  // over the screen panel when the frame is split, so the word never lands on the speaker's face
  const clip = clipAt(edl, overlay.from);
  const areaW = clip?.layout === "split" ? Math.round(W * 0.72) : W;
  return (
    <AbsoluteFill style={{ opacity: io.out }}>
      <div style={{ position: "absolute", left: 0, width: areaW, top: top - size, height: size * 2, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        {overlay.props.emoji ? <div style={{ fontSize: size * 0.7, transform: `scale(${pop})` }}>{overlay.props.emoji}</div> : null}
        <div
          style={{
            fontFamily: displayFont(edl, text),
            fontWeight: 900,
            fontSize: size,
            lineHeight: bn ? 1.3 : 1,
            color: overlay.props.color || t.accent,
            textTransform: bn ? "none" : "uppercase",
            WebkitTextStroke: `${Math.round(size * (bn ? 0.05 : 0.07))}px ${t.ink}`,
            paintOrder: "stroke fill",
            transform: `scale(${0.4 + 0.6 * pop}) rotate(${(1 - pop) * -6 - 2}deg)`,
            maxWidth: edl.safe.w,
            textAlign: "center",
            textShadow: `0 ${Math.round(10 * u)}px ${Math.round(30 * u)}px rgba(0,0,0,0.35)`,
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// A card placed on the side away from the face (16:9) or in the title band (vertical).
const CardFrame: React.FC<{ edl: Edl; overlay: Overlay; width: number; children: React.ReactNode }> = ({ edl, overlay, width, children }) => {
  const { frame, fps, u: u0, vertical, t, H } = useBasics(edl);
  const u = u0 * (vertical ? 1.3 : 1);
  const io = inOut(frame, overlay.durationInFrames, 0, 8);
  const p = spring({ frame, fps, config: { damping: 18, stiffness: 150 } });
  const side = overlay.props.side || freeSide(edl, overlay);
  const left = vertical ? edl.safe.x + (edl.safe.w - width) / 2 : side === "right" ? edl.safe.x + edl.safe.w - width : edl.safe.x;
  const top = vertical ? edl.bands.title.y : Math.round(H * 0.2);
  const dx = vertical ? 0 : (side === "right" ? 1 : -1) * (1 - p) * 80 * u;
  const dy = vertical ? (1 - p) * -40 * u : 0;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width,
        transform: `translate(${dx}px, ${dy}px)`,
        opacity: Math.min(io.out, p * 1.3),
        backgroundColor: t.card,
        color: t.cardText,
        borderRadius: Math.round(t.radius * u),
        boxShadow: shadow(u),
        overflow: "hidden",
      }}
    >
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: Math.round(12 * u), backgroundColor: t.accent }} />
      <div style={{ padding: `${Math.round(34 * u)}px ${Math.round(40 * u)}px ${Math.round(34 * u)}px ${Math.round(52 * u)}px` }}>{children}</div>
    </div>
  );
};

const Stat: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u: u0, vertical, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const value = String(overlay.props.value ?? "");
  const label = String(overlay.props.label ?? "");
  const n = splitNumber(value);
  const settle = Math.round(0.9 * fps);
  const shown =
    n.num === null
      ? value
      : frame >= settle
        ? value
        : n.pre + formatNumber(interpolate(frame, [0, settle], [0, n.num], { ...clampOpts, easing: easeOut }), n.decimals, n.comma) + n.post;
  const width = Math.round(vertical ? edl.safe.w : 620 * u);
  return (
    <CardFrame edl={edl} overlay={overlay} width={width}>
      <div style={{ fontFamily: displayFont(edl, value), fontWeight: 900, fontSize: Math.round((vertical ? 150 : 132) * u), lineHeight: 1, letterSpacing: "-0.02em", color: t.cardText, fontVariantNumeric: "tabular-nums" }}>{shown}</div>
      <div style={{ fontFamily: bodyFont(edl, label), fontWeight: 600, fontSize: Math.round(36 * u), lineHeight: isBengali(label) ? 1.45 : 1.25, marginTop: Math.round(12 * u), color: t.cardText }}>{label}</div>
      {overlay.props.source ? (
        <div style={{ fontFamily: bodyFont(edl, String(overlay.props.source)), fontWeight: 500, fontSize: Math.round(22 * u), marginTop: Math.round(14 * u), color: t.muted }}>
          {String(overlay.props.source)}
        </div>
      ) : null}
    </CardFrame>
  );
};

const List: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u: u0, vertical, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const items: string[] = (overlay.props.items || []).map(String);
  const title = overlay.props.title ? String(overlay.props.title) : "";
  const step = Math.max(Math.round(0.35 * fps), Math.min(Math.round(0.9 * fps), Math.floor((overlay.durationInFrames * 0.55) / Math.max(1, items.length))));
  const width = Math.round(vertical ? edl.safe.w : 680 * u);
  const size = Math.round(34 * u);
  return (
    <CardFrame edl={edl} overlay={overlay} width={width}>
      {title ? <div style={{ fontFamily: displayFont(edl, title), fontWeight: 800, fontSize: Math.round(40 * u), marginBottom: Math.round(18 * u), lineHeight: 1.2 }}>{title}</div> : null}
      {items.map((it, i) => {
        const p = spring({ frame: frame - Math.round(0.25 * fps) - i * step, fps, config: { damping: 18, stiffness: 170 } });
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: Math.round(18 * u), marginTop: i ? Math.round(14 * u) : 0, opacity: p, transform: `translateX(${(1 - p) * 30 * u}px)` }}>
            <div style={{ flex: "none", width: Math.round(48 * u), height: Math.round(48 * u), borderRadius: "50%", backgroundColor: t.accent, color: t.ink, fontFamily: font(t.display), fontWeight: 900, fontSize: Math.round(26 * u), display: "flex", alignItems: "center", justifyContent: "center" }}>
              {i + 1}
            </div>
            <div style={{ fontFamily: bodyFont(edl, it), fontWeight: 600, fontSize: size, lineHeight: isBengali(it) ? 1.45 : 1.25 }}>{it}</div>
          </div>
        );
      })}
    </CardFrame>
  );
};

const Compare: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, W, u: u0, vertical, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const io = inOut(frame, overlay.durationInFrames, 0, 8);
  const left = String(overlay.props.left ?? "");
  const right = String(overlay.props.right ?? "");
  const title = overlay.props.title ? String(overlay.props.title) : "";
  const pl = spring({ frame, fps, config: { damping: 18, stiffness: 160 } });
  const pr = spring({ frame: frame - 6, fps, config: { damping: 18, stiffness: 160 } });
  const width = Math.round(vertical ? edl.safe.w : Math.min(1180 * u, edl.safe.w));
  const colW = (width - 80 * u) / 2;
  // short sides read as a headline, long ones as a card; with no face or screen behind (voiceOnly, brollFull) the
  // comparison is the picture, so it sits in the middle between the title band and the lower band
  const longest = Math.max(left.length, right.length);
  const size = Math.round((longest <= 16 ? 64 : longest <= 28 ? 50 : 38) * u);
  const clip = clipAt(edl, overlay.from);
  const open = !clip || clip.layout === "voiceOnly" || clip.layout === "brollFull";
  const col = (text: string, color: string, p: number, dir: number) => (
    <div style={{ width: colW, backgroundColor: t.card, color: t.cardText, borderRadius: Math.round(t.radius * u), padding: `${Math.round(34 * u)}px ${Math.round(30 * u)}px`, boxShadow: shadow(u), borderTop: `${Math.round(10 * u)}px solid ${color}`, transform: `translateX(${(1 - p) * dir * 60 * u}px)`, opacity: p, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <div style={{ fontFamily: displayFont(edl, text), fontWeight: 800, fontSize: size, lineHeight: isBengali(text) ? 1.45 : 1.2 }}>{text}</div>
    </div>
  );
  const place: React.CSSProperties = open
    ? { top: edl.bands.title.y, height: edl.bands.lower.y - edl.bands.title.y, display: "flex", flexDirection: "column", justifyContent: "center" }
    : { top: vertical ? edl.bands.title.y : edl.safe.y + edl.safe.h * 0.18 };
  return (
    <AbsoluteFill style={{ opacity: io.out }}>
      <div style={{ position: "absolute", left: (W - width) / 2, width, ...place }}>
        {title ? <div style={{ textAlign: "center", fontFamily: displayFont(edl, title), fontWeight: 900, fontSize: Math.round(46 * u), color: t.text, marginBottom: Math.round(18 * u), textShadow: "0 4px 18px rgba(0,0,0,0.5)" }}>{title}</div> : null}
        <div style={{ display: "flex", alignItems: "stretch", justifyContent: "space-between", position: "relative" }}>
          {col(left, t.danger, pl, -1)}
          {col(right, t.accent, pr, 1)}
          <div style={{ position: "absolute", left: "50%", top: "50%", width: Math.round(76 * u), height: Math.round(76 * u), marginLeft: Math.round(-38 * u), marginTop: Math.round(-38 * u), borderRadius: "50%", backgroundColor: t.ink, color: t.text, fontFamily: font(t.display), fontWeight: 900, fontSize: Math.round(28 * u), display: "flex", alignItems: "center", justifyContent: "center", boxShadow: shadow(u, 0.4) }}>
            VS
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Quote: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u: u0, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const text = String(overlay.props.text || "");
  const io = inOut(frame, overlay.durationInFrames, 6, 8);
  const bn = isBengali(text);
  return (
    <AbsoluteFill style={{ backgroundColor: hexToRgba(t.ink, 0.92), opacity: io.v, alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: edl.safe.w * 0.86, textAlign: "center" }}>
        <div style={{ fontFamily: font(t.display), fontWeight: 900, fontSize: Math.round(200 * u), lineHeight: 0.6, color: t.accent }}>&ldquo;</div>
        <WordsIn text={text} frame={frame} fps={fps} size={Math.round(64 * u)} color={t.text} accent={t.accent} highlight={overlay.props.highlight} family={displayFont(edl, text)} weight={800} />
        {overlay.props.by ? (
          <div style={{ marginTop: Math.round(30 * u), fontFamily: bodyFont(edl, String(overlay.props.by)), fontWeight: 600, fontSize: Math.round(30 * u), color: t.muted, lineHeight: bn ? 1.4 : 1.2 }}>
            {String(overlay.props.by)}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const Chapter: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u: u0, vertical, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const title = String(overlay.props.title || "");
  const label = overlay.props.label ? String(overlay.props.label) : "";
  const p = spring({ frame, fps, config: { damping: 20, stiffness: 140 } });
  const io = inOut(frame, overlay.durationInFrames, 0, 8);
  const left = vertical ? edl.safe.x : edl.safe.x;
  return (
    <AbsoluteFill style={{ opacity: io.out }}>
      <div style={{ position: "absolute", left, top: edl.bands.title.y, maxWidth: edl.safe.w, transform: `translateX(${(1 - p) * -60 * u}px)`, opacity: p }}>
        <div style={{ width: `${p * 100}%`, height: Math.round(8 * u), backgroundColor: t.accent, borderRadius: Math.round(4 * u), marginBottom: Math.round(14 * u) }} />
        {label ? <div style={{ fontFamily: bodyFont(edl, label), fontWeight: 800, fontSize: Math.round(26 * u), letterSpacing: isBengali(label) ? 0 : "0.12em", textTransform: "uppercase", color: t.accent, marginBottom: Math.round(8 * u) }}>{label}</div> : null}
        <div style={{ display: "inline-block", backgroundColor: hexToRgba(t.ink, 0.82), padding: `${Math.round(14 * u)}px ${Math.round(24 * u)}px`, borderRadius: Math.round(16 * u) }}>
          <div style={{ fontFamily: displayFont(edl, title), fontWeight: 900, fontSize: Math.round((vertical ? 64 : 60) * u), lineHeight: isBengali(title) ? 1.35 : 1.1, color: t.text }}>{title}</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const LowerThird: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, u: u0, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const name = String(overlay.props.name || "");
  const role = overlay.props.role ? String(overlay.props.role) : "";
  const bar = spring({ frame, fps, config: { damping: 22, stiffness: 120 } });
  const txt = spring({ frame: frame - 5, fps, config: { damping: 20, stiffness: 140 } });
  const io = inOut(frame, overlay.durationInFrames, 0, 10);
  const band = edl.bands.lower;
  return (
    <AbsoluteFill style={{ opacity: io.out }}>
      <div style={{ position: "absolute", left: edl.safe.x, top: band.y, height: band.h, display: "flex", alignItems: "center", gap: Math.round(18 * u) }}>
        <div style={{ width: Math.round(10 * u), height: `${bar * 100}%`, backgroundColor: t.accent, borderRadius: Math.round(5 * u) }} />
        <div style={{ backgroundColor: hexToRgba(t.ink, 0.85), borderRadius: Math.round(18 * u), padding: `${Math.round(16 * u)}px ${Math.round(26 * u)}px`, clipPath: `inset(0 ${(1 - txt) * 100}% 0 0)` }}>
          <div style={{ fontFamily: displayFont(edl, name), fontWeight: 800, fontSize: Math.round(44 * u), color: t.text, lineHeight: isBengali(name) ? 1.35 : 1.1 }}>{name}</div>
          {role ? <div style={{ fontFamily: bodyFont(edl, role), fontWeight: 500, fontSize: Math.round(28 * u), color: t.muted, marginTop: Math.round(6 * u), lineHeight: isBengali(role) ? 1.4 : 1.2 }}>{role}</div> : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Cta: React.FC<P> = ({ edl, overlay }) => {
  const { frame, fps, W, u: u0, t } = useBasics(edl);
  const u = u0 * (H_VERTICAL(edl) ? 1.3 : 1);
  const text = String(overlay.props.text || "");
  const sub = overlay.props.sub ? String(overlay.props.sub) : "";
  const p = spring({ frame, fps, config: { damping: 12, stiffness: 170, mass: 0.7 } });
  const pulse = 1 + 0.025 * Math.sin((frame / fps) * Math.PI * 2 * 0.9) * Math.min(1, frame / fps);
  const io = inOut(frame, overlay.durationInFrames, 0, 8);
  const band = edl.bands.lower;
  return (
    <AbsoluteFill style={{ opacity: io.out }}>
      <div style={{ position: "absolute", left: 0, width: W, top: band.y, height: band.h, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: Math.round(12 * u) }}>
        <div style={{ transform: `scale(${(0.5 + 0.5 * p) * pulse})`, backgroundColor: t.accent, color: t.ink, fontFamily: displayFont(edl, text), fontWeight: 900, fontSize: Math.round(46 * u), padding: `${Math.round(18 * u)}px ${Math.round(42 * u)}px`, borderRadius: 999, boxShadow: shadow(u, 0.4), lineHeight: isBengali(text) ? 1.35 : 1.1 }}>
          {text}
        </div>
        {sub ? <div style={{ fontFamily: bodyFont(edl, sub), fontWeight: 600, fontSize: Math.round(28 * u), color: t.text, textShadow: "0 3px 14px rgba(0,0,0,0.6)", opacity: p }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

const MediaInsert: React.FC<P> = ({ edl, overlay }) => {
  const { frame, W, H, u, t } = useBasics(edl);
  const src = edl.sources[overlay.props.source];
  if (!src) return null;
  const url = mediaSrc(edl.base, src.src);
  const still = IMAGE.test(src.src);
  const dur = overlay.durationInFrames;
  const fit = overlay.props.fit || "full";
  const hard = overlay.props.enter === "cut";
  const io = inOut(frame, dur, hard ? 0 : 4, hard ? 0 : 4);
  const motion = overlay.props.motion || "push";
  const k = interpolate(frame, [0, dur], [0, 1], clampOpts);
  const scale = still ? (motion === "pull" ? 1.08 - 0.08 * k : motion === "none" ? 1 : 1 + 0.08 * k) : 1;
  const panX = still && motion === "pan-left" ? -0.5 + k : still && motion === "pan-right" ? 0.5 - k : 0;
  const box = fit === "box" ? overlay.props.box || (H > W ? { x: 0.08, y: 0.16, w: 0.84, h: 0.3 } : { x: 0.5, y: 0.14, w: 0.44, h: 0.5 }) : { x: 0, y: 0, w: 1, h: 1 };
  const bw = Math.round(box.w * W);
  const bh = Math.round(box.h * H);
  if (src.alpha && !still) {
    // a cutout with its own transparency: placed and sized like any insert, but with no card around it
    const fitted = containRect(src.width || W, src.height || H, bw, bh);
    return (
      <AbsoluteFill style={{ opacity: io.v }}>
        <div style={{ position: "absolute", left: box.x * W, top: box.y * H, width: bw, height: bh }}>
          <OffthreadVideo
            src={url}
            trimBefore={overlay.props.trimBefore || 0}
            muted
            transparent
            style={{ position: "absolute", left: fitted.left, top: fitted.top, width: fitted.width, height: fitted.height }}
          />
        </div>
      </AbsoluteFill>
    );
  }
  const sw = src.width || W;
  const sh = src.height || H;
  const r: Rect = coverRect(sw, sh, bw, bh, 0.5 + panX * 0.2, 0.5, scale * (panX ? 1.12 : 1));
  const media = still ? (
    <Img src={url} style={{ position: "absolute", left: r.left, top: r.top, width: r.width, height: r.height }} />
  ) : (
    <Video src={url} trimBefore={overlay.props.trimBefore || 0} muted objectFit="fill" style={{ position: "absolute", left: r.left, top: r.top, width: r.width, height: r.height }} />
  );
  if (fit !== "box") {
    return <AbsoluteFill style={{ opacity: io.v, overflow: "hidden" }}>{media}</AbsoluteFill>;
  }
  const pop = interpolate(frame, [0, 8], [0.92, 1], { ...clampOpts, easing: easeOut });
  return (
    <AbsoluteFill style={{ opacity: io.v }}>
      <div style={{ position: "absolute", left: box.x * W, top: box.y * H, width: bw, height: bh, borderRadius: Math.round(t.radius * u), overflow: "hidden", border: `${Math.max(3, Math.round(5 * u))}px solid #FFFFFF`, boxShadow: shadow(u, 0.45), transform: `scale(${pop})` }}>
        {media}
      </div>
    </AbsoluteFill>
  );
};

export const OverlayView: React.FC<P> = ({ edl, overlay }) => {
  switch (overlay.type) {
    case "hook":
      return <Hook edl={edl} overlay={overlay} />;
    case "keyword":
      return <Keyword edl={edl} overlay={overlay} />;
    case "stat":
      return <Stat edl={edl} overlay={overlay} />;
    case "list":
      return <List edl={edl} overlay={overlay} />;
    case "compare":
      return <Compare edl={edl} overlay={overlay} />;
    case "quote":
      return <Quote edl={edl} overlay={overlay} />;
    case "chapter":
      return <Chapter edl={edl} overlay={overlay} />;
    case "lowerThird":
      return <LowerThird edl={edl} overlay={overlay} />;
    case "cta":
      return <Cta edl={edl} overlay={overlay} />;
    case "broll":
    case "image":
    case "segment":
      return <MediaInsert edl={edl} overlay={overlay} />;
    case "callout":
    case "redact":
      return <FrameMark edl={edl} overlay={overlay} />;
    default:
      return null;
  }
};

// Callouts and redactions drawn in frame coordinates (layer "frame").
const FrameMark: React.FC<P> = ({ edl, overlay }) => {
  const { W, H } = useBasics(edl);
  const frame = useCurrentFrame();
  return <Mark edl={edl} overlay={overlay} rect={{ left: 0, top: 0, width: W, height: H }} local={frame} />;
};

const Mark: React.FC<{ edl: Edl; overlay: Overlay; rect: Rect; local: number }> = ({ edl, overlay, rect, local }) => {
  const { fps, u, t } = useBasics(edl);
  const b = overlay.props.box || { x: 0, y: 0, w: 0, h: 0 };
  const left = rect.left + b.x * rect.width;
  const top = rect.top + b.y * rect.height;
  const width = b.w * rect.width;
  const height = b.h * rect.height;
  if (overlay.type === "redact") {
    const solid = overlay.props.style === "solid";
    return (
      <div
        style={{
          position: "absolute",
          left,
          top,
          width,
          height,
          borderRadius: Math.round(10 * u),
          backgroundColor: solid ? t.ink : "rgba(20,20,24,0.35)",
          backdropFilter: solid ? undefined : "blur(28px)",
          WebkitBackdropFilter: solid ? undefined : "blur(28px)",
        }}
      />
    );
  }
  const draw = spring({ frame: local, fps, config: { damping: 20, stiffness: 160 } });
  const io = inOut(local, overlay.durationInFrames, 0, 8);
  const label = overlay.props.label ? String(overlay.props.label) : "";
  const stroke = Math.max(4, Math.round(6 * u));
  return (
    <div style={{ position: "absolute", left: 0, top: 0, right: 0, bottom: 0, opacity: io.out }}>
      <div
        style={{
          position: "absolute",
          left: left - stroke,
          top: top - stroke,
          width: width + stroke * 2,
          height: height + stroke * 2,
          border: `${stroke}px solid ${t.accent}`,
          borderRadius: Math.round(14 * u),
          transform: `scale(${1.25 - 0.25 * draw})`,
          opacity: draw,
          boxShadow: overlay.props.spotlight ? `0 0 0 ${Math.round(4000 * u)}px rgba(0,0,0,${0.45 * draw})` : `0 0 ${Math.round(24 * u)}px ${hexToRgba(t.accent, 0.55)}`,
        }}
      />
      {label ? (
        <div
          style={{
            position: "absolute",
            left,
            top: top + height + stroke * 2 + Math.round(10 * u) < rect.top + rect.height - Math.round(60 * u) ? top + height + stroke * 2 + Math.round(10 * u) : top - Math.round(64 * u),
            backgroundColor: t.accent,
            color: t.ink,
            fontFamily: font(isBengali(label) ? "HindSiliguri" : t.display),
            fontWeight: 800,
            fontSize: Math.round(30 * u),
            padding: `${Math.round(8 * u)}px ${Math.round(18 * u)}px`,
            borderRadius: 999,
            opacity: draw,
            whiteSpace: "nowrap",
            boxShadow: shadow(u, 0.3),
          }}
        >
          {label}
        </div>
      ) : null}
    </div>
  );
};

// Marks that belong to a recording: drawn inside its layer, so they move with its zoom.
export const LayerMarks: React.FC<{ edl: Edl; layer: string; rect: Rect; globalFrame: number }> = ({ edl, layer, rect, globalFrame }) => {
  const marks = edl.overlays.filter(
    (o) => isLayerOverlay(o) && (o.props.layer ?? "screen") === layer && globalFrame >= o.from && globalFrame < o.from + o.durationInFrames,
  );
  if (!marks.length) return null;
  return (
    <>
      {marks.map((o) => (
        <Mark key={o.id} edl={edl} overlay={o} rect={rect} local={globalFrame - o.from} />
      ))}
    </>
  );
};
