import json, unittest
from datetime import date, datetime
from desk import label_ellipsis as core

class BehaviorTests(unittest.TestCase):
    def test_exact_width_and_small_limits(self):
        self.assertEqual(core.truncate_label("abcdef",4), "abc…")
        self.assertEqual(core.truncate_label("abcdef",1), "…")
        self.assertEqual(core.truncate_label("abcdef",0), "")
        self.assertEqual(core.truncate_label("",0), "")
    def test_unicode_and_invalid_limits(self):
        self.assertEqual(core.truncate_label("a😀bc",3), "a😀…")
        self.assertEqual(core.truncate_label("abc",9), "abc")
        for limit in (-1, True, 1.5, "2"):
            with self.assertRaises(ValueError): core.truncate_label("abcdef",limit)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
