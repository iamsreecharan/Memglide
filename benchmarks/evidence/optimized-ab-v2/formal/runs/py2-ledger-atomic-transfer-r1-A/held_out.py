import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import atomic_transfer as core

class BehaviorTests(unittest.TestCase):
    def test_failure_has_no_partial_write(self):
        for args in (("a","b",6),("a","missing",1),("a","a",1),("a","b",True),("a","b",0)):
            balances = {"a":5,"b":2}
            with self.assertRaises(ValueError): api.transfer(balances, *args)
            self.assertEqual(balances, {"a":5,"b":2})
    def test_snapshot_and_exact_drain(self):
        balances = {"a":5,"b":2}
        result = core.transfer(balances,"a","b",5)
        self.assertEqual(balances,{"a":0,"b":7})
        result["a"] = 999
        self.assertEqual(balances["a"],0)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
