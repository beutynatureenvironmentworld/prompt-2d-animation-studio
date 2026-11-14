"""Validation, safe paths, audio timeline and deterministic templates."""
from __future__ import annotations
import copy
from pathlib import Path
import pytest
from studio.core import ROOT, audio_args, finite, plan_prompt, safe_path, validate, create_original_wav, render_frame
from studio.automatic import run


def test_repeatable_prompt():
    assert plan_prompt("bedroom snores") == plan_prompt("bedroom snores")
    assert plan_prompt("නිදන කාමරය")["scenes"][0]["environment"] == "bedroom"


def test_other_environment():
    assert plan_prompt("forest walking")["scenes"][0]["environment"] == "forest"


def test_basic_validation():
    assert validate(plan_prompt("bedroom"))


@pytest.mark.parametrize("field,bad", [("duration", 0), ("duration", float("nan")), ("action", "exec"), ("environment", "unknown"), ("character", "../../root")])
def test_scene_validation(field, bad):
    board = plan_prompt("bedroom")
    board["scenes"][0][field] = bad
    with pytest.raises(ValueError):
        validate(board)


def test_audio_tracks_safe(tmp_path):
    (tmp_path / "test.wav").write_bytes(b"test")
    board = plan_prompt("bedroom")
    board["audio"] = [{"kind": "music", "file": "test.wav", "offset": 1.25, "volume": .4}]
    validate(board, tmp_path)
    argv = audio_args("ffmpeg", Path("/tmp/silent.mp4"), board["audio"], tmp_path, Path("/tmp/out.mp4"))
    filters = argv[argv.index("-filter_complex") + 1]
    assert "adelay=1250:all=1" in filters and "volume=0.4000" in filters
    assert "amix=inputs=1" in filters


def test_reject_timeline_beyond_video(tmp_path):
    (tmp_path / "test.wav").write_bytes(b"test")
    board = plan_prompt("bedroom")
    board["audio"] = [{"kind": "sfx", "file": "test.wav", "offset": 60, "volume": 1}]
    with pytest.raises(ValueError):
        validate(board, tmp_path)


def test_path_security(tmp_path):
    (tmp_path / "ok.mp4").write_bytes(b"x")
    assert safe_path(tmp_path, "ok.mp4", {".mp4"}).exists()
    for path in ("../outside.mp4", "/tmp/outside.mp4", "..\\outside.mp4"):
        with pytest.raises(ValueError):
            safe_path(tmp_path, path, {".mp4"})


def test_symlink_escape(tmp_path):
    outside = tmp_path.parent / "outside-file.wav"
    outside.write_bytes(b"x")
    (tmp_path / "escape.wav").symlink_to(outside)
    with pytest.raises(ValueError):
        safe_path(tmp_path, "escape.wav", {".wav"})
    outside.unlink()


def test_duplicate_ids():
    board = plan_prompt("bedroom")
    board["scenes"][1]["id"] = board["scenes"][0]["id"]
    with pytest.raises(ValueError):
        validate(board)


def test_frame_has_real_pixels_and_movement():
    scene = plan_prompt("bedroom")["scenes"][0]
    a = render_frame(scene, .2, 320, 180)
    b = render_frame(scene, 1.2, 320, 180)
    assert a.size == b.size == (320, 180)
    assert a.tobytes() != b.tobytes()


def test_synth_original_audio(tmp_path):
    p = tmp_path / "original.wav"
    create_original_wav(p, "music", 1.0)
    assert p.stat().st_size > 10000
    with pytest.raises(FileExistsError):
        create_original_wav(p, "music", 1.0)


def test_finite():
    assert finite(2, .1, 10, "sec") == 2.
    with pytest.raises(ValueError):
        finite(float("inf"), .1, 10, "sec")
