const clamp=x=>Math.max(0,Math.min(1,x)), ease=x=>clamp(x)**2*(3-2*clamp(x));
const mix=(a,b,t)=>a+(b-a)*t;
const ink='#211b36', ivory='#f7e6cf', lilac='#aea4ce';
const defs='<defs><linearGradient id="wall" x2=".85" y2="1"><stop stop-color="#232444"/><stop offset=".57" stop-color="#514d76"/><stop offset="1" stop-color="#787198"/></linearGradient><linearGradient id="quilt" x2="0" y2="1"><stop stop-color="#8683b2"/><stop offset="1" stop-color="#44425f"/></linearGradient><linearGradient id="glass" x2="1" y2=".3"><stop stop-color="#d1f9ef" stop-opacity=".46"/><stop offset=".45" stop-color="#8399c6" stop-opacity=".14"/><stop offset="1" stop-color="#c2fcf2" stop-opacity=".55"/></linearGradient></defs>';
const P=(d,fill='none',stroke=ink,w=2.8)=>`<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"/>`;
const E=(x,y,rx,ry,color)=>`<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${color}"/>`;
const G=(tr,s)=>`<g transform="${tr}">${s}</g>`;
function star(x,y,r,c){return G(`translate(${x} ${y}) scale(${r})`,P('M0 -1 Q.1 -.12 1 0 Q.12 .1 0 1 Q-.1 .12 -1 0 Q-.12 -.1 0 -1Z',c,'none'))}
function zed(x,y,scale,rot,color){return G(`translate(${x} ${y}) rotate(${rot}) scale(${scale})`,P('M-9 -6 Q0 -8 9 -8 L-7 7 Q1 5 10 6','none',ink,5)+P('M-9 -6 Q0 -8 9 -8 L-7 7 Q1 5 10 6','none',color,2.7))}

