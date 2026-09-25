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

// Chart area in frame coordinates. Values follow the real curve (1 + GROWTH.rate)^day from copy.ts.
const X0 = 1080;
const X1 = 1690;
const YB = 790;
const YT = 300;
const END = Math.pow(1 + GROWTH.rate, GROWTH.days);
// A round top for the axis just above the final value, and four even ticks up to it.
const YMAX = (() => {
  const mag = Math.pow(10, Math.floor(Math.log10(END * 1.05)));
  return ([1, 2, 2.5, 4, 5, 10].map((m) => m * mag).find((v) => v >= END * 1.05) ?? 10 * mag);
})();
const TICKS = [1, 2, 3, 4].map((i) => (YMAX * i) / 4);
const toX = (day: number) => X0 + (day / GROWTH.days) * (X1 - X0);
const toY = (v: number) => YB - (v / YMAX) * (YB - YT);

const CURVE = (() => {
  let d = "";
  for (let day = 0; day <= GROWTH.days; day++) {
    d += `${day === 0 ? "M" : "L"}${toX(day).toFixed(1)},${toY(Math.pow(1 + GROWTH.rate, day)).toFixed(1)} `;
  }
  return d.trim();
})();
const AREA = `${CURVE} L${X1},${YB} L${X0},${YB} Z`;

export const StatScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const card = spring({
    frame,
    fps,
    config: { damping: 200 },
    durationInFrames: 18,
  });
  const title = interpolate(frame, [4, 16], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const progress = interpolate(frame, [12, 50], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.sin),
  });
  const day = progress * GROWTH.days;
  const value = Math.pow(1 + GROWTH.rate, day);
  const tip = { x: toX(day), y: toY(value) };
  const land = interpolate(frame, [50, 55, 62], [1, 1.1, 1], {
    ...clamp,
    easing: Easing.out(Easing.quad),
  });
  const pulse = ((frame - 50) % 20) / 20;
  const legend = interpolate(frame, [14, 24], [0, 1], clamp);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#F4EEE5",
        backgroundImage:
          "radial-gradient(rgba(120, 90, 60, 0.12) 2px, transparent 2px)",
        backgroundSize: "36px 36px",
      }}
    >
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
          top: 200,
          width: 760,
          fontFamily: POPPINS,
          opacity: title,
          translate: `0px ${(1 - title) * 30}px`,
        }}
      >
        <div
          style={{
            fontWeight: 800,
            fontSize: 80,
            lineHeight: 1.04,
            color: "#1E1B2E",
            letterSpacing: -1.5,
          }}
        >
          {COPY.stat.title[0]}
          <br />
          {COPY.stat.title[1]}
        </div>
        <div
          style={{
            marginTop: 34,
            fontWeight: 800,
            fontSize: 190,
            lineHeight: 1,
            color: "#FF6A1F",
            letterSpacing: -4,
            fontVariantNumeric: "tabular-nums",
            transformOrigin: "0% 70%",
            scale: `${land}`,
          }}
        >
          {`${value.toFixed(1)}x`}
        </div>
        <div
          style={{
            marginTop: 14,
            fontWeight: 600,
            fontSize: 52,
            color: "#5B5566",
          }}
        >
          {COPY.stat.result}
        </div>
        <div
          style={{
            marginTop: 70,
            fontWeight: 500,
            fontSize: 30,
            color: "#9A93A6",
          }}
        >
          {(1 + GROWTH.rate).toFixed(2)}<sup style={{ fontSize: 20 }}>{GROWTH.days}</sup> ≈ {END.toFixed(1)}
        </div>
      </div>
      <svg
        width={1920}
        height={1080}
        style={{ position: "absolute", left: 0, top: 0, opacity: card }}
      >
        <defs>
          <clipPath id="stat-reveal">
            <rect
              x={X0 - 12}
              y={0}
              width={Math.max(0, tip.x - X0 + 12)}
              height={1080}
            />
          </clipPath>
        </defs>
        {TICKS.map((v) => (
          <g key={v}>
            <line
              x1={X0}
              y1={toY(v)}
              x2={X1}
              y2={toY(v)}
              stroke="#E9E2D8"
              strokeWidth={2}
              strokeDasharray="6 10"
            />
            <text
              x={X0 - 18}
              y={toY(v) + 8}
              textAnchor="end"
              fontFamily={POPPINS}
              fontWeight={600}
              fontSize={24}
              fill="#A59EAF"
            >
              {`${Number(v.toFixed(1))}x`}
            </text>
          </g>
        ))}
        <line
          x1={X0}
          y1={YB}
          x2={X1}
          y2={YB}
          stroke="#CFC6BB"
          strokeWidth={3}
        />
        <text
          x={X0}
          y={YB + 44}
          fontFamily={POPPINS}
          fontWeight={600}
          fontSize={24}
          fill="#8E879A"
        >
          {COPY.stat.axisStart}
        </text>
        <text
          x={X1}
          y={YB + 44}
          textAnchor="end"
          fontFamily={POPPINS}
          fontWeight={600}
          fontSize={24}
          fill="#8E879A"
        >
          {COPY.stat.axisEnd}
        </text>
        <line
          x1={X0}
          y1={toY(1)}
          x2={Math.max(X0, tip.x)}
          y2={toY(1)}
          stroke="#A39DB0"
          strokeWidth={6}
          strokeDasharray="2 14"
          strokeLinecap="round"
        />
        <g clipPath="url(#stat-reveal)">
          <path d={AREA} fill="#FF6A1F" opacity={0.13} />
          <path
            d={CURVE}
            fill="none"
            stroke="#FF6A1F"
            strokeWidth={9}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
        {progress > 0 ? (
          <g>
            {frame >= 50 ? (
              <circle
                cx={tip.x}
                cy={tip.y}
                r={13 + 26 * pulse}
                fill="none"
                stroke="#FF6A1F"
                strokeWidth={4}
                opacity={1 - pulse}
              />
            ) : null}
            <circle
              cx={tip.x}
              cy={tip.y}
              r={13}
              fill="#FF6A1F"
              stroke="#FFFFFF"
              strokeWidth={5}
            />
          </g>
        ) : null}
      </svg>
      <div
        style={{
          position: "absolute",
          left: X0,
          top: 196,
          display: "flex",
          gap: 34,
          fontFamily: POPPINS,
          fontWeight: 600,
          fontSize: 30,
          color: "#3A3548",
          opacity: legend,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 18,
              height: 18,
              borderRadius: 9,
              backgroundColor: "#FF6A1F",
            }}
          />
          {COPY.stat.lineGrow}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 18,
              height: 18,
              borderRadius: 9,
              backgroundColor: "#A39DB0",
            }}
          />
          {COPY.stat.lineFlat}
        </div>
      </div>
    </AbsoluteFill>
  );
};
