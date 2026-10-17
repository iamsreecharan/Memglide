import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_half_up_and_exact_integer_arithmetic(self):
        from atlas.billing import prorated_cents
        for monthly, active, days in ((101, 1, 2), (100, 1, 3), (100, 2, 3), (99, 30, 30), (0, 0, 31), (9007199254740991, 6, 7), (9007199254740991, 999, 1000)):
            numerator = monthly * active
            expected = numerator // days + (2 * (numerator % days) >= days)
            self.assertEqual(prorated_cents(monthly, active, days), expected)

    def test_validation_and_zero(self):
        from atlas.billing import prorated_cents
        self.assertEqual(prorated_cents(100, 0, 31), 0)
        for args in ((-1, 1, 2), (10, 3, 2), (10, 0, 0), (1.2, 1, 2), (True, 1, 2)):
            with self.assertRaises(ValueError):
                prorated_cents(*args)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
