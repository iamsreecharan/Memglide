import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from ledger import api
from ledger import audit_hash_chain as core

class BehaviorTests(unittest.TestCase):
    def test_canonical_chain_and_tampering(self):
        import hashlib
        events=[{"b":2,"a":"é"},{"id":2}]; previous="0"*64; expected=[]
        for serialized in ('{"a":"é","b":2}','{"id":2}'):
            previous=hashlib.sha256((previous+"\n"+serialized).encode("utf-8")).hexdigest(); expected.append(previous)
        self.assertEqual(api.audit_chain(events),expected)
        changed=core.audit_chain([{"a":"different","b":2},{"id":2}])
        self.assertTrue(all(a!=b for a,b in zip(changed,expected)))
    def test_empty_ordering_and_immutability(self):
        self.assertEqual(api.audit_chain([]),[])
        events=[{"x":[1,2]}]; original=deepcopy(events); api.audit_chain(events); self.assertEqual(events,original)
        self.assertEqual(api.audit_chain([{"a":1,"b":2}]),api.audit_chain([{"b":2,"a":1}]))

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
