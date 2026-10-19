import json, unittest
from datetime import date, datetime
from form import form_plus_decoding as core

class BehaviorTests(unittest.TestCase):
    def test_raw_plus_and_percent_order(self):
        self.assertEqual(core.decode_component("a+b%2Bc"),"a b+c")
        self.assertEqual(core.decode_component("++%2B+"),"  + ")
    def test_unicode_and_malformed(self):
        self.assertEqual(core.decode_component("caf%C3%A9+%E6%9D%B1%E4%BA%AC"),"café 東京")
        self.assertEqual(core.decode_component("%ZZ+%FF"),"%ZZ �")
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
