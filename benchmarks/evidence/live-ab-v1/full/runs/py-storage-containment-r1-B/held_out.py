import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_sibling_prefix_and_absolute_denied(self):
        from atlas.security import resolve_under
        for key in ("../database/secret", "../data-backup/key", "../../etc/passwd", "/srv/data/absolute"):
            with self.assertRaises(ValueError, msg=key):
                resolve_under("/srv/data", key)

    def test_normalization_and_service(self):
        from atlas.service import DocumentService
        service = DocumentService()
        for key, expected in (("", "/srv/data"), (".", "/srv/data"), ("docs/../a/./b", "/srv/data/a/b"), ("docs..txt", "/srv/data/docs..txt")):
            self.assertEqual(service.storage_key("/srv/data", key), expected)
        self.assertEqual(service.storage_key("/srv/data/", "a"), "/srv/data/a")
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
