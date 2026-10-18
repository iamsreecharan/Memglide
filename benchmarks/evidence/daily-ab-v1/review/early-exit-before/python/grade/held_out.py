import json, unittest
from datetime import date, datetime
from desk import elapsed_clock as core

class BehaviorTests(unittest.TestCase):
    def test_long_durations_and_boundaries(self):
        for seconds, expected in ((0,"0:00:00"),(59,"0:00:59"),(60,"0:01:00"),(86400,"24:00:00"),(90061,"25:01:01"),(3600000001,"1000000:00:01")):
            self.assertEqual(core.format_elapsed(seconds), expected)
    def test_invalid_values(self):
        for value in (-1, True, False, 1.5, "60", None):
            with self.assertRaises(ValueError): core.format_elapsed(value)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
