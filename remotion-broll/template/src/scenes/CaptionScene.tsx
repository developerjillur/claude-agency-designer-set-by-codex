import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Underline } from "@remotion/rough-notation";
import { POPPINS, clamp } from "../theme";
import { COPY } from "../copy";

export const CAPTION_BG =
  "radial-gradient(ellipse at 50% 58%, #3A1231 0%, #1B0B18 55%, #0B070B 100%)";
export const FIRST_LINE = COPY.caption.first;

// Kinetic caption words: each word rises in, key words get a hand-drawn underline.
export const CaptionWords: React.FC<{
  words: string[];
  keyWords?: string[];
  start?: number;
  underlineFrom?: number;
  zoom?: number;
}> = ({ words, keyWords = [], start = 6, underlineFrom = 36, zoom = 1 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        width: 1500,
        textAlign: "center",
        fontFamily: POPPINS,
        fontWeight: 700,
        fontSize: 104,
        lineHeight: 1.2,
        color: "#FFFFFF",
        letterSpacing: -1,
        scale: `${zoom}`,
      }}
    >
      {words.map((word, i) => {
        const at = start + i * 4;
        const opacity = interpolate(frame, [at, at + 8], [0, 1], clamp);
        const rise = interpolate(frame, [at, at + 10], [36, 0], {
          ...clamp,
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        });
        const blur = interpolate(frame, [at, at + 8], [10, 0], clamp);
        return (
          <span
            key={word}
            style={{
              display: "inline-block",
              margin: "0 0.13em",
              opacity,
              translate: `0px ${rise}px`,
              filter: `blur(${blur}px)`,
            }}
          >
            {keyWords.includes(word) ? (
              <Underline
                progress={interpolate(frame, [underlineFrom, underlineFrom + 12], [0, 1], clamp)}
                color="#FFC43D"
                strokeWidth={9}
                iterations={1}
                seed={7}
                padding={{ top: 2 }}
              >
                <span style={{ color: "#FFC43D" }}>{word}</span>
              </Underline>
            ) : (
              word
            )}
          </span>
        );
      })}
    </div>
  );
};

// Kinetic caption: words rise in one by one, the key word gets a hand-drawn underline.
export const CaptionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.05]);
  return (
    <AbsoluteFill
      style={{ background: CAPTION_BG, alignItems: "center", justifyContent: "center" }}
    >
      <CaptionWords words={FIRST_LINE} keyWords={COPY.caption.firstKey} zoom={zoom} />
    </AbsoluteFill>
  );
};
