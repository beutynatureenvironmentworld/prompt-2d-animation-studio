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
 let start=0,shot=story.shots.at(-1);
 for(const s of story.shots){shot=s;if(t<start+s.seconds)break;start+=s.seconds}
 const u=ease((t-start)/shot.seconds),v=(k)=>mix(...shot[k],u),camera=shot.camera;
 const dx=mix(camera[0],camera[3],u),dy=mix(camera[1],camera[4],u),zoom=mix(camera[2],camera[5],u);
 const cap=v('capture'),burst=ease((v('burst')-.45)/.38),shock=ease((v('surprise')-.45)/.25);
 const breathe=Math.sin(t*3),blink=(q)=>1-.92*Math.pow(Math.max(0,Math.cos((t+q)*2.2)),70);
 const depth=(k,s)=>flat?s:G(`translate(180 320) scale(${1+(zoom-1)*k}) translate(${-180+dx*k} ${-320+dy*k})`,s);
 let room=P('M-80 -80H440V720H-80Z','url(#wall)','none');
 room+=P('M-80 483 L440 404 V720 H-80Z','#39374f','none');
 room+=P('M-20 465 L380 414','none','#6e6589',5);
 for(let i=0;i<10;i++)room+=P(`M${i*79-120} 700l210 -269`,'none','#474359',1.5);
 room+=P('M225 50L325 39V208L225 206Z','#35354f',ink,5)+P('M233 57L317 50V198L233 197Z','#7b90bb',ink,2);
 room+=E(295,92,20,21,'#ffefc6')+E(304,84,20,21,'#7b90bb');
 for(let i=0;i<14;i++)room+=star(238+(i*32)%74,64+(i*29)%117,1+i%2,'#f9eed5');
 room+=P('M270 54V198 M230 131L320 128','none',ink,4)+P('M220 206L327 202L334 209L221 216Z','#a39bb5');
 room+=P('M36 97L97 103L92 152L31 145Z','#6d5469')+P('M42 105L90 110L86 143L38 139Z','#d1adc0');
 for(let i=0;i<3;i++)room+=E(49+i*14,122+i%2*5,5,6,'#65536f')+P(`M${43+i*14} 136q4 -15 11 0`,'#65536f','none');
 let beam=`<g opacity="${.1*v('light')}">${P('M233 57L319 50L381 360L17 551L-25 479Z','#dbdafa','none')}</g>`;
 let far=P('M152 317Q239 290 320 305L354 418L175 445Z','#51465f')+P('M161 326Q217 309 251 317L271 342L182 355Z','#b4adcd')+P('M162 352L346 330L376 400L187 435Z','url(#quilt)');
 const sx=239,sy=302-breathe*2;
 let sleeper=G(`translate(${sx} ${sy}) rotate(-13)`,E(0,0,32,31,ink)+E(0,0,29,28,ivory)+P(shock>.55?'M-18 -6q5 -8 10 -2 M6 -8q6 -7 11 0':'M-18 -6q5 7 11 0 M5 -7q5 6 10 -1','none',ink,2.8)+E(1,8,shock>.55?4:8,shock>.55?3:8+breathe*2,ink)+E(1,12,4,1.4,'#ce8495'));
 far+=sleeper+P('M246 324Q280 298 329 325L350 343L309 354Q283 331 257 339Z','#9793bb')+P('M251 334Q287 315 321 346','none','#615d83',2.3);
 let bed=P('M-24 404Q50 385 111 405L113 475L-22 490Z','#584961')+P('M-18 451Q47 423 98 435L127 464L34 492Z','#aaa4c6')+P('M-35 483L110 450L178 531L21 584L-32 563Z','url(#quilt)')+P('M-30 554L18 573L177 524L177 548L20 604L-31 580Z','#55465c')+P('M10 581L23 584L24 634L13 637Z M159 543L169 540L171 578L161 580Z','#5b4960');
 const ax=76,ay=405+1.3*Math.sin(t*2)-shock*5;
 let actor=P(`M49 499 Q57 453 ${ax} ${ay+20} M68 451Q49 457 39 475`,'none',ink,5);
 actor+=G(`translate(${ax} ${ay}) rotate(${-5+shock*8})`,P('M-34 -11Q-33 -44 -7 -42Q20 -38 32 -17L15 -15Q-14 -22 -31 8L-41 23Z','#8985b0')+E(-41,24,5,6,lilac)+E(0,0,35,34,ink)+E(0,0,32,31,ivory)+P('M-32 -15Q-14 -36 20 -26L28 -18Q-6 -24 -31 -6Z','#9995c1')+
 G(`scale(1 ${blink(.2)})`,P(shock>.5?'M-16 -4q7 -11 14 -2 M7 -5q7 -11 13 -3':'M-17 -4l15 3 M6 -2l15 -6','none',ink,3.3)+E(-5,2,2.4,3,ink)+E(17,-1,2.4,3,ink))+
 P(cap>.75&&shock<.5?'M-6 13q8 8 17 -2':'M-7 16q9 -6 18 -3','none',ink,2.5));
 const jitter=burst*3*Math.sin(t*38);const jx=146+jitter,jy=435-v('jar'); 
 actor+=P(`M69 453 Q101 478 ${jx-9} ${jy+17}`,'none',ink,5);
 let jar=G(`translate(${jx} ${jy}) rotate(${jitter})`,P('M-12 -15L12 -15L12 -9Q19 -5 18 4L17 25Q15 31 0 32Q-18 31 -18 25L-18 1Q-17 -6 -12 -9Z','url(#glass)',ink,2.7)+P('M-12 3L-12 19','none','#d3e8ef',2)+P('M-9 26Q-2 29 8 26','none','#c3dae3',1.4));
 jar+=G(`translate(${jx+mix(23,0,v('lid'))} ${jy-17-(1-v('lid'))*24-burst*(7+4*Math.sin(t*14))}) rotate(${mix(32,0,v('lid'))+jitter*2})`,P('M-15 -4Q0 -7 16 -4L16 2Q0 6 -15 2Z','#d1a26f'));
 let letters='';
 for(let i=0;i<3;i++){let phase=(t*.44+i/3)%1;let a=Math.sin(phase*Math.PI)*(1-cap);
 letters+=`<g opacity="${a}">${zed(245+phase*51,280-phase*65,0.42+phase*.6,-14+phase*10,'#f5deb7')}</g>`}
 if(cap>.01)letters+=zed(mix(264,jx,cap),mix(247,jy+12,cap)-47*Math.sin(cap*Math.PI),.69,-8,'#ffe4a0');
 if(burst>.01)letters+=`<g opacity="${burst}">${[0,1,2].map(i=>zed(jx+13+i*29,jy-46-i*21+3*Math.sin(t*7+i),.85+i*.28,-12,'#ffde99')).join('')}</g>`;
 return [depth(.25,room),depth(.45,beam),depth(.66,far),depth(.98,bed+actor+jar),depth(.98,letters)];
}
function svg(story,t,layer,flat=false){const parts=at(story,t,flat);return '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 360 640">'+defs+(layer===undefined?parts.join(''):parts[layer])+'</svg>'}
module.exports={svg};
