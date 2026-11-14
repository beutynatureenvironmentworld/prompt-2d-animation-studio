"""CPU-first prompt -> editable storyboard -> 2D animation + original audio -> MP4.

Offline template engine; no arbitrary code execution, AI-video model or GPU required.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import re
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MEDIA = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm", ".mov"}
AUDIO = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac"}
ACTIONS = {"snore", "annoyed", "wake", "react", "walk", "wave", "stand"}
ENVIRONMENTS = {"bedroom", "forest", "meadow", "beach"}
CHARACTERS = {"sleeping_stick", "awake_stick", "nila"}
TRACKS = {"narration", "music", "singing", "sfx"}
ID = re.compile(r"^[a-z][a-z0-9_-]{0,40}$")


def safe_path(root: Path, value: str, allowed: set[str], exists: bool = True) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value or "\\" in value:
        raise ValueError("Invalid path")
    part = Path(value)
    if part.is_absolute() or ".." in part.parts or value.startswith("~"):
        raise ValueError("Absolute or traversing paths are forbidden")
    base = root.resolve()
    path = (base / part).resolve(strict=exists)
    if not path.is_relative_to(base) or path.suffix.lower() not in allowed:
        raise ValueError("File escaped project or unsupported extension")
    if exists and not path.is_file():
        raise ValueError("Asset does not exist")
    return path


def finite(value: object, low: float, high: float, label: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be between {low} and {high}")
    return float(value)


def validate(plan: dict, root: Path = ROOT) -> dict:
    if not isinstance(plan, dict) or plan.get("version") != 1:
        raise ValueError("Storyboard version 1 required")
    video = plan.get("video")
    if not isinstance(video, dict) or (video.get("width"), video.get("height")) not in {
        (320, 180), (640, 360), (1280, 720)
    } or type(video.get("fps")) is not int or video["fps"] not in (12, 18, 24, 30):
        raise ValueError("Use 16:9 (320,640,1280) and FPS 12/18/24/30")
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 8:
        raise ValueError("1-8 scenes required")
    found = set()
    total = 0.0
    for scene in scenes:
        if not isinstance(scene, dict) or not isinstance(scene.get("id"), str):
            raise ValueError("Invalid scene")
        sid = scene["id"]
        if not ID.fullmatch(sid) or sid in found:
            raise ValueError("Unsafe/duplicate scene id")
        found.add(sid)
        total += finite(scene.get("duration"), .5, 15, "duration")
        if scene.get("environment") not in ENVIRONMENTS or scene.get("action") not in ACTIONS:
            raise ValueError("Unknown scene template/action")
        if scene.get("character") not in CHARACTERS:
            raise ValueError("Unknown reusable character")
        ref = scene.get("reference", "")
        if ref:
            safe_path(root, ref, MEDIA)
        if not isinstance(scene.get("caption", ""), str) or len(scene.get("caption", "")) > 200:
            raise ValueError("Invalid caption")
    tracks = plan.get("audio", [])
    if not isinstance(tracks, list) or len(tracks) > 16:
        raise ValueError("Invalid track count")
    for track in tracks:
        if not isinstance(track, dict) or track.get("kind") not in TRACKS:
            raise ValueError("Unknown audio kind")
        safe_path(root, track.get("file", ""), AUDIO)
        finite(track.get("offset"), 0, total, "audio.offset")
        finite(track.get("volume"), 0, 2, "audio.volume")
    return plan


def plan_prompt(prompt: str) -> dict:
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 2000:
        raise ValueError("Prompt must contain 1-2000 characters")
    p = prompt.lower()
    is_night = any(v in p for v in ("bed", "snor", "sleep", "night", "නිදන", "ගොරවන", "ඇඳ", "රාත්‍රී"))
    env = ("bedroom" if is_night else "beach" if any(v in p for v in ("beach", "sea", "වෙරළ"))
           else "forest" if any(v in p for v in ("forest", "tree", "වනාන්තර")) else "meadow")
    scenes = (
        [("night_snoring", "snore", "sleeping_stick"), ("annoyed_reaction", "annoyed", "awake_stick")]
        if is_night else [("opening", "walk", "nila"), ("greeting", "wave", "nila")]
    )
    return {
        "version": 1, "prompt": prompt, "video": {"width": 640, "height": 360, "fps": 18},
        "scenes": [
            {"id": sid, "duration": 3.5 if is_night else 2.5, "environment": env,
             "action": action, "character": ch, "caption": "", "reference": ""}
            for sid, action, ch in scenes
        ], "audio": []
    }


def create_original_wav(destination: Path, kind: str, seconds: float = 7.0) -> None:
    """Small deterministic original synth demonstration, NOT Sinhala TTS."""
    if kind not in {"music", "snore"} or destination.suffix.lower() != ".wav":
        raise ValueError("Unknown original sample")
    finite(seconds, 1, 120, "audio seconds")
    if destination.exists():
        raise FileExistsError(str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    rate = 22050
    tones = (196., 246.94, 293.66)
    melody = (392., 329.63, 293.66, 246.94, 261.63, 293.66, 220.)
    rnd = random.Random(7821)
    samples = []
    for i in range(round(rate * seconds)):
        t = i / rate
        if kind == "music":
            fade = min(1., t / .55, max(0., (seconds - t) / .5))
            body = sum(math.sin(2 * math.pi * f * t + .2 * j) for j, f in enumerate(tones)) / 3
            beat = t * 1.7
            pluck = math.sin(2 * math.pi * melody[int(beat) % len(melody)] * t)
            v = .18 * fade * (.48 * body + .45 * pluck * math.exp(-5 * (beat % 1)))
        else:
            phase = t % 2.2
            breath = max(0., math.sin(math.pi * phase / 1.6)) ** 2 if phase < 1.6 else 0.
            v = .34 * breath * (.55 * math.sin(2 * math.pi * (81 + 8 * math.sin(t * 2)) * t)
                                 + .21 * rnd.uniform(-1, 1))
        samples.append(max(-32767, min(32767, int(v * 32767))))
    with wave.open(str(destination), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(struct.pack("<" + str(len(samples)) + "h", *samples))


def outdoor_frame(scene: dict, t: float, width: int, height: int) -> Image.Image:
    """A separate authored outdoor template with a reusable stylized Nila rig."""
    img = Image.new("RGB", (width, height), "#a9d2dc")
    d = ImageDraw.Draw(img)
    s = width / 640
    q = lambda x: round(x * s)
    env = scene["environment"]
    for y in range(height):
        f = y / height
        d.line((0, y, width, y), fill=(int(104 + f * 92), int(168 + f * 59), int(210 - f * 54)))
    d.ellipse((q(495), q(43), q(566), q(114)), fill="#fff0bd")
    for x, y in ((110, 74), (386, 48), (542, 84)):
        xx = x + 16 * math.sin(t * .25)
        for dx, dy, radius in ((-12, 4, 23), (11, 0, 28), (0, -8, 20)):
            d.ellipse((q(xx + dx - radius), q(y + dy - 10), q(xx + dx + radius), q(y + dy + 12)), fill="#f9f0d9")
    d.ellipse((q(-170), q(190), q(390), q(440)), fill="#77a994")
    d.ellipse((q(260), q(184), q(790), q(438)), fill="#619c83")
    d.ellipse((q(-80), q(263), q(800), q(550)), fill="#8bb779" if env != "beach" else "#eac995")
    for j, x in enumerate((48, 149, 279, 447, 593)):
        sway = 7 * math.sin(t * .8 + j)
        if env != "beach":
            d.line((q(x), q(273), q(x + sway), q(196)), fill="#3e684c", width=q(8))
            d.ellipse((q(x - 28 + sway), q(169), q(x + 31 + sway), q(229)), fill="#427f59")
    walking = scene["action"] == "walk"
    cx = (130 + 330 * min(1, t / float(scene["duration"]))) if walking else 420
    cy = 250 + (3 * math.cos(t * 13) if walking else 0)
    swing = 13 * math.sin(t * 8) if walking else 0
    d.line((q(cx - 8), q(cy + 35), q(cx - 13 + swing), q(318)), fill="#394a60", width=q(8))
    d.line((q(cx + 8), q(cy + 35), q(cx + 14 - swing), q(318)), fill="#394a60", width=q(8))
    d.polygon([(q(cx - 18), q(cy - 15)), (q(cx + 16), q(cy - 15)),
               (q(cx + 22), q(cy + 38)), (q(cx - 23), q(cy + 38))], fill="#427da2")
    d.line((q(cx - 15), q(cy - 10), q(cx - 29 - swing), q(cy + 21)), fill="#bc8b68", width=q(7))
    arm_end = (cx + 33, cy - 39 + 8 * math.sin(t * 7)) if scene["action"] == "wave" else (cx + 26 + swing, cy + 18)
    d.line((q(cx + 14), q(cy - 8), q(arm_end[0]), q(arm_end[1])), fill="#bc8b68", width=q(7))
    d.ellipse((q(cx - 22), q(cy - 62), q(cx + 22), q(cy - 17)), fill="#293943")
    d.ellipse((q(cx - 17), q(cy - 55), q(cx + 17), q(cy - 23)), fill="#e1ab81")
    for dx in (-7, 7):
        d.ellipse((q(cx + dx - 2), q(cy - 39), q(cx + dx + 2), q(cy - 35)), fill="#30343a")
    d.arc((q(cx - 8), q(cy - 36), q(cx + 9), q(cy - 24)), 2, 178, fill="#8e5b50", width=q(2))
    return img


def render_frame(scene: dict, t: float, width: int, height: int) -> Image.Image:
    if scene["environment"] == "bedroom":
        from studio.bedroom import draw_bedroom
        return draw_bedroom(t, scene["action"], width, height)
    return outdoor_frame(scene, t, width, height)


def render_clip(scene: dict, output: Path, video: dict, ffmpeg: str) -> None:
    w, h, fps = video["width"], video["height"], video["fps"]
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for i in range(round(scene["duration"] * fps)):
            process.stdin.write(render_frame(scene, i / fps, w, h).tobytes())
        process.stdin.close()
        assert process.stderr is not None
        stderr = process.stderr.read().decode("utf8", errors="replace")
        if process.wait():
            raise RuntimeError(stderr)
    except Exception:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
        process.kill()
        process.wait()
        raise


def audio_args(ffmpeg: str, silent: Path, tracks: list[dict], root: Path, target: Path) -> list[str]:
    args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent)]
    filters = []
    streams = []
    for i, track in enumerate(tracks):
        args.extend(["-i", str(safe_path(root, track["file"], AUDIO))])
        ms = round(track["offset"] * 1000)
        filters.append(f"[{i + 1}:a]aresample=async=1:first_pts=0,adelay={ms}:all=1,volume={track['volume']:.4f}[a{i}]")
        streams.append(f"[a{i}]")
    filters.append("".join(streams) + f"amix=inputs={len(tracks)}:duration=longest:dropout_transition=0,apad[mix]")
    return args + ["-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[mix]",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                   "-movflags", "+faststart", str(target)]


def render(plan: dict, output: Path, root: Path = ROOT) -> None:
    validate(plan, root)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("Missing FFmpeg; install ffmpeg before rendering")
    if output.exists() or not output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Output must be a NEW project-local MP4")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="prompt2d-") as directory:
        work = Path(directory)
        clips = []
        for scene in plan["scenes"]:
            clip = work / (scene["id"] + ".mp4")
            render_clip(scene, clip, plan["video"], ffmpeg)
            clips.append(clip)
        manifest = work / "clips.txt"
        manifest.write_text("".join("file '" + clip.name + "'\n" for clip in clips), encoding="utf8")
        silent = work / "silent.mp4"
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                        "-f", "concat", "-safe", "0", "-i", str(manifest),
                        "-c", "copy", "-movflags", "+faststart", str(silent)], check=True)
        if plan.get("audio"):
            subprocess.run(audio_args(ffmpeg, silent, plan["audio"], root, output), check=True)
        else:
            shutil.copyfile(silent, output)


def main() -> None:
    parser = argparse.ArgumentParser(description="CPU-first, prompt-driven 2D video studio")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("plan")
    p.add_argument("prompt")
    p.add_argument("--out", default="storyboard.json")
    v = sub.add_parser("validate")
    v.add_argument("storyboard")
    r = sub.add_parser("render")
    r.add_argument("storyboard")
    r.add_argument("--out", required=True)
    a = sub.add_parser("audio-demo")
    a.add_argument("--out-dir", default="assets/audio")
    e = sub.add_parser("extend")
    e.add_argument("storyboard")
    e.add_argument("--seconds", type=float, required=True)
    e.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.cmd == "doctor":
        for name in ("python3", "node", "npm", "ffmpeg", "ffprobe"):
            print(f"{name}: {shutil.which(name) or 'NOT INSTALLED'}")
        print("Pillow:", __import__("PIL").__version__)
        return
    if args.cmd == "audio-demo":
        directory = (ROOT / args.out_dir).resolve()
        if not directory.is_relative_to(ROOT):
            raise ValueError("Audio target must stay inside project")
        create_original_wav(directory / "original-night-music.wav", "music")
        create_original_wav(directory / "original-snore.wav", "snore")
        print("Created original synthesized music + SFX")
        return
    if args.cmd == "plan":
        board = plan_prompt(args.prompt)
        destination = safe_path(ROOT, args.out, {".json"}, exists=False)
        if destination.exists():
            raise FileExistsError(str(destination))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf8")
        print("Storyboard:", destination)
        return
    storyboard = safe_path(ROOT, args.storyboard, {".json"})
    board = validate(json.loads(storyboard.read_text(encoding="utf8")))
    if args.cmd == "validate":
        print("Valid storyboard, scenes:", len(board["scenes"]))
    elif args.cmd == "render":
        out = safe_path(ROOT, args.out, {".mp4"}, exists=False)
        render(board, out)
        print("Wrote", out)
    elif args.cmd == "extend":
        seconds = finite(args.seconds, .1, 10, "extend seconds")
        board["scenes"][-1]["duration"] += seconds
        validate(board)
        target = safe_path(ROOT, args.out, {".json"}, exists=False)
        if target.exists():
            raise FileExistsError(str(target))
        target.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf8")
        print("Extended storyboard:", target)


if __name__ == "__main__":
    main()
