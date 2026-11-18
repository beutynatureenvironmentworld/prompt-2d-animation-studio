"""CPU-only original SVG animation renderer with audio and phone-portrait QA."""
import io, json, math, subprocess
from pathlib import Path
import cairosvg
from PIL import Image

ROOT = Path("overnight-lab/out/svg")
ROOT.mkdir(parents=True,exist_ok=True)
TARGET=ROOT/"FTE_SVG_Vector_Demo.mp4"
W,H,FPS,N=360,640,15,60

cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","rgba",
     "-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0",
     "-f","lavfi","-i","sine=frequency=430:sample_rate=44100:duration=4",
     "-shortest","-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast",
     "-crf","19","-c:a","aac","-b:a","96k",str(TARGET)]
process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for i in range(N):
    t=i/FPS
    bounce=12*math.sin(t*5.1)
    angry=t>=1.1
    spray=max(0,min(1,(t-2.0)*3))
    jet=(f'<path d="M201 343 Q150 {300-12*math.sin(t*18)} 94 314" '
         f'stroke="#c4efff" stroke-width="{12*spray}" fill="none" />') if spray else ""
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="#fff5e6"/>
      <path d="M0 550H360V640H0Z" fill="#e6c7a9"/>
      <g stroke="#14151b" stroke-width="5" fill="#fff">
       <circle cx="90" cy="{352+bounce:.1f}" r="54"/>
       <circle cx="278" cy="345" r="53"/>
       <circle cx="47" cy="{314+bounce:.1f}" r="22"/>
       <circle cx="137" cy="{314+bounce:.1f}" r="22"/>
      </g>
      <path d="M66 {402+bounce:.1f}H112L141 519H34Z" stroke="#15151a" stroke-width="5" fill="#fb6c89"/>
      <rect x="247" y="398" width="62" height="115" rx="18" stroke="#15151a" stroke-width="5" fill="#89bdff"/>
      <g stroke="#15151a" fill="white" stroke-width="4">
       <ellipse cx="72" cy="{340+bounce:.1f}" rx="9" ry="15"/>
       <ellipse cx="109" cy="{340+bounce:.1f}" rx="9" ry="15"/>
       <ellipse cx="258" cy="334" rx="8" ry="13"/>
       <ellipse cx="294" cy="334" rx="8" ry="13"/>
      </g>
      <g fill="#15151a"><circle cx="72" cy="{341+bounce:.1f}" r="4"/>
        <circle cx="109" cy="{341+bounce:.1f}" r="4"/><circle cx="258" cy="335" r="4"/><circle cx="294" cy="335" r="4"/></g>
      <path d="M70 {368+bounce:.1f}Q90 {389+bounce:.1f} 113 {366+bounce:.1f}" stroke="#15151a" stroke-width="5" fill="none"/>
      <path d="M248 363Q278 395 305 360" stroke="#15151a" stroke-width="6" fill="none"/>
      <path d="M112 448L202 360M250 446L221 370" stroke="#15151a" stroke-width="11" fill="none"/>
      <rect x="187" y="332" width="68" height="62" rx="5" fill="#fff" stroke="#15151a" stroke-width="5"/>
      <path d="M190 346L158 337" stroke="#b5e7fa" stroke-width="11" fill="none"/>
      <text x="220" y="369" font-family="sans-serif" font-size="12" text-anchor="middle">MILK</text>
      {jet}
      <text x="180" y="87" font-family="sans-serif" font-weight="bold" font-size="23" text-anchor="middle">SVG VECTOR LAB</text>
      <text x="180" y="606" font-family="sans-serif" font-size="17" text-anchor="middle">CairoSVG + FFmpeg</text>
    </svg>'''
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=W,output_height=H)
    frame=Image.open(io.BytesIO(png)).convert("RGBA")
    process.stdin.write(frame.tobytes())
process.stdin.close()
if process.wait(timeout=100):raise SystemExit("FFmpeg failure")
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(TARGET)],text=True))
streams=probe["streams"]
v=next(s for s in streams if s["codec_type"]=="video")
audio=any(s["codec_type"]=="audio" for s in streams)
qa={"engine":"CairoSVG+Pillow+FFmpeg","video":str(TARGET),
    "width":v["width"],"height":v["height"],"duration":float(probe["format"]["duration"]),
    "has_audio":audio,"fps":FPS,"cpu_only":True}
qa["verified"]=qa["width"]==360 and qa["height"]==640 and qa["duration"]>=3.8 and audio
(ROOT/"QA.json").write_text(json.dumps(qa,indent=2)+"\n")
print(json.dumps(qa))
if not qa["verified"]: raise SystemExit(2)
