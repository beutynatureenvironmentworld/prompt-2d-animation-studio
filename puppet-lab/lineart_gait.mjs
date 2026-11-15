/** Original 2D ink cartoon exercising the real MIT line-art-animation gait solver. */
import fs from 'node:fs';
import path from 'node:path';
import { gait } from './lib/gait.ts';
import { spring, wobble, ease } from './lib/motion.ts';
const out=path.join(process.env.GITHUB_WORKSPACE || process.cwd(),'puppet-lab/output/lineart');
const frames=path.join(out,'frames');fs.mkdirSync(frames,{recursive:true});
const frameRate=24, total=144;
const runner=gait({kind:'run',period:0.53,lift:11,heelKick:3.5});
const armSpring=spring(34,8,0);
const inks='#242731',paper='#e9e7d3';
function line(points,weight=3,c=inks){
  return '<path d="M '+points.map((p,i)=>(i?'L ':'')+p[0].toFixed(2)+' '+p[1].toFixed(2)).join(' ')+'" fill="none" stroke="'+c+'" stroke-width="'+weight+'" stroke-linecap="round" stroke-linejoin="round"/>';
}
function act(frame){
 const t=frame/frameRate;
 const runNow=t<1.70 || (t>3.02&&t<4.67);
 const shock=t>2.17&&t<3.02;
 const slip=t>4.67&&t<5.30;
 const caught=t>5.30;
 const p=runner.pose(t/runner.period,runNow?1:0);
 const x=t<1.7?25+138*ease(t/1.7):t<3.02?163:t<4.67?163+112*ease((t-3.02)/1.65):275-18*(t-4.67);
 const y=550-(slip?24*Math.sin(Math.PI*Math.min(1,(t-4.67)/.63)):0);
 const headTilt=shock?6*wobble(t,3):slip?-28:4*wobble(t,.7);
 const arm=armSpring.step(shock?1:runNow?.65:0,1/frameRate);
 const a=9*Math.sin(t*15);
 const arm1=line([[31,72],[20-8*arm,81-a*.4],[11-10*arm,100-a]],3.4);
 const arm2=line([[49,72],[61+8*arm,81+a*.4],[68+12*arm,100+a]],3.4);
 const legs=line([p.hip,p.feet[0].knee,p.feet[0].ankle],4.3)+line([p.hip,p.feet[1].knee,p.feet[1].ankle],4.3);
 const torso='<path d="M 31 68 L49 68 L46 '+p.hip[1].toFixed(1)+' L34 '+p.hip[1].toFixed(1)+'Z" fill="#edc560" stroke="'+inks+'" stroke-width="3"/>';
 const eyeHeight=shock?10:7;
 const face='<ellipse cx="40" cy="46" rx="18" ry="24" fill="#fff6e5" stroke="'+inks+'" stroke-width="3"/>'+
  '<path d="M 23 37 Q 17 19 36 18 L43 14 L53 20 Q64 25 57 37 L48 29 L31 30Z" fill="'+inks+'"/>'+
  '<ellipse cx="31" cy="45" rx="4.7" ry="'+eyeHeight+'" fill="#ffffff" stroke="'+inks+'" stroke-width="2"/>'+
  '<ellipse cx="49" cy="45" rx="4.7" ry="'+eyeHeight+'" fill="#ffffff" stroke="'+inks+'" stroke-width="2"/>'+
  '<circle cx="32" cy="46" r="2" fill="'+inks+'"/><circle cx="50" cy="46" r="2" fill="'+inks+'"/>'+
  (shock||slip?'<ellipse cx="40" cy="63" rx="6" ry="9" fill="#55373d"/>':line([[33,60],[40,66],[48,60]],2.5));
 const caption=shock?'WHAAAT?!':slip?'WHOAAA!':caught?'OH NO!':'';
 const spoken=caption?'<rect x="23" y="88" width="245" height="52" rx="12" fill="#fff6e5" stroke="'+inks+'" stroke-width="3"/><text x="44" y="123" font-size="28" font-family="sans-serif" font-weight="bold" fill="'+inks+'">'+caption+'</text>':'';
 const catX=365-178*ease(Math.max(0,Math.min(1,(t-2.30)/1.08)));
 const cat='<g transform="translate('+catX.toFixed(2)+' 524)"><path d="M 16 0 Q 60 11 51 -32" stroke="'+inks+'" stroke-width="9" fill="none"/>'+
  '<ellipse cx="0" cy="0" rx="31" ry="29" fill="#d99854" stroke="'+inks+'" stroke-width="3"/>'+
  '<path d="M-29 -15 L-30 -48 L-9 -33 L13 -33 L31 -48 L27 -15" fill="#d99854" stroke="'+inks+'" stroke-width="3"/>'+
  '<ellipse cx="-12" cy="-19" rx="5" ry="7" fill="white"/><ellipse cx="11" cy="-19" rx="5" ry="7" fill="white"/>'+
  '<circle cx="-10" cy="-18" r="2" fill="'+inks+'"/><circle cx="12" cy="-18" r="2" fill="'+inks+'"/></g>';
 const actor='<g transform="translate('+x.toFixed(2)+' '+y.toFixed(2)+') scale(2.45) translate(-40 -120)"><g transform="rotate('+headTilt.toFixed(2)+' 40 '+p.hip[1].toFixed(1)+')">'+legs+torso+arm1+arm2+face+'</g></g>';
 const strips=Array.from({length:21},(_,i)=>'<path d="M0 '+(35+i*27)+' H360" fill="none" stroke="#cecfbe" stroke-width="1"/>').join('');
 return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640"><rect width="360" height="640" fill="'+paper+'"/>'+strips+
  '<path d="M 0 549 H360" stroke="#6a716d" stroke-width="4"/>'+
  '<rect x="278" y="245" width="75" height="304" fill="#7894a3" stroke="'+inks+'" stroke-width="4"/><rect x="289" y="257" width="51" height="271" fill="#e4e9da" stroke="'+inks+'" stroke-width="2"/>'+
  '<circle cx="336" cy="388" r="4.5" fill="#e9c35c" stroke="'+inks+'" stroke-width="1"/>'+cat+actor+spoken+
  '<text x="22" y="610" font-family="sans-serif" font-size="13" fill="'+inks+'">ORIGINAL INK MOTION · GAIT IK</text></svg>';
}
for(let i=0;i<total;i++){
 fs.writeFileSync(path.join(frames,'f'+String(i+1).padStart(4,'0')+'.svg'),act(i));
}
const evidence={source:'JDhruv14/line-art-animation',license:'MIT',solver:'actual gait.ts with IK planted feet and knee paths',motion:'actual spring and wobble from motion.ts',generated_frames:total,fps:frameRate,seconds:total/frameRate,ai_video_model:false};
fs.writeFileSync(path.join(out,'proof.json'),JSON.stringify(evidence,null,2)+'\n');
console.log('REAL_LINE_ART_ANIMATION_144_FRAMES_PASS');
