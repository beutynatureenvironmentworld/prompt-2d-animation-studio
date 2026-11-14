import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame,useVideoConfig} from 'remotion';
import art from './art.cjs';
import story from './story.json';
const Film=({story})=>{
  const frame=useCurrentFrame(),{fps}=useVideoConfig();
  return <AbsoluteFill dangerouslySetInnerHTML={{__html:art.svg(story,frame/fps)}}/>;
};
const frames=s=>Math.round(24*s.shots.reduce((n,shot)=>n+shot.seconds,0));
registerRoot(()=> <Composition id="MoonlitRoom" component={Film} fps={24} width={1080} height={1920}
  durationInFrames={frames(story)} defaultProps={{story}}
  calculateMetadata={({props})=>({durationInFrames:frames(props.story)})}/>);
