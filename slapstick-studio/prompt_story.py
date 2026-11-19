#!/usr/bin/env python3
"""Offline limited action parser (NOT generative AI). Exact known motions only."""
import argparse
import json
from pathlib import Path
WORDS={
 "wave":("wave","waving","hand movement","hand","අත වන","අත ඔසව"),
 "pickup":("pick up","picking","picks","pickup","grab","camera","bag","අහුලා","කැමරාව","බෑගය"),
 "jump":("jump","jumps","jumping","leap","hop","උඩ පන","පනි","පැන"),
 "kick":("kick","kicking","kicks","football","soccer ball","පයින් ගස","පයින් ගහ","බෝලය")
}
DURATION={"wave":1.5,"pickup":2.5,"jump":1.8,"kick":2.2}

def compile_prompt(prompt):
    text=prompt.lower()
    found=[]
    for action,variants in WORDS.items():
        locs=[text.find(w) for w in variants if w in text]
        if locs:found.append((min(locs),action))
    if not found:
        raise ValueError("Unsupported prompt. Available actions: wave, pickup, jump, kick.")
    found.sort()
    beats=[{"action":action,"duration":DURATION[action]} for _,action in found]
    return {"title":prompt,"source":"offline explicit-action parser; no neural video generation",
            "source_pose_fps":12,"output_fps":24,"beats":beats}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--prompt",required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    story=compile_prompt(a.prompt)
    a.output.write_text(json.dumps(story,indent=2,ensure_ascii=False)+"\n")
    print("STORY",a.output,story["beats"])
