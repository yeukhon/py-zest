import unittest
import subprocess
import os
import json

import zest

class TestZestScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__name__), "script.zest")) as f:
            cls.script = json.loads(f.read())

        file_path = os.path.join(os.path.dirname(__file__), "server.py")
        cls.server = subprocess.Popen(["python", file_path])
    @classmethod
    def tearDown(cls):
        cls.server.terminate()
        cls.server.kill()

    def test_loading_script(self):
        z = zest.load(self.script)
        self.assertEqual(z.about, self.script["about"])
        self.assertEqual(z.zestVersion, self.script["zestVersion"])
        self.assertEqual(z.generatedBy, self.script["generatedBy"])
        self.assertEqual(z.title, self.script["title"])
        self.assertEqual(z.description, self.script["description"])
        self.assertEqual(z.type, self.script["type"])
        self.assertEqual(z.parameters, self.script["parameters"])
        self.assertEqual(len(z.statements), len(self.script["statements"]))
        self.assertEqual(z.authentication, self.script["authentication"])
        self.assertEqual(z.index, self.script["index"])
        self.assertEqual(z.elementType, self.script["elementType"])

    def test_run_results(self):
        z = zest.load(self.script)
        z.run()

        self.assertEqual(z.report["failed"], 0)
        # count number of passed
        expected_passes = 0
        for statement in self.script["statements"]:
            expected_passes += len(statement["assertions"])
        self.assertEqual(z.report["passed"], expected_passes)
        # each assertion in the list of assertions is a single class of zest statement
        self.assertEqual(len(z.report["assertions"]), len(self.script["statements"]))
        # verify the number of assertions matches the number of assertions in each statement
        self.assertEqual(len(z.report["assertions"][0]["assertions"]), len(self.script["statements"][0]["assertions"]))
        self.assertEqual(len(z.report["assertions"][1]["assertions"]), len(self.script["statements"][1]["assertions"]))
        self.assertEqual(len(z.report["assertions"][2]["assertions"]), len(self.script["statements"][2]["assertions"]))
        self.assertEqual(len(z.report["assertions"][3]["assertions"]), len(self.script["statements"][3]["assertions"]))
        self.assertEqual(len(z.report["assertions"][4]["assertions"]), len(self.script["statements"][4]["assertions"]))
        self.assertEqual(len(z.report["assertions"][5]["assertions"]), len(self.script["statements"][5]["assertions"]))
        # verify some assertions
        self.assertEqual(z.report["assertions"][0]["assertions"][0]["assert_type"],
            self.script["statements"][0]["assertions"][0]["elementType"])

if __name__ == "__main__":
    unittest.main()
