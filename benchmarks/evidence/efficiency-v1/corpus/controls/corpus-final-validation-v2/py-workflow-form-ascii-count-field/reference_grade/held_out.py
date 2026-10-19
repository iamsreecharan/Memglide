import json, unittest
from datetime import date, datetime
from form import ascii_count_field as core

class BehaviorTests(unittest.TestCase):
    def test_unicode_and_non_digit_rejection(self):
        for text in ("١٢","１２","1٢","+1","-1"," 1","1 ","", "1.0"):
            with self.assertRaises(ValueError): core.parse_count(text)
    def test_large_ascii_and_zero(self):
        self.assertEqual(core.parse_count("9"*80),int("9"*80))
        self.assertEqual(core.parse_count("000"),0)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
