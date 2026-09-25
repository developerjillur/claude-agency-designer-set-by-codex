import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { POPPINS, clamp } from "../theme";

// Numbered chapter card: the badge spins in, the title rises word by word, an accent bar grows.
export const StepCard: React.FC<{
  step: number;
  lines: string[];
  color: string;
  accent: string;
}> = ({ step, lines, color, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const badge = spring({ frame: frame - 2, fps, config: { damping: 11, stiffness: 160 } });
  const label = interpolate(frame, [6, 16], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const bar = interpolate(frame, [12, 28], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: color, overflow: "hidden" }}>
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const r = 80 + random(`step-r-${step}-${i}`) * 160;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: random(`step-x-${step}-${i}`) * 1920 - r,
              top: random(`step-y-${step}-${i}`) * 1080 - r - frame * (0.4 + i * 0.12),
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              backgroundColor: "rgba(255, 255, 255, 0.08)",
            }}
          />
        );
      })}
      <div
        style={{
          position: "absolute",
          left: 200,
          top: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          gap: 70,
          transformOrigin: "30% 50%",
          scale: `${interpolate(frame, [0, 60], [1, 1.05])}`,
        }}
      >
        <div
          style={{
            width: 260,
            height: 260,
            flexShrink: 0,
            borderRadius: 130,
            backgroundColor: "#FFFFFF",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: POPPINS,
            fontWeight: 800,
            fontSize: 170,
            color,
            scale: `${badge}`,
            rotate: `${(1 - badge) * -40}deg`,
            translate: `0px ${Math.sin(frame / 8) * 6}px`,
            boxShadow: "0 24px 60px rgba(0, 0, 0, 0.18)",
          }}
        >
          {step}
        </div>
        <div style={{ fontFamily: POPPINS, color: "#FFFFFF" }}>
          <div
            style={{
              fontWeight: 700,
              fontSize: 40,
              letterSpacing: 6,
              textTransform: "uppercase",
              color: accent,
              opacity: label,
              translate: `${(1 - label) * -30}px 0px`,
            }}
          >
            {`Step ${step}`}
          </div>
          <div
            style={{
              marginTop: 10,
              fontWeight: 800,
              fontSize: 104,
              lineHeight: 1.05,
              letterSpacing: -2,
              maxWidth: 1250,
            }}
          >
            {lines.map((line, row) => (
              <div key={line}>
                {line.split(" ").map((word, col) => {
              const i = lines.slice(0, row).join(" ").split(" ").filter(Boolean).length + col;
              const at = 10 + i * 3;
              return (
                <span
                  key={`${word}-${col}`}
                  style={{
                    display: "inline-block",
                    marginRight: "0.25em",
                    opacity: interpolate(frame, [at, at + 8], [0, 1], clamp),
                    translate: `0px ${interpolate(frame, [at, at + 10], [40, 0], {
                      ...clamp,
                      easing: Easing.bezier(0.16, 1, 0.3, 1),
                    })}px`,
                  }}
                >
                  {word}
                </span>
              );
                })}
              </div>
            ))}
          </div>
          <div
            style={{
              marginTop: 28,
              height: 12,
              width: 260 * bar,
              borderRadius: 6,
              backgroundColor: accent,
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
