import React from "react";
import { AbsoluteFill } from "remotion";
import { RunnerTrack } from "../components/Runner";

export const FINISH_AT = 62;

// Full-width race-day payoff: the same runner rig breaks the finish tape, confetti falls.
export const FinishLineScene: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#A9DDF3" }}>
    <RunnerTrack width={1920} runnerX={700} finishAt={FINISH_AT} />
  </AbsoluteFill>
);
