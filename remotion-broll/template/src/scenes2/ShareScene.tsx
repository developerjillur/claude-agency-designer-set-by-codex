import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { AppIcons } from "../components/AppIcons";
import { GuitarRoom } from "../components/Guitarist";
import { MiniScene } from "../components/MiniScene";
import { Bokeh } from "../scenes/CreatorScene";
import { POPPINS, clamp } from "../theme";
import { COPY } from "../copy";

const UPLOAD_FROM = 16;
export const UPLOAD_DONE = 70;

// Step 2 B-roll: the same creator cutout (mirrored) next to a post that uploads, then reactions fly out.
export const ShareScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cardIn = spring({ frame: frame - 2, fps, config: { damping: 15, stiffness: 130 } });
  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, stiffness: 150 } });
  const progress = interpolate(frame, [UPLOAD_FROM, UPLOAD_DONE], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const posted = frame >= UPLOAD_DONE;
  const check = spring({ frame: frame - UPLOAD_DONE, fps, config: { damping: 10, stiffness: 200 } });
  const breathe = 1 + 0.009 * Math.sin(((frame / fps) * 2 * Math.PI) / 1.7);
  const push = interpolate(frame, [0, durationInFrames], [1, 1.05]);
  const size = 0.9 + 0.1 * enter;
  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(circle at 62% 46%, #FFF3E2 0%, #FFD4A8 42%, #FF9D5C 100%)",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill style={{ scale: `${push}`, transformOrigin: "60% 55%" }}>
        <Bokeh />
        <div
          style={{
            position: "absolute",
            left: 1170,
            top: 996,
            width: 320,
            height: 50,
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
            left: 800,
            top: 170,
            width: 880,
            height: 880,
            transformOrigin: "50% 96%",
            scale: `${-size} ${size * breathe}`,
            translate: `0px ${(1 - enter) * 140}px`,
            opacity: Math.min(1, enter * 2),
          }}
        />
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 170,
          top: 190,
          width: 640,
          padding: 26,
          borderRadius: 32,
          backgroundColor: "#FFFFFF",
          boxShadow: "0 30px 70px rgba(120, 50, 10, 0.25)",
          translate: `0px ${(1 - cardIn) * 760}px`,
          rotate: `${(1 - cardIn) * 6 - 1.5}deg`,
          fontFamily: POPPINS,
        }}
      >
        <div style={{ borderRadius: 20, overflow: "hidden" }}>
          <MiniScene width={588} height={331} scale={0.6125} offsetY={-150}>
            <GuitarRoom />
          </MiniScene>
        </div>
        <div style={{ marginTop: 24, height: 22, width: 420, borderRadius: 11, backgroundColor: "#EFE8DE" }} />
        <div style={{ marginTop: 14, height: 22, width: 300, borderRadius: 11, backgroundColor: "#F4EEE6" }} />
        <div style={{ marginTop: 30, display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ flex: 1, height: 18, borderRadius: 9, backgroundColor: "#F1EBE3", overflow: "hidden" }}>
            <div
              style={{
                width: `${progress * 100}%`,
                height: "100%",
                borderRadius: 9,
                background: "linear-gradient(90deg, #FF9D5C, #FF6A1F)",
              }}
            />
          </div>
          <div
            style={{
              width: 190,
              display: "flex",
              alignItems: "center",
              gap: 10,
              fontWeight: 700,
              fontSize: 32,
              color: posted ? "#1F9D63" : "#8E879A",
            }}
          >
            {posted ? (
              <>
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 19,
                    backgroundColor: "#1F9D63",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    scale: `${check}`,
                  }}
                >
                  <svg width={24} height={24} viewBox="0 0 24 24">
                    <path
                      d="M5 12.5l4.2 4.2L19 7"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth={3.4}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                {COPY.share.posted}
              </>
            ) : (
              COPY.share.uploading
            )}
          </div>
        </div>
      </div>
      <AppIcons
        origin={{ x: 790, y: 260 }}
        startAt={UPLOAD_DONE + 6}
        targets={[
          { x: 1570, y: 250 },
          { x: 1735, y: 410 },
          { x: 1570, y: 570 },
        ]}
      />
    </AbsoluteFill>
  );
};
