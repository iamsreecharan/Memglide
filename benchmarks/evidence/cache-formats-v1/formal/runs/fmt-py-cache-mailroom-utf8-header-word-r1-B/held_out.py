import json, unittest
from datetime import date, datetime
from mailroom import utf8_header_word as core
from mailroom import utf8_header_word_api as api

class BehaviorTests(unittest.TestCase):
    def test_utf8_and_exact_case(self):
        import base64
        for value in ("Été","東京","😀","HELLO"):
            expected=value if value.isascii() else "=?utf-8?b?"+base64.b64encode(value.encode()).decode()+"?="
            self.assertEqual(core.encode_header_word(value),expected)
            self.assertEqual(api.subject_header(value),expected)
    def test_empty_plain_text_and_injection(self):
        self.assertEqual(api.subject_header(""),"")
        self.assertEqual(core.encode_header_word("A & B"),"A & B")
        for value in ("a\nb","a\rb"):
            with self.assertRaises(ValueError): core.encode_header_word(value)
            with self.assertRaises(ValueError): api.subject_header(value)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
