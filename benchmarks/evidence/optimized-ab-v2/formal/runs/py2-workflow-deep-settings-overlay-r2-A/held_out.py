import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import deep_settings_overlay as core

class BehaviorTests(unittest.TestCase):
    def test_recursive_merge_and_literal_null(self):
        base={"db":{"host":"local","pool":{"min":1,"max":4}},"items":[1],"flag":True}
        override={"db":{"pool":{"max":9}},"items":[2,3],"flag":None}
        expected={"db":{"host":"local","pool":{"min":1,"max":9}},"items":[2,3],"flag":None}
        self.assertEqual(api.overlay(base,override),expected)
        self.assertEqual(core.overlay({"x":1},{"x":{"y":2}}),{"x":{"y":2}})
        self.assertEqual(api.overlay({"x":{"y":1}},{"x":False}),{"x":False})
    def test_no_aliases(self):
        base={"nested":{"a":[1]},"keep":[0]}; change={"nested":{"b":[2]}}; originals=deepcopy((base,change))
        result=api.overlay(base,change); result["nested"]["a"].append(3); result["nested"]["b"].append(4); result["keep"].append(5)
        self.assertEqual((base,change),originals)
        self.assertEqual(api.overlay({},{}),{})

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
