// The edit: A-roll clips in their layouts, overlays, captions and the premixed sound, all read from the EDL.
// Every video is muted: the sound is one mixed file (nexa-sound), cut sample-accurately on the same frame grid.
import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio, Video } from "@remotion/media";
import { Captions } from "./captions";
import { LayerMarks, OverlayView, isLayerOverlay } from "./overlays";
import {
  Clip,
  Edl,
  Placement,
  Rect,
  clampOpts,
  containRect,
  coverRect,
  easeOut,
  hexToRgba,
  mediaSrc,
  unit,
  zoomAt,
  zoomTransform,
} from "./lib";

const IMAGE = /\.(png|jpe?g|webp|gif|bmp)$/i;

// One source drawn into a w x h box, with its zoom and its layer marks (callouts, redactions) in source coordinates.
const Layer: React.FC<{
  edl: Edl;
  place: Placement;
  w: number;
  h: number;
  fit: "cover" | "contain";
  layer: "cam" | "screen" | "broll";
  focus?: { x: number; y: number } | null;
  scale?: number;
  globalFrame: number;
}> = ({ edl, place, w, h, fit, layer, focus, scale = 1, globalFrame }) => {
  if (!place) return null;
  const src = edl.sources[place.source];
  if (!src) return null;
  const sw = src.width || edl.width;
  const sh = src.height || edl.height;
  const z = zoomAt(edl.zooms, layer, globalFrame);
  const fx = z.s > 1.0001 ? z.cx : focus?.x ?? 0.5;
  const fy = z.s > 1.0001 ? z.cy : focus?.y ?? 0.42;
  const r: Rect = fit === "cover" ? coverRect(sw, sh, w, h, fx, fy, scale) : containRect(sw, sh, w, h);
  const url = mediaSrc(edl.base, src.src);
  const still = IMAGE.test(src.src);
  const style: React.CSSProperties = { position: "absolute", left: r.left, top: r.top, width: r.width, height: r.height };
  return (
    <div style={{ position: "absolute", width: w, height: h, overflow: "hidden" }}>
      <div style={{ position: "absolute", width: w, height: h, transform: zoomTransform(w, h, z), transformOrigin: "0 0" }}>
        {still ? (
          <Img src={url} style={{ ...style, objectFit: "fill" }} />
        ) : src.alpha ? (
          <OffthreadVideo src={url} trimBefore={place.trimBefore} muted transparent style={style} />
        ) : (
          <Video src={url} trimBefore={place.trimBefore} muted objectFit="fill" style={style} />
        )}
        <LayerMarks edl={edl} layer={layer} rect={r} globalFrame={globalFrame} />
      </div>
    </div>
  );
};

// Behind everything: the theme colour with two slow, soft light pools (a faceless video is never a flat colour).
const Backdrop: React.FC<{ edl: Edl }> = ({ edl }) => {
  const frame = useCurrentFrame();
  const t = frame / (edl.fps * 12);
  const x = 50 + 18 * Math.sin(t * Math.PI * 2);
  const y = 40 + 14 * Math.cos(t * Math.PI * 2);
  const clear = hexToRgba(edl.theme.bg, 0);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: edl.theme.bg,
        backgroundImage: `radial-gradient(circle at ${x}% ${y}%, ${hexToRgba(edl.theme.accent, 0.16)} 0%, ${clear} 55%), radial-gradient(circle at ${100 - x}% ${100 - y}%, ${hexToRgba(edl.theme.accent, 0.08)} 0%, ${clear} 60%)`,
      }}
    />
  );
};

