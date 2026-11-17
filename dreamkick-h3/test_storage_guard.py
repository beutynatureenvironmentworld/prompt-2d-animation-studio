import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from storage_guard import inspect,REQUIRED
class StorageGuardTests(unittest.TestCase):
 def test_missing_cache_never_ready(self):
  with tempfile.TemporaryDirectory() as root:
   a=inspect(root);self.assertFalse(a['cache_complete']);self.assertFalse(a['gpu_started'])
 def test_base_fp8_is_not_singularity(self):
  with tempfile.TemporaryDirectory() as root:
   root=Path(root)
   for role,(folder,name) in REQUIRED.items():
    if role=='singularity_ref2va_int8':continue
    p=root/folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'x'*12)
   p=root/'diffusion_models'/'minimax_h3_ref2va_pruned_fp8_scaled.safetensors';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'x'*12)
   self.assertFalse(inspect(root,strict_min_bytes=1)['cache_complete'])
 def test_complete_mock_does_not_pass_real_byte_size(self):
  with tempfile.TemporaryDirectory() as root:
   root=Path(root)
   for folder,name in REQUIRED.values():
    p=root/folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'x'*12)
   self.assertTrue(inspect(root,strict_min_bytes=1)['cache_complete'])
   self.assertFalse(inspect(root)['cache_complete'])
if __name__=='__main__':unittest.main()
