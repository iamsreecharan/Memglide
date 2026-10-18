import json, unittest
from datetime import date, datetime
from metrics import negative_baseline_change as core

class BehaviorTests(unittest.TestCase):
    def test_negative_baselines_and_zero(self):
        self.assertEqual(core.percent_change(-10,-5),50)
        self.assertEqual(core.percent_change(-10,-15),-50)
        self.assertEqual(core.percent_change(-10,10),200)
        self.assertEqual(core.percent_change(0,0),0)
        self.assertIsNone(core.percent_change(0,1))
    def test_normal_values_and_validation(self):
        self.assertEqual(core.percent_change(8,4),-50)
        self.assertEqual(core.percent_change(1.25,2.5),100)
        for args in ((True,1),(1,False),(float("nan"),1),(1,float("inf")),("1",2)):
            with self.assertRaises(ValueError): core.percent_change(*args)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
