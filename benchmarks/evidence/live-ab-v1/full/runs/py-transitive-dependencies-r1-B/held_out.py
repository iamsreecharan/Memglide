import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_cycles_diamonds_and_input(self):
        from atlas.service import DocumentService
        graph = {"a": ["c", "b", "a"], "b": ["d"], "c": ["d", "e"], "d": ["a"], "e": ["leaf"]}
        original = deepcopy(graph)
        self.assertEqual(DocumentService().dependencies_for(graph, "a"), ["b", "c", "d", "e", "leaf"])
        self.assertEqual(graph, original)

    def test_missing_and_long_chain(self):
        from atlas.graph import dependencies
        self.assertEqual(dependencies({}, "missing"), [])
        graph = {str(i): [str(i + 1)] for i in range(300)}
        self.assertEqual(dependencies(graph, "0"), sorted(str(i) for i in range(1, 301)))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
