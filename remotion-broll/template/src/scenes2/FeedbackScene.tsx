import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { AUDIO_Y, Clip, ROW_H, Ruler, TrackIcon, VIDEO_Y } from "../scenes/TimelineScene";
import { clamp } from "../theme";

export const TRIM_AT = 70;
const CLOSE_AT = 84;
const NEW_CLIP_AT = 102;
const CUT_X = 882;
const REACTIONS = [22, 34, 46, 110, 122, 134];

const HEART =
  "M12 20.5s-7.5-4.6-9.6-9C.9 8 3 4.5 6.6 4.5c2.1 0 3.6 1.1 5.4 3.2 1.8-2.1 3.3-3.2 5.4-3.2 3.6 0 5.7 3.5 4.2 7-2.1 4.4-9.6 9-9.6 9z";
const CHAT =
  "M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 4v-4H6.5A2.5 2.5 0 0 1 4 13.5z";
const SCISSORS =
  "M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64zM6 8c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2zm0 12c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zM19 3l-6 6 2 2 7-7V3z";

// Reactions rise above the video track wherever the playhead is.
const Reactions: React.FC<{ frame: number; playheadAt: (f: number) => number }> = ({
  frame,
  playheadAt,
}) => (
  <>
    {REACTIONS.map((at, i) => {
      const age = frame - at;
      if (age < 0 || age > 26) {
        return null;
      }
      const t = age / 26;
      const heart = i % 2 === 0;
      return (
        <div
          key={at}
          style={{
            position: "absolute",
            left: playheadAt(at) - 38 + Math.sin(age / 4 + i) * 10,
            top: VIDEO_Y - 40 - t * 150,
            width: 76,
            height: 76,
            borderRadius: 38,
            background: heart
              ? "linear-gradient(140deg, #FF5C8A, #FF7A59)"
              : "linear-gradient(140deg, #7C6CFF, #5B4BE0)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: interpolate(age, [0, 4, 18, 26], [0, 1, 1, 0], clamp),
            scale: `${interpolate(age, [0, 6], [0.4, 1], clamp)}`,
            boxShadow: "0 10px 24px rgba(76, 29, 149, 0.25)",
          }}
        >
          <svg width={40} height={40} viewBox="0 0 24 24">
            <path d={heart ? HEART : CHAT} fill="#FFFFFF" />
          </svg>
        </div>
      );
    })}
  </>
);

// Step 3 B-roll: the edit gets tighter after feedback. A marked section is cut, the gap closes,
// a new clip lands, and reactions keep coming.
export const FeedbackScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const playheadAt = (f: number) => interpolate(f, [10, 150], [300, 1440], clamp);
  const playhead = playheadAt(frame);
  const trim = interpolate(frame, [TRIM_AT, TRIM_AT + 12], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const close = interpolate(frame, [CLOSE_AT, CLOSE_AT + 14], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const bW = 440 - 180 * trim;
  const cX = 1084 - 180 * close;
  const scissors = spring({ frame: frame - 50, fps, config: { damping: 12, stiffness: 180 } });
  const scissorsOut = interpolate(frame, [TRIM_AT + 14, TRIM_AT + 24], [1, 0], clamp);
  const snip = interpolate(frame, [TRIM_AT - 4, TRIM_AT, TRIM_AT + 4], [-18, 8, 0], clamp);
  const isActive = (x: number, w: number) => playhead >= x && playhead <= x + w;
  const headIn = spring({ frame: frame - 4, fps, config: { damping: 200 } });
  return (
    <AbsoluteFill
      style={{ background: "linear-gradient(135deg, #FCE4F1 0%, #EBD8FF 48%, #C3A2FF 100%)" }}
    >
      <Ruler />
      <TrackIcon kind="video" y={VIDEO_Y} delay={0} />
      <TrackIcon kind="audio" y={AUDIO_Y} delay={3} />
      <Clip x={300} w={300} y={VIDEO_Y} delay={2} kind="video" index={0} active={isActive(300, 300)} />
      <Clip x={622} w={bW} y={VIDEO_Y} delay={6} kind="video" index={1} active={isActive(622, bW)} />
      <Clip x={cX} w={260} y={VIDEO_Y} delay={10} kind="video" index={2} active={isActive(cX, 260)} />
      {frame >= NEW_CLIP_AT ? (
        <Clip x={1186} w={210} y={VIDEO_Y} delay={NEW_CLIP_AT} kind="video" index={3} active={isActive(1186, 210)} />
      ) : null}
      <Clip x={300} w={1096} y={AUDIO_Y} delay={5} kind="audio" index={0} active={isActive(300, 1096)} />
      <div
        style={{
          position: "absolute",
          left: CUT_X,
          top: VIDEO_Y,
          width: 180 * (1 - trim),
          height: ROW_H,
          borderRadius: 26,
          backgroundColor: "rgba(255, 70, 90, 0.35)",
          border: "4px dashed #FF4D6D",
          opacity: interpolate(frame, [52, 58], [0, 1], clamp) * (1 - trim),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: CUT_X - 42,
          top: VIDEO_Y - 104,
          width: 84,
          height: 84,
          borderRadius: 42,
          backgroundColor: "#FFFFFF",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 12px 26px rgba(76, 29, 149, 0.28)",
          scale: `${scissors * scissorsOut}`,
          rotate: `${snip}deg`,
        }}
      >
        <svg width={50} height={50} viewBox="0 0 24 24">
          <path d={SCISSORS} fill="#FF4D6D" />
        </svg>
      </div>
      <Reactions frame={frame} playheadAt={playheadAt} />
      <div
        style={{
          position: "absolute",
          left: playhead - 3,
          top: 236,
          width: 6,
          height: 470,
          borderRadius: 3,
          backgroundColor: "#4C1D95",
          opacity: headIn,
          boxShadow: "0 0 18px rgba(76, 29, 149, 0.45)",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: -15,
            top: -30,
            width: 36,
            height: 36,
            borderRadius: 18,
            backgroundColor: "#4C1D95",
            border: "5px solid #FFFFFF",
            boxSizing: "border-box",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
