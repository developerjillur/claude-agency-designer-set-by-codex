import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { GuitarRoom } from "../components/Guitarist";
import { MiniScene } from "../components/MiniScene";
import { POPPINS } from "../theme";
import { COPY } from "../copy";

const DAYS = 30;
const FILL_START = 18;
const FILL_STEP = 3;
export const HABIT_DONE = FILL_START + DAYS * FILL_STEP;

// Step 1 B-roll: the guitarist keeps practising (live, in a card) while a 30-day streak fills up.
export const HabitScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cardIn = spring({ frame, fps, config: { damping: 15, stiffness: 120 } });
  const calIn = spring({ frame: frame - 6, fps, config: { damping: 15, stiffness: 120 } });
  const filled = Math.max(1, Math.min(DAYS, Math.floor((frame - FILL_START) / FILL_STEP) + 1));
  const bump = Math.sin(Math.min(1, Math.max(0, (frame - HABIT_DONE) / 10)) * Math.PI);
  return (
    <AbsoluteFill style={{ background: "linear-gradient(160deg, #FFF6EA 0%, #FFE2C2 100%)" }}>
      <div
        style={{
          position: "absolute",
          left: 150,
          top: 135,
          borderRadius: 36,
          overflow: "hidden",
          border: "10px solid #FFFFFF",
          boxShadow: "0 30px 70px rgba(120, 60, 10, 0.25)",
          translate: `${(1 - cardIn) * -760}px 0px`,
          rotate: `${-2.5 - (1 - cardIn) * 8}deg`,
        }}
      >
        <MiniScene width={720} height={810} scale={0.75}>
          <GuitarRoom />
        </MiniScene>
      </div>
      <div
        style={{
          position: "absolute",
          left: 1010,
          top: 170,
          width: 760,
          padding: "44px 48px",
          borderRadius: 36,
          backgroundColor: "#FFFFFF",
          boxShadow: "0 30px 70px rgba(120, 60, 10, 0.18)",
          translate: `${(1 - calIn) * 820}px 0px`,
          fontFamily: POPPINS,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontWeight: 700, fontSize: 40, color: "#8E879A" }}>{COPY.habit.title}</div>
          <div
            style={{
              fontWeight: 800,
              fontSize: 64,
              color: frame >= HABIT_DONE ? "#FF6A1F" : "#1E1B2E",
              fontVariantNumeric: "tabular-nums",
              scale: `${1 + 0.15 * bump}`,
            }}
          >
            {`Day ${filled}`}
          </div>
        </div>
        <div
          style={{
            marginTop: 34,
            display: "grid",
            gridTemplateColumns: "repeat(6, 1fr)",
            gap: 18,
          }}
        >
          {new Array(DAYS).fill(0).map((_, i) => {
            const at = FILL_START + i * FILL_STEP;
            const on = frame >= at;
            const pop = spring({ frame: frame - at, fps, config: { damping: 12, stiffness: 220 } });
            return (
              <div
                key={i}
                style={{
                  height: 92,
                  borderRadius: 22,
                  backgroundColor: on ? "#FF7A2F" : "#F4EEE5",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  scale: on ? `${0.7 + 0.3 * pop}` : "1",
                }}
              >
                {on ? (
                  <svg width={46} height={46} viewBox="0 0 24 24">
                    <path
                      d="M5 12.5l4.2 4.2L19 7"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth={3.2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeDasharray={24}
                      strokeDashoffset={24 * (1 - Math.min(1, pop))}
                    />
                  </svg>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
