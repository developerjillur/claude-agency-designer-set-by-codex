import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

type Icon = {
  kind: "chat" | "heart" | "bell";
  background: string;
  to: { x: number; y: number };
  delay: number;
};

const ICONS: Icon[] = [
  {
    kind: "chat",
    background: "linear-gradient(140deg, #7C6CFF 0%, #5B4BE0 100%)",
    to: { x: 1150, y: 230 },
    delay: 14,
  },
  {
    kind: "heart",
    background: "linear-gradient(140deg, #FF5C8A 0%, #FF7A59 100%)",
    to: { x: 1330, y: 400 },
    delay: 20,
  },
  {
    kind: "bell",
    background: "linear-gradient(140deg, #FFC43D 0%, #FF8A2F 100%)",
    to: { x: 1140, y: 570 },
    delay: 26,
  },
];

const TILE = 124;

const Glyph: React.FC<{ kind: Icon["kind"] }> = ({ kind }) => {
  if (kind === "chat") {
    return (
      <svg width={64} height={64} viewBox="0 0 24 24">
        <path
          d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 4v-4H6.5A2.5 2.5 0 0 1 4 13.5z"
          fill="#FFFFFF"
        />
        <circle cx={8.6} cy={9.6} r={1.3} fill="#5B4BE0" />
        <circle cx={12} cy={9.6} r={1.3} fill="#5B4BE0" />
        <circle cx={15.4} cy={9.6} r={1.3} fill="#5B4BE0" />
      </svg>
    );
  }
  if (kind === "heart") {
    return (
      <svg width={64} height={64} viewBox="0 0 24 24">
        <path
          d="M12 20.5s-7.5-4.6-9.6-9C.9 8 3 4.5 6.6 4.5c2.1 0 3.6 1.1 5.4 3.2 1.8-2.1 3.3-3.2 5.4-3.2 3.6 0 5.7 3.5 4.2 7-2.1 4.4-9.6 9-9.6 9z"
          fill="#FFFFFF"
        />
      </svg>
    );
  }
  return (
    <svg width={64} height={64} viewBox="0 0 24 24">
      <path
        d="M12 3a6 6 0 0 0-6 6v3.6L4.2 16h15.6L18 12.6V9a6 6 0 0 0-6-6zm-2.4 14.5a2.4 2.4 0 0 0 4.8 0z"
        fill="#FFFFFF"
      />
    </svg>
  );
};

// Engagement icons fly out of the camera lens and keep floating.
export const AppIcons: React.FC<{
  origin: { x: number; y: number };
  startAt?: number;
  targets?: { x: number; y: number }[];
}> = ({ origin, startAt = 14, targets }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {ICONS.map((icon, i) => {
        const delay = startAt + i * 6;
        const to = targets?.[i] ?? icon.to;
        const fly = spring({
          frame: frame - delay,
          fps,
          config: { damping: 12, stiffness: 150 },
        });
        if (frame < delay) {
          return null;
        }
        const float = 7 * Math.sin((frame - delay) / 9 + i * 1.7);
        const x = origin.x + (to.x - origin.x) * fly;
        const y = origin.y + (to.y - origin.y) * fly + float * fly;
        return (
          <div
            key={icon.kind}
            style={{
              position: "absolute",
              left: x - TILE / 2,
              top: y - TILE / 2,
              width: TILE,
              height: TILE,
              borderRadius: 34,
              background: icon.background,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow:
                "0 16px 34px rgba(90, 30, 0, 0.28), inset 0 2px 0 rgba(255, 255, 255, 0.35)",
              scale: `${0.25 + 0.75 * fly}`,
              rotate: `${(1 - fly) * -25}deg`,
              opacity: Math.min(1, fly * 2),
            }}
          >
            <Glyph kind={icon.kind} />
          </div>
        );
      })}
    </>
  );
};
