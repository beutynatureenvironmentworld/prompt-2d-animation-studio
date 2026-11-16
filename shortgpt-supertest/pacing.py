"""Conservative timing expansion for readable short-form 2D comedy.

Never invents story scenes: only allocates enough time for action and narration.
Keeps the original maximum 3 seconds per beat and <=12 seconds total.
"""
from copy import deepcopy

MAX_SCENE = 3.0
MAX_TOTAL = 12.0


def make_readable(plan: dict, target_seconds: float = 9.0) -> dict:
    out = deepcopy(plan)
    scenes = out["scenes"]
    for s in scenes:
        words = len(s.get("narration", "").split())
        speech_budget = words / 2.4 + .25 if words else 0
        s["duration"] = round(min(MAX_SCENE, max(float(s["duration"]), speech_budget)), 3)
    total = sum(s["duration"] for s in scenes)
    target = max(min(MAX_TOTAL, target_seconds), min(MAX_TOTAL, total))
    add = max(0, target - total)
    priority = {"notice":1, "run":1.4, "knock":1.4, "jump":1.2,
                "shock":1.3, "slip":1.3, "recover":.9, "dance":1}
    for _ in range(50):
        if add <= .005:
            break
        eligible = [s for s in scenes if s["duration"] < MAX_SCENE-.005]
        if not eligible:
            break
        weight = sum(priority.get(s["action"],1) for s in eligible)
        used = 0
        for s in eligible:
            share = min(MAX_SCENE-s["duration"], add*priority.get(s["action"],1)/weight)
            s["duration"] += share
            used += share
        add = max(0, add - used)
    total = sum(s["duration"] for s in scenes)
    if total > MAX_TOTAL+.001:
        excess = total-MAX_TOTAL
        for _ in range(50):
            if excess<=.005:
                break
            eligible = [s for s in scenes if s["duration"]>.61]
            if not eligible:break
            cut = excess/len(eligible)
            for s in eligible:
                n=min(cut,s["duration"]-.6)
                s["duration"]-=n
                excess-=n
    for s in scenes:
        s["duration"] = round(s["duration"],2)
    # Per-scene rounding can otherwise push an exactly-12-second plan to 12.01.
    overflow = round(sum(s["duration"] for s in scenes)-MAX_TOTAL,2)
    if overflow>0:
        longest=max(scenes,key=lambda x:x["duration"])
        longest["duration"]=round(longest["duration"]-overflow,2)
    out["length"]=round(sum(s["duration"] for s in scenes),2)
    return out
