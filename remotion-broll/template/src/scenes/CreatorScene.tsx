import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { noise2D } from "@remotion/noise";
import { AppIcons } from "../components/AppIcons";
import { POPPINS, clamp } from "../theme";
import { COPY } from "../copy";

// Where the camera lens of the illustration lands on the 1920x1080 frame.
const LENS = { x: 900, y: 385 };

const BOKEH = new Array(9).fill(0).map((_, i) => ({
  x: random(`bokeh-x-${i}`) * 1920,
  y: random(`bokeh-y-${i}`) * 1080,
  r: 30 + random(`bokeh-r-${i}`) * 90,
  speed: 0.2 + random(`bokeh-s-${i}`) * 0.6,
}));

export const Bokeh: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {BOKEH.map((b, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: b.x - b.r + noise2D(`bokeh-${i}`, frame / 90, 0) * 30,
            top: b.y - b.r - frame * b.speed,
            width: b.r * 2,
            height: b.r * 2,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 70%)",
          }}
        />
      ))}
    </>
  );
};

const INSET = 56;
const ARM = 84;
const CORNERS = [
  `M${INSET},${INSET + ARM} L${INSET},${INSET} L${INSET + ARM},${INSET}`,
  `M${1920 - INSET - ARM},${INSET} L${1920 - INSET},${INSET} L${1920 - INSET},${INSET + ARM}`,
  `M${INSET},${1080 - INSET - ARM} L${INSET},${1080 - INSET} L${INSET + ARM},${1080 - INSET}`,
  `M${1920 - INSET - ARM},${1080 - INSET} L${1920 - INSET},${1080 - INSET} L${1920 - INSET},${1080 - INSET - ARM}`,
];

// Camera viewfinder UI: corner brackets, blinking REC and a running timecode.
const Viewfinder: React.FC = () => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [8, 18], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const tc = 12 * 30 + 18 + frame;
  const seconds = String(Math.floor(tc / 30) % 60).padStart(2, "0");
  const frames = String(tc % 30).padStart(2, "0");
  return (
    <AbsoluteFill style={{ opacity: appear, scale: `${1.04 - 0.04 * appear}` }}>
      <svg
        width={1920}
        height={1080}
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          filter: "drop-shadow(0 2px 6px rgba(60,20,0,0.35))",
        }}
      >
        {CORNERS.map((d) => (
          <path
            key={d}
            d={d}
            fill="none"
            stroke="#FFFFFF"
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ))}
      </svg>
      <div
        style={{
          position: "absolute",
          left: 104,
          top: 96,
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "10px 22px",
          borderRadius: 14,
          backgroundColor: "rgba(30, 14, 6, 0.55)",
          fontFamily: POPPINS,
          fontWeight: 700,
          fontSize: 32,
          color: "#FFFFFF",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        <div
          style={{
            width: 22,
            height: 22,
            borderRadius: 11,
            backgroundColor: "#FF3B30",
            opacity: frame % 30 < 18 ? 1 : 0.2,
          }}
        />
        <span>{COPY.creator.rec}</span>
        <span
          style={{ fontWeight: 500, opacity: 0.9 }}
        >{`00:00:${seconds}:${frames}`}</span>
      </div>
      <div
        style={{
          position: "absolute",
          right: 104,
          top: 104,
          width: 70,
          height: 34,
          borderRadius: 8,
          border: "4px solid #FFFFFF",
          padding: 4,
          display: "flex",
          gap: 4,
          boxShadow: "0 2px 6px rgba(60,20,0,0.35)",
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{ flex: 1, backgroundColor: "#FFFFFF", borderRadius: 2 }}
          />
        ))}
        <div
          style={{
            position: "absolute",
            right: -12,
            top: 7,
            width: 6,
            height: 12,
            borderRadius: 2,
            backgroundColor: "#FFFFFF",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// AI illustration (codex-imagegen cutout) brought to life with code: pop-in, breathing, sway, push-in.
export const CreatorScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const enter = spring({
    frame: frame - 3,
    fps,
    config: { damping: 14, stiffness: 150 },
  });
  const breathe = 1 + 0.009 * Math.sin(((frame / fps) * 2 * Math.PI) / 1.7);
  const sway = 0.7 * Math.sin(((frame / fps) * 2 * Math.PI) / 2.6);
  const push = interpolate(frame, [0, durationInFrames], [1, 1.07]);
  const size = 0.9 + 0.1 * enter;
  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(circle at 36% 46%, #FFF3E2 0%, #FFD4A8 40%, #FF9D5C 100%)",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill style={{ scale: `${push}`, transformOrigin: "42% 55%" }}>
        <Bokeh />
        <div
          style={{
            position: "absolute",
            left: 450,
            top: 996,
            width: 520,
            height: 52,
            borderRadius: "50%",
            backgroundColor: "rgba(120, 50, 10, 0.22)",
            filter: "blur(10px)",
            scale: `${enter}`,
          }}
        />
        <Img
          src={staticFile("creator-cutout.png")}
          style={{
            position: "absolute",
            left: 250,
            top: 170,
            width: 880,
            height: 880,
            transformOrigin: "50% 96%",
            scale: `${size} ${size * breathe}`,
            rotate: `${sway}deg`,
            translate: `0px ${(1 - enter) * 140}px`,
            opacity: Math.min(1, enter * 2),
          }}
        />
      </AbsoluteFill>
      <Viewfinder />
      <AppIcons origin={LENS} />
      <AbsoluteFill
        style={{
          backgroundColor: "#FFFFFF",
          opacity: interpolate(frame, [5, 6, 13], [0, 0.6, 0], clamp),
        }}
      />
    </AbsoluteFill>
  );
};
