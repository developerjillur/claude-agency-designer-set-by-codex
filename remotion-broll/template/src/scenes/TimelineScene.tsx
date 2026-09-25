import React from "react";
import {
  AbsoluteFill,
  interpolate,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { POPPINS, clamp } from "../theme";

export const ROW_H = 150;
export const VIDEO_Y = 300;
export const AUDIO_Y = 520;
const V_CLIPS = [
  { x: 300, w: 250 },
  { x: 572, w: 600 },
  { x: 1194, w: 170 },
];
const A_CLIPS = [
  { x: 300, w: 540 },
  { x: 862, w: 330 },
];
const PLAY_X0 = 300;
const PLAY_X1 = 1470;

const Thumbs: React.FC<{ w: number }> = ({ w }) => {
  const count = Math.max(1, Math.floor((w - 20) / 112));
  return (
    <div
      style={{
        position: "absolute",
        left: 14,
        top: 14,
        bottom: 14,
        display: "flex",
        gap: 12,
      }}
    >
      {new Array(count).fill(0).map((_, i) => (
        <div
          key={i}
          style={{
            width: 100,
            height: "100%",
            borderRadius: 14,
            backgroundColor: "rgba(255, 255, 255, 0.18)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg width={52} height={40} viewBox="0 0 52 40">
            <circle cx={38} cy={10} r={6} fill="rgba(255,255,255,0.75)" />
            <path
              d="M2,38 L18,16 L28,28 L36,20 L50,38 Z"
              fill="rgba(255,255,255,0.75)"
            />
          </svg>
        </div>
      ))}
    </div>
  );
};

const Wave: React.FC<{ w: number; seed: number; delay: number }> = ({
  w,
  seed,
  delay,
}) => {
  const frame = useCurrentFrame();
  const bars = Math.floor((w - 28) / 14);
  return (
    <svg
      width={w}
      height={ROW_H}
      style={{ position: "absolute", left: 0, top: 0 }}
    >
      {new Array(bars).fill(0).map((_, i) => {
        const envelope = 0.35 + 0.65 * Math.abs(Math.sin(i * 0.33 + seed));
        const h = (0.45 + 0.55 * random(`wave-${seed}-${i}`)) * envelope * 108;
        const grow = interpolate(
          frame - delay - i * 0.35,
          [0, 8],
          [0, 1],
          clamp,
        );
        return (
          <rect
            key={i}
            x={16 + i * 14}
            y={ROW_H / 2 - (h * grow) / 2}
            width={7}
            height={Math.max(2, h * grow)}
            rx={3.5}
            fill="rgba(255, 255, 255, 0.62)"
          />
        );
      })}
    </svg>
  );
};

export const Clip: React.FC<{
  x: number;
  w: number;
  y: number;
  delay: number;
  kind: "video" | "audio";
  active: boolean;
  index: number;
}> = ({ x, w, y, delay, kind, active, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const grow = spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, stiffness: 170 },
  });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: Math.max(0, w * grow),
        height: ROW_H,
        borderRadius: 26,
        background:
          kind === "video"
            ? "linear-gradient(180deg, #8B5CF6 0%, #6D28D9 100%)"
            : "linear-gradient(180deg, #A855F7 0%, #7E22CE 100%)",
        boxShadow: active
          ? "0 0 0 5px #FFFFFF, 0 18px 40px rgba(76, 29, 149, 0.35)"
          : "0 14px 30px rgba(76, 29, 149, 0.25)",
        filter: active ? "brightness(1.12)" : "none",
        overflow: "hidden",
      }}
    >
      {kind === "video" ? (
        <Thumbs w={w} />
      ) : (
        <Wave w={w} seed={index} delay={delay} />
      )}
    </div>
  );
};

