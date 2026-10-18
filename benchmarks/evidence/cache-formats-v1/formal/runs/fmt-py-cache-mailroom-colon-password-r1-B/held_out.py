import json, unittest
from datetime import date, datetime
from mailroom import colon_password as core

class BehaviorTests(unittest.TestCase):
    def test_password_colons_and_unicode(self):
        import base64
        for user,password in (("user","a:b:c"),("","secret"),("user",""),("é","東京:x")):
            header="bAsIc "+base64.b64encode((user+":"+password).encode()).decode()
            self.assertEqual(core.parse_basic_credentials(header),(user,password))
    def test_malformed_headers(self):
        for header in ("Basic", "Bearer dTpw", "Basic ", "Basic dT pw", "Basic @@@", "Basic dXNlcg==", "Basic /zo="):
            with self.assertRaises(ValueError): core.parse_basic_credentials(header)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
