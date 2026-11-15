"""Deterministic prompt -> motion timeline for separately tested 2D puppet experiment.

This is a rule-based motion compiler, NOT an LLM or generative video model.
Natural language is bounded to recognized actions; unsupported input fails safely.
"""
import argparse, json, re
from pathlib import Path

LIBRARY={
 "run":{"duration":1.8,"poses":["stride_left","stride_right","airborne"],"loop":True},
 "knock":{"duration":1.0,"poses":["hand_up","tap","recoil"],"loop":False},
 "shock":{"duration":0.8,"poses":["freeze","eyes_wide","jump"],"loop":False},
 "talk":{"duration":1.4,"poses":["mouth_closed","mouth_open","mouth_round"],"loop":False},
 "slip":{"duration":1.3,"poses":["lose_balance","lean_back","squash"],"loop":False},
 "bounce":{"duration":1.1,"poses":["squash","stretch","recover"],"loop":False}
}
WORDS={
 "run":["run","runs","running","rush","chase","sprint"],
 "knock":["knock","knocks","knocking","tap","door"],
 "shock":["surprise","shock","shocked","scared","fear","startle"],
 "talk":["talk","talks","speak","speaks","say","says","shout","whoa","hello"],
 "slip":["slip","slips","trip","trips","banana","fall","falls"],
 "bounce":["bounce","bounces","rebound","recover","spring"]
}
def build(prompt):
    if not isinstance(prompt,str) or not 3<=len(prompt)<=500:
        raise ValueError("Prompt must be 3..500 chars")
    p=prompt.lower()
    # First occurrence ordering is preserved, so story beats follow the prompt.
    found=[]
    for kind,words in WORDS.items():
        hits=[m.start() for word in words if (m:=re.search(r"\b"+re.escape(word)+r"\b",p))]
        if hits:found.append((min(hits),kind))
    found.sort()
    if not found:raise ValueError("No supported action. Try run, knock, shock, talk, slip, bounce.")
    actions=[]
    time=0.
    for _,name in found:
        step=LIBRARY[name]
        actions.append({"action":name,"t":round(time,2),"duration":step["duration"],"poses":step["poses"],"loop":step["loop"]})
        time+=step["duration"]
    return {"schema":"vidbest-motion-plan-v1","prompt":prompt,
        "character":{"name":"original funny skinny cartoon boy","style":"simple ink-on-paper black ink, white face, light gold shirt"},
        "fps":16,"width":320,"height":480,
        "actions":actions,"duration":round(time,2),
        "total_output_frames":round(time*16),
        "method":"deterministic text-to-motion rules; not an LLM, AI rig or GPU video model"}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prompt",default="A funny skinny boy runs, knocks on a door, is shocked by a cat, talks, slips, then bounces back.")
    ap.add_argument("--output",default="puppet-lab/output/motion-plan.json")
    a=ap.parse_args()
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    result=build(a.prompt)
    assert len(result["actions"])>=4
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("PROMPT_TO_MOTION_PLAN_OK",len(result["actions"]),"actions",result["total_output_frames"],"planned frames",flush=True)
if __name__=="__main__":main()
