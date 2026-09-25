import React, { useId } from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { INK, clamp } from "../theme";
import { Chain, OUTLINE as O, Pt, add, lerp, mul, rad } from "./draw";

const SKIN = "#B97A52";
const HAIR = "#221718";
const TEE = "#FFFDF8";
const TEE_SHADE = "#F0E2D0";
const PANTS = "#EE8A7B";
const WOOD_DARK = "#A95F2A";
const NOTE_COLORS = ["#FF7A2F", "#1F5C63", "#6D3AF0"];
const TAU = Math.PI * 2;

// The guitar is placed by its lower-bout centre and tilted so the neck rises to the right.
const G = { x: 405, y: 640, angle: -22, scale: 0.9 };
const COS = Math.cos(rad(G.angle));
const SIN = Math.sin(rad(G.angle));
const onGuitar = (lx: number, ly: number): Pt => ({
  x: G.x + G.scale * (lx * COS - ly * SIN),
  y: G.y + G.scale * (lx * SIN + ly * COS),
});
const NECK_DIR: Pt = { x: COS, y: SIN };
const NECK_NORMAL: Pt = { x: -SIN, y: COS };

// Fast downstroke, slower upstroke, two strums a second.
const strumAngle = (frame: number) => {
  const s = (frame % 15) / 15;
  return s < 0.35
    ? interpolate(s, [0, 0.35], [-11, 12], { easing: Easing.out(Easing.quad) })
    : interpolate(s, [0.35, 1], [12, -11], {
        easing: Easing.inOut(Easing.sin),
      });
};

// Strings ring for a few frames after the pick crosses them.
const stringRing = (frame: number) => {
  const decay = (age: number) => Math.max(0, 1 - age / 9);
  return Math.max(
    decay((((frame - 3) % 15) + 15) % 15),
    decay((((frame - 10) % 15) + 15) % 15),
  );
};

