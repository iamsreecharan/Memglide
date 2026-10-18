import json, unittest
from datetime import date, datetime
from catalog import saturday_weekend as core

class BehaviorTests(unittest.TestCase):
    def test_all_seven_days(self):
        self.assertEqual([core.is_weekend(day) for day in range(7)],[False,False,False,False,False,True,True])
        self.assertIs(core.is_weekend(5),True)
    def test_invalid_days(self):
        for day in (-1,7,True,False,5.0,"5",None):
            with self.assertRaises(ValueError): core.is_weekend(day)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
