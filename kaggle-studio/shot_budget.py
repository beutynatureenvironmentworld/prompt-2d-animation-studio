"""Choose 1-2 expensive motion shots; leave most video to CPU vector rendering."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

MOTION = {"chase": 10, "trip": 9, "catch": 8, "grab": 7, "sneak": 5}
ACTIONS = MOTION.keys()


def select(board: dict, max_shots: int = 2, max_frames: int = 48) -> list[dict]:
    if not isinstance(board, dict) or not isinstance(board.get("shots"), list):
        raise ValueError("Expected editable Snap2D storyboard with shots")
    fps = board.get("fps")
    if type(fps) is not int or not 12 <= fps <= 60:
        raise ValueError("Invalid FPS")
    if type(max_shots) is not int or not 1 <= max_shots <= 2:
        raise ValueError("Only 1 or 2 GPU shots per episode by default")
    if type(max_frames) is not int or not 8 <= max_frames <= 48:
        raise ValueError("Max 8-48 frames per GPU shot")
    candidates = []
    for i, shot in enumerate(board["shots"]):
        if not isinstance(shot, dict):
            raise ValueError("Invalid shot")
        action = shot.get("action")
        if action not in MOTION:
            continue
        start, duration = shot.get("start"), shot.get("duration")
        if not isinstance(start, (int, float)) or not isinstance(duration, (int, float)):
            raise ValueError("Invalid timing")
        if start < 0 or not 0.3 <= duration <= 20:
            raise ValueError("Unsafe scene timing")
        frames = min(max_frames, max(8, round(duration * fps)))
        candidates.append((MOTION[action], i, {
            "start_frame": round(start * fps),
            "frames": frames,
            "seed": 2317 + i,
            "prompt": (
                "Original expressive 2D hand-inked stick figure comedy, consistent character "
                "with oversized expressive face, thick black outlines, olive-grey flat background. "
                "Short pose-to-pose action: " + action + ". Fast readable silhouette."
            ),
        }))
    picks = sorted(sorted(candidates, key=lambda t: (-t[0], t[1]))[:max_shots], key=lambda t: t[2]["start_frame"])
    result = [p[2] for p in picks]
    if not result:
        raise ValueError("No supported dynamic action found; keep CPU-only")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-shots", type=int, choices=[1, 2], default=2)
    args = parser.parse_args()
    board = json.loads(args.storyboard.read_text(encoding="utf8"))
    result = select(board, max_shots=args.max_shots)
    if args.out.exists():
        parser.error("Will not overwrite shot plan")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print("Selected", len(result), "GPU candidate shot(s); remaining shots are CPU")


if __name__ == "__main__":
    main()
