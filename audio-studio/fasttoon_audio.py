#!/usr/bin/env python3
"""FastToon repeatable audio pipeline: Kokoro-82M TTS + CPU cartoon Foley + mix.

Sound effects here are *procedural* open-code Foley, not model-generated AI SFX.
For text-prompt model SFX use stable_audio_sfx.py on a GPU after accepting license.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import wave
from pathlib import Path
from typing import Optional

import numpy as np

SR = 24000
TWO_PI = 2.0 * math.pi


def limit(signal: np.ndarray, peak: float = 0.86) -> np.ndarray:
    signal = np.asarray(signal, dtype=np.float32)
    mx = float(np.max(np.abs(signal))) if signal.size else 0.0
    return np.clip(signal * min(1.0, peak / max(1e-8, mx)), -1, 1)


def save_wav(path: str | Path, audio: np.ndarray, sr: int = SR):
    import soundfile as sf
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.asarray(audio, dtype=np.float32), sr, subtype="PCM_16")
    print("WAV_SAVED", path, "seconds", round(len(audio) / sr, 3), flush=True)


def tts(text: str, out: str, voice: str, speed: float, lang: str, cpu: bool):
    import torch
    from kokoro import KPipeline
    if cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        torch.set_num_threads(min(os.cpu_count() or 2, 4))
    pipeline = KPipeline(lang_code=lang)
    parts = []
    for _, _, audio in pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+'):
        parts.append(audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio))
    if not parts:
        raise RuntimeError("Kokoro generated no speech samples")
    pcm = np.concatenate([np.asarray(p, dtype=np.float32).reshape(-1) for p in parts])
    save_wav(out, limit(pcm, 0.94))


def smooth(x: np.ndarray) -> np.ndarray:
    return x * x * (3 - 2 * x)


def foley(kind: str, seconds: Optional[float], seed: int = 28) -> np.ndarray:
    """Scriptable cartoon SFX: deterministic enveloped oscillators and filtered noise."""
    defaults = {"whoosh": 0.52, "impact": 0.58, "pop": 0.19,
                "fart": 0.78, "footstep": 0.21, "room": 6.0, "sparkle": 0.75}
    if kind not in defaults:
        raise ValueError(f"Unknown SFX {kind}, choose {list(defaults)}")
    dur = seconds if seconds is not None else defaults[kind]
    n = max(80, round(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    p = np.clip(t / dur, 0, 1)
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=n).astype(np.float32)
    env = np.minimum(1, t * 45) * np.minimum(1, (dur - t) * 25)
    if kind == "whoosh":
        # Two moving resonances and gently smoothed noise.
        blurred = np.convolve(noise, np.ones(45, dtype=np.float32) / 45, mode="same")
        sweep = np.sin(TWO_PI * (110 * t + 180 * t * t / dur))
        v = (blurred * 5.0 + 0.18 * sweep) * np.sin(np.pi * p) ** 1.5
    elif kind == "impact":
        v = np.sin(TWO_PI * (86 * t - 62 * t * t / dur)) * np.exp(-10 * t / dur)
        v += noise * 0.25 * np.exp(-20 * t / dur)
    elif kind == "pop":
        v = (0.54 * noise + np.sin(TWO_PI * (190 * t - 80 * t * t / dur)))
        v *= np.exp(-21 * p)
    elif kind == "fart":
        inst = 47 + 24 * (1 - p) + 13 * np.sin(TWO_PI * 11 * t)
        phase = np.cumsum(inst / SR) * TWO_PI
        buzz = np.sin(phase) + .33 * np.sin(2 * phase) + .18 * np.sin(3 * phase)
        flutter = 0.62 + 0.38 * np.sin(TWO_PI * (15 * t + 6 * p * p))
        v = (buzz * flutter + 0.16 * noise) * (np.sin(np.pi * p) ** .45)
    elif kind == "footstep":
        v = (np.sin(TWO_PI * 65 * t) + noise * .16) * np.exp(-20 * p)
    elif kind == "sparkle":
        v = (np.sin(TWO_PI * (1100 * t + 1400 * t*t / dur))
             + 0.5 * np.sin(TWO_PI * 1800*t)) * (1-p)**2
    else:
        v = .015 * noise + .01 * np.sin(TWO_PI * 60 * t)
    return limit((v * env).astype(np.float32), .72)


def readaudio(path: str) -> np.ndarray:
    import soundfile as sf
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SR:
        duration = len(audio) / sr
        audio = np.interp(np.arange(round(duration * SR)) / SR,
                          np.arange(len(audio)) / sr, audio).astype(np.float32)
    return audio


def add_track(mix: np.ndarray, mono: np.ndarray, seconds: float, gain: float):
    i = round(seconds * SR)
    if i < 0:
        raise ValueError("Timeline offset must be non-negative")
    if i >= len(mix):
        return
    x = mono[:len(mix)-i] * gain
    mix[i:i+len(x)] += x


def build_scene(out: str, seconds: float, speech: Optional[str],
                timeline_json: Optional[str], metadata: Optional[str]):
    """Scene-safe defaults: no voice imitation, no headphones as default prop."""
    mono = foley("room", seconds)
    events = [
       {"at": .42, "type": "whoosh", "gain": .28},
       {"at": 1.58, "type": "whoosh", "gain": .45},
       {"at": 3.82, "type": "impact", "gain": .54},
       {"at": 5.54, "type": "fart", "gain": .66},
       {"at": 6.5, "type": "footstep", "gain": .25},
       {"at": 6.74, "type": "footstep", "gain": .30},
       {"at": 7.04, "type": "footstep", "gain": .30}
    ]
    if timeline_json:
        events = json.loads(Path(timeline_json).read_text(encoding="utf-8"))["events"]
    for event in events:
        add_track(mono, foley(event["type"], None,
                            seed=int(event.get("seed", 28))), float(event["at"]),
                  float(event.get("gain", .5)))
    if speech:
        add_track(mono, readaudio(speech), 0, .76)
    mono = limit(mono, .95)
    # Stereo micro-spatialization without altering lip-sync timestamps.
    delay = np.concatenate([np.zeros(19, dtype=np.float32), mono[:-19]])
    stereo = np.stack([mono * .96, mono * .90 + delay * .065], axis=-1)
    save_wav(out, stereo)
    if metadata:
        payload = {"sample_rate": SR, "seconds": seconds, "events": events,
                   "speech": speech, "character_defaults": {"headphones": False,
                                "superhero_cape": False, "girl_dress": "pink"}}
        Path(metadata).parent.mkdir(parents=True, exist_ok=True)
        Path(metadata).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("tts", help="Actual Kokoro 82M voice synthesis")
    p.add_argument("--text", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--voice", default="am_puck")
    p.add_argument("--speed", type=float, default=1.08)
    p.add_argument("--lang", default="a")
    p.add_argument("--cpu", action="store_true")
    p = commands.add_parser("sfx", help="Deterministic CPU procedural sound")
    p.add_argument("--type", required=True,
                   choices=["whoosh", "impact", "pop", "fart", "footstep", "room", "sparkle"])
    p.add_argument("--seconds", type=float)
    p.add_argument("--seed", type=int, default=28)
    p.add_argument("--out", required=True)
    p = commands.add_parser("scene", help="Mix timed SFX and optional speech into stereo")
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=9.0)
    p.add_argument("--speech")
    p.add_argument("--timeline")
    p.add_argument("--metadata")
    a = parser.parse_args()
    if a.command == "tts":
        tts(a.text, a.out, a.voice, a.speed, a.lang, a.cpu)
    elif a.command == "sfx":
        save_wav(a.out, foley(a.type, a.seconds, a.seed))
    else:
        build_scene(a.out, a.seconds, a.speech, a.timeline, a.metadata)


if __name__ == "__main__":
    main()