function at(story,t,flat=false){
  let begin=0,shot=story.shots[story.shots.length-1];
  for(const s of story.shots){shot=s;if(t<begin+s.seconds)break;begin+=s.seconds}
  const u=ease((t-begin)/shot.seconds);
  const v=(k)=>mix(shot[k][0],shot[k][1],u);
  const c=shot.camera;
  const dx=mix(c[0],c[3],u),dy=mix(c[1],c[4],u),zoom=mix(c[2],c[5],u);
  const first=v('first'),turn=v('turn'),reach=v('reach'),squeeze=v('squeeze');
  const backfire=v('backfire'),laugh=v('laugh');
  const shock=ease((backfire-.10)/.20);
  const blink=(phase)=>1-.96*Math.pow(Math.max(0,Math.cos((t+phase)*2.48)),78);
  const wobble=backfire*(2.5*Math.sin(t*42))+laugh*.75*Math.sin(t*21);
  const depth=(k,s)=>flat?s:G('translate(180 320) scale('+(1+(zoom-1)*k)+') translate('+(-180+dx*k)+' '+(-320+dy*k)+')',s);
  let room=P('M-80 -80H440V720H-80Z','url(#wall)','none');
  room+=P('M-80 483L440 404V720H-80Z','#39374f','none');
  room+=P('M-20 465L380 414','none','#6e6589',5);
  for(let i=0;i<10;i++)room+=P('M'+(i*79-120)+' 700l210 -269','none','#474359',1.5);
  room+=P('M225 50L325 39V208L225 206Z','#35354f',ink,5);
  room+=P('M233 57L317 50V198L233 197Z','#7b90bb',ink,2);
  room+=E(295,92,20,21,'#ffefc6')+E(304,84,20,21,'#7b90bb');
  for(let i=0;i<14;i++)room+=star(238+(i*32)%74,64+(i*29)%117,1+i%2,'#f9eed5');
  room+=P('M270 54V198M230 131L320 128','none',ink,4);
  room+=P('M220 206L327 202L334 209L221 216Z','#a39bb5');
  room+=P('M36 97L97 103L92 152L31 145Z','#6d5469')+P('M42 105L90 110L86 143L38 139Z','#d1adc0');
  for(let i=0;i<3;i++)room+=E(49+i*14,122+i%2*5,5,6,'#65536f')+P('M'+(43+i*14)+' 136q4 -15 11 0','#65536f','none');
  let beam='<g opacity="'+(.095*v('light'))+'">'+P('M233 57L319 50L381 360L17 551L-25 479Z','#dbdafa','none')+'</g>';
  // Background furniture, shaded like the source film, kept separate from movable actors.
  let furniture=P('M13 453Q36 429 66 454L79 469L4 489Z','#817a9e');
  furniture+=P('M256 459L340 447L360 466L257 480Z','#625c83');
  furniture+=P('M244 475L252 478L254 560L247 565Z','#403a59');
  furniture+=P('M347 470L354 468L356 553L350 550Z','#403a59');
  furniture+=P('M127 472L236 463L249 486L119 495Z','#a19bbb',ink,3);
  furniture+=P('M131 493L137 494L141 554L135 556Z M230 483L236 485L241 553L235 557Z','#554760');

  function girlHead(emotion,wet){
    const wasShock=emotion==='shock';
    const angry=emotion==='angry';
    let s=P('M-34 -11Q-33 -44 -7 -42Q20 -38 32 -17L15 -15Q-14 -22 -31 8L-41 23Z','#8985b0');
    s+=E(-41,24,5,6,lilac);
    s+=E(0,0,35,34,ink)+E(0,0,32,31,ivory);
    s+=P('M-32 -15Q-14 -36 20 -26L28 -18Q-6 -24 -31 -6Z','#9995c1');
    if(wasShock){
      s+=P('M-15 -8q-8 -18 -3 -30 M13 -8q8 -18 4 -30','none',ink,2.7);
      s+=E(-17,-41,9,12,ink)+E(15,-41,9,12,ink);
      s+=E(-17,-41,6.5,9.5,ivory)+E(15,-41,6.5,9.5,ivory);
      s+=E(-15,-39,3,5,ink)+E(16,-39,3,5,ink);
      s+=E(1,13,7,10,ink)+E(2,18,3,1.5,'#cb829b');
    }else{
      s+=G('scale(1 '+blink(.2)+')',P('M-17 -4l15 3 M6 -2l15 -6','none',ink,3.3)+E(-5,2,2.4,3,ink)+E(17,-1,2.4,3,ink));
      if(angry)s+=P('M-11 15Q0 9 10 15','none',ink,2.7);
      else s+=P('M-7 13Q3 20 13 12','none',ink,2.5);
    }
    if(wet>.18){
      s+=P('M-25 -7Q-22 5 -25 17','none','#c9edff',3);
      s+=P('M25 3Q28 11 23 25','none','#c9edff',3);
      s+=E(-22,15,3,5,'#e0f7ff')+E(22,19,3,5,'#e4f7ff');
    }
    return s;
  }
  function boyHead(emotion){
    let s=E(0,0,32,31,ink)+E(0,0,29,28,ivory);
    if(emotion==='laugh'){
      s+=P('M-18 -3q7 -11 13 0 M6 -4q7 -10 14 0','none',ink,3);
      s+=E(1,10,13,11,ink)+E(2,17,6,2,'#c78098');
    }else if(emotion==='sly'){
      s+=G('scale(1 '+blink(1.3)+')',P('M-17 -5q6 -4 13 1 M6 -5q6 -5 14 -2','none',ink,2.8)+E(-9,-1,2.5,3.2,ink)+E(13,-1,2.5,3.2,ink));
      s+=P('M-9 13q12 11 22 -3','none',ink,3);
    }else{
      s+=P('M-18 -6q5 7 11 0 M5 -7q5 6 10 -1','none',ink,3);
      s+=E(1,8,8,8,ink)+E(1,12,4,1.4,'#ce8495');
    }
    return s;
  }

  function girl(){
    const x=87+wobble*1.2,y=352+.6*Math.sin(t*3)+shock*1.0*Math.sin(t*35);
    const wet=Math.max(first,backfire);
    const mood=shock>.2?'shock':(first>.22&&t<9.15?'angry':'sly');
    let s=P('M-12 38Q0 45 12 38L16 122Q0 134 -17 119Z','#8782aa',ink,3);
    s+=P('M-6 119Q-21 161 -38 200 M6 119Q16 161 34 200','none',ink,4.7);
    s+=P('M-38 200L-48 204 M34 200L44 204','none',ink,4.5);
    // The non-grabbing arm has continuous shoulder, elbow, wrist and hand anchors.
    s+=P('M-14 52Q-31 71 -35 102','none',ink,5);
    s+=E(-34,103,5,5,ivory);
    const p=reach,px=mix(19,112,p),py=mix(106,46,p);
    const ex=mix(44,58,p),ey=mix(76,49,p);
    s+=P('M14 50Q'+ex+' '+ey+' '+px+' '+py,'none',ink,5);
    s+=E(px,py,5.2,4.8,ivory);
    s+=G('rotate('+(-1+shock*5*Math.sin(t*32))+')',girlHead(mood,wet));
    return G('translate('+x+' '+y+')',s);
  }
  function boy(){
    const x=266,y=356+2*mathSin(t*2)+laugh*2.9*Math.sin(t*19);
    let s=P('M-10 38Q0 42 12 38L17 125L-15 126Z','#777292',ink,3);
    s+=P('M-6 125Q-21 163 -31 205 M8 124Q19 165 34 205','none',ink,4.7);
    s+=P('M-31 205L-43 209 M34 205L46 209','none',ink,4.5);
    const armSwing=laugh*.5*Math.sin(t*19);
    s+=P('M-12 50Q-38 62 -41 75','none',ink,5);
    s+=P('M-41 75Q-51 65 -50 54','none',ink,4.5);
    s+=E(-51,54,5,5,ivory);
    // Holding the sealed right-hand end at the mouth, never the exposed straw.
    s+=P('M11 49Q30 58 31 '+(48-9*armSwing),'none',ink,4.7);
    s+=E(31,47-9*armSwing,5.2,5.2,ivory);
    s+=G('rotate('+(laugh*4*Math.sin(t*18))+')',boyHead(laugh>.14?'laugh':'sly'));
    return G('translate('+x+' '+y+')',s);
  }
  function mathSin(x){return Math.sin(x)}

  function carton(){
    // Local x=-31 is the OPEN straw pointing at the GIRL. Local x=+31 is sealed.
    const r=mix(67,-9,turn);
    const crush=Math.max(squeeze,backfire);
    const scaleX=1-.15*crush, scaleY=1+.13*crush;
    let s=P('M-30 -20H29L31 20H-30Z','#e7e9f6',ink,3);
    s+=P('M-30 -20H27L30 -12H-28Z','#dbe5f3',ink,2.1);
    s+=P('M-29 -19L-12 -28L30 -20Z','#b2badb',ink,2.5);
    s+=P('M28 -20L35 -13V14L29 20Z','#a9b4d1',ink,2);
    s+=P('M-18 -2L8 -3L10 7L-18 7Z','#7b8eaf','none');
    s+=P('M-33 -11L-54 -12L-60 -15','none',ink,7);
    s+=P('M-33 -11L-54 -12L-60 -15','none','#e8faff',3.4);
    s+=E(-59,-15,2,2,ink);
    s+=P('M29 -14L32 13','none','#e6ebf2',2);
    return G('translate(201 396) rotate('+r+') scale('+scaleX+' '+scaleY+')',s);
  }

  function spray(intensity,fromFirst=false){
    if(intensity<.02)return '';
    // Both sprays leave the LEFT-facing hole and go LEFT to the girl's face.
    const opacity=Math.min(1,intensity*3);
    const tip=fromFirst?mix(130,90,intensity):mix(154,88,intensity);
    const ty=fromFirst?mix(391,348,intensity):mix(383,347,intensity);
    const x0=fromFirst?155:149, y0=fromFirst?402:391;
    let s='<g opacity="'+opacity+'">';
    s+=P('M'+x0+' '+y0+'Q118 '+(350-15*Math.sin(t*19))+' '+tip+' '+ty,'none','#b6d7e9',12);
    s+=P('M'+x0+' '+y0+'Q118 '+(350-15*Math.sin(t*19))+' '+tip+' '+ty,'none','#f8fbff',8);
    for(let i=0;i<15;i++){
      const f=((i*0.6180339+t*1.7)%1),ang=i*2.4+t*2.1;
      const xx=tip-5+Math.sin(ang)*(4+f*20), yy=ty+Math.cos(ang)*(7+f*30);
      s+=E(xx,yy,1.8+f*2.6,2+f*3.5,'#e8f8ff');
    }
    s+='</g>';return s;
  }

  let water='';
  const initialBurst=(t>.66&&t<1.92)?Math.min(1,ease((t-.67)/.23))*(1-ease((t-1.48)/.36)):0;
  const reverseBurst=(t>9.10&&t<11.15)?Math.min(1,ease((t-9.12)/.26))*(1-ease((t-10.5)/.55)):0;
  if(initialBurst>0)water+=spray(initialBurst,true);
  if(reverseBurst>0)water+=spray(reverseBurst,false);
  if(backfire>.12){
    const w=Math.min(1,backfire);
    water+=P('M60 315q-14 -13 -21 -28 M95 315q16 -11 23 -29','none','#ffdeb4',2.6*w);
    water+=zed(42,282-8*Math.sin(t*11),.3,-8,'#ffe6b2');
  }
  if(laugh>.2){
    water+=P('M276 310q14 -9 25 0','none','#f2d0e6',2.2);
    water+=P('M279 302l5 -10 M290 301l8 -10','none','#f6d2dc',2);
  }
  // Keep visual layers faithful to original multilayer midnight-jar renderer.
  let actors=girl()+boy()+carton();
  return [
    depth(.25,room),
    depth(.45,beam),
    depth(.75,furniture),
    depth(.96,actors),
    depth(.98,water)
  ];
}
function svg(story,t,layer,flat=false){const parts=at(story,t,flat);return '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 360 640">'+defs+(layer===undefined?parts.join(''):parts[layer])+'</svg>'}
module.exports={svg};
