"""Super Test-inspired vector cartoon director (PyCairo, code-drawn on CPU).

Per-frame procedural 2-bone IK for knees/elbows, planted foot timing, dynamic
expressions, original stage sets, screen-space camera punch-ins, secondary props.
Designed for short 9:16 scenes and original mascot/cat/boy characters.
"""
import math,random
import cairo
TAU=math.tau
MONO=False
INK='#253039'; WHITE='#fffdf4'; SKIN='#f9cfad'; TEAL='#08b9aa'; DARK='#293647'; GOLD='#ffb33e'; ORANGE='#f5a02e'; BLUE='#69c3ea'; GRASS='#39bb52'; PAPER='#f3f0e9'

def color(c,h,a=1):
 if isinstance(h,str):
  if h.startswith('#'):
   s=h.lstrip('#');v=tuple(int(s[i:i+2],16)/255 for i in (0,2,4))
  else:raise ValueError('Unknown color')
 else:v=h
 if MONO:
  lum=.2126*v[0]+.7152*v[1]+.0722*v[2]
  v=(lum,lum,lum)
 c.set_source_rgba(*v,a)
def path(c,points,close=False):
 c.new_path();c.move_to(*points[0])
 for pt in points[1:]:c.line_to(*pt)
 if close:c.close_path()
def fill(c,col,edge=None,width=3):
 color(c,col)
 if edge:
  c.fill_preserve();color(c,edge);c.set_line_width(width);c.set_line_join(cairo.LINE_JOIN_ROUND);c.stroke()
 else:c.fill()
def stroke(c,col=INK,width=3):
 color(c,col);c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND);c.set_line_join(cairo.LINE_JOIN_ROUND);c.stroke()
def ln(c,points,col=INK,width=3):path(c,points);stroke(c,col,width)
def curve(c,p0,p1,p2,p3,col=INK,width=3):
 c.new_path();c.move_to(*p0);c.curve_to(*p1,*p2,*p3);stroke(c,col,width)
def rect(c,x,y,w,h,col,edge=None,width=3,radius=0):
 c.new_path()
 if radius:
  r=min(radius,w/2,h/2)
  c.arc(x+w-r,y+r,r,-math.pi/2,0);c.arc(x+w-r,y+h-r,r,0,math.pi/2)
  c.arc(x+r,y+h-r,r,math.pi/2,math.pi);c.arc(x+r,y+r,r,math.pi,3*math.pi/2);c.close_path()
 else:c.rectangle(x,y,w,h)
 fill(c,col,edge,width)
def oval(c,x,y,rx,ry,col,edge=None,width=3):
 c.save();c.translate(x,y);c.scale(max(.01,rx),max(.01,ry));c.new_path();c.arc(0,0,1,0,TAU);c.restore();fill(c,col,edge,width)
def cap(c,a,b,thick=13,col=SKIN):
 ln(c,[a,b],INK,thick+5);ln(c,[a,b],col,thick)
 for p in [a,b]:oval(c,p[0],p[1],thick/2,thick/2,col)
def clamp(v,a=0,b=1):return max(a,min(b,v))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def overshoot(x):
 x=clamp(x);return 1+2.7*(x-1)**3+1.7*(x-1)**2
def ik(h,f,upper=49,lower=51,side=1):
 dx=f[0]-h[0];dy=f[1]-h[1];dist=max(.01,math.hypot(dx,dy));d=clamp(dist,abs(upper-lower)+1,upper+lower-1)
 along=(d*d+upper*upper-lower*lower)/(2*d)
 out=math.sqrt(max(0,upper*upper-along*along))*side
 return (h[0]+(along*dx-out*dy)/dist,h[1]+(along*dy+out*dx)/dist)

def sky(c,top,bottom):
 gr=cairo.LinearGradient(0,0,0,650)
 for stop,v in [(0,top),(1,bottom)]:
  r,g,b=tuple(int(v[i:i+2],16)/255 for i in (1,3,5))
  if MONO:r=g=b=.2126*r+.7152*g+.0722*b
  gr.add_color_stop_rgb(stop,r,g,b)
 c.rectangle(0,0,480,854);c.set_source(gr);c.fill()
def cloud(c,x,y,s=1):
 c.save();c.translate(x,y);c.scale(s,s)
 for dx,dy,rx,ry in [(-34,0,25,12),(-13,-10,27,18),(15,-5,34,17),(42,2,25,10)]:oval(c,dx,dy,rx,ry,WHITE)
 c.restore()
