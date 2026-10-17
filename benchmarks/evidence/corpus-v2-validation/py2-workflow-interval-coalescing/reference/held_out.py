import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import interval_coalescing as core

class BehaviorTests(unittest.TestCase):
    def test_nested_chains_adjacency_and_negatives(self):
        self.assertEqual(api.coalesce([[1,10],[2,3],[8,12],[12,15],[20,21]]),[[1,15],[20,21]])
        self.assertEqual(core.coalesce([[-5,-1],[-3,-2],[0,0]]),[[-5,-1]])
        self.assertEqual(api.coalesce([[1,2],[4,5],[3,4]]),[[1,2],[3,5]])
        self.assertEqual(api.coalesce([]),[])
    def test_input_and_errors(self):
        rows=[[3,5],[1,4]]; before=deepcopy(rows); result=api.coalesce(rows)
        self.assertEqual(rows,before); result[0][0]=999; self.assertEqual(rows,before)
        self.assertEqual(api.coalesce([[2,2]]),[])
        with self.assertRaises(ValueError): api.coalesce([[3,2]])

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
