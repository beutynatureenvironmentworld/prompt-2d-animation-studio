"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {solveTwoBone, girlPose, boyPose,inspect}=require('./rig_ik.cjs');
const {svg}=require('./art.cjs');
const story=JSON.parse(fs.readFileSync(path.join(__dirname,'story.json'),'utf8'));
assert.equal(story.shots.length,5);
assert.equal(story.shots.reduce((a,s)=>a+s.seconds,0),15);
const samples=inspect();
for(const row of samples){
 assert(row.girl_hand_error<.025,'girl wrist not reachable at '+row.t+': '+row.girl_hand_error);
 assert(row.boy_hand_error<.025,'boy wrist not reachable '+row.t);
 assert(row.leg_error<.025,'foot not reachable '+row.t);
 assert.equal(row.girl_left_foot_y,558,'support foot must stay planted');
}
for(const t of [.2,1.1,3.5,5.8,6.5,7.5,8.8,9.6,10.9,12.8,14.8]){
 const frame=svg(story,t);
 assert(frame.startsWith('<svg'),'actual SVG frame');
 assert(frame.includes('<path')&&frame.includes('<ellipse'),'real vector elements');
 assert(!/(NaN|undefined|Infinity)/.test(frame),'invalid 2D geometry at '+t);
 assert(frame.includes('linearGradient'),'keep original source-film color/shading');
 assert(frame.includes('translate('),'preserve shot camera movement');
}
const hand=girlPose(8.999,{reach:1,shock:0});
assert(Math.hypot(hand.wrist[0]-201,hand.wrist[1]-397)<.005,'girl must actually hold carton center');
const handBoy=boyPose(8.9,{laugh:0});
assert(Math.hypot(handBoy.wrist[0]-232,handBoy.wrist[1]-399)<.005,'boy must hold sealed face not straw');
const straight=solveTwoBone([0,0],[50,0],30,30);
assert(straight.error<.001);
console.log('FTE_2BONE_IK_HOLD_GRIP_FOOTPLANT_TESTS_PASS',JSON.stringify(samples));
