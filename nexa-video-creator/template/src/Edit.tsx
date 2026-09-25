// The edit: A-roll clips in their layouts, designed full-frame scenes, Vox-style beats, overlays, captions and the
// premixed sound, all read from the EDL. Every video is muted: the sound is one mixed file (nexa-sound), cut
// sample-accurately on the same frame grid. Layers from the bottom: clips, full scenes and Vox beats (each run of beats
// on one locked paper ground, grain over it), the presenter's round picture over a scene, the other overlays,
// captions, colour sweeps and light leaks over cuts, the progress bar.
import React from "react";
import { AbsoluteFill, Easing, Img, OffthreadVideo, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio, Video } from "@remotion/media";
import { Captions } from "./captions";
import { LayerMarks, OverlayView, isLayerOverlay } from "./overlays";
import { BarSweep, Paper, SCENE_TYPES, SceneView, scenePip } from "./scenes";
import { Grain, LightLeak, PaperGrid, VoxBeat } from "./vox";
import {
  Clip,
  Edl,
  Overlay,
  Placement,
  Rect,
  clampOpts,
  containRect,
  coverRect,
  easeOut,
  hexToRgba,
  highlightOf,
  mediaSrc,
  mix,
  paletteOf,
  smoothNoise,
  speakingAt,
  unit,
  zoomAt,
  zoomTransform,
} from "./lib";

const IMAGE = /\.(png|jpe?g|webp|gif|bmp)$/i;
const SWEEP_FRAMES = 16;
const LEAK_FRAMES = 20;

// A full-frame overlay: a designed scene, a quote, or a full-frame insert. Drawn under the other overlays.
export const isFull = (o: Overlay): boolean =>
  o.slot
    ? o.slot === "full"
    : SCENE_TYPES.has(o.type) ||
      o.type === "vox" ||
      o.type === "quote" ||
      (["broll", "image", "segment"].includes(o.type) && (o.props.fit || "full") === "full");

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

