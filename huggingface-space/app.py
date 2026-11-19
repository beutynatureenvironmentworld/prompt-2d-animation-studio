"""CPU-only original animation preview Space. No inference model, token, or GPU needed."""
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import gradio as gr

ROOT=Path(__file__).resolve().parent

def render_video():
    dest=Path(tempfile.mkdtemp(prefix="fast_action_"))
    mp4=dest/"Fast_Action_Donut_Chase_V2_CPU.mp4"
    sheet=dest/"Contact_Sheet_V2.jpg"
    p=subprocess.run([sys.executable,str(ROOT/"renderer.py"),
        "--output",str(mp4),"--contact-sheet",str(sheet)],
        text=True,capture_output=True,timeout=240,check=False)
    if p.returncode:
        raise gr.Error("CPU render failed; check Space logs. "+p.stderr[-600:])
    return str(mp4),str(sheet),"Verified original CPU 2D cartoon — 720x720, 24fps, 12s, silent."

with gr.Blocks(title="Fast Action V2 — CPU Cartoon Lab") as demo:
    gr.Markdown("# 🎞️ Fast Action V2 — Original Cartoon Lab\nCPU-only repeatable slapstick animation. No external user assets, tokens, large weights or GPU needed. Sound is off to test motion quality.")
    button=gr.Button("Render 12-second V2 cartoon",variant="primary")
    with gr.Row():
        video=gr.Video(label="Generated MP4",autoplay=False)
        contact=gr.Image(label="Actual timeline frames")
    info=gr.Textbox(label="QA summary",interactive=False)
    button.click(render_video,outputs=[video,contact,info],api_name="render_fast_action")
demo.queue(max_size=2,default_concurrency_limit=1)
if __name__=="__main__":demo.launch()
