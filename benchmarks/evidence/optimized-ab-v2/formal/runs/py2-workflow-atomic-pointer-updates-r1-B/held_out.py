import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import atomic_pointer_updates as core

class BehaviorTests(unittest.TestCase):
    def test_missing_leaf_and_atomicity(self):
        document={"a":{"x":1}}
        for updates in ([("/missing",2)],[("/a/x",9),("/a/nope",3)]):
            with self.assertRaises(KeyError): api.apply_updates(document,updates)
            self.assertEqual(document,{"a":{"x":1}})
        self.assertEqual(core.apply_updates({"a/b":{"~x":1}},[("/a~1b/~0x",2)]),{"a/b":{"~x":2}})
    def test_copies_root_and_bad_escape(self):
        document={"x":[1]}; value=[2]; result=api.apply_updates(document,[("/x",value)]); result["x"].append(3)
        self.assertEqual(document,{"x":[1]}); self.assertEqual(value,[2])
        self.assertEqual(api.apply_updates(document,[("",{"z":0})]),{"z":0})
        for pointer in ("x","/~2","/~"):
            with self.assertRaises(ValueError): api.apply_updates(document,[(pointer,0)])

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
