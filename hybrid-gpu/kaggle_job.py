"""Submit one bounded private Kaggle job. An ambiguous submit is never repeated."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from notebook import build

def main():
    p=argparse.ArgumentParser()
    p.add_argument("bundle",type=Path);p.add_argument("username")
    p.add_argument("--model",choices=("ltx","wan","toon"),default="ltx")
    p.add_argument("--minutes",type=int,default=60)
    a=p.parse_args()
    if not 1<=a.minutes<=720 or not re.fullmatch("[a-zA-Z0-9_-]+",a.username):p.error("Invalid account or runtime")
    key=hashlib.sha256(a.bundle.read_bytes()).hexdigest()[:16]
    title=f"Vidbest {a.model} {key}"; slug=title.lower().replace(" ","-"); identifier=f"{a.username}/{slug}"
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);build(root/"episode.ipynb",a.bundle,a.model)
        (root/"kernel-metadata.json").write_text(json.dumps({"id":identifier,"title":title,"code_file":"episode.ipynb","language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":True,"enable_internet":True,"dataset_sources":[],"kernel_sources":[],"competition_sources":[]}))
        print(f"Status: kaggle kernels status {identifier}\nDownload: kaggle kernels output {identifier} -p renders",flush=True)
        subprocess.run(["kaggle","kernels","push","-p",d,"--accelerator","NvidiaTeslaT4","-t",str(a.minutes*60)],check=True)
if __name__=="__main__":main()
