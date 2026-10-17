import asyncio, json, unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from workflow import api
from workflow import strict_template_expansion as core

class BehaviorTests(unittest.TestCase):
    def test_missing_names_and_nonrecursive_values(self):
        with self.assertRaises(KeyError): api.render("${missing}",{})
        self.assertEqual(core.render("${x}:${n}:${flag}",{"x":"${ignored}","n":0,"flag":False}),"${ignored}:0:False")
        self.assertEqual(api.render("${n}:${flag}",{"n":0,"flag":False}),"0:False")
        with self.assertRaises(KeyError): core.render("${missing}",{})
        self.assertEqual(api.render("$${name}",{}),"${name}")
        self.assertEqual(api.render("$$$$",{}),"$$")
    def test_malformed_inputs_and_plain_text(self):
        for template in ("$","${}","${a-b}","${unclosed","$name"):
            with self.assertRaises(ValueError): api.render(template,{})
        self.assertEqual(api.render("plain",{}),"plain")
        self.assertEqual(api.render("",{}),"")

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
    raise SystemExit(not result.wasSuccessful())
