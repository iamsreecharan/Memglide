import json, unittest
from datetime import date, datetime
from metrics import missing_not_falsy as core

class BehaviorTests(unittest.TestCase):
    def test_missing_and_falsy_values(self):
        self.assertIs(core.is_missing(None),True)
        self.assertIs(core.is_missing(float("nan")),True)
        for value in (0,0.0,False,"",[],{},()): self.assertIs(core.is_missing(value),False)
    def test_other_present_objects(self):
        for value in (1,-1,float("inf"),"nan",object(),[None]): self.assertIs(core.is_missing(value),False)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
