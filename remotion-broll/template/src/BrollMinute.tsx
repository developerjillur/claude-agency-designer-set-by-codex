import React from "react";
import { Series } from "remotion";
import { BrollDemo } from "./BrollDemo";
import { Part2 } from "./Part2";

// The full one-minute cut: the approved 10-second opening, then the next 50 seconds.
export const BrollMinute: React.FC = () => (
  <Series>
    <Series.Sequence name="Seconds 0-10" durationInFrames={300}>
      <BrollDemo />
    </Series.Sequence>
    <Series.Sequence name="Seconds 10-60" durationInFrames={1500}>
      <Part2 />
    </Series.Sequence>
  </Series>
);
