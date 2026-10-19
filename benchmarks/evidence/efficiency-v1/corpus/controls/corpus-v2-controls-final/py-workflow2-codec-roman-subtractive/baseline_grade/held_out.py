import json, unittest
from datetime import date, datetime
from codec import roman_subtractive as core

class BehaviorTests(unittest.TestCase):
    def test_subtractive_pairs(self):
        for value,expected in [(4,"IV"),(9,"IX"),(40,"XL"),(90,"XC"),(400,"CD"),(900,"CM")]:
            self.assertEqual(core.roman_numeral(value),expected)
    def test_combinations_and_upper_limit(self):
        self.assertEqual(core.roman_numeral(1994),"MCMXCIV")
        self.assertEqual(core.roman_numeral(3999),"MMMCMXCIX")
        self.assertEqual(core.roman_numeral(944),"CMXLIV")
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
