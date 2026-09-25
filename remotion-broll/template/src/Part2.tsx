import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { ding, mouseClick, uiSwitch, whip, whoosh } from "@remotion/sfx";
import { BarSweep } from "./components/BarSweep";
import { RoundPip } from "./components/RoundPip";
import { ContinueCaption } from "./scenes2/ContinueCaption";
import { StepCard } from "./scenes2/StepCard";
import { HABIT_DONE, HabitScene } from "./scenes2/HabitScene";
import { ShareScene, UPLOAD_DONE } from "./scenes2/ShareScene";
import { FeedbackScene, TRIM_AT } from "./scenes2/FeedbackScene";
import { BARS_DONE, StatBarsScene } from "./scenes2/StatBarsScene";
import { PayoffSplit } from "./scenes2/PayoffSplit";
import { FINISH_AT, FinishLineScene } from "./scenes2/FinishLineScene";
import { StoryCards } from "./scenes2/StoryCards";
import { CLICK_AT, EndCard } from "./scenes2/EndCard";
import { COPY } from "./copy";

const slideIn = (direction: "from-right" | "from-bottom") => (
  <TransitionSeries.Transition
    presentation={slide({ direction })}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: 10 })}
  />
);

// Scene starts inside this 1500-frame part (slides overlap 10 frames, bar sweeps overlap none).
const AT = {
  step1: 75,
  habit: 125,
  step2: 290,
  share: 340,
  step3: 505,
  feedback: 555,
  bars: 720,
  payoff: 890,
  finish: 1070,
  cards: 1210,
  end: 1350,
};

const SFX: [number, string, number][] = [
  [AT.step1 - 8, whoosh, 0.85],
  [AT.step1 + 2, uiSwitch, 0.6],
  [AT.habit, whip, 0.6],
  [AT.habit + HABIT_DONE, ding, 0.6],
  [AT.step2 - 8, whoosh, 0.85],
  [AT.step2 + 2, uiSwitch, 0.6],
  [AT.share, whip, 0.6],
  [AT.share + UPLOAD_DONE, ding, 0.6],
  [AT.share + UPLOAD_DONE + 6, mouseClick, 0.5],
  [AT.share + UPLOAD_DONE + 12, mouseClick, 0.5],
  [AT.share + UPLOAD_DONE + 18, mouseClick, 0.5],
  [AT.step3 - 8, whoosh, 0.85],
  [AT.step3 + 2, uiSwitch, 0.6],
  [AT.feedback, whip, 0.6],
  [AT.feedback + TRIM_AT, uiSwitch, 0.7],
  [AT.bars - 8, whoosh, 0.85],
  [AT.bars + BARS_DONE, ding, 0.7],
  [AT.payoff, whip, 0.6],
  [AT.finish - 8, whoosh, 0.85],
  [AT.finish + FINISH_AT, whip, 0.7],
  [AT.finish + FINISH_AT + 2, ding, 0.6],
  [AT.cards, whip, 0.6],
  [AT.end, whip, 0.6],
  [AT.end + CLICK_AT, mouseClick, 0.7],
  [AT.end + CLICK_AT + 4, ding, 0.6],
];

// Seconds 10 to 60: three steps, the compounding bars, the payoff and the call to action,
// all built from the assets of the first 10 seconds.
export const Part2: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence name="Caption continues" durationInFrames={75}>
          <ContinueCaption />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Step 1 card" durationInFrames={60}>
          <StepCard step={1} lines={COPY.steps[0]} color="#FF7A2F" accent="#FFE08A" />
        </TransitionSeries.Sequence>
        {slideIn("from-right")}
        <TransitionSeries.Sequence name="Habit streak" durationInFrames={165}>
          <HabitScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Step 2 card" durationInFrames={60}>
          <StepCard step={2} lines={COPY.steps[1]} color="#6D3AF0" accent="#FFB3D9" />
        </TransitionSeries.Sequence>
        {slideIn("from-right")}
        <TransitionSeries.Sequence name="Share and upload" durationInFrames={165}>
          <ShareScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Step 3 card" durationInFrames={60}>
          <StepCard step={3} lines={COPY.steps[2]} color="#1F5C63" accent="#8EE3C8" />
        </TransitionSeries.Sequence>
        {slideIn("from-right")}
        <TransitionSeries.Sequence name="Feedback edit" durationInFrames={165}>
          <FeedbackScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Compounding bars" durationInFrames={180}>
          <StatBarsScene />
        </TransitionSeries.Sequence>
        {slideIn("from-bottom")}
        <TransitionSeries.Sequence name="Day 1 vs Day 365" durationInFrames={180}>
          <PayoffSplit />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Finish line" durationInFrames={150}>
          <FinishLineScene />
        </TransitionSeries.Sequence>
        {slideIn("from-right")}
        <TransitionSeries.Sequence name="Recap cards" durationInFrames={150}>
          <StoryCards />
        </TransitionSeries.Sequence>
        {slideIn("from-bottom")}
        <TransitionSeries.Sequence name="End card" durationInFrames={150}>
          <EndCard />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      <Sequence name="PiP over share" from={AT.share + 12} durationInFrames={143}>
        <RoundPip src={staticFile("presenter-pip.png")} />
      </Sequence>
      <Sequence name="PiP over feedback" from={AT.feedback + 12} durationInFrames={143}>
        <RoundPip src={staticFile("presenter-pip.png")} />
      </Sequence>

      {SFX.map(([from, src, volume], i) => (
        <Sequence key={`${from}-${i}`} name={`SFX ${i + 1}`} from={from} layout="none">
          <Audio src={src} volume={volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
