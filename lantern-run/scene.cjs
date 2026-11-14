const fs=require('node:fs');
const story=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const fps=Number(process.argv[3]||24);
const voice=JSON.parse(fs.readFileSync(process.env.LANTERN_VOICE,'utf8'));
const {frame}=require('./art.cjs');
for(let n=0;n<Math.round(fps*story.seconds);n++)console.log(frame(n/fps,story,voice[n]||0));
