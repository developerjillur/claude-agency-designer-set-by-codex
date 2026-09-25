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

// Two Vox beats with no media (words, a tag, a chart, a newspaper, a bubble, a typewriter), for the Studio and the
// setup check.
export const VOX_SAMPLE: Edl = {
  ...SAMPLE,
  job: "vox-sample",
  title: "Vox sample",
  durationInFrames: 300,
  theme: {
    ...SAMPLE.theme,
    accent: "#FF8900", paper: "#D9D7D1", paperText: "#161616", highlight: "#F4B41A", marker: "#E04329",
    cream: "#F9F5ED", grid: "rgba(250, 248, 242, 0.62)", display: "Montserrat", backdrop: "grid", grain: 0.16,
  },
  clips: [
    {
      id: "c001", from: 0, durationInFrames: 300, layout: "voiceOnly", masterIn: 0, masterOut: 10, segment: 0, beat: "hook",
      punch: 1, pip: { corner: "br", shape: "circle", size: 0.17 }, cam: null, screen: null, broll: null,
      transitionIn: { type: "cut", frames: 0 },
    },
  ],
  overlays: [
    {
      id: "o001", type: "vox", slot: "full", from: 0, durationInFrames: 150, enter: "cut", exit: "cut",
      props: {
        push: 0.035, tail: 0,
        elements: [
          { id: "paper", kind: "newspaper", x: 0.36, y: 0.52, anchor: "center", w: 0.56, layer: "mid", enter: "rise", at: 0, out: 150, exit: "cut",
            masthead: "The Daily Ledger", left: ["EST. 1921", "WORLD EDITION"], right: ["SAMPLE PAGE", "LATE EDITION"],
            section: "Economy", kicker: "Analysis", corner: "Comment", headline: ["The price of a barrel", "keeps climbing"],
            marks: [{ text: "keeps climbing", at: 40 }], deck: "A sample page with a made-up masthead.", byline: "By the sample desk" },
          { id: "price", kind: "tag", x: 0.8, y: 0.3, anchor: "center", layer: "text", enter: "pop", at: 30, out: 150, exit: "cut",
            value: "$116", from: 25, unit: "per barrel", icon: "barrel", size: 110, land: 75 },
          { id: "ring", kind: "scribble", shape: "circle", x: 0.8, y: 0.3, anchor: "center", w: 0.2, h: 0.2, layer: "text", enter: "none", at: 80, out: 150, exit: "cut" },
          { id: "ask", kind: "bubble", lines: ["Is it", "worth it?"], highlight: "worth", x: 0.8, y: 0.72, anchor: "center", tail: "down-left",
            rotate: 5, size: 60, layer: "text", enter: "pop", at: 95, out: 150, exit: "cut" },
        ],
        cues: [],
      },
    },
    {
      id: "o002", type: "vox", slot: "full", from: 150, durationInFrames: 150, enter: "cut", exit: "cut",
      props: {
        push: 0.035, tail: 0,
        elements: [
          { id: "chart", kind: "chart", x: 0.5, y: 0.45, anchor: "center", w: 0.56, layer: "mid", enter: "rise", at: 0,
            title: "Sample line", note: "made-up values", series: [{ name: "Price", values: [2, 3, 2.5, 4, 6, 5, 7] }, { name: "Trend", values: [2, 2.4, 2.8, 3.2, 3.6, 4, 4.4] }],
            xLabels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], drawAt: 10, drawEnd: 60, callout: { text: ["Week high", "7"], at: 62 },
            moves: [{ at: 80, y: 0.36, scale: 0.8 }] },
          { id: "type", kind: "typewriter", x: 0.08, y: 0.84, anchor: "left", layer: "text", enter: "none", at: 90, size: 50,
            lines: ["Prices end the week higher."], times: [90, 98, 104, 110, 118] },
          { id: "src", kind: "credit", text: "Sample data", x: 0.05, y: 0.94, anchor: "bottom-left", layer: "text", enter: "fade", at: 20 },
        ],
        cues: [],
      },
    },
  ],
  captions: { ...SAMPLE.captions, burn: false, pages: [] },
  progress: "bottom",
  speech: [],
};

