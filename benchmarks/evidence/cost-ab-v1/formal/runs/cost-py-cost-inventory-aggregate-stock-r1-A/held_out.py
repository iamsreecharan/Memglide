import json, unittest
from datetime import date, datetime
from inventory import aggregate_stock as core

class BehaviorTests(unittest.TestCase):
    def test_repeated_skus_and_first_seen_order(self):
        rows=[("A",2),("B",4),("A",-1),("C",0),("B",3)]
        result=core.aggregate_stock(rows)
        self.assertEqual(result,{"A":1,"B":7,"C":0})
        self.assertEqual(list(result),["A","B","C"])
    def test_empty_case_sensitive_and_unchanged(self):
        rows=[("a",2),("A",1),("a",0)]
        self.assertEqual(core.aggregate_stock(rows),{"a":2,"A":1})
        self.assertEqual(rows,[("a",2),("A",1),("a",0)])
        self.assertEqual(core.aggregate_stock([]),{})
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
