"""Run with python3 -m unittest discover -s hybrid-gpu/tests -v."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("provider_readiness", ROOT / "hybrid-gpu/provider_readiness.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProviderReadinessTests(unittest.TestCase):
    def test_repository_and_graphs(self):
        r = MODULE.inspect(ROOT, {})
        self.assertTrue(r["repository"]["required_files_present"])
        self.assertTrue(all(x["valid_json"] for x in r["repository"]["comfy_graphs"].values()))

    def test_no_unverified_gpu_claims(self):
        r = MODULE.inspect(ROOT, {})
        self.assertTrue(all(not p["gpu_video_render_verified"] for p in r["providers"].values()))

    def test_secret_values_not_printed(self):
        secret = "SUPER_SECRET_NEVER_PRINT_8f92"
        r = MODULE.inspect(ROOT, {
            "KAGGLE_USERNAME": "someone", "KAGGLE_API_TOKEN": secret,
            "R2_BUCKET": "bucket", "R2_ENDPOINT": "https://example.invalid",
            "AWS_ACCESS_KEY_ID": secret, "AWS_SECRET_ACCESS_KEY": secret,
        })
        self.assertNotIn(secret, json.dumps(r))
        self.assertTrue(r["providers"]["kaggle"]["account_fields_set"])
        self.assertTrue(r["r2"]["configuration_fields_set"])

    def test_empty_repository_not_ready(self):
        with tempfile.TemporaryDirectory() as empty:
            r = MODULE.inspect(Path(empty), {})
            self.assertFalse(r["repository"]["required_files_present"])
            self.assertFalse(r["repository"]["comfy_graphs"]["ltx"]["valid_json"])


if __name__ == "__main__":
    unittest.main()