def backdrop(c,setting,t,mono=False):
 if mono:sky(c,'#eeeef0','#ffffff')
 elif setting in ('park','beach','forest','street','rooftop'):sky(c,'#77c9f8','#d1f0ff')
 elif setting=='space':sky(c,'#202b58','#5a4f8c')
 else:sky(c,'#f8eaca','#fff1dc')
 if setting in ('park','beach','forest','street','rooftop'):
  for i in range(5):cloud(c,35+i*116+4*math.sin(t*.15+i),90+(i%3)*48,.55+.11*(i%2))
 if setting=='space':
  for i in range(40):
   xx=(i*109+33)%470;yy=(i*37+17)%580
   oval(c,xx,yy,2 if i%7 else 3,2 if i%7 else 3,WHITE)
  oval(c,399,186,70,70,'#ffd78d')
 if setting in ('park','forest'):
  for i in range(4):
   x=28+i*145+(8*math.sin(t*.15+i));y=565-(i%2)*35
   ln(c,[(x,y+60),(x+1,y-46)],'#73533f',13)
   for xoff,yoff in [(-21,-67),(20,-69),(2,-84)]:oval(c,x+xoff,y+yoff,32,37,'#2fa575','#287e61',2)
  rect(c,0,657,480,197,'#56c75b');rect(c,0,660,480,12,'#40a64b')
  for i in range(10):
   x=(i*67+15)%480;y=685+(i%3)*40
   ln(c,[(x,y),(x+8,y-7)],'#90dd64',2)
 elif setting=='beach':
  rect(c,0,545,480,125,'#46bccc');ln(c,[(0,558),(480,558)],'#e8fbff',5)
  rect(c,0,663,480,191,'#edcf96')
  for i in range(5):oval(c,70+i*95,706+i%2*40,5,3,'#d5b783')
 elif setting=='street':
  for i in range(5):
   x=i*111-18;h=240+(i%3)*37
   rect(c,x,650-h,104,h,'#a9bed0',INK,2)
   for row in range(3):
    for colx in range(2):rect(c,x+20+colx*37,650-h+25+row*44,17,23,'#fcf0bd',INK,1)
  rect(c,0,665,480,189,'#777982');ln(c,[(0,748),(480,748)],'#ffeeaa',4)
 elif setting=='rooftop':
  for i in range(5):rect(c,i*119-25,550-(i%2)*90,117,116+(i%2)*90,'#758ca4')
  rect(c,0,667,480,187,'#c7c3ba');rect(c,0,643,480,29,'#6a7776',INK,3)
 elif setting=='space':
  rect(c,0,672,480,182,'#9091b1');oval(c,350,690,110,30,'#76769a')
 else:
  rect(c,0,670,480,184,'#dfc9ae');ln(c,[(0,668),(480,668)],'#9d998a',4)
  for i in range(9):ln(c,[(i*59,673),(i*59-36,854)],'#c5af98',1)
  if setting=='school':
   rect(c,27,210,224,163,'#345f56',INK,6,8)
   rect(c,35,379,220,12,'#b79b74',INK,3)
  elif setting=='kitchen':
   for i in range(4):rect(c,i*109+8,436,104,200,'#d8ede4',INK,3,4)
   rect(c,0,423,480,16,'#bb9c80',INK,3)
  elif setting=='bedroom':
   rect(c,18,501,230,113,'#7cb4d3',INK,4,12)
   rect(c,35,470,83,52,WHITE,INK,3,10)
  elif setting=='office':
   rect(c,25,420,240,15,'#aa8165',INK,4);rect(c,42,435,12,220,'#aa8165');rect(c,225,435,12,220,'#aa8165')
   rect(c,123,344,98,71,'#a9c8cc',INK,4,6)
  elif setting=='toilet':
   rect(c,327,310,143,359,'#afbabc',INK,6,8)
   rect(c,339,328,117,325,'#e4ede9',INK,4,4)
   rect(c,351,345,91,286,'#d3e7e1',INK,3,4)
   oval(c,439,498,7,7,GOLD,INK,2)
   rect(c,331,256,135,51,WHITE,INK,5,8)
   color(c,INK);c.select_font_face('Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(24);c.move_to(344,290);c.show_text('TOILET')
 if setting=='forest':
  for i in range(4):oval(c,i*135-10,595,63,88,'#289b63',None)

def prop(c,kind,t,actor_x):
 if kind=='none':return
 x=270;y=645
 if kind=='banana':
  c.new_path();c.move_to(x-19,y-10);c.curve_to(x+7,y+10,x+21,y-23,x+28,y-26);c.curve_to(x+10,y+31,x-23,y+11,x-19,y-10);fill(c,'#ffe259',INK,3)
 elif kind=='ball':
  px=x+42*math.sin(t*1.7);py=625-35*abs(math.sin(t*3.3))
  oval(c,px,py,23,23,'#f3c45d',INK,4);curve(c,(px-20,py),(px-5,py-16),(px+10,py-16),(px+20,py),INK,2)
 elif kind=='cookie':
  oval(c,x,y-15,24,19,'#d99357',INK,3)
  for k in range(5):oval(c,x+10*math.cos(k*1.5),y-15+8*math.sin(k*1.5),3,3,'#774431')
 elif kind=='phone':rect(c,x-15,y-80,33,58,'#c6d2dd',INK,4,5)
 elif kind=='skateboard':
  rect(c,x-55,y-25,110,14,'#dc9351',INK,4,7)
  for dx in (-33,35):oval(c,x+dx,y-6,10,10,INK)
 elif kind=='cup':
  rect(c,x-16,y-49,34,43,'#fafafa',INK,3,4);oval(c,x+21,y-31,12,15,WHITE,INK,3)
 elif kind=='paper':
  rect(c,x-18,y-45,43,41,WHITE,INK,4,6);oval(c,x+3,y-23,10,10,'#a3abac',INK,2)

def state(plan,t):
 b=plan['beats'][-1]
 for e in plan['beats']:
  if t<e['end']:b=e;break
 action=b['action'];z=clamp((t-b['start'])/(b['end']-b['start']))
 step=math.sin(TAU*t*4.5);sway=math.sin(TAU*t*2.25)
 # All 2D root positions authored to keep meaningful stage continuity.
 x={'notice':130,'anticipate':150,'sprint':135+185*ease(z),
    'jump':300+26*z,'knock':314,'point':258,'talk':260,'wave':260,
    'dodge':265-60*ease(z),'slip':300-55*ease(z),'fall':247,
    'panic':318-27*ease(z),'laugh':260,'dance':240+50*sway,
    'recover':245+25*ease(z)}[action]
 # springy anticipation, exaggerated arcs, clear foot contacts.
 y=0;tilt=0
 if action=='sprint':y=-10*abs(step);tilt=.18
 if action=='jump':y=-142*math.sin(math.pi*z);tilt=-.08
 if action=='anticipate':y=18*ease(z);tilt=.07
 if action=='dodge':y=22*ease(z);tilt=-.25
 if action=='slip':y=38*ease(z);tilt=-.65*ease(z)
 if action=='fall':y=52*ease(z);tilt=-1.25*ease(z)
 if action=='panic':y=-28*math.sin(math.pi*z);tilt=-.17
 if action=='recover':y=-5*math.sin(math.pi*z);tilt=-.05*(1-ease(z))
 if action=='laugh':y=-5*abs(math.sin(t*9));tilt=.05*math.sin(t*8)
 if action=='dance':y=-17*abs(math.sin(t*7));tilt=.16*math.sin(t*7)
 return action,z,x,570+y,tilt,step

def limbs(c,action,t,z,cat=False):
 phase=TAU*t*4.5
 for side,offset in ((-1,math.pi),(1,0)):
  cyc=math.sin(phase+offset)
  hip=(side*20,-7)
  if action=='sprint':ankle=(side*15+71*cyc,94-48*max(0,cyc))
  elif action=='jump':ankle=(side*26+20*side,72-18*math.sin(math.pi*z))
  elif action in ('slip','fall'):ankle=(side*26+60*side*z,93-22*z)
  elif action=='dance':ankle=(side*22+42*cyc,93-40*max(0,cyc))
  elif action=='dodge':ankle=(side*37,92)
  else:ankle=(side*28,93)
  knee=ik(hip,ankle,53,55,-side)
  paint=ORANGE if cat else DARK
  cap(c,hip,knee,13,paint);cap(c,knee,ankle,11,paint)
  oval(c,ankle[0]+10,ankle[1]+3,22,10,WHITE if cat else INK,INK,3)
 for side,offset in ((-1,0),(1,math.pi)):
  cyc=math.sin(phase+offset)
  shoulder=(side*32,-84)
  if action=='sprint':elbow=(side*55+14*cyc,-58+30*cyc);wrist=(side*72+24*cyc,-39+48*cyc)
  elif action=='knock' and side==1:
   v=max(0,math.sin(z*TAU*4));elbow=(65,-135);wrist=(90+17*v,-156)
  elif action in ('panic','slip','fall','jump'):
   v=7*math.sin(t*13+side);elbow=(side*(66+v),-126);wrist=(side*(90+v),-188)
  elif action=='point' and side==1:elbow=(63,-94);wrist=(104,-103)
  elif action=='wave' and side==1:elbow=(58,-133);wrist=(77+15*math.sin(t*15),-185)
  elif action=='dance':elbow=(side*(56+10*cyc),-122);wrist=(side*(80+10*cyc),-167)
  elif action=='dodge':elbow=(side*54,-69);wrist=(side*70,-37)
  else:elbow=(side*53,-70);wrist=(side*63,-36+7*math.sin(t*3))
  paint=ORANGE if cat else TEAL
  cap(c,shoulder,elbow,14,paint);cap(c,elbow,wrist,11,paint)
  oval(c,*wrist,10,10,WHITE if cat else SKIN,INK,3)

def expression(c,action,t,kind):
 blink=(t%2.31)<.08 and action not in ('panic','fall','slip')
 for side in (-1,1):
  x=side*16
  curve(c,(x-9,-187),(x-3,-196),(x+6,-197),(x+10,-189),INK,3)
  if blink:ln(c,[(x-9,-176),(x+10,-176)],INK,3)
  else:
   ry=13 if action in ('panic','fall','slip') else 9
   oval(c,x,-174,10,ry,WHITE,INK,2.5)
   oval(c,x+(3 if action=='sprint' else -1),-172,4,5,INK)
 if action in ('panic','fall','slip'):oval(c,0,-144,12,18,'#383039',INK,2)
 elif action=='talk':oval(c,0,-145,8,8+6*abs(math.sin(t*12)),'#583943',INK,2)
 elif action in ('laugh','recover'):curve(c,(-17,-148),(-8,-132),(8,-132),(17,-148),INK,4)
 elif action=='sprint':ln(c,[(-11,-148),(13,-150)],INK,3)
 else:curve(c,(-12,-146),(-3,-149),(6,-149),(13,-146),INK,2.6)

def actor(c,kind,action,t,z,tilt,step,mono=False):
 c.save();c.rotate(tilt)
 if action=='jump':c.scale(1-.075*math.sin(math.pi*z),1+.13*math.sin(math.pi*z))
 if action in ('fall','slip'):c.scale(1+.08*math.sin(math.pi*z),1-.10*math.sin(math.pi*z))
 iscat=kind=='cat'
 limbs(c,action,t,z,iscat)
 if iscat:
  curve(c,(-30,-38),(-96,-14),(-96,-104+16*math.sin(t*9)),(-120,-74+16*math.sin(t*7)),INK,17)
  curve(c,(-30,-38),(-96,-14),(-96,-104+16*math.sin(t*9)),(-120,-74+16*math.sin(t*7)),ORANGE,11)
  oval(c,0,-56,50,62,ORANGE,INK,5)
  oval(c,18,-55,23,35,WHITE)
  oval(c,0,-167,57,53,ORANGE,INK,5)
  path(c,[(-49,-181),(-54,-232),(-15,-204)],True);fill(c,ORANGE,INK,4)
  path(c,[(15,-204),(51,-234),(50,-178)],True);fill(c,ORANGE,INK,4)
  oval(c,0,-148,35,22,WHITE,INK,2)
  expression(c,action,t,kind)
  oval(c,0,-147,6,5,INK)
 elif kind=='robot':
  rect(c,-40,-111,80,104,'#b3c5cc',INK,5,10)
  rect(c,-49,-225,98,85,'#cddfe0',INK,5,10)
  for x in (-21,22):oval(c,x,-187,11,13,WHITE,INK,3);oval(c,x+2,-184,5,6,INK)
  if action in ('panic','slip'):oval(c,0,-158,9,14,INK)
  else:rect(c,-15,-162,30,5,INK,radius=2)
  ln(c,[(0,-225),(0,-240)],INK,4);oval(c,0,-244,8,8,GOLD,INK,3)
 else:
  hoodie=WHITE if mono or kind=='mascot' else TEAL
  # torso and neck fully vector; no duplicated head sprite.
  c.new_path();c.move_to(-35,-113);c.curve_to(-48,-98,-45,-29,-39,-10)
  c.curve_to(-12,5,29,5,41,-14);c.curve_to(45,-62,42,-94,34,-113);c.close_path()
  fill(c,hoodie,INK,5)
  curve(c,(-21,-15),(-5,-7),(16,-8),(28,-17),INK,2)
  if kind!='mascot':
   ln(c,[(-10,-107),(-9,-75)],WHITE,4);ln(c,[(10,-108),(9,-76)],WHITE,4)
  cap(c,(0,-116),(0,-138),15,WHITE if mono else SKIN)
  face=WHITE if mono or kind=='mascot' else SKIN
  oval(c,0,-180,47,51,face,INK,5)
  if kind!='mascot':
   c.new_path();c.move_to(-42,-195)
   for pt in [(-42,-224),(-22,-224),(-25,-242),(-5,-227),(8,-251),(19,-230),(44,-236),(43,-195),(21,-216),(6,-210),(-21,-205)]:c.line_to(*pt)
   c.close_path();fill(c,'#342f36')
  expression(c,action,t,kind)
 c.restore()

def effects(c,action,t,z,x,y):
 if action=='sprint':
  rng=random.Random(round(t*24)+28)
  for i in range(8):
   px=x-rng.randint(83,170);py=y-rng.randint(50,206)
   ln(c,[(px,py),(px-rng.randint(18,64),py+3)],'#f1fcfc' if i%2 else '#326d69',2+i%3)
  for i in range(3):oval(c,x-42-i*19,662-i*5,5+i*1.5,4+i,WHITE)
 if action=='knock' and math.sin(z*TAU*4)>.35:
  for i in range(3):curve(c,(346+i*8,457+i*10),(356+i*8,444+i*10),(358+i*8,434+i*10),(363+i*8,428+i*10),INK,3)
 if action in ('panic','slip','fall'):
  for i in range(10):
   th=TAU*i/10;xx=x+90*math.cos(th);yy=y-142+105*math.sin(th)
   ln(c,[(xx,yy),(xx+17*math.cos(th),yy+17*math.sin(th))],INK,3)
 if action=='jump':
  shadow_scale=1-.65*math.sin(math.pi*z)
  oval(c,x,667,35*shadow_scale,8*shadow_scale,'#777e7b')

def render_frame(c,plan,t,w,h):
 global MONO
 MONO=plan["style"]=="ink-monochrome"
 action,z,x,y,tilt,step=state(plan,t)
 mono=plan['style']=='ink-monochrome'
 c.save();c.scale(w/480,h/854)
 # Stable world stage; camera follows actor only mildly for vertical Shorts.
 zoom=1
 if action in ('panic','fall','slip'):zoom+=.17*math.sin(math.pi*z)
 elif action=='knock':zoom+=.06*ease(z)
 elif action=='jump':zoom-=.045*math.sin(math.pi*z)
 if zoom!=1:
  c.translate(240,410);c.scale(zoom,zoom);c.translate(-240,-410)
 if action in ('panic','fall','slip') and .15<z<.87:
  c.translate(3*math.sin(t*TAU*16),2*math.cos(t*TAU*13))
 backdrop(c,plan['setting'],t,mono)
 prop(c,plan['prop'],t,x)
 # Soft contact shadow, never duplicate a head layer.
 oval(c,x,673,58*(1-.4*math.sin(math.pi*z) if action=='jump' else 1),9,'#a3aba9')
 c.save();c.translate(x,y)
 actor(c,plan['character'],action,t,z,tilt,step,mono)
 c.restore()
 # Optional second fully independent character for two-person/cat chase prompts.
 secondary=plan.get("cast",[])
 if len(secondary)>=2:
  side_kind=secondary[1]
  second_x=max(38,min(447,x+107 if action=="sprint" else x-98))
  c.save();c.translate(second_x,y+27);c.scale(.70,.70)
  actor(c,side_kind,action,t+.11,z,tilt*.75,step,mono)
  c.restore()
 effects(c,action,t,z,x,y)
 c.restore()
 # Leave branding outside faces to keep subjects clear.
 rect(c,5,5,w-10,min(41,h*.055),'#263d43',radius=7)
 color(c,WHITE);c.select_font_face('Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
 c.set_font_size(min(18,w*.04));c.move_to(14,min(31,h*.041));c.show_text('FUNNY TOON EVER  /  '+action.upper())
 return action