const PipFrame: React.FC<{ edl: Edl; clip: Clip; globalFrame: number; animateIn: boolean }> = ({
  edl,
  clip,
  globalFrame,
  animateIn,
}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const u = unit(width, height);
  const size = Math.round(clip.pip.size * width);
  const w = size;
  const h = clip.pip.shape === "circle" ? size : Math.round(size * 1.15);
  const s = edl.safe;
  const left = clip.pip.corner.endsWith("l") ? s.x : s.x + s.w - w;
  const top = clip.pip.corner.startsWith("t") ? s.y : s.y + s.h - h;
  const pop = animateIn
    ? interpolate(frame, [0, Math.round(0.35 * fps)], [0.6, 1], { ...clampOpts, easing: easeOut })
    : 1;
  const opacity = animateIn ? interpolate(frame, [0, 6], [0, 1], clampOpts) : 1;
  const face = clip.cam ? edl.sources[clip.cam.source]?.face : null;
  const border = Math.max(4, Math.round(6 * u));
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: w,
        height: h,
        borderRadius: clip.pip.shape === "circle" ? "50%" : Math.round(edl.theme.radius * u),
        overflow: "hidden",
        border: `${border}px solid #FFFFFF`,
        boxShadow: `0 ${Math.round(18 * u)}px ${Math.round(44 * u)}px rgba(0,0,0,0.45)`,
        transform: `scale(${pop})`,
        opacity,
        backgroundColor: edl.theme.ink,
      }}
    >
      <Layer edl={edl} place={clip.cam} w={w - 2 * border} h={h - 2 * border} fit="cover" layer="cam" focus={face} scale={1.35} globalFrame={globalFrame} />
    </div>
  );
};

const TransitionIn: React.FC<{ clip: Clip; children: React.ReactNode }> = ({ clip, children }) => {
  const frame = useCurrentFrame();
  const t = clip.transitionIn;
  if (!t || t.type === "cut" || t.frames <= 0) return <>{children}</>;
  const p = interpolate(frame, [0, t.frames], [0, 1], { ...clampOpts, easing: easeOut });
  if (t.type === "zoom") {
    return <AbsoluteFill style={{ transform: `scale(${1.18 - 0.18 * p})` }}>{children}</AbsoluteFill>;
  }
  if (t.type === "whip") {
    return <AbsoluteFill style={{ transform: `translateX(${(1 - p) * 55}%)` }}>{children}</AbsoluteFill>;
  }
  if (t.type === "dip") {
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <AbsoluteFill style={{ opacity: p }}>{children}</AbsoluteFill>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      {children}
      <AbsoluteFill style={{ backgroundColor: "#FFFFFF", opacity: 1 - p }} />
    </AbsoluteFill>
  );
};

export const splitGeometry = (edl: Edl, clip: Clip, W: number, H: number, gap: number) => {
  const camW = Math.round(W * 0.28);
  const screenW = W - camW - gap * 3;
  const src = clip.screen ? edl.sources[clip.screen.source] : null;
  const aspect = src && src.width && src.height ? src.width / src.height : 16 / 9;
  const panelH = Math.round(Math.min(H - gap * 2, screenW / aspect));
  return { screenW, camW, panelH, top: Math.round((H - panelH) / 2) };
};

