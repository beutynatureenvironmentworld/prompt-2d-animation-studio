import importlib.util,io,json
from pathlib import Path
import unittest
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("check_horde_key",ROOT/"check_horde_key.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Response:
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return json.dumps({"username":"confirmed-user","kudos":5000,"id":62}).encode("utf8")

class Tests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(m.check("")["status"],"missing")
    def test_valid_never_returns_username_or_key(self):
        def fake(req,timeout):
            self.assertEqual(req.get_header("Apikey"),"TOPSECRET")
            self.assertEqual(timeout,20)
            return Response()
        status=m.check("TOPSECRET",fake)
        self.assertTrue(status["authenticated"])
        self.assertNotIn("TOPSECRET",str(status))
        self.assertNotIn("confirmed-user",str(status))
    def test_rejected(self):
        def fake(req,timeout):
            raise HTTPError("https://example.invalid",401,"Unauthorized",{},None)
        self.assertEqual(m.check("test",fake)["status"],"rejected")
    def test_network_failure(self):
        def fake(req,timeout):
            raise URLError("offline")
        self.assertEqual(m.check("test",fake)["status"],"network_or_response_error")
if __name__=="__main__":unittest.main()
