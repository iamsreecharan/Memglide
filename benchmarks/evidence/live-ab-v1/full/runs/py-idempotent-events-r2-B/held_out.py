import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_first_payload_and_sequence_win(self):
        from atlas.repository import Repository
        repository = Repository()
        first = repository.put_event("a", {"value": 1})
        duplicate = repository.put_event("a", {"value": 999})
        self.assertEqual(duplicate, first)
        self.assertEqual(repository.events["a"], first)
        self.assertEqual(repository.put_event("b", {})["sequence"], 2)
        self.assertEqual(repository.put_event("a", {})["sequence"], 1)

    def test_nested_defensive_copies(self):
        from atlas.repository import Repository
        repository = Repository()
        payload = {"items": [1]}
        event = repository.put_event("a", payload)
        payload["items"].append(2)
        event["payload"]["items"].append(3)
        duplicate = repository.put_event("a", {})
        self.assertEqual(duplicate["payload"], {"items": [1]})
        duplicate["payload"]["items"].append(4)
        self.assertEqual(repository.events["a"]["payload"], {"items": [1]})
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