const Room: React.FC<{ frame: number; uid: string }> = ({ frame, uid }) => {
  const sway = 2.5 * Math.sin(frame / 14);
  return (
    <g>
      <defs>
        <radialGradient id={`${uid}-wall`} cx="0.7" cy="0.2" r="0.95">
          <stop offset="0" stopColor="#FFF7EA" />
          <stop offset="1" stopColor="#FAD9BA" />
        </radialGradient>
        <linearGradient id={`${uid}-glass`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#BFE6FF" />
          <stop offset="1" stopColor="#EEF9FF" />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={960} height={1080} fill={`url(#${uid}-wall)`} />
      <path
        d="M612,430 L838,430 L720,880 L400,880 Z"
        fill="#FFFFFF"
        opacity={0.2}
      />
      <rect
        x={600}
        y={130}
        width={250}
        height={300}
        rx={18}
        fill={`url(#${uid}-glass)`}
        stroke={INK}
        strokeWidth={O}
      />
      <ellipse cx={668} cy={206} rx={40} ry={15} fill="#FFFFFF" />
      <ellipse cx={696} cy={196} rx={24} ry={14} fill="#FFFFFF" />
      <line x1={725} y1={130} x2={725} y2={430} stroke={INK} strokeWidth={O} />
      <line x1={600} y1={280} x2={850} y2={280} stroke={INK} strokeWidth={O} />
      <rect
        x={586}
        y={426}
        width={278}
        height={18}
        rx={6}
        fill="#FFFFFF"
        stroke={INK}
        strokeWidth={O}
      />
      <rect
        x={110}
        y={180}
        width={190}
        height={150}
        rx={10}
        fill="#FFE7C2"
        stroke={INK}
        strokeWidth={O}
      />
      <circle cx={246} cy={228} r={24} fill="#FF9F4A" />
      <path d="M117,323 L172,258 L214,300 L250,268 L293,323 Z" fill="#F07A5A" />
      <rect x={0} y={880} width={960} height={200} fill="#F2CBA2" />
      <line
        x1={0}
        y1={880}
        x2={960}
        y2={880}
        stroke="#E0AE7E"
        strokeWidth={6}
      />
      <ellipse
        cx={470}
        cy={918}
        rx={300}
        ry={44}
        fill="#EF8F6B"
        opacity={0.32}
      />
      <g transform={`rotate(${sway} 150 796)`}>
        {[-52, -26, 0, 26, 52].map((a, i) => (
          <ellipse
            key={a}
            cx={150}
            cy={796 - 58 - (i % 2) * 8}
            rx={21}
            ry={62 + (i % 2) * 8}
            fill={i % 2 ? "#4C9A5A" : "#5FAF6A"}
            stroke={INK}
            strokeWidth={4}
            transform={`rotate(${a} 150 796)`}
          />
        ))}
      </g>
      <path
        d="M106,800 L194,800 L182,884 L118,884 Z"
        fill="#D9774B"
        stroke={INK}
        strokeWidth={O}
        strokeLinejoin="round"
      />
      <rect
        x={98}
        y={788}
        width={104}
        height={22}
        rx={6}
        fill="#E88A5C"
        stroke={INK}
        strokeWidth={O}
      />
    </g>
  );
};

const Stool: React.FC = () => (
  <g>
    <line
      x1={470}
      y1={740}
      x2={470}
      y2={890}
      stroke={WOOD_DARK}
      strokeWidth={16}
      strokeLinecap="round"
      opacity={0.8}
    />
    <ellipse
      cx={470}
      cy={832}
      rx={100}
      ry={15}
      fill="none"
      stroke={INK}
      strokeWidth={17}
    />
    <ellipse
      cx={470}
      cy={832}
      rx={100}
      ry={15}
      fill="none"
      stroke={WOOD_DARK}
      strokeWidth={7}
    />
    <Chain
      pts={[
        { x: 392, y: 728 },
        { x: 358, y: 896 },
      ]}
      w={20}
      color={WOOD_DARK}
    />
    <Chain
      pts={[
        { x: 548, y: 728 },
        { x: 582, y: 896 },
      ]}
      w={20}
      color={WOOD_DARK}
    />
    <ellipse
      cx={470}
      cy={730}
      rx={126}
      ry={26}
      fill={WOOD_DARK}
      stroke={INK}
      strokeWidth={O}
    />
    <ellipse
      cx={470}
      cy={718}
      rx={126}
      ry={26}
      fill="#D08A4C"
      stroke={INK}
      strokeWidth={O}
    />
  </g>
);

const Legs: React.FC<{ tap: number }> = ({ tap }) => (
  <g>
    <ellipse
      cx={420}
      cy={716}
      rx={58}
      ry={40}
      fill={PANTS}
      stroke={INK}
      strokeWidth={O}
    />
    <ellipse
      cx={520}
      cy={716}
      rx={58}
      ry={40}
      fill={PANTS}
      stroke={INK}
      strokeWidth={O}
    />
    <Chain
      pts={[
        { x: 418, y: 744 },
        { x: 400, y: 868 },
      ]}
      w={50}
      color={PANTS}
    />
    <Chain
      pts={[
        { x: 522, y: 744 },
        { x: 540, y: 868 },
      ]}
      w={50}
      color={PANTS}
    />
    <g transform={`translate(0 ${-tap}) rotate(${-tap * 0.9} 366 902)`}>
      <path
        d="M352,882 C352,866 372,858 396,860 C420,862 438,874 438,890 C438,902 422,906 396,906 L368,906 C358,906 352,896 352,882 Z"
        fill="#FFFFFF"
        stroke={INK}
        strokeWidth={O}
        strokeLinejoin="round"
      />
    </g>
    <path
      d="M588,882 C588,866 568,858 544,860 C520,862 502,874 502,890 C502,902 518,906 544,906 L572,906 C582,906 588,896 588,882 Z"
      fill="#FFFFFF"
      stroke={INK}
      strokeWidth={O}
      strokeLinejoin="round"
    />
  </g>
);

const Guitar: React.FC<{ frame: number; uid: string }> = ({ frame, uid }) => {
  const ring = stringRing(frame);
  return (
    <g
      transform={`translate(${G.x} ${G.y}) rotate(${G.angle}) scale(${G.scale})`}
    >
      <defs>
        <linearGradient
          id={`${uid}-wood`}
          gradientUnits="userSpaceOnUse"
          x1="0"
          y1="-110"
          x2="0"
          y2="110"
        >
          <stop offset="0" stopColor="#F2B06C" />
          <stop offset="1" stopColor="#D5873F" />
        </linearGradient>
      </defs>
      <rect
        x={185}
        y={-17}
        width={282}
        height={34}
        fill="#7A4722"
        stroke={INK}
        strokeWidth={O}
      />
      {[
        214, 240, 264, 286, 307, 326, 344, 361, 377, 392, 406, 420, 433, 445,
        456,
      ].map((x) => (
        <line
          key={x}
          x1={x}
          y1={-15}
          x2={x}
          y2={15}
          stroke="#D8C29A"
          strokeWidth={2.6}
        />
      ))}
      {[252, 297, 335, 369].map((x) => (
        <circle key={x} cx={x} cy={0} r={3.6} fill="#F4E6C8" />
      ))}
      <path
        d="M464,-22 L528,-31 C534,-31 537,-27 537,-22 L537,22 C537,27 534,31 528,31 L464,22 Z"
        fill="#4A2A15"
        stroke={INK}
        strokeWidth={O}
        strokeLinejoin="round"
      />
      {[480, 500, 520].map((x) => (
        <g key={x}>
          <circle
            cx={x}
            cy={-34}
            r={7}
            fill="#E4DDD0"
            stroke={INK}
            strokeWidth={3}
          />
          <circle
            cx={x}
            cy={34}
            r={7}
            fill="#E4DDD0"
            stroke={INK}
            strokeWidth={3}
          />
        </g>
      ))}
      <ellipse
        cx={0}
        cy={0}
        rx={104}
        ry={110}
        fill={INK}
        stroke={INK}
        strokeWidth={O * 2}
      />
      <ellipse
        cx={128}
        cy={0}
        rx={82}
        ry={88}
        fill={INK}
        stroke={INK}
        strokeWidth={O * 2}
      />
      <ellipse cx={0} cy={0} rx={104} ry={110} fill={`url(#${uid}-wood)`} />
      <ellipse cx={128} cy={0} rx={82} ry={88} fill={`url(#${uid}-wood)`} />
      <path
        d="M-70,62 C-40,96 40,104 80,70"
        fill="none"
        stroke="#C2742F"
        strokeWidth={10}
        strokeLinecap="round"
        opacity={0.55}
      />
      <circle
        cx={112}
        cy={0}
        r={43}
        fill="none"
        stroke="#F7D9A4"
        strokeWidth={6}
      />
      <circle cx={112} cy={0} r={33} fill="#3B2416" />
      <path
        d="M126,40 C150,46 158,70 140,80 C124,84 112,68 118,48 Z"
        fill="#B8692E"
        opacity={0.7}
      />
      <rect
        x={-52}
        y={-42}
        width={18}
        height={84}
        rx={5}
        fill="#4A2A15"
        stroke={INK}
        strokeWidth={3}
      />
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const y = -12.5 + i * 5;
        const off = ring * 2.6 * Math.sin(frame * 2.9 + i * 1.3);
        return (
          <path
            key={i}
            d={`M-43,${y} Q212,${y + off} 470,${y}`}
            fill="none"
            stroke="#F8F1E3"
            strokeWidth={1.8}
          />
        );
      })}
    </g>
  );
};

