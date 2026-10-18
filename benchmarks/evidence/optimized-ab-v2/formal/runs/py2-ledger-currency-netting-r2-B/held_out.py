import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import currency_netting as core

class BehaviorTests(unittest.TestCase):
    def test_independent_nets_and_zero_groups(self):
        rows=[{"currency":"usd","amount":5},{"currency":"EUR","amount":7},{"currency":"USD","amount":-5},{"currency":"eur","amount":-2}]
        self.assertEqual(api.net_by_currency(rows),{"EUR":5,"USD":0})
        self.assertEqual(list(core.net_by_currency(rows)),["EUR","USD"])
    def test_validation_and_no_mutation(self):
        rows=[{"currency":"jpy","amount":10**25}]; original=deepcopy(rows)
        self.assertEqual(api.net_by_currency(rows),{"JPY":10**25}); self.assertEqual(rows,original)
        for row in ({"currency":"US","amount":1},{"currency":"üsd","amount":1},{"currency":"uſd","amount":1},{"currency":"ßd","amount":1},{"currency":"USD","amount":True},{"currency":"USD","amount":1.5}):
            with self.assertRaises(ValueError): api.net_by_currency([row])

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
