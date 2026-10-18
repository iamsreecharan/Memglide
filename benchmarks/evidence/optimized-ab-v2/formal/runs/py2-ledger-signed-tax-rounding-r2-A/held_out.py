import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import signed_tax_rounding as core

class BehaviorTests(unittest.TestCase):
    def test_refunds_half_ties_and_large_integers(self):
        for amount, rate, expected in ((5,1000,1),(-5,1000,-1),(-4,1000,0),(15,1000,2),(-15,1000,-2),(10**20+5,1000,10**19+1)):
            self.assertEqual(api.tax_cents(amount, rate), expected)
            self.assertEqual(core.tax_cents(amount, rate), expected)
    def test_rates_and_types(self):
        self.assertEqual(api.tax_cents(-123, 10000), -123)
        self.assertEqual(api.tax_cents(11, 0), 0)
        for args in ((True,1),(1,True),(1,-1),(1,10001),(1.5,50)):
            with self.assertRaises(ValueError): api.tax_cents(*args)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
