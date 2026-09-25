import React from "react";

// Shows a 960x1080 panel (GuitarRoom, RunnerTrack) scaled down inside a card, still animating.
export const MiniScene: React.FC<{
  width: number;
  height: number;
  scale: number;
  offsetX?: number;
  offsetY?: number;
  children: React.ReactNode;
}> = ({ width, height, scale, offsetX = 0, offsetY = 0, children }) => (
  <div style={{ position: "relative", width, height, overflow: "hidden" }}>
    <div
      style={{
        position: "absolute",
        left: offsetX,
        top: offsetY,
        width: 960,
        height: 1080,
        transformOrigin: "0 0",
        scale: `${scale}`,
      }}
    >
      {children}
    </div>
  </div>
);
