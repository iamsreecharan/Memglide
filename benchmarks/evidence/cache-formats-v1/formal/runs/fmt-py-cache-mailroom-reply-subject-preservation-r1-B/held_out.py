import json, unittest
from datetime import date, datetime
from mailroom import reply_subject_preservation as core
from mailroom import reply_subject_preservation_api as api

class BehaviorTests(unittest.TestCase):
    def test_existing_prefix_and_adapter_whitespace(self):
        self.assertEqual(core.reply_subject("rE: Topic"),"rE: Topic")
        self.assertEqual(api.subject_for_reply("Re:  Topic "),"Re:  Topic ")
        self.assertEqual(api.subject_for_reply(" Topic "),"Re:  Topic ")
    def test_empty_similar_prefixes_and_unicode(self):
        for value,expected in (("","Re: "),("RE","Re: RE"),("Reindeer","Re: Reindeer"),("東京","Re: 東京"),(" re: x","Re:  re: x")):
            self.assertEqual(core.reply_subject(value),expected)
            self.assertEqual(api.subject_for_reply(value),expected)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
