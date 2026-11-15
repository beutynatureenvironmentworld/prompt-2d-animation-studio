"""Validate presence/authentication of GitHub AI_HORDE_API_KEY without exposing key.

This NEVER starts paid/image-generation jobs. It only GETs the official find_user endpoint.
"""
from __future__ import annotations
import json,os,sys,urllib.request,urllib.error
from pathlib import Path

URL="https://stablehorde.net/api/v2/find_user"

def check(key: str, opener=None) -> dict:
    if not key or not key.strip():
        return {"configured":False,"authenticated":False,"status":"missing"}
    req=urllib.request.Request(URL,headers={
        "apikey":key.strip(),
        "Client-Agent":"VidBestColab:0.1:https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio",
        "Accept":"application/json",
    },method="GET")
    try:
        with (opener or urllib.request.urlopen)(req,timeout=20) as response:
            if response.status != 200:
                return {"configured":True,"authenticated":False,"status":"rejected"}
            data=json.load(response)
            # Never return private username, account ID or kudos.
            user=data.get("username") if isinstance(data,dict) else None
            confirmed=isinstance(user,str) and len(user.strip())>0 and user.strip().lower()!="anonymous"
            return {"configured":True,"authenticated":confirmed,
                    "status":"authenticated" if confirmed else "response_requires_review"}
    except urllib.error.HTTPError as exc:
        return {"configured":True,"authenticated":False,
                "status":"rejected" if exc.code in (400,401,403) else "api_http_error"}
    except (urllib.error.URLError,TimeoutError,OSError,ValueError,TypeError):
        return {"configured":True,"authenticated":False,"status":"network_or_response_error"}

def main() -> None:
    key=os.environ.get("AI_HORDE_API_KEY","")
    result=check(key)
    output=Path("colab-studio/ai-horde-check.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("AI_HORDE_KEY_CHECK="+result["status"])
    # Missing/invalid/network: failure prompts review, without leaking key.
    if result["status"]!="authenticated":
        raise SystemExit(1)

if __name__=="__main__":
    main()
