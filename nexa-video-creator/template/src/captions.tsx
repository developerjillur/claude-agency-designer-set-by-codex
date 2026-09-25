// Burned-in captions. Word style: pages of 1 to 3 words, the spoken word lit in the accent colour at its onset.
// Sentence style: subtitle cues of up to two lines on a soft box. Pages come pre-built from the compiler, and the
// active one is found by binary search, so a long video costs the same per frame as a short one.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Edl, Page, clampOpts, easeOut, font, isBengali, unit } from "./lib";

const findActive = <T extends { startMs: number; endMs: number }>(items: T[], ms: number): T | null => {
  let lo = 0;
  let hi = items.length - 1;
  let found = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (items[mid].startMs <= ms) {
      found = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  if (found < 0) return null;
  const item = items[found];
  return ms < item.endMs ? item : null;
};

// Where the caption block is centred: the target's caption band, or the seam of a stacked vertical layout.
const captionCentre = (edl: Edl, frame: number): number => {
  const band = edl.captions.band || edl.bands.captions;
  const clip = edl.clips.find((c) => frame >= c.from && frame < c.from + c.durationInFrames);
  if (clip && clip.layout === "stack") return Math.round(edl.height * 0.5);
  return band.y + band.h / 2;
};

const WordPage: React.FC<{ edl: Edl; page: Page; ms: number; centre: number }> = ({ edl, page, ms, centre }) => {
  const { width, height, fps } = useVideoConfig();
  const u = unit(width, height);
  const text = page.tokens.map((t) => t.text).join("");
  const bn = isBengali(text);
  const upper = edl.captions.case === "upper" && !bn;
  // shrink a long page to fit one line inside the safe width (down to 72 %) before letting it wrap
  const visible = Array.from(text).filter((ch) => !/[ঁ-ঃ়া-্ৗৢৣ‌‍]/.test(ch)).length;
  const base = edl.captions.fontPx * (bn ? 1.1 : 1);
  const perChar = bn ? 0.62 : upper ? 0.7 : 0.6;
  const fit = Math.min(1, edl.safe.w / Math.max(1, visible * perChar * base));
  const size = Math.round(base * Math.max(0.72, fit));
  const since = ((ms - page.startMs) / 1000) * fps;
  const pop = interpolate(since, [0, 4], [0.9, 1], { ...clampOpts, easing: easeOut });
  return (
    <div
      style={{
        position: "absolute",
        left: edl.safe.x,
        width: edl.safe.w,
        top: centre - size,
        height: size * 2,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          fontFamily: font(bn ? "HindSiliguri" : edl.theme.captions),
          fontWeight: bn ? 700 : 900,
          fontSize: size,
          lineHeight: bn ? 1.35 : 1.1,
          textAlign: "center",
          whiteSpace: "pre-wrap",
          transform: `scale(${pop})`,
          maxWidth: edl.safe.w,
        }}
      >
        {page.tokens.map((t, i) => {
          const active = ms >= t.fromMs && ms < t.toMs;
          const color = active || t.emphasis ? edl.theme.accent : "#FFFFFF";
          return (
            <span
              key={i}
              style={{
                color,
                textTransform: upper ? "uppercase" : "none",
                WebkitTextStroke: `${Math.max(2, Math.round(size * (bn ? 0.06 : 0.1)))}px #000000`,
                paintOrder: "stroke fill",
                textShadow: `0 ${Math.round(6 * u)}px ${Math.round(18 * u)}px rgba(0,0,0,0.45)`,
                display: "inline-block",
                transform: active ? "scale(1.06)" : undefined,
              }}
            >
              {t.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const SentenceCue: React.FC<{ edl: Edl; lines: string[] }> = ({ edl, lines }) => {
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  const text = lines.join(" ");
  const bn = isBengali(text);
  const band = edl.captions.band || edl.bands.captions;
  const size = Math.round(edl.captions.fontPx * (bn ? 1.08 : 1));
  return (
    <div style={{ position: "absolute", left: edl.safe.x, width: edl.safe.w, top: band.y, height: band.h, display: "flex", alignItems: "flex-end", justifyContent: "center" }}>
      <div
        style={{
          backgroundColor: "rgba(0,0,0,0.62)",
          borderRadius: Math.round(12 * u),
          padding: `${Math.round(8 * u)}px ${Math.round(20 * u)}px`,
          fontFamily: font(bn ? "HindSiliguri" : edl.theme.body),
          fontWeight: 600,
          fontSize: size,
          lineHeight: bn ? 1.45 : 1.3,
          color: "#FFFFFF",
          textAlign: "center",
          maxWidth: Math.round(width * 0.68),
        }}
      >
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </div>
  );
};

export const Captions: React.FC<{ edl: Edl }> = ({ edl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  if (edl.captions.style === "word") {
    const page = findActive(edl.captions.pages, ms);
    if (!page) return null;
    return (
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <WordPage edl={edl} page={page} ms={ms} centre={captionCentre(edl, frame)} />
      </AbsoluteFill>
    );
  }
  if (edl.captions.style === "sentence") {
    const cue = findActive(edl.captions.cues, ms);
    if (!cue) return null;
    return (
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <SentenceCue edl={edl} lines={cue.lines} />
      </AbsoluteFill>
    );
  }
  return null;
};
