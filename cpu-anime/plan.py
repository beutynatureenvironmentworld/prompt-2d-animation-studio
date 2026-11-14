"""Validate a bounded, editable prompt-driven storyboard. Prompts are data only."""
from __future__ import annotations
import json
import math
from pathlib import Path

ACTIONS = ("walk", "wave", "blink", "look", "wind", "lantern")

def make_plan(prompt: str, duration: float, fps: int) -> dict:
    if not isinstance(prompt, str) or not (1 <= len(prompt) <= 500) or any(ord(ch) < 32 and ch not in "\t\n" for ch in prompt):
        raise ValueError("Prompt must contain 1-500 printable characters")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 2 <= duration <= 12:
        raise ValueError("Duration must be 2-12 seconds")
    if isinstance(fps, bool) or not isinstance(fps, int) or not 8 <= fps <= 24:
        raise ValueError("FPS must be 8-24")
    recognized = [action for action in ACTIONS if action in prompt.lower()]
    return {"schema": 1, "prompt": prompt, "duration": float(duration), "fps": fps,
            "actions": recognized or ["walk", "wave", "blink", "wind"],
            "sound": False, "model": "authored-template-not-generative-ai"}

def safe_output(output: Path, root: Path) -> Path:
    root = root.resolve()
    path = output.absolute()
    if path.exists() or path.is_symlink():
        raise FileExistsError("Refusing to overwrite output")
    if not path.parent.resolve().is_relative_to(root):
        raise ValueError("Output must be inside designated root")
    if path.suffix.lower() not in {".mp4", ".json", ".png"}:
        raise ValueError("Unsupported output extension")
    return path

def write_plan(plan: dict, output: Path, root: Path) -> Path:
    out = safe_output(output, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
