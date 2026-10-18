import json, unittest
from datetime import date, datetime
from reports import weighted_mean as core
from reports import weighted_mean_api as api

class BehaviorTests(unittest.TestCase):
    def test_weight_denominator_and_no_public_rounding(self):
        self.assertAlmostEqual(core.weighted_mean([10,20],[1,3]),17.5)
        self.assertAlmostEqual(api.report_mean([1,2],[0.25,0.75]),1.75)
        self.assertEqual(api.report_mean([2,100],[2,0]),2)
    def test_invalid_inputs_and_preservation(self):
        for values,weights in (([],[]),([1],[1,2]),([1],[-1]),([1],[0]),([float("inf")],[1]),([1],[float("nan")])):
            with self.assertRaises(ValueError): api.report_mean(values,weights)
        values=[2,4];weights=[1,2];api.report_mean(values,weights)
        self.assertEqual(values,[2,4]);self.assertEqual(weights,[1,2])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
