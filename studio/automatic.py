"""One-command CPU demo: text prompt -> storyboard + original music/SFX -> MP4."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from studio.core import ROOT, create_original_wav, plan_prompt, render, safe_path, validate


def run(prompt: str, output: str, silent: bool = False) -> Path:
    target = safe_path(ROOT, output, {".mp4"}, exists=False)
    if target.exists():
        raise FileExistsError(str(target))
    boardfile = target.with_suffix(".storyboard.json")
    if boardfile.exists():
        raise FileExistsError(str(boardfile))
    board = plan_prompt(prompt)
    if not silent:
        audio_dir = ROOT / "assets" / "audio"
        sources = [("original-night-music.wav", "music")]
        if board["scenes"][0]["environment"] == "bedroom":
            sources.append(("original-snore.wav", "snore"))
        for name, kind in sources:
            file = audio_dir / name
            if not file.exists():
                create_original_wav(file, kind)
        board["audio"] = [
            {"kind": "music", "file": "assets/audio/original-night-music.wav", "offset": 0., "volume": .48}
        ]
        if len(sources) == 2:
            board["audio"].append(
                {"kind": "sfx", "file": "assets/audio/original-snore.wav", "offset": 0., "volume": .72}
            )
    validate(board)
    render(board, target)
    boardfile.parent.mkdir(parents=True, exist_ok=True)
    boardfile.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("Video:", target)
    print("Editable plan:", boardfile)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline prompt-to-cartoon and original audio")
    parser.add_argument("prompt", help="English/Sinhala template keywords: bedroom snore, forest, beach")
    parser.add_argument("--out", default="output/animation.mp4")
    parser.add_argument("--silent", action="store_true", help="Do not generate/mix sample audio")
    args = parser.parse_args()
    run(args.prompt, args.out, args.silent)


if __name__ == "__main__":
    main()
