import json, unittest
from datetime import date, datetime
from catalog import tag_normalization as core
from catalog import tag_normalization_api as api

class BehaviorTests(unittest.TestCase):
    def test_dedup_casefold_and_stable_order(self):
        self.assertEqual(core.normalize_tags([" B ","a","b"," A ","ß","SS"," "]),["b","a","ss"])
        self.assertEqual(api.tags_for_card(["a,b","C","A,B"]),["a,b","c"])
        self.assertEqual(api.tags_for_card([" Straße ","STRASSE"]),["strasse"])
    def test_one_shot_input_and_no_mutation(self):
        values=[" One ","ONE","two"]
        self.assertEqual(api.tags_for_card(values),["one","two"])
        self.assertEqual(values,[" One ","ONE","two"])
        self.assertEqual(core.normalize_tags(iter([" X ","x",""])),["x"])
        self.assertEqual(api.tags_for_card([]),[])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
