import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import capped_backoff as core

class BehaviorTests(unittest.TestCase):
    def test_exponential_zero_and_cap(self):
        self.assertEqual([api.backoff(n,3,20) for n in range(6)],[3,6,12,20,20,20])
        self.assertEqual(core.backoff(10**9,1,99),99)
        self.assertEqual(api.backoff(10**9,0,99),0)
        self.assertEqual(api.backoff(3,4,0),0)
        self.assertEqual(api.backoff(0,100,5),5)
    def test_exactness_and_validation(self):
        self.assertEqual(api.backoff(100,3,10**40),3*2**100)
        for args in ((-1,1,2),(0,-1,2),(0,1,-2),(True,1,2),(0,1.2,2)):
            with self.assertRaises(ValueError): api.backoff(*args)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
