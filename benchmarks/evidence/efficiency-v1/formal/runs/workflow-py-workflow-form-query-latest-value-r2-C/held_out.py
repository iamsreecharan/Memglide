import json, unittest
from datetime import date, datetime
from form import query_latest_value as core
from form import query_latest_value_api as api

class BehaviorTests(unittest.TestCase):
    def test_repeats_and_first_key_order(self):
        pairs=[("A","1"),("b","2"),("A","3"),("b","4")]
        result=core.latest_values(pairs)
        self.assertEqual(result,{"A":"3","b":"4"})
        self.assertEqual(list(result),["A","b"])
    def test_adapter_exact_case_default_and_preservation(self):
        pairs=[("A","first"),("a","lower"),("A","last")]
        self.assertEqual(api.query_value(pairs,"A"),"last")
        self.assertEqual(api.query_value(pairs,"missing"," fallback ")," fallback ")
        self.assertEqual(pairs,[("A","first"),("a","lower"),("A","last")])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
