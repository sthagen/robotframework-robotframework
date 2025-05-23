#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from robot.result import ResultVisitor, TestCase, TestSuite
from robot.utils import XmlWriter


class XUnitWriter:

    def __init__(self, execution_result):
        self._execution_result = execution_result

    def write(self, output):
        xml_writer = XmlWriter(output, usage="xunit")
        writer = XUnitFileWriter(xml_writer)
        self._execution_result.visit(writer)


class XUnitFileWriter(ResultVisitor):
    """Provides an xUnit-compatible result file.

    Attempts to adhere to the de facto schema guessed by Peter Reilly, see:
    http://marc.info/?l=ant-dev&m=123551933508682
    """

    def __init__(self, xml_writer: XmlWriter):
        self._writer = xml_writer

    def start_suite(self, suite: TestSuite):
        stats = suite.statistics  # Accessing property only once.
        attrs = {
            "name": suite.name,
            "tests": str(stats.total),
            "errors": "0",
            "failures": str(stats.failed),
            "skipped": str(stats.skipped),
            "time": format(suite.elapsed_time.total_seconds(), ".3f"),
            "timestamp": suite.start_time.isoformat() if suite.start_time else None,
        }
        self._writer.start("testsuite", attrs)

    def end_suite(self, suite: TestSuite):
        if suite.metadata or suite.doc:
            self._writer.start("properties")
            if suite.doc:
                self._writer.element(
                    "property", attrs={"name": "Documentation", "value": suite.doc}
                )
            for meta_name, meta_value in suite.metadata.items():
                self._writer.element(
                    "property", attrs={"name": meta_name, "value": meta_value}
                )
            self._writer.end("properties")
        self._writer.end("testsuite")

    def visit_test(self, test: TestCase):
        attrs = {
            "classname": test.parent.full_name,
            "name": test.name,
            "time": format(test.elapsed_time.total_seconds(), ".3f"),
        }
        self._writer.start("testcase", attrs)
        if test.failed:
            self._writer.element(
                "failure", attrs={"message": test.message, "type": "AssertionError"}
            )
        if test.skipped:
            self._writer.element(
                "skipped", attrs={"message": test.message, "type": "SkipExecution"}
            )
        self._writer.end("testcase")

    def visit_keyword(self, kw):
        pass

    def visit_statistics(self, stats):
        pass

    def visit_errors(self, errors):
        pass

    def end_result(self, result):
        self._writer.close()