export const TrackIcon: React.FC<{
  kind: "video" | "audio";
  y: number;
  delay: number;
}> = ({ kind, y, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  return (
    <div
      style={{
        position: "absolute",
        left: 150,
        top: y + (ROW_H - 110) / 2,
        width: 110,
        height: 110,
        borderRadius: 30,
        backgroundColor: "#FFFFFF",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 12px 28px rgba(76, 29, 149, 0.18)",
        scale: `${pop}`,
      }}
    >
      <svg width={60} height={60} viewBox="0 0 24 24">
        {kind === "video" ? (
          <path
            d="M3 7.5A2.5 2.5 0 0 1 5.5 5h8A2.5 2.5 0 0 1 16 7.5v9a2.5 2.5 0 0 1-2.5 2.5h-8A2.5 2.5 0 0 1 3 16.5zM17 10l4-2.5v9L17 14z"
            fill="#6D28D9"
          />
        ) : (
          <path
            d="M9 18.5a3 3 0 1 1-2-2.83V5.5l11-2v11a3 3 0 1 1-2-2.83V7.2l-7 1.3z"
            fill="#6D28D9"
          />
        )}
      </svg>
    </div>
  );
};

export const Ruler: React.FC = () => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [0, 10], [0, 1], clamp);
  const ticks = new Array(21).fill(0).map((_, i) => PLAY_X0 + i * 60);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 176,
        width: 1920,
        height: 60,
        opacity: appear,
      }}
    >
      {ticks.map((x, i) => (
        <div
          key={x}
          style={{
            position: "absolute",
            left: x - 1.5,
            top: i % 4 === 0 ? 30 : 40,
            width: 3,
            height: i % 4 === 0 ? 24 : 14,
            borderRadius: 2,
            backgroundColor: "rgba(76, 29, 149, 0.45)",
          }}
        />
      ))}
      {ticks
        .filter((_, i) => i % 4 === 0)
        .map((x, i) => (
          <div
            key={`l${x}`}
            style={{
              position: "absolute",
              left: x + 8,
              top: 0,
              fontFamily: POPPINS,
              fontWeight: 600,
              fontSize: 22,
              color: "rgba(76, 29, 149, 0.7)",
            }}
          >
            {`0:${String(i * 4).padStart(2, "0")}`}
          </div>
        ))}
    </div>
  );
};

// Editing-timeline UI built from divs: clips grow in, waveforms rise, the playhead scrubs across.
export const TimelineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const playhead = interpolate(frame, [8, 54], [PLAY_X0, PLAY_X1], clamp);
  const headIn = spring({ frame: frame - 4, fps, config: { damping: 200 } });
  return (
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(135deg, #FCE4F1 0%, #EBD8FF 48%, #C3A2FF 100%)",
      }}
    >
      <Ruler />
      <TrackIcon kind="video" y={VIDEO_Y} delay={0} />
      <TrackIcon kind="audio" y={AUDIO_Y} delay={3} />
      {V_CLIPS.map((c, i) => (
        <Clip
          key={`v${c.x}`}
          x={c.x}
          w={c.w}
          y={VIDEO_Y}
          delay={2 + i * 4}
          kind="video"
          index={i}
          active={playhead >= c.x && playhead <= c.x + c.w}
        />
      ))}
      {A_CLIPS.map((c, i) => (
        <Clip
          key={`a${c.x}`}
          x={c.x}
          w={c.w}
          y={AUDIO_Y}
          delay={5 + i * 4}
          kind="audio"
          index={i}
          active={playhead >= c.x && playhead <= c.x + c.w}
        />
      ))}
      <div
        style={{
          position: "absolute",
          left: playhead - 3,
          top: 236,
          width: 6,
          height: 470,
          borderRadius: 3,
          backgroundColor: "#4C1D95",
          opacity: headIn,
          boxShadow: "0 0 18px rgba(76, 29, 149, 0.45)",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: -15,
            top: -30,
            width: 36,
            height: 36,
            borderRadius: 18,
            backgroundColor: "#4C1D95",
            border: "5px solid #FFFFFF",
            boxSizing: "border-box",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
