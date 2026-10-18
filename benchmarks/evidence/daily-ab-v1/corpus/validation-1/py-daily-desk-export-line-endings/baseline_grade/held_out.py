import json, unittest
from datetime import date, datetime
from desk import export_line_endings as core
from desk import export_line_endings_api as api

class BehaviorTests(unittest.TestCase):
    def test_false_option_and_crlf_forwarding(self):
        self.assertEqual(core.join_lines(["a","b"],final_newline=False), "a\nb")
        self.assertEqual(api.export_notes(["a","b"],newline="\r\n",final_newline=False), "a\r\nb")
        self.assertEqual(api.export_notes(["a"],newline="\r\n"), "a\r\n")
        self.assertEqual(api.export_notes([],newline="\r\n"), "")
    def test_blank_lines_validation_and_immutability(self):
        lines=["", "x", ""]
        self.assertEqual(core.join_lines(lines), "\nx\n\n")
        self.assertEqual(lines,["", "x", ""])
        for separator in ("", "\r", "--"):
            with self.assertRaises(ValueError): api.export_notes(["x"],newline=separator)
        for line in ("a\nb","a\rb"):
            with self.assertRaises(ValueError): core.join_lines([line])
            with self.assertRaises(ValueError): api.export_notes([line])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
