import json, unittest
from datetime import date, datetime
from catalog import single_pass_partition as core

class BehaviorTests(unittest.TestCase):
    def test_one_decision_in_order_and_iterators(self):
        seen=[]
        def predicate(value):
            seen.append(value)
            return len(seen)%2==1
        self.assertEqual(core.partition(iter([1,2,3,4]),predicate),([1,3],[2,4]))
        self.assertEqual(seen,[1,2,3,4])
        calls=[]
        self.assertEqual(core.partition([2,1],lambda x:calls.append(x) or x==2),([2],[1]))
        self.assertEqual(calls,[2,1])
    def test_input_empty_and_error_identity(self):
        values=[1,2,1]
        self.assertEqual(core.partition(values,lambda x:x==1),([1,1],[2]))
        self.assertEqual(values,[1,2,1])
        self.assertEqual(core.partition([],lambda x:True),([],[]))
        error=RuntimeError("predicate")
        def fail(value): raise error
        with self.assertRaises(RuntimeError) as caught: core.partition([1],fail)
        self.assertIs(caught.exception,error)
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
