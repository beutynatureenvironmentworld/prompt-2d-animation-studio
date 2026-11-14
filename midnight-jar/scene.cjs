const fs=require('node:fs');
const path=require('node:path');
const story=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,'story.json'),'utf8'));
const duration=story.shots.reduce((s,v)=>s+v.seconds,0);
const {svg}=require('./art.cjs');
const fps=Number(process.argv[3]||24);
const layer=process.argv[4]===undefined?undefined:Number(process.argv[4]);
for(let i=0;i<Math.round(duration*fps);i++)console.log(svg(story,i/fps,layer,layer!==undefined));
