"use strict";
/* Original Funny Toon Ever two-bone IK rig. No external assets or neural generation. */
const PI=Math.PI,ink="#211b36",skin="#f7e6cf";
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const smooth=v=>{v=clamp(v);return v*v*(3-2*v);};
const mix=(a,b,v)=>a+(b-a)*v;
const coord=q=>q.map(v=>Number(v).toFixed(2)).join(" ");
function path(d,fill="none",stroke=ink,width=4){
 return '<path d="'+d+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+width+'" stroke-linecap="round" stroke-linejoin="round"/>';
}
function ellipse(x,y,rx,ry,fill=skin,stroke=ink,width=2){
 return '<ellipse cx="'+x+'" cy="'+y+'" rx="'+rx+'" ry="'+ry+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+width+'"/>';
}
function solveTwoBone(a,target,l1,l2,side=1){
 let dx=target[0]-a[0],dy=target[1]-a[1],distance=Math.hypot(dx,dy);
 if(distance<.00001){dx=1;dy=0;distance=1;}
 const length=clamp(distance,Math.abs(l1-l2)+.001,l1+l2-.001);
 const ux=dx/distance,uy=dy/distance;
 const cos=clamp((l1*l1+length*length-l2*l2)/(2*l1*length),-1,1);
 const sin=Math.sqrt(Math.max(0,1-cos*cos));
 const elbow=[a[0]+l1*(ux*cos-side*uy*sin),a[1]+l1*(uy*cos+side*ux*sin)];
 const wrist=[a[0]+ux*length,a[1]+uy*length];
 return {elbow,wrist,error:Math.hypot(target[0]-wrist[0],target[1]-wrist[1])};
}
function limb(a,target,l1,l2,side=1,width=4.5){
 const data=solveTwoBone(a,target,l1,l2,side);
 const svg=path("M"+coord(a)+"L"+coord(data.elbow)+"L"+coord(data.wrist),"none",ink,width)
 +ellipse(data.elbow[0],data.elbow[1],2.6,2.6,skin,ink,1.2)
 +ellipse(data.wrist[0],data.wrist[1],4.2,4.2,skin,ink,1.8);
 return Object.assign({svg},data);
}
function legs(x,y,t,type){
 const lift=type==="girl"?13*Math.sin(PI*clamp((t-6.25)/1.6)):0;
 const step=smooth((t-6.25)/1.6);
 // World-anchored left foot prevents the classic cutout-slide artifact.
 const leftFoot=type==="girl"?[50,558]:[229,558];
 const rightFoot=type==="girl"?[124+12*step,558-Math.max(0,lift)]:[303,558];
 const left=limb([x-9,y+124],leftFoot,54,59,1,4.4);
 const right=limb([x+9,y+124],rightFoot,54,59,-1,4.4);
 return {svg:left.svg+right.svg
 +path("M"+(leftFoot[0]-6)+" "+(leftFoot[1]+1)+"h13","none",ink,4)
 +path("M"+(rightFoot[0]-6)+" "+(rightFoot[1]+1)+"h13","none",ink,4),
 feet:[leftFoot,rightFoot],knees:[left.elbow,right.elbow],
 error:Math.max(left.error,right.error)};
}
function girlPose(t,state={}){
 const reach=clamp(state.reach||0),shock=clamp(state.shock||0);
 const x=87+11.5*smooth((t-6.2)/1.55)+shock*1.3*Math.sin(t*31);
 const y=352+.6*Math.sin(t*2.8);
 const body=legs(x,y,t,"girl");
 const dress=path("M"+(x-12)+" "+(y+38)+"Q"+x+" "+(y+45)+" "+(x+12)+" "+(y+38)
  +"L"+(x+16)+" "+(y+122)+"Q"+x+" "+(y+134)+" "+(x-17)+" "+(y+119)+"Z","#8782aa",ink,3);
 const left=limb([x-14,y+51],[x-33,y+105],37,34,-1,4.6);
 const contact=[201,397];
 const wrist=[mix(x+19,contact[0],smooth(reach)),mix(y+107,contact[1],smooth(reach))];
 const right=limb([x+14,y+50],wrist,56,52,1,4.9);
 const pinch=smooth((reach-.7)/.26);
 const fingers=pinch?ellipse(wrist[0]+2,wrist[1]-2,3.2,2.6,skin,ink,1.4)
    +path("M"+(wrist[0]+3)+" "+(wrist[1]-3)+"q8 -5 13 -3","none",ink,2):"";
 return {x,y,svg:body.svg+dress+left.svg+right.svg+fingers,
    wrist,contact,armError:right.error,knees:body.knees,feet:body.feet,
    legError:body.error,pinch};
}
function boyPose(t,state={}){
 const laugh=clamp(state.laugh||0);
 const x=266+1.2*laugh*Math.sin(t*14),y=356+2*Math.sin(t*2)+2.5*laugh*Math.sin(t*19);
 const body=legs(x,y,t,"boy");
 const shirt=path("M"+(x-10)+" "+(y+38)+"Q"+x+" "+(y+43)+" "+(x+12)+" "+(y+38)
  +"L"+(x+17)+" "+(y+125)+"L"+(x-15)+" "+(y+126)+"Z","#777292",ink,3);
 const release=smooth((laugh-.18)/.6);
 const contact=[232,399];
 const leftWrist=[mix(contact[0],x-50,release),mix(contact[1],y+12,release)];
 const rightWrist=[mix(x+28,x+47,release),mix(y+75,y+8,release)];
 const left=limb([x-12,y+50],leftWrist,34,32,-1,4.8);
 const right=limb([x+13,y+50],rightWrist,41,33,1,4.7);
 const fingers=release<.6?path("M"+(leftWrist[0]-4)+" "+(leftWrist[1]-2)+"q-4 -6 -8 -1","none",ink,2.2):"";
 return {x,y,svg:body.svg+shirt+left.svg+right.svg+fingers,
   wrist:leftWrist,contact,armError:left.error,feet:body.feet,
   knees:body.knees,legError:body.error};
}
function inspect(){
 return [0,5.5,6.4,7.2,8,9.6,11.7,13.7].map(t=>{
  const reach=smooth((t-6)/3),laugh=smooth((t-11.4)/2.6);
  const g=girlPose(t,{reach,shock:t>9.15?.7:0}),b=boyPose(t,{laugh});
  return {t,girl_hand_error:+g.armError.toFixed(3),boy_hand_error:+b.armError.toFixed(3),
    leg_error:Math.max(g.legError,b.legError),
    girl_left_foot_y:g.feet[0][1],girl_right_foot_y:g.feet[1][1],
    girl_knee:g.knees.map(k=>k.map(n=>+n.toFixed(1)))};
 });
}
module.exports={solveTwoBone,limb,legs,girlPose,boyPose,inspect};
