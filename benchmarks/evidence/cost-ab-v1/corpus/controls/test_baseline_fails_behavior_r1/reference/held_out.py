import json, unittest
from datetime import date, datetime
from inventory import reorder_inclusive as core
from inventory import reorder_inclusive_api as api

class BehaviorTests(unittest.TestCase):
    def test_inclusive_boundary_and_public_order(self):
        self.assertTrue(core.reorder_needed(3,3))
        self.assertEqual(api.reorder_skus([("z",1,2),("A",2,2),("z",0,4)]),["z","A","z"])
    def test_negatives_empty_and_unchanged(self):
        rows=[("b",-2,-1),("a",2,1),("b",-1,-1)]
        self.assertEqual(api.reorder_skus(rows),["b","b"])
        self.assertEqual(rows,[("b",-2,-1),("a",2,1),("b",-1,-1)])
        self.assertEqual(api.reorder_skus([]),[])
        self.assertFalse(core.reorder_needed(2,1))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
