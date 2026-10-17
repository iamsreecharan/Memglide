import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_permanent_error_not_retried(self):
        from atlas.retry import run_with_retry
        calls = []
        error = ValueError("permanent")
        def operation():
            calls.append(1)
            raise error
        with self.assertRaises(ValueError) as caught:
            run_with_retry(operation, max_attempts=5)
        self.assertIs(caught.exception, error)
        self.assertEqual(len(calls), 1)

    def test_temporary_success_exhaustion_and_validation(self):
        from atlas.retry import run_with_retry, TemporaryError
        calls = []
        error = TemporaryError("later")
        def operation():
            calls.append(1)
            if len(calls) < 3:
                raise error
            return {"ok": True}
        self.assertEqual(run_with_retry(operation, max_attempts=3), {"ok": True})
        self.assertEqual(len(calls), 3)
        calls.clear()
        with self.assertRaises(TemporaryError) as caught:
            run_with_retry(operation, max_attempts=2)
        self.assertIs(caught.exception, error)
        self.assertEqual(len(calls), 2)
        with self.assertRaises(ValueError):
            run_with_retry(lambda: None, max_attempts=0)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
