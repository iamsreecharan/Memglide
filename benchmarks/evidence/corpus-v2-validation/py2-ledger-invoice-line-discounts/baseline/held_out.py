import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import invoice_line_discounts as core

class BehaviorTests(unittest.TestCase):
    def test_per_unit_rounding_and_extremes(self):
        self.assertEqual(api.invoice_total([{"price":1,"quantity":3}],5000),3)
        self.assertEqual(core.invoice_total([{"price":3,"quantity":2},{"price":1,"quantity":1}],5000),5)
        self.assertEqual(api.invoice_total([{"price":10**22+1,"quantity":3}],0),(10**22+1)*3)
        self.assertEqual(api.invoice_total([{"price":9,"quantity":7}],10000),0)
    def test_validation_and_no_mutation(self):
        rows=[{"price":7,"quantity":2}]; before=deepcopy(rows); api.invoice_total(rows,1); self.assertEqual(rows,before)
        for rows,rate in (([{"price":True,"quantity":1}],0),([{ "price":1,"quantity":-1}],0),([],True),([],10001)):
            with self.assertRaises(ValueError): api.invoice_total(rows,rate)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
