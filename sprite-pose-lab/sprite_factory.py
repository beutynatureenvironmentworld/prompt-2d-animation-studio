"""Create original transparent, reusable cartoon PNG sprites (no reference-frame extraction)."""
from pathlib import Path
import argparse
import cairosvg

HERE = Path(__file__).resolve().parent
POSES = ('idle', 'talk', 'grin', 'blink', 'point', 'shock', 'run', 'kick', 'jump', 'crouch', 'fall', 'celebrate')

# Continuous strokes hide elbows/knees. All sprite canvases use foot anchor (140, 390).
ARM = {
'idle': ('M105 210 Q93 262 70 270', 'M177 210 Q187 255 215 262'),
'talk': ('M105 210 Q94 258 64 244', 'M177 210 Q201 186 227 207'),
'grin': ('M105 210 Q85 240 76 207', 'M177 210 Q201 233 211 201'),
'blink': ('M105 210 Q96 266 76 271', 'M177 210 Q188 262 214 268'),
'point': ('M105 210 Q81 207 52 172', 'M177 210 Q209 219 245 205'),
'shock': ('M105 210 Q72 192 62 151', 'M177 210 Q206 177 225 142'),
'run': ('M105 210 Q76 185 61 216', 'M177 210 Q207 239 219 265'),
'kick': ('M105 210 Q77 190 55 205', 'M177 210 Q205 181 223 204'),
'jump': ('M105 210 Q76 177 64 143', 'M177 210 Q210 171 225 137'),
'crouch': ('M105 210 Q68 233 70 296', 'M177 210 Q206 234 208 296'),
'fall': ('M105 210 Q67 202 52 247', 'M177 210 Q204 169 237 172'),
'celebrate': ('M105 210 Q67 184 64 127', 'M177 210 Q205 181 232 118'),
}
LEGS = {
'idle': ('M122 309 Q112 351 103 381', 'M163 309 Q169 356 183 381'),
'talk': ('M122 309 Q114 357 103 381', 'M163 309 Q165 352 184 381'),
'grin': ('M122 309 Q117 353 99 381', 'M163 309 Q175 348 190 381'),
'blink': ('M122 309 Q112 351 103 381', 'M163 309 Q169 356 183 381'),
'point': ('M122 309 Q111 350 108 381', 'M163 309 Q175 347 187 381'),
'shock': ('M122 309 Q102 348 91 381', 'M163 309 Q184 354 197 381'),
'run': ('M122 309 Q82 335 58 361', 'M163 309 Q193 337 226 361'),
'kick': ('M122 309 Q92 334 68 382', 'M163 309 Q214 304 243 318'),
'jump': ('M122 309 Q94 330 77 338', 'M163 309 Q194 337 208 325'),
'crouch': ('M122 309 Q97 329 79 381', 'M163 309 Q188 320 208 381'),
'fall': ('M122 309 Q82 320 63 338', 'M163 309 Q206 314 238 328'),
'celebrate': ('M122 309 Q105 348 90 381', 'M163 309 Q185 345 202 381'),
}

