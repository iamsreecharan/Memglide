import json, unittest
from datetime import date, datetime
from catalog import tag_normalization as core
from catalog import tag_normalization_api as api

class BehaviorTests(unittest.TestCase):
    def test_dedup_casefold_and_stable_order(self):
        self.assertEqual(core.normalize_tags([" B ","a","b"," A ","ß","SS"," "]),["b","a","ss"])
        self.assertEqual(api.tags_for_card(["a,b","C","A,B"]),["a,b","c"])
        self.assertEqual(api.tags_for_card([" Straße ","STRASSE"]),["strasse"])
        cards=[api.CatalogCard("b","Second",[" B ","b","a,b"]),api.CatalogCard("a","First",["Straße","STRASSE"])]
        self.assertEqual(api.cards_for_export(cards),[{"id":"b","title":"Second","tags":["b","a,b"],"metadata":{}},{"id":"a","title":"First","tags":["strasse"],"metadata":{}}])
    def test_one_shot_input_and_no_mutation(self):
        values=[" One ","ONE","two"]
        self.assertEqual(api.tags_for_card(values),["one","two"])
        self.assertEqual(values,[" One ","ONE","two"])
        self.assertEqual(core.normalize_tags(iter([" X ","x",""])),["x"])
        self.assertEqual(api.tags_for_card([]),[])
        from unittest.mock import patch
        card=api.CatalogCard("id","Title",[" A ","a"],{"info":{"values":[1]}})
        with patch.object(api,"tags_for_card",wraps=api.tags_for_card) as called:
            exported=api.cards_for_export(iter([card]))
            self.assertEqual(called.call_count,1)
        exported[0]["tags"].append("new")
        exported[0]["metadata"]["info"]["values"].append(2)
        self.assertEqual(card.tags,[" A ","a"])
        self.assertEqual(card.metadata,{"info":{"values":[1]}})
        self.assertEqual(api.cards_for_export([]),[])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
