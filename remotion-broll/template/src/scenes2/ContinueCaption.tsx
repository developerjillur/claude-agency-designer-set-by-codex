import React from "react";
import { AbsoluteFill, Easing, Freeze, interpolate, useCurrentFrame } from "remotion";
import { CAPTION_BG, CaptionWords, FIRST_LINE } from "../scenes/CaptionScene";
import { clamp } from "../theme";
import { COPY } from "../copy";

// Picks up exactly where the first caption ended (frozen on its last frame), lifts it,
// and finishes the sentence underneath.
export const ContinueCaption: React.FC = () => {
  const frame = useCurrentFrame();
  const lift = interpolate(frame, [2, 16], [0, -95], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill
      style={{ background: CAPTION_BG, alignItems: "center", justifyContent: "center" }}
    >
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          scale: `${interpolate(frame, [16, 75], [1, 1.04], clamp)}`,
        }}
      >
      <div style={{ translate: `0px ${lift}px` }}>
        <Freeze frame={59}>
          <CaptionWords words={FIRST_LINE} keyWords={COPY.caption.firstKey} zoom={1.049} />
        </Freeze>
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 596,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <CaptionWords
          words={COPY.caption.next}
          keyWords={COPY.caption.nextKey}
          start={10}
          underlineFrom={34}
          zoom={1.049}
        />
      </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
