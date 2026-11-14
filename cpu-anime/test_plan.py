import math
import tempfile
import unittest
from pathlib import Path
from plan import make_plan, safe_output

class TestScenePlan(unittest.TestCase):
    def test_valid(self):
        self.assertIn("wave", make_plan("wave and blink", 5, 15)["actions"])
    def test_default(self):
        self.assertTrue(make_plan("hello", 3, 12)["actions"])
    def test_empty(self):
        with self.assertRaises(ValueError): make_plan("", 5, 15)
    def test_injection_as_data(self):
        p=make_plan("wave; rm -rf /", 3, 12)
        self.assertIn("rm -rf", p["prompt"])
    def test_duration(self):
        for value in (float("nan"), float("inf"), -1, 100):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_plan("walking", value, 12)
    def test_fps(self):
        for value in (0, 25, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_plan("walking", 3, value)
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"out";root.mkdir()
            with self.assertRaises(ValueError):
                safe_output(Path(d)/"unsafe.mp4",root)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/"existing.mp4";out.write_bytes(b"x")
            with self.assertRaises(FileExistsError):safe_output(out,root)

if __name__ == "__main__": unittest.main()
