import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_all_tokens_and_no_mutation(self):
        from atlas.service import DocumentService
        records = [{"id": "b", "title": "Cloud", "body": "CACHE docs"}, {"id": "a", "title": "cache cloud", "body": "guide"}, {"id": "c", "title": "Cloud", "body": "unrelated"}, {"id": "d", "title": "cloudy", "body": "cache"}]
        original = deepcopy(records)
        self.assertEqual([r["id"] for r in DocumentService().search_documents(records, "CLOUD cache")], ["a", "b"])
        self.assertEqual(records, original)

    def test_empty_repeated_and_punctuation(self):
        from atlas.search import search
        records = [{"id": "a", "title": "alpha beta", "body": ""}, {"id": "b", "title": "alpha", "body": ""}]
        self.assertEqual(search(records, "!!!"), [])
        self.assertEqual([r["id"] for r in search(records, "alpha ALPHA,beta")], ["a"])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
