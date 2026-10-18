import json, unittest
from datetime import date, datetime
from metrics import histogram_boundary_slots as core
from metrics import histogram_boundary_slots_api as api

class BehaviorTests(unittest.TestCase):
    def test_exact_boundaries_and_empty_bins(self):
        self.assertEqual(core.histogram([0,10,20],[0,10,20]),[0,1,1,1])
        self.assertEqual(api.chart_buckets([5],[0,10,20]),[0,1,0,0])
        self.assertEqual(api.chart_buckets([],[]),[0])
        self.assertEqual(api.chart_buckets([1,2],[]),[2])
    def test_validation_and_input_immutability(self):
        values=[-1,0,1];bounds=[0];self.assertEqual(api.chart_buckets(values,bounds),[1,2]);self.assertEqual(values,[-1,0,1]);self.assertEqual(bounds,[0])
        for values,bounds in (([],[1,1]),([],[2,1]),([float("nan")],[0]),([],[float("inf")])):
            with self.assertRaises(ValueError): core.histogram(values,bounds)
            with self.assertRaises(ValueError): api.chart_buckets(values,bounds)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
