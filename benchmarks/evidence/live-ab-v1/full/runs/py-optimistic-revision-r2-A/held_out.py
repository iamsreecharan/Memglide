import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_conflicts_are_atomic(self):
        from atlas.repository import Repository, ConflictError
        repository = Repository()
        repository.create("a", {"value": 1})
        repository.update("a", {"value": 2}, expected_revision=1)
        for revision in (1, 0, 99):
            with self.assertRaises(ConflictError):
                repository.update("a", {"value": 99}, expected_revision=revision)
            self.assertEqual(repository.records["a"], {"id": "a", "body": {"value": 2}, "revision": 2})

    def test_success_and_defensive_copy(self):
        from atlas.repository import Repository
        repository = Repository()
        repository.create("a", {})
        body = {"items": [1]}
        result = repository.update("a", body, expected_revision=1)
        body["items"].append(2)
        result["body"]["items"].append(3)
        self.assertEqual(repository.records["a"]["body"], {"items": [1]})
        self.assertEqual(result["revision"], 2)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
