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
import { COPY } from "../copy";

const WORDS = COPY.end.words;
export const CLICK_AT = 84;
const BELL =
  "M12 3a6 6 0 0 0-6 6v3.6L4.2 16h15.6L18 12.6V9a6 6 0 0 0-6-6zm-2.4 14.5a2.4 2.4 0 0 0 4.8 0z";

// End card: the call to action rises in, a cursor clicks Subscribe, the bell rings.
export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const btnIn = spring({ frame: frame - 34, fps, config: { damping: 12, stiffness: 160 } });
  const travel = interpolate(frame, [52, 80], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.33, 0, 0.2, 1),
  });
  const cursor = {
    x: interpolate(travel, [0, 1], [1560, 1040]),
    y: interpolate(travel, [0, 1], [1010, 772]),
  };
  const press = interpolate(frame, [CLICK_AT, CLICK_AT + 3, CLICK_AT + 12], [1, 0.92, 1], clamp);
  const subscribed = frame >= CLICK_AT + 2;
  const ripple = interpolate(frame, [CLICK_AT, CLICK_AT + 16], [0, 1], clamp);
  const ringAge = frame - CLICK_AT - 2;
  const bell = ringAge >= 0 ? 22 * Math.exp(-ringAge / 10) * Math.sin(ringAge * 0.9) : 0;
  const cursorOpacity = interpolate(frame, [50, 56, 120, 130], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(140deg, #FF9A4D 0%, #FF6A1F 60%, #E8521A 100%)",
        overflow: "hidden",
      }}
    >
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const r = 90 + random(`end-r-${i}`) * 170;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: random(`end-x-${i}`) * 1920 - r,
              top: random(`end-y-${i}`) * 1080 - r - frame * (0.3 + i * 0.1),
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              backgroundColor: "rgba(255, 255, 255, 0.08)",
            }}
          />
        );
      })}
      <AbsoluteFill style={{ scale: `${interpolate(frame, [0, 150], [1, 1.04])}` }}>
      <div
        style={{
          position: "absolute",
          left: 210,
          top: 250,
          width: 1500,
          textAlign: "center",
          fontFamily: POPPINS,
          fontWeight: 800,
          fontSize: 116,
          lineHeight: 1.1,
          letterSpacing: -2,
          color: "#FFFFFF",
        }}
      >
        {WORDS.map((word, i) => {
          const at = 6 + i * 4;
          return (
            <React.Fragment key={word}>
              {i === 3 ? <br /> : null}
            <span
              style={{
                display: "inline-block",
                margin: "0 0.13em",
                opacity: interpolate(frame, [at, at + 8], [0, 1], clamp),
                translate: `0px ${interpolate(frame, [at, at + 10], [40, 0], {
                  ...clamp,
                  easing: Easing.bezier(0.16, 1, 0.3, 1),
                })}px`,
              }}
            >
              {word}
            </span>
            </React.Fragment>
          );
        })}
      </div>
      <div
        style={{
          position: "absolute",
          left: 960 - 230,
          top: 700,
          width: 460,
          height: 124,
          borderRadius: 62,
          backgroundColor: subscribed ? "#2B1D16" : "#FFFFFF",
          color: subscribed ? "#FFF4E4" : "#E8521A",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 18,
          fontFamily: POPPINS,
          fontWeight: 800,
          fontSize: 50,
          scale: `${btnIn * press}`,
          boxShadow: "0 20px 50px rgba(120, 40, 0, 0.35)",
        }}
      >
        <svg width={52} height={52} viewBox="0 0 24 24" style={{ rotate: `${bell}deg` }}>
          <path d={BELL} fill={subscribed ? "#FFC43D" : "#E8521A"} />
        </svg>
        {subscribed ? COPY.end.pressed : COPY.end.button}
      </div>
      {ripple > 0 && ripple < 1 ? (
        <div
          style={{
            position: "absolute",
            left: 1040 - 40 - 90 * ripple,
            top: 772 - 40 - 90 * ripple,
            width: 80 + 180 * ripple,
            height: 80 + 180 * ripple,
            borderRadius: "50%",
            border: "6px solid rgba(255, 255, 255, 0.9)",
            opacity: 1 - ripple,
          }}
        />
      ) : null}
      <svg
        width={56}
        height={70}
        viewBox="0 0 28 42"
        style={{
          position: "absolute",
          left: cursor.x,
          top: cursor.y,
          opacity: cursorOpacity,
          scale: `${frame >= CLICK_AT && frame < CLICK_AT + 6 ? 0.88 : 1}`,
          transformOrigin: "0 0",
          filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.3))",
        }}
      >
        <path
          d="M1,1 L1,33 L9,26 L15,40 L21,37 L15,24 L26,24 Z"
          fill="#FFFFFF"
          stroke="#1E1B2E"
          strokeWidth={2}
          strokeLinejoin="round"
        />
      </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
