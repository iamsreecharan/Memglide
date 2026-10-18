import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import csv_bank_import as core

class BehaviorTests(unittest.TestCase):
    def test_quoted_fields_bom_and_reordered_columns(self):
        text='\ufeffmemo,reference,amount\r\n"hello, bank\nnext line",r1,-12\r\n'
        expected=[{"reference":"r1","amount":-12,"memo":"hello, bank\nnext line"}]
        self.assertEqual(api.parse_bank_csv(text),expected)
        self.assertEqual(core.parse_bank_csv("reference,amount,memo\n"),[])
    def test_invalid_exports(self):
        for text in ("", "reference,amount,amount\na,1,2\n", "reference,amount,memo\na,1.2,x\n", "reference,amount,memo\na,1,x,extra\n", "reference,amount\na,1\n"):
            with self.assertRaises(ValueError): api.parse_bank_csv(text)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
