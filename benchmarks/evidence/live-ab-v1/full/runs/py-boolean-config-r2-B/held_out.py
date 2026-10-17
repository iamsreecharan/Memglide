import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_supported_values_and_service(self):
        from atlas.config import parse_flag
        from atlas.service import DocumentService
        for value in (True, "true", "  TRUE ", "1", "Yes", "ON"):
            self.assertTrue(DocumentService().feature_enabled(value), repr(value))
        for value in (False, "false", "  FALSE ", "0", "No", "OFF"):
            self.assertFalse(DocumentService().feature_enabled(value), repr(value))
        self.assertTrue(parse_flag(None, default=True))
        self.assertFalse(parse_flag(None))

    def test_invalid_values_rejected(self):
        from atlas.config import parse_flag
        for value in (0, 1, 1.0, "", "truthy", [], {}, ["true"]):
            with self.assertRaises((ValueError, TypeError), msg=repr(value)):
                parse_flag(value)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
