const fs=require('fs'), M=require('matter-js');
const p=JSON.parse(fs.readFileSync(process.argv[2]));
const e=M.Engine.create();e.gravity.y=0.72;
const dropping=p.move==='drop', sliding=p.move==='slide';
const y=dropping?36:sliding?449:338,x=dropping?201:20;
const opts={restitution:sliding?.08:.72,friction:.025,frictionAir:.003};
const obj=p.prop==='parcel'?M.Bodies.rectangle(x,y,33,27,opts):M.Bodies.circle(x,y,17,opts);
M.Composite.add(e.world,[M.Bodies.rectangle(180,485,620,20,{isStatic:true}),M.Bodies.rectangle(359,340,12,290,{isStatic:true}),M.Bodies.rectangle(-12,340,12,290,{isStatic:true}),obj]);
let rows=[],hits=[];
M.Events.on(e,'collisionStart',()=>hits.push(rows.length));
for(let i=0;i<240;i++){
 if(i===48){M.Body.setVelocity(obj,{x:dropping?1.2:sliding?6:4.8,y:dropping?0:sliding?0:-2});M.Body.setAngularVelocity(obj,sliding?.03:.06)}
 if(i>=48)for(let j=0;j<5;j++)M.Engine.update(e,1000/120);
 rows.push([obj.position.x,obj.position.y,obj.angle]);
}
const distances=rows.map(([x,y],i)=>i<48||i>130?1e6:Math.hypot(x-192,y-(dropping?332:438)));
const cue=distances.indexOf(Math.min(...distances));
fs.writeFileSync(process.argv[3],JSON.stringify({rows,hits,cue}));