// Behind everything: warm dotted paper, a dusk gradient, or the theme colour with two slow light pools (a faceless
// video is never a flat colour).
const Backdrop: React.FC<{ edl: Edl }> = ({ edl }) => {
  const frame = useCurrentFrame();
  const kind = edl.theme.backdrop || "pools";
  if (kind === "paper") return <Paper theme={edl.theme} />;
  if (kind === "grid") return <PaperGrid theme={edl.theme} />;
  if (kind === "dusk") {
    const c = paletteOf(edl.theme)[1];
    return <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 58%, ${mix(c, "#000000", 0.6)} 0%, ${mix(c, "#000000", 0.83)} 55%, #0B070B 100%)` }} />;
  }
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

// The presenter in a round frame: a white rim, a soft shadow, and a ring that moves only while someone speaks.
// `seqFrom` is where the enclosing sequence starts on the output timeline.
const RoundPip: React.FC<{
  edl: Edl;
  clip: Clip;
  place: Placement;
  seqFrom: number;
  animateIn: boolean;
  exitAt?: number | null;
  sizePx?: number;
  corner?: string;
}> = ({ edl, clip, place, seqFrom, animateIn, exitAt = null, sizePx, corner }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const g = seqFrom + frame;
  const u = unit(width, height);
  const size = sizePx ?? Math.round(clip.pip.size * width);
  const at = corner ?? clip.pip.corner;
  const s = edl.safe;
  const left = at.endsWith("l") ? s.x + 16 * u : s.x + s.w - size - 16 * u;
  const top = at.startsWith("t") ? s.y + 16 * u : s.y + s.h - size - 16 * u;
  const pop = animateIn ? spring({ frame, fps, config: { damping: 12, stiffness: 170, mass: 0.8 } }) : 1;
  const out = exitAt !== null ? interpolate(frame, [exitAt - 8, exitAt - 1], [1, 0], { ...clampOpts, easing: Easing.in(Easing.cubic) }) : 1;
  const talking = speakingAt(edl, g);
  const talk = talking ? 1 + 0.045 * smoothNoise("pip-voice", g / 4) : 1;
  const face = clip.cam ? edl.sources[clip.cam.source]?.face : null;
  const border = Math.max(4, Math.round(8 * u));
  return (
    <div style={{ position: "absolute", left, top, width: size, height: size, transform: `scale(${pop * out})` }}>
      <div
        style={{
          position: "absolute",
          inset: -16 * u,
          borderRadius: "50%",
          border: `${5 * u}px solid ${hexToRgba(highlightOf(edl.theme), talking ? 0.95 : 0.55)}`,
          transform: `scale(${talk})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          overflow: "hidden",
          border: `${border}px solid #FFFFFF`,
          boxShadow: `0 ${18 * u}px ${44 * u}px rgba(20, 10, 5, 0.38)`,
          backgroundColor: edl.theme.ink,
        }}
      >
        <Layer edl={edl} place={place} w={size - 2 * border} h={size - 2 * border} fit="cover" layer="cam" focus={face} scale={1.35} globalFrame={g} />
      </div>
    </div>
  );
};

const PipFrame: React.FC<{ edl: Edl; clip: Clip; globalFrame: number; animateIn: boolean }> = ({ edl, clip, globalFrame, animateIn }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  if (clip.pip.shape === "circle") {
    return <RoundPip edl={edl} clip={clip} place={clip.cam} seqFrom={clip.from} animateIn={animateIn} />;
  }
  const u = unit(width, height);
  const size = Math.round(clip.pip.size * width);
  const w = size;
  const h = Math.round(size * 1.15);
  const s = edl.safe;
  const left = clip.pip.corner.endsWith("l") ? s.x : s.x + s.w - w;
  const top = clip.pip.corner.startsWith("t") ? s.y : s.y + s.h - h;
  const pop = animateIn ? interpolate(frame, [0, Math.round(0.35 * fps)], [0.6, 1], { ...clampOpts, easing: easeOut }) : 1;
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
        borderRadius: Math.round(edl.theme.radius * u),
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
  const { fps } = useVideoConfig();
  const t = clip.transitionIn;
  if (!t || t.type === "cut" || t.type === "sweep" || t.type === "leak" || t.frames <= 0) return <>{children}</>;
  const p = interpolate(frame, [0, t.frames], [0, 1], { ...clampOpts, easing: easeOut });
  if (t.type === "slide") {
    // over the previous clip, which stays underneath for these frames
    const s = spring({ frame, fps, config: { damping: 200 }, durationInFrames: t.frames });
    return <AbsoluteFill style={{ transform: `translateX(${(1 - s) * 100}%)` }}>{children}</AbsoluteFill>;
  }
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

// The presenter over a full scene: one round picture per clip under the scene, placed at the clip's own time.
const scenePips = (edl: Edl) => {
  const out: {
    key: string;
    from: number;
    dur: number;
    clip: Clip;
    place: Placement;
    animateIn: boolean;
    exitAt: number | null;
    size: number;
    corner: string;
  }[] = [];
  const withPip = edl.overlays.filter((o) => isFull(o) && o.props.pip);
  // scenes with the presenter back to back keep one steady picture: no pop out and in at the join
  const joined = (f: number, side: "end" | "start") =>
    withPip.some((o) => Math.abs((side === "end" ? o.from + o.durationInFrames : o.from) - f) <= 1);
  for (const o of withPip) {
    const end = o.from + o.durationInFrames;
    const look = scenePip(edl, o, edl.width, edl.height);
    const joinedBefore = joined(o.from, "end");
    const joinedAfter = joined(end, "start");
    for (const c of edl.clips) {
      if (!c.cam) continue;
      const a = Math.max(o.from, c.from);
      const b = Math.min(end, c.from + c.durationInFrames);
      if (b - a < 1) continue;
      out.push({
        key: `${o.id}-${c.id}`,
        from: a,
        dur: b - a,
        clip: c,
        place: { source: c.cam.source, trimBefore: c.cam.trimBefore + (a - c.from) },
        animateIn: a === o.from && !joinedBefore,
        exitAt: b === end && !joinedAfter ? b - a : null,
        size: look.size,
        corner: look.corner,
      });
    }
  }
  return out;
};

// Frames where a sweep (or a light leak) hides a cut: into a clip, or into or out of an overlay that asks for one.
const cutsWith = (edl: Edl, kind: string): number[] => {
  const at = new Set<number>();
  for (const c of edl.clips) if (c.transitionIn?.type === kind && c.from > 0) at.add(c.from);
  for (const o of edl.overlays) {
    if (o.enter === kind) at.add(o.from);
    if (o.exit === kind) at.add(o.from + o.durationInFrames);
  }
  return [...at].filter((f) => f > 0 && f < edl.durationInFrames).sort((a, b) => a - b);
};

// Vox beats back to back share one ground: where each run of them starts and ends (with the last beat's tail).
const voxRuns = (full: Overlay[]) => {
  const runs: { first: string; last: string; from: number; to: number }[] = [];
  for (const o of full) {
    if (o.type !== "vox") continue;
    const end = o.from + o.durationInFrames + Number(o.props.tail || 0);
    const cur = runs[runs.length - 1];
    if (cur && o.from - cur.to <= 1 + Number(full.find((x) => x.id === cur.last)?.props.tail || 0)) {
      cur.last = o.id;
      cur.to = Math.max(cur.to, end);
    } else {
      runs.push({ first: o.id, last: o.id, from: o.from, to: end });
    }
  }
  return runs;
};

const Progress: React.FC<{ edl: Edl }> = ({ edl }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  const w = `${(100 * frame) / Math.max(1, edl.durationInFrames - 1)}%`;
  if (edl.progress === "bottom") {
    // the explainer's own bar: thick, along the bottom edge
    return <div style={{ position: "absolute", left: 0, bottom: 0, height: Math.max(8, Math.round(38 * u)), width: w, backgroundColor: edl.theme.accent }} />;
  }
  return <div style={{ position: "absolute", left: 0, top: 0, height: Math.max(4, Math.round(6 * u)), width: w, backgroundColor: edl.theme.accent }} />;
};

// A full scene stays under the next one while that one slides, pops or fades in over it.
const holdUnder = (full: Overlay[], o: Overlay): number => {
  const next = full.find((n) => n.from >= o.from + o.durationInFrames - 1 && n.id !== o.id);
  if (!next || next.from - (o.from + o.durationInFrames) > 1) return 0;
  return ["slide", "slideUp", "pop", "fade"].includes(next.enter || "") ? 12 : 0;
};

export const Edit: React.FC<Edl> = (edl) => {
  const full = edl.overlays.filter((o) => !isLayerOverlay(o) && isFull(o)).sort((a, b) => a.from - b.from);
  const rest = edl.overlays.filter((o) => !isLayerOverlay(o) && !isFull(o));
  const half = SWEEP_FRAMES / 2;
  const runs = voxRuns(full);
  const premount = Math.round(edl.fps);
  return (
    <AbsoluteFill style={{ backgroundColor: edl.theme.bg }}>
      {edl.clips.map((clip, i) => {
        // a clip stays under the next one while it slides in
        const next = edl.clips[i + 1];
        const hold = next && next.transitionIn?.type === "slide" ? next.transitionIn.frames : 0;
        return (
          <Sequence key={clip.id} from={clip.from} durationInFrames={clip.durationInFrames + hold} premountFor={Math.round(edl.fps)} name={`${clip.id} ${clip.layout}`}>
            <ClipView edl={edl} clip={clip} prevLayout={i > 0 ? edl.clips[i - 1].layout : null} />
          </Sequence>
        );
      })}
      {full.map((o) => {
        if (o.type === "vox") {
          // a run of beats: the ground once under all of them, each beat running on under the next while its
          // elements leave, the grain once over all of them
          const run = runs.find((r) => r.first === o.id || r.last === o.id);
          return (
            <React.Fragment key={o.id}>
              {run && run.first === o.id ? (
                <Sequence from={run.from} durationInFrames={run.to - run.from} premountFor={premount} name={`ground ${o.id}`}>
                  <PaperGrid theme={edl.theme} />
                </Sequence>
              ) : null}
              <Sequence from={o.from} durationInFrames={o.durationInFrames + Number(o.props.tail || 0)} premountFor={premount} name={`${o.id} vox`}>
                <VoxBeat edl={edl} overlay={o} />
              </Sequence>
              {run && run.last === o.id ? (
                <Sequence from={run.from} durationInFrames={run.to - run.from} premountFor={premount} name={`grain ${o.id}`}>
                  <Grain opacity={Number(edl.theme.grain ?? 0.16)} />
                </Sequence>
              ) : null}
            </React.Fragment>
          );
        }
        return (
          <Sequence key={o.id} from={o.from} durationInFrames={o.durationInFrames + holdUnder(full, o)} premountFor={premount} name={`${o.id} ${o.type}`}>
            {SCENE_TYPES.has(o.type) ? <SceneView edl={edl} overlay={o} /> : <OverlayView edl={edl} overlay={o} />}
          </Sequence>
        );
      })}
      {scenePips(edl).map((p) => (
        <Sequence key={p.key} from={p.from} durationInFrames={p.dur} premountFor={Math.round(edl.fps)} name={`pip ${p.key}`}>
          <RoundPip edl={edl} clip={p.clip} place={p.place} seqFrom={p.from} animateIn={p.animateIn} exitAt={p.exitAt} sizePx={p.size} corner={p.corner} />
        </Sequence>
      ))}
      {rest.map((o) => (
        <Sequence key={o.id} from={o.from} durationInFrames={o.durationInFrames} premountFor={Math.round(edl.fps)} name={`${o.id} ${o.type}`}>
          <OverlayView edl={edl} overlay={o} />
        </Sequence>
      ))}
      {edl.captions.burn ? <Captions edl={edl} /> : null}
      {cutsWith(edl, "sweep").map((f) => (
        <Sequence key={`sweep-${f}`} from={Math.max(0, f - half)} durationInFrames={SWEEP_FRAMES} name={`sweep ${f}`}>
          <BarSweep theme={edl.theme} />
        </Sequence>
      ))}
      {cutsWith(edl, "leak").map((f) => (
        <Sequence key={`leak-${f}`} from={Math.max(0, f - LEAK_FRAMES / 2)} durationInFrames={LEAK_FRAMES} name={`leak ${f}`}>
          <LightLeak />
        </Sequence>
      ))}
      {edl.progress ? <Progress edl={edl} /> : null}
      {edl.audio ? <Audio src={mediaSrc(edl.base, edl.audio)} /> : null}
    </AbsoluteFill>
  );
};
