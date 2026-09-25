import React, { useId } from "react";
import { random, useCurrentFrame } from "remotion";
import { INK, POPPINS } from "../theme";
import { Chain, OUTLINE as O, Pt, add, fromDown, lerp, mul, rad } from "./draw";
import { COPY } from "../copy";

const T = 18; // frames per stride cycle
const GROUND = 16; // track speed in px per frame
const TAU = Math.PI * 2;
const L_TH = 112;
const L_SH = 112;
const L_UA = 78;
const L_FA = 74;
const LEAN = 12;
const HAIR = "#3B2418";

type Look = { skin: string; tee: string; shorts: string; shoe: string };
const NEAR: Look = {
  skin: "#F6C9A4",
  tee: "#7B5CFF",
  shorts: "#2B2D42",
  shoe: "#E5484D",
};
const FAR: Look = {
  skin: "#DDA57F",
  tee: "#5F45D8",
  shorts: "#1C1D2E",
  shoe: "#BF3A3F",
};

const wrap = (x: number, span: number) => ((x % span) + span) % span;

// Procedural run cycle: the thigh swings on a sine, the knee folds most as the thigh passes
// vertical on the way forward (heel kick), and the foot stays flat while it carries the weight.
const legPose = (hip: Pt, p: number) => {
  const thigh = 7.5 + 37.5 * Math.sin(p);
  const flex = 25 + 95 * Math.pow(Math.max(0, Math.cos(p + Math.PI / 12)), 1.2);
  const knee = add(hip, mul(fromDown(thigh), L_TH));
  const shin = thigh - flex;
  const ankle = add(knee, mul(fromDown(shin), L_SH));
  const stance = Math.min(
    1,
    Math.max(0, (Math.cos(p - rad(190)) - 0.7) / 0.25),
  );
  // In the air the toes point along the shin (more as the knee folds), so the kicked-up foot
  // never stands vertical behind the planted leg.
  const pointed = 0.6 * (flex - 25) + Math.max(0, -thigh) * 0.9;
  const swingFoot = -shin + pointed;
  return { knee, ankle, footAngle: swingFoot * (1 - stance) };
};

// Arms swing against the leg on the same side.
const armPose = (shoulder: Pt, p: number) => {
  const upper = -38 * Math.sin(p);
  const bend = 88 + 12 * Math.sin(p);
  const elbow = add(shoulder, mul(fromDown(upper), L_UA));
  const wrist = add(elbow, mul(fromDown(upper + bend), L_FA));
  return { elbow, wrist };
};

const Leg: React.FC<{ hip: Pt; p: number; look: Look }> = ({
  hip,
  p,
  look,
}) => {
  const { knee, ankle, footAngle } = legPose(hip, p);
  const sock = lerp(ankle, knee, 0.18);
  return (
    <g>
      <Chain pts={[hip, knee, ankle]} w={30} color={look.skin} />
      <Chain pts={[sock, ankle]} w={33} color="#FFFFFF" outline={4} />
      <Chain pts={[hip, lerp(hip, knee, 0.45)]} w={46} color={look.shorts} />
      <g transform={`translate(${ankle.x} ${ankle.y}) rotate(${footAngle})`}>
        <path
          d="M-16,-6 C-18,8 -12,16 0,16 L50,16 C60,16 62,6 54,-1 C46,-8 30,-11 16,-11 L0,-12 C-9,-12 -14,-11 -16,-6 Z"
          fill={look.shoe}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
        <rect
          x={-17}
          y={11}
          width={76}
          height={9}
          rx={4.5}
          fill="#FFFFFF"
          stroke={INK}
          strokeWidth={3}
        />
      </g>
    </g>
  );
};

const Arm: React.FC<{ shoulder: Pt; p: number; look: Look }> = ({
  shoulder,
  p,
  look,
}) => {
  const { elbow, wrist } = armPose(shoulder, p);
  return (
    <g>
      <Chain pts={[shoulder, elbow, wrist]} w={26} color={look.skin} />
      <Chain
        pts={[shoulder, lerp(shoulder, elbow, 0.45)]}
        w={40}
        color={look.tee}
      />
      <circle
        cx={wrist.x}
        cy={wrist.y}
        r={15}
        fill={look.skin}
        stroke={INK}
        strokeWidth={O}
      />
    </g>
  );
};

