import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import statement_timezones as core

class BehaviorTests(unittest.TestCase):
    def test_half_open_offsets_and_stability(self):
        start = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
        end = datetime.fromisoformat("2026-01-02T00:00:00+00:00")
        records=[{"id":"end","at":end},{"id":"a","at":datetime.fromisoformat("2026-01-01T01:00:00+01:00")},{"id":"b","at":start}]
        self.assertEqual([r["id"] for r in api.statement(records,start,end)],["a","b"])
        self.assertEqual(core.statement(records,start,start),[])
    def test_validation_and_detachment(self):
        start=datetime(2026,1,1,tzinfo=timezone.utc); end=start+timedelta(days=1)
        rows=[{"at":start,"tags":[1]}]; result=api.statement(rows,start,end); result[0]["tags"].append(2)
        self.assertEqual(rows[0]["tags"],[1])
        for a,b in ((end,start),(start.replace(tzinfo=None),end),("2026-01-01",end)):
            with self.assertRaises(ValueError): api.statement(rows,a,b)
        with self.assertRaises(ValueError): api.statement([{"at":datetime(2026,1,1)}],start,end)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
