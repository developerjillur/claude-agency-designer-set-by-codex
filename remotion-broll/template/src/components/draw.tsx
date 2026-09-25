import React from "react";
import { INK } from "../theme";

export type Pt = { x: number; y: number };

export const OUTLINE = 5;

export const add = (a: Pt, b: Pt): Pt => ({ x: a.x + b.x, y: a.y + b.y });
export const mul = (a: Pt, k: number): Pt => ({ x: a.x * k, y: a.y * k });
export const lerp = (a: Pt, b: Pt, t: number): Pt => ({
  x: a.x + (b.x - a.x) * t,
  y: a.y + (b.y - a.y) * t,
});
export const rad = (deg: number) => (deg * Math.PI) / 180;

// Unit vector for an angle measured from straight down; positive angles swing toward screen-right.
export const fromDown = (deg: number): Pt => ({
  x: Math.sin(rad(deg)),
  y: Math.cos(rad(deg)),
});

export const pathOf = (pts: Pt[]) =>
  pts
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`)
    .join(" ");

// A limb or any thick stroke: outline pass first, fill pass second, so joints stay seamless.
export const Chain: React.FC<{
  pts: Pt[];
  w: number;
  color: string;
  outline?: number;
}> = ({ pts, w, color, outline = OUTLINE }) => {
  const d = pathOf(pts);
  return (
    <>
      <path
        d={d}
        fill="none"
        stroke={INK}
        strokeWidth={w + outline * 2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={w}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </>
  );
};
