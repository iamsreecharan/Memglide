import json, unittest
from datetime import date, datetime
from codec import unsigned_varint_batch as core
from codec import unsigned_varint_batch_api as api

class BehaviorTests(unittest.TestCase):
    def test_continuation_boundaries_and_large_values(self):
        self.assertEqual(core.encode_unsigned(128),b"\x80\x01")
        self.assertEqual(core.encode_unsigned(16384),b"\x80\x80\x01")
        self.assertEqual(core.encode_unsigned(1 << 70),b"\x80"*10+b"\x01")
    def test_batch_order_and_nonmutation(self):
        values=[128,1,0,16384]; before=list(values)
        self.assertEqual(api.encode_values(values),b"\x80\x01\x01\x00\x80\x80\x01")
        self.assertEqual(values,before)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
