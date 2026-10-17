import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import deterministic_build_order as core

class BehaviorTests(unittest.TestCase):
    def test_dependencies_ready_ties_and_external_nodes(self):
        graph={"a":["z"],"b":[],"c":["a","b","a"]}
        self.assertEqual(api.build_order(graph),["b","z","a","c"])
        self.assertEqual(core.build_order({"d":["b","c"],"b":["a"],"c":["a"]}),["a","b","c","d"])
        self.assertEqual(api.build_order({}),[])
        self.assertEqual(api.build_order({"x":[]}),["x"])
    def test_cycles_and_input(self):
        for graph in ({"a":["a"]},{"a":["b"],"b":["a"]},{"safe":[],"a":["b"],"b":["a"]}):
            with self.assertRaises(ValueError): api.build_order(graph)
        graph={"b":["a","a"]}; before=deepcopy(graph); api.build_order(graph); self.assertEqual(graph,before)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
