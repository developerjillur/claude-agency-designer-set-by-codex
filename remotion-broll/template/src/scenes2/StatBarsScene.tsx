import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { POPPINS, clamp } from "../theme";
import { COPY, GROWTH } from "../copy";

// Real values of (1 + GROWTH.rate)^days. Bar length is linear in the value, so the year dwarfs the rest.
// Four periods: GROW_START and GROW_LENGTH below time one bar each.
const ROWS = COPY.bars.periods;
const MAX_W = 980;
const MAX_V = Math.pow(1 + GROWTH.rate, Math.max(...COPY.bars.periods.map((r) => r.days)));
const GROW_START = [22, 38, 54, 74];
const GROW_LENGTH = [14, 14, 18, 36];
const growStart = (i: number) => GROW_START[i];
const growLength = (i: number) => GROW_LENGTH[i];
export const BARS_DONE = GROW_START[3] + GROW_LENGTH[3];

const format = (v: number) => `${v.toFixed(v < 2 ? 2 : 1)}x`;

export const StatBarsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const push = interpolate(frame, [0, durationInFrames], [1, 1.035]);
  const card = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 18 });
  const title = interpolate(frame, [4, 16], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#F4EEE5",
        backgroundImage: "radial-gradient(rgba(120, 90, 60, 0.12) 2px, transparent 2px)",
        backgroundSize: "36px 36px",
      }}
    >
      <AbsoluteFill style={{ scale: `${push}` }}>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 110,
          width: 1640,
          height: 860,
          borderRadius: 36,
          backgroundColor: "#FFFFFF",
          boxShadow: "0 30px 80px rgba(60, 30, 10, 0.16)",
          opacity: card,
          translate: `0px ${(1 - card) * 80}px`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 230,
          top: 190,
          fontFamily: POPPINS,
          fontWeight: 800,
          fontSize: 76,
          letterSpacing: -1.5,
          color: "#1E1B2E",
          opacity: title,
          translate: `0px ${(1 - title) * 30}px`,
        }}
      >
        {COPY.bars.title}
      </div>
      {ROWS.map((row, i) => {
        const grow = interpolate(frame, [growStart(i), growStart(i) + growLength(i)], [0, 1], {
          ...clamp,
          easing: i === ROWS.length - 1 ? Easing.in(Easing.quad) : Easing.out(Easing.cubic),
        });
        const value = Math.pow(1 + GROWTH.rate, row.days * grow);
        const width = Math.max(26, (MAX_W * value) / MAX_V) * Math.min(1, grow * 3);
        const rowIn = interpolate(frame, [growStart(i) - 8, growStart(i)], [0, 1], clamp);
        const last = i === ROWS.length - 1;
        const land = last
          ? interpolate(frame, [BARS_DONE, BARS_DONE + 5, BARS_DONE + 12], [1, 1.12, 1], clamp)
          : 1;
        return (
          <div
            key={row.label}
            style={{
              position: "absolute",
              left: 230,
              top: 360 + i * 130,
              display: "flex",
              alignItems: "center",
              fontFamily: POPPINS,
              opacity: rowIn,
            }}
          >
            <div style={{ width: 250, fontWeight: 700, fontSize: 44, color: "#3A3548" }}>{row.label}</div>
            <div
              style={{
                width,
                height: 72,
                borderRadius: 36,
                background: last
                  ? "linear-gradient(90deg, #FF9D5C 0%, #FF6A1F 100%)"
                  : "linear-gradient(90deg, #FFD2AE 0%, #FFB27A 100%)",
              }}
            />
            <div
              style={{
                marginLeft: 26,
                fontWeight: 800,
                fontSize: last ? 64 : 48,
                color: last ? "#FF6A1F" : "#5B5566",
                fontVariantNumeric: "tabular-nums",
                transformOrigin: "0% 50%",
                scale: `${land}`,
              }}
            >
              {format(value)}
            </div>
          </div>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: 230,
          top: 880,
          fontFamily: POPPINS,
          fontWeight: 500,
          fontSize: 28,
          color: "#9A93A6",
          opacity: title,
        }}
      >
        {COPY.bars.note}
      </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
