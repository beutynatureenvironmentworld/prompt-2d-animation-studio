#!/usr/bin/env python3
"""Import properly licensed Freesound recordings into a reusable FastToon sound library.

Free Freesound API use: noncommercial only unless separately authorized.
Manual import of separately obtained CC0/CC-BY sounds does not call the API.
"""
import argparse,csv,json,os,subprocess
from pathlib import Path
from urllib.parse import urlparse

VALID={"CC0":"https://creativecommons.org/publicdomain/zero/1.0/",
       "CC-BY-4.0":"https://creativecommons.org/licenses/by/4.0/",
       "CC-BY-3.0":"https://creativecommons.org/licenses/by/3.0/"}
FIELDS=["filename","title","author","source_url","license","license_url"]
def slug(value):
    return "".join(c for c in value if c.isascii() and (c.isalnum() or c in "_-"))[:55].strip("_-") or "sound"

def import_local(file,title,author,url,lic,outdir):
    if lic not in VALID:raise ValueError("Use CC0/CC-BY. CC-BY-NC is not supported.")
    if not title or not author or not url:raise ValueError("Original name, author and source URL required")
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.netloc.endswith("freesound.org"):
        raise ValueError("Original Freesound HTTPS source page required")
    src=Path(file).resolve()
    if not src.is_file():raise FileNotFoundError(src)
    folder=Path(outdir)
    folder.mkdir(parents=True,exist_ok=True)
    dest=folder/(slug(title).lower()+".wav")
    if dest.exists():raise FileExistsError("Sound already imported; not overwriting")
    subprocess.run(["ffmpeg","-v","error","-nostdin","-i",str(src),"-ac","2",
                    "-ar","48000","-c:a","pcm_s16le",str(dest)],check=True,timeout=120)
    row={"filename":dest.name,"title":title,"author":author,"source_url":url,
         "license":lic,"license_url":VALID[lic]}
    manifest=folder/"credits.csv"
    old=list(csv.DictReader(manifest.open(encoding="utf-8",newline=""))) if manifest.exists() else []
    with manifest.open("w",encoding="utf-8",newline="") as fd:
        w=csv.DictWriter(fd,fieldnames=FIELDS);w.writeheader();w.writerows(old+[row])
    print("LICENSED_CLIP_IMPORTED",dest,"CREDITS",manifest)

def search(query,limit):
    import requests
    token=os.getenv("FREESOUND_API_TOKEN")
    if not token:raise RuntimeError("Missing private FREESOUND_API_TOKEN")
    r=requests.get("https://freesound.org/apiv2/search/text/",
      headers={"Authorization":"Token "+token},params={
       "query":query,"page_size":min(10,max(1,limit)),
       "filter":'license:"Creative Commons 0"',
       "fields":"id,name,username,license,url"},timeout=30)
    r.raise_for_status();print(json.dumps(r.json().get("results",[]),indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="mode",required=True)
    imp=sub.add_parser("import-local")
    for field in ("file","title","author","source-url"):imp.add_argument("--"+field,required=True)
    imp.add_argument("--license",choices=list(VALID),required=True)
    imp.add_argument("--outdir",default="audio-studio/freesound_library")
    s=sub.add_parser("search")
    s.add_argument("--query",required=True)
    s.add_argument("--limit",type=int,default=5)
    s.add_argument("--noncommercial-api-ok",action="store_true")
    args=p.parse_args()
    if args.mode=="import-local":
        import_local(args.file,args.title,args.author,args.source_url,args.license,args.outdir)
    else:
        if not args.noncommercial_api_ok:
            raise SystemExit("Noncommercial-only free Freesound API: use approved commercial license for monetized services.")
        search(args.query,args.limit)
