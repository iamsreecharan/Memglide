import json, unittest
from datetime import date, datetime
from metrics import warmup_moving_average as core

class BehaviorTests(unittest.TestCase):
    def test_warmup_windows_and_signed_values(self):
        self.assertEqual(core.moving_average([2,4,6,8],3),[2,3,4,6])
        self.assertEqual(core.moving_average([-2,2],9),[-2,0])
        self.assertEqual(core.moving_average([],2),[])
    def test_validation_and_no_mutation(self):
        values=[1.5,2.5];self.assertEqual(core.moving_average(values,2),[1.5,2]);self.assertEqual(values,[1.5,2.5])
        for window in (0,-1,True,1.5):
            with self.assertRaises(ValueError): core.moving_average([1],window)
        for values in ([True],[float("nan")],[float("inf")],["1"]):
            with self.assertRaises(ValueError): core.moving_average(values,1)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
