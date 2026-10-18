import json, unittest
from datetime import date, datetime
from desk import calendar_month_shift as core
from desk import calendar_month_shift_api as api

class BehaviorTests(unittest.TestCase):
    def test_month_end_and_negative_deltas(self):
        self.assertEqual(core.shift_month(date(2024,1,31),1), date(2024,2,29))
        self.assertEqual(core.shift_month(date(2025,3,31),-1), date(2025,2,28))
        self.assertEqual(api.move_due_date(date(2025,5,15),-3), date(2025,2,15))
        self.assertEqual(api.move_due_date(date(2025,5,15),0), date(2025,5,15))
        self.assertEqual(api.move_due_date(date(2024,2,29),12), date(2025,2,28))
        items=[api.DueItem("a",date(2024,1,31)),api.DueItem("b",date(2025,3,31))]
        self.assertEqual([item.due for item in api.reschedule_due_items(items,1)],[date(2024,2,29),date(2025,4,30)])
        self.assertEqual([item.due for item in api.reschedule_due_items(items,-1)],[date(2023,12,31),date(2025,2,28)])
        self.assertEqual([item.due for item in api.reschedule_due_items(items,0)],[item.due for item in items])
    def test_types_and_year_rollover(self):
        self.assertEqual(core.shift_month(date(2025,1,1),-1), date(2024,12,1))
        self.assertEqual(api.move_due_date(date(2025,1,1),24), date(2027,1,1))
        for value, months in ((datetime(2025,1,1),1),(date(2025,1,1),True),(date(2025,1,1),1.5),("2025-01-01",1)):
            with self.assertRaises(ValueError): core.shift_month(value, months)
            with self.assertRaises(ValueError): api.move_due_date(value, months)
        item=api.DueItem("keep-id",date(2025,5,15),{"labels":["original"]})
        result=api.reschedule_due_items(iter([item]),2)
        self.assertEqual([entry.item_id for entry in result],["keep-id"])
        self.assertIsNot(result[0],item)
        result[0].metadata["labels"].append("new")
        self.assertEqual(item.metadata,{"labels":["original"]})
        self.assertEqual(item.due,date(2025,5,15))
        self.assertEqual(api.reschedule_due_items([],1),[])
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
