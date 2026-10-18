import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import bounded_async_execution as core

class BehaviorTests(unittest.TestCase):
    def test_bound_order_and_empty(self):
        async def scenario():
            active=0; peak=0
            async def operation(item):
                nonlocal active,peak
                active+=1; peak=max(peak,active)
                try: await asyncio.sleep((5-item)*0.001); return item*2
                finally: active-=1
            self.assertEqual(await api.map_async([0,1,2,3,4],operation,2),[0,2,4,6,8])
            self.assertLessEqual(peak,2); self.assertEqual(active,0)
            self.assertEqual(await core.map_async([],operation,1),[])
        asyncio.run(scenario())
    def test_error_cleanup_and_validation(self):
        async def scenario():
            active=0; error=RuntimeError("planned")
            async def operation(item):
                nonlocal active
                active+=1
                try:
                    if item==0: await asyncio.sleep(0); raise error
                    await asyncio.sleep(1)
                finally: active-=1
            with self.assertRaises(RuntimeError) as caught: await api.map_async([0,1,2,3],operation,2)
            self.assertIs(caught.exception,error); self.assertEqual(active,0)
            for concurrency in (0,-1,True,1.5):
                with self.assertRaises(ValueError): await api.map_async([],operation,concurrency)
        asyncio.run(scenario())

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