const ClipView: React.FC<{ edl: Edl; clip: Clip; prevLayout: string | null }> = ({ edl, clip, prevLayout }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const g = clip.from + frame;
  const u = unit(W, H);
  const cam = clip.cam ? edl.sources[clip.cam.source] : null;
  const face = cam?.face ?? null;
  const gap = Math.round(24 * u);
  const radius = Math.round(edl.theme.radius * u);
  let body: React.ReactNode = null;

  if (clip.layout === "camFull") {
    body = <Layer edl={edl} place={clip.cam} w={W} h={H} fit="cover" layer="cam" focus={face} scale={clip.punch} globalFrame={g} />;
  } else if (clip.layout === "screenFull") {
    body = <Layer edl={edl} place={clip.screen} w={W} h={H} fit="contain" layer="screen" globalFrame={g} />;
  } else if (clip.layout === "screenPip") {
    body = (
      <>
        <Layer edl={edl} place={clip.screen} w={W} h={H} fit="contain" layer="screen" globalFrame={g} />
        <PipFrame edl={edl} clip={clip} globalFrame={g} animateIn={prevLayout !== "screenPip"} />
      </>
    );
  } else if (clip.layout === "split") {
    // screen 72 % and camera 28 % of the width, both as tall as the screen recording's own shape needs (no bars)
    const { screenW, camW, panelH, top } = splitGeometry(edl, clip, W, H, gap);
    body = (
      <>
        <div style={{ position: "absolute", left: gap, top, width: screenW, height: panelH, borderRadius: radius, overflow: "hidden", backgroundColor: edl.theme.ink, boxShadow: `0 ${Math.round(14 * u)}px ${Math.round(36 * u)}px rgba(0,0,0,0.35)` }}>
          <Layer edl={edl} place={clip.screen} w={screenW} h={panelH} fit="contain" layer="screen" globalFrame={g} />
        </div>
        <div style={{ position: "absolute", left: gap * 2 + screenW, top, width: camW, height: panelH, borderRadius: radius, overflow: "hidden", boxShadow: `0 ${Math.round(14 * u)}px ${Math.round(36 * u)}px rgba(0,0,0,0.35)` }}>
          <Layer edl={edl} place={clip.cam} w={camW} h={panelH} fit="cover" layer="cam" focus={face} scale={clip.punch} globalFrame={g} />
        </div>
      </>
    );
  } else if (clip.layout === "stack") {
    const top = Math.round(H * 0.5);
    const seam = Math.max(4, Math.round(6 * u));
    body = (
      <>
        <div style={{ position: "absolute", left: 0, top: 0, width: W, height: top - seam / 2, overflow: "hidden" }}>
          <Layer edl={edl} place={clip.screen} w={W} h={top - seam / 2} fit="cover" layer="screen" globalFrame={g} />
        </div>
        <div style={{ position: "absolute", left: 0, top: top + seam / 2, width: W, height: H - top - seam / 2, overflow: "hidden" }}>
          <Layer edl={edl} place={clip.cam} w={W} h={H - top - seam / 2} fit="cover" layer="cam" focus={face} scale={clip.punch} globalFrame={g} />
        </div>
        <div style={{ position: "absolute", left: 0, top: top - seam / 2, width: W, height: seam, backgroundColor: edl.theme.accent }} />
      </>
    );
  } else if (clip.layout === "brollFull") {
    const push = interpolate(frame, [0, clip.durationInFrames], [1, 1.06], clampOpts);
    body = <Layer edl={edl} place={clip.broll} w={W} h={H} fit="cover" layer="broll" scale={push} globalFrame={g} />;
  }
  return (
    <AbsoluteFill>
      <Backdrop edl={edl} />
      <TransitionIn clip={clip}>{body}</TransitionIn>
    </AbsoluteFill>
  );
};

const Progress: React.FC<{ edl: Edl }> = ({ edl }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, height: Math.max(4, Math.round(6 * u)), width: `${(100 * frame) / edl.durationInFrames}%`, backgroundColor: edl.theme.accent }} />
  );
};

export const Edit: React.FC<Edl> = (edl) => {
  return (
    <AbsoluteFill style={{ backgroundColor: edl.theme.bg }}>
      {edl.clips.map((clip, i) => (
        <Sequence key={clip.id} from={clip.from} durationInFrames={clip.durationInFrames} premountFor={Math.round(edl.fps)} name={`${clip.id} ${clip.layout}`}>
          <ClipView edl={edl} clip={clip} prevLayout={i > 0 ? edl.clips[i - 1].layout : null} />
        </Sequence>
      ))}
      {edl.overlays
        .filter((o) => !isLayerOverlay(o))
        .map((o) => (
          <Sequence key={o.id} from={o.from} durationInFrames={o.durationInFrames} premountFor={Math.round(edl.fps)} name={`${o.id} ${o.type}`}>
            <OverlayView edl={edl} overlay={o} />
          </Sequence>
        ))}
      {edl.captions.burn ? <Captions edl={edl} /> : null}
      {edl.progress ? <Progress edl={edl} /> : null}
      {edl.audio ? <Audio src={mediaSrc(edl.base, edl.audio)} /> : null}
    </AbsoluteFill>
  );
};
