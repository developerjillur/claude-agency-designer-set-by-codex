import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { POPPINS } from "../theme";

// Dark location-style label that pops in, like the "MODEL SHOP" tag in the reference.
export const LabelChip: React.FC<{
  text: string;
  delay: number;
  x?: number;
  y?: number;
  tone?: "dark" | "light";
}> = ({ text, delay, x = 56, y = 56, tone = "dark" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: frame - delay,
    fps,
    config: { damping: 13, stiffness: 190 },
  });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        padding: "14px 26px",
        borderRadius: 16,
        backgroundColor: tone === "dark" ? "rgba(43, 29, 22, 0.9)" : "#FFF4E4",
        color: tone === "dark" ? "#FFF4E4" : "#2B1D16",
        fontFamily: POPPINS,
        fontWeight: 700,
        fontSize: 38,
        letterSpacing: 2,
        textTransform: "uppercase",
        whiteSpace: "nowrap",
        transformOrigin: "0% 50%",
        scale: `${pop}`,
        opacity: Math.min(1, Math.max(0, pop * 1.6)),
        boxShadow: "0 10px 24px rgba(43, 29, 22, 0.25)",
      }}
    >
      {text}
    </div>
  );
};
