import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import reconciliation_version_merge as core

class BehaviorTests(unittest.TestCase):
    def test_latest_first_tie_and_sorted(self):
        rows=[{"id":"b","version":1,"value":"old"},{"id":"a","version":2,"value":"first"},{"id":"a","version":2,"value":"tie"},{"id":"b","version":3,"value":"new"},{"id":"b","version":2,"value":"stale"}]
        self.assertEqual([(r["id"],r["value"]) for r in api.reconcile(rows)],[("a","first"),("b","new")])
    def test_deep_copy_and_version_types(self):
        rows=[{"id":"a","version":0,"body":{"tags":[1]}}]; result=core.reconcile(rows); result[0]["body"]["tags"].append(2)
        self.assertEqual(rows[0]["body"]["tags"],[1]); rows[0]["body"]["tags"].append(3); self.assertEqual(result[0]["body"]["tags"],[1,2])
        for version in (-1,True,1.5):
            with self.assertRaises(ValueError): api.reconcile([{"id":"a","version":version}])

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
