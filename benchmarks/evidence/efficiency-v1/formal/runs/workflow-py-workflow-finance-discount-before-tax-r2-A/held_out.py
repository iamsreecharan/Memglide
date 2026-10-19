import json, unittest
from datetime import date, datetime
from finance import discount_before_tax as core

class BehaviorTests(unittest.TestCase):
    def test_discount_is_not_taxed(self):
        self.assertAlmostEqual(core.checkout_total(100,20,0.1),88)
        self.assertAlmostEqual(core.checkout_total(2.5,0.75,0.2),2.1)
    def test_full_discount_and_fractional_result(self):
        self.assertEqual(core.checkout_total(7,7,0.25),0)
        self.assertAlmostEqual(core.checkout_total(1.25,0.25,0.075),1.075)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
