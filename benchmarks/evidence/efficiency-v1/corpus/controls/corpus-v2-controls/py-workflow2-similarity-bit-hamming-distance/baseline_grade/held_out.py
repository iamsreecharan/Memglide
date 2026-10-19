import json, unittest
from datetime import date, datetime
from similarity import bit_hamming_distance as core

class BehaviorTests(unittest.TestCase):
    def test_position_count_not_numeric_distance(self):
        self.assertEqual(core.hamming_distance("1000","0111"),4)
        self.assertEqual(core.hamming_distance("1010","0101"),4)
    def test_leading_zeros_and_long_values(self):
        self.assertEqual(core.hamming_distance("0001","1001"),1)
        self.assertEqual(core.hamming_distance("10"*100,"01"*100),200)
        self.assertEqual(core.hamming_distance("0"*200,"0"*199+"1"),1)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
