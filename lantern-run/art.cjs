const pi=Math.PI,S=Math.sin,C=Math.cos;
const ink='#29263b',skin='#dca984',light='#f3c29c',dark='#a76c60',teal='#448b87',navy='#384358',gold='#f2bf68';
const svg=(d,fill,stroke='none',w=2)=>`<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"/>`;
const oval=(x,y,a,b,fill)=>`<ellipse cx="${x}" cy="${y}" rx="${a}" ry="${b}" fill="${fill}"/>`;
const group=(tr,s)=>`<g transform="${tr}">${s}</g>`;
const move=(x,y,s)=>group(`translate(${x} ${y})`,s);
const clamp=x=>Math.max(0,Math.min(1,x)),mix=(a,b,u)=>a+(b-a)*u;
function ease(u){u=clamp(u);return u*u*(3-2*u)}
function k(t,keys){let a=keys[0];for(let b of keys.slice(1)){if(t<b[0])return mix(a[1],b[1],ease((t-a[0])/(b[0]-a[0])));a=b}return a[1]}
function ik(a,b,l,m,bend){
 const dx=b[0]-a[0],dy=b[1]-a[1],dist=Math.hypot(dx,dy)||.01;
 const d=Math.max(Math.abs(l-m)+.01,Math.min(l+m-.01,dist));
 const along=(l*l-m*m+d*d)/(2*d),h=Math.sqrt(Math.max(0,l*l-along*along));
 return [a[0]+(along*dx-h*dy*bend)/dist,a[1]+(along*dy+h*dx*bend)/dist];
}
function segment(a,b,r,q,fill){
 const angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/pi,L=Math.hypot(b[1]-a[1],b[0]-a[0]);
 return group(`translate(${a}) rotate(${angle})`,svg(`M0 ${-r} Q${L*.48} ${-r*.98} ${L} ${-q} Q${L+q} 0 ${L} ${q} Q${L*.35} ${r*.92} 0 ${r} Q${-r*.85} 0 0 ${-r}Z`,fill,ink,1.8))
}
const defs='<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#515479"/><stop offset=".5" stop-color="#cd9191"/><stop offset="1" stop-color="#f6c898"/></linearGradient><radialGradient id="glow"><stop stop-color="#fff8a9" stop-opacity=".85"/><stop offset="1" stop-color="#ffe293" stop-opacity="0"/></radialGradient><linearGradient id="paper"><stop stop-color="#e88650"/><stop offset=".44" stop-color="#ffe19b"/><stop offset="1" stop-color="#ef9b58"/></linearGradient></defs>';
function lantern(x,y,s,angle,on,t){
 let body=svg('M-17 -18Q0 -28 17 -18Q25 0 17 18Q0 25 -17 18Q-24 0 -17 -18Z',on>.35?'url(#paper)':'#9e7874',ink,2);
 for(const n of [-12,-5,5,12])body+=svg(`M${n*.8} -19 Q${n*1.7} 0 ${n*.8} 19`,'none','#b97759',1);
 return group(`translate(${x} ${y}) rotate(${angle}) scale(${s})`,`<g opacity="${on}">${oval(0,0,51,51,'url(#glow)')}</g>`+svg('M-8 -21Q0 -41 8 -21','none',ink,2)+body+svg('M-15 -21H15L16 -17H-16Z M-16 17H16L13 22H-13Z','#534152',ink,1.5)+svg(`M0 22q${S(t*4)*3} 7 1 13`,'none','#975745',2)+oval(1,36,2.7,5,'#b24f46'))
}
function scene(t,s,amp){
 const r=s.release,c=s.catch,g=s.relight, keys=(...p)=>k(t,p);
 const X=keys([0,200],[r,200],[r+1,211],[c-1.3,242],[c,258],[c+2,260]);
 const crouch=keys([0,0],[r+.4,0],[c-1.4,15],[c,26],[c+.35,30],[c+2.3,0],[g-1,3],[g,0]);
 const lean=keys([0,0],[r,0],[c-1,9],[c,12],[c+2,1],[g-1,9],[g,0]);
 const hip=[X,217+crouch],sh=[X+lean,167+crouch],head=[sh[0]+2,sh[1]-22];
 const step=(a,b,start,end,dy)=>[mix(a,b,ease((t-start)/(end-start))),281-dy*S(pi*clamp((t-start)/(end-start)))];
 const feet=[step(185,241,r+1.6,c-.16,15),step(216,278,r+.2,c-1.45,20)];
 const legs=feet.map((foot,i)=>{let h=[hip[0]+(i?7:-7),hip[1]],ank=[foot[0],foot[1]-6],kne=ik(h,ank,30,32,-1);
 return segment(h,kne,9,7,i?'#57617a':navy)+segment(kne,ank,7.4,5,i?'#677087':'#485269')+move(...foot,svg('M-6 -9Q1 -11 6 -7L10 -4Q18 -3 16 1H-7Z','#523e48',ink,2)+svg('M-6 1H15','none','#d9ad86',2))}).join('');
 const loc=[keys([0,408],[r,408],[r+1.35,380],[c-1.4,352],[c,293],[c+.35,292],[c+2.3,289],[g-1,289],[g,300]),
 keys([0,105],[r,105],[r+1.35,132],[c-1.4,161],[c,214],[c+.35,222],[c+2.3,192],[g-1,187],[g,195])];
 const ang=keys([0,0],[r,-5],[r+1.1,36],[c-1.1,-25],[c,0],[c+.3,5],[c+1.3,0])+2*S(t*2)*(1-ease((t-c+.5)/.5));
 const lit=keys([0,.8],[c,.8],[c+.65,.04],[g-.12,.04],[g+.18,1],[g+1,.85]);
 const catchMix=ease((t-(c-.85))/.85),anticip=ease((t-r)/2);
 const palms=[0,1].map(i=>{let a=[sh[0]+(i?11:-11),sh[1]+2],side=i?1:-1;
 let loose=[a[0]+side*8+anticip*(i?27:18),a[1]+41-anticip*29+2*S(t*2+i)];
 let target=[loc[0]+(i?12:-13),loc[1]+6];return [mix(loose[0],target[0],catchMix),mix(loose[1],target[1],catchMix)]});
 function arm(i){const a=[sh[0]+(i?11:-11),sh[1]+2],b=palms[i],e=ik(a,b,28,30,i?1:-1);
 return segment(a,e,7.4,5,i?teal:'#36706f')+segment(e,b,4.8,3.2,i?light:skin)+oval(...b,4.4,3.8,skin)}
 const torso=svg(`M${sh[0]-13} ${sh[1]-3} Q${sh[0]-20} ${sh[1]+6} ${hip[0]-12} ${hip[1]-4} L${hip[0]-15} ${hip[1]+5} Q${hip[0]} ${hip[1]+10} ${hip[0]+14} ${hip[1]+5} L${hip[0]+11} ${hip[1]-8} Q${sh[0]+23} ${sh[1]+6} ${sh[0]+12} ${sh[1]-3}Z`,teal,ink,2.2)+svg(`M${sh[0]-8} ${sh[1]} l9 11 8 -11`,'#eedcb5',ink,1.4)+svg(`M${sh[0]+10} ${sh[1]+2} L${hip[0]-7} ${hip[1]+2}`,'none','#634952',4);
 const blink=1-.93*Math.pow(Math.max(0,C(t*2.14+.9)),66), gaze=t<c?2:.6;
 let face=oval(-13,-7,11,12,ink)+oval(-18,-14,8,8,'#393043')+svg('M-15 -7Q-16 -22 0 -23Q16 -23 17 -7L19 0L16 7Q13 16 3 19Q-10 17 -14 6Z',skin,ink,1.9)+svg('M-15 -6Q-21 -24 -4 -27Q12 -32 21 -16L15 -8L12 -15Q7 -9 0 -8L2 -14Q-4 -6 -10 -4L-11 3Z','#3a3246',ink,1.8)+svg('M-17 -21Q-5 -29 8 -25','none','#c87d64',2.4);
 for(let ex of [-3,10])face+=oval(ex,0,3.6,3.6*blink,'#fff0d9')+oval(ex+gaze,.3,1.9,2.8*blink,ink)+svg(`M${ex-3} -6q3 -2 6 -1`,'none',ink,1.5);
 face+=svg('M7 4l2 2 -3 1','none',dark,1)+svg(`M2 11 Q7 ${9-amp*3} 12 10 Q7 ${12+amp*8} 2 11Z`,amp>.12?'#673d4c':dark,ink,1);
 const hero=legs+arm(0)+torso+move(...head,face);
 const cam=keys([0,0],[r,1],[c,23],[c+2,23],[g,19],[g+3,6]);
 const zoom=keys([0,1],[r,1.06],[c,1.23],[g,1.23],[g+3,1.02]);
 const layer=(k,content)=>group(`translate(300 200) scale(${1+(zoom-1)*k}) translate(${-300-cam*k} -200)`,content);
 let sky=svg('M-90 -90H740V420H-90Z','url(#sky)')+oval(484,69,26,26,'#fbe6bb');
 for(let i=0;i<33;i++)sky+=oval((i*151)%680,(i*29)%108,1,1,'#fbe6c4');
 let hills='';
 for(let j=0;j<3;j++){let line='M-100 380';for(let x=-100;x<800;x+=8)line+=` L${x} ${142+j*28+19*S(x/62+2*j)+14*C(x/41+j)}`;hills+=svg(line+' L800 400Z',['#a7939c','#79848f','#556e79'][j])}
 let town='';
 for(let i=-1;i<14;i++){let x=i*58,y=206+12*S(i*8);town+=svg(`M${x} ${y}h41v48h-41Z`,'#82696d')+svg(`M${x-6} ${y+3}l23 -15 31 15Z`,'#4c515e');for(let n=0;n<3;n++)town+=svg(`M${x+6+n*11} ${y+13}h5v9h-5Z`,'#e2ad83')}
 let deck=svg('M-80 269Q230 262 720 272V405H-80Z','#ab8a80')+svg('M-100 291L760 284V292L-100 303Z','#886f71');
 for(let i=-2;i<13;i++)deck+=svg(`M${i*73} 365l68 -84`,'none','#967a77',1.2);
 let chain=svg('M-40 64Q310 152 700 51','none','#403944',2);
 for(let i=0;i<9;i++){let x=15+i*71,y=69+42*S(pi*x/675);if(i!==5)chain+=lantern(x,y+13,.45,.06*S(t+i)*60,.15+.83*ease((t-g-.16*i)/.45),t)}
 chain+=svg(t<r?'M402 102L408 81':'M402 102q5 5 6 8','none','#504555',1.4);
 let fx='';for(let i=0;i<18;i++){let x=(i*131+34*t+10*S(t+i))%700-30,y=158+57*S(i+t*.5);fx+=oval(x,y,.7+i%2,.7,'#f0cfad')}
 return layer(.18,sky)+layer(.35,hills)+layer(.55,town)+layer(.72,chain)+layer(1,deck+oval(X,283,35,4,'#897174')+hero+lantern(...loc,.72,ang,lit,t)+arm(1)+fx)
}
function frame(t,story,amp){return '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 640 360">'+defs+scene(t,story,amp)+'</svg>'}
module.exports={frame};
