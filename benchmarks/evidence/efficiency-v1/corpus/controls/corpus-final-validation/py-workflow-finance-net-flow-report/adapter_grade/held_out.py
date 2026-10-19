import json, unittest
from datetime import date, datetime
from finance import net_flow_report as core
from finance import net_flow_report_api as api

class BehaviorTests(unittest.TestCase):
    def test_signed_domain_balance(self):
        self.assertEqual(core.net_flow(2,5),-3)
        self.assertEqual(core.net_flow(5,2),3)
        self.assertEqual(core.net_flow(8,8),0)
    def test_report_preserves_negative_order_and_inputs(self):
        rows=[("z",1,3),("A",4,2),("z",0,2)]
        self.assertEqual(api.flow_report(rows),[("z",-2),("A",2),("z",-2)])
        self.assertEqual(rows,[("z",1,3),("A",4,2),("z",0,2)])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
