import json, unittest
from copy import deepcopy

class BehaviorTests(unittest.TestCase):
    def test_walk_and_no_mutation(self):
        from atlas.pagination import page
        records = [{"id": key} for key in ["d", "a", "c", "b", "e"]]
        original = deepcopy(records)
        seen, cursor = [], None
        for _ in range(10):
            current = page(records, cursor=cursor, limit=2)
            seen.extend(item["id"] for item in current["items"])
            cursor = current["next_cursor"]
            if cursor is None:
                break
        self.assertEqual(seen, ["a", "b", "c", "d", "e"])
        self.assertIsNone(cursor)
        self.assertEqual(records, original)

    def test_deleted_cursor_and_service(self):
        from atlas.pagination import page
        from atlas.service import DocumentService
        self.assertEqual(page([{"id": "a"}, {"id": "d"}], cursor="b", limit=1)["items"], [{"id": "d"}])
        service = DocumentService()
        for key in ("b", "a", "c"):
            service.repository.create(key, {})
        self.assertEqual([item["id"] for item in service.list_documents(cursor="b")["items"]], ["c"])
        for limit in (0, -1, 101):
            with self.assertRaises(ValueError):
                page([], limit=limit)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
