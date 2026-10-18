import json, unittest
from datetime import date, datetime
from desk import rectangular_transpose as core

class BehaviorTests(unittest.TestCase):
    def test_ragged_and_empty_shapes(self):
        for rows in ([[1,2],[3]], [[],[1]], [[1],[]]):
            with self.assertRaises(ValueError): core.transpose(rows)
        self.assertEqual(core.transpose([]), [])
        self.assertEqual(core.transpose([[],[]]), [])
    def test_values_and_no_input_mutation(self):
        rows = [["a",None],[False,0]]
        result = core.transpose(rows)
        self.assertEqual(result, [["a",False],[None,0]])
        result[0].append("new")
        self.assertEqual(rows, [["a",None],[False,0]])
        self.assertEqual(core.transpose([[1,2,3]]), [[1],[2],[3]])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
