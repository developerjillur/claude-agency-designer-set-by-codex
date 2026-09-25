import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { GuitarRoom } from "../components/Guitarist";
import { MiniScene } from "../components/MiniScene";
import { RunnerTrack } from "../components/Runner";
import { POPPINS, clamp } from "../theme";
import { COPY } from "../copy";

const CARD_W = 500;
const CARD_H = 560;
const GAP = 60;
const LEFT = (1920 - (3 * CARD_W + 2 * GAP)) / 2;
const INNER_W = CARD_W - 16;
const INNER_H = CARD_H - 16;

const CARDS = [
  { label: COPY.recap[0], kind: "guitar", tilt: -3 },
  { label: COPY.recap[1], kind: "creator", tilt: 0 },
  { label: COPY.recap[2], kind: "runner", tilt: 3 },
] as const;

const CreatorCard: React.FC = () => {
  const frame = useCurrentFrame();
  const breathe = 1 + 0.009 * Math.sin((frame / 30) * ((2 * Math.PI) / 1.7));
  return (
    <div
      style={{
        position: "relative",
        width: INNER_W,
        height: INNER_H,
        overflow: "hidden",
        background: "radial-gradient(circle at 45% 45%, #FFF3E2 0%, #FFD4A8 45%, #FF9D5C 100%)",
      }}
    >
      <Img
        src={staticFile("creator-cutout.png")}
        style={{
          position: "absolute",
          left: -34,
          top: -6,
          width: 560,
          height: 560,
          transformOrigin: "50% 96%",
          scale: `1 ${breathe}`,
        }}
      />
    </div>
  );
};

// Recap: the three characters as live cards on a dark board, one per step.
export const StoryCards: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const push = interpolate(frame, [0, durationInFrames], [1, 1.04]);
  return (
    <AbsoluteFill
      style={{ background: "radial-gradient(circle at 50% 40%, #2B2140 0%, #120D1A 70%)" }}
    >
      <AbsoluteFill style={{ scale: `${push}` }}>
        {CARDS.map((card, i) => {
          const s = spring({ frame: frame - i * 5, fps, config: { damping: 14, stiffness: 120 } });
          const labelIn = interpolate(frame, [18 + i * 5, 28 + i * 5], [0, 1], clamp);
          return (
            <div key={card.label} style={{ position: "absolute", left: LEFT + i * (CARD_W + GAP), top: 170 }}>
              <div
                style={{
                  width: CARD_W,
                  height: CARD_H,
                  borderRadius: 28,
                  overflow: "hidden",
                  border: "8px solid #FFFFFF",
                  boxShadow: "0 30px 70px rgba(0, 0, 0, 0.45)",
                  translate: `0px ${(1 - s) * 820}px`,
                  rotate: `${card.tilt * (1 + (1 - s) * 2)}deg`,
                }}
              >
                {card.kind === "guitar" ? (
                  <MiniScene width={INNER_W} height={INNER_H} scale={INNER_W / 960}>
                    <GuitarRoom />
                  </MiniScene>
                ) : null}
                {card.kind === "creator" ? <CreatorCard /> : null}
                {card.kind === "runner" ? (
                  <MiniScene width={INNER_W} height={INNER_H} scale={INNER_W / 960}>
                    <RunnerTrack />
                  </MiniScene>
                ) : null}
              </div>
              <div
                style={{
                  marginTop: 34,
                  textAlign: "center",
                  fontFamily: POPPINS,
                  fontWeight: 700,
                  fontSize: 52,
                  color: "#FFFFFF",
                  opacity: labelIn,
                  translate: `0px ${(1 - labelIn) * 20}px`,
                }}
              >
                {card.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
