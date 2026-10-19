import json, unittest
from datetime import date, datetime
from similarity import jaccard_stable_selection as core
from similarity import jaccard_stable_selection_api as api

class BehaviorTests(unittest.TestCase):
    def test_distinct_set_denominator(self):
        self.assertEqual(core.jaccard_score(["a","a"],["a","b","b"]),0.5)
        self.assertEqual(core.jaccard_score(["x","x"],["x","x"]),1.0)
    def test_earliest_tie_and_nonmutation(self):
        candidates=[["a"],["a"],["b"]]; before=[list(row) for row in candidates]
        self.assertEqual(api.most_similar(candidates,["a"]),0)
        self.assertEqual(api.most_similar([["a","a"],["a","b"]],["a"]),0)
        self.assertEqual(candidates,before)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
