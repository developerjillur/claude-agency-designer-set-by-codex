// Every word the video shows, and the numbers its charts compute from. For a new product change this file and
// theme.ts, mirror the lines into copy/onscreen.json, and lint them:
//   python3 ~/.claude/skills/codex-design/scripts/design.py copylint --copy copy/onscreen.json
// Keep each line short: a line on screen gets about a second.
export const COPY = {
  split: { left: "Just for fun", right: "Race day" },
  creator: { rec: "REC" },
  stat: {
    title: ["Get 1% better", "every day"],
    result: "better after one year",
    axisStart: "Today",
    axisEnd: "1 year",
    lineGrow: "1% a day",
    lineFlat: "No change",
  },
  caption: {
    first: ["If", "your", "skills", "aren't", "paying", "you", "yet,"],
    firstKey: ["paying"],
    next: ["try", "this", "for", "one", "year."],
    nextKey: ["one", "year."],
  },
  steps: [
    ["Practice a little", "every day"],
    ["Share what", "you make"],
    ["Fix one thing", "every time"],
  ],
  habit: { title: "Practice streak" },
  share: { uploading: "Uploading", posted: "Posted" },
  bars: {
    title: "What 1% a day adds up to",
    note: "Math: 1.01 to the power of the number of days",
    periods: [
      { label: "1 week", days: 7 },
      { label: "1 month", days: 30 },
      { label: "6 months", days: 180 },
      { label: "1 year", days: 365 },
    ],
  },
  payoff: { before: "Day 1", after: "Day 365" },
  finish: "FINISH",
  recap: ["Practice", "Share", "Improve"],
  end: { words: ["Pick", "one", "skill", "and", "start", "today."], button: "Subscribe", pressed: "Subscribed" },
};

// The stat card and the bar chart compute from these: (1 + rate) to the power of the days. Keep the copy above
// (the stat title, the bar chart's note) in step with them.
export const GROWTH = { rate: 0.01, days: 365 };
