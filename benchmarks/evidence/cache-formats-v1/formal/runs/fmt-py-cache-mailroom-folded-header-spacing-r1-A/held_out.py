import json, unittest
from datetime import date, datetime
from mailroom import folded_header_spacing as core

class BehaviorTests(unittest.TestCase):
    def test_continuations_and_exact_content(self):
        self.assertEqual(core.unfold_header(["Subject: hello","  world","\tagain "]),"Subject: hello world again ")
        self.assertEqual(core.unfold_header(["X: a  b"," "]),"X: a  b ")
        self.assertEqual(core.unfold_header([]),"")
    def test_invalid_lines_and_input_preservation(self):
        for lines in (["X: a","not-indented"],["X: a\nb"],["X: a"," b\rc"]):
            with self.assertRaises(ValueError): core.unfold_header(lines)
        lines=[" X: a ","  b "]; result=core.unfold_header(lines)
        self.assertEqual(result," X: a  b ")
        self.assertEqual(lines,[" X: a ","  b "])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
