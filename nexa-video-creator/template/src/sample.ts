// A small synthetic edit with no media files, so the Studio and the setup check can render without a job.
import { Edl, Page } from "./lib";

const words: [string, number, number][] = [
  ["Most", 0.2, 0.45], ["people", 0.5, 0.85], ["lose", 0.9, 1.15], ["their", 1.2, 1.4], ["viewers", 1.45, 1.9],
  ["in", 1.95, 2.05], ["three", 2.1, 2.4], ["seconds.", 2.45, 3.0], ["Here", 3.6, 3.8], ["is", 3.85, 3.95],
  ["the", 4.0, 4.1], ["fix,", 4.15, 4.6], ["in", 4.8, 4.9], ["three", 4.95, 5.25], ["steps.", 5.3, 5.9],
];

const pages: Page[] = [];
for (let i = 0; i < words.length; i += 3) {
  const group = words.slice(i, i + 3);
  const next = words[i + 3];
  pages.push({
    startMs: Math.round(group[0][1] * 1000),
    endMs: Math.round((next && next[1] - group[group.length - 1][2] < 0.3 ? next[1] : group[group.length - 1][2] + 0.15) * 1000),
    tokens: group.map(([w, s, e], k) => ({ text: (k ? " " : "") + w, fromMs: Math.round(s * 1000), toMs: Math.round(e * 1000), emphasis: w === "three" })),
  });
}

export const SAMPLE: Edl = {
  schema: "nvc-edl/1",
  job: "sample",
  target: "youtube",
  title: "Sample edit",
  language: "en",
  width: 1920,
  height: 1080,
  fps: 30,
  durationInFrames: 360,
  safe: { x: 96, y: 54, w: 1728, h: 972 },
  bands: { title: { y: 90, h: 220 }, lower: { y: 760, h: 150 }, captions: { y: 890, h: 130 } },
  theme: {
    accent: "#FFD23F", text: "#FFFFFF", ink: "#0E1014", bg: "#0E1014", card: "#FFFFFF", cardText: "#0E1014",
    muted: "#9AA3B2", danger: "#FF4D4D", display: "Poppins", body: "Inter", captions: "Montserrat", radius: 28,
    palette: ["#FF7A2F", "#6D3AF0", "#1F5C63", "#E8521A", "#2A6FDB"], paper: "#F4EEE5", paperText: "#1E1B2E",
    highlight: "#FFC43D", backdrop: "paper", displayBn: "AnekBangla", bodyBn: "HindSiliguri",
  },
  base: "",
  audio: null,
  sources: {},
  clips: [
    {
      id: "c001", from: 0, durationInFrames: 180, layout: "voiceOnly", masterIn: 0, masterOut: 6, segment: 0, beat: "hook",
      punch: 1, pip: { corner: "br", shape: "circle", size: 0.17 }, cam: null, screen: null, broll: null,
      transitionIn: { type: "cut", frames: 0 },
    },
    {
      id: "c002", from: 180, durationInFrames: 180, layout: "voiceOnly", masterIn: 6, masterOut: 12, segment: 1, beat: "steps",
      punch: 1, pip: { corner: "br", shape: "circle", size: 0.17 }, cam: null, screen: null, broll: null,
      transitionIn: { type: "zoom", frames: 9 },
    },
  ],
  overlays: [
    { id: "o001", type: "kinetic", slot: "full", from: 0, durationInFrames: 96, enter: "cut", props: { lines: ["Most people lose their", "viewers in three seconds"], highlight: "three seconds", hideCaptions: true } },
    { id: "o002", type: "step", slot: "full", from: 96, durationInFrames: 84, enter: "sweep", props: { n: 1, label: "Step 1", numText: "1", lines: ["Open on the result"], hideCaptions: true } },
    { id: "o003", type: "bars", slot: "full", from: 180, durationInFrames: 110, enter: "slide", props: { title: ["Viewers still watching"], rows: [{ label: "0 s", value: 100, text: "100%" }, { label: "3 s", value: 62, text: "62%" }, { label: "30 s", value: 41, text: "41%" }], focus: 1, note: "Sample figures", t: { start: 20, step: 15, len: 17, focus: 1, land: 66 } } },
    { id: "o004", type: "endCard", slot: "full", from: 290, durationInFrames: 70, enter: "slideUp", props: { lines: ["Start today"], button: "Subscribe", pressed: "Subscribed", t: { click: 44 }, hideCaptions: true } },
  ],
  zooms: [],
  captions: { style: "word", burn: true, fontPx: 64, band: { y: 890, h: 130 }, pages, cues: [], case: "upper" },
  chapters: [],
  progress: true,
  speech: [[6, 90], [108, 177]],
};
