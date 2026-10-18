import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import ready_job_order as core

class BehaviorTests(unittest.TestCase):
    def test_due_priority_and_stable_ties(self):
        jobs=[{"id":k,"status":s,"due":due,"priority":p} for k,s,due,p in (("low","queued",0,1),("a","queued",1,9),("future","queued",2,99),("b","queued",0,9),("running","running",0,100))]
        self.assertEqual([j["id"] for j in api.ready_jobs(jobs,1,3)],["a","b","low"])
        self.assertEqual([j["id"] for j in core.ready_jobs(jobs,1,1)],["a"])
        self.assertEqual(api.ready_jobs(jobs,1,0),[])
        self.assertEqual(jobs[0]["id"],"low")
    def test_detachment_and_limits(self):
        jobs=[{"id":"a","status":"queued","due":0,"priority":1,"data":[1]}]
        result=api.ready_jobs(jobs,0,5); result[0]["data"].append(2); self.assertEqual(jobs[0]["data"],[1])
        self.assertEqual(api.ready_jobs([],0,1),[])
        for limit in (-1,True,1.5):
            with self.assertRaises(ValueError): api.ready_jobs(jobs,0,limit)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
