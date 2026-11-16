"""Heuristic storyboard QA. Warns; does not pretend to perceive finished animation."""
def review_plan(plan, asset_pack=None):
    warnings = []
    scenes = plan.get("scenes", [])
    actions = [s.get("action") for s in scenes]
    length = sum(float(s.get("duration", 0)) for s in scenes)
    if length < 8.0:
        warnings.append("Comedy setup/punchline may feel rushed: timeline under 8 seconds")
    if "run" in actions and "knock" in actions and actions.index("knock") < actions.index("run"):
        warnings.append("Door contact occurs before the approach; rearrange story beats")
    if not any(a in actions for a in ("shock", "slip", "jump", "dance")):
        warnings.append("No clear unexpected physical punchline; include a reaction or visual reversal")
    if len({s.get("location") for s in scenes}) > 2:
        warnings.append("Too many location changes can break visual continuity")
    for i, s in enumerate(scenes):
        words = len(s.get("narration", "").split())
        # espeak at about 155 wpm: >2.6 words/s is a potential clipping hazard
        seconds = float(s.get("duration", 1))
        if words and words / seconds > 2.6:
            warnings.append(f"Scene {i+1} narration may be cut off; use fewer words or a longer scene")
    if asset_pack is not None and asset_pack.root is not None:
        if (asset_pack.root / "reference_character.png").is_file():
            warnings.append("Character reference sheet is stored but not image-conditioned into the vector actor")
        if not asset_pack.notes:
            warnings.append("No character/story memory loaded: add style.md, story_bible.md or memory.md")
    return warnings
