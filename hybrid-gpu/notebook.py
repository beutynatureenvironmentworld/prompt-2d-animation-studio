"""Build a portable notebook with the worker, node graphs and optional episode input."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

HERE=Path(__file__).resolve().parent
def cell(kind,text):
    c={"cell_type":kind,"metadata":{},"source":text.splitlines(True)}
    if kind=="code":c.update(execution_count=None,outputs=[])
    return c

def build(out,bundle=None,model="ltx"):
    source=io.BytesIO()
    with ZipFile(source,"w",ZIP_DEFLATED) as z:
        for file in [HERE/"setup.py",HERE/"hybrid.py",*sorted(HERE.glob("*-api.json"))]:z.write(file,file.name)
    code='''import base64, io, json, os, subprocess, sys, shutil, tempfile
from pathlib import Path
from zipfile import ZipFile
import torch
if not torch.cuda.is_available():
    raise RuntimeError("Select GPU in notebook settings, reconnect, then rerun.")
print(torch.cuda.get_device_name(0), round(torch.cuda.get_device_properties(0).total_memory/2**30,1), "GiB VRAM")
temporary=Path(tempfile.gettempdir())/"vidbest-gpu"
temporary.mkdir(exist_ok=True)
studio=temporary/"worker"
root=temporary/"ComfyUI"
output=Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd()
bundle=temporary/"episode.zip"
'''
    code+='ZipFile(io.BytesIO(base64.b64decode('+repr(base64.b64encode(source.getvalue()).decode())+'))).extractall(studio)\n'
    if bundle:
        code+='bundle.write_bytes(base64.b64decode('+repr(base64.b64encode(bundle.read_bytes()).decode())+'))\n'
    else:
        code+='''if "google.colab" in sys.modules:
    from google.colab import files
    bundle.write_bytes(next(iter(files.upload().values())))
else:
    available=list(Path("/kaggle/input").rglob("*.zip"))
    if len(available)!=1: raise ValueError("Attach one episode bundle ZIP or build a notebook with --bundle.")
    shutil.copyfile(available[0],bundle)
'''
    cells=[cell("markdown","# VidBest GPU shots\nSelect GPU, then Run all. The included CPU episode supplies the reference frames and original sound. Only the selected shot windows are regenerated. Choose ltx, wan or toon below. GPU capacity and model downloads depend on your account. Keep the output before disconnecting."),
           cell("code",f'MODEL = "{model}"  # ltx, wan, toon\nUSE_R2 = False  # Optional notebook secrets for checkpoints\n'),cell("code",code),
           cell("code",'''if USE_R2:
    names=("R2_BUCKET","R2_ENDPOINT","AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY")
    if Path("/kaggle/working").exists():
        from kaggle_secrets import UserSecretsClient
        fetch=UserSecretsClient().get_secret
    elif "google.colab" in sys.modules:
        from google.colab import userdata
        fetch=userdata.get
    else:
        fetch=os.environ.__getitem__
    for name in names: os.environ[name]=fetch(name)
    subprocess.run([sys.executable,"-m","pip","install","boto3"],check=True)
subprocess.run([sys.executable, studio/"setup.py", MODEL, "--root", root], check=True)
# For persistent output on Colab, set output to a mounted Drive directory.
subprocess.run([sys.executable, studio/"hybrid.py","gpu", bundle,output/"renders","--root",root,"--model",MODEL],check=True)
'''),cell("code",'''import hashlib
from IPython.display import Video, display
result=output/"renders"/hashlib.sha256(bundle.read_bytes()).hexdigest()/MODEL/"episode.mp4"
display(Video(str(result),embed=True))
if "google.colab" in sys.modules:
    from google.colab import files
    files.download(str(result))
''')]
    notebook=dict(cells=cells,nbformat=4,nbformat_minor=4,metadata={"accelerator":"GPU","kernelspec":{"name":"python3","display_name":"Python 3","language":"python"}})
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(notebook))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);p.add_argument("--bundle",type=Path);p.add_argument("--model",choices=("ltx","wan","toon"),default="ltx")
    a=p.parse_args();build(a.output,a.bundle,a.model)
