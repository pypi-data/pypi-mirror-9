import re

import xml.etree.ElementTree as ET
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class CheckTest(BaseTest):

    def __init__(self):
        super().__init__("Check")

    def applies_to(self, exercise):
        return path.isfile(path.join(exercise.path(), "Makefile"))

    def test(self, exercise):
        _, _, err = self.run(["make", "clean", "all", "run-test"], exercise)
        ret = []

        testpath = path.join(exercise.path(), "test", "tmc_test_results.xml")
        if not path.isfile(testpath):
            return [TestResult(success=False, message=err)]

        if len(err) > 0:
            ret.append(TestResult(message=err, warning=True))

        xmlsrc = ""
        with open(testpath) as fp:
            xmlsrc = fp.read()

        xmlsrc = re.sub(r"&(\s)", r"&amp;\1", xmlsrc)

        ns = "{http://check.sourceforge.net/ns}"
        matchtest = ns + "test"
        matchdesc = ns + "description"
        matchmsg = ns + "message"

        root = ET.fromstring(xmlsrc)
        for test in root.iter(matchtest):
            name = test.find(matchdesc).text
            if test.get("result") in ["failure", "error"]:
                success = False
                message = test.find(matchmsg).text
                message = message.replace(r"&amp;", "&")
            else:
                success = True
                message = ""
            ret.append(TestResult(success=success, name=name, message=message))

        return ret