const Eighth: React.FC<{ color: string }> = ({ color }) => (
  <g>
    {[INK, color].map((c, i) => (
      <g key={c}>
        <line
          x1={9}
          y1={-2}
          x2={9}
          y2={-42}
          stroke={c}
          strokeWidth={i ? 4.5 : 9}
          strokeLinecap="round"
        />
        <path
          d="M9,-42 C24,-36 27,-22 17,-12"
          fill="none"
          stroke={c}
          strokeWidth={i ? 4.5 : 9}
          strokeLinecap="round"
        />
        <ellipse
          cx={0}
          cy={0}
          rx={i ? 10.5 : 13}
          ry={i ? 7 : 9.5}
          transform="rotate(-22)"
          fill={c}
        />
      </g>
    ))}
  </g>
);

const Beamed: React.FC<{ color: string }> = ({ color }) => (
  <g>
    {[INK, color].map((c, i) => (
      <g key={c}>
        <line
          x1={9}
          y1={-2}
          x2={9}
          y2={-44}
          stroke={c}
          strokeWidth={i ? 4.5 : 9}
          strokeLinecap="round"
        />
        <line
          x1={37}
          y1={-8}
          x2={37}
          y2={-50}
          stroke={c}
          strokeWidth={i ? 4.5 : 9}
          strokeLinecap="round"
        />
        <line
          x1={9}
          y1={-44}
          x2={37}
          y2={-50}
          stroke={c}
          strokeWidth={i ? 8 : 13}
          strokeLinecap="round"
        />
        <ellipse
          cx={0}
          cy={0}
          rx={i ? 10.5 : 13}
          ry={i ? 7 : 9.5}
          transform="rotate(-22)"
          fill={c}
        />
        <ellipse
          cx={28}
          cy={-6}
          rx={i ? 10.5 : 13}
          ry={i ? 7 : 9.5}
          transform="rotate(-22 28 -6)"
          fill={c}
        />
      </g>
    ))}
  </g>
);

