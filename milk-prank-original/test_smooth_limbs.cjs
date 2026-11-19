"use strict";
const assert=require("node:assert/strict");
const rig=require("./rig_ik.cjs");
const fs=require("node:fs");
const art=require("./art.cjs");
const story=JSON.parse(fs.readFileSync(__dirname+"/story.json","utf8"));
const easy=rig.limb([0,0],[65,0],48,48,1,5.6,.02);
const move=rig.limb([0,0],[65,0],48,48,1,5.6,.20);
assert(easy.svg.startsWith('<path'),'single visible limb path');
assert(easy.svg.includes('Q'),'continuous smooth quadratic, not V-shaped strokes');
assert(!easy.svg.includes('<ellipse'),'joint markers are forbidden');
assert(!easy.svg.includes('L'),'visible elbow/knee straight-segment V is forbidden');
assert(Math.abs(easy.curve)<1.6,'rest-pose curvature must be barely perceptible');
assert(Math.abs(move.curve)<7.3,'action bend must remain subtle');
assert(Math.abs(move.curve)>Math.abs(easy.curve),'only action should bend more');
for(const t of [0,.5,1.2,3.5,5.5,6.6,7.8,8.8,9.6,10.5,12.5,14.7]){
 const g=rig.girlPose(t,{reach:t<6?0:(t>9?1:(t-6)/3),shock:t>9.2?.7:0});
 const b=rig.boyPose(t,{laugh:t>11.3?(t-11.3)/3:0});
 assert(g.armError<.02 && b.armError<.02,'hidden rig must still reach hand target');
 assert(g.legError<.02 && b.legError<.02,'hidden IK foot planting');
 assert(!g.svg.includes('ellipse'),'girl skeleton must not expose joint circles');
 assert(!b.svg.includes('ellipse'),'boy skeleton must not expose joint circles');
 const svg=art.svg(story,t);
 assert(!svg.includes('NaN') && !svg.includes('undefined'),'valid source style frame');
}
const grip=rig.girlPose(8.99,{reach:1});
assert(Math.hypot(grip.wrist[0]-201,grip.wrist[1]-397)<.01);
console.log("SMOOTH_STROKE_HIDDEN_IK_V3_ALL_TESTS_PASS");
