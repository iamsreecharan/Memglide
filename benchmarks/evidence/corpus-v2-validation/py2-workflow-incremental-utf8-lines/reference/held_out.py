import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import incremental_utf8_lines as core

class BehaviorTests(unittest.TestCase):
    def test_arbitrary_byte_boundaries_and_crlf(self):
        raw="é\r\n😀\n\nlast".encode("utf-8")
        self.assertEqual(api.decode_lines([raw[i:i+1] for i in range(len(raw))]),["é","😀","","last"])
        self.assertEqual(core.decode_lines([b"a\r",b"\n",b"b"]),["a","b"])
        self.assertEqual(api.decode_lines([b"\n\n"]),["",""])
        self.assertEqual(api.decode_lines([]),[])
        self.assertEqual(api.decode_lines([b"",b""]),[])
    def test_strict_utf8_and_final_fragment(self):
        self.assertEqual(api.decode_lines([b"plain"]),["plain"])
        self.assertEqual(api.decode_lines([b"final\r"]),["final\r"])
        for chunks in ([b"\xff"],[b"\xc3"],[b"\xe2",b"("]):
            with self.assertRaises(UnicodeDecodeError): api.decode_lines(chunks)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
