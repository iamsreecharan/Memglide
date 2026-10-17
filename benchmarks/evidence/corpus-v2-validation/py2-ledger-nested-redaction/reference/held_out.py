import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import nested_redaction as core

class BehaviorTests(unittest.TestCase):
    def test_recursive_lists_casefold_and_exact_names(self):
        value={"children":[{"PASSWORD":"x","password_hint":"safe"},{"token":"y"}],"false":False,"none":None}
        expected={"children":[{"PASSWORD":"[REDACTED]","password_hint":"safe"},{"token":"[REDACTED]"}],"false":False,"none":None}
        self.assertEqual(api.redact(value,["password","TOKEN"]),expected)
        self.assertEqual(core.redact([value],["password","token"]),[expected])
    def test_no_mutation_or_alias(self):
        value={"items":[{"password":"x","tags":[1]}]}; before=deepcopy(value)
        result=api.redact(value,["password"]); result["items"][0]["tags"].append(2)
        self.assertEqual(value,before)
        self.assertEqual(api.redact(0,[]),0)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
