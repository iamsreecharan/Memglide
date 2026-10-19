import json, unittest
from datetime import date, datetime
from codec import glob_literal_escape as core

class BehaviorTests(unittest.TestCase):
    def test_original_metacharacters_once(self):
        self.assertEqual(core.escape_glob("a*?[b]"),"a[*][?][[]b]")
        self.assertEqual(core.escape_glob("[?*"),"[[][?][*]")
    def test_literal_matching_and_preservation(self):
        import fnmatch
        for name in ["*", "?", "[abc]", "a*b?.txt", "雪[?]", "a\\b"]:
            self.assertTrue(fnmatch.fnmatchcase(name,core.escape_glob(name)))
        self.assertFalse(fnmatch.fnmatchcase("axb",core.escape_glob("a*b")))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
