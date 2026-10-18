import json, unittest
from datetime import date, datetime
from catalog import relative_indentation as core

class BehaviorTests(unittest.TestCase):
    def test_relative_indentation_and_blank_lines(self):
        self.assertEqual(core.dedent_lines(["  root","    child"," ","   peer"]),["root","  child",""," peer"])
        self.assertEqual(core.dedent_lines(["root","    child"]),["root","    child"])
        self.assertEqual(core.dedent_lines(["   "," ",""]),["","",""])
    def test_new_list_and_empty_input(self):
        lines=["   a", "     b"]
        result=core.dedent_lines(lines)
        self.assertEqual(result,["a","  b"])
        self.assertEqual(lines,["   a","     b"])
        self.assertIsNot(result,lines)
        self.assertEqual(core.dedent_lines([]),[])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
