import json, unittest
from datetime import date, datetime
from catalog import strict_column_projection as core
from catalog import strict_column_projection_api as api

class BehaviorTests(unittest.TestCase):
    def test_missing_is_distinct_from_present_null(self):
        for operation in (core.select_columns,api.export_row):
            with self.assertRaises(KeyError): operation({"a":None},["missing"])
        self.assertEqual(api.export_row({"a":None,"b":0,"c":False,"d":""},["d","a","b","c"]),{"d":"","a":None,"b":0,"c":False})
        self.assertEqual(list(api.export_row({"a":None,"b":1},["b","a"])),["b","a"])
    def test_no_input_changes_and_empty_selection(self):
        row={"a":[1],"b":2};columns=["a"]
        result=api.export_row(row,columns)
        self.assertIsNot(result,row)
        self.assertIs(result["a"],row["a"])
        self.assertEqual(row,{"a":[1],"b":2})
        self.assertEqual(columns,["a"])
        self.assertEqual(core.select_columns(row,[]),{})
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
