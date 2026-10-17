import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import weighted_allocation as core

class BehaviorTests(unittest.TestCase):
    def test_remainders_and_conservation(self):
        self.assertEqual(api.allocate(5, [1, 1, 1]), [2, 2, 1])
        self.assertEqual(core.allocate(11, [0, 2, 1]), [0, 7, 4])
        self.assertEqual(sum(api.allocate(10**19 + 7, [3, 5, 9])), 10**19 + 7)
    def test_validation_and_immutability(self):
        weights = [1, 3, 2]
        self.assertEqual(api.allocate(0, weights), [0, 0, 0])
        self.assertEqual(weights, [1, 3, 2])
        for total, values in ((-1, [1]), (True, [1]), (1, [0, 0]), (1, [-1, 2]), (1, [1.5]), (1, [])):
            with self.assertRaises(ValueError): api.allocate(total, values)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
