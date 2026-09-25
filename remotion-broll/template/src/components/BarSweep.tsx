import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { clamp } from "../theme";

const BLOCK_W = 2300;

// Orange and yellow bars sweep left to right and hide the cut underneath (used as a TransitionSeries overlay).
export const BarSweep: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const mid = (durationInFrames - 1) / 2;
  const left = interpolate(
    frame,
    [0, mid, durationInFrames - 1],
    [-BLOCK_W - 300, width / 2 - BLOCK_W / 2, width + 300],
    { ...clamp, easing: Easing.bezier(0.45, 0, 0.55, 1) },
  );
  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: -60,
          left,
          width: BLOCK_W,
          height: height + 120,
          display: "flex",
          transform: "skewX(-12deg)",
        }}
      >
        <div style={{ flex: 3, backgroundColor: "#E85D1C" }} />
        <div style={{ flex: 0.35, backgroundColor: "#FFF4E4" }} />
        <div style={{ flex: 4, backgroundColor: "#FF7A2F" }} />
        <div style={{ flex: 0.5, backgroundColor: "#FFE08A" }} />
        <div style={{ flex: 3, backgroundColor: "#FFC43D" }} />
      </div>
    </AbsoluteFill>
  );
};
