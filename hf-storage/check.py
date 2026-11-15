"""Read-only Hugging Face credential and private dataset readiness.
No secrets, owner names, tokens, or account data are printed or uploaded.
"""
import json,os,urllib.request,urllib.error
from pathlib import Path
out=Path("hf-storage/output");out.mkdir(parents=True,exist_ok=True)
token=os.environ.get("HF_TOKEN","").strip()
result={"hf_secret_present":bool(token),"hf_identity_verified":False,
        "private_dataset_exists":False,"private_dataset_access":False,
        "new_repository_created":False,"large_weights_uploaded":False}
if token:
    headers={"Authorization":"Bearer "+token,"User-Agent":"VidBestStorage-0.1"}
    def get(path):
        req=urllib.request.Request("https://huggingface.co/api/"+path,headers=headers)
        with urllib.request.urlopen(req,timeout=25) as resp:
            return json.load(resp)
    try:
        me=get("whoami-v2")
        name=me.get("name") or me.get("fullname")
        result["hf_identity_verified"]=bool(name and isinstance(name,str))
        if result["hf_identity_verified"]:
            try:
                d=get("datasets/"+name+"/vidbest-animation-storage")
                result["private_dataset_exists"]=True
                result["private_dataset_access"]=True
                result["dataset_is_private"]=bool(d.get("private",False))
            except urllib.error.HTTPError as exc:
                if exc.code==404:
                    result["dataset_is_private"]=None
                else:
                    result["dataset_access_http_code"]=exc.code
    except urllib.error.HTTPError as exc:
        result["hf_login_http_code"]=exc.code
    except (urllib.error.URLError,TimeoutError,ValueError):
        result["hf_network_or_response_error"]=True
out.joinpath("hf-storage-check.json").write_text(json.dumps(result,indent=2)+"\n")
print("HF_TOKEN_AUTHENTICATION_CHECK="+("authenticated" if result["hf_identity_verified"] else "missing_or_not_verified"))
print("HF_PRIVATE_DATASET_AVAILABLE="+str(result["private_dataset_access"]))
print("HF_STORAGE_NO_WRITE_ACTION_PERFORMED")
