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
/**
 * Invisible two-bone IK: calculate reachable wrist and knee positions internally,
 * but show ONE smooth, thick, continuous stroke, never elbow/knee circles or V joints.
 * The midpoint is a C1-continuous quadratic Bezier. Curvature is close to zero
 * except during purposeful reaching/stepping, then only a subtle bow is allowed.
 */
function limb(a,target,l1,l2,side=1,width=5.4,bend=.02){
 const data=solveTwoBone(a,target,l1,l2,side);
 const [x0,y0]=a,[x1,y1]=data.wrist;
 let dx=x1-x0,dy=y1-y0;
 const len=Math.max(0.001,Math.hypot(dx,dy));
 const ux=dx/len,uy=dy/len;
 const mx=(x0+x1)/2,my=(y0+y1)/2;
 // Analytic IK is an INTERNAL controller only: no skeleton edges are rendered.
 // Limit perpendicular silhouette deviation to 1px at rest, 5-7px in actions.
 const fromElbow=(data.elbow[0]-mx)*(-uy)+(data.elbow[1]-my)*ux;
 const wanted=fromElbow*clamp(bend,0,.30);
 const maxCurve=clamp(len*.09,1.8,7.2);
 const curve=clamp(wanted,-maxCurve,maxCurve);
 const cx=mx-uy*curve,cy=my+ux*curve;
 const svg=path('M'+coord(a)+'Q'+coord([cx,cy])+' '+coord(data.wrist),'none',ink,width);
 return Object.assign({svg,curve,control:[cx,cy]},data);
}
function legs(x,y,t,type){
 const lift=type==="girl"?13*Math.sin(PI*clamp((t-6.25)/1.6)):0;
 const step=smooth((t-6.25)/1.6);
 // World-anchored left foot prevents the classic cutout-slide artifact.
 const leftFoot=type==="girl"?[50,558]:[229,558];
 const rightFoot=type==="girl"?[124+12*step,558-Math.max(0,lift)]:[303,558];
 const left=limb([x-9,y+124],leftFoot,54,59,1,5.4,.018);
 const right=limb([x+9,y+124],rightFoot,54,59,-1,5.4,type==="girl" ? .05+.11*Math.sin(PI*clamp((t-6.25)/1.6)) : .022);
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
 const left=limb([x-14,y+51],[x-33,y+105],37,34,-1,5.4,.018);
 const contact=[201,397];
 const wrist=[mix(x+19,contact[0],smooth(reach)),mix(y+107,contact[1],smooth(reach))];
 const right=limb([x+14,y+50],wrist,56,52,1,5.7,.02+.16*Math.sin(Math.PI*clamp(reach)));
 const pinch=smooth((reach-.7)/.26);
 // Only draw a tiny contact contour when gripping; no ball-shaped wrist marker.
 const fingers=pinch>.3?path("M"+(wrist[0]-1)+" "+(wrist[1]-2)+"q5 -3 9 1","none",ink,2):"";
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
 const left=limb([x-12,y+50],leftWrist,34,32,-1,5.7,.03+.12*release);
 const right=limb([x+13,y+50],rightWrist,41,33,1,5.5,.025+.12*release);
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
    girl_knee_internal_only:g.knees.map(k=>k.map(n=>+n.toFixed(1)))};
 });
}
module.exports={solveTwoBone,limb,legs,girlPose,boyPose,inspect};
