import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { GuitarRoom } from "../components/Guitarist";
import { RunnerTrack } from "../components/Runner";
import { LabelChip } from "../components/LabelChip";
import { clamp } from "../theme";
import { COPY } from "../copy";

// Hand-drawn looking orange divider that grows down the middle and "boils" a little every 3 frames.
export const Divider: React.FC = () => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [6, 18], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const step = Math.floor(frame / 3);
  const edge = (base: number, amp: number, period: number, phase: number) => {
    const pts: string[] = [];
    for (let y = -20; y <= 1100; y += 20) {
      pts.push(
        `${(base + amp * Math.sin(y / period + phase + step * 0.6)).toFixed(1)},${y}`,
      );
    }
    return pts;
  };
  const band = `M${edge(14, 3.5, 38, 0).join(" L")} L${edge(50, 3.5, 44, 1.3).reverse().join(" L")} Z`;
  const stripe = `M${edge(21, 2, 30, 2.1).join(" L")} L${edge(30, 2, 34, 0.4).reverse().join(" L")} Z`;
  return (
    <svg
      width={64}
      height={1080}
      viewBox="0 0 64 1080"
      style={{ position: "absolute", left: 928, top: 0 }}
    >
      <defs>
        <clipPath id="ss-grow">
          <rect x={0} y={0} width={64} height={1080 * grow} />
        </clipPath>
      </defs>
      <g clipPath="url(#ss-grow)">
        <path d={band} fill="#FF7A2F" />
        <path d={stripe} fill="#FFC43D" />
      </g>
    </svg>
  );
};

export const SplitScreenScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inLeft = spring({
    frame,
    fps,
    config: { damping: 200 },
    durationInFrames: 16,
  });
  const inRight = spring({
    frame: frame - 3,
    fps,
    config: { damping: 200 },
    durationInFrames: 16,
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#FFF4E4", overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 960,
          height: 1080,
          overflow: "hidden",
          translate: `${(inLeft - 1) * 960}px 0px`,
        }}
      >
        <GuitarRoom />
        <LabelChip text={COPY.split.left} delay={14} x={104} y={84} />
      </div>
      <div
        style={{
          position: "absolute",
          left: 960,
          top: 0,
          width: 960,
          height: 1080,
          overflow: "hidden",
          translate: `${(1 - inRight) * 960}px 0px`,
        }}
      >
        <RunnerTrack />
        <LabelChip text={COPY.split.right} delay={18} x={64} y={84} />
      </div>
      <Divider />
    </AbsoluteFill>
  );
};
