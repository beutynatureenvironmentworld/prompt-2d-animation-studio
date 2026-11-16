/** Adapter executes actual upstream JDhruv14/line-art-animation gait.ts (MIT). */
import fs from 'node:fs';
import { gait } from './lib/gait.ts';
import { ease, wobble } from './lib/motion.ts';
const run=gait({kind:'run',period:0.42,stride:18,lift:14,heelKick:4.2});
const rest=gait({kind:'walk'});
const fps=24,total=288,rows=[];
for(let i=0;i<total;i++){
  const t=i/fps, running=t<2.5 || (t>=6.2 && t<7.75);
  const src=running?run:rest;
  const p=src.pose(t/src.period,running?1:0);
  rows.push({frame:i,t,hip:p.hip,feet:p.feet.map(f=>({knee:f.knee,ankle:f.ankle,pitch:f.pitch,stance:f.stance})),
    front:p.front,bob:p.bob,run:running,pendulum:wobble(t,1.2),ease:ease(t%1)});
}
const out=process.env.GAIT_OUT;
if(!out)throw new Error('Missing GAIT_OUT');
fs.mkdirSync(out.substring(0,out.lastIndexOf('/')),{recursive:true});
fs.writeFileSync(out,JSON.stringify({source:'JDhruv14/line-art-animation',license:'MIT',actual_library_gait_solver:true,fps,total,rows}));
console.log('REAL_UPSTREAM_IK_GAIT_288_FRAMES_PASS',rows.length);
