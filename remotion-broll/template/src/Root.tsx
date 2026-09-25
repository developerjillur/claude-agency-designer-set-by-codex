import "./index.css";
import { Composition, Folder } from "remotion";
import { BrollDemo } from "./BrollDemo";
import { SplitScreenScene } from "./scenes/SplitScreenScene";
import { CreatorScene } from "./scenes/CreatorScene";
import { TimelineScene } from "./scenes/TimelineScene";
import { StatScene } from "./scenes/StatScene";
import { CaptionScene } from "./scenes/CaptionScene";
import { BrollMinute } from "./BrollMinute";
import { Part2 } from "./Part2";
import { HabitScene } from "./scenes2/HabitScene";
import { ShareScene } from "./scenes2/ShareScene";
import { FeedbackScene } from "./scenes2/FeedbackScene";
import { StatBarsScene } from "./scenes2/StatBarsScene";
import { PayoffSplit } from "./scenes2/PayoffSplit";
import { FinishLineScene } from "./scenes2/FinishLineScene";
import { StoryCards } from "./scenes2/StoryCards";
import { EndCard } from "./scenes2/EndCard";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="BrollDemo-Scenes">
        <Composition
          id="SplitScreen"
          component={SplitScreenScene}
          width={1920}
          height={1080}
          fps={30}
          durationInFrames={70}
        />
        <Composition
          id="Creator"
          component={CreatorScene}
          width={1920}
          height={1080}
          fps={30}
          durationInFrames={66}
        />
        <Composition
          id="Timeline"
          component={TimelineScene}
          width={1920}
          height={1080}
          fps={30}
          durationInFrames={58}
        />
        <Composition
          id="StatCard"
          component={StatScene}
          width={1920}
          height={1080}
          fps={30}
          durationInFrames={64}
        />
        <Composition
          id="Caption"
          component={CaptionScene}
          width={1920}
          height={1080}
          fps={30}
          durationInFrames={60}
        />
      </Folder>
      <Folder name="Part2-Scenes">
        <Composition id="Habit" component={HabitScene} width={1920} height={1080} fps={30} durationInFrames={165} />
        <Composition id="Share" component={ShareScene} width={1920} height={1080} fps={30} durationInFrames={165} />
        <Composition id="Feedback" component={FeedbackScene} width={1920} height={1080} fps={30} durationInFrames={165} />
        <Composition id="StatBars" component={StatBarsScene} width={1920} height={1080} fps={30} durationInFrames={180} />
        <Composition id="Payoff" component={PayoffSplit} width={1920} height={1080} fps={30} durationInFrames={180} />
        <Composition id="FinishLine" component={FinishLineScene} width={1920} height={1080} fps={30} durationInFrames={150} />
        <Composition id="RecapCards" component={StoryCards} width={1920} height={1080} fps={30} durationInFrames={150} />
        <Composition id="EndCard" component={EndCard} width={1920} height={1080} fps={30} durationInFrames={150} />
      </Folder>
      <Composition id="Part2" component={Part2} width={1920} height={1080} fps={30} durationInFrames={1500} />
      <Composition id="BrollMinute" component={BrollMinute} width={1920} height={1080} fps={30} durationInFrames={1800} />
      <Composition
        id="BrollDemo"
        component={BrollDemo}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={300}
      />
    </>
  );
};