// A new note leaves the guitar every 12 frames and floats up toward the window.
const Notes: React.FC<{ frame: number }> = ({ frame }) => {
  const LIFE = 40;
  const notes: React.ReactNode[] = [];
  for (
    let k = Math.max(0, Math.floor((frame - LIFE) / 12));
    k <= Math.floor(frame / 12);
    k++
  ) {
    const age = frame - k * 12;
    if (age < 0 || age > LIFE) {
      continue;
    }
    const t = age / LIFE;
    const x =
      interpolate(t, [0, 1], [548, 640 + (k % 3) * 55]) +
      Math.sin(age / 5 + k) * 10;
    const y = interpolate(t, [0, 1], [560, 250 - (k % 2) * 40], {
      easing: Easing.out(Easing.quad),
    });
    const opacity = interpolate(
      age,
      [0, 6, LIFE - 10, LIFE],
      [0, 1, 1, 0],
      clamp,
    );
    const scale = interpolate(age, [0, 8], [0.4, 1], clamp);
    const color = NOTE_COLORS[k % NOTE_COLORS.length];
    notes.push(
      <g
        key={k}
        opacity={opacity}
        transform={`translate(${x} ${y}) rotate(${Math.sin(age / 7 + k) * 12}) scale(${scale})`}
      >
        {k % 2 === 0 ? <Eighth color={color} /> : <Beamed color={color} />}
      </g>,
    );
  }
  return <g>{notes}</g>;
};

