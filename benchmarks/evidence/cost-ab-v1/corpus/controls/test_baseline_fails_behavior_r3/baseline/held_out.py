import json, unittest
from datetime import date, datetime
from reports import csv_quoted_cell as core

class BehaviorTests(unittest.TestCase):
    def test_quotes_commas_and_linebreaks(self):
        for value,expected in [('a"b','"a""b"'),('"','""""'),('a,b','"a,b"'),('a\nb','"a\nb"'),('a\rb','"a\rb"')]:
            self.assertEqual(core.csv_cell(value),expected)
    def test_plain_empty_and_unicode(self):
        for value in (""," plain ","東京","tab\tvalue"):
            self.assertEqual(core.csv_cell(value),value)
        self.assertEqual(core.csv_cell('É,"x"'),'"É,""x"""')
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
