import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_exact_and_resource_wildcard(self):
        from atlas.service import DocumentService
        service = DocumentService()
        for scopes in (["docs:read"], ["docs:*"], ["other:write", "docs:read"]):
            self.assertTrue(service.authorized(scopes, "docs", "read"))

    def test_partial_and_unrelated_scopes_denied(self):
        from atlas.security import can_access
        for scope in ("", "read", "docs", "doc", "docs:rea", "*", "*:read", "doc:*", "docs:write", "archive:read"):
            self.assertFalse(can_access([scope], "docs", "read"), scope)
        self.assertFalse(can_access([], "docs", "read"))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