// Same guitarist, a year later: a small stage with string lights, a spotlight and a crowd.
const Stage: React.FC<{ frame: number; uid: string }> = ({ frame, uid }) => {
  const bulbs = new Array(16)
    .fill(0)
    .map((_, i) => ({ x: 30 + i * 60, y: 120 + 30 * Math.sin(i * 0.9) }));
  return (
    <g>
      <defs>
        <linearGradient id={`${uid}-stage`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1A0F2E" />
          <stop offset="1" stopColor="#3A1F52" />
        </linearGradient>
        <linearGradient id={`${uid}-beam`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#FFF4D6" stopOpacity={0.55} />
          <stop offset="1" stopColor="#FFF4D6" stopOpacity={0.05} />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={960} height={1080} fill={`url(#${uid}-stage)`} />
      <path
        d={bulbs.map((b, i) => `${i === 0 ? "M" : "L"}${b.x},${b.y}`).join(" ")}
        fill="none"
        stroke="#5A4470"
        strokeWidth={3}
      />
      {bulbs.map((b, i) => {
        const glow = 0.55 + 0.45 * (0.5 + 0.5 * Math.sin(frame / 5 + i * 1.7));
        return (
          <g key={i} opacity={glow}>
            <circle cx={b.x} cy={b.y + 12} r={20} fill="#FFD27A" opacity={0.25} />
            <circle cx={b.x} cy={b.y + 12} r={9} fill="#FFD27A" />
          </g>
        );
      })}
      <path d="M430,-20 L510,-20 L760,900 L180,900 Z" fill={`url(#${uid}-beam)`} />
      <rect x={0} y={880} width={960} height={200} fill="#2A1830" />
      <line x1={0} y1={880} x2={960} y2={880} stroke="#4A2C52" strokeWidth={6} />
      {[0, 1, 2, 3].map((i) => (
        <line key={i} x1={0} y1={925 + i * 45} x2={960} y2={925 + i * 45} stroke="#3A2242" strokeWidth={3} />
      ))}
      <ellipse cx={470} cy={912} rx={320} ry={46} fill="#FFE8B0" opacity={0.28} />
    </g>
  );
};

const Person: React.FC<{
  x: number;
  y: number;
  s: number;
  color: string;
  clapping: boolean;
  frame: number;
  seed: number;
}> = ({ x, y, s, color, clapping, frame, seed }) => {
  const clap = Math.abs(Math.sin(frame / 3 + seed));
  return (
    <g fill={color} stroke="#3A2A50" strokeWidth={3}>
      {clapping ? (
        <g stroke={color} strokeWidth={16 * s} strokeLinecap="round" fill="none">
          <path d={`M${x - 34 * s},${y - 20 * s} L${x - 12 * s - 14 * s * clap},${y - 150 * s}`} />
          <path d={`M${x + 34 * s},${y - 20 * s} L${x + 12 * s + 14 * s * clap},${y - 150 * s}`} />
        </g>
      ) : null}
      <ellipse cx={x} cy={y} rx={56 * s} ry={42 * s} />
      <circle cx={x} cy={y - 64 * s} r={30 * s} />
    </g>
  );
};

// Two rows of silhouettes in the foreground that bob and clap along.
const Audience: React.FC<{ frame: number }> = ({ frame }) => (
  <g>
    {new Array(9).fill(0).map((_, i) => (
      <Person
        key={`b${i}`}
        x={20 + i * 115}
        y={1010 + 4 * Math.sin(frame / 6 + i * 1.3)}
        s={0.9}
        color="#140B22"
        clapping={i % 3 === 1}
        frame={frame}
        seed={i}
      />
    ))}
    {new Array(8).fill(0).map((_, i) => (
      <Person
        key={`f${i}`}
        x={75 + i * 120}
        y={1090 + 5 * Math.sin(frame / 5 + i * 0.9 + 1)}
        s={1.1}
        color="#0B0614"
        clapping={i % 4 === 2}
        frame={frame}
        seed={i + 10}
      />
    ))}
  </g>
);

// Left half of the split screen: a guitarist strumming on a stool, fully drawn and rigged in code.
export const GuitarRoom: React.FC<{ stage?: boolean }> = ({ stage = false }) => {
  const frame = useCurrentFrame();
  const uid = `gr${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const breath = 2 * Math.sin((TAU * frame) / 48);
  const head = 3.2 * Math.sin((TAU * frame) / 30);
  const mouth = 4 + 5 * Math.abs(Math.sin((TAU * frame) / 30));
  const tap = Math.pow(Math.max(0, Math.sin((TAU * frame) / 15)), 2) * 12;
  const strum = strumAngle(frame);
  const chord =
    352 + (16 * Math.tanh(3 * Math.sin((TAU * frame) / 60))) / Math.tanh(3);

  const shoulderR: Pt = { x: 398, y: 482 - breath };
  const elbowR: Pt = { x: 352, y: 570 };
  const handR = add(
    elbowR,
    mul({ x: Math.cos(rad(23 + strum)), y: Math.sin(rad(23 + strum)) }, 124),
  );
  const pickDir = 23 + strum + 38;
  const pick = add(
    handR,
    mul({ x: Math.cos(rad(pickDir)), y: Math.sin(rad(pickDir)) }, 14),
  );

  const shoulderL: Pt = { x: 542, y: 482 - breath };
  const fret = onGuitar(chord, 0);
  const palm = add(fret, mul(NECK_NORMAL, 24));
  const thumb = add(fret, mul(NECK_NORMAL, -19));
  const elbowL: Pt = { x: 612 + (chord - 352) * 0.3, y: 606 };

  return (
    <svg
      width={960}
      height={1080}
      viewBox="0 0 960 1080"
      style={{ position: "absolute", left: 0, top: 0 }}
    >
      {stage ? <Stage frame={frame} uid={uid} /> : <Room frame={frame} uid={uid} />}
      <Stool />
      <g transform={`translate(0 ${-breath}) rotate(${head} 470 440)`}>
        <path
          d="M388,352 C376,292 418,258 470,258 C526,258 566,294 554,352 C564,420 578,500 552,566 C520,580 420,580 390,566 C364,500 378,420 388,352 Z"
          fill={HAIR}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
      </g>
      <Legs tap={tap} />
      <g transform={`translate(0 ${-breath})`}>
        <rect
          x={452}
          y={408}
          width={36}
          height={56}
          rx={14}
          fill={SKIN}
          stroke={INK}
          strokeWidth={O}
        />
        <path
          d="M388,482 C388,464 402,454 420,452 L520,452 C538,454 552,464 552,482 L556,640 C556,672 538,694 510,696 L430,696 C402,694 384,672 384,640 Z"
          fill={TEE}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
        <path
          d="M526,470 C546,530 548,610 536,690 C548,686 556,668 556,640 L552,482 C552,472 542,466 526,470 Z"
          fill={TEE_SHADE}
        />
        <path
          d="M446,452 Q470,480 494,452"
          fill={SKIN}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
      </g>
      <g transform={`translate(0 ${-breath}) rotate(${head} 470 440)`}>
        <ellipse
          cx={470}
          cy={352}
          rx={66}
          ry={74}
          fill={SKIN}
          stroke={INK}
          strokeWidth={O}
        />
        <circle cx={436} cy={381} r={11} fill="#E07A5F" opacity={0.38} />
        <circle cx={504} cy={381} r={11} fill="#E07A5F" opacity={0.38} />
        <path
          d="M436,358 Q449,346 462,358"
          fill="none"
          stroke={INK}
          strokeWidth={5}
          strokeLinecap="round"
        />
        <path
          d="M478,358 Q491,346 504,358"
          fill="none"
          stroke={INK}
          strokeWidth={5}
          strokeLinecap="round"
        />
        <path
          d="M434,334 Q448,327 462,332"
          fill="none"
          stroke={HAIR}
          strokeWidth={5}
          strokeLinecap="round"
        />
        <path
          d="M478,332 Q492,327 506,334"
          fill="none"
          stroke={HAIR}
          strokeWidth={5}
          strokeLinecap="round"
        />
        <path
          d="M470,368 Q477,380 466,385"
          fill="none"
          stroke="#8C5535"
          strokeWidth={4}
          strokeLinecap="round"
        />
        <ellipse
          cx={470}
          cy={404}
          rx={13}
          ry={mouth}
          fill="#7A2E2A"
          stroke={INK}
          strokeWidth={4}
        />
        <path
          d="M398,352 C394,296 430,270 472,270 C518,270 548,298 544,348 C530,318 500,300 474,300 C456,322 428,338 398,352 Z"
          fill={HAIR}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
        <path
          d="M402,322 C390,362 388,422 396,472 C404,474 410,470 414,464 C406,422 408,372 416,332 Z"
          fill={HAIR}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
        <path
          d="M538,322 C550,362 552,422 544,472 C536,474 530,470 526,464 C534,422 532,372 524,332 Z"
          fill={HAIR}
          stroke={INK}
          strokeWidth={O}
          strokeLinejoin="round"
        />
      </g>
      <circle
        cx={thumb.x}
        cy={thumb.y}
        r={9}
        fill={SKIN}
        stroke={INK}
        strokeWidth={4}
      />
      <Chain pts={[shoulderL, elbowL, palm]} w={32} color={SKIN} />
      <circle
        cx={palm.x}
        cy={palm.y}
        r={20}
        fill={SKIN}
        stroke={INK}
        strokeWidth={O}
      />
      <Chain
        pts={[shoulderL, lerp(shoulderL, elbowL, 0.4)]}
        w={46}
        color={TEE}
      />
      <Guitar frame={frame} uid={uid} />
      {[-16, -1, 14].map((off) => {
        const base = add(fret, mul(NECK_DIR, off));
        return (
          <Chain
            key={off}
            pts={[
              add(base, mul(NECK_NORMAL, 22)),
              add(base, mul(NECK_NORMAL, -4)),
            ]}
            w={11}
            color={SKIN}
            outline={3.5}
          />
        );
      })}
      <Chain pts={[shoulderR, elbowR, handR]} w={32} color={SKIN} />
      <Chain
        pts={[shoulderR, lerp(shoulderR, elbowR, 0.42)]}
        w={46}
        color={TEE}
      />
      <path
        d="M0,-9 L18,0 L0,9 Z"
        transform={`translate(${pick.x} ${pick.y}) rotate(${pickDir})`}
        fill="#FF7A2F"
        stroke={INK}
        strokeWidth={3}
        strokeLinejoin="round"
      />
      <circle
        cx={handR.x}
        cy={handR.y}
        r={19}
        fill={SKIN}
        stroke={INK}
        strokeWidth={O}
      />
      <Notes frame={frame} />
      {stage ? <Audience frame={frame} /> : null}
    </svg>
  );
};
