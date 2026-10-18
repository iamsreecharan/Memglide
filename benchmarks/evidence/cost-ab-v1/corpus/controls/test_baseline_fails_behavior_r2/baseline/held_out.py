import json, unittest
from datetime import date, datetime
from inventory import pack_ceiling as core

class BehaviorTests(unittest.TestCase):
    def test_round_up_and_large_exact_integer(self):
        for units,size,expected in ((1,6,1),(7,6,2),(0,3,0),(12,6,2),(10**30+1,10,10**29+1)):
            self.assertEqual(core.packs_required(units,size),expected)
    def test_invalid_arguments(self):
        for units,size in ((-1,2),(1,0),(1,-1),(True,2),(2,False),(2.0,2),(2,"2")):
            with self.assertRaises(ValueError): core.packs_required(units,size)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
