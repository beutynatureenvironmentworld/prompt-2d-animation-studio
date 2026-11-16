"""Hugging Face Docker Space app; requires eligible HF compute subscription.
Runs only limited isolated jobs, user-provided prompts never executed as shell code.
"""
from pathlib import Path
import gradio as gr
from shortgpt_supertest import run,PipelineError

def create(prompt,planner,image_provider,voice_provider):
    try:
        path=Path('output/funny_short.mp4')
        result=run(prompt,path,planner,image_provider,voice_provider)
        return str(path.resolve()),f"Rendered {result['scene_count']} scenes; actual AI images: {result['ai_generated_images']}"
    except Exception as e:
        return None,f"Generation failed: {type(e).__name__}: {str(e)[:150]}"
with gr.Blocks(title='ShortGPT SuperTest Studio') as app:
    gr.Markdown('# ShortGPT SuperTest — CPU composer\nAI backgrounds require Hugging Face Inference quota; default mode creates code-drawn backgrounds (not AI images).')
    prompt=gr.Textbox(label='Funny Short Prompt',lines=3,value='Boy runs to the toilet, knocks on the door and gets shocked')
    with gr.Row():
        planner=gr.Dropdown(['offline','local','hf'],value='offline',label='Story planner')
        image=gr.Dropdown(['procedural','hf'],value='procedural',label='Image generator')
        voice=gr.Dropdown(['espeak','edge','none'],value='espeak',label='Voice')
    btn=gr.Button('Create MP4')
    video=gr.Video(label='Your cartoon video')
    status=gr.Textbox(label='Status')
    btn.click(create,[prompt,planner,image,voice],[video,status],concurrency_limit=1)
app.queue(max_size=3)
app.launch(server_name='0.0.0.0',server_port=7860,show_api=False)
