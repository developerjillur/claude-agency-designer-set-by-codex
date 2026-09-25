import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { ding, mouseClick, shutterModern, whip, whoosh } from "@remotion/sfx";
import { SplitScreenScene } from "./scenes/SplitScreenScene";
import { CreatorScene } from "./scenes/CreatorScene";
import { TimelineScene } from "./scenes/TimelineScene";
import { StatScene } from "./scenes/StatScene";
import { CaptionScene } from "./scenes/CaptionScene";
import { BarSweep } from "./components/BarSweep";
import { RoundPip } from "./components/RoundPip";

// 10-second B-roll sampler (300 frames at 30 fps).
// Timeline: split screen 0-70, creator 70-136, timeline UI 126-184, stat card 184-248, caption 240-300.
export const BrollDemo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence name="Split screen" durationInFrames={70}>
          <SplitScreenScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Creator + icons" durationInFrames={66}>
          <CreatorScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={springTiming({
            config: { damping: 200 },
            durationInFrames: 10,
          })}
        />
        <TransitionSeries.Sequence name="Timeline UI" durationInFrames={58}>
          <TimelineScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Overlay durationInFrames={16}>
          <BarSweep />
        </TransitionSeries.Overlay>
        <TransitionSeries.Sequence name="Stat card" durationInFrames={64}>
          <StatScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-bottom" })}
          timing={springTiming({
            config: { damping: 200 },
            durationInFrames: 8,
          })}
        />
        <TransitionSeries.Sequence name="Kinetic caption" durationInFrames={60}>
          <CaptionScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      <Sequence name="Presenter PiP" from={80} durationInFrames={100}>
        <RoundPip src={staticFile("presenter-pip.png")} />
      </Sequence>

      <Sequence name="SFX panels in" from={0} layout="none">
        <Audio src={whoosh} volume={0.55} />
      </Sequence>
      <Sequence name="SFX sweep 1" from={62} layout="none">
        <Audio src={whoosh} volume={0.85} />
      </Sequence>
      <Sequence name="SFX shutter" from={75} layout="none">
        <Audio src={shutterModern} volume={0.8} />
      </Sequence>
      <Sequence name="SFX icon 1" from={84} layout="none">
        <Audio src={mouseClick} volume={0.5} />
      </Sequence>
      <Sequence name="SFX icon 2" from={90} layout="none">
        <Audio src={mouseClick} volume={0.5} />
      </Sequence>
      <Sequence name="SFX icon 3" from={96} layout="none">
        <Audio src={mouseClick} volume={0.5} />
      </Sequence>
      <Sequence name="SFX slide" from={126} layout="none">
        <Audio src={whip} volume={0.6} />
      </Sequence>
      <Sequence name="SFX sweep 2" from={176} layout="none">
        <Audio src={whoosh} volume={0.85} />
      </Sequence>
      <Sequence name="SFX stat lands" from={234} layout="none">
        <Audio src={ding} volume={0.7} />
      </Sequence>
    </AbsoluteFill>
  );
};
