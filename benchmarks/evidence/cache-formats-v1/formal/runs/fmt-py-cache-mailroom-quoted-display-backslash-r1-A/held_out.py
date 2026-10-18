import json, unittest
from datetime import date, datetime
from mailroom import quoted_display_backslash as core

class BehaviorTests(unittest.TestCase):
    def test_backslashes_and_quotes(self):
        slash=chr(92)
        self.assertEqual(core.quote_display_name('a'+slash+'b'), '"a'+slash*2+'b"')
        self.assertEqual(core.quote_display_name('a"b'), '"a'+slash+'"b"')
        self.assertEqual(core.quote_display_name('a'+slash+'"b'), '"a'+slash*3+'"b"')
    def test_empty_unicode_and_line_breaks(self):
        self.assertEqual(core.quote_display_name(''), '""')
        self.assertEqual(core.quote_display_name('é'), '"é"')
        for name in ('a\nb','a\rb'):
            with self.assertRaises(ValueError): core.quote_display_name(name)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
