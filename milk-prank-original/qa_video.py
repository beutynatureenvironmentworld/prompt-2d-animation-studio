"""Decode real MP4 and produce repeatable technical QA + contact sheet.
The visual quality still requires a human review after numeric gates.
"""
from pathlib import Path
import sys,json,subprocess
from PIL import Image,ImageChops,ImageStat

video=Path(sys.argv[1])
out=Path(sys.argv[2])
out.mkdir(parents=True,exist_ok=True)
probe=json.loads(subprocess.check_output([
 "ffprobe","-v","error","-show_format","-show_streams","-of","json",str(video)],text=True))
v=next(s for s in probe["streams"] if s["codec_type"]=="video")
a=next((s for s in probe["streams"] if s["codec_type"]=="audio"),None)
duration=float(probe["format"]["duration"])
checkpoints=[.8,3.5,6.8,8.55,9.8,12.8,14.5]
frames=[]
for i,at in enumerate(checkpoints):
    png=out/("frame_"+str(i)+".png")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(at),
                    "-i",str(video),"-frames:v","1",str(png)],check=True)
    frame=Image.open(png).convert("RGB")
    frame.thumbnail((180,320))
    frames.append(frame)
contact=Image.new("RGB",(180*len(frames),320),"#f6f3f0")
for i,frame in enumerate(frames):contact.paste(frame,(180*i,0))
contact.save(out/"FRAME_AUDIT.jpg",quality=89)
variation=[]
for frame in frames[1:]:
    d=ImageChops.difference(frames[0],frame)
    variation.append(round(sum(ImageStat.Stat(d).mean)/3,3))
report={
 "source":"original Snore Collector JS/SVG rig source",
 "story":"Clever Milk Carton Reverse Prank",
 "engine":"Node.js + analytic 2-bone IK + Cairo/librsvg + FFmpeg",
 "method":"100% code-rendered original vector animation (not GPU AI video)",
 "verified_encoded":False,
 "video_codec":v.get("codec_name"),
 "width":v.get("width"),"height":v.get("height"),
 "duration":duration,"fps":v.get("avg_frame_rate"),
 "audio_codec":a.get("codec_name") if a else None,
 "audio_channels":a.get("channels") if a else None,
 "file_bytes":video.stat().st_size,
 "frame_checkpoints_seconds":checkpoints,
 "frame_variation_vs_first":variation,
 "visual_limitations":"Contact geometry and acting should be evaluated on contact sheet and actual playback."
}
report["verified_encoded"]=(v.get("codec_name")=="h264" and
     v.get("width")==1080 and v.get("height")==1920 and
     14.8<=duration<=15.3 and a is not None and
     a.get("codec_name")=="aac" and max(variation)>2)
(out/"VIDEO_QA.json").write_text(json.dumps(report,indent=2)+"\n")
print("FTE_2D_IK_PRO_RENDER_QA",json.dumps(report),flush=True)
if not report["verified_encoded"]:raise SystemExit("Real MP4 QA failed")