def svg_character(which, pose):
    yellow = which == 'luma'
    shirt = '#FFD747' if yellow else '#FF7861'
    trim = '#F1B927' if yellow else '#D74F46'
    skin = '#DC996C' if yellow else '#B87656'
    hair = '#4C3028' if yellow else '#552F39'
    eyes = pose in ('shock', 'fall')
    body = '<path d="M111 192 Q143 184 174 192 L181 308 Q145 324 107 308 Z" fill="%s" stroke="#20202A" stroke-width="7"/>' % shirt
    if yellow:
        body += '<path d="M113 280 L178 280 L207 321 Q142 336 83 321 Z" fill="%s" stroke="#20202A" stroke-width="6"/>' % trim
    else:
        body += '<path d="M113 275 Q145 283 176 275" stroke="%s" stroke-width="5" fill="none"/>' % trim
    hair_extra = ('<circle cx="210" cy="83" r="37" fill="%s" stroke="#20202A" stroke-width="6"/>' % hair) if yellow else ''
    hair_top = ('<path d="M74 109 Q77 40 148 41 Q210 49 214 111 Q178 78 139 94 Q104 90 74 109Z" fill="%s" stroke="#20202A" stroke-width="5"/>' % hair) if yellow else ('<path d="M67 95 Q88 24 152 43 Q214 57 208 91 L167 80 Q130 69 95 102Z" fill="%s" stroke="#20202A" stroke-width="5"/>' % hair)
    hair_front = '<path d="M88 75 Q137 41 191 82" stroke="#7C4B4E" stroke-width="5" fill="none"/>' if not yellow else '<path d="M93 80 Q125 57 167 68" stroke="#76503D" stroke-width="5" fill="none"/>'
    if pose == 'blink':
        eye_shapes = '<path d="M101 139 Q114 130 128 138 M152 139 Q165 131 178 138" stroke="#20202A" stroke-width="6" fill="none" stroke-linecap="round"/>'
    elif eyes:
        eye_shapes = '<ellipse cx="113" cy="135" rx="23" ry="31" fill="white" stroke="#20202A" stroke-width="5"/><ellipse cx="166" cy="135" rx="23" ry="31" fill="white" stroke="#20202A" stroke-width="5"/><circle cx="119" cy="137" r="7" fill="#20202A"/><circle cx="160" cy="137" r="7" fill="#20202A"/>'
    else:
        eye_shapes = '<ellipse cx="112" cy="137" rx="19" ry="23" fill="white" stroke="#20202A" stroke-width="5"/><ellipse cx="169" cy="137" rx="19" ry="23" fill="white" stroke="#20202A" stroke-width="5"/><circle cx="119" cy="142" r="6" fill="#20202A"/><circle cx="163" cy="142" r="6" fill="#20202A"/>'
    if pose in ('shock','fall'):
        mouth = '<ellipse cx="143" cy="171" rx="18" ry="24" fill="#421B24" stroke="#20202A" stroke-width="4"/><ellipse cx="146" cy="184" rx="9" ry="6" fill="#FF777B"/>'
    elif pose in ('grin','celebrate','kick','jump','run'):
        mouth = '<path d="M118 165 Q143 193 170 164 Q146 173 118 165Z" fill="#401C22" stroke="#20202A" stroke-width="4"/><path d="M121 166 Q145 175 168 165" stroke="white" stroke-width="7" fill="none"/>'
    elif pose == 'talk':
        mouth = '<ellipse cx="143" cy="173" rx="13" ry="10" fill="#4D2429" stroke="#20202A" stroke-width="4"/>'
    else:
        mouth = '<path d="M125 171 Q145 186 164 171" stroke="#20202A" stroke-width="5" fill="none" stroke-linecap="round"/>'
    limb = lambda p: '<path d="%s" fill="none" stroke="#20202A" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>' % p
    a,b=ARM[pose];c,d=LEGS[pose]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="400" viewBox="0 0 280 400">
    <g>{limb(c)}{limb(d)}<ellipse cx="103" cy="383" rx="18" ry="7" fill="#20202A"/><ellipse cx="183" cy="383" rx="18" ry="7" fill="#20202A"/>
    {limb(a)}{limb(b)}{body}
    <path d="M118 182 L160 181 L155 205 L123 206Z" fill="{skin}" stroke="#20202A" stroke-width="5"/>
    {hair_extra}<ellipse cx="140" cy="128" rx="75" ry="79" fill="{skin}" stroke="#20202A" stroke-width="6"/>
    {hair_top}{hair_front}<ellipse cx="66" cy="153" rx="10" ry="17" fill="{skin}" stroke="#20202A" stroke-width="5"/>
    {eye_shapes}{mouth}
    <circle cx="86" cy="174" r="7" fill="#E89185" opacity="0.45"/>
    </g></svg>'''

def asset_svg(name):
    if name=='ball':
        obj='<circle cx="100" cy="100" r="78" fill="#78DC77" stroke="#253D34" stroke-width="9"/><path d="M38 53 Q94 99 163 64 M48 150 Q102 98 155 148" stroke="#2F9266" stroke-width="8" fill="none"/>'
    elif name=='cup':
        obj='<path d="M60 36 L157 36 L144 179 Q107 190 77 179Z" fill="#BCEEFF" stroke="#1F3440" stroke-width="9"/><path d="M66 104 Q107 97 151 104 L144 179 Q110 188 77 179Z" fill="#FFFFFF"/><path d="M83 16 L143 16" stroke="#1F3440" stroke-width="11" stroke-linecap="round"/><path d="M132 26 L177 4" stroke="#FF826F" stroke-width="9" stroke-linecap="round"/>'
    elif name=='burst':
        obj='<path d="M105 5 L130 51 L183 21 L171 76 L199 105 L163 128 L174 187 L121 164 L92 199 L75 148 L11 160 L45 113 L3 70 L67 67Z" fill="#FFD749" stroke="#23212A" stroke-width="9"/><text x="98" y="127" font-size="50" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="#E54D3E">POP!</text>'
    elif name=='splash':
        obj='<path d="M95 6 Q105 67 131 71 L197 21 Q148 95 195 142 Q136 106 109 189 Q92 128 15 170 Q58 109 7 62 Q73 82 95 6Z" fill="#FFFFFF" stroke="#96D0F1" stroke-width="7"/>'
    else: raise ValueError(name)
    return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">'+obj+'</svg>'

def background_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">
    <rect width="720" height="1280" fill="#BCEEFF"/><path d="M0 1010 L720 1010 L720 1280 L0 1280Z" fill="#E8CB98"/><path d="M0 1010 L720 1010" stroke="#34333A" stroke-width="7"/>
    <rect x="442" y="175" width="213" height="370" rx="14" fill="#FFFFFF" stroke="#34333A" stroke-width="12"/><rect x="459" y="190" width="179" height="335" rx="8" fill="#85C5FF"/>
    <path d="M548 191 L548 523 M459 357 L638 357" stroke="#FFFFFF" stroke-width="12"/>
    <path d="M464 491 Q528 436 583 495 Q612 466 634 493 L634 526 L460 526Z" fill="#9BD98E"/>
    <rect x="55" y="704" width="282" height="320" rx="38" fill="#F96D79" stroke="#32313B" stroke-width="10"/><rect x="39" y="854" width="314" height="167" rx="30" fill="#EA5069" stroke="#32313B" stroke-width="10"/>
    <path d="M83 1018 L80 1058 M315 1018 L319 1058" stroke="#34333A" stroke-width="11"/>
    <path d="M71 543 L315 543" stroke="#754F48" stroke-width="15" stroke-linecap="round"/><rect x="114" y="477" width="68" height="67" rx="5" fill="#CE8E5D"/><path d="M149 476 Q89 440 114 396 Q146 412 149 452 Q153 400 205 398 Q208 447 149 476" fill="#59AC75" stroke="#24543D" stroke-width="5"/>
    <rect x="352" y="840" width="110" height="170" rx="19" fill="#FFC779" stroke="#34333A" stroke-width="8"/>
    </svg>'''

def generate(output=HERE/'assets'):
    output=Path(output)
    for who in ('pip','luma'):
        d=output/'characters'/who; d.mkdir(parents=True,exist_ok=True)
        for pose in POSES:
            cairosvg.svg2png(bytestring=svg_character(who,pose).encode(),write_to=str(d/(pose+'.png')),output_width=560,output_height=800)
    d=output/'props';d.mkdir(parents=True,exist_ok=True)
    for p in ('ball','cup','burst','splash'):
        cairosvg.svg2png(bytestring=asset_svg(p).encode(),write_to=str(d/(p+'.png')),output_width=400,output_height=400)
    d=output/'backgrounds';d.mkdir(parents=True,exist_ok=True)
    cairosvg.svg2png(bytestring=background_svg().encode(),write_to=str(d/'living_room.png'),output_width=720,output_height=1280)
    print('Created',len(POSES)*2+5,'PNG assets in',output)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'assets')
    generate(ap.parse_args().output)
