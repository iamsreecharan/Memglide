import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_deadline_and_service(self):
        from atlas.service import DocumentService
        service = DocumentService()
        service.cache.put("a", "old", now=100, ttl=10)
        self.assertEqual(service.cached_document("a", now=109.999), "old")
        self.assertIsNone(service.cached_document("a", now=110))
        self.assertNotIn("a", service.cache.entries)

    def test_overwrite_and_zero_ttl(self):
        from atlas.cache import TTLCache
        cache = TTLCache()
        cache.put("a", 1, now=0, ttl=2)
        cache.put("a", 2, now=1, ttl=10)
        self.assertEqual(cache.get("a", now=3), 2)
        self.assertIsNone(cache.get("a", now=11))
        cache.put("zero", 1, now=0, ttl=0)
        self.assertIsNone(cache.get("zero", now=0))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
