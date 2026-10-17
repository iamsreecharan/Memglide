import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_successful_read_refreshes_recency(self):
        from atlas.cache import TTLCache
        cache = TTLCache(2)
        cache.put("a", 1, now=0, ttl=100)
        cache.put("b", 2, now=0, ttl=100)
        self.assertEqual(cache.get("a", now=1), 1)
        cache.put("c", 3, now=2, ttl=100)
        self.assertIsNone(cache.get("b", now=2))
        self.assertEqual(cache.get("a", now=2), 1)
        self.assertEqual(len(cache.entries), 2)

    def test_updates_misses_and_expiration(self):
        from atlas.cache import TTLCache
        cache = TTLCache(2)
        cache.put("a", 1, now=0, ttl=10)
        cache.put("b", 2, now=0, ttl=100)
        self.assertIsNone(cache.get("missing", now=1))
        cache.put("a", 9, now=1, ttl=10)
        cache.put("c", 3, now=2, ttl=100)
        self.assertIsNone(cache.get("b", now=2))
        self.assertEqual(cache.get("a", now=5), 9)
        self.assertIsNone(cache.get("a", now=12))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
