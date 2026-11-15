import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(filename):
    spec = importlib.util.spec_from_file_location(filename, ROOT / (filename + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StudioTests(unittest.TestCase):
    def test_generated_kaggle_kernel_is_private_and_syntax_valid(self):
        maker = load("dispatch")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "prepared"
            kernel = maker.create_job(path, "exampleuser", "probe", 4, "smoke1")
            self.assertTrue(kernel.startswith("exampleuser/vidbest-probe"))
            info = json.loads((path / "kernel-metadata.json").read_text())
            self.assertTrue(info["is_private"])
            self.assertTrue(info["enable_gpu"])
            self.assertEqual(info["machine_shape"], "NvidiaTeslaT4")
            self.assertFalse(info["enable_internet"])
            source = (path / "gpu_job.py").read_text()
            ast.parse(source)
            self.assertIn("KAGGLE_STUDIO_MODE = 'probe'", source)
            with self.assertRaises(FileExistsError):
                maker.create_job(path, "exampleuser", "probe", 4, "smoke1")

    def test_gpu_pose_mode_is_distinct(self):
        maker = load("dispatch")
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "job"
            maker.create_job(p, "example", "pose-ai", 12, "pose")
            self.assertTrue(json.loads((p / "kernel-metadata.json").read_text())["enable_internet"])

    def test_invalid_owner_and_time_rejected(self):
        maker = load("dispatch")
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                maker.create_job(Path(folder) / "a", "../../secrets", "probe", 4)
            with self.assertRaises(ValueError):
                maker.create_job(Path(folder) / "b", "example", "pose-ai", 45)

    def test_gpu_shot_policy_limits_to_two_dynamic_shots(self):
        planner = load("shot_budget")
        board = json.loads((ROOT.parent / "snap2d/examples/storyboard_cookie.json").read_text())
        chosen = planner.select(board)
        self.assertEqual(len(chosen), 2)
        self.assertTrue(all(s["frames"] <= 48 for s in chosen))
        self.assertTrue(chosen[0]["start_frame"] < chosen[1]["start_frame"])
        self.assertEqual(len(planner.select(board, max_shots=1)), 1)

    def test_rejects_invalid_storyboard(self):
        planner = load("shot_budget")
        with self.assertRaises(ValueError):
            planner.select({"fps": 0, "shots": []})


if __name__ == "__main__":
    unittest.main()
