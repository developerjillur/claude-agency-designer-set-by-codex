import React from "react";
import {
  Easing,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { noise2D } from "@remotion/noise";
import { clamp } from "../theme";

const SIZE = 300;

// Round picture-in-picture of the presenter. In production, swap the photo for the talking-head clip.
export const RoundPip: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const pop = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 170, mass: 0.8 },
  });
  const out = interpolate(
    frame,
    [durationInFrames - 8, durationInFrames - 1],
    [1, 0],
    {
      ...clamp,
      easing: Easing.in(Easing.cubic),
    },
  );
  const zoom = interpolate(frame, [0, durationInFrames], [1.08, 1.16]);
  // Voice-like pulse on the ring so the bubble reads as "speaking".
  const talk = 1 + 0.04 * Math.abs(noise2D("pip-voice", frame / 5, 0));
  return (
    <div
      style={{
        position: "absolute",
        right: 100,
        bottom: 100,
        width: SIZE,
        height: SIZE,
        scale: `${pop * out}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: -16,
          borderRadius: "50%",
          border: "5px solid rgba(255, 196, 61, 0.95)",
          scale: `${talk}`,
        }}
      />
      <div
        style={{
          width: SIZE,
          height: SIZE,
          borderRadius: "50%",
          overflow: "hidden",
          border: "8px solid #FFFFFF",
          boxShadow: "0 18px 44px rgba(20, 10, 5, 0.38)",
          backgroundColor: "#3A2A22",
        }}
      >
        <Img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 38%",
            scale: `${zoom}`,
          }}
        />
      </div>
    </div>
  );
};
