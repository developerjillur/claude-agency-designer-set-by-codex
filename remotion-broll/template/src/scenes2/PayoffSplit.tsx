import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { GuitarRoom } from "../components/Guitarist";
import { LabelChip } from "../components/LabelChip";
import { Divider } from "../scenes/SplitScreenScene";
import { COPY } from "../copy";

// Payoff: the same guitarist on day 1 (alone at home) and day 365 (small stage, a crowd).
export const PayoffSplit: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inLeft = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 16 });
  const inRight = spring({ frame: frame - 3, fps, config: { damping: 200 }, durationInFrames: 16 });
  return (
    <AbsoluteFill style={{ backgroundColor: "#1A0F2E", overflow: "hidden" }}>
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
        <LabelChip text={COPY.payoff.before} delay={12} x={104} y={84} />
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
        <GuitarRoom stage />
        <LabelChip text={COPY.payoff.after} delay={16} x={64} y={84} tone="light" />
      </div>
      <Divider />
    </AbsoluteFill>
  );
};
