import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import utf8_batch_budget as core

class BehaviorTests(unittest.TestCase):
    def test_unicode_boundaries_and_order(self):
        self.assertEqual(api.batch_messages(["é","é","a","😀"],4),[["é","é"],["a"],["😀"]])
        self.assertEqual(core.batch_messages(["","a","","b"],1),[["","a",""],["b"]])
        self.assertEqual(api.batch_messages([],1),[])
        with self.assertRaises(ValueError): api.batch_messages(["😀"],3)
    def test_validation_and_input(self):
        values=["a","a","b"]; self.assertEqual(api.batch_messages(values,2),[["a","a"],["b"]]); self.assertEqual(values,["a","a","b"])
        for budget in (0,-1,True,1.5):
            with self.assertRaises(ValueError): api.batch_messages([],budget)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