const Head: React.FC<{ c: Pt; p: number }> = ({ c, p }) => {
  const bounce = 5 * Math.sin(2 * p - 0.9);
  const mouth = 5 + 3 * Math.abs(Math.sin(p));
  const at = (deg: number, r: number): Pt => ({
    x: c.x + r * Math.cos(rad(deg)),
    y: c.y + r * Math.sin(rad(deg)),
  });
  const capA = at(-172, 69);
  const capB = at(-12, 69);
  const bandA = at(-155, 62);
  const bandB = at(-30, 62);
  const band = `M${bandA.x},${bandA.y} Q${c.x},${c.y - 26} ${bandB.x},${bandB.y}`;
  return (
    <g>
      <path
        d={`M${c.x - 20},${c.y - 40} C${c.x - 70},${c.y - 40} ${c.x - 88},${c.y + 10} ${c.x - 70},${c.y + 44 + bounce} C${c.x - 58},${c.y + 62 + bounce} ${c.x - 34},${c.y + 60 + bounce} ${c.x - 20},${c.y + 44} Z`}
        fill={HAIR}
        stroke={INK}
        strokeWidth={O}
        strokeLinejoin="round"
      />
      <circle
        cx={c.x}
        cy={c.y}
        r={64}
        fill={NEAR.skin}
        stroke={INK}
        strokeWidth={O}
      />
      <path
        d={`M${c.x + 56},${c.y - 6} C${c.x + 72},${c.y + 2} ${c.x + 72},${c.y + 16} ${c.x + 57},${c.y + 18}`}
        fill={NEAR.skin}
        stroke={INK}
        strokeWidth={4}
        strokeLinecap="round"
      />
      <path
        d={`M${capA.x},${capA.y} A69,69 0 0 1 ${capB.x},${capB.y} Q${c.x + 10},${c.y - 34} ${capA.x},${capA.y} Z`}
        fill={HAIR}
        stroke={INK}
        strokeWidth={O}
        strokeLinejoin="round"
      />
      <path
        d={band}
        fill="none"
        stroke={INK}
        strokeWidth={24}
        strokeLinecap="round"
      />
      <path
        d={band}
        fill="none"
        stroke="#FFC43D"
        strokeWidth={15}
        strokeLinecap="round"
      />
      <ellipse
        cx={c.x - 8}
        cy={c.y + 8}
        rx={11}
        ry={15}
        fill={NEAR.skin}
        stroke={INK}
        strokeWidth={4}
      />
      <ellipse cx={c.x + 32} cy={c.y - 1} rx={7} ry={10} fill={INK} />
      <circle cx={c.x + 34} cy={c.y - 5} r={2.6} fill="#FFFFFF" />
      <path
        d={`M${c.x + 22},${c.y - 14} L${c.x + 44},${c.y - 18}`}
        stroke={HAIR}
        strokeWidth={6}
        strokeLinecap="round"
      />
      <circle
        cx={c.x + 24}
        cy={c.y + 22}
        r={10}
        fill="#FF8A7A"
        opacity={0.45}
      />
      <path
        d={`M${c.x + 34},${c.y + 27} L${c.x + 56},${c.y + 24} Q${c.x + 50},${c.y + 27 + mouth * 2.2} ${c.x + 34},${c.y + 27} Z`}
        fill="#7A2E2A"
        stroke={INK}
        strokeWidth={3.5}
        strokeLinejoin="round"
      />
    </g>
  );
};

