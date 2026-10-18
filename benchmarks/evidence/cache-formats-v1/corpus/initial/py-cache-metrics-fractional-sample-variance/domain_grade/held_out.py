import json, unittest
from datetime import date, datetime
from metrics import fractional_sample_variance as core
from metrics import fractional_sample_variance_api as api

class BehaviorTests(unittest.TestCase):
    def test_sample_denominator_and_fractional_api(self):
        self.assertEqual(core.sample_variance([1,2,3]),1)
        self.assertEqual(api.variance_for_report([1,2]),0.5)
        self.assertEqual(api.variance_for_report([-1.5,0.5]),2)
    def test_validation_and_no_mutation(self):
        values=[1,2,4];self.assertAlmostEqual(api.variance_for_report(values),7/3);self.assertEqual(values,[1,2,4])
        for values in ([],[1],[1,True],[1,float("nan")],[1,float("inf")],[1,"2"]):
            with self.assertRaises(ValueError): core.sample_variance(values)
            with self.assertRaises(ValueError): api.variance_for_report(values)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
