import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import { Edit } from "./Edit";
import { Edl } from "./lib";
import { SAMPLE, VOX_SAMPLE } from "./sample";

// Size, frame rate and length come from the EDL passed with --props, so one composition serves every target.
const calculateMetadata: CalculateMetadataFunction<Edl> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationInFrames)),
  fps: props.fps,
  width: props.width,
  height: props.height,
  defaultOutName: `${props.job}-${props.target}`,
});

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Edit"
      component={Edit}
      defaultProps={SAMPLE}
      calculateMetadata={calculateMetadata}
      durationInFrames={SAMPLE.durationInFrames}
      fps={SAMPLE.fps}
      width={SAMPLE.width}
      height={SAMPLE.height}
    />
    <Composition
      id="VoxSample"
      component={Edit}
      defaultProps={VOX_SAMPLE}
      calculateMetadata={calculateMetadata}
      durationInFrames={VOX_SAMPLE.durationInFrames}
      fps={VOX_SAMPLE.fps}
      width={VOX_SAMPLE.width}
      height={VOX_SAMPLE.height}
    />
  </>
);