const Scenery: React.FC<{ frame: number; w: number; uid: string }> = ({
  frame,
  w,
  uid,
}) => {
  const hillCopies = Math.ceil(w / 960) + 1;
  const treeSpan = w + 290;
  const fenceSpan = w + 120;
  const speckSpan = w + 440;
  return (
    <g>
      <defs>
        <linearGradient id={`${uid}-sky`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#A9DDF3" />
          <stop offset="1" stopColor="#FFF1DC" />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={w} height={810} fill={`url(#${uid}-sky)`} />
      <circle cx={w - 190} cy={170} r={98} fill="#FFE9A8" opacity={0.55} />
      <circle cx={w - 190} cy={170} r={62} fill="#FFD166" />
      {[0, 1].map((i) => {
        const x = wrap(180 + i * 560 - frame * 0.8, w + 300) - 150;
        return (
          <g key={`c${i}`} transform={`translate(${x} ${120 + i * 96})`}>
            <ellipse cx={0} cy={0} rx={70} ry={26} fill="#FFFFFF" />
            <ellipse cx={30} cy={-16} rx={40} ry={26} fill="#FFFFFF" />
          </g>
        );
      })}
      {new Array(hillCopies).fill(0).map((_, k) => (
        <path
          key={`h${k}`}
          transform={`translate(${-wrap(frame * 1.5, 960) + k * 960} 0)`}
          d="M0,640 C120,560 260,560 380,620 C500,680 620,560 760,580 C860,594 920,620 960,640 L960,810 L0,810 Z"
          fill="#CFE8C4"
        />
      ))}
      {new Array(hillCopies).fill(0).map((_, k) => (
        <path
          key={`n${k}`}
          transform={`translate(${-wrap(frame * 3, 960) + k * 960} 0)`}
          d="M0,700 C160,640 300,650 460,700 C600,742 760,660 960,700 L960,810 L0,810 Z"
          fill="#B5DDA6"
        />
      ))}
      {new Array(Math.round(treeSpan / 250)).fill(0).map((_, i) => {
        const x = wrap(i * 250 - frame * 7, treeSpan) - 145;
        return (
          <g key={`t${i}`}>
            <rect x={x - 8} y={700} width={16} height={74} fill="#8A5A3C" stroke={INK} strokeWidth={3} />
            <circle cx={x} cy={680} r={46} fill="#6DBB6F" stroke={INK} strokeWidth={4} />
            <circle cx={x - 15} cy={665} r={14} fill="#8FD48E" />
          </g>
        );
      })}
      <line x1={0} y1={754} x2={w} y2={754} stroke={INK} strokeWidth={10} />
      <line x1={0} y1={754} x2={w} y2={754} stroke="#FFFFFF" strokeWidth={5} />
      {new Array(Math.round(fenceSpan / 90)).fill(0).map((_, i) => {
        const x = wrap(i * 90 - frame * 11, fenceSpan) - 60;
        return (
          <rect key={`f${i}`} x={x} y={742} width={11} height={36} rx={3} fill="#FFFFFF" stroke={INK} strokeWidth={3} />
        );
      })}
      <rect x={0} y={772} width={w} height={36} fill="#8CCB7A" />
      <rect x={0} y={806} width={w} height={274} fill="#E0784E" />
      <line x1={0} y1={808} x2={w} y2={808} stroke="#C9623B" strokeWidth={6} />
      <line x1={0} y1={896} x2={w} y2={896} stroke="#FFF6EA" strokeWidth={7} />
      <line x1={0} y1={1016} x2={w} y2={1016} stroke="#FFF6EA" strokeWidth={7} />
      {new Array(Math.round(speckSpan / 140)).fill(0).map((_, i) => {
        const x = wrap(i * 140 - frame * GROUND, speckSpan) - 100;
        return (
          <rect key={`s${i}`} x={x} y={930 + (i % 3) * 24} width={40} height={6} rx={3} fill="#EE9A74" />
        );
      })}
    </g>
  );
};

// A puff of dust each time a foot lands (every half stride).
const Dust: React.FC<{ frame: number; x0: number }> = ({ frame, x0 }) => {
  const puffs: React.ReactNode[] = [];
  for (let k = Math.floor((frame - 12) / 9); k <= Math.floor(frame / 9); k++) {
    const start = k * 9;
    const age = frame - start;
    if (start < 0 || age < 0 || age > 12) {
      continue;
    }
    const x = x0 - age * GROUND * 0.55;
    const r = 7 + age * 1.7;
    puffs.push(
      <g key={k} opacity={0.55 * (1 - age / 12)}>
        <circle cx={x - 12} cy={880} r={r} fill="#F7C3A5" />
        <circle cx={x - 30} cy={872} r={r * 0.8} fill="#F7C3A5" />
        <circle cx={x + 6} cy={874} r={r * 0.7} fill="#F7C3A5" />
      </g>,
    );
  }
  return <g>{puffs}</g>;
};

const SpeedLines: React.FC<{ frame: number; y: number; x: number }> = ({
  frame,
  y,
  x,
}) => (
  <g stroke="#FFFFFF" strokeLinecap="round">
    {[
      { dy: -170, len: 120 },
      { dy: -100, len: 80 },
      { dy: -30, len: 140 },
    ].map((l, i) => {
      const shift = ((frame + i * 2) % 6) * 6;
      return (
        <line key={l.dy} x1={x - l.len - shift} y1={y + l.dy} x2={x - shift} y2={y + l.dy} strokeWidth={8} opacity={0.75} />
      );
    })}
  </g>
);

// The finish tape meets the chest this far in front of the hip.
const TAPE_REACH = 25;
const CONFETTI = ["#FF7A2F", "#FFC43D", "#7B5CFF", "#1F9D8A", "#FF5C8A"];

// Finish gate that rolls in with the track: checkered line, two posts, a FINISH board and a tape
// that snaps at `finishAt` and swings back on both posts. Drawn in two layers around the runner.
const FinishGate: React.FC<{
  frame: number;
  finishAt: number;
  runnerX: number;
  layer: "back" | "front";
  uid: string;
}> = ({ frame, finishAt, runnerX, layer, uid }) => {
  const x = runnerX + TAPE_REACH + (finishAt - frame) * GROUND;
  if (x < -400 || x > 3200) {
    return null;
  }
  const t = frame - finishAt;
  const near: Pt = { x: x - 50, y: 640 };
  const far: Pt = { x: x + 100, y: 500 };
  const swing = (rest: number, from: number) =>
    rest + (from - rest) * Math.exp(-t / 7) * Math.cos(t * 0.55);
  const half = (pivot: Pt, deg: number) =>
    `M${pivot.x},${pivot.y} L${pivot.x + 102 * Math.cos(rad(deg))},${pivot.y + 102 * Math.sin(rad(deg))}`;
  const tape = (d: string) => (
    <g fill="none" strokeLinecap="round">
      <path d={d} stroke={INK} strokeWidth={14} />
      <path d={d} stroke="#E5484D" strokeWidth={9} />
      <path d={d} stroke="#FFFFFF" strokeWidth={3} strokeDasharray="8 10" />
    </g>
  );
  if (layer === "back") {
    return (
      <g>
        <defs>
          <pattern id={`${uid}-chk`} width={20} height={20} patternUnits="userSpaceOnUse">
            <rect width={20} height={20} fill="#FFFFFF" />
            <rect width={10} height={10} fill="#1E1B2E" />
            <rect x={10} y={10} width={10} height={10} fill="#1E1B2E" />
          </pattern>
        </defs>
        <path
          d={`M${near.x - 15},896 L${near.x + 15},896 L${far.x + 15},808 L${far.x - 15},808 Z`}
          fill={`url(#${uid}-chk)`}
          opacity={0.9}
        />
        <rect x={far.x - 6} y={220} width={12} height={800 - 220} fill="#E4E4EA" stroke={INK} strokeWidth={4} />
        <g transform={`translate(${far.x} 262)`}>
          <rect x={-150} y={-48} width={300} height={96} rx={14} fill="#1E1B2E" stroke={INK} strokeWidth={4} />
          <text
            x={0}
            y={19}
            textAnchor="middle"
            fontFamily={POPPINS}
            fontWeight={800}
            fontSize={54}
            letterSpacing={6}
            fill="#FFFFFF"
          >
            {COPY.finish}
          </text>
        </g>
        {t < 0
          ? tape(`M${near.x},${near.y} L${far.x},${far.y}`)
          : tape(half(far, swing(90, 137)))}
      </g>
    );
  }
  return (
    <g>
      <rect x={near.x - 7} y={near.y - 12} width={14} height={905 - near.y + 12} fill="#EDEDF2" stroke={INK} strokeWidth={4} />
      {t >= 0 ? tape(half(near, swing(95, -43))) : null}
    </g>
  );
};

const Burst: React.FC<{ t: number; at: Pt }> = ({ t, at }) => {
  if (t < 0 || t > 10) {
    return null;
  }
  const k = t / 10;
  return (
    <g stroke="#FFC43D" strokeWidth={7} strokeLinecap="round" opacity={1 - k}>
      {new Array(8).fill(0).map((_, i) => {
        const a = (i / 8) * TAU;
        const r1 = 34 + 44 * k;
        const r2 = r1 + 28;
        return (
          <line
            key={i}
            x1={at.x + r1 * Math.cos(a)}
            y1={at.y + r1 * Math.sin(a)}
            x2={at.x + r2 * Math.cos(a)}
            y2={at.y + r2 * Math.sin(a)}
          />
        );
      })}
    </g>
  );
};

const Confetti: React.FC<{ frame: number; start: number; width: number }> = ({
  frame,
  start,
  width,
}) => {
  const t = frame - start;
  if (t < 0) {
    return null;
  }
  return (
    <g>
      {new Array(Math.round(width / 20)).fill(0).map((_, i) => {
        const tt = t - random(`cf-d-${i}`) * 10;
        if (tt < 0) {
          return null;
        }
        const x = random(`cf-x-${i}`) * width + Math.sin(tt / 6 + i) * 24;
        const y = -30 + tt * (7 + random(`cf-v-${i}`) * 5);
        const rot = tt * (8 + random(`cf-r-${i}`) * 10);
        return (
          <rect
            key={i}
            x={-8}
            y={-5}
            width={16}
            height={10}
            rx={2}
            fill={CONFETTI[i % CONFETTI.length]}
            transform={`translate(${x} ${y}) rotate(${rot})`}
          />
        );
      })}
    </g>
  );
};

// A young runner on race day, rigged and animated in code. Defaults draw the 960px split-screen
// panel; `width`, `runnerX` and `finishAt` make the full-width finish-line shot.
export const RunnerTrack: React.FC<{
  width?: number;
  runnerX?: number;
  finishAt?: number;
}> = ({ width = 960, runnerX = 462, finishAt }) => {
  const frame = useCurrentFrame();
  const uid = `rt${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const p = (frame / T) * TAU;
  const bob = 9 * Math.pow(Math.cos(p), 2);
  const hip: Pt = { x: runnerX, y: 632 + bob };
  const up = fromDown(180 - LEAN);
  const chest = add(hip, mul(up, 150));
  const head = add(chest, { x: 30, y: -104 });
  const armRoot = add(chest, mul(up, -12));
  const bib = lerp(hip, chest, 0.5);
  const hasFinish = finishAt !== undefined;
  return (
    <svg
      width={width}
      height={1080}
      viewBox={`0 0 ${width} 1080`}
      style={{ position: "absolute", left: 0, top: 0 }}
    >
      <Scenery frame={frame} w={width} uid={uid} />
      {hasFinish ? (
        <FinishGate frame={frame} finishAt={finishAt} runnerX={runnerX} layer="back" uid={uid} />
      ) : null}
      <Dust frame={frame} x0={runnerX - 12} />
      <SpeedLines frame={frame} y={hip.y} x={runnerX - 132} />
      <Arm shoulder={armRoot} p={p + Math.PI} look={FAR} />
      <Leg hip={hip} p={p + Math.PI} look={FAR} />
      <g transform={`rotate(${LEAN} ${hip.x} ${hip.y})`}>
        <rect
          x={hip.x - 50}
          y={hip.y - 22}
          width={100}
          height={62}
          rx={20}
          fill={NEAR.shorts}
          stroke={INK}
          strokeWidth={O}
        />
      </g>
      <Leg hip={hip} p={p} look={NEAR} />
      <Chain pts={[chest, add(head, { x: -16, y: 44 })]} w={30} color={NEAR.skin} />
      <Chain pts={[add(hip, mul(up, 22)), chest]} w={100} color={NEAR.tee} />
      <g transform={`translate(${bib.x + 4} ${bib.y}) rotate(${LEAN})`}>
        <rect x={-36} y={-30} width={72} height={58} rx={7} fill="#FFFFFF" stroke={INK} strokeWidth={4} />
        <text x={0} y={15} textAnchor="middle" fontFamily={POPPINS} fontWeight={800} fontSize={38} fill={INK}>
          27
        </text>
        {[
          [-28, -22],
          [28, -22],
          [-28, 20],
          [28, 20],
        ].map(([x, y]) => (
          <circle key={`${x}:${y}`} cx={x} cy={y} r={3} fill="#9AA0A6" />
        ))}
      </g>
      <Head c={head} p={p} />
      <Arm shoulder={armRoot} p={p} look={NEAR} />
      {hasFinish ? (
        <>
          <FinishGate frame={frame} finishAt={finishAt} runnerX={runnerX} layer="front" uid={uid} />
          <Burst t={frame - finishAt} at={{ x: runnerX + 70, y: 590 }} />
          <Confetti frame={frame} start={finishAt - 2} width={width} />
        </>
      ) : null}
    </svg>
  );
};
